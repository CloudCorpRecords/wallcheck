#!/usr/bin/env bash
# Resumable driver for the wallcheck exposure deep sweep (Wave 2).
#
# The full 500-site deep sweep runs for hours and this VM restarts
# without warning, killing any single long process. So the sweep runs
# as slices of 100 sites, each a fresh exposure_scan.py process:
# slice 0 (sites 1-100) already exists as findings.json / run.log;
# this driver runs offsets 100, 200, 300, 400 in order.
#
# Resume semantics: before each slice, the driver checks whether the
# slice is already complete (its findings file exists AND its slice
# log records the slice's final global progress line). Complete slices
# are skipped. An incomplete slice's stale outputs are removed and the
# slice restarts from its own beginning — it re-fetches only its own
# 100 sites. If a slice process exits non-zero, the driver stops;
# re-running the driver resumes at the first incomplete slice.
#
# Launch detached so VM/session teardown cannot take it down with a
# shell:  setsid nohup scripts/run_deep_slices.sh > validation/exposure-wave2/driver.out 2>&1 < /dev/null &
set -u

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
URLS="$ROOT/validation/exposure-wave1/urls.txt"
OUT="$ROOT/validation/exposure-wave2"
mkdir -p "$OUT"
DLOG="$OUT/driver.log"
TOTAL="$(grep -c '^http' "$URLS")"

log() { echo "$(date -u +%FT%TZ) $*" | tee -a "$DLOG"; }

log "driver start (pid $$), $TOTAL urls total"

for offset in 100 200 300 400; do
    end=$((offset + 100))
    [ "$end" -gt "$TOTAL" ] && end=$TOTAL
    f="$OUT/findings_slice_${offset}.json"
    l="$OUT/run_slice_${offset}.log"
    if [ -f "$f" ] && [ -f "$l" ] && grep -q "^${end}/${TOTAL} sites" "$l"; then
        log "slice offset=$offset already complete (${end}/${TOTAL}) - skipping"
        continue
    fi
    rm -f "$f" "$l"
    log "starting slice offset=$offset (sites $((offset + 1))-$end of $TOTAL)"
    python3 "$ROOT/scripts/exposure_scan.py" deep "$URLS" "$OUT" \
        --offset "$offset" --limit 100 >> "$OUT/slice_${offset}.out" 2>&1
    rc=$?
    if [ "$rc" -ne 0 ]; then
        log "slice offset=$offset exited rc=$rc - driver stopping; re-run to resume"
        exit "$rc"
    fi
    log "slice offset=$offset complete"
done

log "all slices complete"
