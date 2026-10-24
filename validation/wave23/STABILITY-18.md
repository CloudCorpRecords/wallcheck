# Wave 23 — Round-19 re-probe measuring the Wave 22 fixes (Leg A)

**500/500 rows probed once each** with the Wave 22-fixed
classifier — the measurement Wave 22's STABILITY-17 deferred.
The runner (`validation/wave23/run_round19.py`, written fresh
for round 19 with the round number in exactly one constant)
imported the Wave 22 tree at launch (before any Wave 23
battery edit landed): all Wave 22 fixes were grep-verified
present before probing (W22-P1 `_SVG_META_RE`, W22-P2 the
451 branch, W22-P3 `_is_sso_prompt`, W22-P7 the GU/KN/NE/KM
phrases). The runner ran fully detached (setsid nohup,
resumable, monitored via its log) — no incident this wave:
500 new probes, zero missing URLs vs the INDEX table, zero
duplicate round-19 lines. All 500 history lines parse.

**Method note on fresh captures:** the round measured the
Wave 22 tree, but fresh captures necessarily ran on the
current (Wave 23-fixed) tree. Every fresh capture therefore
carries TWO involvement checks: Wave 23 rules (status 418,
picture text nodes carrying a phrase, EL/CS/HU/RO phrases —
whether the corroboration is tree-comparable) and Wave 22
rules (SVG title/desc phrase, SSO machinery, GU/KN/NE/KM
phrase, status 451 — whether the move could be fix-driven).
All 6 fresh captures report zero Wave 23 involvement, so the
corroborations below are tree-comparable. Fetch failures are
tree-independent (no response was classified).

Round-19 raw distribution: OPEN 416 · CHALLENGED 26 ·
WALLED 34 · RATE_LIMITED 7 · UNREACHABLE 17 · LOGIN_GATED 0.
Three verdict diffs (the two annotated rows, npmjs.com † and
amazon.com ‡, both read agreeing with standing — npmjs
CHALLENGED / Cloudflare on a direct 403, no connection drop
this round; amazon CHALLENGED / Generic), zero vendor-only
diffs. All three diffs were hand-checked with two fresh
captures each (`validation/wave23/fresh_captures.py`,
results in `fresh-captures.json`) before merging — no diff
was merged on the round-19 reading alone. The strict rule:
merge only on round + 2 agreeing fresh readings; otherwise
hold.

## The 3 verdict diffs: 2 merged, 1 held

- **britishairways.com (UNREACHABLE → OPEN, MERGED).**
  Round-19 read a served 200; both fresh captures read
  OPEN 200 (Akamai server header only, zero involvement).
  The corroboration triple is met, so the row merges to
  OPEN — the mirror of its Wave 15 merge: round 11 plus
  two agreeing failures retired it, round 19 plus two
  agreeing served readings recover it. The row oscillates
  on transport, not posture.
- **todoist.com (OPEN → UNREACHABLE, MERGED).** Round-19's
  fetch failed; both fresh captures also failed (fetch
  failures are tree-independent — no response was
  classified in any of the three). Three consecutive
  failures retire a stale served row: the britishairways
  Wave 15 / ed.gov Wave 19 pattern, applied to a row that
  has stood OPEN since its Wave 14 merge.
- **webex.com (WALLED / Akamai → OPEN, HELD).** Round-19
  read a served 200; the fresh captures split 1–1 — one
  403 edgesuite deny (WALLED / Akamai, zero involvement),
  one served 200 carrying an `sso-mention` Wave 22 flag.
  No corroboration triple for either side, so the strict
  rule holds the row at WALLED / Akamai — its second
  split-hold (Wave 20 held it the same way). The
  sso-mention is noted, not determinative: the W22-P3
  rule fires LOGIN_GATED only on a small prompt page, and
  this served page read OPEN under both trees — the deny
  simply sat this reading out. Target-side intermittency,
  not a rule move.

## Zero fix-driven moves

- No row moved under the Wave 22 classifier rules. The
  two merges are transport events in opposite directions
  (a recovery and a failure streak); the one candidate
  shape on a diff row (webex's sso-mention) is
  non-determinative for the reason above.
- No index row answered 418 or 451 in round 19, and no
  fresh capture carried a GU/KN/NE/KM phrase or an
  SVG-metadata phrase: the Wave 22 fixes are measured on
  live traffic with zero live effect.
- Spotlights hold: rubygems.org OPEN (the W17-007
  passkey fix holds), remoteok.com / td.com / venmo.com
  OPEN (no QR misfire recurs), forbes.com CHALLENGED /
  DataDome holds its Wave 19 merge, all ten Wave 20
  merges agree with round 19.

## Index state after round 19

500 rows: OPEN 415 · CHALLENGED 26 · WALLED 35 ·
RATE_LIMITED 7 · UNREACHABLE 17 · LOGIN_GATED 0 — the two
merges cancel (one OPEN gained, one OPEN lost), so the
distribution is identical to standing, verified by a full
recount (498 plain rows + the 2 annotated rows). The
round-19 narrative is appended to the header's round
history. The Wave 23 battery fixes are unmeasured on live
traffic until round 20.
