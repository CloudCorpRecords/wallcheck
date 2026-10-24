"""Wave 22 Leg C: fresh captures for the vendor re-audit's doubtful
cells — apnews.com (INDEX CHALLENGED/Cloudflare vs a round-17 probe
failure) and the four "unattributed (bare 403)" WALLED cells. One
honest fetch each via fetch_raw + classify, no retries, no spoofing.
Results in vendor-captures.json.

METHOD NOTE: round 18 is measured by a runner that imported the
Wave 21 tree at launch, so these captures (on the CURRENT Wave
22-fixed tree) carry a Wave 22-rule involvement check: whether the
fresh body contains any shape a Wave 22 rule could act on (an SVG
<title>/<desc> challenge phrase, an SSO button/link, a GU/KN/NE/KM
human-check phrase) and whether the evidence carries a Wave 22
code. A corroboration counts only when no Wave 22 rule is involved.
"""

import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from wallcheck.audit import fetch_raw  # noqa: E402
from wallcheck.classify import classify  # noqa: E402

TARGETS = [
    "https://apnews.com",
    "https://www.catho.com.br",
    "https://www.haaretz.com",
    "https://www.hyatt.com",
    "https://www.state.gov",
]

OUT = os.path.join(os.path.dirname(__file__), "vendor-captures.json")

_W22_LANG = ("તમે રોબોટ નથી તેની ખાતરી કરો",
             "ನೀವು ರೋಬೋಟ್ ಅಲ್ಲ ಎಂದು ಖಚಿತಪಡಿಸಿ",
             "तपाईं रोबोट होइन भनेर पुष्टि गर्नुहोस्",
             "បញ្ជាក់ថាអ្នកមិនមែនជាមនុស្សយន្ត")
_SVG_META_RE = re.compile(r"<(title|desc)\b[^>]*>.*?</\1>", re.S | re.I)
_SSO_RE = re.compile(r"sso", re.I)


def involvement(body):
    flags = []
    if _SVG_META_RE.search(body or ""):
        m = _SVG_META_RE.search(body)
        if "verify you are human" in m.group(0).lower():
            flags.append("svg-meta-phrase")
    if _SSO_RE.search(body or "") and ("button" in (body or "").lower()
                                       or "<a " in (body or "").lower()):
        flags.append("sso-mention")
    if any(p in (body or "") for p in _W22_LANG):
        flags.append("w22-language-phrase")
    return flags


def main():
    out = []
    for url in TARGETS:
        try:
            r = fetch_raw(url, timeout=15)
            body = r.get("body") or ""
            c = classify(r.get("status"), r.get("headers") or {}, body,
                         final_url=r.get("final_url") or url,
                         redirect_chain=r.get("redirect_chain") or [])
            row = {"target": url, "status": r.get("status"),
                   "verdict": c["verdict"], "vendor": c["vendor"],
                   "evidence": c.get("evidence"),
                   "w22_involvement": involvement(body),
                   "body_len": len(body)}
        except Exception as e:  # never let one target kill the run
            row = {"target": url, "status": None, "verdict": "UNREACHABLE",
                   "vendor": None, "w22_involvement": [],
                   "error": "%s: %s" % (type(e).__name__, e)}
        out.append(row)
        print(json.dumps(row, sort_keys=True), flush=True)
    with open(OUT, "w") as f:
        json.dump(out, f, indent=1, sort_keys=True)
    print("vendor captures complete: %d targets" % len(out), flush=True)


if __name__ == "__main__":
    main()
