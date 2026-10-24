# Wave 22 — Round-18 re-probe measuring the Wave 21 fixes (Leg A)

**500/500 rows probed once each** with the Wave 21-fixed
classifier — the measurement Wave 21's STABILITY-16 deferred.
The runner (`validation/wave22/run_round18.py`, written fresh
for round 18 with the round number in exactly one constant)
imported the Wave 21 tree at launch (before any Wave 22 battery
edit landed): all Wave 21 fixes were grep-verified present before
probing (W21-N1 object/embed routing species, W21-N2 "high
traffic" throttle cause, W21-N3 authenticator-app prompts,
W21-N6 non-HTTP-scheme sitemap loc rejection, W21-N7 TA/TE/MR/PA
phrases). The runner ran fully detached (setsid nohup,
resumable, monitored via its log) — no incident this wave: 500
new probes, zero missing URLs vs the INDEX table, zero
duplicate round-18 lines. All 500 history lines parse.

**Method note on fresh captures:** the round measured the Wave
21 tree, but fresh captures necessarily ran on the current
(Wave 22-fixed) tree. Every fresh capture therefore carries a
Wave 22-rule involvement check (SVG title/desc challenge
phrases, SSO buttons/links, GU/KN/NE/KM phrases). All 4 fresh
captures report zero involvement flags — the corroborations
below are tree-comparable. Fetch failures are tree-independent
(no response was classified).

Round-18 raw distribution: OPEN 415 · CHALLENGED 26 · WALLED 35 ·
RATE_LIMITED 7 · UNREACHABLE 17 · LOGIN_GATED 0 — identical to
standing before disposition, and identical after it.

## The 2 verdict diffs, both hand-checked with fresh captures

Every verdict diff was hand-checked with two fresh captures
(`validation/wave22/fresh_captures.py`, results in
`fresh-captures.json`) before merging — no diff was merged on
the round-18 reading alone. The strict rule: merge only on
round + 2 agreeing fresh readings; otherwise hold.

- **chicagotribune.com (OPEN → WALLED, HELD).** Round-18
  read a 403; both fresh captures read OPEN 200 with
  STATUS_200 evidence and zero Wave 22 involvement. The
  round's 403 was a transient refusal, overturned twice —
  the Wave 16 france24 pattern. Held at OPEN.
- **forbes.com (CHALLENGED / DataDome → OPEN, HELD).**
  Round-18 read a served 200; fresh captures split 1–1
  (one served 200 carrying a DataDome header, one 403
  DataDome challenge). Served-leaning 2–1 with no
  corroboration triple for either side, so the strict rule
  holds the row at its standing CHALLENGED / DataDome
  verdict. The oscillator record extends — this is the
  first served-leaning split in the oscillator's history
  (prior splits were challenged-leaning or even).

## Zero rows merged, zero fix-driven moves

- No row moved under the Wave 21 classifier rules.
- All ten Wave 20 merges agree with round 18 (claude.ai
  CHALLENGED/Cloudflare, amazon CHALLENGED/Generic, ed.gov
  CHALLENGED/Azure WAF, fda.gov OPEN, goodrx
  CHALLENGED/PerimeterX, irishjobs.ie / jobs.ie /
  totaljobs.com UNREACHABLE, jobrapido OPEN, ubereats
  CHALLENGED/Cloudflare).
- All spotlights hold: rubygems.org OPEN (the W17-007
  passkey fix holds), remoteok.com / td.com / venmo.com
  OPEN (no Wave 17 QR misfire recurs under the Wave 21
  tree), forbes.com held as above.

## Index state after round 18

Unchanged at 500 rows: OPEN 415 · CHALLENGED 26 · WALLED 35 ·
RATE_LIMITED 7 · UNREACHABLE 17 · LOGIN_GATED 0. Header
recount verified exact; the round-18 narrative is appended
to the header's round history. The Wave 22 battery fixes
are unmeasured on live traffic until round 19.
