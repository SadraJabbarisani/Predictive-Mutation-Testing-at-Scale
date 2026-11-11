"""Command line interface.

فارسی: رابط خط فرمان. دستور اصلی: python -m pmt all  (ساخت دیتاست + اجرای همه‌ی RQها + گزارش)

    python -m pmt dataset  [--config C]          # data/raw -> data/processed (or synthetic / generic csv)
    python -m pmt run      [--config C] [--only rq1 rq2 ...] [--set key=value ...]
    python -m pmt report   [--config C]          # results/*.csv -> figures + summary.md/json
    python -m pmt all      [--config C]          # dataset + run + report
    python -m pmt estimate --project NAME --budget 0.1 [--method ace]   # one-off estimate
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from .config import load_config


def _dataset(cfg):
    src = cfg["dataset"]["source"]
    p = cfg["paths"]
    if src == "pit":
        from .data.dataset import build_dataset
        data = build_dataset(p["raw"], p["processed"], p.get("subjects"))
    elif src == "synthetic":
        from .data.synthetic import generate
        s = cfg["dataset"]["synthetic"]
        data = generate(s["n_projects"], tuple(s["mutants_per_project"]), s["seed"])
    elif src == "generic_csv":
        from .data.generic_csv import load_generic_csv
        data = load_generic_csv(cfg["dataset"]["generic_csv"])
    else:
        raise ValueError(src)
    Path(p["processed"]).mkdir(parents=True, exist_ok=True)
    data.to_pickle(Path(p["processed"]) / "mutants.pkl")
    print(f"[dataset] {len(data)} mutants, {data['project'].nunique()} projects, "
          f"kill rate {data['killed'].mean():.3f} -> {p['processed']}/mutants.pkl")
    return data


def main(argv=None):
    ap = argparse.ArgumentParser(prog="pmt", description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("command", choices=["dataset", "run", "report", "all", "estimate"])
    ap.add_argument("--config", default="configs/default.yaml")
    ap.add_argument("--set", nargs="*", default=[], help="override config keys, e.g. seeds=5 model.name=rf")
    ap.add_argument("--only", nargs="*", default=None, help="subset of rq1 rq2 rq3 rq4 rq5")
    ap.add_argument("--project")
    ap.add_argument("--budget", type=float, default=0.1)
    ap.add_argument("--method", default="ace")
    a = ap.parse_args(argv)
    cfg = load_config(a.config, a.set)

    if a.command in ("dataset", "all"):
        data = _dataset(cfg)
    if a.command in ("run", "all", "estimate"):
        from .data.dataset import load_dataset
        data = load_dataset(cfg["paths"]["processed"])
    if a.command in ("run", "all"):
        from .experiments import run_all
        run_all(cfg, data, a.only)
    if a.command in ("report", "all"):
        from .report import make_report
        make_report(cfg["paths"]["results"])
        print(f"[report] {cfg['paths']['results']}/summary.md")
    if a.command == "estimate":
        from .estimators import ESTIMATORS
        from .experiments import Pipeline
        pl = Pipeline(cfg, data)
        ctx = pl.target(a.project)
        opts = cfg["methods"].get(a.method, {})
        e = ESTIMATORS[a.method](ctx, a.budget, np.random.default_rng(cfg["seed"]), **opts)
        print(f"{a.project}: estimated score {e.score:.3f}  95% CI [{e.ci_low:.3f}, {e.ci_high:.3f}]  "
              f"executed {e.n_executed}/{ctx.N} mutants   (true score {ctx.true_score:.3f})")


if __name__ == "__main__":
    main()
