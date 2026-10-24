"""Wave 28 Leg A: fresh captures for the round-24 verdict diff.
Two fresh captures for the single diff target (npmjs.com), via
fetch_raw + classify (one honest fetch each, no retries, no
spoofing — the probe_url equivalent with the body retained).
Results in fresh-captures.json.

METHOD NOTE (read before trusting a corroboration): round 24 was
probed by a runner that imported the Wave 27 tree at launch
(before any Wave 28 battery edit landed), so the round measures
the Wave 27 tree end to end. These fresh captures necessarily
run on the CURRENT (Wave 28-fixed) tree. For the diff this
script therefore records both involvement checks: a Wave 27-rule
check (the round's tree — a diff is fix-driven under the Wave 27
rules only if the fresh body carries a Wave 27 shape: a
biometric prompt, or an Albanian / Icelandic / Kazakh /
Malayalam phrase; the robots-token and llms-comment fixes are
audit-side and cannot act on a homepage capture) and a Wave
28-rule check (the fresh tree — a corroboration counts only
when no Wave 28 rule is involved in the fresh reading: a
Windows PIN prompt, a Burmese / Sinhala / Amharic / Azerbaijani
phrase, or an ARIA modal container). Fetch failures are
tree-independent (no response was classified).
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from wallcheck.audit import fetch_raw  # noqa: E402
from wallcheck.classify import classify, _is_biometric_prompt, \
    _is_windows_pin_prompt, _MODAL_ROLE_TAG_RE  # noqa: E402

OUT = os.path.join(os.path.dirname(__file__), "fresh-captures.json")

_W27_LANG = ("konfirmoni që nuk jeni robot",
             "staðfestu að þú sért ekki vélmenni",
             "робот емес екеніңізді растаңыз",
             "നിങ്ങൾ ഒരു റോബോട്ട് അല്ലെന്ന് സ്ഥിരീകരിക്കുക")
_W28_LANG = ("သင်သည် စက်ရုပ်မဟုတ်ကြောင်း အတည်ပြုပါ",
             "ඔබ රොබෝවෙක් නොවන බව තහවුරු කරන්න",
             "ሮቦት እንዳልሆኑ ያረጋግጡ",
             "robot olmadığınızı təsdiqləyin")


def w27_involvement(status, body):
    flags = []
    body = body or ""
    if _is_biometric_prompt(body):
        flags.append("biometric-prompt")
    bl = body.lower()
    if any(p in bl for p in _W27_LANG):
        flags.append("w27-language-phrase")
    return flags


def w28_involvement(status, body):
    flags = []
    body = body or ""
    if _is_windows_pin_prompt(body):
        flags.append("windows-pin-prompt")
    if _MODAL_ROLE_TAG_RE.search(body):
        flags.append("aria-modal-container")
    bl = body.lower()
    if any(p in bl for p in _W28_LANG):
        flags.append("w28-language-phrase")
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
                "evidence": c["evidence"],
                "w27_involvement": w27_involvement(r.get("status"),
                                                   body),
                "w28_involvement": w28_involvement(r.get("status"),
                                                   body),
                "error": None}
    except Exception as e:
        return {"target": url, "status": None,
                "verdict": "UNREACHABLE", "vendor": None,
                "evidence": [], "w27_involvement": [],
                "w28_involvement": [],
                "error": "%s: %s" % (type(e).__name__, e)}


def main():
    targets = sys.argv[1:]
    out = []
    for url in targets:
        for _ in range(2):
            out.append(capture(url))
    with open(OUT, "w") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
    for row in out:
        print(json.dumps(row, ensure_ascii=False))


if __name__ == "__main__":
    main()
