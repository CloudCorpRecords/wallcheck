# Report Card: Imperva (Thales) Advanced Bot Protection

**Vendor:** Imperva, a Thales company (Advanced Bot Protection)
**Graded by:** the wallcheck campaign (Rene Turcios / CloudCorpRecords)
**Date:** October 2026 (Bot Wall Index rounds 1–3)
**Companion:** `REPORT-CARD-CLOUDFLARE.md` — same rubric, same
standard. Grades are ours; vendor claims are tagged as vendor claims.

Every factual claim below is tagged: **[MEASURED]** (our index /
probes), **[VENDOR]** (the vendor's own published claim),
**[SOURCE]** (a cited third-party or primary source), **[POSITION]**
(our argument).

## Scorecard

| Dimension | Grade | One-line basis |
|---|---|---|
| Standards & identity | **D** | No public Web Bot Auth or signature-verification support found; identity is a proprietary classification database, closed to the agent it classifies |
| Owner controls | **B** | Customers can customize good/bad bot lists, exceptions, and per-bot policies [VENDOR docs] |
| Transparency | **C−** | Publishes AI-bot policy guidance; no false-positive rates, no agent-outcome data |
| False-positive handling | **D** | "Unidentified" is suspicious by default [VENDOR docs], and there is no route by which a new legitimate agent can stop being unidentified |
| Net effect on legitimate agents | **D** | The one Imperva property in our index is walled on every path we probed — the index's only whole-domain wall [MEASURED] |

## Where credit is due

- **The classification model is explicit about its categories.**
  Imperva's documentation states plainly how it sorts traffic —
  human, good bot, bad bot, or *unidentified* — and that customers
  can customize the good/bad lists and define exceptions [VENDOR:
  Thales/Imperva docs, "Bot Mitigation"]. Owners are not flying
  blind; the console model is legible.
- **Its public guidance on AI bots is genuinely policy-shaped.**
  Imperva's own AI-bot traffic guidance recommends differentiated
  handling — allow AI search bots on public content, review
  training bots, allow fetch bots with inspection and rate controls
  — rather than blanket blocking [VENDOR: imperva.com blog, "AI
  Bot Traffic: Which Bots to Allow or Block"]. That is the right
  advice. Our measured complaint is that the product's default
  treatment of an *unknown* agent makes the advice hard to follow
  for anyone not already in the database.
- **The human false-positive engineering is serious.** Imperva
  states that where customers select CAPTCHA as a response,
  legitimate users are not served one on 99.999% of requests
  [VENDOR: imperva.com ABP FAQ], and its Bot Confidence model
  publishes interpretable tiers (high/medium/low/none) with
  recommended actions [VENDOR: imperva.com ABP resources]. For
  human visitors, this is careful work.

## Where it hurts — measured

- `www.guru.com` — **WALLED**, Imperva, HTTP 403 [MEASURED:
  INDEX.md, freelance] — and not just the homepage. In Wave 2 path
  probing, Guru was the **only whole-domain wall in the set**:
  landing, jobs, login, robots.txt, sitemap, llms.txt — every
  probed path returned the same Imperva wall (Incapsula incident
  page, `_Incapsula_Resource` challenge) [MEASURED:
  validation/wave2/PATHS.md]. Even the files a site publishes
  *specifically for machines* were behind it.
- Guru is a freelance marketplace. The population with the most
  legitimate reason to send an identified agent to it — freelancers
  and the people hiring them — is the population the wall excludes
  most completely [POSITION, on MEASURED evidence].

The structural problem is in Imperva's own documentation: "By
default, we treat an unidentified bot as suspicious because it is
an unknown" [VENDOR: Thales/Imperva docs]. Pair that with the
identity model — classification happens in Imperva's client
database; exceptions are granted by the *customer*, per Client App
ID, for bots Imperva already knows [VENDOR: imperva.com blog] —
and a new legitimate agent has no move to make. It cannot sign a
request Imperva will verify (no signature verification is publicly
documented; we searched for Web Bot Auth support and found none —
if it exists, it is not discoverable, which for an agent operator
is the same thing). It cannot register itself. It can only wait to
be classified by a database it cannot see, while being treated as
suspicious for not being in it [POSITION, grounded in the VENDOR
docs above].

Every other vendor in this series has at least begun the move from
identity-by-database to identity-by-cryptography. As of this card,
Imperva has not publicly begun [POSITION, per our searches cited
below].

## The asks

1. **Verify Web Bot Auth signatures, and say so in the docs.**
   RFC 9421 verification at the edge is shipped by Cloudflare,
   Akamai, AWS WAF, HUMAN, and DataDome. A signed request should be
   a first-class classification input — the strongest possible
   answer to "who are you?", which Imperva's own docs name as the
   first question bot mitigation asks.
2. **Give "unidentified" a graduation path.** A published route by
   which an agent operator can register an identity (key directory,
   dedicated user-agent, contact) and be reclassified on evidence —
   with a stated timeline. Suspicious-by-default is a starting
   posture, not a life sentence.
3. **Stop walling the machine-readable surface by default.**
   robots.txt, sitemap.xml, and llms.txt exist to be read by
   machines. The default ABP policy template should serve them
   (rate-limited if need be) even on protected properties, so a
   site's own published machine surface is not collateral in its
   bot policy.

## What would raise these grades

- Documented signature verification → Standards up by letter
  grades; it is the single largest gap in this series.
- A self-identification/registration route for new agents →
  False-positive handling up.
- Guru-class properties serving their machine-readable paths →
  Net effect up.

Errors in this card will be corrected publicly, with the correction
noted, on the same terms we offered Cloudflare. If Imperva ships
signature verification and we missed it, we will correct this card
prominently — that correction is one we would be glad to publish.

## Sources

- Thales/Imperva documentation, "Bot Mitigation" (client
  classification; unidentified treated as suspicious by default;
  customizable good/bad lists):
  https://docs-cybersec.thalesgroup.com/bundle/cloud-application-security/page/settings/auto-mitigation.htm
- Imperva blog, "AI Bot Traffic: Which Bots to Allow or Block"
  (differentiated AI-bot policy; exceptions by Client App ID):
  https://www.imperva.com/blog/ai-bot-traffic-which-bots-to-trust/
- Imperva, Advanced Bot Protection product page (99.999%
  no-CAPTCHA claim for legitimate users):
  https://www.imperva.com/products/advanced-bot-protection-management/?redirect=Distil
- Searches for Imperva Web Bot Auth / HTTP Message Signatures
  support, run October 2026 for this card, returned no vendor
  documentation of signature verification.
- wallcheck Bot Wall Index (Guru row) and Wave 2 path probing:
  `INDEX.md`, `validation/wave2/PATHS.md` in this repository.
