"""Wave 24 Leg A: diff round-20 results against the standing INDEX.

Reads validation/wave24/results-round20.jsonl and INDEX.md, prints
every row whose round-20 verdict differs from standing, plus rows
whose vendor differs after normalization (INDEX em-dash and the
"unattributed (bare 403)" wording both mean vendor None). Verdict
diffs need fresh captures before any merge (the strict rule);
vendor-only diffs are reported for the STABILITY narrative.
"""

import json
import os
import re

BASE = os.path.join(os.path.dirname(__file__), "..", "..")
INDEX = os.path.join(BASE, "INDEX.md")
RESULTS = os.path.join(os.path.dirname(__file__), "results-round20.jsonl")
ROW = re.compile(r"^\| \[([^\]]+)\]\((https?://[^)]+)\) \| (\w+) \| "
                 r"([^|]+) \| (\S+) \|")


def norm_vendor(cell):
    cell = cell.strip()
    if cell in ("—", "-", "") or cell.startswith("unattributed"):
        return None
    return cell


def main():
    standing = {}
    with open(INDEX) as f:
        for line in f:
            m = ROW.match(line.strip())
            if m:
                standing[m.group(2)] = (m.group(3),
                                        norm_vendor(m.group(4)),
                                        m.group(5))
    print("standing rows: %d" % len(standing))
    n = 0
    vdiffs, wdiffs = [], []
    with open(RESULTS) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            n += 1
            url = r["target"]
            if url not in standing:
                print("NOT IN INDEX: %s" % url)
                continue
            sv, wv, ss = standing[url]
            if r["verdict"] != sv:
                vdiffs.append((url, sv, wv, ss, r["verdict"], r["vendor"],
                               r["status"]))
            elif r["vendor"] != wv:
                wdiffs.append((url, sv, wv, r["vendor"], r["status"]))
    print("round rows: %d" % n)
    print("--- verdict diffs: %d ---" % len(vdiffs))
    for d in vdiffs:
        print("VDIFF %s standing=%s/%s/%s round=%s/%s/%s" % d)
    print("--- vendor-only diffs: %d ---" % len(wdiffs))
    for d in wdiffs:
        print("WDIFF %s verdict=%s standing_vendor=%s round_vendor=%s "
              "status=%s" % d)


if __name__ == "__main__":
    main()
