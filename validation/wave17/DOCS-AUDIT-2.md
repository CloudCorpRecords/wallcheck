# Wave 17 — Docs Re-Audit (Leg C)

Wave 9's docs audit is 8 waves stale. This pass re-checked
README.md, SPEC.md, DOGFOOD.md, INDEX.md, and campaign/*.md
against measured reality as of Wave 17: version stamps
(0.5.0-rc + unreleased fixes), test counts (423 after the Wave 17
battery), the index distribution (recounted row by row from the
table), adopter counts (4/499 + Wave 16 spot-check movement),
vendor lists, and own-properties grades. LAUNCH-POST.md's Wave 1
numbers were NOT touched (launch copy, refresh at ship — Wave 9's
rule stands).

## Corrections made

- **C-01 (README.md, suite count).** Before: the 0.5.0-rc section
  said "the suite stands at 120 tests." After: "the suite stood at
  120 tests at the Wave 9 stamp. Waves 10–17 took it to 423 tests."
  (423 = 375 at Wave 16 + 48 Wave 17 battery tests, full suite
  green, verified this wave.)
- **C-02 (README.md, wave list).** Before: the validation-waves
  paragraph ended at Wave 8 ("took the front-doors file to 65
  platforms"). After: extended with "Wave 9 stamped 0.5.0-rc and
  added the audit MCP tool; Waves 10–17 ran seven more stability
  rounds (rounds 6–12) and adversarial batteries v2–v9 (280+
  shapes), took the suite to 423 tests, and kept the launch hold."
  (Shape count: v2 32 + v3 31 + v4 27 + v5 25 + v6 32 + v7 39 +
  v8 49 + v9 48 = 283.)
- **C-03 (SPEC.md, Bot Wall Index status).** Before: "Status (Wave
  9, 0.5.0-rc)" with "stability rounds 2–5". After: "Status (Wave
  17, 0.5.0-rc + unreleased fixes)" with "stability rounds 2–12
  (round 12 re-probed all 499 with zero rows moved)" and "Wave
  16's spot-check found all four [adopters] still publishing."
- **C-04 (INDEX.md, rounds narrative).** Before: the narrative
  jumped from Wave 11 round 7 to Wave 13 round 9 with no round-8
  record. After: added the round-8 parenthetical (amazon.com to
  CHALLENGED on two agreeing interstitial readings,
  britishairways.com to UNREACHABLE on two agreeing timeouts;
  npmjs.com held CHALLENGED, 6th transport-pattern sighting;
  webex.com held OPEN on a single uncorroborated Akamai 403; no
  row moved under the Wave 11 classifier rules). Arithmetic
  verified: Wave 11 end (416/24/34/7/17/1) → round 8
  (414/25/34/7/18/1) → round 9 (415/25/35/7/17/0).
- **C-05 (campaign/REPORT-CARD-AKAMAI.md, vendor share).** Before:
  "Current index (499 rows, Wave 9 re-verified): Akamai holds 21
  of the 34 WALLED rows." After: "Current index (499 rows, Wave
  17 re-verified): Akamai holds 22 of the 35 WALLED rows." The
  change is webex.com's round-9 move OPEN → WALLED / Akamai
  (Wave 13); the count was re-verified by recounting the table
  this wave (Akamai 22, Cloudflare 5, AWS CloudFront 3, Imperva
  1, unattributed 4 = 35).
- **C-06 (DOGFOOD.md, suite-count chain).** Before: the file ended
  at Wave 8 (114 tests). After: appended the Waves 9–17 addendum
  (Wave 9: 120; Wave 10: 152; Wave 11: 183; Wave 12: 210; Wave 13:
  236; Wave 14: 270; Wave 15: 321; Wave 16: 375; Wave 17 battery:
  423, with round 13 noted as in progress — STABILITY-12
  completes the Wave 17 record).

## Verified current (no change needed)

- **INDEX.md distribution line.** Recounted from the table
  (including the two annotated rows, npmjs.com † and amazon.com
  ‡, which a naive row regex misses): OPEN 415 · CHALLENGED 25 ·
  WALLED 35 · RATE_LIMITED 7 · UNREACHABLE 17 · LOGIN_GATED 0 =
  499 rows. The line is exact.
- **INDEX.md notes † and ‡.** Both current through round 12
  (npmjs transport pattern, amazon/britishairways/forbes/webex
  oscillation records with Wave 15/16 updates).
- **Vendor list (README + SPEC).** Nine vendors, unchanged since
  Wave 5: Cloudflare, PerimeterX, DataDome, Akamai, Imperva,
  AWS WAF, Microsoft Azure WAF, Kasada, AWS CloudFront. Waves
  10–17 added rules, not vendors.
- **Adopter counts.** 4/499 stands (chatgpt.com, indeed,
  substack, ahrefs); Wave 16's spot-check (4/4 still publishing,
  chatgpt.com's window extended) is recorded in ADOPTER-SPOT.md
  and now reflected in SPEC's status line (C-03).
- **Own-properties grades.** clipwise D 5/12, portfolio F 3/12,
  Pages F 3/12, staged-deploy correction to C 7/12 (Wave 8) —
  unchanged since Wave 8; no re-audit has run since, so no doc
  claims otherwise.
- **campaign/LAUNCH-READINESS.md.** A point-in-time Wave 9 memo;
  its 499-site numbers and 4/499 adoption are still true, and its
  ship-needs (the ship call, the launch-post refresh) are still
  open. Not drift.
- **campaign/FRONT-DOORS.md.** "Seed edition, extended Wave 8"
  — no front-doors work has run since Wave 8, so the label is
  current.
- **campaign/WAR-PLAN.md.** The "500 targets" figure is a day-30
  target, not a claim of current size (see Observations).

## Intentional non-corrections

- **LAUNCH-POST.md's Wave 1 numbers.** Untouched per Wave 9's
  rule; refresh at ship.
- **Historical wave sentences** (e.g. README's v0.4 section
  describing the Wave 4 census "of all 154 index domains",
  SPEC's v0.5 section narrating through Wave 9). They describe
  their own wave, not the present; Wave 9's rule keeps them.
- **Historical test counts** in DOGFOOD.md's per-wave entries
  and SPEC's v0.2/v0.3 sections. They are the chain, not claims.

## Observations (not corrections)

- **Index at 499, one row short of the war plan's 500 target.**
  The next expansion wave closes it; no doc misstates the
  current size.
- **Round-13 measurement was in progress during this audit.**
  INDEX.md's distribution and narrative are current through
  round 12; STABILITY-12 (this wave's Leg A) is the record that
  moves them to round 13.
