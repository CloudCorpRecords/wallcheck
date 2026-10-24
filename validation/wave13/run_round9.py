"""Wave 13 Leg A: round-9 re-probe measuring the Wave 12 fixes on live traffic.

Re-probes the full 499-row INDEX table with the CURRENT (Wave 12-fixed)
classifier -- the fixes were verified present in the tree before this
runner started (W12-001 PL/TR/AR/ZH/RU localized phrases, W12-002
"browser check" JS_PROOF phrase, W12-003 form-action/login-yield split,
W12-004 JSON llms WARN, W12-005 markdown mislabel carve-out, W12-006
gzip sitemap decompression). One honest fetch
per URL, no retries, no spoofing. Appends one JSON line per probe to
validation/wave4/history.jsonl (round=9) and to
validation/wave12/results-round9.jsonl. Resumable: URLs already present
in history with round=9 are skipped. Flushes + fsyncs after every line.
"""

import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from wallcheck.probe import probe_url  # noqa: E402

BASE = os.path.join(os.path.dirname(__file__), "..", "..")
INDEX = os.path.join(BASE, "INDEX.md")
HISTORY = os.path.join(BASE, "validation", "wave4", "history.jsonl")
OUT = os.path.join(os.path.dirname(__file__), "results-round9.jsonl")
LINK = re.compile(r"^\| \[([^\]]+)\]\((https?://[^)]+)\)")


def index_urls():
    urls, seen = [], set()
    with open(INDEX) as f:
        for line in f:
            m = LINK.match(line.strip())
            if m and m.group(2) not in seen:
                seen.add(m.group(2))
                urls.append(m.group(2))
    return urls


def done_urls(path, round_no):
    done = set()
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except ValueError:
                    continue
                if row.get("round") == round_no:
                    done.add(row["target"])
    return done


def main():
    urls = index_urls()
    print("index urls: %d" % len(urls), flush=True)
    done = done_urls(HISTORY, 9)
    print("already probed round 9: %d" % len(done), flush=True)
    n = 0
    with open(HISTORY, "a") as hist, open(OUT, "a") as out:
        for url in urls:
            if url in done:
                continue
            try:
                r = probe_url(url, timeout=15)
                row = {"round": 9, "target": url, "status": r["status"],
                       "verdict": r["verdict"], "vendor": r["vendor"]}
            except Exception as e:  # never let one target kill the run
                row = {"round": 9, "target": url, "status": None,
                       "verdict": "UNREACHABLE", "vendor": None,
                       "error": "%s: %s" % (type(e).__name__, e)}
            line = json.dumps(row, sort_keys=True)
            hist.write(line + "\n")
            hist.flush()
            os.fsync(hist.fileno())
            out.write(line + "\n")
            out.flush()
            os.fsync(out.fileno())
            n += 1
            if n % 50 == 0:
                print("probed %d" % n, flush=True)
    print("round 9 complete: %d new probes" % n, flush=True)


if __name__ == "__main__":
    main()
