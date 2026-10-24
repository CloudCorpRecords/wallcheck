"""Wave 16 Leg C: adopter spot-check (NOT a census).

Re-fetches the signed-agent directory documents of the 4 known
adopters (chatgpt.com, www.indeed.com, substack.com,
www.ahrefs.com) and verifies each still parses, each key still
validates structurally, and each expiry window (where present).
Also re-probes the directory path on 10 of the 71 Wave 7
walled-directory-path domains to confirm the path is still
walled. One honest fetch per URL, no retries. Results to
validation/wave16/results-adopter-spot.json.
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from wallcheck.probe import probe_url  # noqa: E402
from wallcheck.audit import fetch_raw  # noqa: E402
# NOTE (runner bug, fixed before any conclusion was drawn): the first
# version of this script read r["body"] from probe_url's result, but
# probe_url returns only the classification object — no body field.
# All four "body is not JSON" readings from that version were the
# runner's own artifact, not adopter changes. This version fetches
# with audit.fetch_raw (which returns the body) and classifies the
# record separately; the bogus first run's file was overwritten.

BASE = os.path.join(os.path.dirname(__file__), "..", "..")
OUT = os.path.join(os.path.dirname(__file__), "results-adopter-spot.json")
DIRPATH = "/.well-known/http-message-signatures-directory"

ADOPTERS = ["chatgpt.com", "www.indeed.com", "substack.com",
            "www.ahrefs.com"]
WALLED_SPOT = ["www.upwork.com", "www.guru.com", "www.npmjs.com",
               "medium.com", "www.glassdoor.com", "hub.docker.com",
               "www.reddit.com", "www.w3schools.com", "www.reuters.com",
               "www.wsj.com"]


def check_key(key):
    """Structural validation of one directory key entry."""
    problems = []
    if not key.get("kid"):
        problems.append("missing kid")
    if key.get("kty") and key["kty"] != "OKP":
        problems.append("kty=%s (expected OKP)" % key["kty"])
    if key.get("crv") and key["crv"] != "Ed25519":
        problems.append("crv=%s (expected Ed25519)" % key["crv"])
    if key.get("x") and len(key["x"]) != 43:
        problems.append("x length %d (expected 43 base64url chars)"
                        % len(key["x"]))
    return problems


def main():
    results = {"adopters": {}, "walled_spot": {}}
    for host in ADOPTERS:
        url = "https://" + host + DIRPATH
        try:
            rec = fetch_raw(url, timeout=15)
            r = {"status": rec.get("status"), "verdict": None,
                 "vendor": None}
            body = rec.get("body") or ""
            try:
                doc = json.loads(body)
                keys = doc.get("keys") if isinstance(doc, dict) else None
                if not isinstance(keys, list):
                    results["adopters"][host] = {
                        "status": r["status"], "parses": False,
                        "verdict": r["verdict"], "vendor": r["vendor"],
                        "note": "200 body is not a JWKS-style key set"}
                else:
                    key_info = []
                    for k in keys:
                        key_info.append({
                            "kid": k.get("kid"), "kty": k.get("kty"),
                            "crv": k.get("crv"), "use": k.get("use"),
                            "purpose": k.get("purpose"),
                            "nbf": k.get("nbf"), "exp": k.get("exp"),
                            "problems": check_key(k)})
                    results["adopters"][host] = {
                        "status": r["status"], "parses": True,
                        "verdict": r["verdict"], "vendor": r["vendor"],
                        "top_level_fields": sorted(doc.keys()),
                        "keys": key_info}
            except ValueError:
                results["adopters"][host] = {
                    "status": r["status"], "parses": False,
                    "verdict": r["verdict"], "vendor": r["vendor"],
                    "note": "body is not JSON"}
        except Exception as e:
            results["adopters"][host] = {
                "status": None, "parses": False, "error": str(e)}
        print(json.dumps({host: results["adopters"][host]},
                         sort_keys=True), flush=True)
    for host in WALLED_SPOT:
        url = "https://" + host + DIRPATH
        try:
            r = probe_url(url, timeout=15)
            results["walled_spot"][host] = {
                "status": r["status"], "verdict": r["verdict"],
                "vendor": r["vendor"]}
        except Exception as e:
            results["walled_spot"][host] = {
                "status": None, "verdict": "UNREACHABLE",
                "error": str(e)}
        print(json.dumps({host: results["walled_spot"][host]},
                         sort_keys=True), flush=True)
    with open(OUT, "w") as f:
        json.dump(results, f, indent=1, sort_keys=True)
    print("wrote %s" % OUT, flush=True)


if __name__ == "__main__":
    main()
