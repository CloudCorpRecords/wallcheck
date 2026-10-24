# Report Card: Cloudflare

**Subject:** Cloudflare, Inc.: bot management, managed challenges,
and agent access.
**Issued by:** the wallcheck campaign (Rene Turcios /
CloudCorpRecords), 2026-10-24. First edition; will be updated as
Cloudflare responds or the data changes.
**Rules of this document:** every factual claim is either (a) our
measured data, labeled **[MEASURED]** with methodology, (b) a
Cloudflare statement, labeled **[VENDOR]** with a source, or
(c) a secondary source, labeled **[SOURCE]** with a link. Our opinions
are labeled **[POSITION]**. If we got something wrong, we will correct
it in the open, with a dated erratum: that offer stands to Cloudflare
in writing, here.

## Grades (ours, argued below)

| Dimension | Grade | One-line basis |
| --- | --- | --- |
| Standards leadership | **A** | Co-authored the identity standard the whole industry needed |
| Identity infrastructure | **B+** | Web Bot Auth + Verified Bots exist and work: but opt-in on both ends |
| Owner controls | **A−** | AI Crawl Control / Pay Per Crawl give owners real, granular choice |
| False-positive handling | **D** | No published false-positive rate, no appeal path with an SLA that we could find |
| Net effect on legitimate agents | **D+** | Our measured data: identified, lawful agent traffic hard-walled on major platforms |

**Overall: a company building the right future and shipping the wrong
defaults.** Cloudflare is simultaneously the best actor in this space
and the wall our agent hit most. Both facts are in the record below.

## What Cloudflare does well (credit, with sources)

1. **They wrote the standard.** Web Bot Auth: bots and agents
   cryptographically signing requests with HTTP Message Signatures
   (RFC 9421), keys published as a JWKS directory: was proposed by
   Cloudflare (with the IETF draft `draft-meunier-web-bot-auth-
   architecture`) in May 2025, precisely because user-agent strings
   and IP ranges cannot tell a wanted agent from an impersonator.
   **[VENDOR]** https://blog.cloudflare.com/web-bot-auth/ (via the
   follow-up post at https://blog.cloudflare.com/verified-bots-with-cryptography/)
   **[SOURCE]** https://ppc.land/web-bot-auth/
2. **They wired identity into the product.** Message Signatures are
   integrated into the Verified Bots program, and Cloudflare states
   that verified bots "do not face challenges from our Bot Management"
   because they are already identified: identity in, challenges off.
   That is exactly the bargain this campaign wants everywhere.
   **[VENDOR]** https://blog.cloudflare.com/verified-bots-with-cryptography/
3. **They extended it to user-directed agents.** The "signed agents"
   work recognizes that an agent acting for an end user is a different
   thing from a crawler acting for a company, and gives that traffic a
   classification and an application path. **[VENDOR]**
   https://blog.cloudflare.com/signed-agents/
4. **They gave owners real controls.** AI Audit (launched September
   2024, since evolved into AI Crawl Control) lets owners see AI
   crawlers per-bot and allow, block, or charge each one; Pay Per
   Crawl (private beta, July 2025) makes access machine-negotiable
   via HTTP 402 instead of silently binary. Owners choosing their
   policy: explicitly, per bot: is the healthy end state.
   **[SOURCE]** https://www.siteauditlint.com/blog/cloudflare-for-seo ·
   https://guptadeepak.com/who-is-buying-building-ai-visibility/
5. **They publish.** A public bots directory, engineering posts on
   methodology, participation in the IETF process. Sunlight is their
   house style more often than their competitors'. **[POSITION,
   based on the sources above]**

## Where the harm is (evidence)

1. **[MEASURED] Identified, lawful agent traffic is hard-walled on
   Cloudflare-protected platforms.** Bot Wall Index, Wave 1
   (2026-10-24): one honest fetch per target, wallcheck's identified
   user agent, datacenter egress IP. Results behind Cloudflare:
   `www.upwork.com` → **WALLED** (403, "Sorry, you have been
   blocked"), `medium.com` → **WALLED** (403), `www.npmjs.com` →
   **CHALLENGED** (403). Full methodology and evidence:
   `../validation/wave1/INDEX-SEED.md`. Context matters and we state
   it: a datacenter IP is the hardest case: which is the point. VMs,
   CI runners, and cloud desktops *are* where agents legitimately
   live.
2. **[MEASURED] The wall ate a working day and never said its name.**
   2026-10-23: Cloudflare's wall on one platform cycled an
   authenticated browser session through roughly ten environment
   replacements, broke every file transfer bound to that session, and
   cost hours on a portfolio publish its account owner had explicitly
   directed. At no point did the wall present a machine-readable
   identity, reason, or appeal route to the agent it was stopping.
   (Incident record: `../SPEC.md`.)
3. **[MEASURED: our observation] Challenge loops exist.** During
   that same session, challenges repeatedly verified-then-reset : 
   "prove you're human, again": with no escalation path and no
   terminal error. A wall that cannot complete its own challenge is
   not a security control; it's a tarpit.
4. **No published false-positive rate.** In preparing this card we
   could find no false-positive rate for Cloudflare's managed
   challenges or bot scores, and no public error budget. A system
   that fronts a large share of the web and makes identity decisions
   at that scale should publish its measured error rate the way it
   publishes its attack statistics. If the number exists somewhere we
   missed, we will cite it in an erratum the day it's shown to us.
   **[POSITION: based on our research, Oct 2026]**
5. **Defaults are policy.** Cloudflare flipped new domains to
   blocking AI crawlers by default on 2025-07-01 and has expanded
   default blocking since, including for existing free-plan
   customers. Defaults decide for the owners least likely to audit
   them: the docs site, the indie marketplace, the job board: and
   those owners' visitors pay for a choice nobody remembers making.
   **[SOURCE]** https://novaknown.com/2026/07/02/cloudflare-blocks-ai-crawlers-default/ ·
   https://blog.rudrakasturi.com/should-you-block-ai-crawlers-pay-per-crawl-and-the-new-rules-explained/
6. **Charging doesn't fix false positives.** Pay Per Crawl prices
   *crawlers*. The freelancer's agent publishing a portfolio, the
   job-seeker's agent reading a listing, the researcher's agent
   checking a public doc: none of them are a monetizable crawl, and
   a toll booth is not an appeal process. **[POSITION]**

## The three asks

Concrete, implementable, and consistent with Cloudflare's own stated
direction:

1. **Honor signed agents by default in managed rules.** Cloudflare
   already validates Web Bot Auth signatures at the edge and already
   exempts Verified Bots from challenges. Extend the default: traffic
   with a *valid* Web Bot Auth signature from a registered directory
   should not receive a managed challenge by default, on any plan.
   Site owners can opt out per rule; abuse stays actionable because a
   signed identity can be revoked: which is the entire point of
   identity.
2. **A real false-positive appeal path, with an SLA, for account
   holders.** When a platform's wall blocks its own authenticated
   customer doing customer things (the 2026-10-23 pattern), there
   should be a named channel: in-product, not a forum thread: with
   a response-time commitment (we propose: acknowledgment in 1
   business day, resolution or a named workaround in 5) and a case
   ID an agent can carry. Walls that can be appealed get fixed;
   walls that can't get routed around, and Cloudflare says it doesn't
   want that either.
3. **Publish false-positive rates.** Quarterly, per product (Managed
   Challenge, Bot Management), the measured share of challenges and
   blocks later determined to be legitimate traffic: methodology
   included. Cloudflare publishes some of the best attack data on the
   internet; the error side of the ledger deserves the same rigor.
   What's measured gets managed; right now the false positives are
   measured by nobody, which is why campaigns like this one exist.

## What would raise the grades

- Ask 1 shipped → Identity infrastructure to **A**, net effect up a
  full letter.
- Ask 2 shipped → False-positive handling to **B** on the spot, **A**
  after two quarters of SLA data.
- Ask 3 shipped → this card gets a "measurement" section instead of a
  complaint, and Cloudflare gets credited in every future edition.

We are not hard to convince. We are, in fact, running the
measurement infrastructure to prove them right if they do it : 
the Bot Wall Index re-scans weekly, and improvements show up in it
whether or not anyone sends us a press release.

*Corrections: open an issue against the wallcheck repo or reply to
the Ship Log issue. Errata will be dated, specific, and ungrouchy.*
