#!/usr/bin/env bash
# Run PIT with the FULL mutation matrix on one Maven project and copy the
# فارسی: اجرای PIT با ماتریس کامل روی یک پروژه‌ی Maven و ذخیره‌ی خروجی در data/raw/<name>/
# result (mutations.xml + linecoverage.xml + sources) into data/raw/<name>/.
#
# Usage:  java/scripts/run_pit.sh <project_dir> <name> [target_classes] [junit5_plugin_version|'']
# Example: java/scripts/run_pit.sh java/subjects/commons-cli commons-cli 'org.apache.commons.cli.*'
#
# Env vars: PIT_VERSION (default 1.30.1), THREADS (default nproc), MUTATORS (default ALL)
set -euo pipefail
PROJ=$(realpath "$1"); NAME=$2; TC=${3:-}; J5=${4-1.2.3}
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
PIT_VERSION=${PIT_VERSION:-1.30.1}
THREADS=${THREADS:-$(nproc)}
MUTATORS=${MUTATORS:-ALL}   # ALL gives more operator variety; use DEFAULTS for the PIT standard set
OUT="$ROOT/data/raw/$NAME"
mkdir -p "$OUT"

python3 "$ROOT/java/scripts/inject_pit.py" "$PROJ/pom.xml" --pit "$PIT_VERSION" \
  --junit5 "$J5" --target-classes "$TC" --threads "$THREADS" --mutators "$MUTATORS"

# Skip the usual Apache-Commons quality gates that are irrelevant here.
SKIPS="-Drat.skip -Dcheckstyle.skip -Djapicmp.skip -Danimal.sniffer.skip -Dmaven.javadoc.skip \
 -Djacoco.skip -Dspotbugs.skip -Dpmd.skip -Dcyclonedx.skip -Dspdx.skip -Denforcer.skip -Dmoditect.skip \
 -Dbuildnumber.skip -Dsurefire.failIfNoSpecifiedTests=false"

START=$(date +%s)
( cd "$PROJ" && mvn -B -q $SKIPS test-compile org.pitest:pitest-maven:$PIT_VERSION:mutationCoverage ) \
  2>&1 | tee "$OUT/pit.log" | tail -n 20
END=$(date +%s)

cp "$PROJ/target/pit-reports/mutations.xml" "$OUT/mutations.xml"
cp "$PROJ/target/pit-reports/linecoverage.xml" "$OUT/linecoverage.xml" 2>/dev/null || true
# keep sources so static features (statement type, nesting, complexity) can be extracted
rm -rf "$OUT/src"; mkdir -p "$OUT/src"
cp -r "$PROJ/src/main/java/." "$OUT/src/main/" 2>/dev/null || true
cp -r "$PROJ/src/test/java/." "$OUT/src/test/" 2>/dev/null || true
COMMIT=$( (cd "$PROJ" && git rev-parse --verify -q HEAD) 2>/dev/null || true)
python3 - "$OUT/meta.json" "$NAME" "$((END-START))" "$THREADS" "$PIT_VERSION" "${COMMIT:-local}" "$MUTATORS" <<'PY'
import json, sys
o, name, secs, thr, ver, commit, muts = sys.argv[1:]
json.dump(dict(name=name, pit_seconds=int(secs), threads=int(thr), pit_version=ver,
               commit=commit, mutators=muts), open(o, "w"), indent=2)
PY
echo "[run_pit] $NAME done in $((END-START)) s -> $OUT"
