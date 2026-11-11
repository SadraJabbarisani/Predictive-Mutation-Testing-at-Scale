"""Parse PIT ``mutations.xml`` produced with ``fullMutationMatrix=true``.

فارسی: خواندن خروجی XML ابزار PIT (با ماتریس کامل)؛ برای هر mutant یک سطر با تست‌های پوشش‌دهنده و کشنده.

Output of :func:`parse_mutations_xml` is a DataFrame with one row per mutant:

=====================  =====================================================
column                 meaning
=====================  =====================================================
mutant_id              ``<project>:<n>`` (stable order of the XML)
project                subject name
source_file, mutated_class, mutated_method, method_desc, line, index, block
mutator                short operator name (e.g. ``NegateConditionalsMutator``)
status                 PIT status (KILLED, SURVIVED, NO_COVERAGE, TIMED_OUT ...)
killed                 1 if PIT reports ``detected='true'`` (= ground truth)
covering_tests         list[str] tests covering the mutated line  (pre-execution info)
killing_tests          list[str] tests that kill the mutant      (LABEL INFO - never a feature)
n_tests_run            PIT ``numberOfTestsRun``                    (LABEL INFO - never a feature)
=====================  =====================================================
"""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path

import pandas as pd

_TEST_RE_J5 = re.compile(r"\[class:([^\]]+)\]/\[method:([^\(\]]+)")
_TEST_RE_J4 = re.compile(r"^([\w$]+)\(([\w.$]+)\)$")


def short_mutator(full: str) -> str:
    """``org.pitest...gregor.mutators.returns.NullReturnValsMutator`` -> ``NullReturnValsMutator``."""
    return full.rsplit(".", 1)[-1]


def normalize_test(name: str) -> str:
    """Return ``fully.qualified.TestClass#method`` for JUnit4/5 PIT test ids."""
    name = name.strip()
    m = _TEST_RE_J5.search(name)
    if m:
        return f"{m.group(1)}#{m.group(2)}"
    m = _TEST_RE_J4.match(name)
    if m:
        return f"{m.group(2)}#{m.group(1)}"
    return name


def _split_tests(text: str | None) -> list[str]:
    if not text:
        return []
    return sorted({normalize_test(t) for t in text.split("|") if t.strip()})


def parse_mutations_xml(path: str | Path, project: str) -> pd.DataFrame:
    root = ET.parse(str(path)).getroot()
    rows = []
    for i, m in enumerate(root.iter("mutation")):
        g = lambda tag: (m.findtext(tag) or "").strip()  # noqa: E731
        idx = [int(x.text) for x in m.iter("index")] or [0]
        blk = [int(x.text) for x in m.iter("block")] or [0]
        killing = _split_tests(m.findtext("killingTests"))
        succeeding = _split_tests(m.findtext("succeedingTests"))
        covering = _split_tests(m.findtext("coveringTests"))
        if not covering:  # older PIT versions: covering = killing ∪ succeeding
            covering = sorted(set(killing) | set(succeeding))
        rows.append(dict(
            mutant_id=f"{project}:{i}",
            project=project,
            source_file=g("sourceFile"),
            mutated_class=g("mutatedClass"),
            mutated_method=g("mutatedMethod"),
            method_desc=g("methodDescription"),
            line=int(g("lineNumber") or 0),
            index=idx[0],
            block=blk[0],
            mutator=short_mutator(g("mutator")),
            description=g("description"),
            status=m.get("status"),
            killed=int(m.get("detected") == "true"),
            n_tests_run=int(m.get("numberOfTestsRun") or 0),
            covering_tests=covering,
            killing_tests=killing,
        ))
    return pd.DataFrame(rows)
