"""Feature groups and the design-matrix builder.

To add a feature: compute the column in ``pmt/data/dataset.py`` and list it in
one of the groups below. Groups are what the ablation (RQ5) switches off.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

FEATURE_GROUPS: dict[str, list[str]] = {
    # فارسی: چهار گروه ویژگی؛ ablation (RQ5) هر گروه را یکی‌یکی حذف می‌کند.
    # برای افزودن ویژگی: ستون را در dataset.py بسازید و نامش را اینجا اضافه کنید.
    # what kind of change was made
    "operator": ["mutator", "op_family"],
    # where the change was made (AST-lite / structural)
    "static": ["stmt_kind", "nesting", "line_tokens", "has_cmp", "has_arith", "method_loc", "method_cc",
               "rel_pos", "class_loc", "n_methods", "is_ctor", "is_lambda", "is_accessor", "n_params",
               "ret_kind", "index", "block", "mutants_on_line", "mutants_in_method"],
    # how well the location is executed by tests (PIT/JaCoCo coverage, pre-execution)
    "coverage": ["n_cover", "covered", "n_cover_classes"],
    # how strong the covering tests are (PMT "test oracle" features)
    "oracle": ["assert_sum", "assert_max", "assert_mean", "n_cover_no_assert", "test_loc_mean",
               "direct_tests", "direct_asserts", "class_named_tests"],
}
CATEGORICAL = ["mutator", "op_family", "stmt_kind", "ret_kind"]

# Feature set of the original PMT paper (Zhang et al.) re-implemented as a baseline:
# operator + coverage + test-oracle features + a few structural ones.
PMT_FEATURES = FEATURE_GROUPS["operator"] + FEATURE_GROUPS["coverage"] + FEATURE_GROUPS["oracle"][:5] + [
    "nesting", "method_cc", "method_loc", "is_ctor", "ret_kind"]


def columns_for(groups: list[str]) -> list[str]:
    cols: list[str] = []
    for g in groups:
        cols += [c for c in FEATURE_GROUPS[g] if c not in cols]
    return cols


class Featurizer:
    # فارسی: تبدیل ستون‌ها به ماتریس عددی؛ ستون‌های دسته‌ای one-hot می‌شوند
    """One-hot encodes categoricals with a vocabulary fixed at ``fit`` time.

    The vocabulary is taken from *all* mutants (no labels involved), so an
    operator that only appears in the target project still gets a column.
    """

    def __init__(self, columns: list[str]):
        self.columns = columns
        self.vocab: dict[str, list[str]] = {}
        self.out_columns: list[str] = []

    def fit(self, df: pd.DataFrame) -> "Featurizer":
        for c in self.columns:
            if c in CATEGORICAL:
                self.vocab[c] = sorted(df[c].astype(str).unique())
        self.out_columns = list(self.transform(df.head(1)).columns)
        return self

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        parts = []
        for c in self.columns:
            if c in CATEGORICAL:
                cat = pd.Categorical(df[c].astype(str), categories=self.vocab[c])
                parts.append(pd.get_dummies(cat, prefix=c, dtype=float).set_index(df.index))
            else:
                parts.append(df[[c]].astype(float))
        X = pd.concat(parts, axis=1)
        if self.out_columns:
            X = X.reindex(columns=self.out_columns, fill_value=0.0)
        return X

    def matrix(self, df: pd.DataFrame) -> np.ndarray:
        return self.transform(df).to_numpy(dtype=float)
