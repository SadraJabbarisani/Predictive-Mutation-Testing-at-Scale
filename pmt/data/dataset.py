"""Build the mutant-level dataset (features + ground-truth label).

Two kinds of features:

* **static** – depend only on the program and the mutant (operator, statement
  kind, nesting, method size/complexity, ...). Computed once.
* **suite** – depend on which test suite is used (coverage + test-oracle
  features). Recomputed by :func:`add_suite_features` for any subset of tests,
  which is what RQ4 (ranking test suites) needs.

LEAKAGE RULE: nothing derived from executing a mutant may become a feature
(``status``, ``killing_tests``, ``n_tests_run`` are labels/metadata only).
Coverage *is* allowed: PIT computes it once on the original program, before
any mutant is executed.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from .java_source import STATEMENT_KINDS, load_java, method_for, statement_kind, test_assertions
from .pit_xml import parse_mutations_xml

LABEL_ONLY_COLUMNS = ["status", "killed", "killing_tests", "n_tests_run", "description"]
# فارسی: این ستون‌ها از اجرای mutant به دست می‌آیند و هرگز نباید ویژگی شوند (نشت داده)


def operator_family(op: str) -> str:
    o = op.lower()
    for key, fam in [("conditionalsboundary", "boundary"), ("negateconditionals", "negate_cond"),
                     ("removeconditional", "remove_cond"), ("math", "math"), ("increment", "increment"),
                     ("invertnegs", "math"), ("return", "return"), ("voidmethodcall", "call_removal"),
                     ("nonvoidmethodcall", "call_removal"), ("constructorcall", "call_removal"),
                     ("inlineconstant", "constant"), ("membervariable", "field"), ("switch", "switch"),
                     ("argumentpropagation", "call_removal"), ("nakedreceiver", "call_removal")]:
        if key in o:
            return fam
    return "other"


def _return_kind(desc: str) -> str:
    r = desc.rsplit(")", 1)[-1] if desc else ""
    if r == "V":
        return "void"
    if r == "Z":
        return "bool"
    if r in ("I", "J", "S", "B", "C"):
        return "int"
    if r in ("F", "D"):
        return "float"
    return "object"


def _n_params(desc: str) -> int:
    if not desc or "(" not in desc:
        return 0
    inner = desc[desc.index("(") + 1:desc.index(")")]
    n, i = 0, 0
    while i < len(inner):
        c = inner[i]
        while c == "[":
            i += 1
            c = inner[i]
        if c == "L":
            i = inner.index(";", i)
        n += 1
        i += 1
    return n


def add_static_features(df: pd.DataFrame, src_main: Path) -> pd.DataFrame:
    # فارسی: ویژگی‌های ایستا از کد منبع: نوع دستور، عمق تودرتو، اندازه و پیچیدگی متد، ...
    rows = []
    for r in df.itertuples():
        pkg_path = r.mutated_class.split("$")[0].rsplit(".", 1)[0].replace(".", "/")
        jf = load_java(str(src_main / pkg_path / r.source_file))
        cls_simple = r.mutated_class.split("$")[0].rsplit(".", 1)[-1]
        f = dict(line_text="", nesting=np.nan, stmt_kind="other", line_tokens=np.nan, has_cmp=0, has_arith=0,
                 method_loc=np.nan, method_cc=np.nan, rel_pos=np.nan, class_loc=np.nan, n_methods=np.nan)
        if jf is not None and 0 < r.line <= len(jf.lines):
            text = jf.lines[r.line - 1]
            f.update(line_text=text.strip(), nesting=jf.depth[r.line - 1], stmt_kind=statement_kind(text),
                     line_tokens=len(text.split()), has_cmp=int(any(t in text for t in ("<", ">", "==", "!="))),
                     has_arith=int(any(t in text for t in ("+", "-", "*", "/", "%"))),
                     class_loc=jf.loc, n_methods=len(jf.methods))
            ms = method_for(jf, r.mutated_method, r.line, cls_simple)
            if ms is not None:
                f.update(method_loc=ms.end - ms.start + 1, method_cc=ms.complexity,
                         rel_pos=(r.line - ms.start) / max(1, ms.end - ms.start))
            elif "{" in text and "}" in text:  # one-line method, e.g. getters
                f.update(method_loc=1, method_cc=1, rel_pos=0.0)
        rows.append(f)
    out = pd.concat([df.reset_index(drop=True), pd.DataFrame(rows)], axis=1)
    out["op_family"] = out["mutator"].map(operator_family)
    out["is_ctor"] = (out["mutated_method"] == "<init>").astype(int)
    out["is_lambda"] = out["mutated_method"].str.startswith("lambda$").astype(int)
    out["is_accessor"] = out["mutated_method"].str.match(r"^(get|set|is|has)[A-Z]").astype(int)
    out["n_params"] = out["method_desc"].map(_n_params)
    out["ret_kind"] = out["method_desc"].map(_return_kind)
    out["mutants_on_line"] = out.groupby(["mutated_class", "line"])["mutant_id"].transform("count")
    out["mutants_in_method"] = out.groupby(["mutated_class", "mutated_method", "method_desc"])["mutant_id"].transform("count")
    out["stmt_kind"] = pd.Categorical(out["stmt_kind"], categories=STATEMENT_KINDS).astype(str)
    return out


def add_suite_features(df: pd.DataFrame, test_info: dict[str, tuple[int, int, str]],
                       suite: set[str] | None = None) -> pd.DataFrame:
    """(Re)compute coverage/oracle features and the label for a given test suite.

    فارسی: ویژگی‌های پوشش و قدرت تست (تعداد assert، تست‌های مستقیم) و برچسب را برای یک
    مجموعه‌تست دلخواه حساب می‌کند؛ RQ4 از همین برای زیرمجموعه‌های تست استفاده می‌کند.

    ``suite=None`` -> the full test suite (PIT's original result).
    """
    out = df.copy()
    cov = out["covering_tests"] if suite is None else out["covering_tests"].map(lambda ts: [t for t in ts if t in suite])
    out["n_cover"] = cov.map(len)
    out["covered"] = (out["n_cover"] > 0).astype(int)
    out["n_cover_classes"] = cov.map(lambda ts: len({t.split("#")[0] for t in ts}))
    a = cov.map(lambda ts: [test_info.get(t, (np.nan, np.nan, ''))[0] for t in ts])
    lo = cov.map(lambda ts: [test_info.get(t, (np.nan, np.nan, ''))[1] for t in ts])
    out["assert_sum"] = a.map(lambda v: np.nansum(v) if v else 0.0)
    out["assert_max"] = a.map(lambda v: np.nanmax(v) if v and not np.all(np.isnan(v)) else 0.0)
    out["assert_mean"] = a.map(lambda v: np.nanmean(v) if v and not np.all(np.isnan(v)) else 0.0)
    out["n_cover_no_assert"] = a.map(lambda v: int(sum(1 for x in v if x == 0)))
    out["test_loc_mean"] = lo.map(lambda v: np.nanmean(v) if v and not np.all(np.isnan(v)) else 0.0)
    # "direct" tests: covering tests that call the mutated method / class by name.
    # Assertions in such tests are much more likely to observe the mutant (PIE: propagation).
    names = out["mutated_method"].where(out["mutated_method"] != "<init>",
                                        out["mutated_class"].str.split("$").str[0].str.rsplit(".").str[-1])
    names = names.str.replace(r"^lambda\$([^$]+)\$.*$", r"\1", regex=True)
    simple_cls = out["mutated_class"].str.split("$").str[0].str.rsplit(".").str[-1]
    bodies = cov.map(lambda ts: [test_info.get(t, (0, 0, ""))[2] for t in ts])
    out["direct_tests"] = [sum(1 for b in bs if f"{n}(" in b) for bs, n in zip(bodies, names)]
    out["direct_asserts"] = [sum(1 for b in bs for ln in b.splitlines() if "assert" in ln and f"{n}(" in ln)
                             for bs, n in zip(bodies, names)]
    out["class_named_tests"] = [sum(1 for t in ts if t.split("#")[0].rsplit(".", 1)[-1].startswith(c))
                                for ts, c in zip(cov, simple_cls)]
    if suite is not None:
        out["killed"] = out["killing_tests"].map(lambda ts: int(any(t in suite for t in ts)))
        # TIMED_OUT / MEMORY_ERROR etc. have no killing test but are "detected" by any covering run
        detected_other = df["status"].isin(["TIMED_OUT", "MEMORY_ERROR", "RUN_ERROR"]) & (out["n_cover"] > 0)
        out.loc[detected_other, "killed"] = 1
    return out


def build_project(raw_dir: Path, name: str) -> pd.DataFrame:
    df = parse_mutations_xml(raw_dir / "mutations.xml", name)
    df = add_static_features(df, raw_dir / "src" / "main")
    tinfo = test_assertions(str(raw_dir / "src" / "test"))
    return add_suite_features(df, tinfo)


def build_dataset(raw_root: str | Path, out_dir: str | Path, subjects_csv: str | Path | None = None) -> pd.DataFrame:
    # فارسی: همه‌ی data/raw/<project>/mutations.xml را به دیتاست واحد data/processed/mutants.pkl تبدیل می‌کند
    """Parse every ``data/raw/<project>/mutations.xml`` into ``data/processed/mutants.pkl`` (+csv)."""
    raw_root, out_dir = Path(raw_root), Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    split = {}
    if subjects_csv and Path(subjects_csv).exists():
        s = pd.read_csv(subjects_csv)
        split = dict(zip(s["name"], s["split"]))
    frames, meta = [], {}
    for d in sorted(p for p in raw_root.iterdir() if (p / "mutations.xml").exists()):
        df = build_project(d, d.name)
        df["split"] = split.get(d.name, "train")
        frames.append(df)
        m = json.loads((d / "meta.json").read_text()) if (d / "meta.json").exists() else {}
        meta[d.name] = m
    data = pd.concat(frames, ignore_index=True)
    data.to_pickle(out_dir / "mutants.pkl")
    flat = data.copy()
    for c in ("covering_tests", "killing_tests"):
        flat[c] = flat[c].map(lambda v: "|".join(v))
    flat.to_csv(out_dir / "mutants.csv", index=False)
    (out_dir / "projects_meta.json").write_text(json.dumps(meta, indent=2))
    return data


def load_dataset(processed_dir: str | Path) -> pd.DataFrame:
    return pd.read_pickle(Path(processed_dir) / "mutants.pkl")


def load_test_info(raw_root: str | Path, project: str) -> dict[str, tuple[int, int, str]]:
    return test_assertions(str(Path(raw_root) / project / "src" / "test"))
