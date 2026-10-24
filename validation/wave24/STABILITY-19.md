# Wave 24 — Stability Round 20 (Leg A)

Round 20 re-probed all 500 index rows with the Wave 23-fixed
classifier (the runner imported the tree at launch, before any
Wave 24 battery edit landed — the established import discipline,
this time preserved across a mid-round service restart: the
runner died at 276/500, the three Wave 24 fixes were temporarily
reverted, verified absent by grep AND by the battery failing on
exactly the same 8 gaps again, the runner relaunched against
the pristine Wave 23 tree and resumed at 276, and only then was
the fixed file restored and hash-verified).

**Zero rows moved under the Wave 23 classifier rules.** Round
20 measured W23-Q1 (picture-block strip), W23-Q2 (418 refusal),
and W23-Q7 (EL/CS/HU/RO phrases) on live traffic with zero
live effect — the same verdict rounds 13, 17, 18, and 19
returned for their predecessor rules. At the status level: no
index row answered 418 or 451 in the round, and all six fresh
diff captures plus all four 402-watch captures carried
`w23_involvement: []` (no picture-block phrase, no
Greek/Czech/Hungarian/Romanian phrase).

**Three verdict diffs, all hand-checked with two fresh
captures each (strict corroboration), all tree-comparable
(`w24_involvement: []` on every fresh capture):**

| Row | Standing | Round 20 | Fresh ×2 | Disposition |
|-----|----------|----------|----------|-------------|
| wayfair.com | OPEN / 200 | CHALLENGED / PerimeterX / 429 | CHALLENGED/PX/429 ×2 | **MERGED → CHALLENGED / PerimeterX** |
| apnews.com | CHALLENGED / Cloudflare / 403 | UNREACHABLE | UNREACHABLE ×2 | **MERGED → UNREACHABLE** |
| britishairways.com | OPEN / 200 | UNREACHABLE | UNREACHABLE, OPEN/200 | **HELD OPEN** (1–1 split) |

- **wayfair.com** — the transient PerimeterX throttle held
  twice (rounds 16, 17) on overturning fresh readings is now
  the standing answer across three consecutive readings
  (round + 2 fresh, all 429 with PX_CAPTCHA evidence). The
  forbes/amazon precedent governs: a corroboration triple
  merges even a documented oscillator; a served triple would
  move it back.
- **apnews.com** — three consecutive fetch failures (round +
  2 fresh) retire the stale CHALLENGED row: the
  britishairways Wave 15 / ed.gov Wave 19 pattern. Its
  earlier transport-noise holds (rounds 12, 15, 17) were all
  splits or overturns; this round the failures corroborate.
- **britishairways.com** — 1–1 fresh split (one failure, one
  served 200): no corroboration triple for either side, the
  strict rule holds the row at OPEN. Its second split-hold
  (round 12 was the first, from the other side).

**Vendor-only diffs: zero.** The two analyzer-invisible rows
(npmjs.com †, amazon.com ‡ — note suffixes in the name cell)
were hand-checked from the raw results: npmjs read
CHALLENGED / Cloudflare / 403 directly (no connection drop —
the standing pattern breaks again), amazon read CHALLENGED /
Generic / 200; both agree with standing.

**The 402 watch (new, forward-looking).** Two rows answered
HTTP 402 in the round and read OPEN under the Wave 23 tree,
agreeing with their standing OPEN: telegraph.co.uk and
usatoday.com. Fresh scouting captures (`watch-402.json`,
2 each) read both as 402 with `STATUS_402` evidence →
WALLED under the Wave 24 tree, and body inspection confirms
both are small refusal stubs, not served articles
(telegraph: 1,028-byte "our security systems have detected
some unusual activity" refusal; usatoday: 254-byte "Access
Restricted" stub). No merge this round — round 20 measured
the Wave 23 tree — so both rows are round 21's expected
first fix-driven moves under W24-R2, to be judged by the
same fresh-capture protocol then.

**Distribution after merges (recount-verified against the
table):** OPEN 414 · CHALLENGED 26 · WALLED 35 ·
RATE_LIMITED 7 · UNREACHABLE 18 · LOGIN_GATED 0 (500 rows).
Net: wayfair OPEN→CHALLENGED, apnews CHALLENGED→UNREACHABLE.
