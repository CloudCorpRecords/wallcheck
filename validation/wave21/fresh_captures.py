"""Wave 21 Leg A: fresh captures for every round-17 verdict diff.

Two fresh captures per diff target, via fetch_raw + classify (one
honest fetch each, no retries, no spoofing — the probe_url
equivalent with the body retained). Results in fresh-captures.json.

METHOD NOTE (read before trusting a corroboration): round 17 was
probed by a runner that imported the Wave 20 tree at launch
(before any Wave 21 battery edit landed — the runner started
before test_adversarial13.py existed), so the round measures
the Wave 20 tree end to end. These fresh captures necessarily
run on the CURRENT (Wave 21-fixed) tree. For each diff this
script therefore also records a Wave 21-rule involvement check:
whether the fresh body contains any shape a Wave 21 rule could
act on (an object data URL or embed src to a login/challenge
target, "high traffic" wording with a Retry-After header, an
authenticator prompt, a TA/TE/MR/PA human-check phrase) and
whether the evidence carries a Wave 21 code. A corroboration
counts only when no Wave 21 rule is involved in the fresh
reading — otherwise the row would need a Wave 20-tree re-probe,
and this script flags it. Fetch failures are tree-independent
(no response was classified).
"""

import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from wallcheck.audit import fetch_raw  # noqa: E402
from wallcheck.classify import classify  # noqa: E402

# Every round-17 verdict diff target from analyze_round17.py.
TARGETS = [
    "https://apnews.com",
    "https://www.amazon.com",
    "https://www.npmjs.com",
    "https://www.wayfair.com",
]

OUT = os.path.join(os.path.dirname(__file__), "fresh-captures.json")

_W21_LANG = ("நீங்கள் ரோபோ இல்லை என்பதை உறுதிப்படுத்தவும்",
             "మీరు రోబో కాదని నిర్ధారించండి",
             "तुम्ही रोबोट नाही याची पुष्टी करा",
             "ਤੁਸੀਂ ਰੋਬੋਟ ਨਹੀਂ ਹੋ ਇਸ ਦੀ ਪੁਸ਼ਟੀ ਕਰੋ")
_OBJECT_DATA_RE = re.compile(
    r"<object[^>]+data\s*=\s*[\"']([^\"']+)[\"']", re.I)
_EMBED_SRC_RE = re.compile(
    r"<embed[^>]+src\s*=\s*[\"']([^\"']+)[\"']", re.I)
_TOTP_INPUT_RE = re.compile(
    r"""<input[^>]*\b(?:name|id)\s*=\s*["'][^"']*(totp|authenticator)[^"']*["']""",
    re.I)


def w21_involvement(body, headers, evidence):
    """True when a Wave 21 rule could have shaped this reading."""
    b = (body or "")
    bl = b.lower()
    flags = []
    for src in _OBJECT_DATA_RE.findall(b) + _EMBED_SRC_RE.findall(b):
        path = src.split("?", 1)[0].split("#", 1)[0].lower()
        if "login" in path or "sign" in path or "auth" in path:
            flags.append("object-embed-login-src")
        if any(tok in path for tok in ("captcha", "challenge",
                                       "verify-human", "bot-check",
                                       "human-check")):
            flags.append("object-embed-challenge-src")
    if "high traffic" in bl and "retry-after" in (headers or {}):
        flags.append("W21-high-traffic-throttle")
    if "authenticator" in bl and _TOTP_INPUT_RE.search(b):
        flags.append("W21-authenticator-prompt")
    for phrase in _W21_LANG:
        if phrase in b:
            flags.append("W21-lang-phrase")
    if "AUTHENTICATOR_PROMPT" in (evidence or []):
        flags.append("AUTHENTICATOR_PROMPT-evidence")
    if "RETRY_AFTER_THROTTLE" in (evidence or []):
        flags.append("RETRY_AFTER_THROTTLE-evidence")
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
                    "w21_flags": w21_involvement(rec["body"] or "",
                                                 rec["headers"] or {},
                                                 r["evidence"]),
                })
            except Exception as e:
                caps.append({"status": None, "verdict": "UNREACHABLE",
                             "vendor": None, "error": "%s: %s" % (
                                 type(e).__name__, e),
                             "w21_flags": []})
        results[url] = caps
        print("%s: %s" % (url, [(c["status"], c["verdict"], c["vendor"],
                                c["w21_flags"]) for c in caps]), flush=True)
    with open(OUT, "w") as f:
        json.dump(results, f, indent=2, sort_keys=True)
    print("wrote %s" % OUT)


if __name__ == "__main__":
    main()
