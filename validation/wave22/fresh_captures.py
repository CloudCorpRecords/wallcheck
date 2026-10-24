"""Wave 22 Leg A: fresh captures for every round-18 verdict diff.
Two fresh captures per diff target, via fetch_raw + classify (one
honest fetch each, no retries, no spoofing — the probe_url
equivalent with the body retained). Results in fresh-captures.json.
Targets come from argv (filled from analyze_round18.py output).

METHOD NOTE (read before trusting a corroboration): round 18 was
probed by a runner that imported the Wave 21 tree at launch
(before any Wave 22 battery edit landed), so the round measures
the Wave 21 tree end to end. These fresh captures necessarily
run on the CURRENT (Wave 22-fixed) tree. For each diff this
script therefore also records a Wave 22-rule involvement check:
whether the fresh body contains any shape a Wave 22 rule could
act on (an SVG title/desc challenge phrase, an SSO button/link,
a GU/KN/NE/KM human-check phrase) and whether the evidence
carries a Wave 22 code. A corroboration counts only when no
Wave 22 rule is involved in the fresh reading — otherwise the
row would need a Wave 21-tree re-probe, and this script flags
it. Fetch failures are tree-independent (no response was
classified).
"""

import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from wallcheck.audit import fetch_raw  # noqa: E402
from wallcheck.classify import classify  # noqa: E402

OUT = os.path.join(os.path.dirname(__file__), "fresh-captures.json")

_W22_LANG = ("તમે રોબોટ નથી તેની ખાતરી કરો",
             "ನೀವು ರೋಬೋಟ್ ಅಲ್ಲ ಎಂದು ಖಚಿತಪಡಿಸಿ",
             "तपाईं रोबोट होइन भनेर पुष्टि गर्नुहोस्",
             "បញ្ជាក់ថាអ្នកមិនមែនជាមនុស្សយន្ត")
_SVG_META_RE = re.compile(r"<(title|desc)\b[^>]*>.*?</\1>", re.S | re.I)


def involvement(body):
    flags = []
    m = _SVG_META_RE.search(body or "")
    if m and "verify you are human" in m.group(0).lower():
        flags.append("svg-meta-phrase")
    bl = (body or "").lower()
    if "sso" in bl and ("<button" in bl or "<a " in bl):
        flags.append("sso-mention")
    if any(p in (body or "") for p in _W22_LANG):
        flags.append("w22-language-phrase")
    return flags


def capture(url):
    try:
        r = fetch_raw(url, timeout=15)
        body = r.get("body") or ""
        c = classify(r.get("status"), r.get("headers") or {}, body,
                     final_url=r.get("final_url") or url,
                     redirect_chain=r.get("redirect_chain") or [])
        return {"target": url, "status": r.get("status"),
                "verdict": c["verdict"], "vendor": c["vendor"],
                "evidence": c.get("evidence"),
                "w22_involvement": involvement(body)}
    except Exception as e:  # never let one target kill the run
        return {"target": url, "status": None, "verdict": "UNREACHABLE",
                "vendor": None, "w22_involvement": [],
                "error": "%s: %s" % (type(e).__name__, e)}


def main():
    targets = sys.argv[1:]
    out = []
    for url in targets:
        for i in (1, 2):
            row = capture(url)
            row["attempt"] = i
            out.append(row)
            print(json.dumps(row, sort_keys=True), flush=True)
    with open(OUT, "w") as f:
        json.dump(out, f, indent=1, sort_keys=True)
    print("fresh captures complete: %d rows" % len(out), flush=True)


if __name__ == "__main__":
    main()
