#!/usr/bin/env python3
"""(Optional track) Convert mutmut 3.x results of a Python project into the generic CSV format.

Steps (inside the Python project you want to study):
    pip install "mutmut>=3" pytest
    mutmut run                       # creates ./mutants/ with *.meta files and mutmut-stats.json
    python /path/to/python_mutmut/mutmut_to_csv.py . --project myproj --out myproj_mutants.csv

Then in this repo:
    python -m pmt all --set dataset.source=generic_csv dataset.generic_csv=myproj_mutants.csv

Notes / limitations (verify against your mutmut version - formats change):
* label: exit code 1 (tests failed) = killed; 0 = survived; 33/34/None = not run / no tests.
* covering tests come from ``mutants/mutmut-stats.json`` ("tests_by_mangled_function_name"),
  i.e. per *function*, not per line -> coarser than PIT.
* mutmut stops at the first failing test, so ``killing_tests`` is empty and RQ4
  (sub-suite ranking) is not meaningful for this track.
* mutmut does not expose the operator name; we derive a coarse one by diffing
  the mutated function against the original (see ``guess_operator``).
"""
from __future__ import annotations

import argparse
import csv
import difflib
import json
import re
from pathlib import Path

KILLED, SURVIVED = {1, 3}, {0}


def guess_operator(orig: str, mutated: str) -> str:
    a, b = orig.split(), mutated.split()
    sm = difflib.SequenceMatcher(None, a, b)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        x, y = " ".join(a[i1:i2]), " ".join(b[j1:j2])
        if re.fullmatch(r"[<>=!]+", x or "") or re.fullmatch(r"[<>=!]+", y or ""):
            return "ConditionalsMutator"
        if re.fullmatch(r"[+\-*/%]+=?", x or "") or re.fullmatch(r"[+\-*/%]+=?", y or ""):
            return "MathMutator"
        if re.search(r"\d", x + y):
            return "InlineConstantMutator"
        if "None" in y:
            return "NullReturnValsMutator"
        if x in ("True", "False", "and", "or", "not") or y in ("True", "False", "and", "or", "not"):
            return "NegateConditionalsMutator"
        if re.search(r"['\"]", x + y):
            return "StringMutator"
        return "OtherMutator"
    return "OtherMutator"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project_dir")
    ap.add_argument("--project", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--split", default="train")
    a = ap.parse_args()
    root = Path(a.project_dir)
    mdir = root / "mutants"
    stats_p = mdir / "mutmut-stats.json"
    tests_by_fn = json.loads(stats_p.read_text()).get("tests_by_mangled_function_name", {}) if stats_p.exists() else {}
    rows = []
    for meta in mdir.rglob("*.meta"):
        info = json.loads(meta.read_text())
        src = meta.with_suffix("")  # mutants/<path>.py
        text = src.read_text(errors="replace") if src.exists() else ""
        for key, code in info.get("exit_code_by_key", {}).items():
            if code is None or (code not in KILLED and code not in SURVIVED):
                status = "NO_COVERAGE" if code in (33, 34) else "NOT_RUN"
                if status == "NOT_RUN":
                    continue
            else:
                status = "KILLED" if code in KILLED else "SURVIVED"
            fn = key.rsplit("__mutmut_", 1)[0]
            module, _, func = fn.rpartition(".")
            func_clean = func.replace("x_", "", 1).replace("xǁ", "").replace("ǁ", ".")
            # best-effort extraction of original/mutated bodies for operator + line
            m_orig = re.search(rf"def {re.escape(func)}__mutmut_orig\(.*?(?=\ndef |\Z)", text, re.S)
            m_mut = re.search(rf"def {re.escape(key.rsplit('.', 1)[-1])}\(.*?(?=\ndef |\Z)", text, re.S)
            op = guess_operator(m_orig.group(0), m_mut.group(0)) if m_orig and m_mut else "OtherMutator"
            line = text[: m_mut.start()].count("\n") + 1 if m_mut else 0
            cov = tests_by_fn.get(fn, []) if status != "NO_COVERAGE" else []
            rows.append(dict(project=a.project, split=a.split, source_file=str(src.relative_to(mdir)),
                             mutated_class=module, mutated_method=func_clean, line=line, mutator=op,
                             killed=int(status == "KILLED"), status=status,
                             covering_tests="|".join(cov), killing_tests="", line_text=""))
    with open(a.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]) if rows else ["project"])
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {len(rows)} mutants -> {a.out}")


if __name__ == "__main__":
    main()
