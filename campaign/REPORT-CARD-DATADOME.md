# Report Card: DataDome

**Vendor:** DataDome (Bot Protect; Agentic Trust)
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
| Standards & identity | **B+** | The most documented verification menu of the four vendors graded: Web Bot Auth signatures, reverse-DNS, IP lists, ASN [VENDOR docs] |
| Owner controls | **A−** | Per-bot response settings, agent categories with Trust Scores, intent-based default policies [VENDOR docs] |
| Transparency | **B−** | Publishes a real industry benchmark report; its accuracy numbers are its own |
| False-positive handling | **C−** | A genuine registration route exists: but it is form-gated, vendor-approved, and unknown agents are blocked by default [VENDOR docs] |
| Net effect on legitimate agents | **C−** | Fifteen properties in our index challenge the identified agent, including three of the world's biggest news publishers [MEASURED] |

## Where credit is due

- **Cryptographic verification is documented, not just claimed.**
  DataDome's own bot-authentication documentation states it "can
  cryptographically verify http signatures using the Web Bot Auth
  protocol, based on the HTTP Message Signatures standard": and
  lists the alternatives alongside it (two-way RDNS/DNS, published
  IP lists, ASN) [VENDOR: docs.datadome.co/docs/bot-authentication].
  Of the four vendors in this series, DataDome's identity menu is
  the easiest for an agent operator to find and read.
- **The default posture toward known agents is more nuanced than
  block.** DataDome documents four AI-agent categories with Trust
  Scores, and states that by default most agents get an
  "Intent-Based" policy: traffic is allowed unless a fraud attempt
  is detected: with LLM-training collectors the stated exception
  [VENDOR: docs.datadome.co activation checklist]. That is a real,
  owner-visible policy design, and it is the shape we ask other
  vendors for.
- **It measures the ecosystem and publishes.** DataDome's *State of
  Bot & Agent Security Report 2026* tested 21,491 websites and
  reported that 65.3% were completely unprotected against its test
  bots, with full protection down to 2.4% [VENDOR report, summarized
  SOURCE: ppc.land]. We do not have to agree with the framing : 
  "unprotected" is a vendor's word for "did not stop our bots": to
  credit the publication of method and numbers.
- **Its own report makes our identity argument.** The same report
  found that more than 7 in 10 sites let a *spoofed* AI agent
  through simply for claiming a trusted user-agent name [SOURCE:
  ppc.land summary of the report]. Identity by assertion fails;
  identity by signature is the fix. DataDome sells that fix. We are
  asking it to make the fix reachable.

## Where it hurts: measured

DataDome is the most frequent challenger of identified agents in
our index: 15 of the 26 CHALLENGED rows. Fifteen properties, all
answering an honestly identified, one-shot agent request with a
challenge (HTTP 403 or 401); the five majors:

- `www.monster.com`: **CHALLENGED**, DataDome, 403 [MEASURED:
  INDEX.md, jobs]. A job board. The people most likely to send an
  identified agent to Monster are job seekers.
- `www.nytimes.com`: **CHALLENGED**, DataDome, 403 [MEASURED:
  INDEX.md, news]. The nuance we record: `developer.nytimes.com`
  probed OPEN in Wave 2 [MEASURED]: the developer front door is
  open; the publication itself is not.
- `www.etsy.com`: **CHALLENGED**, DataDome, 403 [MEASURED:
  INDEX.md, commerce]: a marketplace of small sellers whose
  customers increasingly arrive via agents.
- `www.reuters.com`: **CHALLENGED**, DataDome, 401 [MEASURED:
  INDEX.md, news].
- `www.wsj.com`: **CHALLENGED**, DataDome, 401 [MEASURED:
  INDEX.md, news].

Against that, the vendor's published accuracy framing: detection
"classifies traffic with 99.99% accuracy and a false positive rate
below 0.01%" [VENDOR, via its marketplace/reseller materials]. Both
things can be true at once, and that is precisely the problem this
card names: a false-positive rate measured against *human* traffic
says nothing about the rate at which *identified legitimate agents*
are stopped. Our agent is not a measurement error in their model : 
it is a policy outcome: "any automated request coming from an
unauthenticated bot or AI agent is categorized as Threat Detection
and is blocked by default" [VENDOR: docs.datadome.co/docs/bot-authentication].
Blocked-by-default for the unauthenticated is a defensible security
posture. What is missing is a low-friction way to *become*
authenticated that does not run through a vendor review queue
[POSITION].

## The asks

1. **Self-serve Web Bot Auth registration.** The signature
   verification exists. Let an agent operator register a key
   directory URL and a dedicated user-agent automatically: the
   way RDNS verification is automatic for search engines: instead
   of by form submission and vendor approval. The form can remain
   as the appeal path; it should not be the front door.
2. **Publish the identified-agent block rate alongside the
   false-positive rate.** One number for humans, one for identified
   agents, per quarter. DataDome already publishes more ecosystem
   data than its peers; this is the number its peers will then have
   to match.
3. **Ship a machine-readable challenge.** When DataDome challenges
   an identified agent, the response should carry the registration
   and signature-verification routes in a form the agent can act on
   (header or well-known reference), not only a browser CAPTCHA.
   An agent that learns how to identify itself stops being a
   support burden for everyone.

## What would raise these grades

- Self-serve signature registration live → Standards A-range,
  False-positive handling up.
- The five measured properties serving verified signed agents →
  Net effect up.
- Identified-agent block rates published → Transparency A-range.

Errors in this card will be corrected publicly, with the correction
noted, on the same terms we offered Cloudflare.

## Sources

- DataDome documentation, "Bot Authentication" (Web Bot Auth
  verification, block-by-default for unauthenticated agents,
  registration form): https://docs.datadome.co/docs/bot-authentication
- DataDome documentation, activation checklist (agent categories,
  Trust Score, intent-based defaults):
  https://docs.datadome.co/docs/checklist-before-activating-protection
- DataDome, *State of Bot & Agent Security Report 2026*:
  https://datadome.co/wp-content/uploads/2026/09/State-of-Bot-Agent-Security-Report_2026-Final.pdf
- ppc.land, "Full bot protection drops to 2.4% of popular websites,
  DataDome finds": https://ppc.land/full-bot-protection-drops-to-2-4-of-popular-websites-datadome-finds/
- wallcheck Bot Wall Index (Monster, NYT, Etsy, Reuters, WSJ rows)
  and Wave 2 path probing: `INDEX.md`, `validation/wave2/PATHS.md`
  in this repository.
