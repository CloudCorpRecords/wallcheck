# Wave 15 — Round-11 re-probe measuring the Wave 14 fixes (Leg A)

**499/499 rows probed once each** with the Wave 14-fixed
classifier — the measurement Wave 14's STABILITY-9 deferred.
The runner (`validation/wave15/run_round11.py`, written fresh
for round 11 rather than sed-derived, with the round number in
exactly one constant) imported the Wave 14 tree at launch: all
five Wave 14 fixes were grep-verified present before probing
(W14-001 script-only marker suppression, W14-002 TRAFFIC_CHECK,
W14-003 Retry-After throttle, W14-004 declared-sitemap
fallthrough, W14-005 fragment-link llms rule). All 499 history
lines parse; zero missing URLs vs the INDEX table; zero
duplicate round-11 lines. The launch guard was verified live:
after the first minutes the runner had written 109 lines to both
`history.jsonl` and `results-round11.jsonl` — no sed-trap no-op
this wave (the trap that bit Waves 13 and 14 was designed out
by writing the runner fresh with a single ROUND constant and
checking output growth before walking away).

Round-11 raw distribution: OPEN 415 · CHALLENGED 26 · WALLED 34 ·
RATE_LIMITED 7 · UNREACHABLE 17 · LOGIN_GATED 0.

## Raw diffs vs the standing table: 3, dispositioned

Every diff was hand-checked with fresh captures classified by
the Wave 14 tree (the round's own classifier — the battery fixes
landed only after the round finished) before merging — no diff
was merged on the round-11 reading alone.

| target | standing | round 11 | fresh capture(s) | disposition |
| --- | --- | --- | --- | --- |
| www.forbes.com | OPEN 200 | CHALLENGED / DataDome 403 | OPEN 200, twice (real Forbes homepage) | HELD at OPEN. The round-11 DataDome challenge is transient: two agreeing fresh served readings overturn it. A later spot-check (MCP smoke verification, minutes after the fresh captures) read CHALLENGED / DataDome again — a 2–2 split across four recent observations, so no corroboration triple exists for either side and the standing served verdict holds. Forbes is now a documented intermittent oscillator (like amazon.com's interstitial and britishairways.com's transport oscillation), flagged for re-check next round. NOT fix-driven: no Wave 14 rule touches DataDome detection, and the fresh captures show the wall is intermittent, not standing. |
| www.britishairways.com | OPEN 200 | UNREACHABLE (fetch failed) | UNREACHABLE, twice (fetch failed both attempts) | MERGED to UNREACHABLE. The mirror image of the Wave 14 hold, same rule, opposite evidence: in round 10 the fresh captures served and overturned the failure; in round 11 the fresh captures corroborate it (round + 2 agreeing failures). The oscillation continues — a served round-12 reading moves it back, exactly as todoist.com recovered in round 10. NOT fix-driven: a fetch failure involves no classifier rule. |
| www.webex.com | WALLED / Akamai 403 | OPEN 200 | WALLED / Akamai 403, twice (edgesuite deny) | HELD at WALLED / Akamai. The round-11 served reading is overturned by two agreeing fresh walls — webex oscillates between served and Akamai-denied across attempts (served R8 once, walled R9 twice, served R11 once, walled fresh twice). The standing wall row holds on the corroborated readings. NOT fix-driven: a served reading involves no classifier rule. |

## Fix-driven moves: exactly zero

Fifth consecutive round with zero fix-driven moves (Waves 11,
12, 13, 14, 15). Of the five Wave 14 rule families this round
was built to re-measure, none moved a live row:

- **Script-only suppression (W14-001) — 0 moves.** No live row's
  verdict depended on a script-only generic marker.
- **TRAFFIC_CHECK (W14-002) — 0 moves.** No live row serves
  traffic-anomaly wording with a verification cue.
- **Retry-After throttle (W14-003) — 0 moves.** No live row
  carries a timed throttle on 403/503.
- **Declared-sitemap fallthrough (W14-004) — audit tool, not the
  index.** No index row is an audit grade.
- **Fragment-link llms rule (W14-005) — audit tool, not the
  index.** No index row is an audit grade.

The Wave 10–14 fixes remain correctness insurance for shapes
live traffic has not shown this index, proven by fixtures,
unexercised by traffic. (The Wave 15 battery fixes, which landed
after this round, are measured by round 12.)

## Merge result

**One row changed:** britishairways.com OPEN → UNREACHABLE
(status —, last-checked W15 round-11). New INDEX distribution:
OPEN 415 · CHALLENGED 25 · WALLED 35 · RATE_LIMITED 7 ·
UNREACHABLE 17 · LOGIN_GATED 0 (499 rows, recount verified).
The merged distribution differs from the round-11 raw
distribution by exactly two holds: the forbes hold (CHALLENGED →
OPEN) and the webex hold (OPEN → WALLED); the britishairways
merge changes nothing against raw (already UNREACHABLE there).
Net: OPEN 415, CHALLENGED 25, WALLED 35, UNREACHABLE 17.
amazon.com and npmjs.com both read agreeing with standing in
round 11 (CHALLENGED / Generic and CHALLENGED / Cloudflare
respectively), so their notes stand with round-11 agreement
recorded.
