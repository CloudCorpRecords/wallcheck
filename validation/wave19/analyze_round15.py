"""Wave 19 Leg A: compare round-15 results against the INDEX.md
standing table. Prints: coverage (rows probed vs rows in the
table), every verdict/vendor diff with before/after, and
spotlights on the rows the Wave 18 rules must hold:
ubereats.com (the Wave 17 head-strip move must hold OPEN),
remoteok.com / td.com / venmo.com (the Wave 18 QR fix must read
OPEN), rubygems.org (the Wave 17 passkey fix must hold OPEN).
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


def round15():
    rows = {}
    path = os.path.join(os.path.dirname(__file__), "results-round15.jsonl")
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
    rows = round15()
    print("standing rows: %d, round-15 rows: %d" % (len(table), len(rows)))
    missing = [u for u in table if u not in rows]
    print("missing from round 15: %d" % len(missing))
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
    for url in ("https://www.ubereats.com", "https://ubereats.com",
                "https://remoteok.com", "https://www.td.com",
                "https://www.venmo.com", "https://rubygems.org",
                "https://www.rubygems.org"):
        if url in rows:
            r = rows[url]
            print("SPOTLIGHT %s: standing=%s round15=%s/%s status=%s"
                  % (url, table.get(url), r["verdict"], r["vendor"],
                     r["status"]))


if __name__ == "__main__":
    main()
