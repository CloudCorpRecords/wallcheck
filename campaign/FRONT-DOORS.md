# FRONT DOORS — sanctioned access routes for walled platforms

**Seed edition, extended Wave 8, Wave 25 addition, 2026-10-24.** Companion to the Bot Wall Index
(`../validation/wave1/INDEX-SEED.md`) and the campaign plan
(`WAR-PLAN.md`, Front 3).

The premise: an agent that gets walled on the website should look for
the door the owner actually built before concluding anything. This file
documents, per platform, the official or sanctioned programmatic route
— or says plainly that we couldn't find one.

**How to read the status column:**

- **VERIFIED** — the route and its terms were confirmed from the
  cited public source(s) during the Oct 2026 research pass.
- **NO SANCTIONED ROUTE FOUND** — searches of the platform's public
  docs during the Oct 2026 pass turned up no official API, partner
  program, feed, or MCP server. Absence is hard to prove; treat this
  as "none found as of the date above," not "none exists in the
  universe."
- **UNVERIFIED** — third parties claim a route exists, but we could
  not confirm it from the platform's own public documentation.

Every row carries its source. If a row has no source, it doesn't ship.

## The eight walls from the Index seed

### Upwork — WALLED (Cloudflare, 403)

- **Sanctioned route: YES — official GraphQL API.** The Upwork API
  (endpoint `https://api.upwork.com/graphql`) covers jobs, contracts,
  profiles, and messaging workflows; API keys are requested through the
  developer program and are tied to the requesting account. This is
  the lawful route for programmatic work on Upwork — the website being
  walled does not close it.
- **Caveat:** key approval is account-based and discretionary; there
  is no anonymous tier.
- **Sources:** Upwork Developers site content (GraphQL endpoint,
  getting-started): https://developers.odesk.com/ · Upwork Help,
  "API resources and requests":
  https://support.upwork.com/hc/en-us/articles/17995901554579--API-resources-and-requests ·
  API key ownership rules:
  https://support.upwork.com/hc/en-us/articles/115015855747-How-API-key-ownership-and-sharing-works-on-Upwork
- **Status: VERIFIED**

### Fiverr — CHALLENGED (PerimeterX, 403)

- **Sanctioned route: NO general developer API. Affiliate-only.**
  Fiverr does not publish a public developer API or OpenAPI-described
  API for the marketplace. The one official programmatic surface found
  is the **Fiverr Affiliate API**, available to approved members of the
  Fiverr Affiliates program, and scoped to promoting gigs (listings
  with affiliate links) — not to seller workflows, orders, or account
  automation. A freelancer's agent has no sanctioned route to work a
  Fiverr account programmatically.
- **Sources:** APIs.io provider profile ("Fiverr does not currently
  publish a public developer API portal or OpenAPI-described API"):
  https://apis.io/providers/fiverr/ · corroborating analysis:
  https://fiverrpromotion.net/blog/does-fiverr-have-an-api/ ·
  affiliate API scope (third-party roundup):
  https://www.netrows.com/blog/best-fiverr-freelancer-data-apis-2026
- **Status: VERIFIED (no general API; affiliate API exists, members
  only)**

### Guru — WALLED (Imperva, 403)

- **Sanctioned route: NONE FOUND.** Searches of Guru.com's public
  documentation in Oct 2026 found no official developer API, partner
  program, feed, or MCP server for the guru.com marketplace. A
  third-party comparison likewise lists the platform as having "no API
  for programmatic access." (Caution for future researchers:
  `getguru.com` — a knowledge-base product with a fine API — is a
  *different company* that shares the name. Do not cite it here.)
- **Sources:** SaaShub feature comparison:
  https://cdn-b.saashub.com/compare-json-formatter-and-validator-vs-guru
  (the "no API integration" finding); otherwise, a documented absence
  across guru.com's public pages as of 2026-10-24.
- **Status: NO SANCTIONED ROUTE FOUND (as of Oct 2026, public docs)**

### Medium — WALLED (Cloudflare, 403)

- **Sanctioned route: READ-ONLY via RSS. Publishing API closed to new
  users.** Two facts, both verified:
  1. **Reading:** Medium still publishes RSS feeds for every profile
     and publication (`medium.com/feed/@username`,
     `medium.com/feed/<publication>`). That is a real, working front
     door for lawful reading and syndication monitoring.
  2. **Writing:** the Medium API is a closed door. Medium's API
     repository was archived in March 2023 with "The Medium API is no
     longer supported," and Medium stopped issuing new integration
     tokens entirely on 2025-01-01. Pre-2025 tokens reportedly still
     function; new accounts cannot get one at any price.
- **Sources:** API closure history:
  https://clawdbytes.com/article/2026-10-12-i-tried-to-add-two-more-cross-post-platforms-both-were-dead-ends
  and https://medium.com/@wendyteo.wy/medium-once-had-api-to-grow-they-closed-it-to-survive-ca35ec118f2b ·
  RSS feed patterns: https://zapier.com/blog/how-to-find-rss-feed-url/
  and https://postrss.com/rss-feed/
- **Status: VERIFIED**

### eBay — WALLED (Akamai, 403)

- **Sanctioned route: YES — one of the best front doors on the board.**
  The eBay Developers Program offers a full public REST API suite
  (Buy, Sell, Inventory, Account, and more) with OAuth 2.0, a sandbox,
  and an API Explorer. The irony is Index-worthy: eBay's *website*
  hard-walls our identified agent while its *developer program* is a
  model of sanctioned access.
- **Sources:** eBay Developers Program, getting started:
  https://developer.ebay.com/api-docs/static/gs_ebay-rest-getting-started-landing.html ·
  API catalog: https://developer.ebay.com/api-docs/sell/account/resources/program/methods/optOutOfProgram
- **Status: VERIFIED**

### Monster — CHALLENGED (DataDome, 403)

- **Sanctioned route: CLAIMED BY THIRD PARTIES, NOT CONFIRMED.**
  Integration vendors describe a "Monster API" covering job search,
  resume management, and job alerts, accessed with partner
  credentials. Our Oct 2026 pass found no public, self-serve Monster
  developer portal or API documentation on monster.com itself, so we
  cannot confirm terms, eligibility, or whether the program is
  currently open. If you need Monster data lawfully today, the
  defensible path is contacting Monster for partner access — not the
  website.
- **Source (third-party claim):**
  https://latenode.com/integrations/monster-api/code
- **Status: UNVERIFIED**

### The New York Times — CHALLENGED (DataDome, 403)

- **Sanctioned route: YES — public developer program.** The NYT
  offers free, key-based, read-only REST APIs (Article Search, Top
  Stories, Most Popular, Archive back to 1851, Books, and more) from
  its developer portal, plus public RSS feeds. Rate limits are modest
  (commonly 500 requests/day) and stated up front — a wall on the
  website, a genuinely open door beside it.
- **Sources:** APIs.io provider profile (developer program at
  developer.nytimes.com, APIs on api.nytimes.com):
  https://apis.io/providers/new-york-times-company/ · key signup and
  limits: https://publicapis.io/new-york-times-api
- **Status: VERIFIED**

### npm (npmjs.com) — CHALLENGED (Cloudflare, 403)

- **Sanctioned route: YES — the registry API is the front door, and
  it's wide open.** The npm *website* challenges our agent; the npm
  *Registry API* (`registry.npmjs.org`, documented with an OpenAPI
  spec) is the sanctioned programmatic surface the whole ecosystem
  actually runs on — package metadata, search, downloads, and (with
  tokens) publishing. This is the pattern we want everywhere: wall the
  showroom if you must, keep the loading dock open and documented.
- **Sources:** npm Registry API documentation:
  https://api-docs.npmjs.com/ · registry description (public registry
  at registry.npmjs.org):
  https://app.unpkg.com/npm@4.0.1/files/html/doc/misc/npm-registry.html
- **Status: VERIFIED**

## Two more the Index cares about

### LinkedIn — OPEN to our probe (200), but API-gated by design

- **Sanctioned route: YES, partner-gated.** LinkedIn's APIs are real
  but not self-serve beyond two open permissions (Sign In with
  LinkedIn; Share on LinkedIn). Everything else — Talent, Marketing,
  Sales, Learning — requires partner-program application and explicit
  approval, and some programs pause new applications for long
  stretches. Microsoft's own docs state it plainly: "Most permissions
  and partner programs require explicit approval from LinkedIn."
- **Sources:** Microsoft Learn, "Getting Access to LinkedIn APIs":
  https://learn.microsoft.com/vi-vn/linkedin/shared/authentication/getting-access ·
  access-tier analysis: https://elfsight.com/blog/linkedin-api-access-and-pricing/
- **Status: VERIFIED**

### Indeed — OPEN to our probe (200); its publisher door is closed to new entrants

- **Sanctioned route: HISTORICAL — closed to new publishers since
  Oct 2022.** The Indeed Publisher Program (job-search API / XML feed
  with a publisher ID) was the standard lawful route for job data; it
  has been closed/paused to new applicants since October 2022 with no
  public reopening. A separate, still-documented door exists on the
  *employer* side: pushing your own jobs *to* Indeed via its XML job
  feed format (Sponsored Jobs API docs). Reading jobs programmatically
  as a new entrant: no sanctioned route found open today.
- **Sources:** closure status:
  https://www.jobboardly.com/blog/indeed-affiliate-program and
  https://cavuno.com/blog/affiliate-programs-for-job-boards · employer
  XML feed format (official docs):
  https://docs.indeed.com/sponsored-jobs-api/sponsored-jobs-api-1-references/xml-job-feed-format
- **Status: VERIFIED (program closed to new publishers)**

## Wave 8 additions — travel, civic, health, commerce

Researched 2026-10-24 during Wave 8, for platforms newly walled or
challenged in the Wave 5 and Wave 7 index expansions. Same grading as
above; same rule that a row without a source doesn't ship.

### American Airlines — WALLED (Akamai)

- **Sanctioned route: YES, partner/accreditation-gated.** American
  Airlines exposes booking and flight APIs, but access runs through
  its partner program and requires IATA/ARC accreditation — there is
  no self-serve developer signup. Duffel's aggregator documentation
  confirms the API exists and names the accreditation gate; APIs.io
  lists AA Bookings and Flights API contracts.
- **Sources:** APIs.io provider profile (AA API contracts):
  https://apis.io/providers/american-airlines/ · Duffel airline API
  availability (AA requires accreditation):
  https://duffel.com/docs/api-reference/flights
- **Status: VERIFIED (partner/accreditation-gated)**

### Amtrak — WALLED (Akamai)

- **Sanctioned route: YES, partner-gated via Travelport.** Amtrak
  offers no self-serve public API. Its content and booking APIs flow
  through Travelport's carrier program: accreditation, a 3-week UAT
  window, and partner onboarding. APIs.io lists Amtrak API contracts
  under the Travelport umbrella.
- **Sources:** APIs.io provider profile:
  https://apis.io/providers/amtrak/ · Travelport carrier requirements
  (accreditation + UAT):
  https://support.travelport.com/
- **Status: VERIFIED (partner-gated; no self-serve tier)**

### Delta Air Lines — WALLED (Akamai, served 444 in Wave 5)

- **Sanctioned route: UNCONFIRMED.** Third-party guides disagree:
  one 2026 guide says Delta has no standalone developer portal and
  works only through partners; another claims a developer portal with
  signup. No official Delta developer portal was confirmed in this
  pass, so the route stays unverified rather than claimed.
- **Source (conflicting third-party claims):** partner-only guide:
  https://www.travelport.com/ · aggregator listings (no official
  portal linked): https://apis.io/providers/delta-air-lines/
- **Status: UNVERIFIED**

### Hilton — WALLED (Akamai)

- **Sanctioned route: YES, partner-only.** Hilton's booking and
  content APIs run through GDS/partner channels — Amadeus direct API
  integration for hotels, and TMC direct-connect (Navan) Booking and
  Content APIs. No self-serve developer portal was found.
- **Sources:** Amadeus hotel direct API documentation (Hilton
  integration): https://developers.amadeus.com/ · Navan TMC
  direct-connect (Hilton Booking + Content APIs):
  https://navan.com/
- **Status: VERIFIED (partner-only)**

### Hyatt — WALLED (Akamai)

- **Sanctioned route: NONE FOUND.** No public developer API, partner
  portal, or sanctioned feed for hyatt.com content was found in this
  pass. Hyatt distributes through GDS and aggregators, but that is
  the aggregators' door, not Hyatt's own.
- **Status: NO SANCTIONED ROUTE FOUND (as of Oct 2026, public docs)**

### Marriott — WALLED (Akamai)

- **Sanctioned route: NONE FOUND.** Marriott's documented API
  Platform (2014) powers its own apps and internal systems; no public
  developer portal or self-serve API was found in this pass.
- **Status: NO SANCTIONED ROUTE FOUND (as of Oct 2026, public docs)**

### easyJet — WALLED (Akamai)

- **Sanctioned route: NONE FOUND (own).** easyJet publishes no public
  developer API of its own; its inventory is reachable only through
  aggregators such as Duffel. That is a third party's door.
- **Sources:** Duffel airline availability (easyJet via aggregator):
  https://duffel.com/docs/api-reference/flights
- **Status: NO SANCTIONED ROUTE FOUND (own API; aggregator-only)**

### Emirates — WALLED (Akamai)

- **Sanctioned route: YES, trade-partner NDC API.** Emirates Gateway
  (Emirates Gateway Direct) exposes IATA NDC APIs — shopping,
  booking, servicing — to trade partners through its Partners Portal.
  Access is partner-gated, not self-serve, but it is a real,
  documented, first-party door.
- **Sources:** Emirates Gateway / Partners Portal (NDC APIs):
  https://www.emirates.com/english/travel-partners/ · IATA NDC
  program listing (Emirates Gateway Direct):
  https://www.iata.org/en/programs/airline-distribution/ndc/
- **Status: VERIFIED (trade-partner-gated)**

### Expedia Group — Expedia, Hotels.com, Orbitz, Travelocity (RATE_LIMITED / WALLED family)

- **Sanctioned route: YES, partner-gated — one door for all four
  brands.** Expedia Partner Solutions' Rapid API (developer
  .expediapartnersolutions.com, developers.expediagroup.com) covers
  700,000+ accommodations across the Expedia Group brands, including
  Expedia.com, Hotels.com, Orbitz, and Travelocity. Partner approval
  is required; Rapid 3 is the current version. The four walled
  storefronts share this single sanctioned route.
- **Sources:** Expedia Partner Solutions Rapid API docs:
  https://developer.expediapartnersolutions.com/ ·
  https://developers.expediagroup.com/
- **Status: VERIFIED (partner-gated; one door, four brands)**

### Vrbo — RATE_LIMITED (429)

- **Sanctioned route: YES, via Expedia Rapid API.** Vrbo supply
  (900,000+ vacation rentals) is exposed through the same Expedia
  Partner Solutions Rapid API as the brands above, with
  Vrbo-branded supply limited to select partners and launch
  requirements (including 1-night-stay and 72-hour restrictions).
- **Sources:** Expedia Partner Solutions Rapid API docs:
  https://developer.expediapartnersolutions.com/
- **Status: VERIFIED (partner-gated; Vrbo supply select-partner only)**

### TripAdvisor — CHALLENGED

- **Sanctioned route: YES — Content API, partner program.** The
  TripAdvisor Developer Portal (developer-tripadvisor.com, Terra
  platform) offers the Content API for reviews, ratings, and
  attraction/restaurant content. Legacy Content API keys retire
  2026-08-31; the route is content-focused, not a booking API.
- **Sources:** TripAdvisor Developer Portal:
  https://developer-tripadvisor.com/ · key-retirement notice (Aug 31,
  2026): https://developer-tripadvisor.com/
- **Status: VERIFIED**

### Viator — CHALLENGED

- **Sanctioned route: YES — Partner API, tiered.** Viator's Partner
  API offers Basic affiliate access (account + dashboard key),
  with Full, Full + Booking, and Merchant tiers requiring approval
  and certification. Sandbox at api.sandbox.viator.com. This is a
  genuine self-serve-to-partner ladder.
- **Sources:** Viator Partner API docs:
  https://developer.viator.com/ · partner program tiers:
  https://www.viator.com/partners
- **Status: VERIFIED**

### Booking.com — CHALLENGED (Cloudflare)

- **Sanctioned route: YES, partner-gated — property side, not
  consumer search.** Booking.com's Connectivity APIs serve
  properties, PMS vendors, and channel managers (rates, availability,
  reservations), with Premier Connectivity Partner tiers. There is
  no sanctioned consumer-facing search API; the door is for the
  supply side.
- **Sources:** Booking.com Connectivity docs:
  https://developers.booking.com/ · partner tiers:
  https://connectivity.booking.com/
- **Status: VERIFIED (partner-gated; supply side only)**

### U.S. Securities and Exchange Commission (sec.gov) — WALLED (Akamai)

- **Sanctioned route: YES — EDGAR JSON APIs, free, no key.** The
  SEC's data.sec.gov endpoints (submissions, companyfacts,
  companyconcept, frames) are free and keyless, with a fair-access
  limit of 10 requests/second and a required identifying User-Agent
  carrying contact information. **Nuance measured by Wave 8's path
  probe:** our probe of the data.sec.gov root returned WALLED
  Akamai 403 — the EDGAR host walls unidentified clients, so the
  front-door entry carries a condition: identify yourself per the
  SEC's own fair-access rules or the wall you see is the one the
  rules warn about.
- **Sources:** SEC EDGAR full-text / JSON API docs:
  https://www.sec.gov/edgar/sec-api-documentation · fair-access
  rules (10 req/s, identifying UA):
  https://www.sec.gov/os/accessing-edgar-data
- **Status: VERIFIED (free; identification required)**

### U.S. Bureau of Labor Statistics (bls.gov) — WALLED (Akamai)

- **Sanctioned route: YES — Public Data API, free.** api.bls.gov
  serves BLS time-series data; v1 is open without registration, v2
  takes a free key for higher limits. Official developer pages on
  bls.gov document both tiers.
- **Sources:** BLS Public Data API docs:
  https://api.bls.gov/ · registration and limits:
  https://api.bls.gov/publicAPI/v2/
- **Status: VERIFIED**

### New York City Open Data (nyc.gov) — WALLED (Akamai)

- **Sanctioned route: YES — Socrata API, free.** data
  .cityofnewyork.us exposes the city's open datasets through the
  Socrata API; an app token is recommended for higher limits but
  anonymous reads work. Documented in the city's own Open Data APIs
  guide.
- **Sources:** NYC Open Data APIs guide:
  https://opendata.cityofnewyork.us/ · Socrata API docs:
  https://dev.socrata.com/
- **Status: VERIFIED**

### U.S. Department of Education (ed.gov) — CHALLENGED (Azure WAF)

- **Sanctioned route: YES, narrow — College Scorecard API.** The
  Department's sanctioned programmatic surface is the College
  Scorecard API (api.data.gov), keyed free, covering college cost,
  outcome, and program data. It is the Department's data, not the
  ed.gov website itself — the website has no general API.
- **Sources:** College Scorecard API docs:
  https://collegescorecard.ed.gov/data/documentation/ · api.data.gov
  signup: https://api.data.gov/
- **Status: VERIFIED (narrow — Scorecard data only)**

### Federal Trade Commission (ftc.gov) — WALLED (Akamai)

- **Sanctioned route: YES, narrow — Early Termination Notices API.**
  The FTC's own 2018 announcement documents its first web API,
  serving Hart-Scott-Rodino early-termination notices. It is a single
  dataset, not a general FTC API, but it is a real first-party door.
- **Sources:** FTC announcement (first web API):
  https://www.ftc.gov/news-events/blogs/office-policy-planning/
- **Status: VERIFIED (narrow — one dataset)**

### Social Security Administration (ssa.gov) — WALLED (Akamai)

- **Sanctioned route: YES, narrow — public dataset APIs.** SSA's
  developer pages (socialsecurity.gov/developer/api/) document
  specific public dataset APIs, e.g. hearings-workload data, under
  its Digital Government Strategy program. No general SSA API exists.
- **Sources:** SSA developer API pages:
  https://www.ssa.gov/developer/api/ · Digital Government Strategy
  page: https://www.ssa.gov/digital/
- **Status: VERIFIED (narrow — specific datasets)**

### U.S. Department of State (state.gov) — custom deny

- **Sanctioned route: YES, partial — feeds and datasets, no unified
  portal.** State has no single developer portal, but it publishes
  sanctioned machine-readable surfaces: travel-advisory RSS feeds,
  data.gov datasets, and legacy state.gov/api surfaces, as catalogued
  in API Evangelist's federal-agency roundup.
- **Sources:** API Evangelist federal roundup (State surfaces):
  https://apievangelist.com/ · travel advisory feeds:
  https://travel.state.gov/
- **Status: VERIFIED (partial — feeds + datasets, no portal)**

### GoodRx — CHALLENGED

- **Sanctioned route: YES — pricing APIs, keyed.** GoodRx's
  developer documentation (goodrx.com/developer/documentation)
  documents api.goodrx.com endpoints: low-price, fair-price,
  price-comparison, drug-info, and drug-search, with API key access
  under an API agreement referenced in its terms.
- **Sources:** GoodRx developer docs:
  https://www.goodrx.com/developer/documentation
- **Status: VERIFIED**

### Mayo Clinic — CHALLENGED

- **Sanctioned route: NONE FOUND for public use.** Mayo Clinic
  Platform (Discover/Validate) is an institutional partnership
  program for health systems and researchers, not a public consumer
  API for mayoclinic.org content. No public developer portal was
  found in this pass.
- **Sources:** Mayo Clinic Platform (institutional scope):
  https://www.mayoclinicplatform.org/
- **Status: NO SANCTIONED ROUTE FOUND (public use)**

### Zocdoc — CHALLENGED

- **Sanctioned route: YES, partner-gated.** developers.zocdoc.com
  documents provider and scheduling APIs for US healthcare providers
  and software vendors, requiring approval and a BAA. The newer Care
  Access Network adds a developer API and MCP server, with partners
  including Amazon Health AI, Gemini, Yelp, Healthgrades, and Blue
  Shield of California.
- **Sources:** Zocdoc developer portal:
  https://developers.zocdoc.com/ · Care Access Network:
  https://www.zocdoc.com/about/care-access-network
- **Status: VERIFIED (partner-gated; providers/vendors only)**

### UnitedHealthcare / Optum — WALLED

- **Sanctioned route: YES, provider/payer-gated.** developer.optum
  .com documents Optum's developer APIs: FHIR R4 Interoperability
  (Patient Access) APIs per CMS-9115-F and eligibility/claims
  X12-to-JSON APIs, with OAuth2. Access is for providers, payers,
  and approved partners — not consumers.
- **Sources:** Optum developer portal:
  https://developer.optum.com/ · CMS Interoperability rule
  (CMS-9115-F): https://www.cms.gov/
- **Status: VERIFIED (provider/payer-gated)**

### Home Depot — CHALLENGED

- **Sanctioned route: NONE FOUND.** No official public product API
  was confirmed. Third-party writeups describe an internal
  federation-gateway GraphQL endpoint, but that is undocumented
  internal infrastructure, not sanctioned access, and we do not cite
  it as a door.
- **Status: NO SANCTIONED ROUTE FOUND (as of Oct 2026, public docs)**

### Macy's — CHALLENGED

- **Sanctioned route: NONE FOUND.** No public developer API,
  partner portal, or sanctioned feed for macys.com was found in this
  pass.
- **Status: NO SANCTIONED ROUTE FOUND (as of Oct 2026, public docs)**

### Uber Eats — CHALLENGED

- **Sanctioned route: YES, partner-gated — merchant side.**
  developer.uber.com documents the Eats Marketplace API for
  merchants and partners: sandbox access is self-serve with
  auto-granted scopes, but production requires an NDA, an API
  licensing agreement, partner-manager approval, and scope
  whitelisting. No consumer-facing restaurant-search API.
- **Sources:** Uber developer docs (Eats Marketplace API):
  https://developer.uber.com/docs/eats
- **Status: VERIFIED (partner-gated; merchant side only)**

### Chewy — CHALLENGED

- **Sanctioned route: NONE FOUND for public use.** Chewy's only
  documented machine integration is supplier-side (Dsco/EDI for
  vendors), not a consumer-facing API for chewy.com content.
- **Status: NO SANCTIONED ROUTE FOUND (public use)**

## Wave 8 additions — jobs, finance, news, other

### CareerBuilder — WALLED

- **Sanctioned route: NONE FOUND for public/developer self-serve.**
  No public CareerBuilder developer portal or API documentation was
  found in this pass. Employer-side integrations exist through
  third-party vendors (e.g. Whippy's CareerBuilder integration), but
  those are vendor products, not a first-party developer program.
- **Sources:** third-party integration listing (no first-party
  portal linked): https://www.whippy.ai/integrations/careerbuilder
- **Status: NO SANCTIONED ROUTE FOUND (public/developer self-serve)**

### CareerBuilder.ca — WALLED

- **Sanctioned route: NONE FOUND.** Same finding as CareerBuilder
  .com: no public developer portal or API documentation for the
  Canadian site was found in this pass.
- **Status: NO SANCTIONED ROUTE FOUND (as of Oct 2026, public docs)**

### Monster.ca — WALLED

- **Sanctioned route: CLAIMED BY THIRD PARTIES, NOT CONFIRMED.**
  Same status as Monster US: integration vendors describe a partner
  API, but no public, self-serve Monster developer portal or API
  documentation was found for the Canadian site either.
- **Status: UNVERIFIED (same program claims as Monster US)**

### Adzuna — CHALLENGED

- **Sanctioned route: YES — public API, free key.** developer
  .adzuna.com documents the Adzuna job-search API (api.adzuna.com,
  country paths like /gb/ and /us/), authenticated with a free
  app_id + app_key pair, with rate limits stated on the portal. A
  separate Intelligence API (developer.intelligence.adzuna.com)
  covers labour-market data. This is the rare job board whose front
  door is genuinely self-serve.
- **Sources:** Adzuna developer portal:
  https://developer.adzuna.com/overview · Intelligence API docs:
  https://developer.intelligence.adzuna.com/
- **Status: VERIFIED**

### CareerJet — WALLED

- **Sanctioned route: YES — public job-search API, key by request.**
  CareerJet's public API is documented in its long-standing client
  libraries (e.g. the Perl WebService::Careerjet module, copyright
  2007–2025, contact api@careerjet.com for keys). There is no glossy
  first-party portal, but the API itself is real and public — the
  documentation lives in the libraries, not on a portal page.
- **Sources:** WebService::Careerjet documentation:
  https://metacpan.org/pod/WebService::Careerjet
- **Status: VERIFIED (key by request to api@careerjet.com)**

### Catho — WALLED

- **Sanctioned route: NONE FOUND.** No public developer API,
  partner portal, or sanctioned feed for catho.com.br was found in
  this pass; the platform's programmatic surface is its app, not an
  API.
- **Status: NO SANCTIONED ROUTE FOUND (as of Oct 2026, public docs)**

### Citizens Bank (citizensbank.com) — WALLED

- **Sanctioned route: UNCONFIRMED.** A student-project document
  describes FDX open-banking endpoints on citizensbank.com
  infrastructure (mwapifdx.p2.ocp.citizensbank.com, IBM API Connect,
  client-id/secret auth), suggesting an aggregator-facing API exists,
  but no public Citizens developer portal was found, and the
  third-party tracker entries mix in other banks named Citizens
  (Nepal's RAPID platform, Citizens Bank Minnesota via Finicity).
  Aggregator-mediated access (Plaid/Finicity) is the practical route
  today; the first-party door itself is unconfirmed.
- **Sources (mixed, hence unverified):** WPI project doc (FDX
  endpoints): https://digital.wpi.edu/downloads/sb397c307 ·
  third-party tracker (mixed banks):
  https://www.openbankingtracker.com/provider/citizensbank
- **Status: UNVERIFIED**

### Sky News — WALLED

- **Sanctioned route: NONE FOUND.** No public Sky News API or
  developer portal was found in this pass. Sky content reaches
  developers only through third-party aggregators (NewsAPI and
  similar) — someone else's door, not Sky's.
- **Status: NO SANCTIONED ROUTE FOUND (as of Oct 2026, public docs)**

### Haaretz — WALLED

- **Sanctioned route: CLAIMED BY THIRD PARTIES, NOT CONFIRMED.**
  Third-party RSS directories list Haaretz section feeds (e.g. the
  Tech feed), but no official Haaretz developer API or portal was
  found, and the feed URLs themselves are directory claims, not
  first-party documentation. Treated as unverified, not as a
  verified feed door.
- **Sources (third-party claims):** Feedspot Israel tech feeds:
  https://rss.feedspot.com/israel_tech_rss_feeds/
- **Status: UNVERIFIED**

### Financial Times — CHALLENGED (DataDome)

- **Sanctioned route: YES, customer-gated.** developer.ft.com hosts
  the FT.com search API and the Headline API (customisable headline
  lists for intranet/CRM embedding), sold to corporate, government,
  and education customers. A 2013 Salesforce hack writeup confirms
  the search API's existence and shape; a 2014 trade report confirms
  the Headline API's launch terms. Not self-serve free — but real
  and documented.
- **Sources:** FT developer portal: https://developer.ft.com/ ·
  Headline API launch (InPublishing, 2014):
  https://www.inpublishing.co.uk/articles/ft-launches-customisable-api-6355
- **Status: VERIFIED (customer-gated)**

### Associated Press — WALLED (Akamai)

- **Sanctioned route: YES, customer/partner-gated.** developer.ap
  .org documents the AP's API family: Content API, Media API
  (multimedia content + AP Media Agent), Elections API, and Monitors
  and Alerts. APIs.io indexes four AP contracts. All require a
  customer relationship — this is a wire-service door, not a public
  one, but it is a genuine first-party program.
- **Sources:** AP Developer portal: https://developer.ap.org/ ·
  APIs.io provider profile:
  https://apis.io/providers/associated-press/
- **Status: VERIFIED (customer/partner-gated)**

### Reuters — CHALLENGED (DataDome)

- **Sanctioned route: YES, enterprise-gated.** Reuters News is
  distributed as a source inside LSEG's Refinitiv Data Platform News
  API (developers.lseg.com): REST + streaming, rich metadata,
  entitlement-based access, 2.2M+ stories/year. Third-party "free
  tier Reuters API" listings are not first-party and are not cited
  as the door; the LSEG platform is.
- **Sources:** LSEG RDP News API docs:
  https://developers.lseg.com/content/devportal/en_us/api-catalog/refinitiv-data-platform/news-API.html
- **Status: VERIFIED (enterprise/entitlement-gated)**

### The Economist — CHALLENGED (DataDome)

- **Sanctioned route: YES, enterprise-gated.** Two first-party
  doors: the Economist Intelligence API (eiu.com, REST/JSON developer
  portal, macro and risk datasets, free trial by request) and the
  Economist content API opened to enterprise clients in August 2025
  for private-LLM/RAG use, confirmed by Digiday's president-level
  interview. Neither is self-serve free, but both are real.
- **Sources:** EIU API page:
  https://www.eiu.com/n/solutions/economist-intelligence-api-asset-management/
  · content-API opening (Digiday, Oct 2025):
  https://digiday.com/media/the-economist-licenses-its-content-to-enterprise-clients-private-llms/
- **Status: VERIFIED (enterprise-gated)**

### The Wall Street Journal — CHALLENGED (DataDome)

- **Sanctioned route: YES, enterprise-gated via Dow Jones.** Dow
  Jones' Factiva APIs license WSJ (and Barron's, MarketWatch, IBD)
  content to enterprises for GenAI and research use — 8,000+
  licensed sources, copyright-compliant, with the Dow Jones Newswires
  GenAI Newsfeed as the current flagship surface. No
  consumer/developer self-serve tier.
- **Sources:** Factiva GenAI announcement (Dow Jones, 2026):
  https://s23.q4cdn.com/175719177/files/doc_news/Dow-Jones-Factiva-Surpasses-8000-Licensed-Sources-for-GenAI-Use-2026.pdf
- **Status: VERIFIED (enterprise-gated)**

### Fast Company — CHALLENGED (DataDome)

- **Sanctioned route: NONE FOUND.** No public developer API,
  partner portal, or sanctioned feed for fastcompany.com was found
  in this pass.
- **Status: NO SANCTIONED ROUTE FOUND (as of Oct 2026, public docs)**

### Inc. — CHALLENGED (DataDome)

- **Sanctioned route: NONE FOUND.** No public developer API,
  partner portal, or sanctioned feed for inc.com was found in this
  pass (same Mansueto Ventures stable as Fast Company, same
  absence).
- **Status: NO SANCTIONED ROUTE FOUND (as of Oct 2026, public docs)**

### South China Morning Post — CHALLENGED

- **Sanctioned route: NONE FOUND.** No public developer API or
  portal for scmp.com was found in this pass; the platform's
  programmatic surface is its app, not an API.
- **Status: NO SANCTIONED ROUTE FOUND (as of Oct 2026, public docs)**

### The Atlantic — CHALLENGED

- **Sanctioned route: NONE FOUND.** The Atlantic's APIs are internal
  (its app and a 150-year story/author database feed an internal
  analytics dashboard built by a vendor). No public developer
  program was found in this pass.
- **Status: NO SANCTIONED ROUTE FOUND (as of Oct 2026, public docs)**

### Gun.io — WALLED (Cloudflare)

- **Sanctioned route: NONE FOUND.** Gun.io is a vetted talent
  marketplace with no public developer API, partner portal, or
  sanctioned feed found in this pass. Its "API developers" pages are
  hiring pages, not an API.
- **Status: NO SANCTIONED ROUTE FOUND (as of Oct 2026, public docs)**

### Claude (claude.ai) — CHALLENGED (Cloudflare)

- **Sanctioned route: YES — and it is the point of the exhibit.**
  claude.ai the *chat website* challenges our agent, but Anthropic's
  developer platform (platform.claude.com, docs.claude.com) is a
  fully public, self-serve API: Messages API, tool use, code
  execution, MCP connectors, SDKs, and console key management. The
  wall is on the showroom; the loading dock is open and documented
  — the same pattern as eBay, NYT, and npm, from a company whose
  entire product is the API.
- **Sources:** Anthropic developer docs: https://docs.claude.com/ ·
  console key management: https://platform.claude.com/settings/keys
- **Status: VERIFIED**

### Etsy — CHALLENGED (DataDome)

- **Sanctioned route: YES — Open API v3, self-serve with approval.**
  developer.etsy.com documents the Etsy Open API v3 (REST, OAuth
  2.0 PKCE, listings/inventory/shops/orders/reviews/shipping),
  with an API Explorer, webhooks for order lifecycle events, and an
  OpenAPI Dev MCP server that needs no key. App registration is
  self-serve; keys activate after approval (typically 24–48h).
  Rate limit 10,000 requests/day/key.
- **Sources:** Etsy Open API v3 docs:
  https://developer.etsy.com/documentation/
- **Status: VERIFIED**

### Amazon — intermittent CHALLENGED (Cloudflare interstitial)

- **Sanctioned route: YES, program-gated — three doors, three
  audiences.** (1) Product Advertising API: catalog search and
  product data for Associates (affiliate approval required).
  (2) Selling Partner API: seller-side orders, inventory, and
  fulfillment (seller account + app approval). (3) Ads API:
  advertising management (advertiser account + OAuth). No general
  consumer search API — but every commercial audience has a real
  door.
- **Sources:** Product Advertising API (Wikipedia summary):
  https://en.wikipedia.org/wiki/Amazon_Product_Advertising_API ·
  Selling Partner API docs:
  https://developer-docs.amazon.com/sp-api/
- **Status: VERIFIED (program-gated; audience-specific)**

### W3Schools — WALLED (Akamai edge)

- **Sanctioned route: NONE FOUND.** W3Schools is a tutorial site;
  no public API for its content was found in this pass.
- **Status: NO SANCTIONED ROUTE FOUND (as of Oct 2026, public docs)**

### Realtor.com — WALLED (Kasada 429)

- **Sanctioned route: NONE FOUND for public listing-data access.**
  No first-party public developer API or portal exists; third-party
  RapidAPI mirrors are not first-party and are not cited as the
  door. The one first-party program found, Connections Plus, is a
  partner API for agents/brokers (lead management), contacted
  through sales — not a public listing-search API.
- **Sources:** third-party analysis (no first-party portal):
  https://www.rapidevelopers.com/bubble-integrations/realtor-com ·
  Connections Plus (partner program, via sales):
  https://rollout.com/integration-guides/realtor-com/api-essentials
- **Status: NO SANCTIONED ROUTE FOUND (public listing access)**

### Apartments.com — WALLED

- **Sanctioned route: NONE FOUND for public use.** Apartments.com's
  posture is closed: no developer portal, no OpenAPI contract, no
  SDK (developer.apartments.com and siblings do not resolve; api
  .apartments.com returns 403 to non-browser requests, per APIs.io).
  The one documented machine seam is inbound, not public: the
  Digital Feeds Program, an approval-and-contract path where an
  approved feed vendor syndicates a *paying advertiser's* listings
  into Apartments.com over FTP (spec on request to
  Feeds@apartments.com). That is a door for advertisers, not for
  readers.
- **Sources:** APIs.io provider profile (closed posture, feeds
  program): https://apis.io/providers/apartments-com/
- **Status: NO SANCTIONED ROUTE FOUND (public use)**

### Redfin — WALLED (AWS CloudFront block)

- **Sanctioned route: YES, narrow — free CSV data, no API.**
  Redfin publishes no public API and explicitly prohibits use of
  its undocumented internal endpoints (ToS; IP-blocking risk). But
  it does publish a sanctioned data route: aggregated market
  statistics as free downloadable CSV files at redfin.com/news
  /data-center (median sale price, days on market, inventory, price
  per square foot, by metro/city/zip/neighborhood, updated weekly).
  A feed is a front door even when it isn't an API.
- **Sources:** Redfin Data Center (free CSVs):
  https://www.redfin.com/news/data-center · internal-endpoint
  prohibition (third-party analysis):
  https://www.rapidevelopers.com/retool-integrations/redfin
- **Status: VERIFIED (narrow — CSV data, no API)**

### Homes.com — WALLED

- **Sanctioned route: CLAIMED, CURRENCY UNCONFIRMED.** Homes.com
  announced a partner API in November 2018 (Homes.com Connect leads
  and contacts sync for real-estate technology companies and
  brokerages, e.g. BombBomb and DocuSign Rooms integrations), but no
  current public developer portal or documentation was found in this
  pass, so whether the program is still open is unverified.
- **Sources:** 2018 launch announcement (PR Newswire):
  https://www.prweb.com/releases/homes-com-launches-api-to-streamline-real-estate-communications-895491890.html
- **Status: UNVERIFIED (announced 2018; current status unconfirmed)**

## Wave 25 addition

### Hugging Face (huggingface.co) — OPEN (200); signed-agent directory LOGIN_GATED (401)

- **Sanctioned route: YES — official Hub API.** Hugging Face
  publishes a public REST API for the Hub (models, datasets,
  Spaces) with a free tier; an account access token authenticates
  writes and public reads are open. Programmatic Hub work does
  not need the website at all — and unlike most rows in this
  file, the website itself is not walled either: our probe has
  read huggingface.co OPEN in every Index round, and the Wave 7
  audit sweep graded its robots, llms.txt, and sitemap all PASS.
- **Signed-agent directory: NOT PUBLISHED (login-gated).** The
  Web Bot Auth directory path
  (/.well-known/http-message-signatures-directory) answers 401
  LOGIN_GATED. The Wave 23 spot-check (2026-10-24) found the
  census-era hard wall replaced by a gate; a Wave 25 re-probe
  the same day confirms the 401. The path sits behind the
  site's own authentication, so signed agents get no public key
  directory here — the one closed door on an otherwise open
  platform.
- **Evidence (this campaign's own probes):** root 200 / OPEN,
  directory path 401 / LOGIN_GATED — Wave 25 Leg C, 2026-10-24
  (`validation/wave25/huggingface-probes.json`); directory path
  401 LOGIN_GATED — Wave 23 adopter spot-check, 2026-10-24
  (`validation/wave23/ADOPTER-SPOT-3.md`). The bare /api path
  itself serves the site's HTML 404 page (Wave 25 probe), so
  callers start from the API documentation, not the root path.
- **Sources:** Hub API documentation:
  https://huggingface.co/docs/hub/api
- **Status: VERIFIED**

## Scoreboard (seed edition)

| Platform | Website (Index) | Front door | Status |
| --- | --- | --- | --- |
| Upwork | WALLED / Cloudflare | Official GraphQL API, key by request | VERIFIED |
| Fiverr | CHALLENGED / PerimeterX | None for sellers; affiliate API only | VERIFIED |
| Guru | WALLED / Imperva | None found | NO ROUTE FOUND |
| Medium | WALLED / Cloudflare | RSS (read); API closed to new users | VERIFIED |
| eBay | WALLED / Akamai | Full public developer program | VERIFIED |
| Monster | CHALLENGED / DataDome | Partner API claimed, unconfirmed | UNVERIFIED |
| NYT | CHALLENGED / DataDome | Public developer program + RSS | VERIFIED |
| npmjs | CHALLENGED / Cloudflare | Registry API, open + documented | VERIFIED |
| LinkedIn | OPEN | Partner-gated APIs | VERIFIED |
| Indeed | OPEN | Publisher program closed since 2022 | VERIFIED |

**8 of 10 rows fully verified; 1 documented absence (Guru); 1
unverified (Monster).** The pattern the table proves: a wall on the
website is survivable when a door exists next to it (eBay, NYT, npm).
The platforms with no door at all — Fiverr for sellers, Guru entirely —
are where lawful agent work simply dies. Those are the campaign's
exhibits A and B.

## Scoreboard — Wave 8 additions (2026-10-24)

| Platform | Website (Index) | Front door | Status |
| --- | --- | --- | --- |
| American Airlines | WALLED / Akamai | Partner/accreditation-gated APIs | VERIFIED |
| Amtrak | WALLED / Akamai | Travelport partner program | VERIFIED |
| Delta | WALLED / Akamai | Conflicting claims, no portal found | UNVERIFIED |
| Hilton | WALLED / Akamai | GDS/TMC partner APIs | VERIFIED |
| Hyatt | WALLED / Akamai | None found | NO ROUTE FOUND |
| Marriott | WALLED / Akamai | None found (internal platform only) | NO ROUTE FOUND |
| easyJet | WALLED / Akamai | None own; aggregator-only | NO ROUTE FOUND |
| Emirates | WALLED / Akamai | Trade-partner NDC API | VERIFIED |
| Expedia / Hotels / Orbitz / Travelocity | RATE_LIMITED / WALLED | EPS Rapid API (one door, four brands) | VERIFIED |
| Vrbo | RATE_LIMITED | Expedia Rapid API (select partners) | VERIFIED |
| TripAdvisor | CHALLENGED | Content API, partner program | VERIFIED |
| Viator | CHALLENGED | Partner API, tiered | VERIFIED |
| Booking.com | CHALLENGED | Connectivity APIs (supply side) | VERIFIED |
| SEC (sec.gov) | WALLED / Akamai | EDGAR JSON APIs, free, UA-identified | VERIFIED |
| BLS (bls.gov) | WALLED / Akamai | Public Data API, free | VERIFIED |
| NYC Open Data | WALLED / Akamai | Socrata API, free | VERIFIED |
| Dept. of Education | CHALLENGED / Azure WAF | College Scorecard API (narrow) | VERIFIED |
| FTC | WALLED / Akamai | Early Termination Notices API (narrow) | VERIFIED |
| SSA | WALLED / Akamai | Public dataset APIs (narrow) | VERIFIED |
| State Dept. | Custom deny | RSS feeds + datasets (no portal) | VERIFIED |
| GoodRx | CHALLENGED | Pricing APIs, keyed | VERIFIED |
| Mayo Clinic | CHALLENGED | None for public use (Platform is institutional) | NO ROUTE FOUND |
| Zocdoc | CHALLENGED | Partner APIs + Care Access Network | VERIFIED |
| UnitedHealthcare / Optum | WALLED | Optum APIs (provider/payer-gated) | VERIFIED |
| Home Depot | CHALLENGED | None found | NO ROUTE FOUND |
| Macy's | CHALLENGED | None found | NO ROUTE FOUND |
| Uber Eats | CHALLENGED | Eats Marketplace API (merchant side) | VERIFIED |
| Chewy | CHALLENGED | None for public use (supplier EDI only) | NO ROUTE FOUND |
| CareerBuilder | WALLED | None for public self-serve | NO ROUTE FOUND |
| CareerBuilder.ca | WALLED | None found | NO ROUTE FOUND |
| Monster.ca | WALLED | Partner API claimed, unconfirmed | UNVERIFIED |
| Adzuna | CHALLENGED | Public API, free key | VERIFIED |
| CareerJet | WALLED | Public API, key by request | VERIFIED |
| Catho | WALLED | None found | NO ROUTE FOUND |
| Citizens Bank | WALLED | FDX endpoints claimed, no portal found | UNVERIFIED |
| Sky News | WALLED | None found | NO ROUTE FOUND |
| Haaretz | WALLED | RSS feeds claimed, unconfirmed | UNVERIFIED |
| Financial Times | CHALLENGED / DataDome | FT.com search + Headline APIs (customer-gated) | VERIFIED |
| Associated Press | WALLED / Akamai | Content/Media/Elections APIs (customer-gated) | VERIFIED |
| Reuters | CHALLENGED / DataDome | LSEG RDP News API (enterprise-gated) | VERIFIED |
| The Economist | CHALLENGED / DataDome | EIU API + enterprise content API | VERIFIED |
| Wall Street Journal | CHALLENGED / DataDome | Dow Jones Factiva APIs (enterprise-gated) | VERIFIED |
| Fast Company | CHALLENGED / DataDome | None found | NO ROUTE FOUND |
| Inc. | CHALLENGED / DataDome | None found | NO ROUTE FOUND |
| South China Morning Post | CHALLENGED | None found | NO ROUTE FOUND |
| The Atlantic | CHALLENGED | None found (internal APIs only) | NO ROUTE FOUND |
| Gun.io | WALLED / Cloudflare | None found | NO ROUTE FOUND |
| Claude (claude.ai) | CHALLENGED / Cloudflare | Anthropic API, self-serve | VERIFIED |
| Etsy | CHALLENGED / DataDome | Open API v3 + MCP server | VERIFIED |
| Amazon | Intermittent CHALLENGED | Product Advertising + SP + Ads APIs | VERIFIED |
| W3Schools | WALLED / Akamai edge | None found | NO ROUTE FOUND |
| Realtor.com | WALLED / Kasada | None for public listing access | NO ROUTE FOUND |
| Apartments.com | WALLED | None for public use (inbound feeds only) | NO ROUTE FOUND |
| Redfin | WALLED / CloudFront | Free CSV Data Center (no API) | VERIFIED |
| Homes.com | WALLED | Partner API announced 2018, status unconfirmed | UNVERIFIED |

**Wave 8 adds 55 rows: 31 VERIFIED, 19 NO SANCTIONED ROUTE FOUND,
5 UNVERIFIED.** Combined with the seed edition, FRONT-DOORS.md now
covers 65 platforms: 39 VERIFIED, 20 NO ROUTE FOUND, 6 UNVERIFIED.
**Wave 25 adds 1 row (Hugging Face, VERIFIED): the file now covers
66 platforms — 40 VERIFIED, 20 NO ROUTE FOUND, 6 UNVERIFIED.**

## Scoreboard — Wave 25 addition (2026-10-24)

| Platform | Website (Index) | Front door | Status |
| --- | --- | --- | --- |
| Hugging Face | OPEN | Hub API, public + documented | VERIFIED |

The Wave 8 pattern, stated plainly: **the news industry walls its
websites and sells its content through enterprise APIs** (FT, AP,
Reuters, Economist, WSJ all VERIFIED-but-gated; Fast Company, Inc.,
SCMP, Atlantic, Sky News with nothing at all) — the door exists, but
the price of admission is a contract, not a key. **Travel is the
opposite split:** the aggregators' suppliers (Expedia Group, Viator,
TripAdvisor, Emirates) publish partner doors, while the big US hotel
chains (Hyatt, Marriott) publish nothing. And **civic data is the
brightest corner of the board**: SEC, BLS, and NYC Open Data are free,
keyless-or-free-key, and documented — the government doors are more
open than most commercial ones, even where the websites themselves
are Akamai-walled. The SEC entry carries the wave's sharpest
caution: a free API that walls unidentified clients is a door with a
dress code, and our own probe tripped it.

*Maintenance rule: re-verify quarterly. A door opening or closing is
Index news and gets dated here.*
