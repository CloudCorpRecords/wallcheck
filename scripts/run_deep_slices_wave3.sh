#!/usr/bin/env bash
# Resumable driver for the wallcheck exposure deep sweep (Wave 3:
# sites 501-1000 of the doubled census — a fresh 500-site list in
# validation/exposure-wave3/urls.txt, Tranco-ranked, disjoint from
# Waves 1-2). Same slice discipline as the Wave 2 driver: 100-site
# slices, each a fresh exposure_scan.py process, so a VM restart
# loses at most one slice.
#
# Resume semantics: a slice is complete when its findings file exists
# AND its slice log records the slice's final global progress line.
# Incomplete slices have stale outputs removed and restart from their
# own beginning. If a slice exits non-zero the driver stops; re-run
# to resume.
#
# Launch detached:  setsid nohup scripts/run_deep_slices_wave3.sh > validation/exposure-wave3/driver.out 2>&1 < /dev/null &
set -u

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
URLS="$ROOT/validation/exposure-wave3/urls.txt"
OUT="$ROOT/validation/exposure-wave3"
mkdir -p "$OUT"
DLOG="$OUT/driver.log"
TOTAL="$(grep -c '^http' "$URLS")"

log() { echo "$(date -u +%FT%TZ) $*" | tee -a "$DLOG"; }

log "driver start (pid $$), $TOTAL urls total"

for offset in 0 100 200 300 400; do
    end=$((offset + 100))
    [ "$end" -gt "$TOTAL" ] && end=$TOTAL
    if [ "$offset" -eq 0 ]; then
        f="$OUT/findings.json"; l="$OUT/run.log"
    else
        f="$OUT/findings_slice_${offset}.json"; l="$OUT/run_slice_${offset}.log"
    fi
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
