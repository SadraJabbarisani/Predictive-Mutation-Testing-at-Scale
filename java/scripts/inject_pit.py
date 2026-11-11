#!/usr/bin/env python3
"""Inject a PIT (pitest-maven) plugin block into a Maven pom.xml.

فارسی: افزودن خودکار پلاگین PIT (با fullMutationMatrix) به pom.xml هر پروژه.

The block enables the *full mutation matrix* (every covering test is run
against every mutant), which is what we need as ground truth.

Usage:
    python inject_pit.py path/to/pom.xml [--pit 1.30.1] [--junit5 1.2.3]
                         [--target-classes 'org.apache.commons.cli.*']
                         [--mutators DEFAULTS] [--threads 4]

Idempotent: if a pitest plugin already exists directly under <build><plugins>
it is replaced.  A backup ``pom.xml.bak`` is written once.
"""
import argparse
import shutil
from pathlib import Path

from lxml import etree

NS = "http://maven.apache.org/POM/4.0.0"
N = "{%s}" % NS


def _el(parent, tag, text=None):
    e = etree.SubElement(parent, N + tag)
    if text is not None:
        e.text = text
    return e


def build_plugin(pit, junit5, target_classes, target_tests, mutators, threads, timeout_const):
    p = etree.Element(N + "plugin")
    _el(p, "groupId", "org.pitest")
    _el(p, "artifactId", "pitest-maven")
    _el(p, "version", pit)
    if junit5:
        deps = _el(p, "dependencies")
        d = _el(deps, "dependency")
        _el(d, "groupId", "org.pitest")
        _el(d, "artifactId", "pitest-junit5-plugin")
        _el(d, "version", junit5)
    cfg = _el(p, "configuration")
    _el(cfg, "fullMutationMatrix", "true")
    of = _el(cfg, "outputFormats")
    _el(of, "param", "XML")
    _el(of, "param", "HTML")
    _el(cfg, "timestampedReports", "false")
    _el(cfg, "threads", str(threads))
    _el(cfg, "timeoutConstant", str(timeout_const))
    _el(cfg, "exportLineCoverage", "true")
    _el(cfg, "failWhenNoMutations", "false")
    if mutators:
        m = _el(cfg, "mutators")
        for x in mutators.split(","):
            _el(m, "mutator", x.strip())
    if target_classes:
        tc = _el(cfg, "targetClasses")
        for x in target_classes.split(","):
            _el(tc, "param", x.strip())
    if target_tests:
        tt = _el(cfg, "targetTests")
        for x in target_tests.split(","):
            _el(tt, "param", x.strip())
    return p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pom")
    ap.add_argument("--pit", default="1.30.1")
    ap.add_argument("--junit5", default="1.2.3", help="'' for JUnit4 projects")
    ap.add_argument("--target-classes", default="")
    ap.add_argument("--target-tests", default="")
    ap.add_argument("--mutators", default="DEFAULTS")
    ap.add_argument("--threads", type=int, default=4)
    ap.add_argument("--timeout-const", type=int, default=4000)
    a = ap.parse_args()

    pom = Path(a.pom)
    bak = pom.with_suffix(".xml.bak")
    if not bak.exists():
        shutil.copy(pom, bak)
    parser = etree.XMLParser(remove_blank_text=False)
    tree = etree.parse(str(pom), parser)
    root = tree.getroot()
    build = root.find(N + "build")
    if build is None:
        build = _el(root, "build")
    plugins = build.find(N + "plugins")
    if plugins is None:
        plugins = _el(build, "plugins")
    for old in plugins.findall(N + "plugin"):
        aid = old.find(N + "artifactId")
        if aid is not None and aid.text == "pitest-maven":
            plugins.remove(old)
    plugins.append(build_plugin(a.pit, a.junit5, a.target_classes, a.target_tests,
                                a.mutators, a.threads, a.timeout_const))
    tree.write(str(pom), xml_declaration=True, encoding="UTF-8")
    print(f"[inject_pit] PIT {a.pit} injected into {pom}")


if __name__ == "__main__":
    main()
