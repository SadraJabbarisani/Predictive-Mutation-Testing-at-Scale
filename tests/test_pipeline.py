"""Fast unit tests: `pytest -q` (no Java needed; uses bundled data or synthetic data)."""
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from pmt.data.dataset import add_suite_features, build_project
from pmt.data.java_source import statement_kind
from pmt.data.pit_xml import normalize_test
from pmt.data.synthetic import generate
from pmt.estimators import ESTIMATORS, Target
from pmt.features import FEATURE_GROUPS, Featurizer, columns_for
from pmt.metrics import a12, ece

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"


def test_normalize_test_names():
    j5 = "a.BTest.[engine:junit-jupiter]/[class:a.BTest]/[method:foo()]"
    assert normalize_test(j5) == "a.BTest#foo"
    assert normalize_test("foo(a.BTest)") == "a.BTest#foo"


def test_statement_kind():
    assert statement_kind("if (a < b) {") == "if"
    assert statement_kind("for (int i = 0; i < n; i++) {") == "loop"
    assert statement_kind("return x + 1;") == "return"


@pytest.mark.skipif(not (RAW / "toy-bank" / "mutations.xml").exists(), reason="bundled PIT data missing")
def test_build_project_no_leakage():
    df = build_project(RAW / "toy-bank", "toy-bank")
    assert len(df) > 50
    assert set(df["killed"].unique()) <= {0, 1}
    feats = columns_for(list(FEATURE_GROUPS))
    for leak in ("status", "killed", "killing_tests", "n_tests_run"):
        assert leak not in feats
    # uncovered mutants are never killed
    assert df.loc[df["covered"] == 0, "killed"].sum() == 0


@pytest.mark.skipif(not (RAW / "toy-bank" / "mutations.xml").exists(), reason="bundled PIT data missing")
def test_subsuite_labels_monotone():
    df = build_project(RAW / "toy-bank", "toy-bank")
    tests = sorted({t for ts in df["covering_tests"] for t in ts})
    sub = add_suite_features(df, {}, set(tests[: len(tests) // 2]))
    assert sub["killed"].sum() <= df["killed"].sum()


def _ctx(seed=0, n=600):
    rng = np.random.default_rng(seed)
    p = rng.uniform(0.05, 0.95, n)
    y = (rng.random(n) < p).astype(int)
    df = pd.DataFrame(dict(covered=1, op_family=rng.choice(["a", "b", "c"], n), mutated_class="C",
                           mutated_method="m", method_desc="()V", line=rng.integers(0, 50, n)))
    return Target(df=df, y=y, p=p, cost=np.ones(n), extra=dict(p_pmt=p, p_seshat=p))


@pytest.mark.parametrize("name", ["random", "stratified", "selective", "pmt", "model_only", "active_topk", "ace",
                                  "ace_strat"])
def test_estimators_run_and_respect_budget(name):
    ctx = _ctx()
    e = ESTIMATORS[name](ctx, 0.1, np.random.default_rng(1))
    assert 0 <= e.score <= 1
    assert e.n_executed <= round(0.1 * ctx.N)


def test_ace_is_close_to_unbiased():
    ctx = _ctx(3)
    est = [ESTIMATORS["ace"](ctx, 0.1, np.random.default_rng(s), combine=False).score for s in range(200)]
    assert abs(np.mean(est) - ctx.true_score) < 0.01


def test_full_is_exact():
    ctx = _ctx(4)
    assert ESTIMATORS["full"](ctx, 1.0, np.random.default_rng(0)).score == pytest.approx(ctx.true_score)


def test_featurizer_and_synthetic():
    d = generate(3, (80, 120), seed=1)
    fz = Featurizer(columns_for(list(FEATURE_GROUPS))).fit(d)
    X = fz.matrix(d)
    assert X.shape[0] == len(d) and np.isfinite(np.nan_to_num(X)).all()


def test_metrics():
    assert a12([1, 2, 3], [1, 2, 3]) == pytest.approx(0.5)
    assert ece(np.array([0, 1]), np.array([0.0, 1.0])) == pytest.approx(0.0)
