# Wave 7, Leg B — Round-5 Stability Re-probe

**Method.** Every row of the merged index re-probed once (honest
wallcheck UA, no retries): 394 pre-existing rows against their
INDEX.md verdicts, 105 new expansion rows against their Leg A
verdicts. One honest fetch each; a 429 ends that target's turn.
Machine-readable results: `results-round5.json`; history appended
to `validation/wave4/history.jsonl` (rounds 3, 4, 5 now live there).

## Headline

**496 of 499 verdicts identical.** Three flips, all churn or
transport, zero classifier defects. Round-5 distribution (499
authoritative rows): OPEN 415 · WALLED 34 · CHALLENGED 24 ·
UNREACHABLE 19 · RATE_LIMITED 7.

## The three flips

| Target | Was | Round 5 | Reading |
|---|---|---|---|
| otta.com | OPEN | UNREACHABLE (timeout) | Isolated transport failure, 06:51 UTC. Standing verdict HELD — UNREACHABLE claims no verdict (SPEC). |
| www.careerbuilder.com | CHALLENGED / DataDome | UNREACHABLE (timeout) | Same isolated incident window, 06:51 UTC. Standing verdict HELD. |
| www.amazon.com | OPEN | CHALLENGED / Generic (200) | The intermittent captcha interstitial is back. See oscillation note below. Merged CHALLENGED. |

## Amazon's oscillation (documented, not smoothed)

amazon.com's interstitial has now appeared in 2 of 4 measured
rounds: Wave 1 OPEN → Wave 3 stability CHALLENGED (gate raised)
→ Wave 4 round 3 OPEN (interstitial sat out) → Wave 5 round 4
OPEN → Wave 7 round 5 CHALLENGED (200, "continue shopping"
captcha interstitial, capture-verified shape). Merge rule applied
consistently with Wave 4: the standing verdict follows the
latest *real* measurement (a served interstitial is a posture
fact, unlike transport noise), and the oscillation is recorded
here rather than averaged away. The next round will show whether
CHALLENGED sticks.

## Vendor attributions filled (verdict unchanged)

- **www.npmjs.com**: CHALLENGED, vendor was unattributed ("—") →
  **Cloudflare** (403 with full challenge suite). The standing
  verdict never moved; the attribution caught up.
- **www.realtor.com**: RATE_LIMITED, vendor unattributed →
  **Kasada** (429 payload). Same verdict, better receipt.

## UNREACHABLE, all 19 (no posture change in any)

- 2 flips above (otta, careerbuilder — isolated timeouts).
- 7 pre-existing repeat-unreachables (flexjobs, totaljobs,
  bestbuy, kroger, united, etrade, todoist — all timeouts, same
  as their standing rows).
- 10 new-row repeats (the Leg A UNREACHABLEs re-measured in
  round 5: irishjobs.ie, jobs.ie, magento.com,
  washingtonpost.com, cbc.ca, airfrance.com, klm.com timeouts;
  doj.gov, block.com, getyourguide.com connection drops).

## The mid-round incident: egress-proxy credential rotation

**What happened.** At 07:15:06 UTC, mid-round, the VM's egress
proxy credential rotated. The long-lived runner held the stale
credential, so every fetch from 07:15:06 onward failed at the
proxy: first a timeout phase (~07:15–07:20, sequential ~16 s
timeouts), then hard `Tunnel connection failed: 403 Forbidden`
errors (~07:21 onward). 52 consecutive round-5 rows were poisoned
this way — a continuous run of UNREACHABLEs across unrelated
operators (Zillow, Salesforce, HubSpot, Zendesk, Mailchimp,
Webflow...) that no honest reading could call 52 simultaneous
site outages.

**How it was diagnosed.** A fresh-shell probe of example.com
succeeded while the runner kept failing; the proxy-URL hash in
the runner's `/proc/<pid>/environ` differed from the current
shell's — proof the credential had rotated under the old process.

**How it was repaired (no data laundered).** (1) The runner was
killed precisely (shell `kill` on its PID — not the runtime's
session kill, which would have torn down detached descendants).
(2) The 52 poisoned rows were removed from
`results-round5.json` and archived verbatim to
`results-round5-window.json`. (3) The runner was restarted from
a fresh shell (fresh credential) and re-probed exactly the
missing rows; the recovery values are the round-5 record — the
recovered rows confirm the diagnosis (paddle.com, zendesk.com,
chargebee.com and the rest all probe OPEN again). (4) The runner
also had a latent resume bug (`r["url"]` on records keyed by
`"target"`, inherited from the Wave 4 script whose resume path
never executed); fixed in `run_wave7.py` before the restart.

**History accounting (read this before counting).**
`history.jsonl` now holds 859 lines: rounds 3 and 4 (154 each)
plus 551 round-5 lines. The 551 = 499 targets, of which the 52
window targets appear TWICE: once for the failed attempt
(UNREACHABLE, proxy error) and once for the recovery attempt
(authoritative). Counting round-5 lines naively over-counts
UNREACHABLE (71 vs the true 19). The authoritative round-5
distribution is the one in `results-round5.json`, not the raw
line count. This paragraph exists so nobody has to rediscover
that.

## Merge decisions (all in INDEX.md, verified after merge)

- otta.com, careerbuilder.com: standing verdicts HELD
  (UNREACHABLE claims no verdict).
- amazon.com: merged CHALLENGED / Generic (latest real
  measurement; oscillation noted above).
- npmjs.com: vendor filled → Cloudflare; realtor.com: vendor
  filled → Kasada.
- All other rows: unchanged. The 105 expansion rows merged from
  Leg A (careerjet.com's CHALLENGED / Cloudflare stands — see
  PROBLEMS.md W7-001 for why the suspected defect was not one).
