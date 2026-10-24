"""Wave 11 Leg C: spot re-audit of the 3 C-graded Wave 7 sweep domains
(hub.docker.com, huggingface.co, typeform.com) with the post-Wave-10
audit gates (llms JSON-error FAIL, robots HTML-error FAIL). Verifies
the new gates change real grades correctly and nothing else regressed.
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from wallcheck.audit import audit_site  # noqa: E402

DOMAINS = ["hub.docker.com", "huggingface.co", "www.typeform.com"]
OUT = os.path.join(os.path.dirname(__file__), "results-reaudit.json")


def main():
    results = []
    for d in DOMAINS:
        try:
            r = audit_site(d)
        except Exception as e:
            r = {"target": d, "error": "%s: %s" % (type(e).__name__, e)}
        results.append(r)
        print("%s grade=%s score=%s" % (
            d, r.get("grade"), r.get("score")), flush=True)
        for c in r.get("checks", []):
            print("  %-13s %s %s" % (c["check"], c["status"],
                                     ",".join(c["evidence"])), flush=True)
    with open(OUT, "w") as f:
        json.dump(results, f, indent=2, sort_keys=True)
        f.flush()
        os.fsync(f.fileno())
    print("wrote %s" % OUT)


if __name__ == "__main__":
    main()
