# Wave 12 — Adversarial Battery v4: Hand Classifications

Discipline (as Waves 6, 10, 11): every shape below was classified BY HAND
against SPEC's verdict definitions BEFORE the classifier was allowed to
see it. All shapes are NEW relative to Wave 6 (S1–S6), Wave 10 (B1–B10),
and Wave 11 (C1–C8): no repeats of soft-404 variants, redirect-chain
walls in meta-refresh/JS-location form (but see D9, which tests CHAIN
LENGTH and chain-vs-final-answer precedence, not the redirect species),
202 JS-proof stubs with vendor tokens, multi-vendor stacks, login
hybrids in widget form (but see D5, which tests the FORM-ACTION rule
against the login yield — a rule interaction, not a repeat), geo-blocks,
meta-refresh walls, consent boundaries in banner form (but see D4,
which tests the consent gate EXPLICITLY blocking content), Cloudflare
error variants, app interstitials, DataDome variants, or audit soft-404
variants. Any mismatch is a defect candidate: fix generalized with a
capture-built fixture, or ledger it as a genuine honest limitation
with the reason. No silent passes, no per-shape special cases.

Reference — SPEC verdicts: OPEN = the resource was served; CHALLENGED =
an interactive human-verification challenge was presented; WALLED = a
hard block page, no challenge offered; LOGIN_GATED = content exists
behind authentication; RATE_LIMITED = plain 429 throttle; UNREACHABLE =
the fetch itself failed. Audit grades: PASS / WARN / FAIL per check.

## D1 — challenge pages in additional languages

The Wave 6 list (ES/DE/FR/JA/PT) plus Wave 11 (IT/NL/KO) is still not
the whole world. Each presents an interactive human check in one
language only; all hand-classify **CHALLENGED / Generic** (the page
offers the check, it does not refuse outright). All are 403 small
pages with no vendor tokens.

- **D1a (PL)** — Polish only: "Potwierdź, że nie jesteś robotem.
  Zaznacz pole «Nie jestem robotem»." → **CHALLENGED / Generic**.
  Predicted gap: Polish is not in the localized list.
- **D1b (TR)** — Turkish only: "Robot olmadığınızı doğrulayın.
  «Robot değilim» kutusunu işaretleyin." → **CHALLENGED / Generic**.
  Predicted gap: Turkish is not in the localized list.
- **D1c (AR)** — Arabic only: "أكد أنك لست روبوتًا. ضع علامة على
  «أنا لست روبوتًا»." → **CHALLENGED / Generic**. Predicted gap:
  Arabic is not in the localized list.
- **D1d (ZH)** — Chinese only: "请确认您不是机器人。请勾选
  «我不是机器人»。" → **CHALLENGED / Generic**. Predicted gap:
  Chinese is not in the localized list.
- **D1e (RU)** — Russian only: "Подтвердите, что вы не робот.
  Отметьте «Я не робот»." → **CHALLENGED / Generic**. Predicted
  gap: Russian is not in the localized list.

## D2 — countdown / timer interstitial pages

- **D2a** — 200, small page, "Please wait 5 seconds…" + a countdown
  script + a meta refresh to /content/page (the site's real content
  page). → **OPEN**. Pin (Wave 10 B4d species): a redirect to
  content is routing, not a wall — a timer does not turn routing
  into a challenge, and no verification wording appears.
- **D2b** — 200, small page, "Please wait 10 seconds while we
  verify your connection" + a countdown + an auto-submitting form
  whose action is /challenge/verify. → **CHALLENGED / Generic**.
  Pin: the form-action rule (Wave 11 W11-001) owns this even though
  "verify your connection" is not itself a JS_PROOF phrase — the
  page's only content routes the client to a challenge.
- **D2c** — 200, small page, "Please wait 5 seconds" + a countdown +
  a meta refresh to /challenge/verify-human, no verification wording
  anywhere. → **CHALLENGED / Generic**. Pin (Wave 10 B4a species):
  the redirect target names the challenge even when the page's own
  words do not.

## D3 — "browser check" wording with no vendor tokens

- **D3a** — 200, small page, only content "Browser check in
  progress…" + a spinner + an auto-reload script. No vendor tokens,
  no "verify"/"human"/"robot" words anywhere. → **CHALLENGED /
  Generic**. The Wave 6 S3a species in new wording: the page's only
  content is a browser-verification proof the agent cannot perform.
  Predicted gap: "browser check" is not in the JS_PROOF phrase list
  ("checking your browser" and "verifying your browser" are, but
  neither is a substring of this page's text).
- **D3b** — 200, 20 KB real article page that mentions "browser
  check" once in its text (an article about bot detection). →
  **OPEN**. Pin: the served-page gate protects content *about*
  checks from tripping the new phrase — the fix for D3a must stay
  gated to small pages.

## D4 — consent gates that ALSO block content (hybrid)

- **D4a** — 200, small page, only content a cookie-consent gate
  ("Accept cookies to continue" + accept button) PLUS explicit
  content-block wording ("This content is blocked until you accept
  cookies"). No bot-check wording. → **OPEN**. Pin (Wave 10 B5b
  reaffirmed under pressure): a consent gate is a legal gate, not a
  bot wall — even when it says out loud that it blocks content.
  The tool's scope is bot walls; calling this CHALLENGED would
  mislabel every GDPR gate as a wall.
- **D4b** — same page as D4a, plus "verify you are human" prose in
  the gate copy. → **CHALLENGED / Generic**. Pin (Wave 10 B5c
  species): the human-check prose, not the consent UI, is the wall
  signal.

## D5 — login forms whose action IS a challenge endpoint

This pair tests the Wave 11 form-action rule against the login yield
— a rule interaction no earlier battery exercised.

- **D5a** — 200, final URL https://site.example/login, a password
  form carrying an hCaptcha widget, whose form action is
  /challenge/verify-human (the sign-in submits through a challenge
  endpoint). → **LOGIN_GATED**. The page IS the login: the form is
  the sign-in form, and its action is the form's own submission
  endpoint — part of the auth experience, not a routing stub whose
  whole content points elsewhere (the Wave 11 W11-001 species was a
  stub page with no login). The Wave 6 S5c principle (human-check
  elements on an identified login page are auth, not wall) must
  extend to the form-action rule. Predicted gap: the
  REDIRECT_TO_CHALLENGE branch does not yield to identified login
  pages the way the generic-marker branch does, so the classifier
  will read this CHALLENGED.
- **D5b** — 200, non-login URL, small page, only content a
  "continue" form whose action is /challenge/verify (no password
  field, no login URL). → **CHALLENGED / Generic**. Pin (Wave 11
  W11-001 species): a stub whose only content routes to a
  challenge is a challenge by reference — and this pin guards the
  D5a fix from over-correcting into "form actions never count".

## D6 — robots.txt per-agent carve-outs (audit tool)

Post-Wave-11 semantics (W11-006): FAIL means EVERY tracked agent is
blocked; any carve-out or restriction-only posture drops to WARN.

- **D6a** — robots.txt: `User-agent: *` Disallow: `/`, PLUS named
  groups `User-agent: GPTBot` Allow: `/` and `User-agent: ClaudeBot`
  Allow: `/`. → **WARN** (GPTBot and ClaudeBot open; CCBot and
  Google-Extended blocked). Pin of the W11-006 fix with two
  carve-outs.
- **D6b** — robots.txt: `User-agent: *` Disallow: `/`, PLUS all four
  tracked agents each Disallow: `/private` only. → **WARN** (all
  four restricted, none blocked outright). Pin.
- **D6c** — robots.txt: `User-agent: *` Disallow: `/`, PLUS
  `User-agent: GPTBot` Disallow: `/` explicitly. → **FAIL** (every
  tracked agent blocked — three by the wildcard, GPTBot by its own
  group too). Pin: an explicit named block does not soften FAIL.

## D7 — llms.txt format variants (audit tool)

- **D7a** — /llms.txt served as Content-Type text/markdown, body is
  a genuine markdown index (# Title, section links). → **PASS**.
  Pin: llms.txt IS defined as markdown — the format's own canonical
  form must pass, whatever the content-type label.
- **D7b** — /llms.txt served as Content-Type text/plain, body is
  plain-text index lines. → **PASS**. Control pin.
- **D7c** — /llms.txt served as Content-Type application/ld+json,
  body is a JSON-LD structured-data document (schema.org, no error
  key). → **WARN**. A JSON-LD document is machine-readable data,
  but it is not an llms.txt: the file at the llms.txt location is
  in the wrong format, so claiming PASS ("served as genuine text")
  overstates it — and FAIL would overstate the other way, since
  it is neither an error document nor a deception. Predicted gap
  (policy refinement, not a crash): the check's JSON gate only
  fails error documents, so a non-error JSON body passes today.
- **D7d** — /llms.txt served as Content-Type text/html, body is a
  genuine markdown index (no HTML tags anywhere — a server
  mislabeling its content-type). → **PASS**. The body IS the
  index; agents ingest the body, not the header. Predicted gap:
  the HTML gate trusts the content-type header over the body, so
  a mislabeled markdown file fails today.

## D8 — compressed sitemaps (audit tool, live local server)

A sitemap served gzip-compressed is still a sitemap; an HTTP client
that cannot decompress it misgrades the site. Both shapes run
against a real localhost server (no synthetic records).

- **D8a** — /sitemap.xml returns 200 with a gzip-compressed
  `<urlset>` body and Content-Encoding: gzip. → **PASS**. Predicted
  gap: the audit fetcher does not decompress gzip bodies, so the
  XML check sees binary garbage and answers WARN.
- **D8b** — /sitemap.xml returns 404, robots.txt declares
  `Sitemap: /sitemap.xml.gz`, and /sitemap.xml.gz returns 200 with a
  gzip-compressed `<urlset>` body. → **PASS**. Same predicted gap
  via the robots-declaration fallback path (the declaration is
  followed, but the body still needs decompression).

## D9 — multi-redirect chains ending at a wall (3+ hops)

Chain length must not change the rule: the final answer owns the
verdict, and a challenge URL in the chain must not outrank a served
final page (Wave 6 S2b, extended to 3+ hops and to login finals).

- **D9a** — chain [site → /a → /b → /c/challenge], final 403
  "Just a moment" page with cf-ray. → **CHALLENGED / Cloudflare**.
  Pin: the final answer is a fired wall; the chain is decoration.
- **D9b** — chain [site → /challenge → /login], final 200 login
  page, no wall signals. → **LOGIN_GATED**. Pin: a challenge URL
  in the chain must not outrank the served login final.
- **D9c** — chain [site → /a → /b → /home], final 200 full
  homepage. → **OPEN**. Pin: routing hops to content are routing.
- **D9d** — chain [site → /challenge → /x], final 200 full
  article page. → **OPEN**. Pin: the Wave 6 S2b rule at 3 hops —
  a challenge URL in the chain never outranks a served final page.
