#!/usr/bin/env python3
"""Merge wallcheck deep-sweep slice outputs into one findings file.

Deep sweeps run as restart-survivable slices (see run_deep_slices.sh):
slice 0 writes findings.json, later slices write findings_slice_<N>.json.
This tool combines whatever slices are present in the outdir into
findings_all.json, deduping identical (site, source, pattern,
sha256_16) rows, and prints class totals plus the candidate list.
Findings are fingerprint-only by construction, so the merge never
sees a value.

Append-only semantics (added 2026-10-26): the merged file also keeps
rows already banked in a previous findings_all.json. Slice drivers
delete an incomplete slice's outputs on resume, so a plain replace
would silently drop findings a dead slice had already banked (this
lost Wave 3's 50-site partial in Oct 2026). Rows are never removed
by a merge; a re-scan re-confirms them instead. When a key collides,
the banked row wins.

Usage: merge_deep_findings.py [outdir]   (default validation/exposure-wave2)
"""
import json
import pathlib
import sys
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parent.parent


def slice_files(outdir):
    files = []
    base = outdir / "findings.json"
    if base.exists():
        files.append(base)
    files += sorted(outdir.glob("findings_slice_*.json"),
                    key=lambda p: int(p.stem.rsplit("_", 1)[1]))
    return files


def _row_key(row):
    return (row.get("site"), row.get("source"), row.get("pattern"),
            row.get("sha256_16"))


def merge(outdir):
    outdir = pathlib.Path(outdir)
    merged, seen = [], set()
    per_file = {}
    for f in slice_files(outdir):
        rows = json.loads(f.read_text())
        per_file[f.name] = len(rows)
        for row in rows:
            key = _row_key(row)
            if key in seen:
                continue
            seen.add(key)
            merged.append(row)
    # Append-only: keep rows banked in a previous merged file, so a
    # slice restart (which deletes that slice's partial outputs) can
    # never shrink the merged snapshot. Banked rows win on collision.
    banked = outdir / "findings_all.json"
    if banked.exists():
        try:
            banked_rows = json.loads(banked.read_text())
        except json.JSONDecodeError:
            banked_rows = []
        kept = 0
        for row in banked_rows:
            if _row_key(row) in seen:
                continue
            seen.add(_row_key(row))
            merged.append(row)
            kept += 1
        if kept:
            per_file["<banked findings_all.json>"] = kept
    return merged, per_file


def main():
    outdir = (pathlib.Path(sys.argv[1]) if len(sys.argv) > 1
              else ROOT / "validation" / "exposure-wave2")
    merged, per_file = merge(outdir)
    if not per_file:
        raise SystemExit(f"no slice findings found in {outdir}")
    target = outdir / "findings_all.json"
    tmp = outdir / "findings_all.json.tmp"
    tmp.write_text(json.dumps(merged, indent=1))
    tmp.replace(target)
    print("inputs:", ", ".join(f"{k}={v}" for k, v in per_file.items()))
    print(f"merged: {len(merged)} unique findings -> {target}")
    counts = Counter(f["class"] for f in merged)
    print("class totals:", dict(counts))
    cand = [f for f in merged if f["class"] == "CANDIDATE_EXPOSURE"]
    print(f"candidates ({len(cand)}):")
    for f in sorted(cand, key=lambda r: (r["site"], r["source"])):
        print("  %s | %s | %s | len %s | sha256 %s" % (
            f["site"], f["pattern"], f["source"], f["value_len"],
            f["sha256_16"]))


if __name__ == "__main__":
    main()
