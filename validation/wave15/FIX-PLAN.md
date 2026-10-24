# Wave 15 — Fix plan (written BEFORE application; fixes land only after round 11 finishes)

Battery v7 baseline (pre-fix tree = Wave 14-fixed tree): 39 shapes,
13 mismatches, all predicted, 26 pins held. Each fix below is
generalized (a rule, not a shape) with guard fixtures named. No fix
is applied until the round-11 runner exits, so Leg A measures the
pure Wave 14 tree.

- **W15-001 (G1c) JSON-LD vendor suppression.** Vendor markers inside
  `<script type="application/ld+json">` blocks are metadata, not fired
  walls: strip ld+json blocks from the vendor-scan body when the page
  has visible text (same visible-text condition as W14-001). Content-
  free pages still fire (G1d). Regular scripts (loaders) untouched —
  the strip regex matches ld+json type only. Guards: loader script
  with a vendor marker + visible text still fires; G1a/G1b/G1d pins.
- **W15-002 (G2a) Refusal-phrase rule.** Small-page (<4 KB, like
  GEO_REFUSAL) "access denied" wording reads WALLED, verdict-only, no
  vendor. Branch placed after the 401 branch (G2c keeps LOGIN_GATED)
  and before the login heuristic, guarded to status < 500 (G2e keeps
  UNREACHABLE). Guards: G2b/G2c/G2d/G2e.
- **W15-003 (G3b) Visible-text phrase scan.** Generic human-check
  phrases are also matched against tag-stripped visible text, so a
  phrase split across SVG tspans (or any elements) fires. Served-
  page gate still applies (G3c). Guards: split non-challenge text
  does not fire; contiguous SVG text (G3a) unchanged.
- **W15-004 (G4c) Invisible-widget suppression.** A "captcha" token
  appearing ONLY in an invisible-captcha widget tag
  (data-size="invisible") is form-submission machinery, not a
  presented challenge: it does not verdict-drive when the page has
  visible text. Content-free pages still fire (G4d); visible widgets
  and prose still fire. Implemented as an additional conjunct in the
  GENERIC_CAPTCHA branch (token must survive invisible-tag
  stripping when visible text exists).
- **W15-005 (G5a/G5b) Refresh-header redirect targets.** The HTTP
  `Refresh` header's url is parsed as a redirect target with the
  same login/challenge/content semantics as meta refresh. Gated by
  markers_count (G5d: served articles untouched). Guards: G5c/G5d.
- **W15-006 (G6c) Code-entry form login signal.** A served 2xx page
  whose form carries a code input (otp/2fa/auth-code/verification-
  code/security-code/one-time-code, or exactly "code") AND auth
  wording (verification/one-time/authentication/security code,
  6-digit) reads LOGIN_GATED. Narrower than general form-text
  detection: a "sign in" link alone does not fire, and discount-
  code forms match neither key. Branch placed immediately before
  the login heuristic; wall signals keep precedence. Narrows (does
  not close) the Wave 14 F5 limitation — see LIMITATIONS-REVISIT.md.
- **W15-007 (G7b) Footer-badge suppression on served pages.** On 2xx
  responses, "protected by X" / "powered by X" badge phrases are
  blanked before vendor-marker scans: a badge on served content is
  furniture, not a fired wall. Error statuses keep full attribution
  (a 403 deny page's badge still attributes). Guards: G7a/G7c and
  a 403 badge page keeping its vendor.
- **W15-008 (G8d) Robots Allow-tiebreak (RFC 9309).** In
  `_agent_state`, an Allow: / in the applicable group cancels a
  Disallow: / (tie resolves to Allow); a non-root Allow alongside a
  Disallow: / softens blocked to restricted (partial access, the
  C8b carve-out principle generalized). Existing C8/D6/E5 pins must
  still pass via the full suite.
- **W15-009 (G9b/G9d) llms frontmatter stripping.** A leading YAML
  frontmatter block (--- ... ---) is stripped before llms content
  analysis: metadata URLs/links are not index entries. G9a/G9c
  (frontmatter + real content) still PASS; frontmatter-only files
  fall through to the existing length/stub gates (WARN).
- **W15-010 (G10a/G10c) Sitemap must name a URL.** A sitemap
  document (urlset/sitemapindex, or bare <?xml prolog) with zero
  <loc> entries reads WARN (SITEMAP_NO_URLS), not PASS. One <loc>
  suffices (G10d). Blast radius, documented: a bare <?xml prolog
  with no sitemap content, previously PASS via the prolog rule,
  now reads WARN — a prolog alone is not a sitemap.

Corpus regression: corpus-baseline.txt (44 captures, pre-fix tree)
must diff clean against the post-fix run, or every change explained.
