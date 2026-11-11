"""Load mutants from a language-agnostic CSV (Python/mutmut, JS/Stryker, C#, ...).

فارسی: خواندن داده از CSV عمومی برای زبان‌های دیگر (Python و ...)؛ قالب در docs/DATA_FORMAT.md

Required columns (see docs/DATA_FORMAT.md):
    project, mutated_class, mutated_method, line, mutator, killed,
    covering_tests ('|' separated), killing_tests ('|' separated)
Optional: split, source_file, line_text, status, and any feature column
from pmt/features.py (missing numeric features are filled with NaN/0).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .dataset import operator_family
from .java_source import statement_kind

DEFAULTS = dict(source_file="", method_desc="", index=0, block=0, description="", status="", n_tests_run=0,
                line_text="", split="train")


def load_generic_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    for c, v in DEFAULTS.items():
        if c not in df:
            df[c] = v
    df["line_text"] = df["line_text"].fillna("")
    for c in ("covering_tests", "killing_tests"):
        df[c] = df[c].fillna("").astype(str).map(lambda s: sorted(t for t in s.split("|") if t))
    df["mutant_id"] = df.get("mutant_id", df["project"] + ":" + df.groupby("project").cumcount().astype(str))
    df["op_family"] = df["mutator"].map(operator_family)
    if "stmt_kind" not in df:
        df["stmt_kind"] = df["line_text"].map(statement_kind)
    df["is_ctor"] = df["mutated_method"].isin(["<init>", "__init__", "constructor"]).astype(int)
    df["is_lambda"] = df["mutated_method"].str.contains("lambda").astype(int)
    df["is_accessor"] = df["mutated_method"].str.match(r"^(get|set|is|has)[A-Z_]").astype(int)
    df["ret_kind"] = df.get("ret_kind", "object")
    df["n_params"] = df.get("n_params", 0)
    df["mutants_on_line"] = df.groupby(["mutated_class", "line"])["mutant_id"].transform("count")
    df["mutants_in_method"] = df.groupby(["mutated_class", "mutated_method"])["mutant_id"].transform("count")
    cov = df["covering_tests"]
    df["n_cover"] = cov.map(len)
    df["covered"] = (df["n_cover"] > 0).astype(int)
    df["n_cover_classes"] = cov.map(lambda ts: len({t.split("#")[0].split("::")[0] for t in ts}))
    for c in ("nesting", "line_tokens", "method_loc", "method_cc", "rel_pos", "class_loc", "n_methods"):
        if c not in df:
            df[c] = np.nan
    for c in ("has_cmp", "has_arith", "assert_sum", "assert_max", "assert_mean", "n_cover_no_assert",
              "test_loc_mean", "direct_tests", "direct_asserts", "class_named_tests"):
        if c not in df:
            df[c] = 0
    return df
