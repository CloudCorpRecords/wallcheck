# Wave 6, Leg A — Adversarial Hardening Battery (DONE)

24 synthetic edge shapes, each classified by hand first
(`HANDCLASS.md`), then pinned as fixtures in
`tests/test_adversarial.py`. The battery found **4 classifier
defects, all fixed test-first with generalized rules** — plus one
hand-classification the evidence corrected.

## Defects and fixes

**W6-001 — 202 JS-proof stub without vendor tokens → false OPEN.**
A "Verifying your browser…" stub served 202 with no vendor
signature fell through to OPEN. Generalized fix: the `JS_PROOF`
marker — interstitial-voice verification phrasing
("verifying your browser", "checking your browser", "performing
security verification", "please enable javascript to continue",
…) on a non-served page ⇒ CHALLENGED (Generic) at any status,
the same reasoning as the AWS/Azure WAF stub rules. This is the
vendor-neutral species behind W3-001 and W5-002 with the brand
filed off. Boundaries pinned: a 20 KB article *about* bot walls
(S3b) stays OPEN via the served-page gate; a 3 KB SPA shell whose
only JS note is "enable JavaScript to run this app" (S3c) stays
OPEN — the phrases are interstitial-voice, not capability notes.

**W6-002 — login page with human-check prose → false CHALLENGED.**
A 200 sign-in page whose copy says "verify you are human" was
CHALLENGED by the generic branch before the login branch ran.
Generalized fix: the generic-marker branch now yields to an
identified login page — human-check prose on a sign-in form is
part of the auth experience (the W5-001 lesson: a captcha widget
on a login page is presence, not a wall). Vendor wall codes keep
their precedence: a Cloudflare challenge at /login (S5a) is still
CHALLENGED, an Incapsula block at /login (S5d) still WALLED.

**W6-003 — localized challenge pages → false WALLED.**
Challenge pages in Spanish, German, French, Japanese (and
Portuguese) carried no English markers, so they fell to bare-403
⇒ WALLED. Generalized fix: the generic human-check scan now
matches tight interstitial-voice phrasing in ES/DE/FR/JA/PT
("verifica que eres humano", "dass sie ein mensch sind", "vérifiez
que vous êtes humain", "ロボットでないことを確認", "verifique se
você é humano", …). All five classify CHALLENGED / Generic; the
EN control was already correct.

**W6-004 — Incapsula block page served 200 → LOGIN_GATED.**
The Imperva verdict rule was pinned to 401/403, but the block
page is commonly served 200. Generalized fix: `IMPERVA_BLOCK_PAGE`
evidence (the incident-ID line, the block page's signature) ⇒
WALLED at any status — parallel to CF_BLOCK_SORRY, which already
wins at any status. A bare "incapsula" mention on 401/403 keeps
the old pin.

## The hand-classification the evidence corrected

**W6-S2c** (200, empty body, meta-refresh to /px/captcha/) was
first hand-classified OPEN. Making that true required broadening
the captcha-loader blanking to all quoted "captcha" spans — which
the wave-3 Amazon capture then falsified: Amazon's real
interstitial ("Click the button below to continue shopping",
form action /errors_page/validateCaptcha) has its only "captcha"
in that quoted span, and the broadened blanking falsely OPENed it
(the corpus diff caught it: 41 captures, 1 mismatch). The blanking
stays narrow (loader hosts only); S2c re-classifies **CHALLENGED /
Generic** — a page whose whole content routes the client to a
captcha is a CAPTCHA page by reference, and calling it OPEN would
tell an agent the resource was served when an empty stub was.

## Pins that held (no classifier change needed)

- Soft-404s (200/404/410/empty 200) → OPEN: the status is the answer.
- Challenge URL in the redirect chain but a real 30 KB homepage
  served at the end → OPEN: the final answer outranks the chain.
- Cloudflare-fronted PerimeterX captcha → CHALLENGED / PerimeterX
  (the wall that fired outranks the CDN that fronted); with
  cf-mitigated: challenge also present → Cloudflare keeps it.
- DataDome over an Akamai cookie → CHALLENGED / DataDome;
  Kasada stub over an Akamai cookie on 429 → RATE_LIMITED / Kasada.

## Verification

- 24/24 adversarial fixtures pass; full suite **109/109**
  (85 pre-existing pins all green — zero regressions).
- Corpus check: new classifier vs latest recorded verdicts on all
  41 wave1–5 real captures → 1 diff, the npmjs flapping case
  (capture holds a genuine Cloudflare challenge body; the
  UNREACHABLE record is a different, dropped fetch — correct per
  the merge rule). The Amazon interstitial the battery nearly
  broke classifies CHALLENGED / Generic, as recorded.
- MCP smoke: initialize, tools/list, classify + probe_url — OK.

SPEC.md updated: Generic vendor section (loader-blanking
narrowness, JS_PROOF, localized phrases), verdict precedence
(login yield, Incapsula incident rule).
