# Method — ACE-MT (Active, Calibrated, model-assisted Estimation of Mutation score)

## Problem
A project has N mutants. Running all of them with PIT (full matrix) is expensive. We may
execute only `B = budget · N` of them and must return an estimate of the mutation score
`MS = (#killed) / N` **and** a 95 % confidence interval.

## Pipeline
1. **Ground truth (offline, once):** PIT with `fullMutationMatrix=true` → `mutations.xml`
   (status, covering tests, killing tests per mutant).
2. **Features** (no execution of mutants needed):
   * *operator*: PIT mutator, operator family;
   * *static*: statement kind, nesting depth, method LOC/complexity, relative position,
     class size, constructor/lambda/accessor, #params, return type, bytecode index/block,
     #mutants on the same line/method;
   * *coverage*: #covering tests, covered flag, #covering test classes;
   * *oracle* (PMT-style): assertions in covering tests (sum/max/mean), tests without
     assertions, test LOC, tests that call the mutated method directly / assert on it,
     tests named after the class.
3. **Cross-project model:** XGBoost (or LightGBM/RF/LogReg) trained on the other
   projects, **isotonic calibration** with project-grouped CV → probability `p_i` that
   mutant *i* is killed.
4. **Free information:** uncovered mutants survive for sure (cost 0, applied to all methods).
5. **Active sampling with a difference estimator** (the novelty). For each draw:
   * sampling distribution over *not yet executed* covered mutants
     `q_i ∝ (1−mix)·sqrt(p_i(1−p_i)) + mix·uniform` (uncertainty-weighted, `mix=0.3`
     keeps every mutant reachable → unbiasedness);
   * execute mutant j, observe `y_j`;
   * unbiased estimate of #killed:
     `T_j = Σ_executed y + Σ_unexecuted p + (y_j − p_j)/q_j`.
6. **Project adaptation between rounds** (4 rounds): Platt recalibration of `p` on the
   labels seen so far (removes the project-level bias of the cross-project model).
   `p` and `q` only depend on past labels ⇒ each `T_j` stays unbiased (martingale argument).
7. **Estimate and CI:** `T̂ = mean(T_j)`, `Var = s²(T_j)/n`, normal 95 % CI (or bootstrap).
8. **Empirical-Bayes combination:** with the adapted model's own prediction
   `M = Σ_executed y + Σ_unexecuted p`, return `w·M + (1−w)·T̂` with
   `w = V / (V + max(0, (T̂−M)² − V))` — trust the model only as much as the data cannot
   show it is biased. Big win at very small budgets (5 %). CI keeps the unbiased half-width.

## Baselines (same budget, same data, same machine)
| Baseline | Implementation |
|---|---|
| Full PIT | gold standard (cost 100 %) |
| Random sampling | SRS without replacement, finite-population-corrected CI |
| Stratified sampling | by operator family, proportional allocation |
| Selective mutation | whole operator families in a fixed priority order while they fit the budget |
| PMT (Zhang et al.) | random forest, PMT feature set, hard labels, no execution |
| Seshat-lite | TF-IDF of the mutated source line + operator + method name → logistic regression (approximation of Seshat's token-based idea; check the real tool at project start) |
| Model only | sum of calibrated probabilities (no execution) |
| Active top-k | classic uncertainty AL: execute the B most uncertain, model for the rest |

## Research questions
RQ1 prediction (precision/recall/MCC/AUC/Brier/ECE; within- vs cross-project) ·
RQ2 MAE vs budget 5/10/20 % + CI coverage + Wilcoxon/A12 ·
RQ3 cost (mutants & test runs executed, estimated seconds saved) ·
RQ4 Kendall τ when ranking 20 random sub-suites per project ·
RQ5 ablation (feature groups, sampling policy, adaptation, combination, rounds, calibration).

## Known threats to validity
Small self-written subjects (replace/extend with Apache Commons via `java/subjects.csv`);
equivalent mutants counted as survived (PIT definition); time saved is estimated from
test-run fractions, not measured per mutant; Seshat is approximated.
