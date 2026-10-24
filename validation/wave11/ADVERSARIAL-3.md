# Wave 11 — Adversarial Battery v3 (Leg B)

31 hand-classified shapes, all NEW relative to Wave 6 (S1–S6) and Wave 10
(B1–B10) — see `HANDCLASS-3.md` for the hand verdicts and
`tests/test_adversarial3.py` for the pins. First run: **21 pass, 10
mismatches — 9 were genuine defects, all fixed test-first with
generalized rules; 1 (C6b) was a verdict/vendor inconsistency of the
Wave 10 W10-006 species, also fixed.** No honest limitations had to
be ledgered beyond the two boundary pins that were already the
discipline's position (C1a, C3b). Full suite **183/183** (152 prior +
31 new); 44-capture corpus diff clean.

## Defects and fixes

**W11-001 — form-action redirect targets read OPEN (C1b).** A small
page whose only content is an auto-submitting form posting to
`/challenge/verify-human` read OPEN: the Wave 10 redirect-target
rule covered meta refresh and JS location only. Generalized fix:
form actions join the redirect-target collection, gated to SERVED
(2xx) small pages — a form is interactive content, not a routing
directive, so a 403 page carrying a login form stays a refusal
(the Wave 8 B2b rule), not a gate by reference. Content-target
form actions (search, login on a login page) produce no evidence.

**W11-002 — "verify your request" stub read OPEN (C1c).** A stub
whose only content is "Please wait while we verify your request"
carried no JS_PROOF phrase. Generalized fix: "verify your
request" / "verifying your request" join the JS_PROOF phrase list
(request-directed verification wording, interstitial-voice like
the rest of the list). Deliberately NOT added: "verification in
progress", which also describes account-email verification flows —
a different gate, and claiming it would false-positive status
pages.

**W11-003 — Turnstile widget on a login form read CHALLENGED
(C2c).** The classifier's own W7-001 note named this shape: a
challenge-platform loader on a small login page is the form's own
check, but the vendor branch (unlike the generic branch) did not
yield to login pages. Generalized fix: when the ONLY Cloudflare
signal on an identified login page is the challenge-platform
loader (no cf-mitigated, no Just a moment, no block page, no
other vendor/generic wall signal), the CF branch yields and the
login branch owns the verdict → LOGIN_GATED / Cloudflare
(presence attribution, the Wave 6 S5b pattern). Boundaries held:
the Wave 7 careerjet case (loader on a check-only, non-login
page) still reads CHALLENGED, and "Just a moment" at a login URL
(Wave 6 S5a, a fired wall) still reads CHALLENGED.

**W11-004 — Italian, Dutch, Korean challenge pages read WALLED
(C4b/C4c/C4d).** The localized phrase list stopped at ES/DE/FR/
JA/PT, so an Italian, Dutch, or Korean challenge fell to bare-403
WALLED. Generalized fix: the list gains Italian ("verifica di
essere umano", "non sono un robot"), Dutch ("bevestig dat u geen
robot bent", "ik ben geen robot"), and Korean ("로봇이 아님을 확인",
"나는 로봇이 아닙니다") — language coverage, not per-site rules,
in the Wave 6 pattern.

**W11-005 — generic vendor leaked onto a login verdict (C6b).**
A login page carrying an hCaptcha widget + human-check prose
read LOGIN_GATED / Generic: the verdict said "auth gate" while
the vendor field named a wall. Generalized fix (the Wave 10
W10-006 species): a LOGIN_GATED verdict with a Generic-only
vendor is nulled — the generic evidence was judged to be auth
copy, not a wall. Named-vendor presence (cf-ray on a served
login page, Wave 6 S5b) is untouched; only the generic-only leak
is nulled.

**W11-006 — robots wildcard block overstated as FAIL (C8b/C8c/
C8g).** A wildcard `Disallow: /` PLUS a named-agent carve-out
(GPTBot Allow: /, ClaudeBot restricted to /private) read FAIL:
the `wildcard_all` short-circuit fired whenever a wildcard rule
existed, even when a tracked agent was explicitly reachable.
Generalized fix: FAIL means every tracked agent is blocked; a
carve-out drops the grade to WARN with the blocked/restricted
agents named. The WILDCARD_BLOCK_ALL evidence line is kept. A
wildcard block with NO carve-out still FAILs exactly as before
(all four agents blocked), and group order does not matter
(C8g: named group first, same WARN).

## Pins that held (no classifier change needed)

- Silent stubs: a reload-timer-only empty page → OPEN (C1a, the
  Wave 3 honest-limitation boundary, re-affirmed: no deterministic
  signal exists); an SPA loading shell → OPEN (C1d, Wave 6 S3c).
- Widgets: hCaptcha-only and Turnstile-only pages → CHALLENGED
  (C2a/C2b); a px-captcha div at a login URL → CHALLENGED /
  PerimeterX (C2d, vendor precedence over the login yield).
- Image/SVG: an img captcha with alt text → CHALLENGED (C3a); an
  SVG whose `<text>` reads "Verify you are human" → CHALLENGED
  (C3c, raw-body scan); a textless SVG graphic → WALLED, vendor
  none (C3b, honest boundary: pixels with no text carry no
  signal, and the 403 owns the verdict).
- Languages: EN+ES mixed → CHALLENGED (C4a).
- Status+header only: 403 + cf-ray → WALLED / Cloudflare (C5a);
  403 + an unknown vendor's header (Sucuri) → WALLED, vendor none
  (C5b — a synthetic header alone does not earn a vendor rule;
  Sucuri is noted as a future candidate IF a live capture shows
  its wall page); 429 + Retry-After → RATE_LIMITED (C5c); 503 +
  cf-ray → UNREACHABLE, vendor none (C5d, W10-006).
- Login widgets: a reCAPTCHA loader on a login form → LOGIN_GATED
  (C6a, loader blanking); hCaptcha + prose on a login form →
  LOGIN_GATED (C6b, generic yields to login).
- Audit sitemaps: a `<sitemapindex>` → PASS (C7a); a sitemapindex
  with dead children → PASS (C7b, scope: the check grades the file
  served, not the tree — child-fetching would break the ≤10-fetch
  budget); a redirected sitemap resolving to a urlset → PASS
  (C7c).
- Audit robots: crawl-delay only → PASS (C8a, politeness, not a
  block); lowercase agent names → WARN, restricted (C8e,
  case-insensitive matching); empty Disallow → PASS (C8f,
  empty means allow); Sitemap: declaration → PASS with evidence
  (C8d).

## Verification

- 31/31 battery fixtures pass; full suite 183/183 (zero
  regressions on the 152 prior pins).
- Corpus check: new classifier vs the 44 wave1–7 real captures —
  no verdict or vendor changed (baseline in
  `corpus-baseline.txt`, post-fix in `corpus-after.txt`, diff
  empty). The three Wave 10 risk captures (npmjs CHALLENGED /
  Cloudflare, kickstarter OPEN, duolingo OPEN) and careerjet
  (non-login URL, so the W11-003 yield cannot touch it) are all
  unchanged.

## Saturation consequence

Wave 11 found **6 genuine defects** (5 classifier, 1 audit-tool
spanning 3 shapes). Under the overnight saturation test the clock
resets AGAIN: Wave 11 is NOT a clean wave, and the two-wave clean
pair must restart from the next defect-free measurement wave.
