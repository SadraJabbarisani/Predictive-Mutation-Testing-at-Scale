#!/usr/bin/env bash
# Reproduce everything from scratch:  bash scripts/run_all.sh [quick]
#   1) PIT full-matrix on every enabled subject (skips subjects already in data/raw)
#   2) dataset -> experiments RQ1..RQ5 -> report (results/summary.md, results/figures/)
set -e
cd "$(dirname "$0")/.."
CFG=configs/default.yaml; [ "${1:-}" = "quick" ] && CFG=configs/quick.yaml
if command -v mvn >/dev/null; then bash java/scripts/collect_all.sh; else echo "[warn] no maven: using bundled data/raw"; fi
python3 -m pmt all --config "$CFG"
python3 -m pytest -q
