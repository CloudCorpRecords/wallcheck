"""Wave 20 Leg C: adopter spot-check — the 4 signed-agent directory
adopters from census v2 (Wave 7) + Wave 16 spot-check. One honest
fetch per directory URL; records whether the directory still serves.
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from wallcheck.probe import probe_url  # noqa: E402

ADOPTERS = [
    "https://chatgpt.com/.well-known/http-message-signatures-directory",
    "https://www.indeed.com/.well-known/http-message-signatures-directory",
    "https://substack.com/.well-known/http-message-signatures-directory",
    "https://ahrefs.com/.well-known/http-message-signatures-directory",
]

OUT = os.path.join(os.path.dirname(__file__), "results-adopter-spot.json")


def main():
    rows = []
    for url in ADOPTERS:
        try:
            r = probe_url(url, timeout=15)
            rows.append({"target": url, "status": r["status"],
                         "verdict": r["verdict"], "vendor": r["vendor"]})
        except Exception as e:  # noqa: BLE001 - never let one kill the run
            rows.append({"target": url, "status": None,
                         "verdict": "UNREACHABLE", "vendor": None,
                         "error": "%s: %s" % (type(e).__name__, e)})
        print("%s -> %s %s" % (rows[-1]["target"], rows[-1]["status"],
                               rows[-1]["verdict"]), flush=True)
    with open(OUT, "w") as f:
        json.dump(rows, f, indent=2, sort_keys=True)
    print("wrote %s" % OUT, flush=True)


if __name__ == "__main__":
    main()
