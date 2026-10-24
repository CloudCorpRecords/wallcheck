# Wave 4, Leg A — Third Data Point: Verdict History, Round 3

Re-probed the full 154-site Bot Wall Index set (the exact URLs in
`INDEX.md`, i.e. the Wave 3 merged verdicts as the baseline), one
honest fetch per target, `wallcheck/0.4.0` user-agent, no retries,
runner `validation/wave4/run_wave4.py`. Raw results:
`results-history.json`; the machine-readable history line for every
target was appended to `history.jsonl` (`target`, `round: 3`, `ts`,
`verdict`, `vendor`, `status`).

## Round 3 distribution (vs Wave 3 merged baseline)

| Verdict | Wave 3 merged | Wave 4 round 3 |
|---|---|---|
| OPEN | 133 | 136 |
| CHALLENGED | 10 | 8 |
| WALLED | 6 | 6 |
| RATE_LIMITED | 1 | 1 |
| UNREACHABLE | 4 | 3 |

**Merge policy for the root INDEX:** rows merge on positive
evidence (a served page, a served wall). The three loosening flips
were merged into `INDEX.md` (provenance "W4 history"); npmjs.com
was *held* at CHALLENGED because a dropped connection is an absence
of evidence, not evidence of a changed posture — the same rule
Wave 3 applied. Merged index after Wave 4: OPEN 136 · CHALLENGED 9 ·
WALLED 6 · RATE_LIMITED 1 · UNREACHABLE 2.

## The flips: 4 of 154 — all churn, zero classifier defects

| Target | Baseline | Round 3 | Verdict on the flip |
|---|---|---|---|
| replit.com | UNREACHABLE | **OPEN** 200 | **Churn.** The transport-level refusal seen in W1 and W3 is gone; Replit served its real homepage to the identified agent. |
| discord.com | UNREACHABLE | **OPEN** 200 | **Churn.** Same pattern: previously refused/reset, now a normal full serve. |
| www.amazon.com | CHALLENGED | **OPEN** 200 | **Churn.** The "continue shopping" interstitial Amazon added between W1 and W3 did not appear this round. Amazon's challenge is intermittent; our verdict tracks what is served, round by round. |
| www.npmjs.com | CHALLENGED | **UNREACHABLE** (no status) | **Churn (transport), known flapping case.** The fetch died with `RemoteDisconnected` — the fourth sighting of this exact pattern (W2 paths, W3 stability, W3 audit sample, now W4). The root INDEX keeps CHALLENGED, with the instability note, per the W3 precedent. |

Every flip was hand-checked against its recorded evidence:

- The two UNREACHABLE → OPEN flips carry full-serve evidence
  (`STATUS_200`, Cloudflare ray/server headers on real homepages) —
  the targets changed their posture toward this client, not the
  classifier.
- The Amazon flip has no challenge markers in evidence at all this
  round; the W3 interstitial body markers are absent because the
  interstitial was absent.
- The npmjs flip is a fetch error, not a wall signal; UNREACHABLE is
  the honest verdict for a dropped connection, and no wall verdict
  was claimed.

Zero vendor-attribution changes among non-flipped rows. **No
classifier changes were needed in Wave 4** — the first wave with a
clean defect sheet on the stability leg. (The defect process still
ran on the new Ed25519 code instead; see the Wave 4 addendum in
`validation/wave2/SIGNING.md`.)

## What three data points now say

- **The hard core is stable:** all 6 WALLED verdicts (Upwork,
  LinkedIn, eBay, Guru, Best Buy, w3schools) and the single
  RATE_LIMITED (expedia.com) reproduced exactly. The walls that
  define the campaign's problem statement are not weather; they are
  fixtures.
- **The churn lives at the edges:** of the 58 Wave 1 originals,
  cumulative flips across rounds 2–3 of re-probing are concentrated
  in transport reachability (Replit, Discord, npmjs) and one
  intermittent interstitial (Amazon). Verdict-level stability for
  the merged 154 after three rounds: 150/154 unchanged this round
  (97.4%).
- **Direction of travel this round was toward open** (3 of 4 flips
  loosened). One round is not a trend; the history file now exists
  precisely so future rounds can say when it becomes one.
