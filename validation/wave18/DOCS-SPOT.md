# Wave 18 — Docs Consistency Spot-Check (Leg D)

Scope (per the wave task): README.md's suite count, SPEC.md's
version/test-count lines, INDEX.md's header distribution.
LAUNCH-POST.md's Wave 1 numbers were NOT touched (launch copy,
refresh at ship — Wave 9's rule stands).

## The 423 vs 428 question — resolved

Wave 17's audit (DOCS-AUDIT-2.md, C-01) wrote 423 while the
suite finished at 428. **428 was right at Wave 17's end:**
423 was the battery-end count (375 at Wave 16 + 48 Wave 17
battery tests), and the W17-007 live fix added 5 fixtures after
the audit ran — verified by this wave's baseline run (428/428
green before any Wave 18 change). The audit measured the suite
mid-wave, not at its end. Both numbers are now superseded: the
Wave 18 final suite count is **481** (428 + 48 battery v10 +
5 W18-007 live-fix fixtures), verified by a full green run.

## Corrections made

- **D-01 (README.md, suite count, "New in 0.5.0-rc"
  paragraph).** Before: "Waves 10–17 took it to 423 tests."
  After: "Waves 10–17 took it to 428 tests (the Wave 17 audit's
  423 predates the W17-007 live fix's 5 fixtures); Wave 18's
  battery v10 plus the W18-007 live fix took it to 481."
- **D-02 (README.md, wave-list paragraph).** Before: "Waves
  10–17 ran seven more stability rounds (rounds 6–12) and
  adversarial batteries v2–v9 (280+ new shapes), took the suite
  to 423 tests." After: "Waves 10–18 ran nine more stability
  rounds (rounds 6–14) and adversarial batteries v2–v10 (330+
  new shapes), took the suite to 481 tests." Shape arithmetic:
  v2 32 + v3 31 + v4 27 + v5 25 + v6 32 + v7 39 + v8 49 + v9 48
  + v10 48 = 331. Round arithmetic: rounds 6–14 = 9 rounds.
  (Note: the old sentence was stale twice over — it also
  omitted Wave 17's round 13.)
- **D-03 (README.md, index size, "New in v0.5" paragraph).**
  Before: "The index now covers 499 sites (Waves 6–7
  expansion)." After: "covers 500 sites (Waves 6–7 expansion,
  Wave 18 row 500)."
- **D-04 (SPEC.md, Bot Wall Index status line).** Before:
  "Status (Wave 17, 0.5.0-rc + unreleased fixes): … 499 sites
  … stability rounds 2–12 (round 12 re-probed all 499 with zero
  rows moved …)." After: "Status (Wave 18, 0.5.0-rc +
  unreleased fixes): … 500 sites … stability rounds 2–14, and
  the Wave 18 row-500 addition (round 14 re-probed all 499 with
  five rows moved, one fix-driven under the Wave 17 head-strip
  rule …)."
- **D-05 (INDEX.md, header distribution).** Recounted row by
  row from the table after the round-14 merges and the row-500
  addition: OPEN 418 · CHALLENGED 21 · WALLED 35 · RATE_LIMITED
  7 · UNREACHABLE 17 · LOGIN_GATED 2 = 500 rows, 500 unique
  URLs. The header line matches exactly; no "499 sites" string
  remains in the file. The rounds narrative was also extended
  with the missing Wave 17 round-13 parenthetical (zero rows
  moved) and the Wave 18 round-14 parenthetical (five rows
  moved, seven held, row 500 added).

## Verified current (no change needed)

- **SPEC.md version stamp (0.5.0-rc).** No version files were
  touched this wave; the tree remains 0.5.0-rc + unreleased
  fixes, consistent with Wave 12's conclusion that the next
  stamp is 0.5.0 final, not another rc. No test-count line in
  SPEC besides the status line was stale.
- **Directory census denominator ("4 of 499").** Kept as the
  census's own denominator: census v2 measured 499 domains, and
  the 500th row was not censused. Changing it to "4 of 500"
  would misstate the census.
- **README.md historical sentences.** The v0.3-era "499 sites
  after the Waves 6–7 expansion" line and the "Wave 7 took the
  index to 499 sites" line describe their own waves, not the
  present; Wave 9's rule keeps them.
- **campaign/LAUNCH-POST.md.** Untouched per Wave 9's rule.

## Observation (not a correction — out of scope)

- **DOGFOOD.md's suite-count chain** ends at the Wave 17
  battery (423) with round 13 noted as in progress. A Wave 18
  addendum (481, round 14 complete) is due in the next docs
  pass; this leg's scope was README/SPEC/INDEX only, so it is
  recorded here rather than written.
