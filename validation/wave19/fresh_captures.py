"""Wave 19 Leg A: fresh captures for every round-15 verdict diff.

Two fresh captures per diff target, via fetch_raw + classify (one
honest fetch each, no retries, no spoofing — the probe_url
equivalent with the body retained). Results in fresh-captures.json.

METHOD NOTE (read before trusting a corroboration): round 15 was
probed by a runner that imported the Wave 18 tree at launch (11:57
UTC, before any Wave 19 battery edit landed), so the round measures
the Wave 18 tree end to end. These fresh captures necessarily run on
the CURRENT (Wave 19-fixed) tree. For each diff this script therefore
also records a Wave 19-rule involvement check: whether the fresh
body contains any shape a Wave 19 rule could act on (<template>
blocks, split alt phrases, <dialog> tags, Continue-step forms,
HE/FA/UR/BN phrases) and whether the evidence carries the new
EMAIL_CONTINUE_PROMPT code. A corroboration counts only when no
Wave 19 rule is involved in the fresh reading — otherwise the row
would need a Wave 18-tree re-probe, and this script flags it.
Fetch failures are tree-independent (no response was classified).
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
    "https://www.abc.net.au",
    "https://www.ed.gov",
    "https://www.forbes.com",
    "https://www.irishjobs.ie",
    "https://www.jobrapido.com",
    "https://www.jobs.ie",
    "https://www.lowes.com",
    "https://www.npmjs.com",
    "https://www.totaljobs.com",
]

OUT = os.path.join(os.path.dirname(__file__), "fresh-captures.json")


def w19_involvement(body, evidence):
    """True when a Wave 19 rule could have shaped this reading."""
    b = (body or "").lower()
    flags = []
    if "<template" in b:
        flags.append("template-block")
    if "<dialog" in b:
        flags.append("dialog-tag")
    if "continue" in b and "<button" in b:
        flags.append("continue-button-present")
    if "EMAIL_CONTINUE_PROMPT" in (evidence or []):
        flags.append("EMAIL_CONTINUE_PROMPT-evidence")
    for phrase in ("אמת שאינך רובוט", "אני לא רובוט", "تأیید کنید که ربات نیستید",
                   "تصدیق کریں کہ آپ روبوٹ نہیں ہیں", "আপনি রোবট নন তা নিশ্চিত করুন"):
        if phrase in (body or ""):
            flags.append("L7-phrase-present")
    return flags


def main():
    results = {}
    for url in TARGETS:
        caps = []
        for _ in range(2):
            try:
                rec = fetch_raw(url, timeout=20)
                # fetch_raw returns the record; classify it the way
                # probe_url would (same classifier, same inputs).
                # NOTE: probe_url does not return the body, so the
                # W19-involvement check needs fetch_raw + classify
                # (the Wave 16 spot-check hit the same discovery).
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
                    "w19_flags": w19_involvement(rec["body"] or "",
                                                 r["evidence"]),
                })
            except Exception as e:
                caps.append({"status": None, "verdict": "UNREACHABLE",
                             "vendor": None, "error": "%s: %s" % (
                                 type(e).__name__, e),
                             "w19_flags": []})
        results[url] = caps
        print("%s: %s" % (url, [(c["status"], c["verdict"], c["vendor"],
                                c["w19_flags"]) for c in caps]), flush=True)
    with open(OUT, "w") as f:
        json.dump(results, f, indent=2, sort_keys=True)
    print("wrote %s" % OUT)


if __name__ == "__main__":
    main()
