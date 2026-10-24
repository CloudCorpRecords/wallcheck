# Wave 15 — Adversarial Battery v7: Results

**39 shapes, 13 mismatches before fixes, 0 after.** All 13
mismatches were predicted in HANDCLASS-7.md (zero surprises);
all fixed test-first and generalized; 26 pins held. Full suite
after fixes: **321/321** (270 prior + 51 new: 39 battery pins +
12 guards). Real-capture corpus: replayed after the fixes (see
PROBLEMS.md) — no verdict/vendor change on any real wall capture.

## Mismatches → fixes (13 defects, 10 fix families)

| shape | pre-fix | hand | fix |
| --- | --- | --- | --- |
| G1c (JSON-LD vendor marker + visible text) | CHALLENGED / PerimeterX | OPEN | W15-001: vendor markers inside `<script type="application/ld+json">` blocks are metadata, not fired walls — stripped from the vendor scan when the page has visible text (same visible-text condition as W14-001). Content-free pages still fire (G1d); regular scripts (loaders) untouched (guard pin). |
| G2a (200 "Access denied" stub) | OPEN | WALLED | W15-002: REFUSAL_PHRASE — a small-page (<4 KB, like GEO_REFUSAL) "access denied" stub reads WALLED, verdict-only, no vendor. Branch after 401 (G2c keeps LOGIN_GATED), guarded to sub-500 (G2e keeps UNREACHABLE). |
| G3b (SVG tspan-split phrase) | WALLED | CHALLENGED / Generic | W15-003: generic human-check (and JS_PROOF) phrases are also matched against tag-stripped visible text — rendered text is what matters, markup splits are not semantic splits. Served-page gate still applies (G3c). |
| G4c (invisible hCaptcha widget + visible text) | CHALLENGED / Generic | OPEN | W15-004: a "captcha" token appearing ONLY in an invisible-widget tag (data-size="invisible") is form-submission machinery, not a presented challenge — it must also survive invisible-tag stripping to fire when visible text exists. Content-free pages still fire (G4d); visible widgets and prose still fire (guards). |
| G5a (Refresh header to challenge) | OPEN | CHALLENGED / Generic | W15-005: the HTTP Refresh header's url is parsed as a redirect target with meta-refresh semantics. Served-page-gated (G5d). |
| G5b (Refresh header to login) | OPEN | LOGIN_GATED | W15-005, same rule in login form. |
| G6c (2FA code form off a login URL) | OPEN | LOGIN_GATED | W15-006: CODE_ENTRY_FORM — a served 2xx page whose form carries a code input (otp/2fa/auth-code/verification-code/security-code/one-time-code, or exactly "code") AND auth wording (verification/one-time/authentication/security code, 6-digit) reads LOGIN_GATED. Narrower than general form-text detection: discount-code forms match neither key (guards). Narrows, not closes, the Wave 14 F5 limitation — see LIMITATIONS-REVISIT.md. |
| G7b (small article + footer badge) | CHALLENGED / PerimeterX | OPEN | W15-007: "protected by X" / "powered by X" badge phrases are blanked from marker scans on 2xx pages — a badge on served content is furniture, not a fired wall. Error statuses keep full attribution (guard: 403 badge page keeps PerimeterX). |
| G8d (robots Disallow: / + Allow: /) | FAIL | PASS | W15-008: RFC 9309 tiebreak in `_agent_state` — an Allow: / in the applicable group cancels a Disallow: /; a non-root Allow alongside a Disallow: / softens blocked to restricted (partial access, the Wave 11 carve-out principle generalized to Allow lines). Existing C8/D6/E5 pins still pass via the suite. |
| G9b (frontmatter-only llms with url field) | PASS | WARN | W15-009: a leading YAML frontmatter block is stripped before llms content analysis — metadata URLs/links are not index entries. Frontmatter + real content still passes (G9a/G9c). |
| G9d (frontmatter link only) | PASS | WARN | W15-009, same fix. |
| G9c (frontmatter + one link) | WARN (post-W15-009) | PASS | W15-009 refinement, found during the fix: stripping metadata can push a real one-link index under the 20-char length gate — so the length gate no longer fires on bodies carrying a link, URL, or path ("effectively empty" means no usable content; E6b already holds that a minimal linked file is a real index). |
| G10a (urlset, lastmod-only entries) | PASS | WARN | W15-010: a sitemap document with zero <loc> entries reads WARN (SITEMAP_NO_URLS) — a table of contents with no contents. One <loc> suffices (G10d). |
| G10c (sitemapindex, lastmod-only) | PASS | WARN | W15-010, same fix. |

Two fixes needed a second iteration, both caught by re-running
the battery (not by the suite): G3b's first fix added the
visible-text alternative only to the second half of the
human-check condition, but the first half (phrase in raw body)
still gated everything — the visible-text alternative belongs
in both halves (and, by the same principle, in the JS_PROOF
branch, pinned by a tspan-split JS_PROOF guard). G9c's first
fix exposed the length-gate interaction above. Both are
documented here because they are the kind of half-fix that a
single battery run would have missed.

## Pins that held (26 shapes)

G1a/G1b/G1d (JSON-LD generic rules), G2b/G2c/G2d/G2e (refusal
variants), G3a/G3c (SVG text), G4a/G4b/G4d (hCaptcha variants),
G5c/G5d (Refresh routing), G6a/G6b/G6d (2FA screens), G7a/G7c
(footer badges), G8a/G8b/G8c (robots Allow semantics),
G9a (frontmatter + index), G10b/G10d (sitemaps with locs).

## Notable interactions

- **W15-001 vs W14-001 is a scope distinction, not a contradiction.**
  W14-001 left vendor markers load-bearing in scripts because
  challenge-platform loader scripts ARE wall signals. JSON-LD is
  data, not code: the fix strips ld+json blocks only, by script
  TYPE, and the guard pin (regular script + vendor marker +
  visible text → still CHALLENGED) proves the loader species
  survived.
- **W15-003 changes what "the body" means for phrase scans.**
  The raw body is markup; the visible text is the rendered page.
  A phrase scan that only reads markup misses rendered sentences
  split across elements — and, symmetrically, a scan that only
  read visible text would miss script-only challenges (F1a).
  Both scans now run, and the script-only suppression still
  decides between them. The next wave should test whether
  TRAFFIC_CHECK needs the same treatment (noted, not assumed).
- **W15-006 is deliberately narrow.** The Wave 14 F5 limitation
  (password sign-in forms are not login signals) stands: a
  "sign in" link still cannot fire LOGIN_GATED. Code-entry forms
  earned an exception because the signal is two-keyed (code
  input + auth wording) and specific — the discount-code guards
  prove the boundary holds on both sides.
- **W15-010's blast radius is honest and small.** A bare <?xml
  prolog with no sitemap content, previously PASS via the prolog
  rule, now reads WARN (a prolog alone is not a sitemap) —
  pinned by a guard fixture rather than silently changed.

## What this wave says about saturation

Battery v7 found 13 genuine defects on shapes no earlier battery
exercised — the adversarial surface is still not exhausted, and
Wave 15 is NOT a clean wave on the battery prong regardless of
Leg A's clean sheet (zero fix-driven moves, fifth straight round).
The saturation clock, reset by Wave 14, stays reset: a clean wave
needs zero defects in BOTH the battery and the measurement round.
Wave 16 next; ~2.5h remain to 07:00.
