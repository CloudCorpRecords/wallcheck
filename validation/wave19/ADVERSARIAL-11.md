# Wave 19 — Adversarial Battery v11: Results

51 shapes, hand-classified first in HANDCLASS-11.md, run against
the classifier in `tests/test_adversarial11.py`. **8 defect
families, all fixed test-first and generalized; corpus clean
(44 captures, zero diff vs the Wave 15 baseline); full suite
532/532 green** (481 pre-existing + 51 new).

## Defects fixed

- **W19-001 — template-block challenges read CHALLENGED (L1).**
  A <template> element's contents are inert — parsed but never
  rendered until a script clones them — yet no strip existed
  anywhere, so template text drove the generic and vendor scans
  on served paragraphs. Fix, in the family conditioning: template
  blocks are stripped from _visible_text, from the vendor scan,
  from the generic survival variants, from the traffic scan, and
  from the overlay/banner/dialog windows — all conditioned on
  visible text, so template-only pages still fire
  (blob-is-the-page, L1b). Fixtures: L1a/d/f + pins L1b/c/e.
- **W19-002 — phrases split across images' alt attributes read
  WALLED (L2a).** The concatenated-text scan removes whole tags
  (alt values included), and no single attribute held the phrase.
  Fix: alt values in document order, joined with spaces, join the
  phrase scans as a presented-text variant (derived from the
  script-stripped body, with template/noscript stripped when the
  page has visible text — script text is configuration, never an
  attribute). Cross-language fragments compose nothing (J7g):
  the join is checked for whole listed phrases only. Fixtures:
  L2a + pins L2b/c/d/f; guard L2e (corrected fixture — see
  below).
- **W19-003 — email-only Continue sign-in steps read OPEN (L3a).**
  No rule named the shape: no link wording (H10), no code input
  (G6), no login URL (heuristic). Fix: EMAIL_CONTINUE_PROMPT —
  email input + Continue button (button text or submit value) +
  auth-purpose wording in rendered visible text — placed beside
  the code-entry, passkey, magic-link, delivery-code, and QR
  siblings with the same served-page size gate. Signup wording
  is deliberately not an auth purpose (L3g boundary). Fixtures:
  L3a + guards L3b/d/e/f/g. One Wave 16 guard superseded, with
  independent justification (see below).
- **W19-004 — declared sitemaps that are stubs by the grade's own
  test blocked the fallthrough (L4a/b).** _is_sitemap_doc counted
  a bare `<?xml` prolog and loc-less urlsets as usable, while
  _check_sitemap grades both WARN — so a stub early in the
  declaration list hid a real sitemap later in it. Fix: one
  usability test in both places — a document is usable only when
  it is a urlset/sitemapindex carrying at least one <loc> naming
  a crawlable URL. The grade for a directly-supplied record is
  unchanged (a prolog-only record still grades WARN); only the
  fallthrough's test tightened. Fixtures: L4a/b + pins L4c/d/f/g;
  L4e now reads WARN with DECLARED_SITEMAP_DEAD evidence (the
  fallthrough correctly reports "declared and nothing usable"
  instead of grading the stub).
- **W19-005 — CR-only frontmatter survived the llms strip (L5d).**
  The frontmatter regex requires `\n`, so a CR-only file's
  metadata URL counted as index content and the stub read PASS.
  Fix: normalize CRLF and CR-only endings to LF before the
  frontmatter anchor (after the BOM strip, so the two compose —
  L5f). Fixtures: L5d + pins L5a/b/c/e/f.
- **W19-006 — fragment-only <loc> entries passed the sitemap
  check (L6b).** The nonempty test counted "#section" as
  content. Fix: a loc counts only when its stripped content is
  non-empty AND not fragment-only; query-string references still
  count (they resolve to URLs). Fixtures: L6b + pins L6a/c/d/e.
- **W19-007 — Hebrew, Persian, Urdu, and Bengali challenge
  phrases missing (L7).** Four new language families added to
  _LOCALIZED_HUMAN_CHECK, gated like every generic marker.
  TR/AR/KO were already in the list (verified by grep, not
  re-claimed). Fixtures: L7a/b/c/d/e + pins L7f/g.
- **W19-008 — native <dialog open> challenges read OPEN (L8a/e).**
  The overlay tag list matches class/id markers only, so a bare
  <dialog> tag was invisible and the size gate suppressed the
  phrase. Fix: a dialog loop beside the overlay/banner rules —
  a <dialog> tag carrying a standalone open attribute (strict
  match: whitespace before "open", then whitespace, =, or tag
  end, so data-open cannot fake it) plus a human-check or
  JS-proof phrase in the following 800 chars fires
  OVERLAY_CHALLENGE, with the login exclusion mirroring J8.
  Fixtures: L8a/e + pins L8d/f; guards L8b/c/g.

## Hand-correction (discipline working, not a flipped test)

- **L2e.** The first draft used alt="ich bin kein roboter" as the
  second half of a cross-language fragment pair, but that IS a
  complete DE phrase (Wave 6) on its own — the classifier rightly
  read CHALLENGED. Corrected to a true fragment ("kein roboter",
  no listed phrase) before any fix landed; the corrected guard
  passes. Same species as Wave 6's S2c correction: a
  hand-classification corrected by independent evidence.

## Guard supersession (independent justification required)

- **Wave 16 guard `test_guard_email_form_without_link_wording`.**
  The guard pinned "an email input plus generic 'sign in' prose
  (no link wording) is not a magic-link form" → OPEN. That
  sentence remains true (the magic-link rule still needs link
  wording). But the guard's shape — "Sign in to your account"
  label + email input + Continue button, the page's only content
  — IS an email-only Continue sign-in step under the new,
  hand-classified L3 rule, so the verdict moves to LOGIN_GATED
  via EMAIL_CONTINUE_PROMPT. The guard test was updated with this
  justification, not silently flipped: the shape meets SPEC's
  LOGIN_GATED definition on its own grounds, and the magic-link
  rule's narrowness is proven intact by the L3d/L3e guards
  (Subscribe buttons and script-only auth wording still read
  OPEN). No other existing test changed verdict.

## Pins (no defect — the classifier was already right)

- **L1b (template-only page).** Blob-is-the-page: the raw scan
  fires when there is no visible text to condition on.
- **L1c (template vendor on a big article).** The size gate.
- **L1e (script asset-filename carrier).** Script blocks are
  already stripped from the survival test.
- **L2b/L2c (single-attribute alts).** F2 species: the raw scan
  already fires.
- **L2d (alt phrase on a big article).** The served-page gate.
- **L2f (script preload list).** Script text is configuration
  when the page has visible text.
- **L3c (Continue at a login URL).** The login heuristic.
- **L3b/L3d (no auth purpose / Subscribe, not Continue).**
  Both keys are load-bearing.
- **L3e (script-identifier carrier).** Auth purpose must appear
  in rendered visible text.
- **L3f (sign-in section on a big article).** The served-page
  size gate.
- **L3g (Create-account Continue).** Boundary pin: signup
  wording is not an auth purpose; the narrow rule stays narrow.
- **L4c/L4d (dead declarations fall through).** Wave 14 species.
- **L4f (conventional path serves).** No fallthrough needed.
- **L4g (commented Sitemap line).** J5 species: not a
  declaration.
- **L5a/L5b/L5c/L5e (CRLF index / stub / shell / CR index).**
  The frontmatter regex already tolerated `\r\n`; link/URL
  tests do not depend on line endings.
- **L6a/L6c/L6d (query-string locs).** References resolve to
  URLs; one good loc suffices.
- **L6e (whitespace-only locs).** K6d species.
- **L7f (quoted Hebrew phrase on a big article).** The
  served-page gate.
- **L7g (code-switched fragments).** J7g species.
- **L8c (cookie-text dialog).** No challenge phrase, no wall.
- **L8d (dialog on a small page).** The small-page path.
- **L8f (dialog on a login URL).** The J8 login exclusion.
- **L8g (stylesheet dialog class).** Style blocks are
  configuration; no dialog element exists.

## Corpus regression

All 44 stored captures replayed through the Wave 19-fixed
classifier (`validation/wave15/corpus_check.py` output vs
Wave 15's `corpus-after.txt`): **diff is empty.** The template
strip, alt-join, Continue rule, dialog rule, language additions,
and audit changes touch no capture.

## Verification

- Full suite: **532/532 green** (481 pre-existing + 51 new).
- MCP smoke: all three tools pass live (`scripts/smoke_mcp.py`:
  initialize, tools/list `['probe_url', 'classify', 'audit']`,
  classify → CHALLENGED / Cloudflare, probe_url(example.com) →
  OPEN 200, audit(example.com) → F 3/12).
- Every Wave 19 JSON re-read and parsed; no 0-byte files.
