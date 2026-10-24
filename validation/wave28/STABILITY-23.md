# Stability round 24 — Wave 28 (Leg A)

**Run:** 500/500 rows probed, single honest fetches, identified
wallcheck UA, no retries — `validation/wave28/results-round24.jsonl`;
round=24 appended to `validation/wave4/history.jsonl` (exactly
500 lines, 500 unique targets, no duplicates — verified against
history after the run). The runner imported the tree at launch,
before any Wave 28 battery edit landed, so **the round measures
the Wave 27 tree end to end**; all four Wave 27 fixes were
grep-verified present in the tree before the launch (W27-V3
`_is_biometric_prompt` at classify.py:2046 with its branch at
:1555; W27-V4 versioned robots tokens at audit.py:145; W27-V5
llms HTML-comment strip at audit.py:282/:330; W27-V7 SQ/IS/KK/ML
phrases at classify.py:377–393). The Wave 28 battery fixes are
unmeasured until a future round. Completion was verified from
the runner's own completion line ("round 24 complete: 500 new
probes") and the on-disk line counts, per the Wave 27 lesson —
no watcher rendering was trusted at any point. No process
incident this wave; the runner ran detached and resumable
throughout.

## Verdict movement

**Zero verdict diffs across the 498 regex-visible rows, zero
rows merged.** The standing table's two annotated rows — the
analyzer-invisible pair every wave checks by hand — split: 
amazon.com read CHALLENGED / Generic / 200 in the round itself,
agreeing with standing, no captures needed. npmjs.com read
UNREACHABLE (status null, a fetch failure) against its standing
CHALLENGED / Cloudflare / 403, and was hand-checked with two
fresh captures (`validation/wave28/fresh-captures.json`):

| Row | Standing | Round 24 | Fresh captures | Disposition |
|---|---|---|---|---|
| www.npmjs.com | CHALLENGED / Cloudflare / 403 | UNREACHABLE (fetch failure) | CHALLENGED / Cloudflare 403 (`CF_MITIGATED_CHALLENGE`), UNREACHABLE (fetch failure) | Held CHALLENGED |

- **npmjs.com held CHALLENGED.** The fresh captures split 1–1:
  one is a full Cloudflare challenge response (the standing
  posture, answering normally), the other is the connection
  failure the round also saw. Under the strict corroboration
  rule there is no triple for either side — the round plus one
  fresh failure is two failures, the standing verdict plus one
  fresh challenge is two challenges — so the row holds. This is
  the **eleventh sighting** of npmjs's transport pattern
  (connection drops recorded since round 5; numbered sightings
  ran 6th in round 8 through 10th in round 17, with direct
  CHALLENGED readings in rounds 10, 11, 19, 20, 22, and 23 in
  between). The pattern is the site's delivery behavior toward
  this client, not a posture change: whenever npmjs answers at
  all, it answers with the Cloudflare challenge.
- Both fresh captures carried **zero Wave 27-rule involvement
  and zero Wave 28-rule involvement** (no biometric prompt, no
  SQ/IS/KK/ML phrase, no Windows PIN prompt, no MY/SI/AM/AZ
  phrase, no ARIA modal container), so the corroboration
  compares like with like across the two trees.

## Vendor-only diffs

Four, all the standing wording difference recorded since Wave
13: www.catho.com.br, www.haaretz.com, www.hyatt.com, and
www.state.gov stand in the table as "unattributed (bare 403)"
while the probe returns vendor None — same WALLED verdict,
same 403 status. The cell text is the campaign's ledgered
annotation, not a measurement change; no cell was edited.
(Wave 22's vendor re-audit confirmed all four as bare 403s
with no signature for the third time.)

## Fix-driven movement: zero

No row moved under the Wave 27 classifier rules. The round ran
the Wave 27 tree; the only diff's fresh evidence carried no
Wave 27 shape, and no other row's reading changed at all. Of
the four Wave 27 fixes, two are audit-side (W27-V4 versioned
robots tokens, W27-V5 llms comment strip) and cannot act on a
homepage capture, so they are untestable by this leg; battery
v19's V4/V5 pins remain their evidence. **The Wave 27 fixes
measured zero live effect in round 24**, the same outcome
rounds 19–23 recorded for their predecessors; the rules stand
on their battery fixtures.

## Bookkeeping

- Merged: 0. Held: 1 (npmjs.com). Vendor-only diffs: 4 (all
  the standing bare-403 annotation wording).
- Index distribution unchanged: **OPEN 415 · CHALLENGED 26 ·
  WALLED 36 · RATE_LIMITED 7 · UNREACHABLE 16 · LOGIN_GATED
  0** (500 rows; the header chain in INDEX.md gains the
  round-24 parenthetical; no row line was edited).
- Round-24 raw distribution: OPEN 415 · CHALLENGED 25 ·
  WALLED 36 · RATE_LIMITED 7 · UNREACHABLE 17. The one-point
  gap to standing is exactly the held npmjs row.
- Saturation bookkeeping: round 24 is the twenty-first
  consecutive round with **zero fix-driven moves** apart from
  round 21's two (W24-R2). A stability round alone can never
  satisfy the saturation test's clean-wave condition — that
  turns on the battery, and battery v20 found three genuine
  defect families (see PROBLEMS.md). The clean clock stays
  reset.
