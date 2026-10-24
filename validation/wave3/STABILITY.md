# Wave 3, Leg A — Stability Re-Probe

The Wave 1 set, re-probed verbatim: same 58 URLs
(`validation/wave1/targets.txt`), same honest wallcheck UA, one
fetch per target, from the same client context as Waves 1–2 (this
build VM, datacenter egress). Results: `results-stability.json`.
Baseline: Wave 1 final merged set (`validation/wave1/results-round2.json`,
OPEN 47 / WALLED 4 / CHALLENGED 4 / UNREACHABLE 3).

**Wave 3 stability distribution: OPEN 46 / WALLED 4 / CHALLENGED 4 /
UNREACHABLE 4.**

## Flips: 2 of 58 — both target-side churn, zero classifier defects

| site | Wave 1 final | Wave 3 | kind |
| --- | --- | --- | --- |
| www.npmjs.com | CHALLENGED (Cloudflare, 403) | UNREACHABLE (no status) | target-side churn |
| www.amazon.com | OPEN (—, 200) | CHALLENGED (Generic, 200) | target-side churn |

### npmjs.com — the wall intermittently kills the connection

Wave 3 evidence: `FETCH_ERROR: RemoteDisconnected: Remote end
closed connection without response`. The classifier never received
a response, so per SPEC the verdict is UNREACHABLE and no wall
verdict is claimed. This is the third sighting of the same pattern
on this domain (Wave 1 W1-005: round-1 UNREACHABLE, minutes later
the full Cloudflare challenge; Wave 2 W2-004: connection kills on
walled domains) — npmjs's wall sometimes answers with a challenge
page and sometimes drops the connection outright. The site's state
did not change; its *mood* did. Recorded as churn, not a defect,
and the root Index keeps Wave 1's CHALLENGED verdict with this
instability noted (see INDEX.md notes).

### amazon.com — Amazon raised its "continue shopping" gate

Wave 1 served this client the real homepage (OPEN, 200). Wave 3
served a 3,781-byte interstitial whose entire content is *"Click
the button below to continue shopping"* with a form posting to
`/errors_page/validateCaptcha` (capture:
`captures/amazon.json`). That is Amazon's bot gate, and the
classifier's CHALLENGED (Generic) verdict on this shape is correct
— the word "captcha" appears in the form's own endpoint. Amazon
hardened against this client between waves; nothing about the
classifier changed. Churn, not a defect. (Amazon's gate is a
one-click interstitial rather than a hard block, which is exactly
what CHALLENGED means: a non-interactive agent stops here.)

## What did not move

The other 56 targets are verdict-identical to Wave 1's final set,
including every wall: Upwork WALLED (Cloudflare), Fiverr CHALLENGED
(PerimeterX), Guru WALLED (Imperva), Medium WALLED (Cloudflare),
eBay WALLED (Akamai), Monster CHALLENGED (DataDome), NYT CHALLENGED
(DataDome). The three Wave 1 UNREACHABLEs (replit.com, discord.com,
bestbuy.com) reproduced a third time — from this client the fetch
genuinely fails, and no wall verdict is claimed for them.
