"""Wave 26 Leg A: fresh captures for every round-22 verdict diff.
Two fresh captures per diff target, via fetch_raw + classify (one
honest fetch each, no retries, no spoofing — the probe_url
equivalent with the body retained). Results in fresh-captures.json.
Targets come from argv (filled from analyze_round22.py output).

METHOD NOTE (read before trusting a corroboration): round 22 was
probed by a runner that imported the Wave 25 tree at launch
(before any Wave 26 battery edit landed), so the round measures
the Wave 25 tree end to end. These fresh captures necessarily
run on the CURRENT (Wave 26-fixed) tree. For each diff this
script therefore also records a Wave 26-rule involvement check:
whether the fresh response carries any shape a Wave 26 rule
could act on (a badge-tap sign-in prompt; a Catalan / Estonian /
Armenian / Georgian human-check phrase). A corroboration counts
only when no Wave 26 rule is involved in the fresh reading —
otherwise the row would need a Wave 25-tree re-probe, and this
script flags it. Fetch failures are tree-independent (no
response was classified).

The w25_involvement check answers the fix-driven question for
the STABILITY narrative: the round ran the Wave 25 tree, so a
diff is fix-driven only if the fresh body carries a shape a
Wave 25 rule acts on (an employee-ID prompt; a Serbian /
Macedonian / Latvian / Lithuanian phrase; a challenge phrase
carried only by a placeholder attribute).
"""

import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from wallcheck.audit import fetch_raw  # noqa: E402
from wallcheck.classify import classify, _is_badge_tap_prompt, \
    _is_employee_id_prompt, _PLACEHOLDER_ATTR_RE  # noqa: E402

OUT = os.path.join(os.path.dirname(__file__), "fresh-captures.json")

_W26_LANG = ("confirma que no ets un robot",
             "kinnitage, et te ei ole robot",
             "հաստատեք, որ ռոբոտ չեք",
             "დაადასტურეთ, რომ რობოტი არ ხართ")
_W25_LANG = ("потврдите да нисте робот",
             "потврдете дека не сте робот",
             "apstipriniet, ka neesat robots",
             "patvirtinkite, kad nesate robotas")
_PHRASE_HINTS = ("verify you are human", "human verification",
                 "are you a robot", "not a robot", "captcha")


def w26_involvement(status, body):
    flags = []
    body = body or ""
    if _is_badge_tap_prompt(body):
        flags.append("badge-tap-prompt")
    bl = body.lower()
    if any(p in bl for p in _W26_LANG):
        flags.append("w26-language-phrase")
    return flags


def w25_involvement(status, body):
    flags = []
    body = body or ""
    if _is_employee_id_prompt(body):
        flags.append("employee-id-prompt")
    bl = body.lower()
    if any(p in bl for p in _W25_LANG):
        flags.append("w25-language-phrase")
    for m in _PLACEHOLDER_ATTR_RE.finditer(body):
        if any(p in m.group(0).lower() for p in _PHRASE_HINTS):
            flags.append("placeholder-phrase")
            break
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
                "w26_involvement": w26_involvement(r.get("status"), body),
                "w25_involvement": w25_involvement(r.get("status"), body)}
    except Exception as e:  # never let one target kill the run
        return {"target": url, "status": None, "verdict": "UNREACHABLE",
                "vendor": None, "w26_involvement": [],
                "w25_involvement": [],
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
