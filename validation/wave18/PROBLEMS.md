# Wave 18 — Problems ledger

## Leg B (adversarial battery v10) — 6 defect families, all fixed

- **W18-001** (classifier, fixed): sticky-banner challenges on
  served articles read OPEN (K2a/K2e: 20 KB article + fixed
  announcement banner with a human-check or JS-proof phrase).
  Fix: a banner rule beside the J8 overlay rule — banner marker
  + phrase in the following 800 chars + a stickiness third key
  (the banner tag itself must signal fixed/sticky positioning).
  The bare-marker first attempt misread the K2f guard (in-flow
  banners are layout) and was corrected before green. Fixtures:
  test_k2a/e + guards K2b/c/d/f.
- **W18-002** (classifier, fixed): SMS/email code prompts in
  digit-box inputs read OPEN (K3a/K3e). Fix: DELIVERY_CODE_PROMPT
  — digit-box input + delivery wording in rendered visible text
  — beside the code-entry, passkey, and magic-link rules with
  the same gates. Fixtures: test_k3a/e + guards K3b/c/d/f.
- **W18-003** (audit tool, fixed, evidence only): a declared-but-
  dead sitemap was indistinguishable from no declaration (K4a/
  K4d). Fix: DECLARED_SITEMAP_DEAD evidence on the sitemap
  check's WARN paths when robots declared sitemaps (accurate
  because the fallthrough already established that none served).
  Grades unchanged. Fixtures: test_k4a/d + pins K4b/c/e.
- **W18-004** (audit tool, fixed): sitemaps with only empty
  `<loc>` elements passed (K6c/K6d). Fix: `_has_nonempty_loc`
  — at least one `<loc>` must carry non-empty content; relative
  references still count. Fixtures: test_k6c/d + pins K6a/b/e.
- **W18-005** (classifier, fixed): PT-BR, Indonesian, Vietnamese,
  and Thai challenge phrases were not in the localized list
  (K7a/c/d/e/f/g/h). Fix: added the phrases to
  `_LOCALIZED_HUMAN_CHECK`. Fixtures: test_k7a/c/d/e/f/g/h +
  pins K7b/i/j.
- **W18-006** (classifier, fixed): aria-labels on non-interactive
  elements drove vendor attribution (K8d: a `<div>`'s
  aria-label "perimeterx" on an article read CHALLENGED /
  PerimeterX). Fix: non-interactive aria-label attributes are
  stripped from every body scan when the page has visible text
  (attribute only — tag prefixes and overlay class markers
  survive); interactive elements keep their accessible names.
  Fixtures: test_k8d + pins K8a/b/c/e.

## Leg B — pins and boundaries (no defect)

- **K1a/K1d (unconsumed custom properties):** stylesheet
  configuration, covered by the style-block strip (H3b/H3e
  species).
- **K1b/K1e (CSS content / property-only pages):** the content
  string is the page's only text (H3a/H3f species).
- **K1f (decorative content: on a big article):** the size gate
  protects the article; the CSS-content wiring is conditioned
  on content-free pages (see the H3b regression note in
  ADVERSARIAL-10.md).
- **K1c (split custom properties via var()):** FIXED, not a
  limitation — the first analysis said a bounded fix was
  infeasible (a regex substitution leaves declaration punctuation
  between the halves), but the implemented fix resolves
  `var()` inside `content:` declarations and concatenates the
  resulting string tokens per CSS rendering rules, which is
  exactly what the rendered text is. The fix is conditioned on
  content-free pages (H3b) and checked per string, never joined
  across declarations (J7g). Fixture: test_k1c.
- **K5 (llms via trailing-slash redirects):** the fetcher
  follows redirects; all five final-document species grade
  correctly. Pins, not fixes.
- **K6a/K6b/K6e (relative locs):** relative references name
  destinations; the counting rule already covers them.
- **K7b (fuller PT-BR form):** substring-covered by the existing
  PT phrase. K7i (quoted Thai phrase on a big article): the
  served-page gate. K7j (code-switched fragments): no phrase
  composes across languages (J7g species).
- **K8a/K8b/K8c/K8e (interactive aria-labels):** accessible
  names of interactive elements are presented text (F2
  principle); the raw scan and the size gate already handle
  them.

## Leg B — corpus regression (done)

Stored captures replayed through the Wave 18-fixed classifier
(`validation/wave15/corpus_check.py`, output vs Wave 15's
`corpus-after.txt`). Zero regressions: diff is empty.

## Leg A (round-14 reclassification) — live catch

- **W18-007** (classifier, fixed): the Wave 17 QR_PROMPT rule
  misfired on three served homepages — remoteok.com (its only QR
  signal is a script filename, `/qrcode.js`), td.com (a script
  identifier, `qrCode` in a Branch analytics token list), and
  venmo.com (stylesheet class names, `.qr-code-image-container`
  rules for an app-download code). The Wave 17 rule read wording
  from the raw body and had no served-page gate — the same
  failure mode W17-007 fixed for its passkey and magic-link
  siblings, one rule later. Fix, generalized to the QR rule:
  (1) QR wording AND auth purpose must appear in rendered
  visible text (the prompt marker stays a raw element check —
  an image, canvas, or button IS presented machinery); (2) the
  QR branch gains the served-page size gate its siblings carry.
  Post-fix live re-probes of all three homepages read OPEN 200.
  Fixtures: test_w18_remoteok_qr_asset_filename_is_open,
  test_w18_td_qr_script_identifier_is_open,
  test_w18_venmo_qr_css_class_is_open,
  test_w18_large_page_qr_prompt_is_open,
  test_w18_real_qr_prompt_still_fires. The three rows HOLD at
  OPEN; the round's only fix-driven move is ubereats.com (see
  STABILITY-13.md). Full suite after the fix: 481/481; corpus
  still clean.

## Leg A (round-14 reclassification) — runner incident

The first round-14 launch died at 123/499 with no traceback in
its log (last line "probed 100"; the process was gone; supervisor
restarts in the same window suggest an external kill, as in Wave
4's service restart). The runner's resume logic skipped the 123
completed rows, but a plain resume would have imported the
Wave 18-fixed tree — mixing trees inside one measurement round,
which the wave discipline forbids (a round measures ONE tree).
Fix, following Wave 14's tree-copy precedent: the resume runner
(`run_round14_resume.py`) imports a reconstructed Wave 17 tree
(`validation/wave18/src-wave17-tree/`, all Wave 18 edits
reverted in the copy only, verified by diff — only classify.py
and audit.py differ — and by behavior probes: K1c OPEN, K2a
OPEN on a truly big article, K7a WALLED, K3a OPEN, K8d
CHALLENGED/PerimeterX on the copy vs CHALLENGED on the current
tree for K2a, J8 overlay still CHALLENGED on both). Round 14
therefore measures the Wave 17 tree end to end; the Wave 18
battery fixes are unmeasured on live traffic until round 15.
See STABILITY-13.md for the round-14 verdict moves.
