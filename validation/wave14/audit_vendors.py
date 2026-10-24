"""Wave 14 Leg C: vendor-attribution audit (records audit + fresh
captures only to resolve disputes; no re-probing).

Checks:
 1. Row count + verdict distribution vs the INDEX.md header claim
    (parsed from the header itself, so it works post-merge).
 2. Every WALLED/CHALLENGED row carries a vendor or an explicit
    unattributed note (not a bare "—").
 3. FULL vendor check: every WALLED/CHALLENGED row's vendor cell
    vs round-10 history (the latest completed round): the vendor
    must match the round-10 evidence, or be explicitly
    "unattributed (bare 403)"-style. Unattributed is a valid,
    honest cell — vendors are never invented for unattributed rows.
 4. The Amazon note (‡) is current through round 10.
"""

import json
import re
from collections import Counter

BASE = "/home/hatch/workspace/github-builds/wallcheck"
ROW = re.compile(r"^\| \[([^\]]+)\]\((https?://[^)]+)\)[^|]*\| (\S+) \| ([^|]+?) \| ([^|]+?) \| ([^|]+?) \|")
SECTION = re.compile(r"^## (.+)$")

rows = []
section = None
text = open(BASE + "/INDEX.md").read()
for line in text.splitlines():
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

# Header claim, parsed from the "499 sites. Verdicts: ..." line.
hm = re.search(r"Verdicts: OPEN (\d+) · CHALLENGED (\d+) · WALLED (\d+) · "
               r"RATE_LIMITED (\d+) · UNREACHABLE (\d+) · LOGIN_GATED (\d+)",
               text)
header_claim = None
if hm:
    header_claim = {"OPEN": int(hm.group(1)), "CHALLENGED": int(hm.group(2)),
                    "WALLED": int(hm.group(3)), "RATE_LIMITED": int(hm.group(4)),
                    "UNREACHABLE": int(hm.group(5)), "LOGIN_GATED": int(hm.group(6))}
    print("header claim: %s" % header_claim)
    print("distribution match: %s" % all(dist.get(v, 0) == c for v, c in header_claim.items()))
else:
    print("header claim: NOT FOUND (header line format changed?)")

# Check 2: vendor or explicit unattributed note on every WALLED/CHALLENGED row.
no_vendor = [r for r in rows if r["verdict"] in ("WALLED", "CHALLENGED")
             and r["vendor"] in ("—", "-", "")]
print("WALLED/CHALLENGED rows missing vendor/unattributed note: %d" % len(no_vendor))
for r in no_vendor:
    print("  NO-VENDOR: %s %s %s" % (r["url"], r["verdict"], r["section"]))

# Round-10 history.
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
        if row.get("round") == 10:
            if row["target"] in hist:
                dups.append(row["target"])
            hist[row["target"]] = row
print("round-10 history lines: %d unique, %d duplicates" % (len(hist), len(dups)))
missing = [r["url"] for r in rows if r["url"] not in hist]
print("index urls missing from round-10 history: %d" % len(missing))
for u in missing[:20]:
    print("  MISSING: %s" % u)

# Check 3: FULL vendor check on all WALLED/CHALLENGED rows.
targets = [r for r in rows if r["verdict"] in ("WALLED", "CHALLENGED")]
print("WALLED/CHALLENGED rows checked: %d" % len(targets))
documented_holds = {
    "https://www.npmjs.com": "held CHALLENGED (round-10 fetch error = known transport pattern)",
}
mismatches = []
for r in targets:
    h = hist.get(r["url"])
    if h is None:
        mismatches.append((r, "no round-10 history"))
        continue
    hv, hven, hstat = h["verdict"], h.get("vendor"), h.get("status")
    iv = None if r["vendor"] in ("—", "-", "") else r["vendor"]
    iv_unattr = iv is not None and iv.startswith("unattributed")
    # Vendor agreement: exact match, or index-unattributed vs history
    # vendor None, or index-unattributed vs a history vendor the row
    # deliberately does not claim (flagged, not auto-mismatched —
    # unattributed is honest, but a newly-evidenced vendor deserves
    # a human look, so it is reported separately below).
    vendor_ok = (hven == iv) or (iv_unattr and hven is None)
    verdict_ok = (hv == r["verdict"])
    status_ok = (r["verdict"] == "UNREACHABLE" or hstat is None
                 or str(hstat) == r["status"])
    if not (verdict_ok and vendor_ok and status_ok):
        if r["url"] in documented_holds:
            print("DOCUMENTED HOLD ok: %s index=%s/%s history=%s/%s (%s)"
                  % (r["url"], r["verdict"], r["vendor"], hv, hven,
                     documented_holds[r["url"]]))
        else:
            mismatches.append((r, "index=%s/%s/%s history=%s/%s/%s"
                               % (r["verdict"], r["vendor"], r["status"],
                                  hv, hven, hstat)))
    elif iv_unattr and hven is not None:
        print("UNATTRIBUTED-BUT-EVIDENCED (review): %s index=%s history vendor=%s"
              % (r["url"], r["vendor"], hven))
print("full-check mismatches (excluding documented holds): %d" % len(mismatches))
for r, why in mismatches:
    print("  MISMATCH: %s [%s] %s" % (r["url"], r["section"], why))

# Check 4: Amazon note currency through round 10.
note10 = "round 10" in text and "‡" in text
print("amazon note mentions round 10: %s" % note10)
