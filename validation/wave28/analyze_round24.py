"""Wave 28 Leg A: diff round-24 results against the standing INDEX table.

Prints the raw round distribution, every verdict diff (standing vs
round), and every vendor-only diff, so each can be hand-checked with
fresh captures before any merge.
"""

import json
import os
import re
from collections import Counter

BASE = os.path.join(os.path.dirname(__file__), "..", "..")
INDEX = os.path.join(BASE, "INDEX.md")
RESULTS = os.path.join(os.path.dirname(__file__), "results-round24.jsonl")
ROW = re.compile(r"^\| \[([^\]]+)\]\((https?://[^)]+)\) \| ([^|]+) \| "
                 r"([^|]+) \| ([^|]+) \|")


def standing():
    rows = {}
    with open(INDEX) as f:
        for line in f:
            m = ROW.match(line.strip())
            if m:
                name, url, verdict, vendor, status = (
                    g.strip() for g in m.groups())
                rows[url] = {"name": name, "verdict": verdict,
                             "vendor": vendor, "status": status}
    return rows


def main():
    idx = standing()
    print("index rows parsed: %d" % len(idx))
    results = {}
    with open(RESULTS) as f:
        for line in f:
            r = json.loads(line)
            results[r["target"]] = r
    print("round rows: %d" % len(results))
    print("raw distribution:", dict(Counter(
        r["verdict"] for r in results.values())))
    print("standing distribution:", dict(Counter(
        r["verdict"] for r in idx.values())))
    print("\n--- verdict diffs ---")
    for url, s in sorted(idx.items()):
        r = results.get(url)
        if r is None:
            print("MISSING in round: %s" % url)
            continue
        if r["verdict"] != s["verdict"]:
            print("%s: standing %s / %s / %s -> round %s / %s / %s" % (
                s["name"], s["verdict"], s["vendor"], s["status"],
                r["verdict"], r["vendor"], r["status"]))
    print("\n--- vendor-only diffs (same verdict) ---")
    for url, s in sorted(idx.items()):
        r = results.get(url)
        if r and r["verdict"] == s["verdict"]:
            rv = r["vendor"] or "—"
            if rv != s["vendor"]:
                print("%s: standing vendor %s -> round vendor %s "
                      "(status %s -> %s)" % (
                          s["name"], s["vendor"], rv,
                          s["status"], r["status"]))


if __name__ == "__main__":
    main()
