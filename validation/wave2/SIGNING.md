# Wave 2, Leg B — Signed Agent Identity (v0.2 passport prototype)

The SPEC's v0.2 bet: agents get walled partly because they are
anonymous. RFC 9421 HTTP Message Signatures are the standards-based
way to stop being anonymous — sign the request, and a site can allow
a *known* agent instead of challenging every agent-shaped client.

## Implementation choice, and why

- **Algorithm: `hmac-sha256` (RFC 9421 §3.3.3), shared secret.**
  Checked first, per the build rules: the `cryptography` package is
  **not installed** on this VM, and Ed25519 exists nowhere in the
  Python standard library. PyNaCl 1.6.2 happens to be installed here,
  but wallcheck's core is stdlib-only *by design* (SPEC.md) — a
  dependency that exists on one dev VM and nowhere else is not a
  foundation. `hmac-sha256` is a registered RFC 9421 algorithm, so
  the output is a real RFC 9421 signature, producible and verifiable
  with `hmac` + `hashlib` + `base64` alone.
- **Honest limitation:** the public Web Bot Auth ecosystem
  (Cloudflare's key directory, the IETF draft profile) runs on
  **Ed25519 with public keys**. A shared secret cannot be published
  in a directory — both sides must hold it beforehand. So this
  prototype covers the bilateral case: an agent operator and a site
  owner who agree on a secret out of band, and owners testing their
  own endpoints. It does **not** claim directory-compatible public
  Web Bot Auth identity. If a stdlib-grade Ed25519 path ever becomes
  acceptable (or the dependency rule is relaxed for an optional
  extra), the signer is structured to add `ed25519` alongside.

## What shipped (src/wallcheck/sign.py, CLI in cli.py)

- `wallcheck keygen [--out FILE] [--keyid ID]` — 32-byte secret,
  JSON key file at mode 0600, prints keyid + a non-secret sha256
  fingerprint (never the secret).
- `wallcheck probe <url> --sign KEYFILE` — attaches
  `Signature-Input` / `Signature` per RFC 9421 to the same single
  honest fetch. Covered components: `"@authority"` (plus
  `"content-type"` when a content type is present — GET probes have
  none). Signature params: `keyid`, `alg="hmac-sha256"`, `created`,
  `expires` (300 s window), `nonce`, `tag="web-bot-auth"`.
- **Offline verify** — `wallcheck.sign.verify_request(...)`:
  recomputes the signature base from the presented headers and
  compares in constant time; rejects on unknown keyid, wrong alg,
  future `created`, expired `expires`, any tampered component or
  parameter.
- `wallcheck verify-server --key KEYFILE [--host] [--port]` — a
  tiny stdlib HTTP server that answers 200 only to correctly signed
  requests, 401 with the rejection reason otherwise. This is the
  owner-side test harness: point `probe --sign` (or any signer) at
  it and watch identity get honored.

## Verification evidence

- **Unit/integration tests: 14** in tests/test_sign.py — keyfile
  round-trip + permissions; signature-input shape (components and
  all params present); sign→verify round-trip; content-type
  coverage; tamper failures (authority, signature bytes, signed
  params), expiry, wrong secret, unknown keyid, missing headers;
  and the verify-server end-to-end on localhost (unsigned → 401,
  signed → 200, wrong key → 401). Suite total after Wave 2:
  **46 tests, all green** (24 pre-existing + 8 classifier fixtures +
  14 signing).
- **Manual CLI smoke:** `keygen` → `verify-server` → unsigned curl
  401 ("missing Signature/Signature-Input headers") → signed
  request 200 ("signature OK — ok (keyid …, tag web-bot-auth)").
- **Signed probes of our own properties** (`results-signed.json`):
  clipwise.replit.app, reneturcios.replit.app,
  cloudcorprecords.github.io — probed unsigned, then signed, one
  fetch each. **Nothing changed** (OPEN 200 / 200 / 404 both ways),
  exactly as expected: Replit and GitHub Pages don't check
  signatures, so a signed request is indistinguishable from an
  unsigned one there. The signatures themselves verify offline
  against each target's authority (re-checked from the recorded
  run's key). The deliverable is the working, tested signer — not a
  behavior change on hosts that don't participate yet.

## What server-side adoption looks like (feeds the v0.3 owner audit)

For an owner, honoring signed agents is three steps, all testable
today with the verify-server as the reference behavior:

1. **Publish acceptance out of band (HMAC) or via directory
   (Ed25519):** for the bilateral case, exchange the shared secret
   the way you'd exchange an API key; the secret *is* the identity
   claim, so `keyid` should map to a named agent operator.
2. **Verify at the edge:** recompute the RFC 9421 base from
   `@authority` (+ covered headers), check `alg`, the
   created/expires window, and the tag `web-bot-auth`; reject or
   fall back to the normal bot policy on any failure — never fail
   open.
3. **Exempt verified signatures from managed challenges on public
   paths only:** in Cloudflare terms, a WAF custom rule like
   "verified signature present → skip managed challenge" for GETs on
   public content, while authenticated/admin paths keep full
   protection. That is the exact checklist the v0.3 `wallcheck
   audit` will emit, with the robots/llms.txt/escape-route findings
   alongside it.

Until platforms adopt step 3, a signature changes nothing at the
wall — Wave 2's signed probes prove the client side works and
measure that reality instead of assuming it.

---

## Wave 4 addendum (2026-10-23): Ed25519 ships — the HMAC ceiling is gone

The "if a stdlib-grade Ed25519 path ever becomes acceptable"
condition above was met the direct way: **Ed25519 is now implemented
in pure Python stdlib** inside `src/wallcheck/sign.py` — RFC 8032
over `hashlib` SHA-512 and big-integer field arithmetic, point
operations in extended twisted Edwards coordinates. No new
dependency; the stdlib-only design rule is intact.

- `wallcheck keygen --alg ed25519` — 32-byte random seed; the key
  file holds `seed_b64` (private) and `public_b64`. `probe --sign`
  auto-detects the key's algorithm and emits RFC 9421 signatures
  with `alg="ed25519"`, `tag="web-bot-auth"`. HMAC keys work exactly
  as before.
- **The correctness gate was the official RFC 8032 §7.1 test
  vectors**, encoded as unit tests (`tests/test_ed25519.py`, 16
  tests): TEST 1 (empty message), TEST 2 (1-byte), TEST 3 (2-byte)
  and the TEST SHA(abc) multi-byte vector — public-key derivation,
  signature bytes, verify, and tamper rejection all match the RFC.
  A bonus interop check cross-verifies our signatures with PyNaCl
  where it happens to be installed (the core never imports it).
  RFC 9421 round-trips, wrong-key and expiry failures, public-only
  verification, and a verify-server end-to-end with an Ed25519 key
  are covered in the same file. Suite total after Wave 4:
  **75 tests, all green.**
- **Performance is a documented non-goal.** The pure-Python
  implementation is not constant-time and takes tens of milliseconds
  per signature — irrelevant for one signed request per probe,
  disqualifying for a high-volume signing service. The module
  docstring says so, in those words.
- **Directory compatibility is now real.** `wallcheck.sign.
  directory_document(key)` renders an Ed25519 key as a Web Bot
  Auth directory document (`purpose: "Web Bot Auth"`, JWKS `keys`
  with `kty: "OKP"`, `crv: "Ed25519"`, base64url `x`) — the exact
  format a site fetches from
  `/.well-known/http-message-signatures-directory`. A sample for
  the campaign's own Wave 4 key is at
  `validation/wave4/sample-directory.json` (public material only;
  the seed is not in the repository). Wave 4 Leg B measured how
  many of the index's 154 domains publish such a directory
  themselves: see `validation/wave4/DIRECTORY.md`.

**Version: 0.4.0.**
