#!/usr/bin/env bash
# Clone (if needed) and run PIT full-matrix on every *enabled* subject in java/subjects.csv.
# فارسی: اجرای PIT روی همه‌ی پروژه‌های فعال (enabled=1) در java/subjects.csv
# Usage: java/scripts/collect_all.sh [only_name ...]     (naming a subject runs it even if enabled=0)
# Results land in data/raw/<name>/. Already-collected subjects are skipped
# (delete data/raw/<name>/mutations.xml to recompute).
set -uo pipefail
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
cd "$ROOT"
ONLY=" $* "
tail -n +2 java/subjects.csv | while IFS=, read -r name url tc j5 split enabled notes; do
  if [ -n "${*}" ]; then [[ "$ONLY" == *" $name "* ]] || continue
  else [ "$enabled" = "1" ] || continue; fi
  if [ -f "data/raw/$name/mutations.xml" ]; then echo "[skip] $name (already collected)"; continue; fi
  dir="java/subjects/$name"
  if [ "$url" != "local" ] && [ ! -d "$dir" ]; then
    git clone -q --depth 1 "$url" "$dir" || { echo "[fail clone] $name"; continue; }
  fi
  bash java/scripts/run_pit.sh "$dir" "$name" "$tc" "$j5" > /dev/null 2>&1 \
    && echo "[ok] $name $(grep -o '"pit_seconds": [0-9]*' data/raw/$name/meta.json)" \
    || echo "[fail pit] $name (see data/raw/$name/pit.log)"
done
