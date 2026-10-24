# Wave 7, Leg D — Owner Audit Sweep of the Most-Walled Domains

**Method.** `wallcheck audit` once per host over the union of
(a) every WALLED / CHALLENGED / RATE_LIMITED row in the merged
index (66 rows) and (b) every host whose directory path itself
was walled in census v2 (71 hosts) — 92 unique hosts after
dedupe. (The roadmap said "50 most-walled"; the task's set
definition is the union, so the sweep ran the full 92 rather
than truncating arbitrarily.) Raw results:
`results-audit-sweep.json`; targets in
`audit-sweep-targets.txt`.

## Grades: F 71 · D 18 · C 3 · B/A 0

No walled domain grades above C — and the ceiling is structural:
even the best-graded hosts fail `signed_agents` because their
directory path is itself walled.

**The three C grades** (best in the sweep): hub.docker.com
(robots PASS + llms.txt PASS + sitemap PASS), huggingface.co
(robots PASS + sitemap PASS + feed PASS), www.typeform.com
(llms.txt PASS + sitemap PASS). All three still fail
`signed_agents` and `api`.

## Per-check totals (92 hosts)

| Check | PASS | WARN | FAIL |
|---|---|---|---|
| robots_txt | 2 | 46 | 44 |
| llms_txt | 14 | 26 | 52 |
| sitemap | 37 | 17 | 38 |
| feed | 5 | 27 | 60 |
| api | 0 | 9 | 83 |
| signed_agents | 0 | 0 | 92 |

## The top-5 systemic owner mistakes (patterns, not exceptions)

**1. No signed-agent recognition path — 92/92 FAIL.**
Every swept host fails `signed_agents`. Selection effect, stated
plainly: adopters are by definition not walled, so they are not
in this sweep — but the census puts the whole web at 4/499, and
even the sweep's OPEN sites (whose homepages serve) fail it
because their directory path is walled. The fix is two steps
owners miss: publish the directory AND let the well-known path
through the wall ruleset.

**2. No machine-readable API surface — 0/92 PASS.**
83 FAIL, 9 WARN — and every WARN is "a developer portal page
serves, but no machine-readable API spec was discovered"
(etsy, huggingface, sendgrid, census.gov, chicagotribune,
energy.gov, reddit, typeform, usps). Sites that *have*
developer programs still do not publish an OpenAPI document at
a conventional path. Agents integrate against specs, not
marketing pages.

**3. Machine directives walled or blanket-blocked.**
robots.txt FAILs split 32 walled / 11 wildcard-block-everything
/ 1 absent. Of the 46 WARNs (robots served), the dominant shape
is named-AI-agent refusal: medium.com, ebay.com, apnews.com,
upwork.com, americanairlines, easyjet, emirates, hilton,
homedepot and most others block or restrict GPTBot, ClaudeBot,
CCBot, Google-Extended. Only 2 hosts in the sweep pass robots
clean (hub.docker.com, huggingface.co — no tracked agent
blocked or restricted). A robots file that agents cannot fetch,
or that refuses every named agent, is not an agent policy — it
is an absence of one.

**4. llms.txt: walled, fake, or missing.**
FAIL splits 48 walled / 4 soft-404-HTML (claude.ai, sendgrid,
engadget, reddit serve HTML at /llms.txt with a 200 — worse
than absent, because it lies to the fetcher); 26 more are
honestly absent (WARN). Only 14 PASS. The soft-404 four are the
cheapest fix in the whole sweep: serve real text or a real 404.

**5. Feeds are dead as an agent channel — 60 FAIL, 5 PASS.**
Only huggingface, chicagotribune, dawn, engadget, koreaherald
advertise a feed. Four of the five are news outlets — the one
category where feeds should be universal — which means even
news has mostly abandoned the lowest-cost agent channel there
is.

## The counter-pattern (why this sweep is not counsel of despair)

Machine files slip through walls that stop homepages — the
Wave 2 seam, now at sweep scale:

- **14 hosts serve real llms.txt**, including five walled
  freelance platforms (upwork, fiverr, monster, careerbuilder,
  catho) plus etsy, expedia, clickup, docker hub, ally,
  glassdoor, levels.fyi, typeform.
- **17 walled/challenged domains serve real sitemaps**
  (medium, americanairlines, catho, easyjet, ebay, emirates,
  hilton, homedepot, booking, economist, fastcompany, ft,
  goodrx, inc, nytimes, reuters, wsj).

The owners who left these files open — deliberately or by
default — already run the cheapest version of the fix kit. The
sweep's message to the other 78 is: your peers' machine files
are already out there, and nothing broke.

## Note on what the sweep does not show

`signed_agents` FAIL 92/92 in this sweep must not be quoted as
"0% adoption" — the census (DIRECTORY-2.md) is the adoption
measure (4/499). The sweep measures the *walled set's* posture,
and its honest headline is narrower: among the web's most-walled
domains, not one offers a signed agent a recognition path.
