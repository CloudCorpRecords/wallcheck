"""Wave 20 Leg A: fresh captures for every round-16 verdict diff.

Two fresh captures per diff target, via fetch_raw + classify (one
honest fetch each, no retries, no spoofing — the probe_url
equivalent with the body retained). Results in fresh-captures.json.

METHOD NOTE (read before trusting a corroboration): round 16 was
probed by a runner that imported the Wave 19 tree at launch
(12:23 UTC, before any Wave 20 battery edit landed — process
start 12:23:43 UTC vs classify.py edits at 12:26:35 UTC), so the
round measures the Wave 19 tree end to end. These fresh captures
necessarily run on the CURRENT (Wave 20-fixed) tree. For each
diff this script therefore also records a Wave 20-rule
involvement check: whether the fresh body contains any shape a
Wave 20 rule could act on (an iframe src to a login/challenge
target, a localized JS-proof phrase, a UK/HI/MS/TL/SW human-
check phrase) and whether the evidence carries a Wave 20 code.
A corroboration counts only when no Wave 20 rule is involved in
the fresh reading — otherwise the row would need a Wave 19-tree
re-probe, and this script flags it. Fetch failures are
tree-independent (no response was classified).
"""

import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from wallcheck.audit import fetch_raw  # noqa: E402
from wallcheck.classify import classify  # noqa: E402

# Filled after analyze_round16.py runs: every round-16 diff target.
TARGETS = [
    "https://claude.ai",
    "https://www.amazon.com",
    "https://www.ed.gov",
    "https://www.fda.gov",
    "https://www.goodrx.com",
    "https://www.irishjobs.ie",
    "https://www.jobrapido.com",
    "https://www.jobs.ie",
    "https://www.npmjs.com",
    "https://www.totaljobs.com",
    "https://www.ubereats.com",
    "https://www.wayfair.com",
    "https://www.webex.com",
]

OUT = os.path.join(os.path.dirname(__file__), "fresh-captures.json")

_W20_JS_PROOF = ("wir überprüfen ihren browser",
                 "nous vérifions votre navigateur",
                 "estamos verificando su navegador",
                 "estamos verificando o seu navegador",
                 "ブラウザを確認しています")
_W20_LANG = ("підтвердіть, що ви не робот",
             "कृपया पुष्टि करें कि आप रोबोट नहीं हैं",
             "sahkan bahawa anda bukan robot",
             "kumpirmahin na hindi ka robot",
             "thibitisha kuwa wewe si roboti")
_IFRAME_SRC_RE = re.compile(
    r"<iframe[^>]+src\s*=\s*[\"']([^\"']+)[\"']", re.I)


def w20_involvement(body, evidence):
    """True when a Wave 20 rule could have shaped this reading."""
    b = (body or "")
    bl = b.lower()
    flags = []
    for src in _IFRAME_SRC_RE.findall(b):
        path = src.split("?", 1)[0].split("#", 1)[0].lower()
        if "login" in path or "sign" in path or "auth" in path:
            flags.append("iframe-login-src")
        if any(tok in path for tok in ("captcha", "challenge",
                                       "verify-human", "bot-check",
                                       "human-check")):
            flags.append("iframe-challenge-src")
    for phrase in _W20_JS_PROOF:
        if phrase in bl:
            flags.append("W20-JS-proof-phrase")
    for phrase in _W20_LANG:
        if phrase in b:
            flags.append("W20-lang-phrase")
    if "REDIRECT_TO_CHALLENGE" in (evidence or []):
        flags.append("REDIRECT_TO_CHALLENGE-evidence")
    return flags


def main():
    results = {}
    for url in TARGETS:
        caps = []
        for _ in range(2):
            try:
                rec = fetch_raw(url, timeout=20)
                r = classify(rec["status"], rec["headers"], rec["body"],
                             final_url=rec["final_url"],
                             redirect_chain=rec["redirect_chain"],
                             error=rec["error"])
                caps.append({
                    "status": rec["status"], "verdict": r["verdict"],
                    "vendor": r["vendor"],
                    "evidence": r["evidence"],
                    "body_len": len(rec["body"] or ""),
                    "body_head": (rec["body"] or "")[:200],
                    "w20_flags": w20_involvement(rec["body"] or "",
                                                 r["evidence"]),
                })
            except Exception as e:
                caps.append({"status": None, "verdict": "UNREACHABLE",
                             "vendor": None, "error": "%s: %s" % (
                                 type(e).__name__, e),
                             "w20_flags": []})
        results[url] = caps
        print("%s: %s" % (url, [(c["status"], c["verdict"], c["vendor"],
                                c["w20_flags"]) for c in caps]), flush=True)
    with open(OUT, "w") as f:
        json.dump(results, f, indent=2, sort_keys=True)
    print("wrote %s" % OUT)


if __name__ == "__main__":
    main()
