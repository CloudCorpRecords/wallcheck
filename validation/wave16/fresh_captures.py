"""Wave 16 Leg A: fresh-capture hand-checks for round-12 diffs.

Fetches each round-12 diff URL twice (fresh, honest fetches) and
classifies with the CURRENT tree, printing status/verdict/vendor
plus the deciding evidence. The round itself ran the Wave 15 tree
(imported at launch, before the Wave 16 fixes landed), so a fresh
reading that differs from the round reading is dispositioned on
the SITE's behavior (status + body facts), and any verdict that
depends on a Wave 16 rule is flagged as such — a fix-driven
effect is not churn, and churn is not a fix-driven move.
Results to validation/wave16/fresh-captures.json.
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from wallcheck.audit import fetch_raw  # noqa: E402
from wallcheck.classify import classify  # noqa: E402

TARGETS = [
    "https://www.npmjs.com",
    "https://apnews.com",
    "https://www.france24.com",
    "https://www.forbes.com",
    "https://www.britishairways.com",
]


def main():
    out = {}
    for url in TARGETS:
        attempts = []
        for _ in range(2):
            rec = fetch_raw(url, timeout=15)
            r = classify(rec.get("status"), rec.get("headers") or {},
                         rec.get("body") or "",
                         final_url=rec.get("final_url", ""),
                         redirect_chain=rec.get("redirect_chain") or [],
                         error=rec.get("error"))
            attempts.append({
                "status": rec.get("status"),
                "final_url": rec.get("final_url"),
                "verdict": r["verdict"], "vendor": r["vendor"],
                "evidence": r["evidence"][:8],
                "error": rec.get("error")})
            print("%s attempt: status=%s verdict=%s vendor=%s evidence=%s" % (
                url, rec.get("status"), r["verdict"], r["vendor"],
                r["evidence"][:6]), flush=True)
        out[url] = attempts
    path = os.path.join(os.path.dirname(__file__), "fresh-captures.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=1, sort_keys=True)
    print("wrote %s" % path, flush=True)


if __name__ == "__main__":
    main()
