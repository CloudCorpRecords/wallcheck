"""Wave 25 Leg C: huggingface.co probes for the FRONT-DOORS row.

Three honest fetches, one each: the root, /api, and the signed-
agent directory path (/.well-known/http-message-signatures-
directory). fetch_raw + classify (the probe_url equivalent with
the body retained), so the FRONT-DOORS-ADD note can cite status,
verdict, vendor, and a body sample as evidence. No retries, no
spoofing, no bypass — the answers are recorded, never forced.
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from wallcheck.audit import fetch_raw  # noqa: E402
from wallcheck.classify import classify  # noqa: E402

OUT = os.path.join(os.path.dirname(__file__), "huggingface-probes.json")
TARGETS = [
    "https://huggingface.co",
    "https://huggingface.co/api",
    "https://huggingface.co/.well-known/http-message-signatures-directory",
]


def probe(url):
    try:
        r = fetch_raw(url, timeout=15)
        body = r.get("body") or ""
        c = classify(r.get("status"), r.get("headers") or {}, body,
                     final_url=r.get("final_url") or url,
                     redirect_chain=r.get("redirect_chain") or [])
        return {"target": url, "status": r.get("status"),
                "final_url": r.get("final_url"),
                "verdict": c["verdict"], "vendor": c["vendor"],
                "evidence": c.get("evidence"),
                "body_bytes": len(body.encode("utf-8")),
                "body_sample": body[:300]}
    except Exception as e:  # never let one target kill the run
        return {"target": url, "status": None, "verdict": "UNREACHABLE",
                "vendor": None,
                "error": "%s: %s" % (type(e).__name__, e)}


def main():
    out = []
    for url in TARGETS:
        row = probe(url)
        out.append(row)
        print(json.dumps({k: row[k] for k in ("target", "status",
                                              "verdict", "vendor")},
                         sort_keys=True), flush=True)
    with open(OUT, "w") as f:
        json.dump(out, f, indent=1, sort_keys=True)
    print("huggingface probes complete: %d rows" % len(out), flush=True)


if __name__ == "__main__":
    main()
