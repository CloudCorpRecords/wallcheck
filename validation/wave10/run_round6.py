"""Wave 10 Leg A: round-6 stability re-probe of the full INDEX table.

Reads URLs from INDEX.md table rows, probes each once with the honest
wallcheck UA (no retries, no spoofing), appends one JSON line per probe
to validation/wave4/history.jsonl (round=6) and to
validation/wave10/results-round6.jsonl. Resumable: URLs already present
in history with round=6 are skipped. Flushes + fsyncs after every line
(the VM exec write-guard lesson: never hold a whole run in memory).
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
OUT = os.path.join(os.path.dirname(__file__), "results-round6.jsonl")
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


def done_urls(path):
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
                if row.get("round") == 6:
                    done.add(row["target"])
    return done


def main():
    urls = index_urls()
    print("index urls: %d" % len(urls), flush=True)
    done = done_urls(HISTORY)
    print("already probed round 6: %d" % len(done), flush=True)
    n = 0
    with open(HISTORY, "a") as hist, open(OUT, "a") as out:
        for url in urls:
            if url in done:
                continue
            try:
                r = probe_url(url, timeout=15)
                row = {"round": 6, "target": url, "status": r["status"],
                       "verdict": r["verdict"], "vendor": r["vendor"]}
            except Exception as e:  # never let one target kill the run
                row = {"round": 6, "target": url, "status": None,
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
                print("probed %d new (total done %d)" % (n, len(done) + n),
                      flush=True)
    print("DONE new=%d" % n, flush=True)


if __name__ == "__main__":
    main()
