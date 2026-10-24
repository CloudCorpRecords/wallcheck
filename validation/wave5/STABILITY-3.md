# Wave 5, Leg A — Fourth Data Point: Verdict History, Round 4

Re-probed the full 154-site Bot Wall Index set (the exact URLs in
`INDEX.md`, i.e. the Wave 4 merged verdicts as the baseline), one
honest fetch per target, `wallcheck/0.4.0` user-agent, no retries,
runner `validation/wave5/run_wave5.py` leg A. Raw results:
`results-history.json`; one history line per target appended to
`validation/wave4/history.jsonl` (`target`, `round: 4`, `ts`,
`verdict`, `vendor`, `status`) — the jsonl now carries two full
rounds (3 and 4, 154 lines each); rounds 1–2 live in the Wave 1
and Wave 3 results files in their own formats.

## Round 4 distribution (vs Wave 4 merged baseline)

| Verdict | Wave 4 merged | Wave 5 round 4 (raw) |
|---|---|---|
| OPEN | 136 | 136 |
| CHALLENGED | 9 | 8 |
| WALLED | 6 | 6 |
| RATE_LIMITED | 1 | 1 |
| UNREACHABLE | 2 | 3 |

The raw round differs from the merged baseline by exactly one
row (below), and per the established merge policy — rows merge
on positive evidence — **the merged index is unchanged by
round 4**: OPEN 136 · CHALLENGED 9 · WALLED 6 · RATE_LIMITED 1 ·
UNREACHABLE 2 for the original 154.

## The flip: 1 of 154 — churn, zero classifier defects

| Target | Baseline | Round 4 | Verdict on the flip |
|---|---|---|---|
| www.npmjs.com | CHALLENGED | **UNREACHABLE** (no status) | **Churn (transport), the known flapping case.** `RemoteDisconnected` again — the fifth sighting of the pattern (W2 paths, W3 stability, W3 audit sample, W4 round 3 + census, now W4). Per the merge rule in force since Wave 3, the root INDEX keeps CHALLENGED with the instability note updated: a dropped connection is an absence of evidence, not evidence of a changed posture. |

The posture is not actually in doubt: minutes after the round-4
probe dropped, this wave's Leg C experiment fetched npmjs.com
twice (unsigned and signed) and was served the real Cloudflare
challenge both times — CHALLENGED, 403 (`SIGNED-EXPERIMENT.md`).
npmjs's wall intermittently refuses the *connection* instead of
serving its challenge; the index records the posture and the
habit, separately, which is all an honest index can do.

Zero vendor-attribution changes among the 153 non-flipped rows.
**No classifier changes came out of Leg A** — the second
consecutive clean defect sheet on a stability leg (Wave 4's
stability leg was also clean; all five Wave 5 defects came from
the Leg B expansion into new territory, see PROBLEMS.md).

## What four data points now say

- **The hard core has never moved.** All 6 WALLED verdicts
  (Upwork, LinkedIn, eBay, Guru, Best Buy, w3schools) and the
  single RATE_LIMITED (expedia.com) have now reproduced in every
  measurement round since they entered the index. Across four
  rounds the walls that define the campaign's problem statement
  have a perfect reproduction record.
- **Stability is compounding.** Verdict-level churn per round
  for the original set: 2 flips (W3), 4 (W4), 1 (W5) — and the
  W5 flip is a transport artifact on the index's one documented
  flapping case, not a posture change. Measured churn
  overstates real churn, and the gap between the two is exactly
  why the merge rule exists.
- **Churn lives where it always lived:** transport reachability
  (npmjs's drops; Replit and Discord's round-3 returns) and one
  intermittent interstitial (Amazon, absent since round 3).
  Nothing in four rounds suggests verdicts drift silently —
  when a posture changes, it changes on the record (Amazon's
  round-2/3 interstitial pair is the model).
