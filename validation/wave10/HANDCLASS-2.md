# Wave 10 — Adversarial Battery v2: Hand Classifications

Discipline (as Wave 6): every shape below was classified BY HAND against
SPEC's verdict definitions BEFORE the classifier was allowed to see it.
Shapes are all NEW relative to Wave 6's battery (no repeats of S1–S6):
mixed/contradictory vendor signals, 401/403 login hybrids, geo-blocks,
meta-refresh/JS-redirect walls, consent-vs-wall boundaries, Cloudflare
error-page variants, PerimeterX app interstitials, DataDome header-only
shapes, and audit soft-404 variants. Any mismatch is a defect
candidate: fix generalized with a capture-built fixture, or ledger it
as a genuine honest limitation with the reason. No silent passes, no
per-shape special cases.

Reference — SPEC verdicts: OPEN = the resource was served; CHALLENGED =
an interactive human-verification challenge was presented; WALLED = a
hard block page, no challenge offered; LOGIN_GATED = content exists
behind authentication; RATE_LIMITED = plain 429 throttle; UNREACHABLE =
the fetch itself failed. Audit grades: PASS / WARN / FAIL per check.

## B1 — mixed / contradictory vendor signals

- **B1a** — 403, cf-ray + Server: cloudflare headers (CDN presence)
  + x-datadome header + DataDome body marker. → **CHALLENGED /
  DataDome**. The wall that fired outranks the CDN that fronted (the
  Wave 6 economist.com principle, generalized): Cloudflare contributed
  presence only; DataDome contributed a wall signal.
- **B1c** — 403, Akamai edgesuite error page + Kasada kpsdk stub in
  the body. → **WALLED / Akamai**. Two wall signals fired; detection
  order (Akamai before Kasada in the wall-signal precedence list)
  names the first. The page refuses outright: WALLED, not CHALLENGED.
- **B1d** — 403, Imperva "incapsula" body marker (no incident line)
  + x-datadome header. → **CHALLENGED / DataDome**. DataDome precedes
  Imperva in detection order and its branch names a challenge; the
  Imperva marker alone on 403 would read WALLED, but the ordered
  precedence rule decides between two fired walls.
- **B1e** — 200, 30 KB served article page with cf-ray header and a
  prose mention of "perimeterx" (an article about bot walls). →
  **OPEN, vendor none**. Served-page gate: mentions on a full page are
  presence, not a wall; a served page has no wall vendor.

## B2 — 401 / 403 login hybrids

- **B2a** — 401, final URL https://site.example/login, body
  "Unauthorized — please sign in". → **LOGIN_GATED**. 401 is an auth
  demand, not a wall.
- **B2b** — 403, final URL https://site.example/login, body is a
  plain login form (no wall signals). → **WALLED**. Per the Wave 8
  rule, a gate must be a served page (2xx/3xx): a 403 at a login URL
  is a refusal, not a gate (the delta 444 precedent, generalized to
  403).
- **B2c** — 401, JSON body {"error": "invalid_token"} at
  https://api.example/data (not a login URL). → **LOGIN_GATED**.
  401 names an auth failure wherever it appears.
- **B2d** — 403, JSON body {"error": "forbidden"} at
  https://api.example/data. → **WALLED**. Bare 403, no wall vendor.

## B3 — geo-blocks and legal refusals

- **B3a** — 403, body "This content is not available in your
  region". → **WALLED**. A refusal with no challenge offered; the
  status already owns it.
- **B3b** — 200, small (2 KB) page whose entire content is "This
  service is not available in your country" + a support link. →
  **WALLED**. OPEN claims the resource was served; it was not — a
  refusal page was served instead, with no challenge and no content.
  This is the 200-status species of B3a, and the classifier's
  served-page logic (200 ⇒ OPEN) is the predicted gap: the fix, if
  made, must be gated to small pages carrying geo-refusal phrasing,
  so articles *about* geo-blocking stay OPEN.
- **B3c** — 451, body "Unavailable for legal reasons". → **WALLED**.
  451 is a deliberate refusal code (RFC 7725), not a served page and
  not a server failure. The classifier's fall-through (451 ⇒ OPEN)
  is the predicted gap; the generalized fix is 451 ⇒ WALLED,
  parallel to the 444 rule.

## B4 — meta-refresh and JS-redirect walls

- **B4a** — 200, small page, only content a meta refresh to
  /challenge/. → **CHALLENGED / Generic**. By the Wave 6 S2c
  precedent (a page whose whole content routes the client to a
  captcha is a challenge by reference), a page whose whole content
  routes the client to a challenge is a challenge by reference.
- **B4b** — 200, small page, only content a meta refresh to
  /login. → **LOGIN_GATED**. The page's entire content is a
  directive to authenticate; the gate is login, not a wall.
- **B4c** — 200, small page, only content a JS redirect
  (`window.location.href = "/challenge/verify-human"`). →
  **CHALLENGED / Generic**. Same reference principle as B4a, in JS
  form: the redirect target names the verification challenge.
- **B4d** — 200, small page, meta refresh to /home (the site's real
  content page). → **OPEN**. A redirect to content is a routing
  mechanism, not a wall; the boundary against B4a/B4b is the
  target: content targets stay OPEN, challenge/login targets do not.

## B5 — cookie-consent walls vs real walls

- **B5a** — 200, 30 KB served page with a cookie-consent banner
  ("We use cookies… Accept all"). → **OPEN**. Consent UI on served
  content is not a wall.
- **B5b** — 200, small (2 KB) page whose only content is a cookie
  consent gate ("Please accept cookies to continue" + accept
  button; content hidden until consent). → **OPEN**. Pinned
  boundary, deliberately: a consent gate is a legal gate, not a
  bot wall — the tool's scope is bot walls, and calling consent
  CHALLENGED would mislabel every GDPR banner as a wall. (If a
  future live capture shows a consent gate that is itself
  bot-gated, that capture — not this fixture — reopens it.)
- **B5c** — 200, small page, cookie banner + "verify you are human"
  prose. → **CHALLENGED / Generic**. The human-check prose, not the
  consent UI, is the wall signal.

## B6 — Cloudflare error-page variants

- **B6a** — 403, Cloudflare "Attention Required!" page (cf-ray,
  no "Just a moment", no "Sorry, you have been blocked"). →
  **WALLED / Cloudflare**. A hard block with no challenge offered;
  the vendor is named by its own headers.
- **B6b** — 403, Cloudflare "Error 1000: DNS points to a prohibited
  IP" page. → **WALLED / Cloudflare**. A configuration refusal
  served by the wall vendor: the fetch succeeded and returned a
  refusal, so neither OPEN nor UNREACHABLE fits.
- **B6c** — 503, Cloudflare "Error 522: Connection timed out"
  page. → **UNREACHABLE**. SPEC's 5xx rule: the origin failed, so
  no wall verdict is claimed even though the error page wears
  Cloudflare's branding.

## B7 — PerimeterX mobile-app interstitials

- **B7a** — 403, px-captcha div + "Please open this page in the
  app" text. → **CHALLENGED / PerimeterX**. The captcha container
  is the wall signal; the app wording is decoration.
- **B7b** — 403, "Download our app to continue" with no vendor
  markers, small page. → **WALLED, vendor none**. An app-only gate
  offers no challenge and no content: a hard block with no
  attribution. The bare-403 rule already owns it.

## B8 — DataDome variants

- **B8a** — 403, DataDome page with captcha-delivery.com script
  reference, no visible widget. → **CHALLENGED / DataDome**. The
  delivery host is the wall signal (Wave 1, W1-008).
- **B8b** — 403, x-datadome header only, body is plain "Forbidden".
  → **CHALLENGED / DataDome**. The vendor's own header is the
  wall signal; the body need not repeat it.
- **B8c** — 200, full served page with a dd_cookie (DataDome
  sensor cookie) in Set-Cookie. → **OPEN, vendor none**. A sensor
  cookie on served content is presence; an OPEN page has no wall
  vendor.

## B10 — three-vendor contradiction

- **B10a** — 403, cf-mitigated: challenge + DataDome body marker +
  px-captcha div. → **CHALLENGED / Cloudflare**. Cloudflare's own
  wall signal fired, so Cloudflare keeps attribution over the
  other two fired walls (the Wave 6 S4b principle, generalized to
  three vendors).

## B9 — audit soft-404 variants (audit tool, not classifier)

- **B9a** — /llms.txt returns 200, Content-Type text/plain, body
  `{"error": "not found"}`. → **FAIL**. The file's content is an
  error document, not an index: worse than absent, because an agent
  ingests it as if it were the real index. Predicted gap: the llms
  check's HTML gate does not catch JSON error documents; the
  generalized fix is an error-document gate (a body that parses
  as JSON carrying an error key), not format policing of llms.txt.
- **B9b** — /llms.txt 301-redirects to the homepage HTML. →
  **FAIL**. The redirect resolves to HTML, which the existing
  HTML gate already catches (pin, not a gap).
- **B9c** — /robots.txt returns 200 with an empty body. → **PASS**.
  An empty robots file is valid and permits everything; empty is
  not missing. (Boundary pin against B9d.)
- **B9d** — /robots.txt returns 200, Content-Type text/plain, body
  is an HTML error page. → **FAIL**. Same species as the llms
  HTML soft-404, but the robots check has no HTML gate — the
  predicted gap. Generalized fix: mirror the llms HTML gate into
  the robots check (SOFT_404_HTML).
- **B9e** — /sitemap.xml returns 200 with an HTML error page body.
  → **WARN**. The sitemap check already answers non-XML 200s with
  WARN (pin, not a gap).
