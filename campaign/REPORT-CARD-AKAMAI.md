# Report Card: Akamai Bot Manager

**Vendor:** Akamai (Bot Manager; App & API Protector)
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
| Standards & identity | **B+** | Web Bot Auth verification at the edge, documented by Akamai itself, with validated-bot classification [VENDOR] |
| Owner controls | **A** | The deepest control surface in this series: Bot Score thresholds per endpoint, a granular AI-bot directory, responses from allow to serve-alternate-content [VENDOR] |
| Transparency | **B−** | Real technical blogging on AI-bot traffic; no published false-positive or legitimate-agent block rates |
| False-positive handling | **C** | Autotuning is claimed to reduce misclassification [VENDOR]: but our index holds two Akamai properties at the hardest verdict we assign |
| Net effect on legitimate agents | **C−** | eBay and w3schools are WALLED to an identified agent, and eBay's developer portal was walled too [MEASURED] |

## Where credit is due

- **Web Bot Auth is a documented Akamai capability, in Akamai's own
  words:** "Web Bot Auth is already supported by Akamai's bot &
  abuse solutions… the Akamai edge retrieves the bot's signature
  directory, validates the signature using RFC 9421 rules," and a
  valid signature classifies the request as validated-bot traffic
  on which customers can set policy [VENDOR: akamai.com blog,
  "Redefine Trust with Web Bot Authentication"]. An independent
  survey of edge providers likewise records documented public
  support [SOURCE: aiwebsignals.com]. This is the standard, shipped.
- **The AI-bot directory got more honest, not just bigger.** Akamai
  split its single "AI Bots" category into AI training crawlers, AI
  search crawlers, and AI fetchers/agents, explicitly so customers
  can "move beyond blanket block or allow rules" [VENDOR:
  akamai.com blog, "Introducing More Granular Controls for AI Bot
  Traffic"]. Granularity is the difference between a wall and a
  policy. (The wider known-bot directory is described in Akamai
  materials at 1,750 entries [VENDOR product brief].)
- **Responses are a dial, not a switch.** Bot Manager offers scores
  (0-100), per-endpoint thresholds, and actions including serve
  alternate content, challenge, and slow [VENDOR: akamai.com,
  "What Is Bot Mitigation?"]. Owners who want nuance can buy it
  here more readily than anywhere else in this series.

## Where it hurts: measured

Akamai held two of the six WALLED verdicts in our 154-row index at
Wave 4: the hardest verdict we assign, reserved for walls with no
challenge path an agent can answer. Current index (500 rows,
Wave 26 re-verified): Akamai holds 22 of the 37 WALLED rows: the
largest single-vendor share of hard walls in the index:

- `www.ebay.com`: **WALLED**, Akamai, HTTP 403 [MEASURED:
  INDEX.md, commerce], an edgesuite error page carrying no path
  forward for an identified agent. And the front doors are walled
  too: `developer.ebay.com` probed WALLED in Wave 2 [MEASURED:
  validation/wave2]: eBay was the one Wave 2 property whose
  developer surface was *more* closed than its peers', not less.
  (Its `robots.txt`, to be recorded fairly, was served OPEN.)
- `www.w3schools.com`: **WALLED**, Akamai, HTTP 403 [MEASURED:
  INDEX.md, docs/learning]: an edgesuite reference error page
  (that verdict's missing vendor attribution was Wave 3 problem
  W3-002; the wall itself reproduced in all three rounds).
  w3schools is a *tutorial site*: the canonical "learn to code"
  front door for beginners worldwide. The apex domain served while
  the `www` host walled [MEASURED]: an inconsistency that suggests
  configuration drift, not considered policy, which is its own kind
  of finding.

The autotuning claim: Bot Manager "learns normal traffic patterns
and automatically tunes detections to avoid potentially
misclassifying requests" [VENDOR]: is aimed at exactly this
problem. Three rounds of measurement say that for identified
agents, on these properties, it has not arrived [POSITION, on
MEASURED evidence].

We also note the asymmetry the campaign keeps finding: the actors
these walls exist to stop run full browsers and clear Bot Manager
detections routinely enough to sustain an industry. The traffic
that arrives with its name on: one request, honest user-agent,
no evasion: is the traffic that gets the error page [POSITION].

## The asks

1. **Make validated-bot the default classification outcome, not a
   policy the customer must discover.** Akamai already verifies
   signatures at the edge. A request with a valid Web Bot Auth
   signature should land in the console pre-classified as a
   validated bot with a recommended-allow default for read-only
   public content, so that blocking a *verified* agent is always a
   deliberate owner choice, never an accident of thresholds.
2. **Fix the drift: audit protected properties for www/apex and
   surface inconsistencies.** If the apex serves and `www` walls,
   one of them is wrong. A Bot Manager consistency report : 
   well-known paths, developer subdomains, apex vs www: would
   catch the w3schools pattern across the customer base.
3. **Publish legitimate-agent outcomes.** Akamai's view of bot
   traffic is the broadest in the industry. A periodic aggregate : 
   share of identified/verified agent requests allowed, challenged,
   blocked: would set the transparency bar for every other vendor
   in this series.

## What would raise these grades

- eBay-class and w3schools-class properties serving verified signed
  agents by default → Net effect and False-positive handling up.
- A published validated-bot default policy → Standards A-range.
- Legitimate-agent outcome statistics → Transparency A-range.

Errors in this card will be corrected publicly, with the correction
noted, on the same terms we offered Cloudflare.

## Sources

- Akamai, "Redefine Trust with Web Bot Authentication" (edge
  verification, validated-bot classification):
  https://www.akamai.com/blog/security/redefine-trust-web-bot-authentication
- Akamai, "Introducing More Granular Controls for AI Bot Traffic":
  https://www.akamai.com/blog/security/introducing-more-granular-controls-ai-bot-traffic
- Akamai, "What Is Bot Mitigation?" (Bot Score, actions, autotuning):
  https://www.akamai.com/glossary/what-is-bot-mitigation
- AIWebSignals, "Web Bot Auth Support Across Five Edge Providers":
  https://aiwebsignals.com/research/web-bot-auth-edge-support
- wallcheck Bot Wall Index (eBay, w3schools rows), Wave 2 path
  probing, Wave 3 problems W3-002: `INDEX.md`,
  `validation/wave2/PATHS.md`, `validation/wave3/PROBLEMS.md` in
  this repository.
