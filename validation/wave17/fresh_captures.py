"""Wave 17 Leg A: fresh-capture corroboration for round-13 diffs.

Fetches each diff URL twice with the CURRENT tree (Wave 17 fixes
included — the round itself ran the Wave 16 tree, imported at
launch before the battery fixes landed; the corroboration question
is the target's live behavior, and any Wave 17-rule contribution
to a fresh verdict is reported, not hidden). Prints status,
verdict, vendor, and evidence for each attempt. One honest fetch
per attempt, no retries within an attempt.
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from wallcheck.probe import probe_url  # noqa: E402

TARGETS = [
    "https://rubygems.org",
    "https://www.britishairways.com",
    "https://www.forbes.com",
]

OUT = os.path.join(os.path.dirname(__file__), "fresh-captures.json")


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
