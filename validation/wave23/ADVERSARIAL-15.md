# Wave 23 — Adversarial Battery v15: Results

36 shapes, hand-classified first in HANDCLASS-15.md, run
against the classifier in `tests/test_adversarial15.py`.
**3 defect families, all fixed test-first and generalized;
corpus clean (44 captures, zero diff vs the Wave 15
baseline); full suite green (see the wave report for the
verified count).**

## Defects fixed

- **W23-Q1 — stray <picture> text nodes drove verdicts
  (Q1a).** A text node inside <picture> is never rendered
  (the element renders only its <img>), yet _visible_text
  kept it as body text, so a challenge phrase there
  challenged a page carrying a real paragraph. Fix: a
  _PICTURE_BLOCK_RE strip joins the never-presented family
  (the Wave 19 template species) in _visible_text and in
  every conditional scan variant — vendor, noscript-clean
  (+ nospace through it), the three generic variants,
  traffic, and the overlay/banner/dialog windows —
  conditioned on visible text like every suppression in
  the family, so a picture-only page still fires (Q1b).
  The alt scan is deliberately exempt: the picture's img
  renders, so its alt is presented text (Wave 19 L2).
- **W23-Q2 — HTTP 418 read OPEN (Q2a/b/d).** The status
  chain had no 418 branch; the final else recorded any
  non-(401/403) remainder as OPEN. Fix: 418 joins the
  deliberate-refusal family (444 Wave 5, 451 Wave 10) as
  WALLED with STATUS_418. The P2c composition holds (a
  challenge phrase in the body records Generic; the code
  governs the verdict — Q2b), and a fired vendor
  challenge still outranks the bare status (Q2c).
- **W23-Q7 — Greek, Czech, Hungarian, Romanian challenge
  phrases missing (Q7a/b/c/d).** Four full "confirm you
  are not a robot" sentences added to
  _LOCALIZED_HUMAN_CHECK, gated like every generic
  marker.

## Hand-correction (discipline working, not a flipped test)

- **Q7f.** The first draft asserted a lone Greek fragment
  on a 403 reads OPEN; it reads WALLED, correctly — a
  bare 403 is a refusal whatever fragment rides along
  (the J7g precedent). The fragment pin now sits on a
  served 200 page, as P7f's did. See PROBLEMS.md.

## Pins (no defect — the classifier/audit was already right)

- Q1b/c/d/e (survival on a picture-only page; served-page
  gate; a picture alone is content; asset filenames are
  configuration); Q3a/b/c/d (robots wildcard placement:
  group selection is by agent match, not position;
  duplicate wildcard groups flatten, Allow tiebreak
  applies); Q4a/b/c/d (frontmatter markdown stays out of
  the llms content analysis — the strip is a block
  strip); Q5a/b/c/d (sitemap scheme case: lowercased
  before comparison, non-HTTP schemes still rejected);
  Q6a/b/c/d (<slot> fallback is presented text — it
  renders in a plain document, the anti-template; and a
  slot inside a template is suppressed with the
  template); Q7e/f/g (served gate; fragments; style-block
  suppression); Q8a/b/c/d (HTTP-date Retry-After: the
  rule keys on presence, never parses the value — date
  and seconds forms behave identically, and the header
  alone still does not convert a refusal).

## Corpus regression

All 44 stored captures replayed through the Wave 23-fixed
classifier (`validation/wave15/corpus_check.py` output vs
Wave 15's `corpus-after.txt`): **diff is empty.** The
picture strip, the 418 branch, and the language additions
touch no capture.

## Verification

- Battery: **36/36 green** after fixes (first run 27/36 —
  8 predicted gaps in 3 families + 1 hand-correction).
- Full suite and MCP smoke: see the wave report.
