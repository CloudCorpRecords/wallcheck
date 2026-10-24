# Wave 19 — Problems ledger

## Leg B (adversarial battery v11) — 8 defect families, all fixed

- **W19-001** (classifier, fixed): challenge markers living only
  inside <template> elements drove verdicts on served paragraphs
  (L1a/L1d/L1f). Fix: template blocks are stripped from
  _visible_text, the vendor scan, the generic survival variants,
  the traffic scan, and the overlay/banner/dialog windows — all
  conditioned on visible text, so template-only pages still fire
  (blob-is-the-page, L1b). Fixtures: test_l1a/d/f + pins
  L1b/c/e.
- **W19-002** (classifier, fixed): a challenge phrase split
  across several images' alt attributes read WALLED (L2a) — the
  concatenated-text scan removes whole tags (alt values
  included) and no single attribute held the phrase. Fix: alt
  values in document order, joined with spaces, join the phrase
  scans as a presented-text variant (derived from the
  script-stripped body, template/noscript stripped when the page
  has visible text). Cross-language fragments compose nothing
  (J7g). Fixtures: test_l2a + pins L2b/c/d/f; guard L2e
  (corrected — see below).
- **W19-003** (classifier, fixed): email-only Continue sign-in
  steps read OPEN (L3a) — no link wording (H10), no code input
  (G6), no login URL (heuristic). Fix: EMAIL_CONTINUE_PROMPT —
  email input + Continue button (button text or submit value) +
  auth-purpose wording in rendered visible text — beside the
  code-entry, passkey, magic-link, delivery-code, and QR
  siblings with the same served-page size gate. Signup wording
  is deliberately not an auth purpose (L3g boundary). Fixtures:
  test_l3a + guards L3b/d/e/f/g. One Wave 16 guard superseded
  with independent justification (see below).
- **W19-004** (audit tool, fixed): the sitemap fallthrough
  stopped at stub documents (L4a/b) — _is_sitemap_doc counted a
  bare `<?xml` prolog and loc-less urlsets as usable, while
  _check_sitemap grades both WARN. Fix: one usability test in
  both places — a document is usable only when it is a
  urlset/sitemapindex carrying at least one <loc> naming a
  crawlable URL. The grade for a directly-supplied record is
  unchanged; only the fallthrough's test tightened. Fixtures:
  test_l4a/b + pins L4c/d/f/g; L4e now reads WARN with
  DECLARED_SITEMAP_DEAD evidence (the fallthrough correctly
  reports "declared and nothing usable" instead of grading the
  stub).
- **W19-005** (audit tool, fixed): CR-only frontmatter survived
  the llms strip (L5d) — the frontmatter regex requires `\n`, so
  a CR-only stub's metadata URL counted as content and the file
  read PASS. Fix: normalize CRLF and CR-only endings to LF
  before the frontmatter anchor (after the BOM strip, so the two
  compose — L5f). Fixtures: test_l5d + pins L5a/b/c/e/f.
- **W19-006** (audit tool, fixed): fragment-only <loc> entries
  passed the sitemap check (L6b) — the nonempty test counted
  "#section" as content. Fix: a loc counts only when its
  stripped content is non-empty AND not fragment-only;
  query-string references still count (they resolve to URLs).
  Fixtures: test_l6b + pins L6a/c/d/e.
- **W19-007** (classifier, fixed): Hebrew, Persian, Urdu, and
  Bengali challenge phrases were not in the localized list
  (L7a/b/c/d/e). Fix: added the phrases to
  _LOCALIZED_HUMAN_CHECK, gated like every generic marker.
  TR/AR/KO verified already present by grep, not re-claimed.
  Fixtures: test_l7a/b/c/d/e + pins L7f/g.
- **W19-008** (classifier, fixed): native <dialog open>
  challenges on served articles read OPEN (L8a/e) — the overlay
  tag list matches class/id markers only, so a bare <dialog>
  tag was invisible and the size gate suppressed the phrase.
  Fix: a dialog loop beside the overlay/banner rules — a
  <dialog> tag carrying a standalone open attribute (strict
  match, so data-open cannot fake it) plus a human-check or
  JS-proof phrase in the following 800 chars fires
  OVERLAY_CHALLENGE, with the login exclusion mirroring J8.
  Fixtures: test_l8a/e + pins L8d/f; guards L8b/c/g.

## Leg B — hand-correction (discipline working)

- **L2e.** The first draft used alt="ich bin kein roboter" as
  the second half of a cross-language fragment pair, but that IS
  a complete DE phrase (Wave 6) on its own — the classifier
  rightly read CHALLENGED. Corrected to a true fragment ("kein
  roboter", no listed phrase) before any fix landed; the
  corrected guard passes. Same species as Wave 6's S2c
  correction: a hand-classification corrected by independent
  evidence, not a test flipped to match code.

## Leg B — guard supersession (independent justification)

- **Wave 16 guard `test_guard_email_form_without_link_wording`.**
  The guard pinned "an email input plus generic 'sign in' prose
  (no link wording) is not a magic-link form" → OPEN. That
  sentence remains true (the magic-link rule still needs link
  wording). But the guard's shape — "Sign in to your account"
  label + email input + Continue button, the page's only content
  — IS an email-only Continue sign-in step under the new,
  hand-classified L3 rule, so the verdict moves to LOGIN_GATED
  via EMAIL_CONTINUE_PROMPT. The guard test was updated with
  this justification: the shape meets SPEC's LOGIN_GATED
  definition on its own grounds, and the magic-link rule's
  narrowness is proven intact by the L3d/L3e guards (Subscribe
  buttons and script-only auth wording still read OPEN). No
  other existing test changed verdict.

## Leg B — corpus regression (done)

Stored captures replayed through the Wave 19-fixed classifier
(`validation/wave15/corpus_check.py`, output vs Wave 15's
`corpus-after.txt`). Zero regressions: diff is empty.

## Leg D (LOGIN_GATED watch) — done, no softening

- **claude.ai:** re-probed once — 200 LOGIN_GATED / Cloudflare,
  final URL https://claude.ai/login. The gate is a real login
  redirect, unchanged from round 14. No softening.
- **fda.gov:** re-probed once — 401 LOGIN_GATED / Akamai. The
  401 stands, unchanged from round 14. No softening.

## Leg A (round-15 reclassification) — DONE

- **Runner:** fresh runner, single ROUND constant, fully
  detached (setsid nohup, resumable, log-monitored) — no
  incident, 500/500 probes, zero missing, zero dupes. The
  runner imported the Wave 18 tree at launch (11:57 UTC, before
  any Wave 19 battery edit), so round 15 measures the Wave 18
  tree end to end; the Wave 19 battery fixes are unmeasured
  until round 16.
- **10 diffs, all hand-checked with two fresh captures each:**
  6 merged (ed.gov to UNREACHABLE on round + 2 failures;
  forbes.com to CHALLENGED / DataDome on round + 2 agreeing
  challenges — the triple the oscillator's earlier 2–1 splits
  never met; irishjobs.ie, jobs.ie, totaljobs.com to OPEN on
  round + 2 served readings; jobrapido.com to RATE_LIMITED on
  round + 2 agreeing 429s), 4 held (apnews.com CHALLENGED on a
  1–1 fresh split; abc.net.au OPEN on two agreeing served
  readings against a round Akamai 403; lowes.com OPEN on a 1–1
  fresh split; npmjs.com CHALLENGED on two agreeing fresh
  challenges against a round connection drop — the 8th
  transport-pattern sighting).
- **Fix-driven moves: zero.** All five spotlights held
  (ubereats.com OPEN — Wave 17 head-strip move holds;
  remoteok.com, td.com, venmo.com OPEN — no QR misfire recurs;
  rubygems.org OPEN — W17-007 holds). The zero-fix-driven-move
  run resumes after round 14's single move.
- **Fresh-capture method note:** probe_url returns no body, so
  the script uses fetch_raw + classify (the Wave 16 spot-check
  hit the same discovery). Because fresh captures ran on the
  Wave 19 tree while the round measured the Wave 18 tree, every
  capture carries a Wave 19-rule involvement check — all 20
  report zero flags, so the corroborations are tree-comparable.
  See STABILITY-14.md. INDEX distribution after merges: OPEN
  419 / CHALLENGED 21 / WALLED 35 / RATE_LIMITED 8 /
  UNREACHABLE 15 / LOGIN_GATED 2 (500 rows, recount verified).
