# Wave 16 — Round-12 re-probe measuring the Wave 15 fixes (Leg A)

**499/499 rows probed once each** with the Wave 15-fixed
classifier — the measurement Wave 15's STABILITY-10 deferred.
The runner (`validation/wave16/run_round12.py`, written fresh
for round 12 rather than sed-derived, with the round number in
exactly one constant) imported the Wave 15 tree at launch: all
ten Wave 15 fixes were grep-verified present before probing
(W15-001 ld+json strip, W15-002 REFUSAL_PHRASE, W15-003
visible-text phrase scan, W15-004 invisible-widget
suppression, W15-005 Refresh-header routing, W15-006
CODE_ENTRY_FORM, W15-007 footer-badge blanking, W15-008
robots Allow tiebreak, W15-009 frontmatter strip, W15-010
SITEMAP_NO_URLS). All 499 history lines parse; zero missing
URLs vs the INDEX table; zero duplicate round-12 lines. The
launch guard was verified live: after the first minutes the
runner had written 61 lines to both `history.jsonl` and
`results-round12.jsonl` — no sed-trap no-op this wave.

**Tree note (stated plainly, as Wave 11's note did):** the
runner imported its classifier at launch, before the Wave 16
battery fixes landed — so round 12 measures the Wave 15 tree,
exactly as this wave's task specified. The Wave 16 fixes
(data-attribute/style suppression, Location-header routing,
passkey/magic-link signals, BOM-tolerant frontmatter, JSON
generalization, the concatenated-text variant) are unmeasured
on live traffic until round 13.

Round-12 raw distribution: OPEN 414 · CHALLENGED 24 · WALLED 36 ·
RATE_LIMITED 7 · UNREACHABLE 18 · LOGIN_GATED 0.

## Raw diffs vs the standing table: 9, of which 4 are not diffs

Four rows differ only in vendor-cell wording: catho.com.br,
haaretz.com, hyatt.com, and state.gov stand as WALLED with the
cell note "unattributed (bare 403)" while the round reports
vendor None — the same verdict (WALLED) and the same absence
of a vendor, written two ways. No row changes, no fresh
capture needed: a wording difference is not a verdict
difference.

## The 5 verdict diffs, all hand-checked with fresh captures

Every verdict diff was hand-checked with two fresh captures
(`validation/wave16/fresh_captures.py`) before merging — no
diff was merged on the round-12 reading alone.

| target | standing | round 12 | fresh capture(s) | disposition |
| --- | --- | --- | --- | --- |
| www.npmjs.com | CHALLENGED / Cloudflare | UNREACHABLE (fetch failed) | UNREACHABLE (RemoteDisconnected) + CHALLENGED / Cloudflare 403 | HELD at CHALLENGED. The round's failure is the known transport pattern (7th sighting); one fresh reading serves the standing challenge. Transport noise is not a posture change. NOT fix-driven: a fetch failure involves no classifier rule. |
| apnews.com | CHALLENGED / Cloudflare | UNREACHABLE (fetch failed) | CHALLENGED / Cloudflare 403 + UNREACHABLE (RemoteDisconnected) | HELD at CHALLENGED. Same pattern as npmjs, first transport-noise sighting for apnews: the fresh challenge corroborates the standing wall; the round's failure is noise. NOT fix-driven. |
| www.france24.com | OPEN 200 | WALLED / Akamai 403 | OPEN 200, twice | HELD at OPEN. The round's single Akamai 403 is overturned by two agreeing served readings — a first single-attempt wall sighting for france24, flagged for re-check next round. NOT fix-driven: no Wave 15 rule touches Akamai 403 detection. |
| www.forbes.com | OPEN 200 | CHALLENGED / DataDome 403 | OPEN 200, twice (DataDome header presence only) | HELD at OPEN. The round's challenge is overturned by two agreeing served readings; the oscillator record extends (Wave 15's 2–2 split, now a round-12 challenge plus two fresh served readings). NOT fix-driven: no Wave 15 rule touches DataDome detection. |
| www.britishairways.com | UNREACHABLE | OPEN 200 | UNREACHABLE (timeout) + OPEN 200 | HELD at UNREACHABLE. The closest call of the wave: fresh evidence splits 1–1, so no corroboration triple exists for either side (round + 2 agreeing fresh is the merge bar, met by neither). The standing row holds on the strict rule; the served-leaning evidence (round + 1 fresh served vs 1 fresh failure) is noted for round 13. NOT fix-driven: a fetch outcome involves no classifier rule. |

## Fix-driven moves: exactly zero

Sixth consecutive round with zero fix-driven moves (Waves 11,
12, 13, 14, 15, 16). Of the Wave 15 rule families this round
was built to re-measure, none moved a live row:

- **JSON data-block strip (W15-001) — 0 moves.** No live
  row's verdict depended on a JSON-LD vendor marker.
- **Refusal phrase (W15-002) — 0 moves.** No live row serves
  a small-page "access denied" stub.
- **Visible-text phrase scan (W15-003) — 0 moves.** No live
  row's verdict depended on a split-markup phrase.
- **Invisible-widget suppression (W15-004) — 0 moves.** No
  live row carries an invisible widget on served content.
- **Refresh-header routing (W15-005) — 0 moves.** No live row
  routes via a Refresh header.
- **Code-entry form (W15-006) — 0 moves.** No live row serves
  a 2FA code form at a non-login URL.
- **Footer-badge blanking (W15-007) — 0 moves.** No live row
  carries a badge phrase as its only marker.
- **Robots tiebreak, frontmatter strip, sitemap loc rule
  (W15-008/009/010) — audit tool, not the index.** No index
  row is an audit grade.

The Wave 10–15 fixes remain correctness insurance for shapes
live traffic has not shown this index, proven by fixtures,
unexercised by traffic. (The Wave 16 battery fixes, which
landed after this round, are measured by round 13.)

## Merge result

**Zero rows changed.** INDEX distribution unchanged: OPEN 415 ·
CHALLENGED 25 · WALLED 35 · RATE_LIMITED 7 · UNREACHABLE 17 ·
LOGIN_GATED 0 (499 rows, recount verified). The merged
distribution differs from the round-12 raw distribution by
exactly five holds (the five verdict diffs above); the four
vendor-wording rows were never diffs.
