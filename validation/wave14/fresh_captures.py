"""Wave 14 Leg A: fresh captures for the 3 round-10 diffs.

Fetches each diff URL twice (two agreeing readings = corroboration,
per the established rule) and classifies with the Wave 13 tree copy
(validation/wave14/src-wave13-tree/), so the fresh reading is judged
by the same classifier as the round itself — not by the Wave 14
fixes restored to src/ mid-run. Prints status/verdict/vendor/
evidence plus a body snippet for hand disposition in STABILITY-9.md.
Results also saved to validation/wave14/fresh-captures.json.
"""

import json
import os
import sys
import time
import urllib.error
import urllib.request

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src-wave13-tree"))
from wallcheck.classify import classify  # noqa: E402
from wallcheck.probe import _RecordingRedirectHandler, BODY_CAP, USER_AGENT  # noqa: E402

URLS = [
    "https://www.britishairways.com",
    "https://www.kaiserpermanente.org",
    "https://todoist.com",
]


def fetch_once(url):
    handler = _RecordingRedirectHandler()
    opener = urllib.request.build_opener(handler)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    status, headers, body, final_url, error = None, {}, "", url, None
    try:
        with opener.open(req, timeout=15) as resp:
            status = resp.status
            headers = dict(resp.headers.items())
            final_url = resp.geturl()
            body = resp.read(BODY_CAP).decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        status = e.code
        headers = dict(e.headers.items()) if e.headers else {}
        final_url = e.geturl() or url
        try:
            body = e.read(BODY_CAP).decode("utf-8", errors="replace")
        except Exception:
            body = ""
    except Exception as e:
        error = "%s: %s" % (type(e).__name__, e)
    r = classify(status, headers, body, final_url=final_url,
                 redirect_chain=handler.chain, error=error)
    return {"url": url, "final_url": final_url, "status": r["status"],
            "verdict": r["verdict"], "vendor": r["vendor"],
            "evidence": r["evidence"], "chain": handler.chain,
            "body_snippet": body[:300].replace("\n", " ")}


def main():
    out = []
    for url in URLS:
        for i in (1, 2):
            rec = fetch_once(url)
            rec["attempt"] = i
            out.append(rec)
            print("%s attempt=%d status=%s verdict=%s vendor=%s evidence=%s final=%s"
                  % (url, i, rec["status"], rec["verdict"], rec["vendor"],
                     rec["evidence"], rec["final_url"]))
            print("   snippet: %s" % rec["body_snippet"][:200])
            if i == 1:
                time.sleep(5)
    path = os.path.join(os.path.dirname(__file__), "fresh-captures.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    print("saved %d captures to %s" % (len(out), path))


if __name__ == "__main__":
    main()
