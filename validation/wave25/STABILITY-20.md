# Wave 25 — Stability Round 21 (Leg A)

Round 21 re-probed all 500 index rows with the Wave 24-fixed
classifier (the runner imported the tree at launch, before any
Wave 25 battery edit landed — the established import discipline,
no incident this round: 500 new probes, zero missing URLs,
zero duplicate round-21 lines; history carries exactly 500
round-21 lines).

**Two rows moved under the Wave 24 classifier rules — the
first fix-driven moves since round 14's single move.** Both
are the 402 watch pair Wave 24's STABILITY-19 flagged forward:
telegraph.co.uk and usatoday.com answered 402 in round 20 and
read OPEN under the Wave 23 tree (no 402 branch — the W24-R2
fallthrough); in round 21, under the Wave 24 tree, the same
402 answers read WALLED, and two fresh captures each agree.

**Four verdict diffs, all hand-checked with two fresh
captures each (strict corroboration), all tree-comparable
(`w25_involvement: []` on every fresh capture):**

| Row | Standing | Round 21 | Fresh ×2 | Disposition |
|-----|----------|----------|----------|-------------|
| telegraph.co.uk | OPEN / 402 | WALLED / 402 | WALLED/402 ×2 (STATUS_402) | **MERGED → WALLED** — fix-driven (W24-R2) |
| usatoday.com | OPEN / 402 | WALLED / 402 | WALLED/402 ×2 (STATUS_402) | **MERGED → WALLED** — fix-driven (W24-R2) |
| todoist.com | UNREACHABLE | OPEN / 200 | OPEN/200 ×2 | **MERGED → OPEN** (recovery) |
| britishairways.com | OPEN / 200 | UNREACHABLE | OPEN/200 ×2 | **HELD OPEN** (fresh readings overturn the round failure) |

- **telegraph.co.uk / usatoday.com** — round + 2 agreeing
  fresh 402 readings, `w24_involvement: ["status-402"]` on
  every capture: the moving rule is W24-R2 itself, so both
  merges are fix-driven by construction, judged by the same
  fresh-capture protocol as every other merge. The bodies
  remain the small refusal stubs Wave 24 inspected
  (telegraph's security-refusal page, usatoday's "Access
  Restricted" stub) — target-side posture unchanged; only
  the reading of it is new.
- **todoist.com** — three consecutive served readings (round
  + 2 fresh) retire the stale UNREACHABLE row: the mirror of
  its own round-19 failure merge, and of britishairways'
  round-10 recovery. Target-side.
- **britishairways.com** — two agreeing fresh served readings
  overturn the round's single transport failure: the Wave 14
  hold pattern (and the mirror of its round-20 split-hold).
  The row stays OPEN; its transport oscillation is documented
  across rounds 11–21 and is not posture.

**The other two Wave 24 fixes measured zero live effect:**
no fresh capture and no round row carried a push-approval
prompt or a Bulgarian/Slovak/Croatian/Slovenian phrase
(`w24_involvement` empty everywhere except the 402 pair).

**Vendor-only diffs: zero.** The two analyzer-invisible rows
(npmjs.com †, amazon.com ‡) were hand-checked from the raw
results: npmjs read CHALLENGED / Cloudflare / 403 directly
(no connection drop), amazon read CHALLENGED / Generic / 200;
both agree with standing.

**Distribution after merges (recount-verified against the
table):** OPEN 413 · CHALLENGED 26 · WALLED 37 ·
RATE_LIMITED 7 · UNREACHABLE 17 · LOGIN_GATED 0 (500 rows).
Net: telegraph OPEN→WALLED, usatoday OPEN→WALLED, todoist
UNREACHABLE→OPEN.
