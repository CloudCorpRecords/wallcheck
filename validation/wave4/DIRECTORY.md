# Wave 4, Leg B — The Signed-Agent Directory Census

**Question:** who publishes a Web Bot Auth key directory today?
For every one of the 154 hostnames in the Bot Wall Index, one
honest fetch of
`https://<host>/.well-known/http-message-signatures-directory`
(the path the Web Bot Auth architecture draft specifies for an
agent operator's public keys). Rules of the expedition: one fetch
per domain, honest `wallcheck/0.4.0` user-agent, no retries; a
second fetch (`/.well-known/http-message-signatures`) was spent
**only** where the primary answer was an ambiguous 200 that was
not a directory (12 domains); a wall or a 429 ended that domain's
turn — and is itself recorded as data. Raw results:
`results-directory.json`.

**What "adopter" means here, precisely:** the domain *publishes
signing keys* — it is an agent operator whose own agents can prove
their identity cryptographically to any site that verifies. That
is the supply side of signed identity. (The demand side — sites
and vendors *verifying* signatures — is graded in the campaign
report cards.) A directory on a domain does not by itself prove
its agents sign every request; it proves the keys exist, in the
standard place, in the standard format.

## The headline

**Adopters: 3 of 154 (1.9%).**

The Wave 3 audit sampled 5 domains and found 0; the full census
confirms the baseline is near zero — but not zero, and the three
names matter:

| Domain | What it publishes (verbatim from the response body) |
|---|---|
| **chatgpt.com** (OpenAI) | The full profile. One key: `kty: "OKP"`, `crv: "Ed25519"`, `x: "P_1c4SX6fCavDcq6FRegWcVvaOKsp_aXHPEN1FcKDIA"`, `kid: "ArwjqcCqtA5oxEWkzXGC-To_0A9whHmajCHtfe8I9aY"`, `use: "sig"`, `nbf: 1735689600` (2025-01-01), `exp: 1793419865` (2026-10-31). Top-level: `purpose: "ai"`, `signature_agent: "https://chatgpt.com"`. |
| **www.indeed.com** | A bare JWKS: one key, `kty: "OKP"`, `crv: "Ed25519"`, `x: "JrQLj5P_89iXES9-vFgrIy29clF9CC_oPPsw3c5D0bs"`. No `kid`, no `purpose`. |
| **substack.com** | A bare JWKS: one key, `kty: "OKP"`, `crv: "Ed25519"`, `x: "o5kcuyjl063DgfCQaCuOG5Dsij1bec7rSOG10gRAT98"`. No `kid`, no `purpose`. |

All three keys are Ed25519 — the ecosystem's algorithm choice is
unanimous in our sample. OpenAI's document is the reference-grade
one (key id, validity window, declared purpose and agent URL);
Indeed's and Substack's are minimal but valid: a verifier needs
nothing more than `kty`/`crv`/`x` to check a signature.

## The full baseline

| Primary-path outcome | Count | Meaning |
|---|---|---|
| ABSENT (404/410) | 120 | No directory published. The honest, common answer. |
| WALLED_FETCH | 16 | The well-known path itself was walled/challenged/rate-limited to our identified agent. |
| AMBIGUOUS_200 | 12 | A 200 that is not a directory: an HTML page (login redirect, homepage, or SPA shell) served at the well-known path — a soft-404. |
| **ADOPTER** | **3** | A JSON key set, documented above. |
| NO_ANSWER | 3 | The fetch itself failed (UNREACHABLE): flexjobs.com, www.bestbuy.com, zoom.com — consistent with those hosts' index posture; no directory claim either way. |

Details worth naming:

- **The walled sixteen:** gun.io, www.guru.com, www.upwork.com,
  www.glassdoor.com, www.levels.fyi, hub.docker.com,
  huggingface.co, www.npmjs.com (its directory fetch hit the same
  connection-drop pattern as its homepage), www.reddit.com,
  medium.com, www.linode.com, www.eventbrite.com,
  www.w3schools.com, www.reuters.com, www.wsj.com,
  www.expedia.com. On these properties an agent cannot even *ask*
  the identity question — the directory path gets the same wall as
  everything else.
- **The ambiguous twelve** (gitlab.com, www.instagram.com,
  www.tiktok.com, www.twitch.tv, www.netflix.com,
  clipwise.replit.app, cloud.google.com, deno.com,
  registry.terraform.io, www.shopify.com, www.pinterest.com,
  www.khanacademy.org): all twelve variant-path fetches were also
  non-directories (eleven ambiguous 200s; Shopify's variant was a
  clean 404). These are soft-404s, not adopters; the census does
  not round a homepage up to a key directory.
- **Wave 3's sample holds:** github.com, reneturcios.replit.app
  and cloudcorprecords.github.io returned clean 404s; clipwise
  returned its SPA shell (ambiguous) — 0 adopters among the five
  audited domains, exactly as the audit found (example.com is not
  an index hostname and was not in this census).

## What this baseline is for

This is the "before" picture for the campaign's identity front.
Three of 154 significant domains publish keys; one of the three
does it completely. Every future wave re-runs this census against
`results-directory.json`, so adoption becomes a trend line with a
denominator, not a vibe. And as of Wave 4, wallcheck's own keys
can join the list the moment we choose a domain to publish on:
`wallcheck keygen --alg ed25519` mints a directory-ready key, and
`validation/wave4/sample-directory.json` shows the exact document
format — the same shape Indeed and Substack serve, one `purpose`
field short of OpenAI's.

One practical note for the next wave: the census shows directory
publication is an *agent-operator* behavior concentrated in
AI/platform companies. The reciprocal measurement — sending our
own signed requests to verifying endpoints and recording who
honors them — remains open work; the vendor report cards grade
the *documented* verification support in the meantime.
