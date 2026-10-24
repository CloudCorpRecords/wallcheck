"""Wave 16 Leg A: round-12 re-probe measuring the Wave 15 fixes on live traffic.

Written fresh for round 12 (NOT sed-derived -- the sed-trap that bit
Waves 13 and 14 came from a stale round constant in a copied resume
check). The round number lives in exactly one place (ROUND below) and
is used by every label, resume check, and output row.

Re-probes the full 499-row INDEX table with the CURRENT (Wave 15-fixed)
classifier -- all ten Wave 15 fixes were grep-verified present in the
tree before this runner started (W15-001 ld+json strip, W15-002
REFUSAL_PHRASE, W15-003 visible-text phrase scan, W15-004 invisible-
widget suppression, W15-005 Refresh-header routing, W15-006
CODE_ENTRY_FORM, W15-007 footer-badge blanking, W15-008 robots
Allow tiebreak, W15-009 frontmatter strip, W15-010 SITEMAP_NO_URLS).
One honest fetch per URL, no retries, no spoofing. Appends one JSON
line per probe to validation/wave4/history.jsonl (round=ROUND) and to
validation/wave16/results-round12.jsonl. Resumable: URLs already present
in history with round=ROUND are skipped. Flushes + fsyncs after every
line.
"""

import json
import os
import re
import sys

ROUND = 12

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from wallcheck.probe import probe_url  # noqa: E402

BASE = os.path.join(os.path.dirname(__file__), "..", "..")
INDEX = os.path.join(BASE, "INDEX.md")
HISTORY = os.path.join(BASE, "validation", "wave4", "history.jsonl")
OUT = os.path.join(os.path.dirname(__file__), "results-round12.jsonl")
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
    done = done_urls(HISTORY, ROUND)
    print("already probed round %d: %d" % (ROUND, len(done)), flush=True)
    n = 0
    with open(HISTORY, "a") as hist, open(OUT, "a") as out:
        for url in urls:
            if url in done:
                continue
            try:
                r = probe_url(url, timeout=15)
                row = {"round": ROUND, "target": url, "status": r["status"],
                       "verdict": r["verdict"], "vendor": r["vendor"]}
            except Exception as e:  # never let one target kill the run
                row = {"round": ROUND, "target": url, "status": None,
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
    print("round %d complete: %d new probes" % (ROUND, n), flush=True)


if __name__ == "__main__":
    main()
