#!/usr/bin/env python3
"""Triage capture: ONE honest fetch of a URL with the wallcheck UA,
dumping the raw response shape (status, headers, body sample) so a
misclassified response can become a regression fixture. Diagnosis only —
same single-fetch discipline as the probe itself.

Usage: python3 capture.py <url> <out.json>
"""
import json
import os
import sys
import urllib.error
import urllib.request

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "src"))
from wallcheck.probe import USER_AGENT, BODY_CAP, _RecordingRedirectHandler  # noqa: E402


def main():
    url, out_path = sys.argv[1], sys.argv[2]
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
    rec = {"url": url, "final_url": final_url, "status": status,
           "headers": headers, "body": body,
           "redirect_chain": handler.chain, "error": error,
           "body_bytes_captured": len(body.encode("utf-8", errors="replace"))}
    with open(out_path, "w") as f:
        json.dump(rec, f, indent=2)
    print("status=%s final=%s body_chars=%d error=%s -> %s"
          % (status, final_url, len(body), error, out_path))


if __name__ == "__main__":
    main()
