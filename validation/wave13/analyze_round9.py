"""Wave 13 Leg A: diff round-9 readings against the standing INDEX.

Compares every INDEX row (vendor cells normalized: the four
Wave 13 audit edits "unattributed (bare 403)" count as None)
against its round-9 history line. Prints every diff for
hand-disposition in STABILITY-8.md, plus coverage checks.
Note: the round-9 runner imported the Wave 12-fixed classifier
at launch, so round 9 genuinely measures the Wave 12 tree even
though Wave 13 fixes landed on disk mid-run.
"""

import json
import re
from collections import Counter

BASE = "/home/hatch/workspace/github-builds/wallcheck"
ROW = re.compile(r"^\| \[([^\]]+)\]\((https?://[^)]+)\)[^|]*\| (\S+) \| ([^|]+?) \| ([^|]+?) \| ([^|]+?) \|")

rows = {}
with open(BASE + "/INDEX.md") as f:
    for line in f:
        m = ROW.match(line.strip())
        if m:
            name, url, verdict, vendor, status, last = m.groups()
            v = vendor.strip()
            if v in ("—", "-", "unattributed (bare 403)"):
                v = None
            rows[url] = {"verdict": verdict, "vendor": v,
                         "status": status.strip()}

hist = {}
dups = []
for line in open(BASE + "/validation/wave4/history.jsonl"):
    line = line.strip()
    if not line:
        continue
    try:
        r = json.loads(line)
    except ValueError:
        continue
    if r.get("round") == 9:
        if r["target"] in hist:
            dups.append(r["target"])
        hist[r["target"]] = r

print("index rows: %d, round-9 lines: %d unique, %d dups"
      % (len(rows), len(hist), len(dups)))
print("index urls missing from round 9: %d"
      % len([u for u in rows if u not in hist]))
print("round-9 urls not in index: %d"
      % len([u for u in hist if u not in rows]))

dist = Counter(r["verdict"] for r in hist.values())
print("round-9 raw distribution: %s" % dict(dist))

diffs = []
for url, idx in rows.items():
    h = hist.get(url)
    if h is None:
        diffs.append((url, idx, None, "NOT-PROBED"))
        continue
    hv, hven, hstat = h["verdict"], h.get("vendor"), h.get("status")
    if hv != idx["verdict"] or hven != idx["vendor"]:
        diffs.append((url, idx, h, "VERDICT/VENDOR"))
    elif idx["verdict"] != "UNREACHABLE" and hstat is not None \
            and str(hstat) != idx["status"]:
        diffs.append((url, idx, h, "STATUS-ONLY"))
print("diffs: %d" % len(diffs))
for url, idx, h, kind in diffs:
    if h is None:
        print("  %s | index=%s/%s/%s | %s" % (url, idx["verdict"],
              idx["vendor"], idx["status"], kind))
    else:
        print("  %s | index=%s/%s/%s | round9=%s/%s/%s | %s"
              % (url, idx["verdict"], idx["vendor"], idx["status"],
                 h["verdict"], h.get("vendor"), h.get("status"), kind))
