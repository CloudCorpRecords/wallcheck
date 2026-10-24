# Wave 15 — Problems ledger

## Leg B (adversarial battery v7) — 13 defects, all fixed

- **W15-001** (classifier, fixed): vendor markers inside JSON-LD
  blocks drove verdicts (G1c: a vendor name in JSON-LD metadata
  on a page with visible text read CHALLENGED / PerimeterX).
  Fix: ld+json blocks are stripped from the vendor scan when the
  page has visible text (same visible-text condition as W14-001);
  content-free pages still fire (G1d); regular scripts untouched
  (guard: loader script + vendor marker + visible text still
  fires). Fixtures: test_g1c, test_g1d, guard pin.
- **W15-002** (classifier, fixed): a 200-status refusal stub read
  OPEN (G2a: small page, only content "Access denied."). Fix:
  REFUSAL_PHRASE — small-page (<4 KB, like GEO_REFUSAL) "access
  denied" reads WALLED, verdict-only; branch after 401 (G2c
  keeps LOGIN_GATED), guarded to sub-500 (G2e keeps
  UNREACHABLE). Fixtures: test_g2a–e, login-URL refusal guard.
- **W15-003** (classifier, fixed): a human-check phrase split
  across SVG tspans read WALLED (G3b: rendered "Verify you are
  human", markup-split). Fix: generic human-check and JS_PROOF
  phrases are also matched against tag-stripped visible text,
  in both halves of the human-check condition (the first fix
  attempt added it to only the second half and G3b still failed
  — the battery re-run caught it). Served-page gate still
  applies (G3c). Fixtures: test_g3b/g3c, split-non-challenge
  guard, JS_PROOF-split guard.
- **W15-004** (classifier, fixed): an invisible hCaptcha widget
  on a content page read CHALLENGED (G4c: widget class token
  "h-captcha" fired GENERIC_CAPTCHA despite visible text). Fix:
  a "captcha" token appearing ONLY in an invisible-widget tag
  must also survive invisible-tag stripping to fire when visible
  text exists. Content-free pages still fire (G4d); visible
  widgets and prose still fire (guards). Fixture: test_g4c/g4d.
- **W15-005** (classifier, fixed): Refresh-header routing read
  OPEN (G5a: header `Refresh: 0; url=/challenge/verify`;
  G5b: to /login). Fix: the header's url is parsed as a
  redirect target with meta-refresh semantics, served-page-
  gated (G5d). Fixtures: test_g5a–d, delay-only guard.
- **W15-006** (classifier, fixed): a 2FA code-entry form at a
  non-login URL read OPEN (G6c: /verify-2fa, otp input +
  "6-digit verification code"). Fix: CODE_ENTRY_FORM — a served
  2xx page with a code input AND auth wording reads LOGIN_GATED,
  placed immediately before the login heuristic; wall signals
  keep precedence. Discount-code and wording-less guards prove
  both keys are required. Fixtures: test_g6c, both guards.
- **W15-007** (classifier, fixed): a footer badge on a small
  served page read CHALLENGED (G7b: 2 KB article + "protected by
  PerimeterX"). Fix: badge phrases ("protected by X" / "powered
  by X", at most three words) are blanked from marker scans on
  2xx pages only; error pages keep full attribution (guard:
  403 badge page keeps PerimeterX). Fixtures: test_g7b, guard.
- **W15-008** (audit tool, fixed): a robots tie (Disallow: / +
  Allow: /) read FAIL (G8d). Fix: RFC 9309 tiebreak in
  `_agent_state` — Allow: / cancels Disallow: /; a non-root
  Allow alongside Disallow: / softens blocked to restricted
  (partial access). Existing C8/D6/E5 pins still pass via the
  suite. Fixtures: test_g8d, partial-allow guard.
- **W15-009** (audit tool, fixed): YAML frontmatter counted as
  index content (G9b: frontmatter-only file with a `url:` field
  read PASS; G9d: frontmatter link read PASS). Fix: a leading
  --- ... --- block is stripped before llms content analysis.
  Refinement found during the fix (G9c): stripping can push a
  real one-link index under the 20-char length gate, so the
  length gate no longer fires on bodies carrying a link, URL, or
  path ("effectively empty" means no usable content). Fixtures:
  test_g9b–d, unclosed-frontmatter guard.
- **W15-010** (audit tool, fixed): lastmod-only sitemaps read
  PASS (G10a: urlset with no <loc>; G10c: sitemapindex with no
  <loc>). Fix: a sitemap document with zero <loc> entries reads
  WARN (SITEMAP_NO_URLS); one <loc> suffices (G10d). Blast
  radius, pinned: a bare <?xml prolog with no sitemap content,
  previously PASS via the prolog rule, now reads WARN.
  Fixtures: test_g10a/c/d, prolog guard.

## Leg B — corpus regression (done)

44 stored captures replayed through the Wave 15-fixed classifier
(`validation/wave15/corpus_check.py`, `corpus-after.txt` vs the
pre-fix `corpus-baseline.txt`). Zero regressions: diff is empty.
Every real wall capture reads as its wave established — the
W15-002 refusal rule moves nothing (w3schools' 371-byte
"Access Denied" edgesuite page and delta's 444 deny were already
WALLED; the rule's verdict matches the branches that already
owned them), the W15-001 ld+json strip moves nothing (the four
LDJSON captures are 65 KB served pages or a 404, all gated out
by size or status), and the visible-text phrase scan moves
nothing (no real capture's wall signal lives only in split
markup). One artifact, not a regression (as in Waves 13–14):
`validation/wave7/captures/careerjet.json` reads OPEN because
the JSON record carries an empty body (the real 10,937-byte
HTML lives in `careerjet.html`, which classifies CHALLENGED /
Cloudflare exactly as Wave 7 established).

## Leg A (round-11 reclassification) — see STABILITY-10.md

499/499 probed with the Wave 14-fixed classifier (clean launch,
no sed-trap incident — the runner was written fresh with a
single ROUND constant and output growth verified before
walking away). Three diffs, all hand-checked with fresh
captures: forbes.com HELD at OPEN (round-11 DataDome challenge
overturned by two fresh served readings; a later spot-check
read CHALLENGED again — forbes is now a documented intermittent
oscillator on a 2–2 split); britishairways.com MERGED to
UNREACHABLE (round-11 plus two agreeing fresh fetch failures —
the mirror of the Wave 14 hold); webex.com HELD at WALLED /
Akamai (round-11 served reading overturned by two fresh
edgesuite denies). Zero fix-driven moves — the fifth
consecutive round. The thirteen battery defects above already
disqualify Wave 15 as a clean wave regardless of Leg A's clean
sheet — the saturation clock stays reset (see OVERNIGHT.md).

## Leg C (limitations revisit) — see LIMITATIONS-REVISIT.md

Ten documented limitations re-tested against the last six
waves' fixtures: one narrowed (the F5 form-signal limitation
gains the code-entry species via W15-006), one resolved by
construction (hop bodies), eight still open with re-test dates
— including the Wave 3 silent-JS-proof boundary, which survives
because a wording-free, token-free proof page still carries no
deterministic signal.
