# Wave 8 — Depth wave 2: the path matrix, second cohort

Wave 2 measured paths on the Index seed's 8 walled/challenged
platforms. Wave 8 repeats the method — homepage, login, signup,
API/docs, robots.txt, sitemap.xml, llms.txt — on the platforms
that joined the wall since: the Wave 5 civic/finance/travel/
health/education additions and the Wave 7 expansion's new
walled/challenged rows, plus 5 open controls. 322 probes across 46
platforms, one honest fetch per path, back-off on 429.

**Source:** `results-paths2.json` — the full 322-probe run, with
one row corrected after a classifier fix (delta login, see
`PROBLEMS.md` W8-001; the original probe time is retained on the
row). Per-platform API overrides: sec.gov's api path is
https://data.sec.gov/, bls.gov's is https://api.bls.gov/ — the
real API hosts, not `/api` guesses.

**Scan context (read before quoting):** 2026-10-24, same client as
every wave — a datacenter egress IP (this build VM), wallcheck's
honest identified user agent, one fetch per URL, no retries, full
back-off on any 429 (19 throttled paths honored it). Verdicts are
*this client's* measured results with evidence on file, not
universal claims about a site.

**Distribution (322 paths):** OPEN 94 · WALLED 145 · CHALLENGED 54 ·
RATE_LIMITED 20 · UNREACHABLE 6 · LOGIN_GATED 3.

## The five stories the data tells

**1. Whole-domain walls are now the norm in this cohort — and
their opposite exists too.** 21 of 46 platforms wall or challenge
*all seven* paths, machine files included: amtrak, apartments,
citizensbank, ed.gov, ftc.gov, haaretz, homes, hyatt, macys,
marriott, mayoclinic, monster.ca, careerbuilder.ca, nyc.gov,
redfin, sec.gov, sky news, ssa.gov, state.gov, ubereats,
unitedhealthcare. Wave 2's cohort had exactly one whole-domain
wall (Guru); this cohort was selected from walled rows, so the
share is expected to be high — but the shape matters: on these
domains there is no machine-file escape hatch at all. The
opposite shape is 8 homepage-only walls — americanairlines,
careerbuilder, careerjet, catho, easyjet, emirates, hilton,
homedepot — where the homepage 403s (or challenges) but 4–6 other
paths serve, including robots.txt. The wall is a front-door
bouncer on those domains, not a domain policy.

**2. APIs don't beat webs here — because the real APIs live
elsewhere.** Wave 2's first story inverted: the `/api` path serves
nothing real in this cohort. It is WALLED/CHALLENGED on 27 of 46,
RATE_LIMITED on 4, an honest 404 (path doesn't exist) on 14, and
UNREACHABLE (a served 500) on 1. No platform serves a real API at
the default path. The sanctioned APIs these platforms do have live
on other hosts and programs — the front-doors file documents them
— and two of those hosts wall this client at their roots too:
data.sec.gov returns Akamai 403, and api.bls.gov returns Akamai
403. A free API that walls unidentified datacenter clients is a
door with a dress code, and both civic entries now carry that
caution. (Root-path probes, not endpoint probes: an identified
client with a contact User-Agent may pass where this probe did
not — the SEC's own fair-access rules say exactly that.)

**3. The machine files slip through — in miniature.** robots.txt
serves as real text on 20 of 46 platforms (every robots OPEN row is
a 200). Genuine sitemaps (XML, 200) exist on only 5: careerbuilder,
chase.com, goodrx, hilton, usa.gov. Genuine llms.txt (200) exists
on only 3: careerbuilder, catho, expedia — each on a platform whose
homepage is walled or challenged. The other llms/sitemap OPEN rows
are honest 404s: the file simply doesn't exist, and nothing
wall-like intervened. Wave 2's story survives, but shrunk: the
files written for machines are the last thing to survive a wall,
and on 21 whole-domain platforms even they don't.

**4. "Login-gated" still almost never means a login page — and
this wave caught the classifier saying otherwise.** Three genuine
gates: airbnb (the control, served 200), careerjet and catho
(both real 200 login forms reached by redirect — catho's login
serves while its homepage bare-403s). The fourth was a defect:
delta's `/login` returned a 444 Akamai deny with an empty
redirect chain, and the classifier called it LOGIN_GATED because
444 wasn't in the login heuristic's exclusion set (W8-001). Fixed
with a generalized rule — a gate must be a served page (2xx/3xx),
never an error status — re-probed live as WALLED Akamai 444, and
delta is now a clean 7-of-7 444 wall. The lesson from Wave 2
holds, sharpened: a login URL is not a login gate, and an error
status is never a gate.

**5. Two denial shapes, and a throttle with a scope.** First, the
bare deny: state.gov, hyatt, and haaretz answer all seven paths
with 403 and zero vendor signals — no marker, no reference, no
attribution. The classifier correctly reports vendor None; a deny
that doesn't identify itself is a story about the denier, not a
gap in the tool. Second, the 404 fall-through: on Akamai-walled
hosts (americanairlines, hilton, easyjet, emirates, homedepot),
paths that don't exist serve plain 404s while real paths 403 —
the wall fires on known routes and the 404 handler answers first
for unknown ones. And the throttle: the Expedia family
(expedia, hotels, orbitz, travelocity, vrbo) 429s on 19 app paths
while robots.txt serves on all five and llms.txt serves on
expedia itself — a throttle is not a wall, and its scope (app
paths only) is measurable. Chewy is the same shape at smaller
scale: Kasada 429 on the homepage only, everything else open.

## Per-platform matrix (final, post-fix)

| platform | home | login | signup | api | robots | sitemap | llms |
| --- | --- | --- | --- | --- | --- | --- | --- |
| airbnb | OPEN 200 | LOGIN_GATED 200 | OPEN 404 | OPEN 404 | OPEN 200 | OPEN 404 | OPEN 404 |
| americanairlines | WALLED Ak 403 | WALLED Ak 403 | OPEN 404 | OPEN 404 | OPEN 200 | OPEN 404 | OPEN 404 |
| amtrak | WALLED Ak 403 | WALLED Ak 403 | WALLED Ak 403 | WALLED Ak 403 | WALLED Ak 403 | WALLED Ak 403 | WALLED Ak 403 |
| apartments | WALLED Ak 403 | WALLED Ak 403 | WALLED Ak 403 | WALLED Ak 403 | WALLED Ak 403 | WALLED Ak 403 | WALLED Ak 403 |
| bls.gov | UNREACHABLE | WALLED Ak 403 | WALLED Ak 403 | WALLED Ak 403 | WALLED Ak 403 | UNREACHABLE | WALLED Ak 403 |
| careerbuilder | CHALLENGED DD 403 | OPEN 404 | OPEN 404 | UNREACHABLE 500 | OPEN 200 | OPEN 200 | OPEN 200 |
| careerbuilder.ca | CHALLENGED DD 403 | CHALLENGED DD 403 | CHALLENGED DD 403 | CHALLENGED DD 403 | CHALLENGED DD 403 | CHALLENGED DD 403 | CHALLENGED DD 403 |
| careerjet | CHALLENGED CF 200 | LOGIN_GATED 200 | OPEN 404 | OPEN 404 | OPEN 200 | OPEN 404 | OPEN 404 |
| catho | WALLED 403 | LOGIN_GATED 200 | OPEN 404 | OPEN 404 | OPEN 200 | OPEN 404 | OPEN 200 |
| chase.com | OPEN 200 | OPEN 200 | OPEN 404 | OPEN 404 | OPEN 200 | OPEN 200 | OPEN 404 |
| chewy | RATE_LIMITED Ka 429 | OPEN 404 | OPEN 404 | OPEN 404 | OPEN 200 | OPEN 404 | OPEN 404 |
| citizensbank | WALLED Ak 403 | WALLED Ak 403 | WALLED Ak 403 | WALLED Ak 403 | WALLED Ak 403 | WALLED Ak 403 | WALLED Ak 403 |
| delta | WALLED Ak 444 | WALLED Ak 444 | WALLED Ak 444 | WALLED Ak 444 | WALLED Ak 444 | WALLED Ak 444 | WALLED Ak 444 |
| easyjet | WALLED Ak 403 | OPEN 404 | OPEN 404 | OPEN 404 | OPEN 200 | OPEN 404 | OPEN 404 |
| ed.gov | CHALLENGED Az 403 | CHALLENGED Az 403 | CHALLENGED Az 403 | CHALLENGED Az 403 | CHALLENGED Az 403 | CHALLENGED Az 403 | CHALLENGED Az 403 |
| emirates | WALLED Ak 403 | UNREACHABLE | OPEN 404 | OPEN 404 | OPEN 200 | OPEN 404 | OPEN 404 |
| expedia | RATE_LIMITED 429 | RATE_LIMITED 429 | RATE_LIMITED 429 | RATE_LIMITED 429 | OPEN 200 | WALLED 403 | OPEN 200 |
| ftc.gov | WALLED Ak 403 | WALLED Ak 403 | WALLED Ak 403 | WALLED Ak 403 | WALLED Ak 403 | WALLED Ak 403 | WALLED Ak 403 |
| goodrx | CHALLENGED PX 403 | CHALLENGED PX 403 | CHALLENGED PX 403 | CHALLENGED PX 403 | OPEN 200 | OPEN 200 | CHALLENGED PX 403 |
| haaretz | WALLED 403 | WALLED 403 | WALLED 403 | WALLED 403 | WALLED 403 | WALLED 403 | WALLED 403 |
| hilton | WALLED Ak 403 | OPEN 404 | UNREACHABLE | OPEN 404 | OPEN 200 | OPEN 200 | OPEN 404 |
| homedepot | WALLED Ak 403 | OPEN 404 | UNREACHABLE | OPEN 404 | OPEN 200 | OPEN 404 | OPEN 404 |
| homes | WALLED Ak 403 | WALLED Ak 403 | WALLED Ak 403 | WALLED Ak 403 | WALLED Ak 403 | WALLED Ak 403 | WALLED Ak 403 |
| hotels | RATE_LIMITED 429 | RATE_LIMITED 429 | RATE_LIMITED 429 | RATE_LIMITED 429 | OPEN 200 | OPEN 404 | WALLED 403 |
| hyatt | WALLED 403 | WALLED 403 | WALLED 403 | WALLED 403 | WALLED 403 | WALLED 403 | WALLED 403 |
| macys | WALLED Ak 403 | WALLED Ak 403 | WALLED Ak 403 | WALLED Ak 403 | WALLED Ak 403 | WALLED Ak 403 | WALLED Ak 403 |
| marriott | WALLED Ak 403 | WALLED Ak 403 | WALLED Ak 403 | WALLED Ak 403 | WALLED Ak 403 | WALLED Ak 403 | WALLED Ak 403 |
| mayoclinic | WALLED Ak 403 | WALLED Ak 403 | WALLED Ak 403 | WALLED Ak 403 | WALLED Ak 403 | WALLED Ak 403 | WALLED Ak 403 |
| monster.ca | CHALLENGED DD 403 | CHALLENGED DD 403 | CHALLENGED DD 403 | CHALLENGED DD 403 | CHALLENGED DD 403 | CHALLENGED DD 403 | CHALLENGED DD 403 |
| nyc.gov | WALLED Ak 403 | WALLED Ak 403 | WALLED Ak 403 | WALLED Ak 403 | WALLED Ak 403 | WALLED Ak 403 | WALLED Ak 403 |
| orbitz | RATE_LIMITED 429 | RATE_LIMITED 429 | RATE_LIMITED 429 | RATE_LIMITED 429 | OPEN 200 | WALLED 403 | WALLED 403 |
| redfin | WALLED CFR 403 | WALLED CFR 403 | WALLED CFR 403 | WALLED CFR 403 | WALLED CFR 403 | WALLED CFR 403 | WALLED CFR 403 |
| sec.gov | WALLED Ak 403 | WALLED Ak 403 | WALLED Ak 403 | WALLED Ak 403 | WALLED Ak 403 | WALLED Ak 403 | WALLED Ak 403 |
| sky news | WALLED Ak 403 | WALLED Ak 403 | WALLED Ak 403 | WALLED Ak 403 | WALLED Ak 403 | WALLED Ak 403 | WALLED Ak 403 |
| ssa.gov | WALLED Ak 403 | WALLED Ak 403 | WALLED Ak 403 | WALLED Ak 403 | WALLED Ak 403 | WALLED Ak 403 | WALLED Ak 403 |
| state.gov | WALLED 403 | WALLED 403 | WALLED 403 | WALLED 403 | WALLED 403 | WALLED 403 | WALLED 403 |
| travelocity | RATE_LIMITED 429 | RATE_LIMITED 429 | RATE_LIMITED 429 | RATE_LIMITED 429 | OPEN 200 | WALLED 403 | WALLED 403 |
| tripadvisor | CHALLENGED DD 403 | CHALLENGED DD 403 | CHALLENGED DD 403 | CHALLENGED DD 403 | OPEN 200 | CHALLENGED DD 403 | CHALLENGED DD 403 |
| ubereats | CHALLENGED CF 403 | CHALLENGED CF 403 | CHALLENGED CF 403 | CHALLENGED CF 404 | CHALLENGED CF 403 | CHALLENGED CF 403 | CHALLENGED CF 403 |
| unitedhealthcare | WALLED CFR 403 | WALLED CFR 403 | WALLED CFR 403 | WALLED CFR 403 | WALLED CFR 403 | WALLED CFR 403 | WALLED CFR 403 |
| usa.gov | OPEN 200 | OPEN 404 | OPEN 404 | OPEN 404 | OPEN 200 | OPEN 200 | OPEN 404 |
| viator | CHALLENGED DD 403 | CHALLENGED DD 403 | CHALLENGED DD 403 | CHALLENGED DD 403 | CHALLENGED DD 403 | OPEN 404 | CHALLENGED DD 403 |
| vrbo | RATE_LIMITED 429 | RATE_LIMITED 429 | RATE_LIMITED 429 | OPEN 404 | OPEN 200 | OPEN 404 | WALLED 403 |
| webmd | OPEN 200 | OPEN 404 | OPEN 404 | OPEN 404 | OPEN 200 | OPEN 404 | OPEN 404 |
| zillow | OPEN 200 | OPEN 404 | OPEN 404 | OPEN 404 | CHALLENGED PX 200 | OPEN 404 | OPEN 404 |
| zocdoc | CHALLENGED DD 403 | CHALLENGED DD 403 | CHALLENGED DD 403 | CHALLENGED DD 403 | CHALLENGED DD 403 | OPEN 404 | CHALLENGED DD 403 |

Ak = Akamai, CF = Cloudflare, DD = DataDome, PX = PerimeterX,
Az = Microsoft Azure WAF, CFR = AWS CloudFront, Ka = Kasada.
WALLED/CHALLENGED with no vendor code are bare denies (no vendor
signals in the body). OPEN 404 rows are served responses with the
status on the record (Wave 2 precedent): the path doesn't exist
there, and nothing wall-like intervened. Delta's login row is the
post-fix re-probe (W8-001).

## Platform notes

- **The 21 whole-domain walls** — amtrak, apartments, citizensbank,
  ed.gov (Azure WAF), ftc.gov, haaretz (bare), homes, hyatt (bare),
  macys, marriott, mayoclinic, monster.ca (DataDome),
  careerbuilder.ca (DataDome), nyc.gov, redfin (CloudFront), sec.gov,
  sky news, ssa.gov, state.gov (bare), ubereats (Cloudflare),
  unitedhealthcare (CloudFront). No machine-file escape hatch on
  any of them. Akamai owns 13 of the 21.
- **The 8 homepage-only walls** — americanairlines, careerbuilder,
  careerjet, catho, easyjet, emirates, hilton, homedepot. The wall
  covers the homepage (and sometimes login) while robots.txt and
  most other paths serve. An agent that only ever fetches the
  homepage would call these platforms walled; an agent that reads
  robots.txt first would not.
- **Delta** — the wave's only 444 platform: all seven paths Akamai
  444, including the login row fixed by W8-001. A connection-kill
  wall is the hardest deny shape in the index: nothing is served,
  so there is nothing to appeal against except the reference ID.
- **The Expedia family throttle** — expedia, hotels, orbitz,
  travelocity 429 on all four app paths; vrbo on three (its `/api`
  is a 404). robots.txt serves on all five; sitemap/llms are bare
  403s on orbitz/travelocity, split on expedia (sitemap walled,
  llms genuine 200) and hotels/vrbo (sitemap 404, llms walled).
  The family's machine-file policy is inconsistent brand to brand
  — the kind of drift a quarterly re-verify exists to catch.
- **CareerBuilder vs careerbuilder.ca** — the same brand, two
  walls: .com is leaky (DataDome challenge on the homepage only;
  login/signup 404s; robots, sitemap, and a genuine llms.txt all
  serve; `/api` answers a 500) while .ca is uniformly
  DataDome-challenged on all seven paths. Regional deployments do
  not share wall policy.
- **Catho and careerjet** — the honest gates. Catho's homepage
  bare-403s but its login redirects to a served sign-in form and
  its llms.txt serves genuine text; careerjet challenges the
  homepage (Cloudflare stub at 200) but serves its login form.
  Both are the Wave 2 story again: the login path is sometimes the
  least-walled path on a walled domain.
- **SEC and BLS** — the dress-code pair. Both agencies' real API
  hosts (data.sec.gov, api.bls.gov) Akamai-wall this probe at
  their roots, while their front-doors entries document free,
  documented APIs. The probe is unidentified and datacenter-shaped;
  the agencies' own rules ask for an identifying User-Agent. The
  wall here may be a policy about the client, not the API.
- **Controls** — usa.gov, chase.com, airbnb, webmd, zillow all
  serve their homepages; the single control anomaly is zillow's
  robots.txt, a PerimeterX challenge body served at 200 (reviewed
  in PROBLEMS.md, not a defect). A control set that is 34-of-35
  clean with one documented exception is a control set working.
