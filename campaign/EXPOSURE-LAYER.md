# Wallcheck Exposure Layer — expansion plan

**Status: v1 built and running its first sweep, 2026-10-24.**
Born from a real catch: wallcheck's own evidence pipeline surfaced
Monster.com's Next.js server-actions encryption key, publicly exposed
as a `NEXT_PUBLIC_` variable — validated live, contained on our side,
and disclosed privately through Monster/CareerBuilder's published
responsible-disclosure channel the same day. This layer turns that
accident into a method.

## What it does

Every page wallcheck fetches is already the page a site hands to any
anonymous visitor. The exposure layer scans that served content for
key-like material and sorts it into three honest classes:

- **CANDIDATE_EXPOSURE** — server-secret classes that should never be
  public: encryption/private keys (incl. any public-env variable whose
  name carries SECRET / PRIVATE / ENCRYPTION / PASSWORD), live secret
  keys (Stripe `sk_live`, webhook secrets), platform tokens (GitHub,
  Slack, SendGrid, Twilio), credentialed database URLs, secret fields
  in inline config, long-lived JWTs.
- **PUBLIC_BY_DESIGN** — the public half of the web's key pairs:
  Google frontend keys, Stripe publishable keys, app IDs, OAuth client
  IDs, public analytics keys. Normal. Counted for the census, never
  reported to anyone as a problem.
- **VISITOR_TOKEN** — short-lived JWTs a site issues to any visitor
  (e.g. Azure WAF tokens). This is wall machinery handing a credential
  to the thing it is screening — census data, not a leak.

Alongside: a **front-door check** per site — does it publish
`/.well-known/security.txt`, the standard security contact route?
(The Monster case: no security.txt, but a disclosure-policy page on
both monster.com and careerbuilder.com naming the reporting address.)

## Hard rules (unchanged wallcheck line, now encoded in the tool)

1. Anonymous GETs only, one fetch per URL, no retries against a wall,
   no JavaScript, no interaction, no challenge-solving — and always
   under wallcheck's own identifying user agent.
2. Found values are never stored, printed, quoted or transmitted.
   Records carry only: pattern, class, value length, and a SHA-256
   fingerprint prefix — enough for an owner to recognise their key,
   useless to anyone else.
3. No found value is ever *used*: no decryption, no test calls, no
   validation against the owner's API. Exposure is the finding;
   exploitability is the owner's to assess.
4. Candidate findings are private by default. Nothing about a
   candidate is published until the owner has resolved it (or
   publicly acknowledged it). Aggregate census publications use
   counts, classes and pattern names only — and only for the
   public-by-design and visitor-token classes.
5. Raw captures are scrubbed before they ever leave this machine
   (scripts/scrub_captures.py) — the lesson our own repo learned when
   GitHub's scanner flagged third-party keys in our evidence files.

## The disclosure pipeline (per candidate, repeatable)

1. **Detect** — exposure scan flags a candidate on a live page.
2. **Validate** — re-fetch the page independently (different UA,
   repeated): the value must be present, static, and identical —
   a fixed deployment key, not a session artifact. Hash comparison
   only.
3. **Document privately** — validation note + project log entry in
   the private Drive folder ("Wallcheck — Private Research Log");
   local working files under validation/ (never pushed).
4. **Find the front door** — security.txt → published disclosure
   policy page → other published security contact. Never a guessed
   address.
5. **Disclose** — policy-compliant email: what, where, how to
   reproduce, fingerprint for the owner's own verification, what we
   did and didn't do, the small fix. Rene sees the exact text and
   approves each send.
6. **Watch** — a reply-watch checks for their response inside their
   promised window; one nudge if it lapses, then patience.
7. **Publish (only after resolution)** — the story joins the
   wallcheck campaign: a wall measured, a front door missing or
   found, a company protected. Credit flows both ways; the owner is
   named as responsive, the project as the finder — with the owner's
   knowledge, per their policy where one exists.

## Roadmap

- **Wave 1 (running)**: 500 index homepages, inline content only,
  plus the security.txt census.
- **Wave 2 (built — deep mode)**: `exposure_scan.py deep` fetches the
  first-party JS chunks linked from the homepage (same-origin only,
  document order, capped at 8), plus each chunk's publicly served
  `.map` source map — source maps can embed the full original sources,
  config included. Same rules, same fingerprint-only output.
- **Wave 3 (built — deep mode, deliberately narrow)**: the same deep
  mode also fetches each site's app shells at exactly three standard
  paths — `/login`, `/signin`, `/app` — and scans whatever is served,
  including 404 shells (Monster's key was on its login page, not the
  homepage). The list is fixed and published here on purpose: three
  conventional paths, never a path fuzzer. Per-site worst case for
  deep mode: 1 + 2×8 + 3 = 20 honest GETs.
- **Standing**: exposure scan folds into the normal wallcheck probe,
  so every future wall measurement also records the exposure classes
  it saw — the index gains an "exposure" column next to the verdict.

## Why this fits the war

The campaign's claim was that bot walls are security theatre aimed at
the wrong door. The exposure layer proves it with the sites' own
output: the walls screen agents at the gate while the front door
hands keys, IDs and tokens to anyone who asks politely. Every
candidate we help a company fix — privately, without ever touching
the key — is that argument made in the real world.
