"""Wave 13 Leg C: INDEX.md records audit (no re-probing).

Checks:
 1. Row count + verdict distribution vs the header claim.
 2. Every WALLED/CHALLENGED row carries a vendor (not "—") or an
    explicit unattributed note.
 3. Spot-check >= 30 rows across categories against history.jsonl
    round 8 (the latest completed round): verdict/vendor/status must
    match, except the two documented Wave 12 holds (npmjs, webex)
    and the two documented merges (amazon, britishairways).
 4. The Amazon note (‡) is current through round 8.
"""

import json
import re
import sys
from collections import Counter, defaultdict

BASE = "/home/hatch/workspace/github-builds/wallcheck"
ROW = re.compile(r"^\| \[([^\]]+)\]\((https?://[^)]+)\)[^|]*\| (\S+) \| ([^|]+?) \| ([^|]+?) \| ([^|]+?) \|")
SECTION = re.compile(r"^## (.+)$")

rows = []
section = None
with open(BASE + "/INDEX.md") as f:
    for line in f:
        m = SECTION.match(line.strip())
        if m:
            section = m.group(1)
            continue
        m = ROW.match(line.strip())
        if m:
            name, url, verdict, vendor, status, last = m.groups()
            rows.append({"name": name, "url": url, "verdict": verdict,
                         "vendor": vendor.strip(), "status": status.strip(),
                         "last": last.strip(), "section": section})

print("rows parsed: %d" % len(rows))
dist = Counter(r["verdict"] for r in rows)
print("distribution: %s" % dict(dist))
# Updated after the round-9 merges (STABILITY-8.md): the pre-merge
# claim (414/25/34/7/18/1) is superseded, not drift.
header_claim = {"OPEN": 415, "CHALLENGED": 25, "WALLED": 35,
                "RATE_LIMITED": 7, "UNREACHABLE": 17, "LOGIN_GATED": 0}
print("header claim: %s" % header_claim)
match = all(dist.get(v, 0) == c for v, c in header_claim.items())
print("distribution match: %s" % match)

# Check 2: vendor on every WALLED/CHALLENGED row
no_vendor = [r for r in rows if r["verdict"] in ("WALLED", "CHALLENGED")
             and r["vendor"] in ("—", "-", "")]
print("WALLED/CHALLENGED rows missing vendor: %d" % len(no_vendor))
for r in no_vendor:
    print("  NO-VENDOR: %s %s %s" % (r["url"], r["verdict"], r["section"]))

# History round 8
hist = {}
dups = []
with open(BASE + "/validation/wave4/history.jsonl") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except ValueError:
            continue
        if row.get("round") == 8:
            if row["target"] in hist:
                dups.append(row["target"])
            hist[row["target"]] = row
print("round-8 history lines: %d unique, %d duplicates" % (len(hist), len(dups)))
missing = [r["url"] for r in rows if r["url"] not in hist]
print("index urls missing from round-8 history: %d" % len(missing))
for u in missing[:20]:
    print("  MISSING: %s" % u)

# Check 3: stratified spot-check — every 13th row + the 4 round-8 diff
# rows + the LOGIN_GATED row, deduplicated.
sample_idx = set(range(0, len(rows), 13))
special = ["https://www.amazon.com", "https://www.npmjs.com",
           "https://www.webex.com", "https://www.britishairways.com"]
by_url = {r["url"]: r for r in rows}
for u in special:
    if u in by_url:
        sample_idx.add(rows.index(by_url[u]))
for r in rows:
    if r["verdict"] == "LOGIN_GATED":
        sample_idx.add(rows.index(r))
sample = [rows[i] for i in sorted(sample_idx)]
print("spot-check sample: %d rows" % len(sample))

documented_holds = {
    "https://www.npmjs.com": "held CHALLENGED (round-8 fetch error = known transport pattern)",
    "https://www.webex.com": "held OPEN (single uncorroborated Akamai 403 vs fresh OPEN)",
}
mismatches = []
for r in sample:
    h = hist.get(r["url"])
    if h is None:
        mismatches.append((r, "no round-8 history"))
        continue
    hv, hven, hstat = h["verdict"], h.get("vendor"), h.get("status")
    iv = r["vendor"] if r["vendor"] != "—" else None
    ok = (hv == r["verdict"] and hven == iv)
    if r["verdict"] != "UNREACHABLE" and hstat is not None:
        ok = ok and (str(hstat) == r["status"])
    if not ok:
        if r["url"] in documented_holds:
            print("DOCUMENTED HOLD ok: %s index=%s/%s history=%s/%s (%s)"
                  % (r["url"], r["verdict"], r["vendor"], hv, hven,
                     documented_holds[r["url"]]))
        else:
            mismatches.append((r, "index=%s/%s/%s history=%s/%s/%s"
                               % (r["verdict"], r["vendor"], r["status"],
                                  hv, hven, hstat)))
print("spot-check mismatches (excluding documented holds): %d" % len(mismatches))
for r, why in mismatches:
    print("  MISMATCH: %s [%s] %s" % (r["url"], r["section"], why))
cats = Counter(r["section"] for r in sample)
print("sample categories: %s" % dict(cats))

# Check 4: Amazon note currency
text = open(BASE + "/INDEX.md").read()
note = "‡ **amazon.com** is listed CHALLENGED as of Wave 12 round 8"
print("amazon note current through round 8: %s" % (note in text))
