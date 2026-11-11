# Data formats

## 1. PIT raw data (`data/raw/<project>/`)
| file | content |
|---|---|
| `mutations.xml` | PIT XML report, generated with `fullMutationMatrix=true` (has `<killingTests>`, `<succeedingTests>`, `<coveringTests>`) |
| `linecoverage.xml` | PIT line coverage (kept for future features) |
| `src/main`, `src/test` | copy of the sources (static + test-oracle features) |
| `meta.json` | PIT runtime in seconds, PIT version, mutators, threads, commit |
| `pit.log` | console output |

## 2. Processed dataset (`data/processed/mutants.csv` / `.pkl`)
One row per mutant. Identifiers: `mutant_id, project, split, source_file, mutated_class,
mutated_method, method_desc, line, index, block, mutator, description`.
Label/metadata (never features): `status, killed, killing_tests, n_tests_run`.
Features: see `pmt/features.py::FEATURE_GROUPS`. In the CSV, test lists are `|`-separated.

## 3. Generic CSV (any language: Python/mutmut, JS/Stryker, C#/Stryker.NET …)
Minimum columns:

```
project,mutated_class,mutated_method,line,mutator,killed,covering_tests,killing_tests
calc,calc.ops,add,12,MathMutator,1,tests/test_ops.py::test_add|tests/test_ops.py::test_sum,tests/test_ops.py::test_add
```
Optional: `split` (train/heldout), `source_file`, `line_text`, `status`, and any numeric feature
from `FEATURE_GROUPS` (missing ones are filled with 0/NaN). Load with:

```bash
python -m pmt all --set dataset.source=generic_csv dataset.generic_csv=my.csv
```
`python_mutmut/mutmut_to_csv.py` produces this format from a mutmut 3 run.
