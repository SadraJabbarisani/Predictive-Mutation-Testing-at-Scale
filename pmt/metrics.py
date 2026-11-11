"""Evaluation metrics and statistical tests."""
from __future__ import annotations

import numpy as np
from scipy import stats
from sklearn.metrics import (brier_score_loss, f1_score, matthews_corrcoef, precision_score, recall_score,
                             roc_auc_score)


def classification_metrics(y: np.ndarray, p: np.ndarray, thr: float = 0.5) -> dict:
    yh = (p >= thr).astype(int)
    out = dict(precision=precision_score(y, yh, zero_division=0), recall=recall_score(y, yh, zero_division=0),
               f1=f1_score(y, yh, zero_division=0), mcc=matthews_corrcoef(y, yh),
               brier=brier_score_loss(y, p), ece=ece(y, p), accuracy=float((yh == y).mean()))
    out["auc"] = roc_auc_score(y, p) if len(np.unique(y)) > 1 else np.nan
    return out


def ece(y: np.ndarray, p: np.ndarray, bins: int = 10) -> float:
    """Expected calibration error."""
    edges = np.linspace(0, 1, bins + 1)
    e = 0.0
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (p >= lo) & (p < hi if hi < 1 else p <= hi)
        if m.any():
            e += m.mean() * abs(p[m].mean() - y[m].mean())
    return float(e)


def a12(x, y) -> float:
    """Vargha-Delaney A12: P(X > Y) + 0.5 P(X = Y). For errors, A12 < 0.5 means X is better."""
    x, y = np.asarray(x), np.asarray(y)
    gt = (x[:, None] > y[None, :]).mean()
    eq = (x[:, None] == y[None, :]).mean()
    return float(gt + 0.5 * eq)


def a12_magnitude(a: float) -> str:
    d = abs(a - 0.5)
    return "negligible" if d < 0.06 else "small" if d < 0.14 else "medium" if d < 0.21 else "large"


def wilcoxon_p(x, y) -> float:
    x, y = np.asarray(x), np.asarray(y)
    if np.allclose(x, y):
        return 1.0
    try:
        return float(stats.wilcoxon(x, y).pvalue)
    except ValueError:
        return np.nan


def kendall_tau(a, b) -> float:
    t = stats.kendalltau(a, b).statistic
    return float(t) if np.isfinite(t) else np.nan
