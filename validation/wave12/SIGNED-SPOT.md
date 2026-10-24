# Wave 12 — Signing spot-check (Leg C)

Second spot-check of the signed-vs-unsigned question, on a fresh
Ed25519 key (keyid wallcheck-d51821cb, 0600 file at
`validation/wave12/wave12-spot-key.json`, secret never printed).
Runner: `validation/wave12/run_signed_spot.py`; results:
`validation/wave12/results-signed-spot.json`.

## Self-verification (offline, no network)

- Own verifier accepts own signatures: ok (tag web-bot-auth).
- Tampered signature rejected.
- `directory_document()` renders 1 key for the fresh key.

## Live spot-check: 2/2 unchanged, as expected

| target | unsigned | signed | changed |
| --- | --- | --- | --- |
| chatgpt.com (reference-grade directory adopter) | OPEN | OPEN | No |
| www.ahrefs.com (Wave 7 census adopter) | OPEN | OPEN | No |

Reading: an unregistered key is not in either site's trust set,
so the signature is not consulted — the same result as the Wave 5
experiment (12/12 unchanged) and the Wave 10 regression (7/7
unchanged). Three independent rounds now agree: signed requests
change nothing anywhere measured, because no measured site honors
a key it did not itself publish or register. That is the campaign
finding, not a tool failure: the passport works (self-verify,
directory rendering, RFC 9421 format), and the adoption gap is on
the sites' side — which is what the directory census (4/499
adopters) and the fix kit exist to move.
