# Wave 21 — Round-17 re-probe measuring the Wave 20 fixes (Leg A)

**500/500 rows probed once each** with the Wave 20-fixed
classifier — the measurement Wave 20's STABILITY-15 deferred.
The runner (`validation/wave21/run_round17.py`, written fresh
for round 17 with the round number in exactly one constant)
imported the Wave 20 tree at launch (process start 12:48:42
UTC, before any Wave 21 battery edit landed — classify.py
and audit.py edits at 12:51:14 UTC, test_adversarial13.py
at 12:51:18 UTC): all Wave 20 fixes were grep-verified
present before probing (W20-001 iframe-src routing targets,
W20-002 localized JS-proof phrases DE/FR/ES/PT/JA, W20-003
localized human-check phrases UK/HI/MS/TL/SW). The runner ran
fully detached (setsid nohup, resumable, monitored via its
log) — no incident this wave: 500 new probes, zero missing
URLs vs the INDEX table, zero duplicate round-17 lines. All
500 history lines parse.

**Method note on fresh captures:** the round measured the
Wave 20 tree, but fresh captures necessarily ran on the
current (Wave 21-fixed) tree. Every fresh capture therefore
carries a Wave 21-rule involvement check (object data URLs
and embed sources to login/challenge targets, "high traffic"
wording with a Retry-After header, authenticator prompts,
TA/TE/MR/PA phrases, AUTHENTICATOR_PROMPT and
RETRY_AFTER_THROTTLE evidence). All 8 fresh captures report
zero involvement flags — the corroborations below are
tree-comparable. Fetch failures are tree-independent (no
response was classified). One runner note, same family as
Wave 16's: probe_url does not return the body, so the
fresh-capture script uses fetch_raw + classify.

Round-17 raw distribution: OPEN 415 · CHALLENGED 24 ·
WALLED 35 · RATE_LIMITED 7 · UNREACHABLE 19 · LOGIN_GATED 0.

## The 4 verdict diffs, all hand-checked with fresh captures

Every verdict diff was hand-checked with two fresh captures
(`validation/wave21/fresh_captures.py`, results in
`fresh-captures.json`) before disposition — no diff was
merged on the round-17 reading alone. The strict rule: merge
only on round + 2 agreeing fresh; a 1–1 fresh split holds
the row; fresh readings agreeing with standing hold the row
against a lone round diff.

| target | standing | round 17 | fresh capture(s) | disposition |
| --- | --- | --- | --- | --- |
| apnews.com | CHALLENGED / Cloudflare | UNREACHABLE (fetch failure) | UNREACHABLE + CHALLENGED / Cloudflare 403 | **HELD at CHALLENGED.** 1–1 fresh split — no corroboration triple for either side (round + 1 fresh failure vs 1 fresh challenge). Transport noise: Wave 16 recorded the first apnews transport-noise sighting on the same pattern. |
| www.amazon.com | CHALLENGED / Generic | OPEN 200 | CHALLENGED / Generic 200, twice | **HELD at CHALLENGED.** The round's served reading is overturned by two agreeing fresh interstitial readings — the oscillator sat out again; note ‡ extends (a served triple would move it back). |
| www.npmjs.com | CHALLENGED / Cloudflare | UNREACHABLE (fetch failure) | CHALLENGED / Cloudflare 403, twice | **HELD at CHALLENGED.** The round's connection drop is overturned by two agreeing fresh challenged readings — the 10th transport-pattern sighting for npmjs.com. |
| www.wayfair.com | OPEN 200 | CHALLENGED / PerimeterX 429 | OPEN 200, twice | **HELD at OPEN.** The round's 429-challenge is overturned by two agreeing fresh served readings — a transient throttle, not a standing wall; the Wave 20 hold repeats. |

## Fix-driven moves: zero

- **Iframe-src routing (W20-001) — 0 moves.** No live row's
  verdict depended on an iframe source.
- **Localized JS-proof phrases (W20-002) — 0 moves.** No live
  row serves a browser-verification stub in DE/FR/ES/PT/JA.
- **Localized human-check phrases (W20-003) — 0 moves.** No
  live row serves a challenge page in UK/HI/MS/TL/SW.
- **Spotlights:** all ten Wave 20 merges agree with round 17
  (claude.ai CHALLENGED/CF, amazon.com — see diff above,
  ed.gov CHALLENGED/Azure, fda.gov OPEN, goodrx.com
  CHALLENGED/PX, irishjobs.ie / jobs.ie / totaljobs.com
  UNREACHABLE, jobrapido.com OPEN, ubereats.com
  CHALLENGED/CF); forbes.com reads CHALLENGED / DataDome,
  agreeing with standing — the Wave 19 merge holds;
  remoteok.com, td.com, venmo.com read OPEN — no QR
  misfire recurs; rubygems.org reads OPEN — the W17-007
  passkey fix holds.

The zero-fix-driven-move run continues: rounds 8–13 moved
no live row correctly, round 14 moved one (ubereats.com),
rounds 15–17 move none. The Wave 21 battery fixes landed
after the runner imported its tree, so they are unmeasured
on live traffic until round 18.

## Merge result

**Zero rows changed** and 4 held (apnews.com, amazon.com,
npmjs.com, wayfair.com). INDEX distribution after
disposition: OPEN 415 · CHALLENGED 26 · WALLED 35 ·
RATE_LIMITED 7 · UNREACHABLE 17 · LOGIN_GATED 0 (500 rows,
recount verified). The merged distribution differs from
the round-17 raw distribution by exactly the four holds
above. The INDEX header carries the Wave 21 round-17
narrative parenthetical.

## Leg C — path-matrix spot-check on the 10 Wave 20 merges

50 probes (5 paths × 10 rows) in
`results-path-matrix.jsonl`, each path probed once:
- **Consistent:** claude.ai (login/signup/api CHALLENGED/CF),
  ed.gov (all five paths CHALLENGED/Azure — the whole
  domain answers through the same wall), fda.gov (all
  OPEN/404), goodrx.com (login/signup/api/llms
  CHALLENGED/PX), jobrapido.com (all OPEN),
  ubereats.com (login/signup/robots/llms CHALLENGED/CF,
  api 404 OPEN).
- **Consistent with nuance:** amazon.com (login/signup
  503 failures, api 429 RATE_LIMITED — failures and a
  throttle, not walls; no contradiction with the root
  CHALLENGED reading).
- **Nuance noted, not a contradiction:** irishjobs.ie,
  jobs.ie, totaljobs.com answer robots.txt 200 OPEN while
  root/login/signup/api/llms all fail — the outage is
  origin-down with an edge-served robots file, not
  domain-dead. The root UNREACHABLE merges stand (round +
  2 fresh failures each in round 16, and round 17 agrees);
  a served robots file does not prove the root serves.
- **No contradictions.** No path evidence suggests any
  round-16 root merge was wrong.
