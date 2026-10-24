"""Wave 21 Leg C: path-matrix spot-check on the 10 Wave 20 merged rows.

For each merged row, probe five paths once each (login, signup, API,
robots.txt, llms.txt) with the same honest-fetch discipline as the
index probes (probe_url, identified wallcheck UA, no retries, no
challenge-solving). Records status/verdict/vendor per path plus the
row's standing round-16 verdict, so STABILITY-16.md can judge
whether the path evidence is consistent with the root merge or
contradicts it. A path verdict differing from the root verdict is
normal (paths differ from roots) and is NOT counted as a
contradiction on its own; only evidence that the root reading itself
was wrong (e.g. a root merged UNREACHABLE whose every path serves,
or a root merged CHALLENGED whose every path serves OPEN with no
wall anywhere) is flagged — and flagged for hand-check, not merged.
"""

import json
import os
import re
import sys
from urllib.parse import urlparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from wallcheck.probe import probe_url  # noqa: E402

BASE = os.path.join(os.path.dirname(__file__), "..", "..")
INDEX = os.path.join(BASE, "INDEX.md")
OUT = os.path.join(os.path.dirname(__file__), "results-path-matrix.jsonl")
LINK = re.compile(r"^\| \[([^\]]+)\]\((https?://[^)]+)\)")

TARGETS = {
    "claude.ai", "www.amazon.com", "www.ed.gov", "www.fda.gov",
    "www.goodrx.com", "www.irishjobs.ie", "www.jobs.ie",
    "www.totaljobs.com", "www.jobrapido.com", "www.ubereats.com",
}
PATHS = ["/login", "/signup", "/api", "/robots.txt", "/llms.txt"]


def index_rows():
    rows = {}
    with open(INDEX) as f:
        for line in f:
            m = LINK.match(line.strip())
            if not m:
                continue
            host = urlparse(m.group(2)).netloc
            if host in TARGETS:
                rows[host] = m.group(2)
    return rows


def main():
    rows = index_rows()
    print("matrix targets: %d" % len(rows), flush=True)
    assert len(rows) == 10, "expected 10 merged rows, got %d" % len(rows)
    with open(OUT, "w") as out:
        for host in sorted(rows):
            base = rows[host].rstrip("/")
            for path in PATHS:
                url = base + path
                try:
                    r = probe_url(url, timeout=15)
                    row = {"target": host, "path": path, "url": url,
                           "status": r["status"], "verdict": r["verdict"],
                           "vendor": r["vendor"]}
                except Exception as e:
                    row = {"target": host, "path": path, "url": url,
                           "status": None, "verdict": "UNREACHABLE",
                           "vendor": None,
                           "error": "%s: %s" % (type(e).__name__, e)}
                out.write(json.dumps(row, sort_keys=True) + "\n")
                out.flush()
                os.fsync(out.fileno())
                print("%s %s -> %s %s" % (host, path, row["status"],
                                           row["verdict"]), flush=True)
    print("path matrix complete", flush=True)


if __name__ == "__main__":
    main()
