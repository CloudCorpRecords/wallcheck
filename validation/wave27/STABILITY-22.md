# Stability round 23 — Wave 27 (Leg A)

**Run:** 500/500 rows probed, single honest fetches, identified
wallcheck UA, no retries — `validation/wave27/results-round23.jsonl`;
round=23 appended to `validation/wave4/history.jsonl` (500 lines,
500 unique targets, no duplicates — verified). The runner
imported the tree at launch, before any Wave 27 battery edit
landed, so **the round measures the Wave 26 tree end to end**;
all three Wave 26 fixes were grep-verified present in the tree
before the launch (`_is_badge_tap_prompt` at classify.py:1982,
invoked at :1524, its `BADGE_TAP_PROMPT` branch at :1533; the
Catalan / Estonian / Armenian / Georgian phrases at
classify.py:358–373; the percent-in-host rejection in
`_has_nonempty_loc` at audit.py:392). The Wave 27 battery fixes
are unmeasured until round 24.

One process note, ledgered for honesty: a backgrounded watcher
process's result was rendered to the operator mid-round claiming
"500 new probes" while the results file held ~250 rows. Disk
verification disproved the rendering immediately; every analysis
step waited for the runner's own completion line and a verified
500-row file. No data was affected — the runner's fsync-per-line
ledger was correct throughout — but the incident is recorded
because this campaign trusts files, not renderings.

## Verdict movement

Four verdict diffs, **zero vendor-only diffs**. Every diff was
hand-checked with two fresh captures
(`validation/wave27/fresh-captures.json`). Every fresh capture
carried **zero Wave 26-rule involvement and zero Wave 27-rule
involvement** (no badge-tap prompt, no biometric prompt, no
Catalan / Estonian / Armenian / Georgian or Albanian /
Icelandic / Kazakh / Malayalam phrase), so every corroboration
below compares like with like. Dispositions:

| Row | Standing | Round 23 | Fresh captures | Disposition |
|---|---|---|---|---|
| forbes.com | CHALLENGED / DataDome / 403 | OPEN / 200 | OPEN 200, OPEN 200 — both carry the DataDome header (`DD_XDATADOME_HEADER`) while the page served | **MERGED → OPEN** |
| chicagotribune.com | OPEN / 200 | WALLED / 403 | OPEN 200, OPEN 200 | Held OPEN |
| hilton.com | WALLED / Akamai / 403 | UNREACHABLE (fetch failure) | WALLED / Akamai 403, WALLED / Akamai 403 (`AKAMAI_SERVER_HEADER` + `STATUS_403`) | Held WALLED |
| webex.com | OPEN / 200 | WALLED / Akamai / 403 | WALLED / Akamai 403 (edgesuite deny), OPEN 200 | Held OPEN (1–1 split) |

- **forbes.com → OPEN is the round's only merge**, and it is
  target-side oscillation meeting the corroboration bar, not a
  rule move. Forbes has been the index's documented intermittent
  oscillator since round 11: held OPEN through rounds 11–13 on
  splits, merged CHALLENGED in round 15 (Wave 19) on the first
  challenge triple, held CHALLENGED in rounds 18 and 22 on
  splits and agreeing challenges. Round 23 plus two agreeing
  fresh served readings is the **served triple** the row's
  earlier splits never met, so the strict rule moves it back.
  Both fresh captures carry DataDome's header — the vendor is
  present on the property; it is simply not challenging this
  client right now. A challenge triple would move it back
  again, and the index makes no promise it won't.
- **chicagotribune.com** repeats its round-18 pattern exactly: a
  single round 403 against two agreeing fresh served readings.
  Transient refusal; held OPEN.
- **hilton.com**'s round reading was a fetch failure with no
  response to classify; two fresh captures agree with the
  standing Akamai 403. Transport noise on the round's side;
  held WALLED.
- **webex.com** split its fresh captures — one edgesuite deny,
  one served reading — three rounds after its standing Akamai
  wall lifted in round 22. A 1–1 split holds the row under the
  strict rule; the deny is noted, and a WALLED triple in a
  future round would move it back.

## Fix-driven movement: zero

No row moved under the Wave 26 classifier rules. The round ran
the Wave 26 tree; every diff was checked for Wave 26-rule
involvement in its fresh evidence (badge-tap prompt, CA/ET/HY/KA
phrase) and none carried any. The third Wave 26 fix — percent-
encoded sitemap host rejection — is audit-side and cannot act
on a homepage capture, so it is untestable by this leg; battery
v18's Q-family pins remain its evidence. **The Wave 26 fixes
measured zero live effect in round 23**, the same outcome rounds
19–22 recorded for their predecessors; the rules stand on their
battery fixtures.

## The annotated pair

npmjs.com read CHALLENGED / Cloudflare / 403 and amazon.com
read CHALLENGED / Generic / 200 in the round itself — both
agree with standing, no fresh captures needed. npmjs's
transport pattern (connection drops in rounds 12–21) did not
recur; amazon's ‡ oscillation continues to sit on the
challenged side.

## Bookkeeping

- Merged: 1 (forbes.com). Held: 3. Vendor-only diffs: 0.
- Index distribution after the merge: **OPEN 415 · CHALLENGED
  26 · WALLED 36 · RATE_LIMITED 7 · UNREACHABLE 16 ·
  LOGIN_GATED 0** (500 rows; recount verified against the
  merged file).
- Round-23 raw distribution before dispositions: OPEN 413 ·
  WALLED 37 · CHALLENGED 26 · UNREACHABLE 17 · RATE_LIMITED 7.
  The two-point gap to standing is exactly the held rows
  (chicagotribune, hilton, webex) minus the merged forbes move.
- Saturation bookkeeping: round 23 is the twentieth consecutive
  round with **zero fix-driven moves** apart from round 21's
  two (W24-R2). A stability round alone can never satisfy the
  saturation test's clean-wave condition — that turns on the
  battery, and battery v19 found four genuine defect families
  (see PROBLEMS.md). The clean clock stays reset.
