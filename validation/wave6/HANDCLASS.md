# Wave 6 — Adversarial Battery: Hand Classifications

Discipline: every shape below was classified BY HAND against SPEC's
verdict definitions before the classifier was allowed to see it. The
hand verdict is then pinned as a fixture in `tests/test_adversarial.py`;
any mismatch is a classifier defect, fixed by a generalized rule only
(no per-shape or per-site special cases). Fixes must also produce zero
verdict changes across the wave1–wave5 real-capture corpus.

Reference — SPEC verdicts: OPEN = the resource was served (an agent
can read it); CHALLENGED = an interactive human-verification challenge
was presented; WALLED = a hard block page, no challenge offered;
LOGIN_GATED = content exists behind authentication; RATE_LIMITED =
plain 429 throttle; UNREACHABLE = the fetch itself failed.

## S1 — soft-404 variants

- **W6-S1a** — 200, body is a complete "Page Not Found" document at
  https://example-shop.com/no-such-page. → **OPEN**. The resource's
  answer was served; the agent can read it (it says "not found").
  No wall fired. A soft-404 is a site bug, not a bot wall.
- **W6-S1b** — 404, body contains human-check prose
  ("Verify you are human to continue"). → **OPEN**. A definitive
  404 is an answer, not a challenge (Wave 2, W2-002) — nothing in
  the fetch is actually gated; the status is the verdict.
- **W6-S1c** — 410 Gone, tiny body. → **OPEN**. Definitive answer.
- **W6-S1d** — 200, empty body. → **OPEN**. Nothing walled; an
  empty page was served.

## S2 — redirect-chain walls

- **W6-S2a** — chain [site → site/cdn-cgi/challenge], final 403,
  cf-ray header, "Just a moment" body. → **CHALLENGED / Cloudflare**.
  The challenge is the final answer.
- **W6-S2b** — chain [site → site/cdn-cgi/challenge-platform/h/b/…],
  final 200 full 30 KB homepage at the site's root. → **OPEN**. The
  fetch landed on the real page; a challenge URL *in the chain*
  must never outrank the final served answer. Guards against the
  naive regression "challenge URL seen ⇒ CHALLENGED".
- **W6-S2c** — 200, empty body with only a meta-refresh to
  /px/captcha/. → **CHALLENGED / Generic**. Corrected during the
  run (see below): the page's entire content is a directive to go
  complete a captcha — a CAPTCHA page by reference, per SPEC's
  CHALLENGED definition. The probe does not *follow* the refresh
  (no JS execution), but it can read what the page says, and what
  it says is "go solve a captcha." Calling it OPEN would tell an
  agent the resource was served; it was not — an empty routing
  stub was. (The W5-001 lesson is about widget *includes on served
  content pages*; here the captcha reference IS the page, and
  Amazon's interstitial — form action /errors_page/validateCaptcha
  — proves quoted captcha references carry real challenge signal.)
- **W6-S2c correction record** — the first hand-classification said
  OPEN ("nothing was presented"). The wave-3 Amazon capture then
  falsified the rule that classification implied: broadening the
  captcha-loader blanking to all quoted "captcha" spans (to make
  S2c OPEN) falsely OPENed Amazon's real interstitial, whose only
  "captcha" is the quoted form action /errors_page/validateCaptcha.
  The blanking stays narrow (loader hosts only); S2c classifies
  CHALLENGED on the unblanked reference. A hand-classification
  corrected by capture evidence is the discipline working, not a
  test flipped to match the code — the Amazon page is the
  independent specimen that decides it.

## S3 — 202 / JS-proof pages with no vendor tokens

- **W6-S3a** — 202, body is a "Verifying your browser…" stub with an
  auto-reload script and no vendor tokens. → **CHALLENGED / Generic**.
  The resource was NOT served; the page's only content is a proof a
  non-JS agent cannot perform. This is the AWS/Azure-WAF species with
  the vendor tokens filed off — the generalized rule must catch the
  species, not the brand.
- **W6-S3b** — 200, 20 KB real article page that mentions
  "verifying your browser" once in its text (an article about bot
  walls). → **OPEN**. The served-page gate protects content *about*
  walls from tripping wall markers.
- **W6-S3c** — 200, 3 KB SPA shell: "You need to enable JavaScript to
  run this app" + bundle include, no reload mechanism. → **OPEN**.
  The app was served (its bundle is referenced); the JS notice is a
  capability note, not a wall. The JS-proof marker must require a
  *verification* phrase (not any "enable JavaScript" wording) — this
  shape pins that boundary.

## S4 — multi-vendor stacks

- **W6-S4a** — 403, Server: cloudflare + CF-Ray + body with
  px-captcha div. → **CHALLENGED / PerimeterX**. The wall that fired
  outranks the CDN that fronted (Fiverr's real setup, SPEC).
- **W6-S4b** — 403, cf-mitigated: challenge + px-captcha body. →
  **CHALLENGED / Cloudflare**. Cloudflare's own wall signal fired
  too, so Cloudflare keeps attribution.
- **W6-S4c** — 403, x-datadome header + ak_bmsc cookie + datadome
  body marker. → **CHALLENGED / DataDome**. First wall signal in the
  detection order owns the verdict when both vendors' signals fired.
- **W6-S4d** — 429, ak_bmsc cookie + Kasada KPSDK stub body. →
  **RATE_LIMITED / Kasada**. The body is Kasada's payload; Akamai is
  cookie presence only (W5-003).

## S5 — login walls behind challenges

- **W6-S5a** — 403, cf-ray, "Just a moment" body, final URL
  https://members.example/login. → **CHALLENGED / Cloudflare**. The
  challenge fired before any login form could be reached (Incapsula
  precedent, SPEC) — a vendor wall code at a login URL still wins.
- **W6-S5b** — 302 chain ending at https://app.example/login, final
  200 login page, cf-ray header only. → **LOGIN_GATED**. No wall
  signal; the agent faces an auth form.
- **W6-S5c** — 200, final URL https://accounts.example/login, small
  login page whose copy says "verify you are human" (part of the
  sign-in flow) + password form. → **LOGIN_GATED**. On an identified
  login page, human-check *prose* is part of the auth experience
  (the W5-001 lesson: a captcha widget on a login page is presence,
  not a wall). The generic-marker branch must yield to an identified
  login page — vendor wall codes keep their precedence (S5a/S5d).
- **W6-S5d** — 200, final URL https://site.example/login, Incapsula
  block body. → **WALLED / Imperva**. Vendor wall at a login URL:
  the wall fired first. Pins the S5c boundary from the other side.

## S6 — localized challenge pages (all 403, small, no vendor tokens)

Challenge pages are not English-only. Each of these presents an
interactive human check in the page's own language; all hand-classify
**CHALLENGED / Generic** (a challenge, not a hard block — the page
offers the check, it does not refuse outright):

- **W6-S6a (ES)** — "Verifica que eres un humano para continuar.
  Marca la casilla «No soy un robot»."
- **W6-S6b (DE)** — "Bitte bestätigen Sie, dass Sie ein Mensch sind.
  Klicken Sie auf „Ich bin kein Roboter“."
- **W6-S6c (FR)** — "Veuillez vérifier que vous êtes un humain.
  Cochez la case « Je ne suis pas un robot »."
- **W6-S6d (JA)** — "あなたがロボットでないことを確認してください。
  「私はロボットではありません」にチェックを入れてください。"
- **W6-S6e (EN control)** — "Verify you are human. Check the box:
  I am not a robot." (already CHALLENGED today; pins the control)
- **W6-S6f (PT)** — "Verifique se você é humano. Marque a caixa
  «Não sou um robô»."

## Expected classifier gaps (pre-run predictions)

1. **S3a → false OPEN.** Status 202 with no vendor token and no
   English generic markers falls through to `200 <= status < 400`
   ⇒ OPEN. Generalized fix: a JS-proof species marker (verification
   phrasing on a non-served page) ⇒ CHALLENGED at any status,
   mirroring the AWS/Azure WAF rules.
2. **S5c → false CHALLENGED.** The generic-marker branch runs before
   the login branch. Generalized fix: the generic branch yields when
   the final URL is an identified login page.
3. **S6a–d, S6f → false WALLED.** Generic markers are English-only,
   so a localized challenge falls to bare-403 ⇒ WALLED.
   Generalized fix: localized human-check phrase lists in the
   generic scan.
