"""Wave 18 Leg A: fresh-capture corroboration for round-14 diffs.

Fetches each diff URL twice with the WAVE 17 TREE (src-wave17-tree/)
— the same tree round 14 measured — so fresh captures are comparable
to the round reading. Prints status, verdict, vendor, and evidence
for each attempt. One honest fetch per attempt, no retries within an
attempt. Targets are filled in from the round-14 diff list once the
round completes; the script refuses to run with an empty list.
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src-wave17-tree"))
from wallcheck.probe import probe_url  # noqa: E402

TARGETS = [
    "https://claude.ai",
    "https://remoteok.com",
    "https://www.abc.net.au",
    "https://www.amazon.com",
    "https://www.britishairways.com",
    "https://www.fda.gov",
    "https://www.forbes.com",
    "https://www.goodrx.com",
    "https://www.kroger.com",
    "https://www.td.com",
    "https://www.ubereats.com",
    "https://www.venmo.com",
]

OUT = os.path.join(os.path.dirname(__file__), "fresh-captures.json")


assert TARGETS, "fill TARGETS from the round-14 diff list before running"


def main():
    results = []
    for url in TARGETS:
        for attempt in (1, 2):
            try:
                r = probe_url(url, timeout=15)
                row = {"target": url, "attempt": attempt,
                       "status": r["status"], "verdict": r["verdict"],
                       "vendor": r["vendor"],
                       "evidence": r.get("evidence", [])}
            except Exception as e:  # noqa: BLE001 - report, don't crash
                row = {"target": url, "attempt": attempt,
                       "status": None, "verdict": "UNREACHABLE",
                       "vendor": None,
                       "error": "%s: %s" % (type(e).__name__, e)}
            print(json.dumps(row, sort_keys=True), flush=True)
            results.append(row)
    with open(OUT, "w") as f:
        json.dump(results, f, indent=2, sort_keys=True)
    print("wrote %s (%d rows)" % (OUT, len(results)), flush=True)


if __name__ == "__main__":
    main()
