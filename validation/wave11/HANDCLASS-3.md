# Wave 11 — Adversarial Battery v3: Hand Classifications

Discipline (as Waves 6 and 10): every shape below was classified BY HAND
against SPEC's verdict definitions BEFORE the classifier was allowed to
see it. All shapes are NEW relative to Wave 6 (S1–S6) and Wave 10
(B1–B10): no repeats of soft-404 variants, redirect-chain walls (meta
refresh / JS location — but see C1b, which is the FORM-ACTION species,
not a repeat), 202 JS-proof stubs with vendor tokens, multi-vendor
stacks, login hybrids, geo-blocks, meta-refresh walls, consent
boundaries, Cloudflare error variants, app interstitials, DataDome
variants, or audit soft-404 variants. Any mismatch is a defect
candidate: fix generalized with a capture-built fixture, or ledger it
as a genuine honest limitation with the reason. No silent passes, no
per-shape special cases.

Reference — SPEC verdicts: OPEN = the resource was served; CHALLENGED =
an interactive human-verification challenge was presented; WALLED = a
hard block page, no challenge offered; LOGIN_GATED = content exists
behind authentication; RATE_LIMITED = plain 429 throttle; UNREACHABLE =
the fetch itself failed. Audit grades: PASS / WARN / FAIL per check.

## C1 — silent JS-proof stubs (200, no vendor tokens)

The Wave 3 honest-limitation boundary, re-tested: "a silent JS-proof
page with neither [signature nor human-check wording] would still read
OPEN — no deterministic signal exists to catch it honestly." These
shapes probe exactly where that boundary sits.

- **C1a** — 200, tiny page, only content an auto-reload script
  (`setTimeout(location.reload, 3000)`) and an empty body. No text,
  no tokens, no form. → **OPEN**. Honest-limitation pin: a reload
  timer alone is not a challenge signal — empty pages and shells
  reload too. Claiming CHALLENGED here would false-positive every
  empty page. The page presents nothing a human could even act on.
- **C1b** — 200, tiny page, only content an auto-submitting form
  whose action is `/challenge/verify-human` (no "captcha" word
  anywhere). → **CHALLENGED / Generic**. The Wave 10 B4 reference
  principle in form-action form: the page's entire content routes
  the client to a challenge. The mechanism (form action vs meta
  refresh vs JS location) is not the boundary — the target is.
  Predicted gap: the redirect-target rule covers meta refresh and
  JS location only, not form actions.
- **C1c** — 200, tiny page, only content "Please wait while we verify
  your request" + a verification script, no vendor tokens. →
  **CHALLENGED / Generic**. The page's only content is a
  verification proof the agent cannot perform — the JS_PROOF
  species, in wording the current phrase list does not contain.
  Predicted gap: JS_PROOF phrases lack "verify your request" /
  "verification in progress" wording.
- **C1d** — 200, 3 KB SPA shell ("Loading…" + bundle include, no
  reload, no verification wording). → **OPEN**. Pin (Wave 6 S3c
  species): a capability note is not a wall.

## C2 — widget variants (hCaptcha vs Turnstile)

- **C2a** — 403, small page, only an hCaptcha widget (div
  `class="h-captcha"` + js.hcaptcha.com loader script), no prose. →
  **CHALLENGED / Generic**. The widget IS the challenge mechanism;
  the "captcha" substring in the widget class is the signal. Pin
  (the loader-blanking regex must not blank the widget class — only
  quoted loader URLs).
- **C2b** — 403, small page, only a Turnstile widget (div
  `class="cf-turnstile"` + challenges.cloudflare.com script), no
  prose. → **CHALLENGED / Cloudflare**. The challenge-platform
  script reference is the wall signal. Pin.
- **C2c** — 200, final URL https://site.example/login, a login form
  carrying a Turnstile widget for its own sign-in (no "Just a
  moment", no cf-mitigated, no block text). → **LOGIN_GATED**.
  The Wave 6 S5c principle, vendor-branch species: a widget on a
  login page is part of the auth experience, not a wall — the
  operative gate is the login. The classifier's own W7-001 note
  flags exactly this shape as the known unobserved case ("a small
  login page carrying Turnstile for its own form would read
  CHALLENGED via this code path — if a live capture ever shows
  that shape, fix it then, generalized"). This fixture IS that
  shape, generalized: the fix must be loader-signal-only (a
  challenge-platform loader with no fired-wall signal) yielding to
  an identified login page. It must NOT change: the Wave 7
  careerjet case (Turnstile loader on a check-only, non-login
  page → CHALLENGED) or Wave 6 S5a ("Just a moment" at a login
  URL → CHALLENGED, a fired wall, not a loader).
- **C2d** — 403, final URL https://site.example/login, a login form
  + a px-captcha div. → **CHALLENGED / PerimeterX**. Pin (Wave 6
  S5d species): a vendor wall code keeps precedence over the
  login yield — the wall fired before any form could be reached.

## C3 — SVG / image-only challenge pages

- **C3a** — 403, small page, only an `<img>` captcha with
  alt="captcha image". → **CHALLENGED / Generic**. The word in the
  alt text is the challenge signal. Pin.
- **C3b** — 403, small page, only an `<svg>` graphic with NO text,
  no alt, no title, no tokens. → **WALLED, vendor none**.
  Honest-limitation pin: a picture with no text carries no
  verdict-driving signal — it cannot be told apart from any
  image-only refusal. The 403 status owns the verdict (a refusal
  with no challenge evidence is WALLED, not CHALLENGED); claiming
  a challenge from pixels we cannot read would be guessing.
- **C3c** — 200, small page, only an SVG whose `<text>` element
  reads "Verify you are human". → **CHALLENGED / Generic**. Pin:
  the raw-body scan reads text wherever it sits, including inside
  SVG markup.

## C4 — multi-language mixed pages

Challenge pages are not English-only, and the Wave 6 list (ES/DE/FR/
JA/PT) is not the whole world. Each of these presents an interactive
human check in one language only; all hand-classify **CHALLENGED /
Generic** (the page offers the check, it does not refuse outright).

- **C4a** — 403, small page, challenge text in English AND Spanish
  mixed ("Verify you are human / Verifica que eres humano"). →
  **CHALLENGED / Generic**. Pin (both languages already listed).
- **C4b** — 403, small page, Italian only: "Verifica di essere
  umano. Non sono un robot." → **CHALLENGED / Generic**.
  Predicted gap: Italian is not in the localized list.
- **C4c** — 403, small page, Dutch only: "Bevestig dat u geen robot
  bent. Ik ben geen robot." → **CHALLENGED / Generic**. Predicted
  gap: Dutch is not in the localized list.
- **C4d** — 403, small page, Korean only: "로봇이 아님을 확인하세요."
  ("Please confirm you are not a robot.") → **CHALLENGED /
  Generic**. Predicted gap: Korean is not in the localized list.

## C5 — WAF pages carrying only a status code + one header

- **C5a** — 403, empty body, headers cf-ray + Server: cloudflare
  only. → **WALLED / Cloudflare**. Pin (bare-403-behind-CDN: the
  status owns the verdict, the CDN header owns the attribution).
- **C5b** — 403, empty body, header x-sucuri-id only (Sucuri, a
  vendor the classifier does not know). → **WALLED, vendor none**.
  Pin: an unknown vendor's header is not claimed — the verdict
  (refusal, no challenge evidence) is correct without attribution.
  Sucuri is noted as a future vendor candidate IF a live capture
  ever shows its wall page; a synthetic header alone does not earn
  a vendor rule.
- **C5c** — 429, empty body, Retry-After header only. →
  **RATE_LIMITED**. Pin (the 429 branch needs no body signal).
- **C5d** — 503, empty body, cf-ray header only. → **UNREACHABLE,
  vendor none**. Pin (Wave 10 W10-006: a 5xx claims no wall even
  when it wears vendor branding).

## C6 — login pages with an embedded captcha widget

- **C6a** — 200, final URL https://site.example/login, a password
  form embedding a reCAPTCHA loader, no prose. → **LOGIN_GATED**.
  Pin (Wave 5 W5-001: a loader reference on a login form is
  presence — and the loader-blanking regex already handles it).
- **C6b** — 200, final URL https://site.example/login, a password
  form embedding an hCaptcha widget + "verify you are human" prose
  in the sign-in copy. → **LOGIN_GATED**. Pin (Wave 6 S5c: the
  generic branch yields to an identified login page).

## C7 — sitemap INDEX files (audit tool, not classifier)

- **C7a** — /sitemap.xml is a `<sitemapindex>` document listing
  child sitemaps. → **PASS**. Pin: a sitemap index IS a sitemap —
  the check already accepts `<sitemapindex` (verify, do not
  assume).
- **C7b** — /sitemap.xml is a `<sitemapindex>` whose child URLs
  404. → **PASS**. Scope pin: the check grades the file served,
  not the tree — fetching every child would break the audit's
  stated ≤10-fetch budget, and a dead child is an owner content
  bug, not an agent-access failure of the index itself.
- **C7c** — /sitemap.xml 301-redirects to /sitemap_index.xml, a
  valid `<urlset>`. → **PASS**. Pin: redirect resolution is the
  fetcher's job; the evaluated record is the final document.

## C8 — robots.txt subtleties (audit tool, not classifier)

- **C8a** — robots.txt with only `Crawl-delay: 10` for `*` (no
  Disallow). → **PASS**. Pin: crawl-delay is a politeness
  directive, not a block — the parser already ignores it.
- **C8b** — robots.txt: `User-agent: *` Disallow: `/`, PLUS a
  named group `User-agent: GPTBot` Allow: `/`. → **WARN**
  (GPTBot open; ClaudeBot, CCBot, Google-Extended blocked).
  Predicted gap: the check's `wildcard_all` short-circuit returns
  FAIL whenever a wildcard Disallow: / exists, even when a
  tracked agent is explicitly carved out — but the file does NOT
  block everything (GPTBot is allowed). FAIL must mean "every
  tracked agent blocked", not "a wildcard rule exists".
- **C8c** — robots.txt: `User-agent: *` Disallow: `/`, PLUS
  `User-agent: ClaudeBot` Disallow: `/private` only. → **WARN**
  (ClaudeBot restricted; the other three blocked). Same predicted
  gap as C8b: ClaudeBot is not blocked outright, so FAIL overstates
  the posture.
- **C8d** — robots.txt with `Crawl-delay: 10` + a `Sitemap:`
  declaration, no Disallow. → **PASS** with SITEMAP_DECLARED
  evidence. Pin.
- **C8e** — robots.txt: `user-agent: gptbot` (lowercase)
  Disallow: `/private`, no wildcard group. → **WARN** (GPTBot
  restricted; others open). Pin: agent matching is
  case-insensitive.
- **C8f** — robots.txt: `User-agent: *` with an empty `Disallow:`
  value. → **PASS**. Pin: an empty Disallow permits everything.
- **C8g** — robots.txt: named group FIRST (`User-agent: GPTBot`
  Disallow: `/private`), wildcard group AFTER (`User-agent: *`
  Disallow: `/`). → **WARN** (GPTBot restricted; others blocked).
  Pin: the named group wins regardless of group order — and this
  also exercises the C8b/C8c fix from the other order.
