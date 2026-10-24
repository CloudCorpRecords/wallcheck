# Docs spot-check 5 — Wave 27 (Leg C)

## DOGFOOD addendum for Waves 19–26 — DONE

`DOGFOOD.md`'s wave chain previously ended at the Wave 18
entry (extended in Wave 19). The Waves 19–26 addendum is now
appended in the same format — one entry per wave with its
round's merges and holds, its battery's defect families, its
test count, and the index distribution it left behind:

| Wave | Round | Battery | Suite after |
|---|---|---|---|
| 19 | 15: 6 merged, 4 held, 0 fix-driven | v11: 8 families | 532 |
| 20 | 16: 10 merged, 3 held, 0 fix-driven; LOGIN_GATED watch empties | v12: 3 families | 571 |
| 21 | 17: 0 merged, 4 held | v13: 5 families + 1 hand-correction | 608 |
| 22 | 18: 0 merged, 2 held; vendor re-audit 61/61 | v14: 3 families + 1 hand-correction | 638 |
| 23 | 19: 2 merged (both transport), 1 held | v15: 3 families + 1 hand-correction | 674 |
| 24 | 20: 2 merged, 1 held; 402 watch opened | v16: 3 families | 710 |
| 25 | 21: 3 merged — incl. the 402 pair, the first fix-driven moves since round 14; one 410 fix VETOED by a Wave 6 pin | v17: 3 families | 747 |
| 26 | 22: 2 merged, 1 held, 0 fix-driven; vendor shares refreshed, 3 report-card corrections | v18: 3 families | 788 |

The addendum also carries the standing facts a reader of the
chain needs: the index at 500 rows, the vendor shares as
recorded in `validation/wave26/VENDOR-SHARES.md` (with the
transparent note that round 22's two merges moved one row each
way between the Akamai and Cloudflare challenged/walled
cells), and FRONT-DOORS at **66 platforms** (40 VERIFIED /
20 NO ROUTE FOUND / 6 UNVERIFIED — verified against
`campaign/FRONT-DOORS.md` line 941 during this spot-check).
The file now holds 23 wave entries across 670 lines; the
append was verified by line count and tail read after writing,
and no staging copy remains.

## README.md — verified and updated

- The "New in 0.5.0-rc" test-count chain ended at Wave 24's
  710. It now continues through Wave 25 (747), Wave 26 (788),
  and Wave 27 (831) — each number is the wave's own verified
  pytest count, and 831 was re-run this wave (see below).
- The stability-rounds summary line read "Waves 10–26 ran
  seventeen more stability rounds (rounds 6–22)… 788 tests."
  It now reads "Waves 10–27 ran eighteen more stability rounds
  (rounds 6–23) and adversarial batteries v2–v19, took the
  suite to 831 tests, and kept the launch hold." Round 23 is
  this wave's Leg A; battery v19 is this wave's Leg B.
- No other README numbers were stale: the index distribution
  is not quoted in the README (it lives in INDEX.md, updated
  by Leg A), and the launch-hold language is unchanged.

## SPEC.md — verified and updated

- Status line (line 6–7): "hardened through Wave 26" →
  "hardened through Wave 27."
- The localized-challenge language list now ends "…plus
  Catalan, Estonian, Armenian, and Georgian (added Wave 26),
  plus Albanian, Icelandic, Kazakh, and Malayalam (added
  Wave 27)" — matching the W27-V7 fix exactly.
- The refinements chain gains the Wave 27 sentence: biometric
  sign-in prompts join the two-keyed auth barriers, with the
  prose-without-machinery boundary stated.
- The `robots_txt` bullet gains the Wave 27 product-token
  rule (a versioned token names the bare identifier's agent;
  a version-only token names no agent).
- The `llms_txt` bullet gains the Wave 27 comment rule (HTML
  comments stripped before content analysis; commented links
  and URLs are not index entries).
- Version stays **0.5.0-rc** with unreleased fixes: 0.5.0 was
  never released, so no new stamp is due until the launch
  decision, per the Wave 12 version note.

## Reality checks run for this spot-check

- Full suite: **831/831 via pytest** (788 + battery v19's 43),
  re-run after all Wave 27 fixes landed.
- Capture corpus regression: clean (44 captures, diff empty).
- Index: 500 rows; distribution after Leg A's round-23 merge
  **OPEN 415 · CHALLENGED 26 · WALLED 36 · RATE_LIMITED 7 ·
  UNREACHABLE 16 · LOGIN_GATED 0** (recount verified).
- MCP smoke: PASS on all three tools (initialize, tools/list
  = [probe_url, classify, audit], classify → CHALLENGED,
  probe_url example.com → OPEN, audit example.com → grade F,
  6 checks).
- LAUNCH-POST.md untouched, per the standing rule — its
  Wave 1 numbers are launch copy and refresh only at ship
  time.
