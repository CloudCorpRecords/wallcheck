"""Wave 18 Leg A: compare round-14 results against the INDEX.md
standing table. Prints: coverage (rows probed vs rows in the
table), every verdict/vendor diff with before/after, and a
rubygems.org spotlight (the Wave 16 passkey false positive fixed
by W17-007 must read OPEN under the Wave 17 tree).
"""

import json
import os
import re

BASE = os.path.join(os.path.dirname(__file__), "..", "..")
ROW = re.compile(r"^\| \[[^\]]+\]\((https?://[^)]+)\)[^|]*\| "
                 r"(\S+) \| ([^|]+) \| ([^|]+) \|")


def _norm_vendor(cell):
    cell = cell.strip()
    # "—" and "unattributed (bare 403)" both mean no vendor named:
    # the Wave 13 index audit records bare-403 rows that way, and a
    # round verdict of WALLED with vendor None is the same reading,
    # not a diff (Wave 16's note records four such rows).
    if cell == "—" or cell.startswith("unattributed"):
        return None
    return cell


def standing():
    table = {}
    with open(os.path.join(BASE, "INDEX.md")) as f:
        for line in f:
            m = ROW.match(line.strip())
            if m:
                url, verdict = m.group(1), m.group(2)
                table[url] = (verdict, _norm_vendor(m.group(3)))
    return table


def round14():
    rows = {}
    path = os.path.join(os.path.dirname(__file__), "results-round14.jsonl")
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            rows[r["target"]] = r
    return rows


def main():
    table = standing()
    rows = round14()
    print("standing rows: %d, round-14 rows: %d" % (len(table), len(rows)))
    missing = [u for u in table if u not in rows]
    print("missing from round 14: %d" % len(missing))
    for u in missing[:20]:
        print("  MISSING:", u)
    diffs = []
    for url, r in rows.items():
        if url not in table:
            print("  EXTRA (not in standing table):", url)
            continue
        sv, svendor = table[url]
        if r["verdict"] != sv or (r["vendor"] or None) != svendor:
            diffs.append((url, sv, svendor, r["verdict"], r["vendor"],
                          r["status"]))
    print("verdict/vendor diffs: %d" % len(diffs))
    for url, sv, svendor, nv, nvendor, status in sorted(diffs):
        print("  DIFF %s: %s/%s -> %s/%s (status %s)"
              % (url, sv, svendor, nv, nvendor, status))
    for url in ("https://rubygems.org", "https://www.rubygems.org"):
        if url in rows:
            r = rows[url]
            print("RUBYGEMS %s: standing=%s round14=%s/%s status=%s"
                  % (url, table.get(url), r["verdict"], r["vendor"],
                     r["status"]))


if __name__ == "__main__":
    main()
