# CONTEXT.md — read this first (written for a new chat / AI assistant)

**Goal of the project (Team 8, "Predictive Mutation Testing at Scale"):** estimate the PIT
mutation score of a Java project while executing only a small budget of mutants (5–20 %),
with a confidence interval, and compare against the baselines from the course guide.
**Proposed method:** ACE-MT, implemented in `pmt/estimators.py::ace`.

## Map — what is where (edit only the file you need)

| Need to change… | File | Notes |
|---|---|---|
| Experiment numbers (budgets, seeds, methods, model) | `configs/default.yaml` | `--set key=value` on the CLI overrides any key |
| Proposed algorithm ACE-MT | `pmt/estimators.py` → `ace()` | options = YAML `methods.ace` |
| Baselines (random, stratified, selective, PMT, Seshat-lite, model-only, top-k) | `pmt/estimators.py` (+ PMT/Seshat models in `pmt/experiments.py::pmt_probs/seshat_probs`) | add a baseline = function + entry in `ESTIMATORS` + line in YAML `methods` |
| Features | `pmt/data/dataset.py` (compute) + `pmt/features.py` (`FEATURE_GROUPS`) | never use `status/killed/killing_tests/n_tests_run` as features (leakage) |
| ML model / calibration | `pmt/models.py` | `model.name: xgboost|lightgbm|rf|logreg|hgb`, `model.calibration: isotonic|sigmoid|none` |
| Research questions RQ1–RQ5 | `pmt/experiments.py` (`Pipeline.rq1..rq5`) | each writes `results/rqN_*.csv` |
| Tables / figures / summary.json | `pmt/report.py` | slides read `results/summary.json` |
| Java subjects & PIT | `java/subjects.csv`, `java/scripts/run_pit.sh`, `java/scripts/inject_pit.py` | `enabled=1` to include a subject; `split=heldout` keeps it for final eval |
| Python / other language data | `python_mutmut/mutmut_to_csv.py`, `pmt/data/generic_csv.py`, `docs/DATA_FORMAT.md` | `dataset.source: generic_csv` |
| Synthetic data (scaling, no Java) | `pmt/data/synthetic.py` | `dataset.source: synthetic` — never report as real results |
| Slides | `presentation/build_deck.js` (pptxgenjs) | text in Persian, font Vazirmatn (`THEME.headFontFace/bodyFontFace`; files in `presentation/fonts/`); numbers come from `results/summary.json` |

## Commands
```bash
pip install -r requirements.txt
python -m pmt all --config configs/quick.yaml      # ~3 min smoke run
python -m pmt all                                   # full run (default.yaml, ~20-30 min on 4 CPUs)
python -m pmt run --only rq2 --set seeds=5          # one RQ, override config
python -m pmt estimate --project toy-graph --budget 0.1
bash java/scripts/collect_all.sh                    # re-run PIT (needs Java 11+ and Maven)
pytest -q                                           # unit tests
node presentation/build_deck.js                     # rebuild the .pptx from results/summary.json
```

## Data facts
* `data/raw/<project>/mutations.xml` = PIT 1.30.1, `fullMutationMatrix=true`, mutators `ALL`.
  10 self-written Java subjects (`java/subjects/toy-*`), 2,451 mutants, 8 train + 2 held-out
  (`toy-graph`, `toy-validator`).
* `data/processed/mutants.pkl|csv` = one row per mutant (features + `killed`).
* Score = killed / all mutants (TIMED_OUT counts as killed, NO_COVERAGE as survived).

## Protocol (do not break)
cross-project = leave-one-project-out over train projects; held-out projects are only
predicted by a model trained on all train projects; no tuning on held-out; every stochastic
method runs `seeds` times; compare with Wilcoxon + Vargha–Delaney A12 (`results/rq2_stats.csv`).
