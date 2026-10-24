# Wave 12 — Round-8 re-probe measuring the Wave 11 fixes (Leg A)

**499/499 rows probed once each** with the CURRENT Wave 11-fixed
classifier — the measurement Wave 11's STABILITY-6 deferred. The
runner (`validation/wave12/run_round8.py`, incremental + resumable
saves to `validation/wave4/history.jsonl` as round=8 and to
`validation/wave12/results-round8.jsonl`) started AFTER the Wave 11
fixes were verified present in the tree (W11-001 form-action
redirect targets, W11-002 "verify your request" phrasing, W11-003
Turnstile-loader-only login yield, W11-004 IT/NL/KO localized
phrases, W11-005 Generic nulling on LOGIN_GATED, W11-006 robots
wildcard FAIL semantics — all confirmed by grep before launch).
All 499 history lines parse; zero missing URLs vs the INDEX table.

Round-8 raw distribution: OPEN 414 · CHALLENGED 25 · WALLED 34 ·
RATE_LIMITED 7 · UNREACHABLE 18 · LOGIN_GATED 1 — identical to the
merged distribution, because every raw diff was dispositioned
below and the merges equal the raw readings.

## Raw diffs vs the standing table: 4, dispositioned

Every diff was hand-checked with a fresh capture before merging —
no diff was merged on the round-8 reading alone.

| target | standing | round 8 | fresh capture | disposition |
| --- | --- | --- | --- | --- |
| www.amazon.com | OPEN 200 | CHALLENGED / Generic 200 | CHALLENGED / Generic 200 (GENERIC_CAPTCHA + REDIRECT_TO_CHALLENGE) | MERGED to CHALLENGED. Target-side oscillation, NOT fix-driven: the interstitial page is the same specimen the Wave 6 S2c record describes (its captcha signal is the quoted form action), which the pre-Wave-11 classifier also reads as CHALLENGED — round 7's two OPEN readings meant the interstitial sat out, not that the old rules missed it. Note ‡ extended. |
| www.britishairways.com | OPEN 200 | UNREACHABLE (fetch error) | UNREACHABLE (TimeoutError, twice) | MERGED to UNREACHABLE. Transport oscillation, following the Wave 10/11 precedent exactly (two agreeing readings decide, in either direction): timed out R6, served R7, timed out R8 ×2. A timeout is not a wall verdict, but the index records the latest corroborated reading. |
| www.npmjs.com | CHALLENGED / Cloudflare | UNREACHABLE (fetch error) | CHALLENGED / Cloudflare 403 (cf-mitigated + Just a moment + challenge platform) | HELD at CHALLENGED. The round-8 UNREACHABLE is the known RemoteDisconnected transport pattern (sixth sighting counting the Wave 4 census); the fresh capture serves the real challenge, so posture is not in doubt. Transport noise is not a posture change. |
| www.webex.com | OPEN 200 | WALLED / Akamai 403 | OPEN 200 (STATUS_200, no wall evidence) | HELD at OPEN. Single uncorroborated Akamai 403 against a fresh OPEN: by the Wave 10 fresh-capture-decides rule the fresh capture wins, and a lone edge deny does not move a row. Recorded here as a single sighting; a second sighting moves it. |

## Fix-driven moves: exactly zero

Of the six Wave 11 rule families this round was built to
re-measure, none moved a live row:

- **Form-action redirect targets (W11-001) — 0 moves.** No live
  row's verdict changed; the amazon.com move is target-side
  oscillation (see above), not the new rule.
- **"Verify your request" phrasing (W11-002) — 0 moves.** No live
  row serves that stub wording.
- **Turnstile-loader-only login yield (W11-003) — 0 moves.** No
  live login row carries a loader-only signal set.
- **IT/NL/KO localized phrases (W11-004) — 0 moves.** No live row
  serves an Italian, Dutch, or Korean challenge page.
- **Generic nulling on LOGIN_GATED (W11-005) — 0 verdict moves, by
  design.** The rule changes the vendor field only; the single
  standing LOGIN_GATED row (merrilledge.com) already shows vendor
  Akamai (presence attribution), not Generic.
- **Robots wildcard FAIL semantics (W11-006) — audit tool, not
  the index.** No index row is an audit grade.

That is itself a finding, and it cuts both ways: the Wave 11 fixes
were validated against all 499 live rows and not one row was
actually misclassified under the old rules — the same shape of
result Wave 11 reported for the Wave 10 fixes. The fixes are
correctness insurance for shapes the live web has not yet shown
this index, proven by fixtures, unexercised by traffic.

## Merge result

**Two rows changed:** amazon.com OPEN → CHALLENGED, britishairways.com
OPEN → UNREACHABLE. New INDEX distribution: OPEN 414 · CHALLENGED 25 ·
WALLED 34 · RATE_LIMITED 7 · UNREACHABLE 18 · LOGIN_GATED 1 (499
rows, recount verified). The merged distribution equals the round-8
raw distribution exactly, because the two held rows (npmjs, webex)
were held AT their round-8-contradicting standing values only after
fresh captures corroborated the standing values — the same
fresh-capture-decides rule that merged the other two.
