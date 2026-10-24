"""Wave 15 Leg B: corpus regression check.

Classifies every stored capture JSON under validation/*/captures with
the current classifier and prints one line per capture:
path, status, verdict, vendor. Run before and after a fix and diff
the outputs: any verdict/vendor change on a real capture must be
explained, not silently accepted.
"""
import glob
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from wallcheck.classify import classify  # noqa: E402

BASE = os.path.join(os.path.dirname(__file__), "..", "..")


def main():
    files = sorted(glob.glob(os.path.join(BASE, "validation", "*",
                                          "captures", "*.json")))
    for path in files:
        try:
            rec = json.load(open(path))
        except Exception as e:
            print("%s UNPARSEABLE %s" % (path, e))
            continue
        r = classify(rec.get("status"), rec.get("headers") or {},
                     rec.get("body") or "",
                     final_url=rec.get("final_url", ""),
                     redirect_chain=rec.get("redirect_chain") or [],
                     error=rec.get("error"))
        print("%s status=%s verdict=%s vendor=%s" % (
            os.path.relpath(path, BASE), rec.get("status"),
            r["verdict"], r["vendor"]))


if __name__ == "__main__":
    main()
