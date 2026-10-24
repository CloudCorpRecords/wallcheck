# The Bot Wall War — Campaign Plan

**A lawful public campaign against indiscriminate bot walls.**
Run by Rene Turcios / CloudCorpRecords. Weapon of choice: `wallcheck`
(measurement) + the Bot Wall Index (daylight) + Web Bot Auth (standards).

> "We don't have to break the law to fight bullies." — Rene Turcios,
> 2026-10-23, after Cloudflare's wall on Upwork burned an afternoon of
> legitimate, authenticated work on his own account.

## Mission

**No agent doing lawful work for an identified principal should be
stopped by a wall that cannot say what it is, who operates it, or how to
appeal it.**

Bot walls are not the enemy. Abuse is real, scraping for model training
without consent is a real grievance, and site owners have every right to
decide who gets in. The enemy is the *indiscriminate* wall: the one that
cannot tell a spammer from a freelancer's agent publishing a portfolio
on the freelancer's own account, that loops a challenge forever, that
offers no name, no evidence, and no appeal. Those walls don't just stop
bots. They quietly tax everyone the network already disadvantages —
and right now nobody measures them. We will.

## Why now (the receipts we already hold)

- **2026-10-23, our own session:** Cloudflare's wall on a single
  platform cycled a working browser through roughly ten environment
  replacements, invalidated every file-transfer grant bound to those
  browsers, and cost hours on a basic task — publishing two portfolio
  drafts on an account whose owner was present and consenting. The wall
  never identified itself in any machine-readable way. (SPEC.md has the
  full incident.)
- **Bot Wall Index, Wave 1 (2026-10-24):** 58 sites probed with an
  honestly identified agent. Result: 47 OPEN · 4 WALLED · 4 CHALLENGED ·
  3 UNREACHABLE. Eight walls, five vendors — and freelance is the most
  walled category measured: **3 of 7 freelance platforms stop an
  identified agent at the door** (Upwork/Cloudflare, Fiverr/PerimeterX,
  Guru/Imperva), while Contra, Freelancer, PeoplePerHour, and Toptal
  serve. Full table: `validation/wave1/INDEX-SEED.md`.

## The five lawful fronts

### Front 1 — MEASURE: the Bot Wall Index at scale

A wall nobody measures is a wall nobody has to defend. The Index turns
private frustration into public, checkable data.

- **Scale:** 58 seed sites → 150 (week 1) → **500 (day 30)**. Categories:
  freelance marketplaces, job boards, dev platforms and registries,
  docs and publishing, social, big web, government and public services,
  banking/finance (read-only public pages), health and education
  portals, and our own properties first (dogfood rule).
- **Cadence:** full re-scan weekly; daily delta scans on the 50 most
  consequential targets (the ones agents actually work through).
- **Methodology (published, not vibes):** one honest fetch per target
  with wallcheck's identified user agent; verdict + vendor + evidence
  recorded verbatim; scan context (network class, client) always
  disclosed; classifier is deterministic, so every verdict is
  reproducible and every historical change is a diff, not an opinion.
  When a wall comes down, the Index says so, loudly — credit is part of
  the weapon.
- **Growth rule:** targets are added because agents need them, not to
  pad the count. Every entry must be a place a person might lawfully
  send an agent to work.

### Front 2 — IDENTIFY: make signed agents the default

Anonymous traffic is unjudgeable traffic. The fix already exists as a
standard; it needs adoption, not invention.

- **Ship the signer:** wallcheck v0.2 `keygen`/`sign` — Ed25519 keys,
  HTTP Message Signatures (RFC 9421), per the Web Bot Auth proposal
  Cloudflare itself co-authored. Any agent builder can sign in an
  afternoon.
- **Publish the lists:** a public **Signing Agents** list (agents and
  frameworks that sign, with their key directories) and an **Accepting
  Sites** list (sites that honor Web Bot Auth / verified-bot
  signatures, verified by signed probe, not by press release).
- **The argument, in public:** a wall that blocks a *signed* agent is
  making a policy choice about an identified party — and can be asked
  to defend it. A wall that blocks anonymous traffic is doing hygiene.
  Signing moves every legitimate agent from the second category to the
  first. "Unsigned and anonymous" has to stop being the default
  assumption the walls are tuned against — and signing is how agents
  make that happen from our side of the fence.

### Front 3 — OPEN THE FRONT DOORS: sanctioned routes, documented

For every walled platform there is usually a door the owner *built*:
an official API, a partner program, an RSS feed, an official MCP
server, a data export. Agents get walled partly because these doors
are scattered, undocumented, or quietly closed. We document them.

- **FRONT-DOORS.md** (seed edition ships with this plan): every walled
  or challenged platform from the Index, its sanctioned route, and a
  source citation — or an explicit "no sanctioned route found."
- **Keep it current:** re-verify quarterly; a door that closes (an API
  deprecated, a publisher program shut to new applicants) is news and
  gets recorded with a date, the same way a wall coming down does.
- **The standard we push:** a platform that walls its website *and*
  offers no sanctioned route has made agent access impossible, not
  merely inconvenient. The Index will say exactly that, with citations.

### Front 4 — HELP OWNERS FIX IT: most walls are accidents

A default ruleset in front of a docs page, a public API, or a pricing
page the owner *wants* read is not malice — it's a default nobody
audited. Vendors ship the defaults; owners inherit them; agents pay.

- **Owner-side audit** (wallcheck `audit`, v0.2): robots.txt AI/agent
  directives, `llms.txt`, sitemap/feed/API escape routes — findings
  with severity and the exact fix.
- **Verified-bot exemption guides, per vendor, Cloudflare first:**
  how to exempt verified bots and signed agents from managed
  challenges on public paths without weakening protection on
  authenticated ones. Step by step, from the vendor's own dashboard.
- **Outreach that helps, not hectors:** when the Index catches a wall
  in front of something obviously public (docs, a package registry's
  website, a job board's listings), the owner gets a short note: the
  evidence, the likely default that caused it, and the fix. Fixes get
  credited in the Index history.

### Front 5 — TELL THE STORY: data-backed public writing

Measurement nobody reads changes nothing. Every claim we publish is
either our measured data (labeled, with methodology) or a cited source.
No vibes, no borrowed outrage.

- **Launch post** — `LAUNCH-POST.md` (ships with this plan).
- **Ship Log newsletter issue** — the long version: the incident, the
  Index, the five fronts, what readers can do (owners: audit your
  wall; builders: sign your requests).
- **Per-vendor report cards** — Cloudflare first
  (`REPORT-CARD-CLOUDFLARE.md`): fair, cited, updated as they respond.
  PerimeterX, DataDome, Akamai, Imperva follow on the same template.
- **The collateral-damage angle — measured, or marked "to measure":**
  the same signals that stop agents also stop people, and we will not
  claim what we haven't measured:
  - **MEASURED (ours):** network-class punishment. Our identified
    agent was walled from a datacenter IP while the same work
    succeeded from the owner's normal session — shared, corporate,
    campus, and hospital networks are exactly the IPs that inherit
    other people's reputations. (Wave 1 scan context + 2026-10-23
    incident.)
  - **TO MEASURE:** challenge friction for screen-reader and other
    assistive-technology users (challenge UX is historically hostile
    to them; we will test with assistive tooling before claiming).
  - **TO MEASURE:** VPN and privacy-tool users inheriting flagged
    exit-node reputations.
  - **TO MEASURE:** shared-network collateral — hospital, campus,
    library, and shelter networks whose egress IP is one abuse report
    away from a wall for every patient, student, and patron behind it.
  - **TO MEASURE:** older devices and low-end hardware that fail or
    time out on heavyweight JavaScript challenges.
  Each "to measure" item gets a methodology and a probe plan before it
  gets a headline. If the data says the harm is small, we publish that
  too.

## What we will NEVER do

This list is permanent, and it is the campaign's credibility:

- No CAPTCHA solving or human-verification farming.
- No fingerprint, user-agent, or TLS spoofing; no "undetected" browser
  tooling. Our probes identify themselves, always.
- No bypassing, evading, or defeating a wall, rate limit, or access
  control — including proxy or identity rotation to get around one.
- No scraping in violation of a site's terms. If the front door is
  closed and the terms say no, the answer is the Index entry and the
  report card — daylight, not a crowbar.
- No inflated claims. Measured data labeled as measured; vendor claims
  labeled as vendor claims; unknowns labeled unknown.

## Success metrics

| Metric | Day 30 target | Why it matters |
| --- | --- | --- |
| Bot Wall Index size | 500 targets, weekly cadence running | The map is the pressure |
| Walls attributed | 100% of non-OPEN verdicts named to a vendor | An unnamed wall is an unaccountable wall |
| Signing agents listed | 10+ agents/frameworks shipping RFC 9421 signing | Identity becomes normal |
| Accepting sites verified | Every claimed Web Bot Auth acceptor probe-verified | Press releases don't count; probes do |
| Owner exemptions | 5+ owners add verified-bot/signed-agent exemptions after outreach | Walls fixed, not just named |
| Front doors opened | 2+ platforms open or document an official agent path (API/MCP/feed) | The end state: doors, not walls |
| Report cards | 5 vendors, published and kept current | Fair, cited, permanent |

A metric we will *not* chase: "walls bypassed." That number stays zero
forever, on purpose.

## 30-day sequence

- **Days 1–3 — Ship the evidence.** wallcheck public release; Index
  seed (58) published with methodology; launch post out; FRONT-DOORS
  seed edition live. Cloudflare report card published.
- **Days 4–7 — Scale the map.** Index to 150 targets (job boards,
  registries, docs, government services added); daily delta scans on
  the top 50 begin; first owner-outreach batch (walls in front of
  obviously public resources).
- **Week 2 — Identity.** wallcheck v0.2: keygen/sign + `audit`.
  Signing Agents and Accepting Sites lists open. Our own agents sign
  everything, first — dogfood rule.
- **Week 3 — Fix-it campaign.** Cloudflare verified-bot exemption
  guide published; PerimeterX/DataDome/Akamai/Imperva report cards;
  second outreach batch with audit reports attached; Ship Log issue.
- **Week 4 — 500 and pressure.** Index to 500 targets; first
  month-in-review post (walls up, walls down, doors opened, owners
  credited); vendor responses (or non-responses) recorded on the
  report cards; next quarter's target list opened to community
  nomination.

## The one-sentence version

They built walls that can't tell a worker from an attack; we're
building the measurements, the identity standard, and the public record
that make them learn the difference — lawfully, in the open, with
receipts.
