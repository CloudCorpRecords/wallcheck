# Wave 20 — Round-16 re-probe measuring the Wave 19 fixes (Leg A)

**500/500 rows probed once each** with the Wave 19-fixed
classifier — the measurement Wave 19's STABILITY-14 deferred.
The runner (`validation/wave20/run_round16.py`, written fresh
for round 16 with the round number in exactly one constant)
imported the Wave 19 tree at launch (process start 12:23:43
UTC, before any Wave 20 battery edit landed — classify.py
edits at 12:26:35 UTC): all Wave 19 fixes were grep-verified
present before probing (W19-001 template-block strip, W19-002
alt-join phrase scan, W19-003 EMAIL_CONTINUE_PROMPT, W19-004
sitemap usability test, W19-005 CR-only frontmatter
normalization, W19-006 fragment-only loc rejection, W19-007
HE/FA/UR/BN phrases, W19-008 native <dialog open> challenge
loop). The runner ran fully detached (setsid nohup, resumable,
monitored via its log) — no incident this wave: 500 new
probes, zero missing URLs vs the INDEX table, zero duplicate
round-16 lines. All 500 history lines parse.

**Method note on fresh captures:** the round measured the
Wave 19 tree, but fresh captures necessarily ran on the
current (Wave 20-fixed) tree. Every fresh capture therefore
carries a Wave 20-rule involvement check (iframe sources to
login/challenge targets, localized JS-proof phrases, UK/HI/MS/
TL/SW phrases, REDIRECT_TO_CHALLENGE evidence). All 26 fresh
captures report zero determinative Wave 20 involvement — the
one flag, on goodrx.com, is non-determinative (see below) —
so the corroborations below are tree-comparable. Fetch
failures are tree-independent (no response was classified).
One runner discovery, same family as Wave 16's: probe_url does
not return the body, so the fresh-capture script uses
fetch_raw + classify.

Round-16 raw distribution: OPEN 414 · CHALLENGED 26 · WALLED 35 ·
RATE_LIMITED 7 · UNREACHABLE 18 · LOGIN_GATED 0.

## The 13 verdict diffs, all hand-checked with fresh captures

Every verdict diff was hand-checked with two fresh captures
(`validation/wave20/fresh_captures.py`, results in
`fresh-captures.json`) before merging — no diff was merged on
the round-16 reading alone. The strict rule: merge only on
round + 2 agreeing fresh; a 1–1 fresh split holds the row.

| target | standing | round 16 | fresh capture(s) | disposition |
| --- | --- | --- | --- | --- |
| claude.ai | LOGIN_GATED / Cloudflare | CHALLENGED / Cloudflare 403 | CHALLENGED / Cloudflare 403, twice | **MERGED to CHALLENGED / Cloudflare.** Round + 2 agreeing challenges — the Wave 18 login gate is replaced by a wall, target-side. NOT fix-driven: no Wave 19 rule touches a CF 403 challenge. |
| www.amazon.com | OPEN 200 | CHALLENGED / Generic 200 | CHALLENGED / Generic 200, twice | **MERGED to CHALLENGED / Generic.** Round + 2 agreeing interstitial readings — the oscillator returns; note ‡ extends (a served triple would move it back). NOT fix-driven. |
| www.ed.gov | UNREACHABLE | CHALLENGED / Microsoft Azure WAF 403 | CHALLENGED / Microsoft Azure WAF 403, twice | **MERGED to CHALLENGED / Microsoft Azure WAF.** Round + 2 agreeing challenges — answering again after the Wave 19 failure merge. NOT fix-driven. |
| www.fda.gov | LOGIN_GATED / Akamai | OPEN 200 | OPEN 200, twice | **MERGED to OPEN.** Round + 2 agreeing served readings — the Wave 18 401 gate is gone. The LOGIN_GATED watch empties (see below). NOT fix-driven. |
| www.goodrx.com | OPEN 200 | CHALLENGED / PerimeterX 403 | CHALLENGED / PerimeterX 403, twice | **MERGED to CHALLENGED / PerimeterX.** Round + 2 agreeing challenges. The fresh evidence carries a Wave 20 flag (REDIRECT_TO_CHALLENGE), but it is NON-DETERMINATIVE: the verdict is driven by PX_CAPTCHA + PX_BODY_MARKER, both pre-existing vendor wall signals, and the round-16 Wave 19-tree reading already agreed on CHALLENGED / PerimeterX — the verdict/vendor pair agrees across trees regardless of which routing species produced the redirect code. |
| www.irishjobs.ie | OPEN 200 | UNREACHABLE (fetch failure) | UNREACHABLE, twice | **MERGED to UNREACHABLE.** Round + 2 agreeing failures — the Wave 19 OPEN merge reversed; the site is down again. NOT fix-driven: no response was classified. |
| www.jobrapido.com | RATE_LIMITED 429 | OPEN 200 | OPEN 200, twice | **MERGED to OPEN.** Round + 2 agreeing served readings — throttle lifted. NOT fix-driven. |
| www.jobs.ie | OPEN 200 | UNREACHABLE (fetch failure) | UNREACHABLE, twice | **MERGED to UNREACHABLE.** Round + 2 agreeing failures — same pattern as irishjobs.ie. NOT fix-driven. |
| www.npmjs.com | CHALLENGED / Cloudflare | UNREACHABLE (fetch failure) | CHALLENGED / Cloudflare 403, twice | **HELD at CHALLENGED.** The round's connection drop is overturned by two agreeing fresh challenged readings — the 9th transport-pattern sighting for npmjs.com. |
| www.totaljobs.com | OPEN 200 | UNREACHABLE (fetch failure) | UNREACHABLE, twice | **MERGED to UNREACHABLE.** Round + 2 agreeing failures — the third Wave 19 recovery reversed. NOT fix-driven. |
| www.ubereats.com | OPEN 200 | CHALLENGED / Cloudflare 403 | CHALLENGED / Cloudflare 403, twice | **MERGED to CHALLENGED / Cloudflare.** Round + 2 agreeing challenges — the Wave 17 head-strip OPEN move is superseded by a live wall: the site now serves a real CF challenge instead of the head-strip page. Target-side, NOT a rule move (no Wave 19 rule produces a CF 403 challenge). |
| www.wayfair.com | OPEN 200 | CHALLENGED / PerimeterX 429 | OPEN 200, twice | **HELD at OPEN.** The round's 429-challenge is overturned by two agreeing fresh served readings — a transient throttle, not a standing wall. |
| www.webex.com | WALLED / Akamai | OPEN 200 | OPEN 200 + WALLED / Akamai 403 | **HELD at WALLED / Akamai.** 1–1 fresh split — no corroboration triple for either side (round + 1 fresh served vs 1 fresh deny is 2–1, not the required round + 2). |

## Fix-driven moves: zero

- **Template-block strip (W19-001) — 0 moves.** No live row's
  verdict depended on template text.
- **Alt-join phrase scan (W19-002) — 0 moves.** No live row
  serves a phrase split across image alts.
- **EMAIL_CONTINUE_PROMPT (W19-003) — 0 moves.** No live row
  serves an email-only Continue sign-in step at its root.
- **Sitemap usability test (W19-004) — 0 moves.** Audit
  tool, not the index.
- **CR-only frontmatter normalization (W19-005) — 0 moves.**
  Audit tool, not the index.
- **Fragment-only loc rejection (W19-006) — 0 moves.** Audit
  tool, not the index.
- **HE/FA/UR/BN phrases (W19-007) — 0 moves.** No live row
  serves a challenge page in those languages.
- **Native <dialog open> loop (W19-008) — 0 moves.** No live
  row serves a dialog challenge at its root.
- **Spotlights:** remoteok.com, td.com, venmo.com read OPEN
  under the Wave 19 tree — no QR misfire recurs; rubygems.org
  reads OPEN (the W17-007 passkey fix holds); forbes.com reads
  CHALLENGED / DataDome, agreeing with standing — the Wave 19
  merge holds, no fresh capture needed. ubereats.com is the
  exception noted above: a target-side wall, not a rule move.

The zero-fix-driven-move run continues: rounds 8–13 moved no
live row correctly, round 14 moved one (ubereats.com), rounds
15–16 move none. The Wave 20 battery fixes landed after the
runner imported its tree, so they are unmeasured on live
traffic until round 17.

## Merge result

**10 rows changed** (claude.ai, amazon.com, ed.gov, fda.gov,
goodrx.com, irishjobs.ie, jobrapido.com, jobs.ie, totaljobs.com,
ubereats.com) and 3 held (npmjs.com, wayfair.com, webex.com).
INDEX distribution after merges: OPEN 415 · CHALLENGED 26 ·
WALLED 35 · RATE_LIMITED 7 · UNREACHABLE 17 · LOGIN_GATED 0
(500 rows, recount verified). The merged distribution differs
from the round-16 raw distribution by exactly the three holds
above. The LOGIN_GATED watch that began in Wave 11 empties:
both standing LOGIN_GATED rows moved this round (claude.ai to
CHALLENGED, fda.gov to OPEN), so there is no LOGIN_GATED row
left to watch — the next wave's Leg D watches for any new
LOGIN_GATED row instead.
