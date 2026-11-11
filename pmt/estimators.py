"""Mutation-score estimators: baselines + the proposed method (ACE-MT).

فارسی: تخمین‌گرهای نمره‌ی جهش؛ همه‌ی baselineها و روش پیشنهادی (ACE-MT) اینجا هستند.
هر تخمین‌گر فقط برچسب mutantهایی را می‌بیند که «اجرا» می‌کند و هزینه = تعداد آن‌ها.
mutantهای بدون پوشش برای همه‌ی روش‌ها رایگان (زنده) حساب می‌شوند تا مقایسه منصفانه باشد.

All estimators share one signature::

    est = ESTIMATORS[name](ctx, budget_frac, rng, **options) -> Estimate

``ctx`` (:class:`Target`) holds one target project: its mutants (with the
hidden ground truth ``y``), and the calibrated cross-project probabilities
``p`` from a model that never saw this project. An estimator may only look at
``y[i]`` for the mutants it "executes"; their number (unique) is the cost.

Mutation score = killed / all mutants (PIT definition). Mutants with no
coverage are known to survive without running anything, so *every* method
(baselines included) gets them for free when ``exploit_no_coverage`` is on.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.linear_model import LogisticRegression

# ---------------------------------------------------------------------------
# data holders
# ---------------------------------------------------------------------------


@dataclass
class Target:
    # فارسی: یک پروژه‌ی هدف؛ y برچسب واقعی (پنهان تا زمان اجرا)، p احتمال کشته‌شدن از مدل بین‌پروژه‌ای
    df: pd.DataFrame                 # target mutants (one project / one suite)
    y: np.ndarray                    # ground truth (only revealed on execution)
    p: np.ndarray                    # calibrated cross-project kill probability
    cost: np.ndarray                 # per-mutant execution cost (test runs)
    exploit_no_coverage: bool = True
    extra: dict = field(default_factory=dict)   # e.g. p_pmt, p_seshat, refit callback

    @property
    def N(self) -> int:
        return len(self.y)

    @property
    def pool(self) -> np.ndarray:
        # فارسی: mutantهایی که برای دانستن نتیجه‌شان باید واقعاً اجرا شوند (پوشش‌داده‌شده‌ها)
        """Indices that actually need execution to know their outcome."""
        if self.exploit_no_coverage:
            return np.flatnonzero(self.df["covered"].to_numpy() > 0)
        return np.arange(self.N)

    @property
    def true_score(self) -> float:
        return float(self.y.mean())


@dataclass
class Estimate:
    score: float
    ci_low: float = np.nan
    ci_high: float = np.nan
    executed: np.ndarray = field(default_factory=lambda: np.array([], dtype=int))
    test_runs: float = 0.0

    @property
    def n_executed(self) -> int:
        return len(self.executed)


def _budget(ctx: Target, frac: float) -> int:
    return int(min(len(ctx.pool), max(1, round(frac * ctx.N))))


def _finish(ctx: Target, killed_in_pool: float, var_pool: float, executed, alpha=0.05) -> Estimate:
    # فارسی: تبدیل «تعداد کشته‌ی تخمینی» به نمره‌ی جهش + بازه‌ی اطمینان نرمال ۹۵٪
    """Convert an estimate of #killed inside the pool into a score + normal CI."""
    executed = np.unique(np.asarray(executed, dtype=int))
    s = killed_in_pool / ctx.N
    if np.isfinite(var_pool) and var_pool >= 0:
        h = stats.norm.ppf(1 - alpha / 2) * np.sqrt(var_pool) / ctx.N
        lo, hi = max(0.0, s - h), min(len(ctx.pool) / ctx.N, s + h)
    else:
        lo = hi = np.nan
    return Estimate(float(np.clip(s, 0, 1)), lo, hi, executed, float(ctx.cost[executed].sum()))


# ---------------------------------------------------------------------------
# baselines
# ---------------------------------------------------------------------------


def full(ctx: Target, budget_frac: float, rng, **_) -> Estimate:
    """Run everything (gold standard, 100 % cost)."""
    pool = ctx.pool
    return _finish(ctx, ctx.y[pool].sum(), 0.0, pool)


def random_sampling(ctx: Target, budget_frac: float, rng, **_) -> Estimate:
    # فارسی: baseline نمونه‌گیری تصادفی ساده بدون جایگذاری، با تصحیح جمعیت محدود در واریانس
    """Simple random sampling without replacement; CI with finite-population correction."""
    pool = ctx.pool
    n = _budget(ctx, budget_frac)
    s = rng.choice(pool, n, replace=False)
    ph = ctx.y[s].mean()
    Np = len(pool)
    var = Np ** 2 * (1 - n / Np) * max(ph * (1 - ph), 0.25 / n) / max(n - 1, 1)
    return _finish(ctx, ph * Np, var, s)


def stratified_sampling(ctx: Target, budget_frac: float, rng, strata: str = "op_family", **_) -> Estimate:
    # فارسی: baseline نمونه‌گیری طبقه‌ای؛ طبقه = خانواده‌ی عملگر، تخصیص متناسب با اندازه‌ی طبقه
    """Proportional stratified sampling by operator family (or any column)."""
    pool = ctx.pool
    n = _budget(ctx, budget_frac)
    groups = ctx.df[strata].to_numpy()[pool]
    labels, counts = np.unique(groups, return_counts=True)
    alloc = np.floor(counts / counts.sum() * n).astype(int)
    rem = n - alloc.sum()
    order = np.argsort(-(counts / counts.sum() * n - alloc))
    alloc[order[:rem]] += 1
    total, var, sel = 0.0, 0.0, []
    for lab, Nh, nh in zip(labels, counts, alloc):
        members = pool[groups == lab]
        if nh == 0:  # stratum not sampled: fall back to the overall sample mean later
            continue
        s = rng.choice(members, min(nh, Nh), replace=False)
        sel.extend(s)
        ph = ctx.y[s].mean()
        total += Nh * ph
        var += Nh ** 2 * (1 - len(s) / Nh) * max(ph * (1 - ph), 0.25 / len(s)) / max(len(s) - 1, 1)
    unsampled = sum(Nh for Nh, nh in zip(counts, alloc) if nh == 0)
    if unsampled:
        total += unsampled * ctx.y[np.array(sel)].mean()
    return _finish(ctx, total, var, sel)


# selective mutation: operator priority (Offutt-style "sufficient" operators first)
SELECTIVE_ORDER = ["negate_cond", "boundary", "math", "increment", "return", "remove_cond",
                   "call_removal", "constant", "field", "switch", "other"]


def selective_mutation(ctx: Target, budget_frac: float, rng, **_) -> Estimate:
    # فارسی: baseline جهش انتخابی؛ فقط چند خانواده‌ی عملگر مهم (به ترتیب اولویت) تا سقف بودجه اجرا می‌شوند
    """Run only whole operator families, in priority order, while they fit the budget.

    The score of the selected operators is used as a proxy for the full score
    (classic cost-reduction technique; no confidence interval).
    """
    pool = ctx.pool
    n = _budget(ctx, budget_frac)
    fam = ctx.df["op_family"].to_numpy()[pool]
    order = SELECTIVE_ORDER + sorted(set(fam) - set(SELECTIVE_ORDER))
    chosen = []
    for f in order:
        m = pool[fam == f]
        if len(m) and len(chosen) + len(m) <= n:
            chosen.extend(m)
    if not chosen:  # even the first family is too big -> random subset of it
        first = next(f for f in order if (fam == f).any())
        m = pool[fam == first]
        chosen = list(rng.choice(m, n, replace=False))
    chosen = np.array(chosen)
    return _finish(ctx, ctx.y[chosen].mean() * len(pool), np.nan, chosen)


def pmt_classifier(ctx: Target, budget_frac: float, rng, key: str = "p_pmt", threshold=0.5, **_) -> Estimate:
    # فارسی: baseline PMT؛ پیش‌بینی همه‌ی mutantها با طبقه‌بند و بدون هیچ اجرایی (برچسب سخت، آستانه ۰٫۵)
    """PMT (Zhang et al.): predict every mutant with a cross-project classifier, run nothing."""
    pool = ctx.pool
    p = ctx.extra[key][pool]
    return _finish(ctx, float((p >= threshold).sum()), np.nan, [])


def model_only(ctx: Target, budget_frac: float, rng, **_) -> Estimate:
    # فارسی: فقط جمع احتمال‌های کالیبره؛ بدون اجرا. بازه‌اش فقط در صورت کالیبراسیون کامل معتبر است
    """Sum of calibrated probabilities (no execution). CI assumes perfect calibration."""
    pool = ctx.pool
    p = ctx.p[pool]
    return _finish(ctx, p.sum(), (p * (1 - p)).sum(), [])


def active_topk(ctx: Target, budget_frac: float, rng, **_) -> Estimate:
    # فارسی: یادگیری فعال کلاسیک؛ B تا نامطمئن‌ترین را اجرا کن، بقیه را مدل پیش‌بینی کند (اریب)
    """Classic uncertainty active learning: execute the B most uncertain mutants,
    use true labels for them and the model for the rest (biased; heuristic CI)."""
    pool = ctx.pool
    n = _budget(ctx, budget_frac)
    p = ctx.p[pool]
    top = pool[np.argsort(-p * (1 - p))[:n]]
    rest = np.setdiff1d(pool, top)
    pr = ctx.p[rest]
    return _finish(ctx, ctx.y[top].sum() + pr.sum(), (pr * (1 - pr)).sum(), top)


# ---------------------------------------------------------------------------
# proposed: ACE-MT  (Active, Calibrated, model-assisted Estimation)
# ---------------------------------------------------------------------------


def _logit(p):
    p = np.clip(p, 1e-4, 1 - 1e-4)
    return np.log(p / (1 - p))


def adapt_platt(p_base: np.ndarray, idx: np.ndarray, y: np.ndarray, prior_strength: float = 5.0):
    # فارسی: کالیبراسیون دوباره‌ی مدل برای پروژه‌ی هدف با برچسب‌های اجراشده (رگرسیون لجستیک روی logit)؛
    # نمونه‌های مجازی (prior) جلوی بیش‌برازش با برچسب‌های کم را می‌گیرند
    """Project-adaptive recalibration: logistic regression on logit(p_base)
    fitted to the labels executed so far. ``prior_strength`` = how many pseudo
    samples pull the fit towards the identity mapping."""
    if len(idx) < 4 or y[idx].min() == y[idx].max():
        return p_base
    z = _logit(p_base)
    # pseudo-observations that encode the prior "base model is right"
    k = int(prior_strength)
    qs = np.quantile(z, np.linspace(0.05, 0.95, max(k, 2)))
    X = np.concatenate([z[idx], qs, qs])[:, None]
    yy = np.concatenate([y[idx], np.ones_like(qs), np.zeros_like(qs)])
    w = np.concatenate([np.ones(len(idx)), 1 / (1 + np.exp(-qs)), 1 - 1 / (1 + np.exp(-qs))])
    lr = LogisticRegression(C=1.0).fit(X, yy, sample_weight=w)
    return lr.predict_proba(z[:, None])[:, 1]


def neighbor_adjust(p: np.ndarray, groups: list[np.ndarray], known: np.ndarray, y: np.ndarray,
                    kappa: float = 2.0) -> np.ndarray:
    # فارسی: (اختیاری) خطای مدل روی mutantهای اجراشده‌ی هم‌خط/هم‌متد به همسایه‌ها منتقل می‌شود
    """Shrink each probability towards the residuals observed on *executed*
    neighbours (same line, same method ...). ``groups`` = list of group-id
    arrays, from coarse to fine; finer groups are applied last."""
    out = p.copy()
    if not known.any():
        return out
    for g in groups:
        res = np.where(known, y - out, 0.0)
        s = pd.Series(res).groupby(g).transform("sum").to_numpy()
        n = pd.Series(known.astype(float)).groupby(g).transform("sum").to_numpy()
        out = np.clip(out + s / (n + kappa), 1e-3, 1 - 1e-3)
    return out


def ace(ctx: Target, budget_frac: float, rng, rounds: int = 4, policy: str = "hybrid", mix: float = 0.3,
        adapt: str = "platt", neighbors: tuple = (), kappa: float = 2.0, ci: str = "normal",
        combine: bool = True, alpha: float = 0.05, n_boot: int = 500, **_) -> Estimate:
    """ACE-MT: Active, Calibrated, model-assisted Estimation of the mutation score.

    1. Start from calibrated cross-project probabilities ``p`` (no execution).
    2. Draw one mutant at a time from the not-yet-executed pool with
       ``q ∝ (1-mix)·sqrt(p(1-p)) + mix·uniform``  (policy 'uncertainty' -> mix=0,
       'uniform' -> mix=1, 'hybrid' -> mix as given). Execute it.
    3. Every draw j yields an unbiased estimate of #killed (difference estimator)
       ``T_j = Σ_known y + Σ_unknown p_i + (y_j - p_j) / q_j``.
    4. After each of ``rounds`` rounds, adapt ``p`` to the project using only
       labels seen so far: Platt recalibration (``adapt='platt'``) and residual
       sharing with executed neighbours on the same method/line (``neighbors``).
       Because ``p`` and ``q`` only use past labels, every T_j stays unbiased.
    5. Estimate = mean(T_j) (unbiased, variance V); CI from their spread
       (normal) or bootstrap.
    6. ``combine=True``: empirical-Bayes shrinkage towards the adapted model
       prediction M = Σ_known y + Σ_unknown p.  Weight w = V / (V + max(0, (T-M)² - V)),
       i.e. trust the model only as far as the data cannot tell it is biased.
       The CI keeps the half-width of the unbiased estimator.
    """
    pool = ctx.pool
    n_total = _budget(ctx, budget_frac)
    mix = {"uncertainty": 0.0, "uniform": 1.0}.get(policy, mix)
    # فارسی: --- روش پیشنهادی ACE-MT ---
    # ۱) p = احتمال کالیبره از مدل بین‌پروژه‌ای   ۲) نمونه‌گیری فعال یکی‌یکی از mutantهای اجرانشده
    # ۳) هر انتخاب یک تخمین نااریب T_j می‌دهد   ۴) بعد از هر دور، تطبیق مدل با پروژه
    # ۵) میانگین T_j + بازه‌ی اطمینان   ۶) ترکیب empirical-Bayes با پیش‌بینی مدل
    yp = ctx.y[pool]
    p_base = ctx.p[pool].copy()
    df = ctx.df.iloc[pool]
    gmap = {"class": df["mutated_class"].to_numpy(),
            "method": (df["mutated_class"] + "#" + df["mutated_method"] + df["method_desc"]).to_numpy(),
            "line": (df["mutated_class"] + ":" + df["line"].astype(str)).to_numpy()}
    groups = [pd.factorize(gmap[g])[0] for g in (neighbors or ())]
    known = np.zeros(len(pool), bool)
    p_cur = p_base.copy()
    T: list[float] = []
    quotas = np.diff(np.linspace(0, n_total, rounds + 1).round().astype(int))
    for quota in quotas:
        for _ in range(quota):
            free = ~known
            if not free.any():
                break
            u = np.sqrt(p_cur * (1 - p_cur)) * free
            # فارسی: احتمال انتخاب q = ترکیب عدم‌قطعیت sqrt(p(1-p)) و توزیع یکنواخت (برای نااریبی)
            q = (1 - mix) * u / u.sum() + mix * free / free.sum()
            q /= q.sum()
            j = rng.choice(len(pool), p=q)
            T.append(yp[known].sum() + p_cur[free].sum() + (yp[j] - p_cur[j]) / q[j])
            # فارسی: تخمین‌گر تفاضلی: برچسب‌های معلوم + پیش‌بینی بقیه + خطای مدل روی نمونه وزن‌دار با ۱/q
            known[j] = True
        if known.all():
            break
        idx = np.flatnonzero(known)
        p_new = adapt_platt(p_base, idx, yp) if adapt == "platt" else p_base
        # فارسی: تطبیق فقط با برچسب‌های گذشته؛ پس T_jهای بعدی هم نااریب می‌مانند
        if groups:
            p_new = neighbor_adjust(p_new, groups, known, yp, kappa)
        p_cur = np.clip(p_new, 1e-3, 1 - 1e-3)
    exe = pool[known]
    if known.all():
        return _finish(ctx, yp.sum(), 0.0, exe)
    T = np.asarray(T)
    est = float(T.mean())
    if ci == "bootstrap":
        b = np.array([rng.choice(T, len(T)).mean() for _ in range(n_boot)])
        lo, hi = np.quantile(b, [alpha / 2, 1 - alpha / 2])
        e = _finish(ctx, est, np.nan, exe)
        e.ci_low, e.ci_high = max(0, lo / ctx.N), min(1, hi / ctx.N)
        return e
    var = T.var(ddof=1) / len(T) if len(T) > 1 else np.inf
    if combine and np.isfinite(var):
        # فارسی: ترکیب empirical-Bayes؛ وزن w به مدل فقط وقتی زیاد است که اختلاف مدل و نمونه از نویز کمتر باشد
        M = yp[known].sum() + p_cur[~known].sum()
        w = var / (var + max(0.0, (est - M) ** 2 - var))
        est = w * M + (1 - w) * est
    return _finish(ctx, min(max(est, yp[known].sum()), len(pool)), var, exe, alpha)


def ace_strat(ctx: Target, budget_frac: float, rng, strata: int = 4, pilot: float = 0.5, adapt: str = "platt",
              min_per_stratum: int = 2, alpha: float = 0.05, **_) -> Estimate:
    """ACE-MT (stratified form).

    1. Split the pool into ``strata`` bins by the cross-project probability p.
    2. Pilot phase (``pilot`` share of the budget): Neyman allocation using the
       model-predicted std ``sqrt(p(1-p))`` per bin, SRS without replacement.
    3. Adapt the model to the project (Platt recalibration on pilot labels).
    4. Second phase: allocate the rest of the budget with Neyman allocation
       using the *observed* residual std per bin (unsampled units only).
    5. Estimate with the stratified difference (GREG) estimator using the
       adapted probabilities; variance from within-stratum residuals.
    """
    pool = ctx.pool
    n = _budget(ctx, budget_frac)
    yp = ctx.y[pool]
    p0 = ctx.p[pool]
    H = int(max(1, min(strata, n // max(min_per_stratum, 1), len(pool) // 4)))
    edges = np.quantile(p0, np.linspace(0, 1, H + 1)[1:-1]) if H > 1 else np.array([])
    h = np.searchsorted(edges, p0, side="right")
    labels = np.unique(h)
    Nh = np.array([(h == k).sum() for k in labels])
    taken = np.zeros(len(pool), bool)

    def allocate(m, sd):
        w = Nh * np.maximum(sd, 1e-3)
        cap = np.array([(~taken & (h == k)).sum() for k in labels])
        a = np.minimum(np.floor(w / w.sum() * m).astype(int), cap)
        while a.sum() < m and (a < cap).any():
            k = np.argmax(np.where(a < cap, w / (a + 1), -1))
            a[k] += 1
        return a

    def draw(alloc):
        for k, a in zip(labels, alloc):
            free = np.flatnonzero(~taken & (h == k))
            if a > 0:
                taken[rng.choice(free, min(a, len(free)), replace=False)] = True

    n1 = max(min(n, len(labels) * min_per_stratum), int(round(pilot * n)))
    sd0 = np.array([np.sqrt((p0[h == k] * (1 - p0[h == k])).mean()) for k in labels])
    a1 = allocate(n1, sd0)
    a1 = np.maximum(a1, np.minimum(min_per_stratum, Nh)) if n1 >= len(labels) * min_per_stratum else a1
    draw(a1)
    idx = np.flatnonzero(taken)
    p1 = adapt_platt(p0, idx, yp) if adapt == "platt" else p0
    if n - taken.sum() > 0:
        res = yp - p1
        sd1 = np.array([res[taken & (h == k)].std(ddof=1) if (taken & (h == k)).sum() > 1 else sd0[i]
                        for i, k in enumerate(labels)])
        draw(allocate(int(n - taken.sum()), np.sqrt(sd1 ** 2 + 0.01)))
        idx = np.flatnonzero(taken)
        p1 = adapt_platt(p0, idx, yp) if adapt == "platt" else p0
    total, var = 0.0, 0.0
    for k, N_k in zip(labels, Nh):
        m = h == k
        s = m & taken
        n_k = s.sum()
        e = yp[s] - p1[s]
        total += p1[m].sum() + (N_k * e.mean() if n_k else 0.0)
        if n_k > 1:
            var += N_k ** 2 * (1 - n_k / N_k) * e.var(ddof=1) / n_k
        elif n_k == 1:
            var += N_k ** 2 * (1 - n_k / N_k) * 0.25
    return _finish(ctx, min(max(total, 0), len(pool)), var, pool[idx], alpha)


ESTIMATORS: dict[str, Callable[..., Estimate]] = {
    "ace_strat": ace_strat,
    "full": full,
    "random": random_sampling,
    "stratified": stratified_sampling,
    "selective": selective_mutation,
    "pmt": pmt_classifier,
    "seshat_lite": lambda ctx, b, rng, **k: pmt_classifier(ctx, b, rng, key="p_seshat"),
    "model_only": model_only,
    "active_topk": active_topk,
    "ace": ace,
}
