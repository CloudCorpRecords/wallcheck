#!/usr/bin/env python3
"""Wave 2 signing check: probe OUR OWN properties unsigned, then with
an RFC 9421 (hmac-sha256) wallcheck signature attached, one fetch each.
Records both result objects so any difference is on the record.

The signing key is generated fresh into /tmp (never the repo tree);
only its keyid + fingerprint are recorded here.

Usage: python3 run_signed.py <results.json>
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))

from wallcheck.probe import probe_url          # noqa: E402
from wallcheck.sign import (generate_key, key_fingerprint,  # noqa: E402
                            load_key, save_key, sign_request)

KEY_PATH = "/tmp/wallcheck-wave2-key.json"
TARGETS = [
    "https://clipwise.replit.app",
    "https://reneturcios.replit.app",
    "https://cloudcorprecords.github.io",
]


def main():
    out_path = sys.argv[1]
    key = generate_key()
    save_key(key, KEY_PATH)
    key = load_key(KEY_PATH)
    rows = []
    for url in TARGETS:
        unsigned = probe_url(url)
        sig_headers = sign_request(url, key)
        signed = probe_url(url, extra_headers=sig_headers)
        changed = (signed["verdict"] != unsigned["verdict"]
                   or signed["status"] != unsigned["status"])
        row = {"url": url, "unsigned": unsigned, "signed": signed,
               "verdict_changed": changed,
               "signature_input": sig_headers["Signature-Input"]}
        rows.append(row)
        print("%-40s unsigned=%s/%s signed=%s/%s changed=%s" % (
            url, unsigned["verdict"], unsigned["status"],
            signed["verdict"], signed["status"], changed), flush=True)
    doc = {"key": {"keyid": key["keyid"], "alg": key["alg"],
                   "fingerprint": key_fingerprint(key),
                   "location": KEY_PATH + " (ephemeral, not in repo)"},
           "targets": rows}
    with open(out_path, "w") as f:
        json.dump(doc, f, indent=2, sort_keys=True)
    print("saved to %s" % out_path)


if __name__ == "__main__":
    main()
