# Wave 13 — Problems ledger

## Leg B (adversarial battery v5) — 3 defects, all fixed

- **W13-001** (classifier, fixed): vendor markers inside HTML
  comments drove verdicts and attribution (E9a: a comment
  containing "Just a moment" on a short article read CHALLENGED /
  Cloudflare; E9b: a comment containing "perimeterx" on a
  refusal read CHALLENGED / PerimeterX). Fix: HTML comments are
  stripped before every body scan in `_detect_vendor` (markers,
  redirect targets, generic phrases alike) — comments are
  developer metadata, not rendered content and not executed
  code. Fixtures: test_e9a, test_e9b.
- **W13-002** (classifier, fixed): "Please wait while we check
  your browser" stub read OPEN. Fix: "check your browser" joins
  the JS_PROOF phrase list, gated to small pages like every
  phrase there (the existing "checking your browser" phrase is
  not a substring of this wording). Guard pin: a 20 KB article
  mentioning "check your browser" stays OPEN. Fixtures:
  test_e4b_js_proof_stub_with_px_cookie (also pins that the
  _pxvid sensor cookie does not upgrade the vendor),
  test_e4b_guard_article_mentioning_check_browser.
- **W13-003** (audit tool, fixed): a title-only llms.txt
  ("# Welcome to Example Corporation", no links, paths, or
  URLs) read PASS. Fix: an llms body with no markdown link, no
  URL, and no path token reads WARN (LLMS_STUB) — a title line
  is not an index, whatever its length; the 20-char length gate
  alone passes any long title. Bodies with even one link or
  path (D7b's plain-text index lines, E6b's minimal linked
  file) still pass. Fixture: test_e6a_title_only_llms.

## Leg B — corrections, not defects

- **E8b hand vendor corrected** (LOGIN_GATED, None →
  LOGIN_GATED, Cloudflare): the Wave 11 C2c precedent already
  establishes loader-vendor attribution on loader-only login
  pages. The classifier was right; HANDCLASS-5.md records the
  correction.
- **E3b fixture bug**: first-draft article 15,600 bytes, under
  the 16,384 served-page gate, so the title phrase legitimately
  fired. Lengthened past the gate with a length assert. Lesson
  restated: fixture sizes must clear the gate they test.

## Leg B — corpus regression

44 stored captures replayed through the Wave 13-fixed
classifier (`validation/wave13/corpus_check.py`, copied from
Wave 11's runner; no git baseline exists, so this is a
read-and-judge pass, not a diff). Every real wall capture reads
as its wave established: ebay/guru/medium WALLED with vendors,
monster/nytimes/npmjs CHALLENGED, amazon CHALLENGED/Generic,
booking AWS WAF, chewy Kasada RATE_LIMITED, delta Akamai 444,
hyatt/state/catho/haaretz WALLED vendor None — the last four
corroborate Leg C's unattributed-bare-403 finding from live
captures, not just history rows. One artifact, not a
regression: `validation/wave7/captures/careerjet.json` reads
OPEN because the JSON record carries an empty body (the real
10,937-byte HTML lives in `careerjet.html`, which classifies
CHALLENGED / Cloudflare exactly as Wave 7 established).

## Leg A (round-9 reclassification) — pending at ledger time

Round 9 was still probing (150/499) when this ledger was
written; its defects, moves, and merges live in STABILITY-8.md.
The three battery defects above already disqualify Wave 13 as
a clean wave regardless of Leg A's outcome — the saturation
clock resets again (see OVERNIGHT.md).

## Leg C (index audit) — see INDEX-AUDIT.md

No verdict drift: 499 rows, distribution matches the header
exactly, 44-row stratified spot-check against round-8 history
with zero mismatches. Four surgical vendor-cell fixes
(unattributed bare-403 notes) applied to INDEX.md.
