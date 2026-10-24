"""Wave 12 Leg C: second signing spot-check.

Generates a FRESH Ed25519 key (0600, secret never printed), then for
chatgpt.com (reference-grade directory adopter) and ahrefs.com (Wave 7
census adopter) runs an unsigned probe and a signed probe, recording
both verdicts. Expectation: no change — an unregistered key is not
in either site's trust set, and the Wave 5 experiment (12/12
unchanged) plus the Wave 10 regression (7/7 unchanged) both say the
same. Any change would be capture-verified twice before being
claimed. Self-verification included (own verifier accepts own
signatures, rejects tampered ones). One honest fetch per probe.
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from wallcheck.probe import probe_url  # noqa: E402
from wallcheck.sign import (  # noqa: E402
    directory_document, generate_key, save_key, sign_request,
    verify_request, authority_of)

HERE = os.path.dirname(__file__)
KEY_PATH = os.path.join(HERE, "wave12-spot-key.json")
OUT = os.path.join(HERE, "results-signed-spot.json")
TARGETS = ["https://chatgpt.com", "https://www.ahrefs.com"]


def slim(r):
    return {"status": r["status"], "verdict": r["verdict"],
            "vendor": r["vendor"], "evidence": r["evidence"],
            "final_url": r["final_url"]}


def main():
    key = generate_key(alg="ed25519")
    save_key(key, KEY_PATH)
    os.chmod(KEY_PATH, 0o600)
    headers = sign_request("https://example.com/", key)
    ok, reason = verify_request(headers, authority_of("https://example.com/"),
                                key)
    tampered = dict(headers)
    sig_key = [k for k in headers if k.lower() == "signature"][0]
    tampered[sig_key] = headers[sig_key][:-2] + "AA"
    ok_t, _ = verify_request(tampered, authority_of("https://example.com/"),
                             key)
    doc = directory_document(key)
    print("self-verify ok=%s (%s) tampered_ok=%s doc_keys=%d"
          % (ok, reason, ok_t, len(doc.get("keys", []))), flush=True)
    assert ok and not ok_t and len(doc.get("keys", [])) == 1

    rows = []
    for url in TARGETS:
        unsigned = probe_url(url, timeout=15)
        signed = probe_url(url, timeout=15,
                           extra_headers=sign_request(url, key))
        row = {"url": url, "round": 8,
               "unsigned": slim(unsigned), "signed": slim(signed),
               "verdict_changed":
                   (unsigned["verdict"], unsigned["vendor"]) !=
                   (signed["verdict"], signed["vendor"])}
        rows.append(row)
        print("%s unsigned=%s/%s signed=%s/%s changed=%s"
              % (url, unsigned["verdict"], unsigned["vendor"],
                 signed["verdict"], signed["vendor"], row["verdict_changed"]),
              flush=True)
    with open(OUT, "w") as f:
        json.dump(rows, f, indent=1, sort_keys=True)
    print("wrote %s (%d rows)" % (OUT, len(rows)), flush=True)


if __name__ == "__main__":
    main()
