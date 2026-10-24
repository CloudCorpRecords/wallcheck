# Wave 5, Leg C — The Signed-vs-Unsigned Experiment

**Question:** does attaching a valid Web Bot Auth signature to
our probe change what any wall answers? This is the campaign's
key measurement — the demand side of signed identity, tested
rather than asserted.

**Method.** A fresh Ed25519 key was minted with the shipped tool
(`wallcheck keygen --alg ed25519`, keyid `wallcheck-wave5`,
fingerprint `ebe1dae10a955795`; the key file lives in this
directory at mode 0600 and its seed is never printed anywhere —
the public half is `7V4MWyCs/V9Kvnn/nzbWhcoVHiJTiC6fN/pHKV1fwOk=`).
For each target: one unsigned `wallcheck probe`, then one
Ed25519-signed probe (RFC 9421, `tag="web-bot-auth"`, the exact
code path any user gets from `probe --sign`). Same honest
user-agent both times; the signature is the only difference.
The signatures themselves were verified offline against the key
before the run was trusted (verify round-trip passes; a tampered
signature fails closed). Raw results:
`results-signed-experiment.json`.

**Targets:** the three directory adopters from the Wave 4 census
(chatgpt.com, www.indeed.com, substack.com), six walled/challenged
platforms (Upwork, Fiverr, Guru, npmjs, Medium, eBay), and our
three own properties as controls.

## The result: 12 of 12 unchanged

| Target | Group | Unsigned | Signed |
|---|---|---|---|
| chatgpt.com | adopter | OPEN 200 | OPEN 200 |
| www.indeed.com | adopter | OPEN 200 | OPEN 200 |
| substack.com | adopter | OPEN 200 | OPEN 200 |
| www.upwork.com | walled | WALLED 403 (Cloudflare) | WALLED 403 (Cloudflare) |
| www.fiverr.com | challenged | CHALLENGED 403 (PerimeterX) | CHALLENGED 403 (PerimeterX) |
| www.guru.com | walled | WALLED 403 (Imperva) | WALLED 403 (Imperva) |
| www.npmjs.com | challenged | CHALLENGED 403 (Cloudflare) | CHALLENGED 403 (Cloudflare) |
| medium.com | walled | WALLED 403 (Cloudflare) | WALLED 403 (Cloudflare) |
| www.ebay.com | walled | WALLED 403 (Akamai) | WALLED 403 (Akamai) |
| clipwise.replit.app | control | OPEN 200 | OPEN 200 |
| reneturcios.replit.app | control | OPEN 200 | OPEN 200 |
| cloudcorprecords.github.io | control | OPEN 404 | OPEN 404 |

No verdict changed. No status changed. No vendor changed. There
is nothing to capture-verify twice because there is no change to
claim — and that *is* the finding.

## The honest reading

An unregistered Ed25519 key proves a mathematical fact (the
request was signed by whoever holds this seed) to exactly nobody
who is checking. Three distinct reasons, all measured or
documented in this campaign's own record:

1. **The walled six do not verify unknown signers.** Their walls
   sort by signals they already trust — Cloudflare's verified-bot
   program classifies a signed agent as verified only when the
   operator is *registered* (Cloudflare's BotBase directory;
   `campaign/FIX-KIT.md` §1 and §4 walk both sides of this). Our
   key is in no directory and no trust set, so at Upwork the
   signature was not rejected — it was *not consulted*. The 403 a
   signed request received is byte-for-byte the wall's answer to
   anonymity, because to the wall, that is what an unregistered
   signature still is.
2. **The adopters publish keys for *their* agents, not doors for
   ours.** ChatGPT, Indeed and Substack serve their homepages
   openly to any identified fetch; their directories exist so
   *their* agents can prove themselves at *other* sites' walls.
   Signing our request to them changes nothing because nothing
   was gated.
3. **The controls don't check** — as in Wave 2's HMAC dogfood,
   our own properties treat signed and unsigned identically
   because nothing on them verifies. Expected; recorded anyway.

What would have to change for a signature to matter is therefore
precise, and none of it is in the agent's hands: the agent
operator registers the key where verifiers look (a published
directory + program enrollment), and the wall's owner exempts
verified signatures on public paths. Both steps are documented
as an owner/operator checklist in `campaign/FIX-KIT.md` (§1, §4).
Until then, "we signed the request" is a true statement with no
mechanical consequence — the campaign will keep re-running this
experiment per wave so the round where that stops being true is
caught on the record.

## Appendix — what "reference-grade" means, verified live

Wave 4 called chatgpt.com's directory "reference-grade" from its
response body. Wave 5 re-fetched it
(`chatgpt-directory-live.json` in this directory) and validated
the document structurally:

- It parses as JSON with exactly the top-level fields `keys`,
  `purpose`, `signature_agent`.
- `purpose: "ai"`; `signature_agent: "https://chatgpt.com"` —
  the document declares *what the key is for* and *who the agent
  is*, not just the key material.
- One key: `kty: "OKP"`, `crv: "Ed25519"`, `kid:
  "ArwjqcCqtA5oxEWkzXGC-To_0A9whHmajCHtfe8I9aY"`, `use: "sig"`.
- The `x` value base64url-decodes to **exactly 32 bytes** — a
  well-formed Ed25519 public key, not a placeholder.
- Validity window: `nbf` 1735689600 (2025-01-01) → `exp`
  1793420455 (2026-10-31); the window contains the fetch time —
  the published key is *currently* valid, not a stale artifact.
- One living detail: `exp` moved +590 seconds against the Wave 4
  snapshot (1793419865 → 1793420455). The document is being
  actively maintained/regenerated by its operator — the
  opposite of a forgotten launch artifact.

Indeed's and Substack's documents (Wave 4) are bare JWKS sets:
valid and verifiable, but with no `kid`, no window, no declared
purpose. That gap — between *a key exists* and *a key is
operated* — is the concrete content of "reference-grade," and
the bar the campaign's own directory document will be held to
when there is a domain decision to publish one on.
