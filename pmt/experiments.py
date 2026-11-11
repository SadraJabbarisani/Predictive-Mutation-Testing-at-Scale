"""Research questions RQ1-RQ5. Each ``rqN`` function returns a tidy DataFrame

فارسی: اجرای سؤال‌های پژوهشی RQ1 تا RQ5. پروتکل: leave-one-project-out روی پروژه‌های آموزشی؛
پروژه‌های held-out فقط یک بار و با مدلِ آموزش‌دیده روی همه‌ی پروژه‌های آموزشی ارزیابی می‌شوند.
and writes ``results/rqN_*.csv``. ``run_all`` runs everything.

Protocol (fixed, see docs/METHOD.md):
* cross-project = leave-one-project-out over the *train* projects;
* held-out projects are only used once, by models trained on all train projects;
* hyper-parameters are never tuned on held-out projects.
"""
from __future__ import annotations

import json
import platform
import subprocess
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold

from .data.dataset import add_suite_features, load_test_info
from .estimators import ESTIMATORS, Target
from .features import PMT_FEATURES, Featurizer, columns_for
from .metrics import a12, a12_magnitude, classification_metrics, kendall_tau, wilcoxon_p
from .models import fit_calibrated, make_model, proba


def log(msg: str):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


class Pipeline:
    def __init__(self, cfg: dict, data: pd.DataFrame):
        self.cfg = cfg
        self.data = data.reset_index(drop=True)
        self.projects = sorted(self.data["project"].unique())
        self.train_projects = sorted(self.data.loc[self.data["split"] == "train", "project"].unique())
        self.heldout_projects = sorted(set(self.projects) - set(self.train_projects))
        self._cache: dict = {}
        self.out = Path(cfg["paths"]["results"])
        self.out.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------ models
    def training_projects(self, target: str) -> list[str]:
        return [p for p in self.train_projects if p != target]

    def fitted(self, target: str, groups=None, model=None, calibration=None, columns=None):
        # فارسی: مدلی که روی همه‌ی پروژه‌های آموزشی به‌جز پروژه‌ی هدف آموزش دیده (کش می‌شود)
        """Model trained on all training projects except ``target`` (cached)."""
        m = self.cfg["model"]
        groups = tuple(groups or m["feature_groups"])
        model = model or m["name"]
        calibration = calibration or m["calibration"]
        cols = tuple(columns or columns_for(list(groups)))
        key = (target, cols, model, calibration)
        if key not in self._cache:
            tr = self.data[self.data["project"].isin(self.training_projects(target))]
            fz = Featurizer(list(cols)).fit(self.data)
            params = m.get("params", {}) if model == m["name"] else {}
            t0 = time.time()
            clf = fit_calibrated(model, params, fz.matrix(tr), tr["killed"].to_numpy(), calibration,
                                 self.cfg["seed"], groups=tr["project"].to_numpy())
            self._cache[key] = (fz, clf, time.time() - t0)
        return self._cache[key]

    def predict(self, target: str, df: pd.DataFrame, **kw) -> np.ndarray:
        fz, clf, _ = self.fitted(target, **kw)
        return proba(clf, fz.matrix(df))

    def pmt_probs(self, target: str, df: pd.DataFrame) -> np.ndarray:
        model = self.cfg["baselines"]["pmt"].get("model", "rf")
        return self.predict(target, df, model=model, calibration="none", columns=PMT_FEATURES)

    def seshat_probs(self, target: str, df: pd.DataFrame) -> np.ndarray:
        key = ("seshat", target)
        if key not in self._cache:
            tr = self.data[self.data["project"].isin(self.training_projects(target))]
            vec = TfidfVectorizer(token_pattern=r"[A-Za-z_]+|[<>=!+\-*/%&|]+", ngram_range=(1, 2), min_df=2)
            clf = LogisticRegression(C=1.0, max_iter=2000).fit(vec.fit_transform(self._text(tr)), tr["killed"])
            self._cache[key] = (vec, clf)
        vec, clf = self._cache[key]
        return clf.predict_proba(vec.transform(self._text(df)))[:, 1]

    @staticmethod
    def _text(df):
        return (df["line_text"].fillna("") + " " + df["mutator"] + " " + df["mutated_method"].str.replace(
            r"[<>$]", " ", regex=True) + " " + np.where(df["covered"] > 0, "COVERED", "UNCOVERED"))

    def target(self, project: str, df: pd.DataFrame | None = None, **kw) -> Target:
        df = self.data[self.data["project"] == project] if df is None else df
        df = df.reset_index(drop=True)
        return Target(df=df, y=df["killed"].to_numpy(), p=self.predict(project, df, **kw),
                      cost=np.maximum(df["n_cover"].to_numpy(), 1).astype(float),
                      exploit_no_coverage=self.cfg.get("exploit_no_coverage", True),
                      extra=dict(p_pmt=self.pmt_probs(project, df), p_seshat=self.seshat_probs(project, df),
                                 refit=lambda idx, y, _df=df: self.refit_probs(project, _df, idx, y, **kw)))

    def refit_probs(self, project: str, df: pd.DataFrame, idx, y, weight: float = 5.0, **kw) -> np.ndarray:
        """``adapt: refit`` option of ACE-MT: retrain on train projects + executed target mutants."""
        fz, _, _ = self.fitted(project, **kw)
        tr = self.data[self.data["project"].isin(self.training_projects(project))]
        X = np.vstack([fz.matrix(tr), fz.matrix(df.iloc[idx])])
        yy = np.concatenate([tr["killed"].to_numpy(), y])
        w = np.concatenate([np.ones(len(tr)), np.full(len(idx), weight)])
        clf = make_model(self.cfg["model"]["name"], self.cfg["model"].get("params"), self.cfg["seed"])
        try:
            clf.fit(X, yy, sample_weight=w)
        except TypeError:
            clf.fit(X, yy)
        return proba(clf, fz.matrix(df))

    def run_methods(self, ctx: Target, methods: dict, budgets, seeds: int, base_seed: int, tag: dict):
        rows = []
        for b in budgets:
            for name, opts in methods.items():
                opts = {k: v for k, v in (opts or {}).items() if not k.startswith("_")}
                est_name = opts.pop("estimator", name if name in ESTIMATORS else "ace")
                for s in range(seeds):
                    rng = np.random.default_rng(base_seed + 1000 * s + 7)
                    t0 = time.time()
                    e = ESTIMATORS[est_name](ctx, b, rng, **opts)
                    rows.append(dict(**tag, method=name, budget=b, seed=s, true=ctx.true_score, est=e.score,
                                     abs_err=abs(e.score - ctx.true_score), ci_low=e.ci_low, ci_high=e.ci_high,
                                     covers=float(e.ci_low - 1e-9 <= ctx.true_score <= e.ci_high + 1e-9)
                                     if np.isfinite(e.ci_low) else np.nan, ci_width=e.ci_high - e.ci_low, n_executed=e.n_executed,
                                     exec_frac=e.n_executed / ctx.N, test_runs=e.test_runs,
                                     test_run_frac=e.test_runs / ctx.cost[ctx.pool].sum(),
                                     seconds=time.time() - t0, N=ctx.N))
        return rows

    # ------------------------------------------------------------------ RQ1
    def rq1(self) -> pd.DataFrame:
        # فارسی: RQ1 - کیفیت پیش‌بینی (Precision/Recall/MCC/AUC) درون‌پروژه‌ای و بین‌پروژه‌ای
        log("RQ1: prediction quality (cross-project LOPO + within-project CV)")
        rows = []
        models = ["xgboost", "lightgbm", "rf", "logreg"]
        for proj in self.projects:
            df = self.data[self.data["project"] == proj].reset_index(drop=True)
            y = df["killed"].to_numpy()
            setting = "cross-project" if proj in self.train_projects else "held-out"
            cov = df["covered"].to_numpy() > 0
            preds = {m: self.predict(proj, df, model=m) for m in models}
            preds["pmt (rf, PMT features)"] = self.pmt_probs(proj, df)
            preds["seshat_lite"] = self.seshat_probs(proj, df)
            for name, p in preds.items():
                for scope, mask in (("all", np.ones_like(cov)), ("covered", cov)):
                    rows.append(dict(project=proj, setting=setting, model=name, scope=scope,
                                     **classification_metrics(y[mask], p[mask])))
            # within-project 5-fold CV (optimistic upper bound; reported for completeness)
            fz = Featurizer(columns_for(self.cfg["model"]["feature_groups"])).fit(self.data)
            X = fz.matrix(df)
            p = np.zeros(len(y))
            for tr, te in StratifiedKFold(5, shuffle=True, random_state=self.cfg["seed"]).split(X, y):
                clf = make_model(self.cfg["model"]["name"], self.cfg["model"].get("params"), self.cfg["seed"])
                p[te] = proba(clf.fit(X[tr], y[tr]), X[te])
            for scope, mask in (("all", np.ones_like(cov)), ("covered", cov)):
                rows.append(dict(project=proj, setting="within-project", model=self.cfg["model"]["name"],
                                 scope=scope, **classification_metrics(y[mask], p[mask])))
        out = pd.DataFrame(rows)
        out.to_csv(self.out / "rq1_prediction.csv", index=False)
        return out

    # ------------------------------------------------------------------ RQ2/RQ3
    def rq2(self) -> pd.DataFrame:
        # فارسی: RQ2 - خطای تخمین نمره‌ی جهش در بودجه‌های مختلف، برای همه‌ی روش‌ها و همه‌ی تکرارها
        log("RQ2/RQ3: score-estimation error vs. budget")
        rows = []
        projects = self.train_projects + (self.heldout_projects if self.cfg.get("evaluate_heldout") else [])
        for i, proj in enumerate(projects):
            ctx = self.target(proj)
            tag = dict(project=proj, setting="cross-project" if proj in self.train_projects else "held-out")
            rows += self.run_methods(ctx, self.cfg["methods"], self.cfg["budgets"], self.cfg["seeds"],
                                     self.cfg["seed"] + i, tag)
            rows += self.run_methods(ctx, {"full": {}}, [1.0], 1, 0, tag)
            log(f"  {proj}: done")
        out = pd.DataFrame(rows)
        out.to_csv(self.out / "rq2_estimates.csv", index=False)
        return out

    def stats_vs_baselines(self, rq2: pd.DataFrame, ours: str = "ace") -> pd.DataFrame:
        # فارسی: آزمون آماری Wilcoxon و اندازه‌ی اثر A12 بین روش ما و هر baseline
        rows = []
        for (setting, b), g in rq2[rq2["method"] != "full"].groupby(["setting", "budget"]):
            # pair by (project, seed)
            piv = g.pivot_table(index=["project", "seed"], columns="method", values="abs_err")
            for m in piv.columns:
                if m == ours:
                    continue
                x, y = piv[ours].to_numpy(), piv[m].to_numpy()
                a = a12(x, y)
                rows.append(dict(setting=setting, budget=b, baseline=m, mae_ours=x.mean(), mae_baseline=y.mean(),
                                 wilcoxon_p=wilcoxon_p(x, y), a12=a, effect=a12_magnitude(a),
                                 ours_better=x.mean() < y.mean()))
        out = pd.DataFrame(rows)
        out.to_csv(self.out / "rq2_stats.csv", index=False)
        return out

    def rq3(self, rq2: pd.DataFrame) -> pd.DataFrame:
        # فارسی: RQ3 - هزینه: درصد mutant و اجرای تست، و زمان صرفه‌جویی‌شده‌ی تخمینی
        log("RQ3: cost savings")
        meta_p = Path(self.cfg["paths"]["processed"]) / "projects_meta.json"
        meta = json.loads(meta_p.read_text()) if meta_p.exists() else {}
        secs = {k: v.get("pit_seconds", np.nan) for k, v in meta.items()}
        g = rq2.copy()
        g["pit_seconds"] = g["project"].map(secs)
        g["est_seconds_saved"] = (1 - g["test_run_frac"]) * g["pit_seconds"]
        train_time = np.mean([v[2] for k, v in self._cache.items() if isinstance(v, tuple) and len(v) == 3]) \
            if self._cache else np.nan
        out = (g.groupby(["method", "budget"]).agg(exec_frac=("exec_frac", "mean"),
                                                   test_run_frac=("test_run_frac", "mean"),
                                                   seconds_saved=("est_seconds_saved", "mean"),
                                                   estimator_seconds=("seconds", "mean"),
                                                   mae=("abs_err", "mean")).reset_index())
        out["model_train_seconds"] = train_time
        out.to_csv(self.out / "rq3_cost.csv", index=False)
        return out

    # ------------------------------------------------------------------ RQ4
    def rq4(self) -> pd.DataFrame:
        # فارسی: RQ4 - رتبه‌بندی زیرمجموعه‌های تصادفی تست با نمره‌ی تخمینی (Kendall tau)
        log("RQ4: ranking test suites (Kendall tau) + CI coverage")
        c = self.cfg["rq4"]
        rows = []
        raw = self.cfg["paths"]["raw"]
        for i, proj in enumerate(self.projects):
            base = self.data[self.data["project"] == proj].reset_index(drop=True)
            tinfo = load_test_info(raw, proj)
            tests = sorted({t for ts in base["covering_tests"] for t in ts})
            rng = np.random.default_rng(self.cfg["seed"] + i)
            suites = []
            for _ in range(c["n_suites"]):
                s = {t for t in tests if rng.random() < c["keep_prob"]} or {tests[0]}
                suites.append(s)
            ctxs = [self.target(proj, add_suite_features(base, tinfo, s)) for s in suites]
            truth = [x.true_score for x in ctxs]
            for method in ("ace", "random", "model_only", "pmt"):
                opts = self.cfg["methods"].get(method, {})
                for seed in range(c["seeds"]):
                    ests = []
                    for k, ctx in enumerate(ctxs):
                        e = ESTIMATORS[method](ctx, c["budget"], np.random.default_rng(seed * 997 + k), **opts)
                        ests.append(e.score)
                    rows.append(dict(project=proj, method=method, seed=seed, kendall_tau=kendall_tau(ests, truth),
                                     mae=float(np.mean(np.abs(np.array(ests) - truth))),
                                     truth_spread=float(np.std(truth))))
        out = pd.DataFrame(rows)
        out.to_csv(self.out / "rq4_ranking.csv", index=False)
        return out

    # ------------------------------------------------------------------ RQ5
    def rq5(self) -> pd.DataFrame:
        # فارسی: RQ5 - ablation: حذف گروه‌های ویژگی و تغییر اجزای ACE-MT
        log("RQ5: ablation (feature groups + selection policies)")
        a = self.cfg["ablation"]
        b = a["budget"]
        seeds = self.cfg["seeds"]
        ace_opts = self.cfg["methods"]["ace"]
        rows = []
        all_groups = a["feature_groups"]
        variants = {"full model": all_groups} | {f"- {g}": [x for x in all_groups if x != g] for g in all_groups}
        for i, proj in enumerate(self.train_projects):
            tag = dict(project=proj)
            for vname, groups in variants.items():
                ctx = self.target(proj, groups=groups)
                auc = classification_metrics(ctx.y[ctx.pool], ctx.p[ctx.pool])["auc"]
                for r in self.run_methods(ctx, {"ace": ace_opts, "model_only": {}}, [b], seeds, i, tag):
                    rows.append(dict(r, kind="features", variant=vname, auc=auc))
            for vname, delta in a["variants"].items():
                opts = dict(ace_opts, **delta)
                cal = opts.get("_calibration")
                ctx = self.target(proj, calibration=cal) if cal else self.target(proj)
                for r in self.run_methods(ctx, {vname: dict(opts, estimator="ace")}, [b], seeds, i, tag):
                    rows.append(dict(r, kind="policy", variant=vname))
            ctx = self.target(proj)
            for r in self.run_methods(ctx, {"ace (default)": dict(ace_opts, estimator="ace")}, [b], seeds, i, tag):
                rows.append(dict(r, kind="policy", variant="ace (default)"))
        out = pd.DataFrame(rows)
        out.to_csv(self.out / "rq5_ablation.csv", index=False)
        return out


def environment_info() -> dict:
    def sh(c):
        try:
            return subprocess.check_output(c, shell=True, text=True, stderr=subprocess.DEVNULL).strip()
        except Exception:
            return "n/a"
    import sklearn
    info = dict(python=platform.python_version(), platform=platform.platform(), sklearn=sklearn.__version__,
                commit=sh("git rev-parse --short HEAD"), nproc=sh("nproc"), time=time.strftime("%Y-%m-%d %H:%M:%S"))
    for lib in ("xgboost", "lightgbm", "numpy", "pandas", "scipy"):
        try:
            info[lib] = __import__(lib).__version__
        except Exception:
            info[lib] = "missing"
    return info


def run_all(cfg: dict, data: pd.DataFrame, only: list[str] | None = None) -> dict:
    pl = Pipeline(cfg, data)
    (pl.out / "environment.json").write_text(json.dumps(dict(environment_info(), config=cfg), indent=2, default=str))
    res = {}
    want = lambda k: not only or k in only  # noqa: E731
    if want("rq1"):
        res["rq1"] = pl.rq1()
    if want("rq2") or want("rq3"):
        res["rq2"] = pl.rq2()
        res["rq2_stats"] = pl.stats_vs_baselines(res["rq2"])
        res["rq3"] = pl.rq3(res["rq2"])
    if want("rq4"):
        res["rq4"] = pl.rq4()
    if want("rq5"):
        res["rq5"] = pl.rq5()
    return res
