"""Synthetic mutant datasets with the *same columns* as the PIT pipeline.

فارسی: داده‌ی مصنوعی فقط برای تست و مطالعه‌ی مقیاس؛ هرگز به‌عنوان نتیجه‌ی واقعی گزارش نشود.

Use for: scaling studies (many / large projects), unit tests, and running the
pipeline when Java/PIT is not available. NEVER report synthetic numbers as
real results. The generative model is intentionally simple and documented:

    logit P(killed) = project_effect + operator_effect + 0.8*log1p(n_cover)
                      + 0.5*direct_asserts - 0.15*nesting + noise
    (uncovered mutants are never killed)
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .dataset import operator_family

OPERATORS = {  # name: (effect on kill logit, relative frequency)
    "NegateConditionalsMutator": (1.2, 11), "ConditionalsBoundaryMutator": (-0.9, 6),
    "MathMutator": (0.8, 11), "IncrementsMutator": (0.6, 2), "InlineConstantMutator": (-0.6, 18),
    "NonVoidMethodCallMutator": (0.2, 14), "VoidMethodCallMutator": (-0.4, 2),
    "PrimitiveReturnsMutator": (1.0, 3), "NullReturnValsMutator": (1.1, 2),
    "BooleanTrueReturnValsMutator": (0.5, 2), "RemoveConditionalMutator_EQUAL_IF": (0.3, 5),
    "RemoveConditionalMutator_ORDER_ELSE": (0.0, 5), "ConstructorCallMutator": (0.4, 3),
    "MemberVariableMutator": (-0.5, 2),
}
STMT = ["if", "loop", "return", "assign", "call", "decl"]


def generate(n_projects: int = 12, mutants_per_project=(300, 1500), seed: int = 7,
             heldout: int = 2) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    ops = list(OPERATORS)
    freq = np.array([OPERATORS[o][1] for o in ops], float)
    freq /= freq.sum()
    frames = []
    for pi in range(n_projects):
        name = f"synth-{pi:02d}"
        n = int(rng.integers(*mutants_per_project))
        n_tests = int(rng.integers(20, 120))
        tests = [f"syn.p{pi}.T{t // 10}#t{t}" for t in range(n_tests)]
        t_asserts = rng.poisson(2.0, n_tests)
        proj_eff = rng.normal(0.3, 0.6)
        coverage_rate = rng.uniform(0.55, 0.95)
        n_classes = max(3, n // 60)
        cls = rng.integers(0, n_classes, n)
        method = cls * 10 + rng.integers(0, 8, n)
        line = method * 20 + rng.integers(1, 15, n)
        op = rng.choice(ops, n, p=freq)
        nesting = rng.integers(1, 6, n)
        covered = rng.random(n) < coverage_rate
        rows = []
        for i in range(n):
            cov = list(rng.choice(tests, int(rng.integers(1, 8)), replace=False)) if covered[i] else []
            direct = sum(1 for t in cov if rng.random() < 0.5)
            da = sum(int(t_asserts[tests.index(t)] > 0) for t in cov[:direct])
            z = (proj_eff + OPERATORS[op[i]][0] + 0.8 * np.log1p(len(cov)) + 0.5 * da - 0.15 * nesting[i]
                 + rng.normal(0, 0.8))
            killed = int(covered[i] and rng.random() < 1 / (1 + np.exp(-z)))
            killing = sorted(rng.choice(cov, int(rng.integers(1, len(cov) + 1)), replace=False)) if killed else []
            a = [t_asserts[tests.index(t)] for t in cov]
            rows.append(dict(
                mutant_id=f"{name}:{i}", project=name, source_file=f"C{cls[i]}.java",
                mutated_class=f"syn.p{pi}.C{cls[i]}", mutated_method=f"m{method[i]}", method_desc="(I)I",
                line=int(line[i]), index=int(rng.integers(0, 80)), block=int(rng.integers(0, 12)), mutator=op[i],
                description="synthetic", status="KILLED" if killed else ("SURVIVED" if cov else "NO_COVERAGE"),
                killed=killed, n_tests_run=len(cov), covering_tests=sorted(cov), killing_tests=list(killing),
                line_text=f"{rng.choice(STMT)} x{op[i][:3]}", nesting=float(nesting[i]),
                stmt_kind=str(rng.choice(STMT)), line_tokens=float(rng.integers(3, 20)),
                has_cmp=int(rng.random() < .4), has_arith=int(rng.random() < .4),
                method_loc=float(rng.integers(3, 40)), method_cc=float(rng.integers(1, 12)),
                rel_pos=float(rng.random()), class_loc=float(rng.integers(30, 400)),
                n_methods=float(rng.integers(3, 30)), n_cover=len(cov), covered=int(bool(cov)),
                n_cover_classes=len({t.split("#")[0] for t in cov}), assert_sum=float(sum(a)),
                assert_max=float(max(a) if a else 0), assert_mean=float(np.mean(a) if a else 0),
                n_cover_no_assert=int(sum(x == 0 for x in a)), test_loc_mean=float(rng.integers(3, 20) if a else 0),
                direct_tests=direct, direct_asserts=da, class_named_tests=direct))
        df = pd.DataFrame(rows)
        df["op_family"] = df["mutator"].map(operator_family)
        df["is_ctor"] = 0
        df["is_lambda"] = 0
        df["is_accessor"] = 0
        df["n_params"] = 1
        df["ret_kind"] = "int"
        df["mutants_on_line"] = df.groupby(["mutated_class", "line"])["mutant_id"].transform("count")
        df["mutants_in_method"] = df.groupby(["mutated_class", "mutated_method"])["mutant_id"].transform("count")
        df["split"] = "heldout" if pi >= n_projects - heldout else "train"
        frames.append(df)
    return pd.concat(frames, ignore_index=True)
