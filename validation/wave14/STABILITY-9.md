# Wave 14 — Round-10 re-probe measuring the Wave 13 fixes (Leg A)

**499/499 rows probed once each** with the Wave 13-fixed
classifier — the measurement Wave 13's STABILITY-8 deferred.
The runner (`validation/wave14/run_round10.py`, incremental +
resumable saves to `validation/wave4/history.jsonl` as round=10
and to `validation/wave14/results-round10.jsonl`) imported the
Wave 13 tree at launch: all three Wave 13 fixes were grep-verified
present before probing (W13-001 HTML comment stripping, W13-002
"check your browser" JS_PROOF phrase, W13-003 title-only llms
WARN). All 499 history lines parse; zero missing URLs vs the
INDEX table; zero duplicate round-10 lines.

Round-10 raw distribution: OPEN 415 · CHALLENGED 25 · WALLED 35 ·
RATE_LIMITED 7 · UNREACHABLE 17 · LOGIN_GATED 0.

## Launch incidents (no data impact, recorded honestly)

Three launches were needed, and the first two are part of the
record — not hidden — because the second one wrote data that
had to be purged:

1. **Sed-trapped resume check (probed nothing).** The runner was
   derived from `run_round9.py` by sed, and the sed missed the
   resume-check call: `done_urls(HISTORY, 9)` survived while
   every label said round 10. The run reported "already probed
   round 10: 499" with zero round-10 lines and exited — the
   same trap Wave 13 documented for its own first launch
   (STABILITY-8.md). The failed launch wrote nothing
   (append-mode files, zero lines written). Fixed to round 10.
2. **Contaminated launch (38 lines written, then purged).**
   The relaunch ran AFTER the Wave 14 battery fixes had landed
   on disk, so it imported the Wave 14-fixed tree — the wrong
   tree for a Wave 13 measurement. It was killed after 38 lines
   (3 more landed before the kill: 41 total). All 41 round-10
   lines were purged from `history.jsonl` via a tmp-file +
   atomic replace (kept 2855, dropped 41, verified zero
   round-10 lines remained), and `results-round10.jsonl` was
   deleted. The kill loop itself briefly matched its own shell
   (the pgrep self-match pitfall, AGENTS.md) and killed its own
   exec session — the runner died as intended, the session did
   not matter.
3. **Clean launch.** The Wave 14 fixes were backed up
   (`validation/wave14/src-wave14-fixed/`), reverted from `src/`
   (verified: zero Wave 14 markers, all three Wave 13 markers
   present, suite 236 green on the reverted tree), and the
   runner launched — importing the Wave 13 tree. The fixed tree
   was then restored from backup (verified byte-identical,
   battery 32/32, suite 236 green) while the runner held the
   Wave 13 modules in memory. A Wave 13-tree copy
   (`validation/wave14/src-wave13-tree/`) was kept so the fresh
   captures below could be judged by the round's own classifier.

## Raw diffs vs the standing table: 3, dispositioned

Every diff was hand-checked with fresh captures classified by
the Wave 13-tree copy before merging — no diff was merged on
the round-10 reading alone.

| target | standing | round 10 | fresh capture(s) | disposition |
| --- | --- | --- | --- | --- |
| www.britishairways.com | OPEN 200 | UNREACHABLE (fetch failed) | OPEN 200, twice (real BA homepage, Akamai server header presence only) | HELD at OPEN. The round-10 failure is transport oscillation, not a posture change: timed out R6, served R7, timed out R8 ×2, served R9 + fresh, failed R10, served fresh ×2. A single uncorroborated transport failure does not move a served row (the npmjs precedent). NOT fix-driven: a fetch failure involves no classifier rule. |
| www.kaiserpermanente.org | OPEN 302 | OPEN 200 | OPEN 302, twice (redirects to regional front-door pages, varying by attempt: Colorado, then Maryland-Virginia-DC) | HELD at OPEN/302. Two agreeing fresh redirects corroborate the standing status cell; round 10's 200 is a routing variant (a regional path resolving directly), not a change. STATUS-ONLY diff, resolved for standing. NOT fix-driven. |
| www.todoist.com | UNREACHABLE (fetch failed) | OPEN 200 | OPEN 200, twice (real Todoist homepage) | MERGED to OPEN. Round 10 plus two agreeing fresh served readings retire the standing transport failure. NOT fix-driven: a recovery from a fetch failure, not a classifier rule — the standing row carried no status for any rule to act on. |

## Fix-driven moves: exactly zero

Fourth consecutive round with zero fix-driven moves (Waves 11,
12, 13, 14). Of the three Wave 13 rule families this round was
built to re-measure, none moved a live row:

- **Comment stripping (W13-001) — 0 moves.** No live row's
  verdict depended on a comment-only marker.
- **"Check your browser" phrase (W13-002) — 0 moves.** No live
  row serves that stub wording.
- **Title-only llms WARN (W13-003) — audit tool, not the
  index.** No index row is an audit grade.

The Wave 10–13 fixes remain correctness insurance for shapes
live traffic has not shown this index, proven by fixtures,
unexercised by traffic.

## Merge result

**One row changed:** todoist.com UNREACHABLE → OPEN (status
200, last-checked W14 round-10). New INDEX distribution: OPEN
416 · CHALLENGED 25 · WALLED 35 · RATE_LIMITED 7 · UNREACHABLE
16 · LOGIN_GATED 0 (499 rows, recount verified by the Leg C
auditor). The merged distribution differs from the round-10 raw
distribution by exactly the todoist merge (raw OPEN 415 /
UNREACHABLE 17 → merged OPEN 416 / UNREACHABLE 16); the
britishairways and kaiser holds change nothing. amazon.com and
npmjs.com both read agreeing with standing in round 10 (no
diffs), so their notes stand with round-10 agreement recorded.
