# Bot Wall Index — Seed (Wave 1, final round)

First measured seed for the Bot Wall Index (SPEC.md): 58 targets across
freelance platforms, job boards, dev platforms, social, docs/news, big
web, and our own properties (dogfood rule: ours are in first).

**Source:** `results-round2.json` — the final verified set (round-1 run
of all 58, with the 14 targets affected by Wave 1 classifier fixes
re-probed live in round 2; see PROBLEMS.md). No verdict here comes from
an unverified round.

**Scan context (read before quoting):** 2026-10-24, from a datacenter
egress IP (this build VM) with wallcheck's honest identified user agent
and a single non-browser fetch per target. Bot walls are
context-sensitive by design — the same site from a residential IP or a
full browser may score differently. These are *this client's* measured
results, with evidence on file (results JSON + captures/), not universal
claims about a site.

**Distribution:** OPEN 47 · WALLED 4 · CHALLENGED 4 · UNREACHABLE 3 ·
LOGIN_GATED 0 · RATE_LIMITED 0.

## The walls (8 of 58)

| site | category | verdict | vendor | status |
| --- | --- | --- | --- | --- |
| www.upwork.com | freelance | WALLED | Cloudflare | 403 |
| www.fiverr.com | freelance | CHALLENGED | PerimeterX | 403 |
| www.guru.com | freelance | WALLED | Imperva | 403 |
| www.monster.com | jobs | CHALLENGED | DataDome | 403 |
| www.npmjs.com | dev | CHALLENGED | Cloudflare | 403 |
| medium.com | docs-news | WALLED | Cloudflare | 403 |
| www.nytimes.com | docs-news | CHALLENGED | DataDome | 403 |
| www.ebay.com | big-web | WALLED | Akamai | 403 |

Five vendors across eight walls — and the freelance category is the
most walled on the board: 3 of 7 freelance platforms stop an identified
agent at the door (Upwork hard-blocks, Fiverr challenges, Guru hard-
blocks), while Contra, Freelancer, PeoplePerHour, and Toptal serve.

## Unreachable from this client (3)

| site | category | verdict | evidence |
| --- | --- | --- | --- |
| replit.com | dev | UNREACHABLE | 15 s timeout, reproduced 3× |
| discord.com | social | UNREACHABLE | 15 s timeout, reproduced 3× |
| www.bestbuy.com | big-web | UNREACHABLE | read timeout, reproduced 3× |

Recorded as UNREACHABLE per SPEC — the fetch fails, so no wall verdict
is claimed. (PROBLEMS.md W1-006.)

## Full table (final round)

| site | category | verdict | vendor | status |
| --- | --- | --- | --- | --- |
| contra.com | freelance | OPEN | — | 200 |
| www.fiverr.com | freelance | CHALLENGED | PerimeterX | 403 |
| www.freelancer.com | freelance | OPEN | — | 200 |
| www.guru.com | freelance | WALLED | Imperva | 403 |
| www.peopleperhour.com | freelance | OPEN | — | 200 |
| www.toptal.com | freelance | OPEN | — | 200 |
| www.upwork.com | freelance | WALLED | Cloudflare | 403 |
| remoteok.com | jobs | OPEN | — | 200 |
| wellfound.com | jobs | OPEN | — | 200 |
| www.dice.com | jobs | OPEN | — | 200 |
| www.glassdoor.com | jobs | OPEN | — | 200 |
| www.indeed.com | jobs | OPEN | — | 200 |
| www.linkedin.com | jobs | OPEN | — | 200 |
| www.monster.com | jobs | CHALLENGED | DataDome | 403 |
| www.ziprecruiter.com | jobs | OPEN | — | 200 |
| bitbucket.org | dev | OPEN | — | 200 |
| github.com | dev | OPEN | — | 200 |
| gitlab.com | dev | OPEN | — | 200 |
| hub.docker.com | dev | OPEN | — | 200 |
| huggingface.co | dev | OPEN | — | 200 |
| pypi.org | dev | OPEN | — | 200 |
| replit.com | dev | UNREACHABLE | — | — |
| sourceforge.net | dev | OPEN | — | 200 |
| stackoverflow.com | dev | OPEN | — | 200 |
| vercel.com | dev | OPEN | — | 200 |
| www.netlify.com | dev | OPEN | — | 200 |
| www.npmjs.com | dev | CHALLENGED | Cloudflare | 403 |
| discord.com | social | UNREACHABLE | — | — |
| www.facebook.com | social | OPEN | — | 200 |
| www.instagram.com | social | OPEN | — | 200 |
| www.reddit.com | social | OPEN | — | 200 |
| www.threads.com | social | OPEN | — | 200 |
| www.tiktok.com | social | OPEN | — | 200 |
| www.twitch.tv | social | OPEN | — | 200 |
| www.youtube.com | social | OPEN | — | 200 |
| x.com | social | OPEN | — | 200 |
| arstechnica.com | docs-news | OPEN | — | 200 |
| dev.to | docs-news | OPEN | — | 200 |
| en.wikipedia.org | docs-news | OPEN | — | 200 |
| medium.com | docs-news | WALLED | Cloudflare | 403 |
| news.ycombinator.com | docs-news | OPEN | — | 200 |
| substack.com | docs-news | OPEN | — | 200 |
| techcrunch.com | docs-news | OPEN | — | 200 |
| www.bbc.com | docs-news | OPEN | — | 200 |
| www.nytimes.com | docs-news | CHALLENGED | DataDome | 403 |
| www.amazon.com | big-web | OPEN | — | 200 |
| www.apple.com | big-web | OPEN | — | 200 |
| www.bestbuy.com | big-web | UNREACHABLE | — | — |
| www.cloudflare.com | big-web | OPEN | — | 200 |
| www.ebay.com | big-web | WALLED | Akamai | 403 |
| www.google.com | big-web | OPEN | — | 200 |
| www.microsoft.com | big-web | OPEN | — | 200 |
| www.netflix.com | big-web | OPEN | — | 200 |
| www.target.com | big-web | OPEN | — | 200 |
| www.walmart.com | big-web | OPEN | — | 200 |
| clipwise.replit.app | own | OPEN | — | 200 |
| cloudcorprecords.github.io | own | OPEN | — | 404 |
| reneturcios.replit.app | own | OPEN | — | 200 |

Notes on reading the table: `cloudcorprecords.github.io` is OPEN with a
404 — the response was served (GitHub Pages' 404 page; no site is
published at that root) and nothing wall-like intervened (PROBLEMS.md
W1-007). Vendor `—` on a walled row would mean an unattributed wall;
Wave 1 ends with every wall attributed.
