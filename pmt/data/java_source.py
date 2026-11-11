"""Light-weight static analysis of Java source (no external parser needed).

فارسی: تحلیل ایستای سبک کد Java با regex و شمارش آکولاد (بدون parser خارجی).

We only need a handful of robust signals, so a brace/regex scanner is enough:
statement kind of the mutated line, nesting depth, method span/size,
cyclomatic complexity approximation, class size; and for test files the
number of assertions per test method (PMT's "test oracle" features).

Replace with a real parser (e.g. ``javalang`` or tree-sitter) by keeping the
same return types if more precise AST features are needed.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

DECISION_RE = re.compile(r"\b(if|for|while|case|catch)\b|&&|\|\||\?")
ASSERT_RE = re.compile(r"\b(assert\w*|fail|verify)\s*\(")
METHOD_DECL_RE = re.compile(
    r"^\s*(?:@\w+(?:\([^)]*\))?\s+)*(?:(?:public|protected|private|static|final|abstract|synchronized|default)\s+)*"
    r"(?:<[^>]+>\s+)?(?P<type>[\w\[\]<>,.?]+\s+)?(?P<name>\w+)\s*\(")
KEYWORDS = {"if", "for", "while", "switch", "catch", "return", "new", "throw", "else", "do", "try"}

STATEMENT_KINDS = ["if", "loop", "return", "throw", "assign", "call", "decl", "switch", "other"]


def statement_kind(line: str) -> str:
    s = line.strip()
    if re.match(r"^(\}\s*)?(else\s+)?if\b", s) or s.startswith("} else if"):
        return "if"
    if re.match(r"^(for|while|do)\b", s):
        return "loop"
    if re.match(r"^(switch|case|default)\b", s):
        return "switch"
    if s.startswith("return"):
        return "return"
    if s.startswith("throw"):
        return "throw"
    if re.search(r"[^=!<>]=[^=]", s) or re.search(r"(\+\+|--|\+=|-=|\*=|/=)", s):
        if re.match(r"^[\w<>\[\],. ]+\s+\w+\s*=", s):
            return "decl"
        return "assign"
    if re.search(r"\w\s*\(", s):
        return "call"
    return "other"


@dataclass
class MethodSpan:
    name: str
    start: int  # 1-based inclusive
    end: int
    complexity: int


@dataclass
class JavaFile:
    lines: list[str]
    depth: list[int]                       # brace depth at start of each line (index 0 = line 1)
    methods: list[MethodSpan] = field(default_factory=list)

    @property
    def loc(self) -> int:
        return sum(1 for ln in self.lines if ln.strip() and not ln.strip().startswith(("//", "*", "/*")))


def _strip_strings(s: str) -> str:
    s = re.sub(r'"(\\.|[^"\\])*"', '""', s)
    s = re.sub(r"'(\\.|[^'\\])*'", "''", s)
    return s.split("//")[0]


@lru_cache(maxsize=4096)
def load_java(path: str) -> JavaFile | None:
    p = Path(path)
    if not p.exists():
        return None
    lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
    depth, d = [], 0
    clean = [_strip_strings(x) for x in lines]
    for c in clean:
        depth.append(d)
        d += c.count("{") - c.count("}")
    jf = JavaFile(lines=lines, depth=depth)
    # methods: a declaration line at class-body depth (1, or 2 for nested/anonymous classes)
    class_names = set(re.findall(r"\b(?:class|enum|record)\s+(\w+)", "\n".join(clean)))
    i = 0
    while i < len(clean):
        m = METHOD_DECL_RE.match(clean[i])
        head = clean[i].split("{")[0]
        ok = (m is not None and depth[i] in (1, 2) and m.group("name") not in KEYWORDS
              and ";" not in head and "=" not in head
              and (m.group("type") is not None or m.group("name") in class_names))
        if not ok:
            i += 1
            continue
        d0, d, opened, end = depth[i], depth[i], False, None
        for k in range(i, len(clean)):
            if ";" in clean[k] and not opened and "{" not in clean[k]:
                break  # abstract / interface method without body
            d += clean[k].count("{") - clean[k].count("}")
            opened = opened or d > d0 or ("{" in clean[k] and "}" in clean[k])
            if opened and d <= d0:
                end = k
                break
        if end is None:
            i += 1
            continue
        body = " ".join(clean[i:end + 1])
        jf.methods.append(MethodSpan(m.group("name"), i + 1, end + 1, 1 + len(DECISION_RE.findall(body))))
        i = end + 1
    return jf


def method_for(jf: JavaFile, method: str, line: int, class_simple: str) -> MethodSpan | None:
    """Find the span containing ``line`` (preferring the PIT method name)."""
    name = method
    if method == "<init>":
        name = class_simple
    elif method.startswith("lambda$"):
        parts = method.split("$")
        name = parts[1] if len(parts) > 1 else method
    cands = [m for m in jf.methods if m.start <= line <= m.end]
    named = [m for m in cands if m.name == name]
    pool = named or cands
    return min(pool, key=lambda m: m.end - m.start) if pool else None


@lru_cache(maxsize=256)
def test_assertions(test_root: str) -> dict[str, tuple[int, int, str]]:
    """Map ``fq.TestClass#method`` -> (n_assertions, loc, body) for every test method under test_root."""
    out: dict[str, tuple[int, int, str]] = {}
    root = Path(test_root)
    if not root.exists():
        return out
    for f in root.rglob("*.java"):
        rel = f.relative_to(root).with_suffix("")
        cls = ".".join(rel.parts)
        jf = load_java(str(f))
        if jf is None:
            continue
        for ms in jf.methods:
            body = "\n".join(jf.lines[ms.start - 1:ms.end])
            out[f"{cls}#{ms.name}"] = (len(ASSERT_RE.findall(body)), ms.end - ms.start + 1, body)
    return out
