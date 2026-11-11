"""Classifier factory + probability calibration.

Every model is a scikit-learn compatible estimator with ``predict_proba``.
Change ``model.name`` / ``model.params`` in the YAML config to switch.
Missing optional libraries (xgboost / lightgbm) fall back to sklearn's
HistGradientBoosting so the pipeline always runs.
"""
from __future__ import annotations

import warnings

import numpy as np
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore", category=UserWarning)


def make_model(name: str = "xgboost", params: dict | None = None, seed: int = 0):
    # فارسی: ساخت مدل از روی نام (xgboost / lightgbm / rf / logreg / hgb)؛ پارامترها از YAML
    params = dict(params or {})
    name = name.lower()
    if name == "xgboost":
        try:
            from xgboost import XGBClassifier
            p = dict(n_estimators=300, max_depth=4, learning_rate=0.05, subsample=0.8,
                     colsample_bytree=0.8, eval_metric="logloss", n_jobs=2, random_state=seed)
            p.update(params)
            return XGBClassifier(**p)
        except ImportError:
            name = "hgb"
    if name == "lightgbm":
        try:
            from lightgbm import LGBMClassifier
            p = dict(n_estimators=300, num_leaves=15, learning_rate=0.05, subsample=0.8, subsample_freq=1,
                     colsample_bytree=0.8, min_child_samples=10, random_state=seed, verbose=-1, n_jobs=2)
            p.update(params)
            return LGBMClassifier(**p)
        except ImportError:
            name = "hgb"
    if name == "hgb":
        p = dict(max_iter=300, learning_rate=0.05, max_depth=4, random_state=seed)
        p.update(params)
        return HistGradientBoostingClassifier(**p)
    if name in ("rf", "random_forest"):
        p = dict(n_estimators=300, min_samples_leaf=2, n_jobs=2, random_state=seed)
        p.update(params)
        return make_pipeline(SimpleImputer(strategy="median"), RandomForestClassifier(**p))
    if name in ("logreg", "lr"):
        p = dict(C=1.0, max_iter=2000)
        p.update(params)
        return make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), LogisticRegression(**p))
    raise ValueError(f"unknown model {name}")


def fit_calibrated(name: str, params: dict | None, X: np.ndarray, y: np.ndarray, method: str = "isotonic",
                   seed: int = 0, groups: np.ndarray | None = None):
    """Fit a model and calibrate it with cross-validated Platt ('sigmoid') or 'isotonic'.

    ``method='none'`` returns the raw model. When ``groups`` (project ids) are
    given, calibration folds are split by project so calibration reflects the
    cross-project setting.
    """
    # فارسی: آموزش + کالیبراسیون (isotonic یا Platt)؛ foldها بر اساس پروژه جدا می‌شوند
    base = make_model(name, params, seed)
    if method in (None, "none"):
        return base.fit(X, y)
    cv = 3
    if groups is not None and len(np.unique(groups)) >= 3:
        from sklearn.model_selection import GroupKFold
        cv = list(GroupKFold(n_splits=min(5, len(np.unique(groups)))).split(X, y, groups))
    return CalibratedClassifierCV(base, method=method, cv=cv).fit(X, y)


def proba(model, X: np.ndarray) -> np.ndarray:
    return np.clip(model.predict_proba(X)[:, 1], 1e-4, 1 - 1e-4)
