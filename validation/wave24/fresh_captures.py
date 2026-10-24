"""Wave 24 Leg A: fresh captures for every round-20 verdict diff.
Two fresh captures per diff target, via fetch_raw + classify (one
honest fetch each, no retries, no spoofing — the probe_url
equivalent with the body retained). Results in fresh-captures.json.
Targets come from argv (filled from analyze_round20.py output).

METHOD NOTE (read before trusting a corroboration): round 20 was
probed by a runner that imported the Wave 23 tree at launch
(before any Wave 24 battery edit landed), so the round measures
the Wave 23 tree end to end. These fresh captures necessarily
run on the CURRENT (Wave 24-fixed) tree. For each diff this
script therefore also records a Wave 24-rule involvement check:
whether the fresh response carries any shape a Wave 24 rule
could act on (status 402; a push-approval sign-in prompt; a
Bulgarian/Slovak/Croatian/Slovenian human-check phrase). A
corroboration counts only when no Wave 24 rule is involved in
the fresh reading — otherwise the row would need a Wave 23-tree
re-probe, and this script flags it. Fetch failures are
tree-independent (no response was classified).
"""

import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from wallcheck.audit import fetch_raw  # noqa: E402
from wallcheck.classify import classify, _is_push_approval_prompt  # noqa: E402

OUT = os.path.join(os.path.dirname(__file__), "fresh-captures.json")

_W24_LANG = ("потвърдете, че не сте робот",
             "potvrďte, že nie ste robot",
             "potvrdite da niste robot",
             "potrdite, da niste robot")
_W23_LANG = ("επιβεβαιώστε ότι δεν είστε ρομπότ",
             "potvrďte, že nejste robot",
             "kérjük, erősítse meg, hogy ön nem robot",
             "confirmați că nu sunteți un robot")
_PICTURE_RE = re.compile(r"<picture\b[^>]*>(.*?)</picture>", re.S | re.I)
_PHRASE_HINTS = ("verify you are human", "human verification",
                 "are you a robot", "not a robot", "captcha",
                 "verifying your browser", "checking your browser")


def involvement(status, body):
    flags = []
    if status == 402:
        flags.append("status-402")
    body = body or ""
    if _is_push_approval_prompt(body):
        flags.append("push-approval-prompt")
    bl = body.lower()
    if any(p in bl for p in _W24_LANG):
        flags.append("w24-language-phrase")
    return flags


def w23_involvement(status, body):
    """Could a Wave 23 rule explain a move on this response? Used to
    judge fix-driven vs target-side for the STABILITY narrative:
    the round ran the Wave 23 tree, so a diff is fix-driven only
    if the fresh body carries a shape a Wave 23 rule acts on."""
    flags = []
    if status == 418:
        flags.append("status-418")
    body = body or ""
    for m in _PICTURE_RE.finditer(body):
        text = re.sub(r"<[^>]+>", " ", m.group(1)).lower()
        if any(p in text for p in _PHRASE_HINTS):
            flags.append("picture-phrase")
            break
    bl = body.lower()
    if any(p in bl for p in _W23_LANG):
        flags.append("w23-language-phrase")
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
                "w24_involvement": involvement(r.get("status"), body),
                "w23_involvement": w23_involvement(r.get("status"),
                                                   body)}
    except Exception as e:  # never let one target kill the run
        return {"target": url, "status": None, "verdict": "UNREACHABLE",
                "vendor": None, "w24_involvement": [],
                "w23_involvement": [],
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
