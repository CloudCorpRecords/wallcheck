# Wave 23 — Battery v15: Problems found and fixed

Battery v15: 36 shapes, hand-classified first in HANDCLASS-15.md.
First run: 9 failures — 8 predicted gaps in 3 families plus 1
hand-classification error of mine (Q7f), zero surprises. After
fixes: 36/36 green.

## Defects fixed (all test-first, generalized)

- **W23-Q1 — stray text nodes inside <picture> drove verdicts
  on served pages (Q1a).** _visible_text strips tags but keeps
  text nodes, and no strip existed for <picture> blocks, so a
  "Verify you are human" text node inside a picture element —
  content no browser renders (the element renders only its
  <img>) — read as presented body text and challenged a page
  with a real paragraph. Fix, in the never-presented family
  (the template species, Wave 19 L1): _PICTURE_BLOCK_RE strips
  <picture>...</picture> blocks from _visible_text itself and
  from every conditional (has_visible) scan variant —
  b_vendor, bl_noscript_clean (and through it the nospace
  variant), bl_generic_noscript, bl_generic_nowidget,
  bl_generic_clean, bl_traffic, and the overlay/banner/dialog
  windows. Content-free pages still fire (Q1b): with no other
  text the survival clause reads the raw body. Deliberate
  exclusion: the strip is NOT applied to the alt-attribute
  scan source — the picture's <img> renders, so its alt text
  IS presented (the Wave 19 L2 family), unlike template
  content, which is inert whole.
- **W23-Q2 — HTTP 418 read OPEN (Q2a/b/d).** No 418 branch
  existed, so a 418 response fell to the final else and read
  OPEN whenever no wall signal had fired — a server that
  declined the request recorded as served. Fix: 418 joins
  the deliberate-refusal family beside 444 (Wave 5) and 451
  (Wave 10) — a new elif in the status chain reads WALLED
  with STATUS_418 evidence. Q2b confirms the P2c composition:
  a challenge phrase in the refusal body still records
  Generic as the vendor (body evidence), while the refusal
  code governs the verdict. Q2c confirms precedence: a fired
  Cloudflare challenge still outranks the bare status.
- **W23-Q7 — Greek, Czech, Hungarian, Romanian challenge
  phrases missing (Q7a/b/c/d).** Verified against the current
  _LOCALIZED_HUMAN_CHECK list before writing: none of the
  four languages had an entry. Fix: four full "confirm you
  are not a robot" sentences added, gated like every generic
  marker. Fragments compose nothing (Q7f) and served-page
  mentions stay OPEN (Q7e); a phrase living only in a
  <style> block stays suppressed on a content page (Q7g,
  the Wave 16 conditioning — the family's negative carrier).

## Hand-correction (discipline working, not a flipped test)

- **Q7f.** My first draft asserted the Greek fragment
  "ρομπότ" alone on a 403 reads OPEN. It reads WALLED, and
  WALLED is correct: a bare 403 is a refusal whatever
  fragment rides in the body (the J7g precedent — its own
  fixture is named "codeswitched fragments are WALLED").
  The fragment pin belongs on a served page (P7f used
  200). The test now uses 200 and asserts OPEN — the
  fragment fires no challenge rule. Recorded here and in
  HANDCLASS-15.md.

## Pins (no defect — the classifier/audit was already right)

- Q1b/c/d/e (picture-only page fires via survival; served
  gate; picture alone is content; asset filenames are
  configuration); Q2c (vendor precedence over bare
  status); Q3a/b/c/d (robots group selection is by agent
  match, not file position; duplicate wildcard groups
  flatten and the Allow tiebreak applies); Q4a/b/c/d
  (frontmatter block strip keeps markdown in metadata
  fields out of the content analysis); Q5a/b/c/d (sitemap
  scheme comparison is case-insensitive but not
  scheme-blind); Q6a/b/c/d (slot fallback is presented
  text — the anti-template; template composition still
  suppresses); Q8a/b/c/d (Retry-After is keyed on
  presence, never parsed — the HTTP-date form behaves
  identically to seconds, and the header alone still
  does not convert a refusal).

## Corpus regression

All 44 stored captures replayed through the Wave 23-fixed
classifier (`validation/wave15/corpus_check.py` output vs
Wave 15's `corpus-after.txt`): **diff is empty.** The
picture strip, the 418 branch, and the language additions
touch no capture.

## Residual edges (ledgered, not fixed)

- None new this wave. The Wave 16 split-script-boundary
  edge remains ledgered as limitation-by-design (Wave 17
  re-test: the rendered page never presents the token).
