# Wave 10 — Round-6 stability (Leg A)

**499/499 rows probed once each** (honest wallcheck UA, no retries;
runner `validation/wave10/run_round6.py`, incremental + resumable
saves to `validation/wave4/history.jsonl` as round=6 and to
`validation/wave10/results-round6.jsonl`). All 499 history lines
parse; zero missing URLs vs round 5.

Round-6 distribution: OPEN 413 · WALLED 36 · CHALLENGED 25 ·
UNREACHABLE 18 · RATE_LIMITED 7.

## Flips vs raw round-5 history: 7

Raw-history flips overstate the merge set, because round 5's raw
rows include two transport timeouts Wave 7 already held (otta.com
and careerbuilder.com timed out once; their standing INDEX
verdicts were never changed). Against the raw history:

| target | round 5 (raw) | round 6 | hand-check | disposition |
| --- | --- | --- | --- | --- |
| otta.com | UNREACHABLE (timeout) | OPEN 200 | — | Not a flip: INDEX already OPEN (W3 expansion); round 6 corroborates it. Standing verdict held. |
| www.careerbuilder.com | UNREACHABLE (timeout) | CHALLENGED / DataDome 403 | — | Not a flip: INDEX already CHALLENGED / DataDome (W5 expansion); round 6 corroborates it. Standing verdict held. |
| www.npmjs.com | CHALLENGED / Cloudflare 403 | CHALLENGED / Cloudflare 403 | — | Stable. No connection-drop this round (the 5th sighting pattern did not recur). |
| www.amazon.com | CHALLENGED / Generic 200 | OPEN 200 | fresh capture CHALLENGED / Generic | Churn (known intermittent interstitial). INDEX HELD at CHALLENGED: the fresh capture minutes after round 6 shows the interstitial again, so round 6's OPEN was a sat-out, not a posture change. |
| www.britishairways.com | OPEN 200 | UNREACHABLE (timeout) | fresh capture ALSO timed out (20 s) | Transport, reproduced twice → MERGED to UNREACHABLE. Not a wall verdict: the site times out for this client rather than refusing. (Precedent: Wave 3 flexjobs reproduced timeout.) |
| www.chicagotribune.com | OPEN 200 | WALLED, bare 403 | fresh capture serves 200 OPEN | Churn (one-round flap). INDEX HELD at OPEN. |
| www.forbes.com | OPEN 200 | CHALLENGED / DataDome 403 | fresh capture serves 200 OPEN (DataDome sensor header present on the served page — presence, correctly not a wall) | Churn (one-round flap; DataDome is present on the site and fires intermittently). INDEX HELD at OPEN. |
| www.webex.com | OPEN 200 | WALLED / Akamai 403 | fresh capture serves 200 OPEN | Churn (one-round flap). INDEX HELD at OPEN. |

## Merge result

**One row changed:** britishairways.com OPEN → UNREACHABLE
(W10 round-6 provenance). New INDEX distribution: OPEN 415 ·
CHALLENGED 25 · WALLED 34 · RATE_LIMITED 7 · UNREACHABLE 18
(499 rows, recount verified). The four one-round flaps and the
amazon sat-out were all hand-checked with fresh captures and
held, not merged — the same rule as Wave 7 (a single
UNREACHABLE reading never overwrites a standing verdict) and
Wave 4/7 (amazon's oscillation is documented, not smoothed).

## Classifier-version note (read before comparing rounds)

Round 6 ran with the **pre-Wave-10 classifier**: the runner imports
its modules once at start, and it started before the Wave 10
fixes (W10-001…W10-008) landed. Round 5 vs round 6 is therefore
an apples-to-apples comparison, and the hand-check captures above
used the NEW classifier — none of the five hand-checked flips
carried a new-rule signal, so no flip is fix-driven. A
fix-driven reclassification of the full index (what the new
geo/451/redirect rules would change on live bodies) is properly
round 7's job, not something inferred from stored verdicts.

## Saturation consequence

Round 6 itself is churn-only (zero classifier defects in the
stability leg), but Wave 10 as a whole is NOT a clean wave: Leg B
found 8 genuine defects. The saturation clock resets regardless
of this leg's clean sheet.
