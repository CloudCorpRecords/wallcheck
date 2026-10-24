# Wave 28 — LAUNCH-READINESS refresh record (Leg C)

`campaign/LAUNCH-READINESS.md` was written in Wave 9 and never
updated since; by Wave 28 its state sections were nineteen
waves stale (it cited 120 tests, a 499-site index, 65
front-doors platforms, and Wave 9's borderline saturation
candidacy). This leg rewrote the state sections to current
reality while keeping the memo's structure (proven / not
proven / what the ship decision needs) and its ship-decision
framing verbatim in form. `campaign/LAUNCH-POST.md` was NOT
touched — its Wave 1 numbers are launch copy and refresh only
at ship time, per the standing rule.

## What changed (Wave 9 state → Wave 28 state)

- **Header:** "(0.5.0-rc, Wave 9)" → "(0.5.0-rc, Wave 28)",
  with a refresh note pointing at this record.
- **Classifier proof:** 120 tests → **885 tests, all green via
  pytest** (Wave 28 count, battery v20 included); "8 waves of
  live captures" → twenty adversarial batteries (Waves 6,
  10–28), 24 stability rounds, and the clean 44-capture corpus
  regression; localized list now 59 language groups.
- **Index proof:** 499 sites with the Wave 9 distribution →
  **500 sites, OPEN 415 · CHALLENGED 26 · WALLED 36 ·
  RATE_LIMITED 7 · UNREACHABLE 16 · LOGIN_GATED 0**; the
  stability record now runs to round 24, with the oscillators'
  split histories named (forbes, amazon, npmjs).
- **Census proof:** "4 of 499" → **4 of 500**, with the full
  spot-check drift record added (all four publishing with
  byte-identical keys at Waves 16, 20, and 23; chatgpt.com's
  expiry drifted forward on all three spot-checks; ahrefs
  never gained purpose/window metadata).
- **Vendor shares (new proof bullet):** the Wave 26 recomputed
  shares (WALLED 37: Akamai 22, Cloudflare 5, unattributed
  bare-403 4, AWS CloudFront 3, unattributed 402 pair 2,
  Imperva 1; CHALLENGED 26: DataDome 15, Cloudflare 5,
  PerimeterX 3, AWS WAF 1, Azure WAF 1, Generic 1), with the
  honest note that round 23 has since moved one CHALLENGED
  row to OPEN, and that the report cards were corrected
  against these shares in Wave 26 (grades untouched).
- **Campaign pack:** front-doors 65 → **66 platforms**
  (40 VERIFIED / 20 NO ROUTE FOUND / 6 UNVERIFIED, the Wave
  27 count).
- **MCP proof:** re-verified in Wave 28 (smoke PASS on all
  three tools), citation updated.
- **Unproven list:** own-properties D/F/F, Ed25519
  non-constant-time, single-client measurement, unconsulted
  signatures, and 0.8% adoption all carried forward — every
  one re-verified still true (the deploys are still
  undeployed; the census count is still 4). Adoption restated
  as 4 of 500. **New unproven item:** the classifier has
  never saturated — every battery from Wave 10 to Wave 28
  found 3–21 genuine defect families, the two-clean-wave
  pair never completed, and the index has simultaneously
  been essentially still for seven rounds (0, 2, 2, 3, 2, 1,
  0 merges in rounds 18–24, exactly two fix-driven). Both
  halves are stated; neither is smoothed.
- **Ship-decision section:** unchanged in substance — the
  same three items (the ship call, the launch-post refresh,
  optionally the own-property deploys first). The candidate
  identity now reads 0.5.0-rc carrying the unreleased Waves
  10–28 fixes, folding into the **0.5.0 final** stamp at
  release per the Wave 12 version note.
- **Saturation section:** rewritten from Wave 9's borderline
  candidacy to the final verdict: **NOT MET after 28 waves**,
  with the clock standing reset at the end of the five-wave
  authorization and the narrower, stronger claim the ledger
  does support (a reproducible 500-site verdict table, every
  known defect class fixture-pinned, remaining finds new
  species in known families).
