"""Wave 15 Leg A: fresh captures for round-11 diffs.

Probes each diff target twice with the CURRENT (Wave 14-fixed) tree --
the same tree the round-11 runner measured -- so dispositions are
judged by the round's own classifier, not by post-battery fixes.
Writes validation/wave15/fresh-captures.json (one record per capture,
with the classifier verdict/vendor attached).
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from wallcheck.probe import probe_url  # noqa: E402

TARGETS = [
    "https://www.forbes.com",
    "https://www.britishairways.com",
    "https://www.webex.com",
]
OUT = os.path.join(os.path.dirname(__file__), "fresh-captures.json")


def main():
    records = []
    for url in TARGETS:
        for attempt in (1, 2):
            try:
                r = probe_url(url, timeout=15)
                records.append({"target": url, "attempt": attempt,
                                "status": r["status"],
                                "verdict": r["verdict"],
                                "vendor": r["vendor"],
                                "final_url": r.get("final_url"),
                                "body_sample": (r.get("body") or "")[:600]})
            except Exception as e:
                records.append({"target": url, "attempt": attempt,
                                "status": None, "verdict": "UNREACHABLE",
                                "vendor": None,
                                "error": "%s: %s" % (type(e).__name__, e)})
            print("%s attempt %d: %s" % (url, attempt,
                  [(k, records[-1].get(k)) for k in
                   ("status", "verdict", "vendor")]), flush=True)
    with open(OUT, "w") as f:
        json.dump(records, f, indent=2)
    print("wrote %d records" % len(records))


if __name__ == "__main__":
    main()
