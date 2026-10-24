"""Wave 27 Leg A: fresh captures for every round-23 verdict diff.
Two fresh captures per diff target, via fetch_raw + classify (one
honest fetch each, no retries, no spoofing — the probe_url
equivalent with the body retained). Results in fresh-captures.json.
Targets come from argv (filled from analyze_round23.py output).

METHOD NOTE (read before trusting a corroboration): round 23 was
probed by a runner that imported the Wave 26 tree at launch
(before any Wave 27 battery edit landed), so the round measures
the Wave 26 tree end to end. These fresh captures necessarily
run on the CURRENT (Wave 27-fixed) tree. For each diff this
script therefore also records a Wave 27-rule involvement check:
whether the fresh response carries any shape a Wave 27 rule
could act on (a biometric sign-in prompt; an Albanian /
Icelandic / Kazakh / Malayalam human-check phrase). A
corroboration counts only when no Wave 27 rule is involved in
the fresh reading — otherwise the row would need a Wave 26-tree
re-probe, and this script flags it. Fetch failures are
tree-independent (no response was classified).

The w26_involvement check answers the fix-driven question for
the STABILITY narrative: the round ran the Wave 26 tree, so a
diff is fix-driven only if the fresh body carries a shape a
Wave 26 rule acts on (a badge-tap prompt; a Catalan / Estonian
/ Armenian / Georgian phrase). The third Wave 26 fix (percent-
encoded sitemap hosts) is audit-side — it cannot act on a
homepage capture — so it is not checked here.
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from wallcheck.audit import fetch_raw  # noqa: E402
from wallcheck.classify import classify, _is_badge_tap_prompt, \
    _is_biometric_prompt  # noqa: E402

OUT = os.path.join(os.path.dirname(__file__), "fresh-captures.json")

_W26_LANG = ("confirma que no ets un robot",
             "kinnitage, et te ei ole robot",
             "հաստատեք, որ ռոբոտ չեք",
             "დაადასტურეთ, რომ რობოტი არ ხართ")
_W27_LANG = ("konfirmoni që nuk jeni robot",
             "staðfestu að þú sért ekki vélmenni",
             "робот емес екеніңізді растаңыз",
             "നിങ്ങൾ ഒരു റോബോട്ട് അല്ലെന്ന് സ്ഥിരീകരിക്കുക")


def w26_involvement(status, body):
    flags = []
    body = body or ""
    if _is_badge_tap_prompt(body):
        flags.append("badge-tap-prompt")
    bl = body.lower()
    if any(p in bl for p in _W26_LANG):
        flags.append("w26-language-phrase")
    return flags


def w27_involvement(status, body):
    flags = []
    body = body or ""
    if _is_biometric_prompt(body):
        flags.append("biometric-prompt")
    bl = body.lower()
    if any(p in bl for p in _W27_LANG):
        flags.append("w27-language-phrase")
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
                "w27_involvement": w27_involvement(r.get("status"), body)}
    except Exception as e:  # never let one target kill the run
        return {"target": url, "status": None, "verdict": "UNREACHABLE",
                "vendor": None, "w26_involvement": [],
                "w27_involvement": [],
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
