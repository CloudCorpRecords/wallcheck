# Report Card: PerimeterX (HUMAN Security) Bot Defender

**Vendor:** HUMAN Security (PerimeterX, acquired 2022: the Bot
Defender product still ships under the PerimeterX detection family:
`_px*` cookies, px-captcha) [SOURCE]
**Graded by:** the wallcheck campaign (Rene Turcios / CloudCorpRecords)
**Date:** October 2026 (Bot Wall Index rounds 1-3)
**Companion:** `REPORT-CARD-CLOUDFLARE.md`: same rubric, same
standard. Grades are ours; vendor claims are tagged as vendor claims.

Every factual claim below is tagged: **[MEASURED]** (our index /
probes), **[VENDOR]** (the vendor's own published claim),
**[SOURCE]** (a cited third-party or primary source), **[POSITION]**
(our argument).

## Scorecard

| Dimension | Grade | One-line basis |
|---|---|---|
| Standards & identity | **B−** | Verifies Web Bot Auth signatures [SOURCE], but its good-bot model is still a curated feed, and the signed path is not the documented front door |
| Owner controls | **B+** | Per-bot policies in a real console; UA-only allow rules honestly flagged as "abusable" by HUMAN itself [VENDOR] |
| Transparency | **C** | Strong research/marketing output; no published false-positive or legitimate-agent block rates |
| False-positive handling | **D+** | No public path for a blocked agent operator; the challenge is a JavaScript wall an HTTP client cannot answer |
| Net effect on legitimate agents | **D+** | Three properties in our index are challenged by PerimeterX, including a top freelance marketplace that challenges an honestly identified agent at the front door [MEASURED] |

## Where credit is due

- **HUMAN verifies Web Bot Auth signatures.** Amazon's Bedrock
  AgentCore documentation states that sites protected by HUMAN
  Security can verify Web Bot Auth signatures and let signed agents
  through without a CAPTCHA, where the domain owner allows verified
  bots [SOURCE: aws.amazon.com AgentCore Browser blog]. An industry
  survey of the standard lists HUMAN among the verifying parties
  [SOURCE: ppc.land, "Explaining Web Bot Auth"]. That is the right
  direction, and it is more than two of the four vendors in this
  series publicly offer.
- **It is honest about weak allow rules.** HUMAN's own documentation
  classifies a customer allow rule as "abusable" when it rests on
  the User-Agent header alone, and explains that attackers can spoof
  it [VENDOR: docs.humansecurity.com, "Known Bots and Crawlers"].
  Vendors rarely label their own customers' shortcuts that plainly.
- **Good-bot detection is a maintained feed, not a static list.**
  Bot Defender "automatically flags good bots based on a constantly
  updated live feed," on top of the customer's own list [VENDOR:
  docs.humansecurity.com, "Detection Overview"].
- **Scale is real.** HUMAN states it verifies 20 trillion digital
  interactions weekly [VENDOR, via its G2 profile]. We grade claims
  as claims, but the deployment footprint is not in doubt.

## Where it hurts: measured

Our index's best-known PerimeterX row is not a scraper farm. It
is **Fiverr**: one of the largest freelance marketplaces on
earth (the current index also records PerimeterX challenges at
wayfair.com and goodrx.com):

- `www.fiverr.com`: **CHALLENGED**, PerimeterX, HTTP 403, stable
  across index rounds 1 and 3 [MEASURED: INDEX.md, freelance].
  The response sets the `_pxhd` challenge cookie and serves the
  px-captcha block experience to a client that identified itself
  honestly in its User-Agent and asked for one page, once.
- The nuance cuts both ways, and we record it: Fiverr's `llms.txt`
  was served in full (OPEN) in our path probing [MEASURED:
  validation/wave2]. The machine-readable front door exists; the
  human front door is the one behind the challenge. A freelancer's
  agent can read Fiverr's llms.txt but cannot read Fiverr.
- A challenge built on browser JavaScript and behavioral telemetry
  is, to a non-browser agent, indistinguishable from a wall
  [POSITION]. CHALLENGED is our honest verdict word for it, but the
  practical effect on the legitimate agent is the same as WALLED:
  it does not get in, and it is offered no identity-based way in.

This is the pattern the campaign exists to name: the wall does not
fall on the worst actors (they run real browsers, residential
proxies, and solving services). It falls on the automation that
*identifies itself*: exactly the traffic a healthy ecosystem should
be able to sort from abuse by identity rather than by obstacle
course [POSITION].

## The asks

1. **Make the signed path a documented product surface, not a
   capability.** Publish the Web Bot Auth verification flow in the
   Bot Defender docs: how a site enables it, what a signed agent
   must send, and what a verified agent is entitled to expect: the
   way the good-bot feed is documented today. Verification that
   operators cannot discover does not change behavior.
2. **Give challenged agents an identity off-ramp.** When Bot
   Defender challenges a request, the response should say how a
   legitimate automated client identifies itself instead (signed
   request, verified-bot registration, API). A challenge page that
   only a browser can solve is a dead end; a challenge page that
   names the front door is a filter.
3. **Publish legitimate-agent block rates.** HUMAN sees more
   interaction volume than almost anyone. A periodic number: how
   much identified, non-spoofed agent traffic is challenged or
   blocked, and how that trends as Web Bot Auth verification rolls
   out: would do more for the ecosystem than another threat report.

## What would raise these grades

- The Fiverr-class properties serving signed, identified agents
  without a JavaScript challenge → Standards A-range, Net effect up
  with it [POSITION].
- A public false-positive / legitimate-agent appeal path with an
  SLA, usable by the agent operator and not only by HUMAN's
  customer → False-positive handling up.
- Published block-rate numbers for identified agents → Transparency
  up.

Errors in this card will be corrected publicly, with the correction
noted, on the same terms we offered Cloudflare.

## Sources

- HUMAN documentation, "Detection Overview" (good-bot feed):
  https://docs.humansecurity.com/applications/bd-detection-overview
- HUMAN documentation, "Known Bots and Crawlers" (abusable rules):
  https://docs.humansecurity.com/applications-and-accounts/docs/known-bots-and-crawlers
- AWS, "Reduce CAPTCHAs for AI agents browsing the web with Web Bot
  Auth (Preview) in Amazon Bedrock AgentCore Browser" (HUMAN among
  verifying WAFs):
  https://aws.amazon.com/blogs/machine-learning/reduce-captchas-for-ai-agents-browsing-the-web-with-web-bot-auth-preview-in-amazon-bedrock-agentcore-browser/
- ppc.land, "Explaining Web Bot Auth" (verifier list):
  https://ppc.land/web-bot-auth/
- wallcheck Bot Wall Index (Fiverr row) and Wave 2 path probing:
  `INDEX.md`, `validation/wave2/PATHS.md` in this repository.
