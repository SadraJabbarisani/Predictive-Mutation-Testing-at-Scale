# Recipes (each touches 1–2 files)

**Add a real Java project** — add a row to `java/subjects.csv` (`git_url`, `target_classes`
package filter, `split`, `enabled=1`), run `bash java/scripts/collect_all.sh <name>`, then
`python -m pmt all`. JUnit 4 projects: leave the `junit5_plugin` column empty.

**Change budgets / repetitions** — `configs/default.yaml` (`budgets`, `seeds`) or
`--set budgets=[0.02,0.05] seeds=50`.

**Switch model** — `--set model.name=lightgbm model.calibration=sigmoid`.

**Add a feature** — compute the column in `pmt/data/dataset.py` (`add_static_features` if it
depends only on code, `add_suite_features` if it depends on the test suite), add its name to a
group in `pmt/features.py`, rebuild with `python -m pmt dataset`.

**Add a baseline** — write `def my_method(ctx, budget_frac, rng, **opts) -> Estimate` in
`pmt/estimators.py`, register it in `ESTIMATORS`, add `my_method: {}` under `methods:` in the
YAML. It is then included in RQ2/RQ3 tables, stats and figures automatically (give it a colour/
label in `pmt/report.py::COLORS/LABELS`).

**Change ACE-MT** — options in YAML `methods.ace` (`rounds, policy: hybrid|uniform|uncertainty,
mix, adapt: platt|none|refit, neighbors: [line, method], combine, ci: normal|bootstrap`);
logic in `pmt/estimators.py::ace`.

**Add an ablation variant** — under `ablation.variants` write `name: {option: value}` (delta
from the ACE default; `_calibration: none` changes the base model's calibration).

**Python track** — see `python_mutmut/mutmut_to_csv.py` docstring.

**Scaling study without Java** — `--set dataset.source=synthetic dataset.synthetic.n_projects=30`
(write outputs to another folder: `--set paths.results=results_synth paths.processed=data/synth`).

**Rebuild slides** — `node presentation/build_deck.js` (reads `results/summary.json`).
