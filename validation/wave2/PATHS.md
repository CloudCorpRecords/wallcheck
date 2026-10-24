# Wave 2 — Depth Probing: the path matrix

Wave 1 measured homepages. Wave 2 asks the sharper question: *where*
does each wall actually stand? 77 probes — login, signup, search,
developer/API surfaces, and the machine files (`/robots.txt`,
`/sitemap.xml`, `/llms.txt`) — across the 8 walled/challenged
platforms from the Index seed, plus Contra (open control) and
LinkedIn/Indeed (open-homepage jobs platforms).

**Source:** `results-paths.json` — merged final set (full 77-probe
run; the 6 paths affected by the Wave 2 classifier fixes re-probed
live in round 2 and merged; round 1 preserved in
`results-paths-round1.json`, the ledger in `PROBLEMS.md`).

**Scan context (read before quoting):** 2026-10-24, same client as
Wave 1 — a datacenter egress IP (this build VM), wallcheck's honest
identified user agent, one fetch per URL, no retries, full back-off
on any 429 (none occurred). Verdicts are *this client's* measured
results with evidence on file, not universal claims about a site.

**Distribution (77 paths):** OPEN 38 · WALLED 17 · CHALLENGED 16 ·
LOGIN_GATED 3 · UNREACHABLE 3 · RATE_LIMITED 0 · SKIPPED 0.

## The four stories the data tells

**1. APIs beat webs.** Where a platform runs a real API host, it
serves the agent its own homepage refuses: `registry.npmjs.org`
answers package queries OPEN while every `www.npmjs.com` path — even
robots.txt — is Cloudflare-challenged; `api.medium.com` serves while
medium.com is WALLED; `developer.nytimes.com` serves while
nytimes.com is DataDome-challenged. The exception is eBay:
`developer.ebay.com` is Akamai-WALLED like the rest of eBay.

**2. The machine files slip through — except when they don't.**
`llms.txt` is real (verified `text/plain` content, not soft-200s) and
OPEN on four walled/challenged platforms: Upwork, Fiverr, Monster,
Indeed. `robots.txt` serves on 9 of 11 platforms. The two platforms
that wall even the machine files are the extremes of the board: Guru
walls *everything* including robots.txt (the only whole-domain wall
in the wave), and npmjs challenges robots.txt, sitemap, and llms.txt
alike — the deepest wall measured. And one inversion: NYT blocks its
`sitemap.xml` (bare 403, unattributed — W2-005) while serving
robots.txt.

**3. "Login-gated" almost never means a login page.** After the
Wave 2 fixes, exactly 3 of 11 login paths are genuine served login
pages (LinkedIn, Indeed, and eBay on the attempt where Bot Manager
let it through). The rest were walls standing *in front of* the
login page (Upwork/Fiverr/npmjs challenged, Guru walled) or paths
that no longer exist (Monster, Contra — plain 404s). An agent that
reports "login required" for a walled login page is debugging the
wrong layer — which is the failure mode wallcheck exists to kill.

**4. Some walls kill the connection.** Three probes (Guru sitemap,
NYT section, npm search) died with the server closing the connection
mid-flight — all on domains that wall this client everywhere else
(W2-004). Recorded UNREACHABLE per SPEC; no wall verdict claimed.

## Per-platform matrix (final, post-fix)

| platform | home | login | signup/join | search | dev/api | robots | sitemap | llms |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| upwork | WALLED CF 403 | CHALLENGED CF | CHALLENGED CF | WALLED CF | WALLED CF | OPEN 200 | WALLED CF | **OPEN 200** |
| fiverr | CHALLENGED PX | CHALLENGED PX | CHALLENGED PX | CHALLENGED PX | — | OPEN 200 | OPEN 404 | **OPEN 200** |
| guru | WALLED Imperva | WALLED Imperva | — | WALLED Imperva | — | WALLED Imperva | UNREACHABLE | WALLED Imperva |
| ebay | WALLED Akamai | LOGIN_GATED 200* | — | WALLED Akamai | WALLED Akamai | OPEN 200 | OPEN 404 | OPEN 404 |
| medium | WALLED CF | WALLED CF | — | WALLED CF (topic) | OPEN 200 (api root) | OPEN 200 | OPEN 404 | WALLED CF |
| monster | CHALLENGED DD | OPEN 404 | — | CHALLENGED DD | — | OPEN 200 | OPEN 404 | **OPEN 200** |
| nytimes | CHALLENGED DD | — | — | CHALLENGED DD | OPEN 200 (dev), OPEN 404 (api) | OPEN 200 | WALLED — 403 | OPEN 404 |
| npmjs | CHALLENGED CF | CHALLENGED CF | CHALLENGED CF | UNREACHABLE | **OPEN 200 (registry)** | CHALLENGED CF | CHALLENGED CF | CHALLENGED CF |
| contra | OPEN 200 | OPEN 404 | OPEN 200 | OPEN 200 (hire) | — | OPEN 200 | OPEN 200 | OPEN 404 |
| linkedin | OPEN 200 | LOGIN_GATED 200 | OPEN 200 | OPEN 200 (jobs) | — | OPEN 200 | OPEN 404 | OPEN 404 |
| indeed | OPEN 200 | LOGIN_GATED 200 | — | OPEN 200 (jobs) | — | OPEN 200 | OPEN 404 | **OPEN 200** |

CF = Cloudflare, PX = PerimeterX, DD = DataDome. OPEN 404 rows are
served responses with the status on the record (family precedent,
W1-007): the path doesn't exist there, and nothing wall-like
intervened. *eBay sign-in alternated across attempts between an
Akamai 403 deny and a served 200 login form (W2-001); the final
merged row is the served form.

## Platform notes

- **Upwork** — every human path is behind Cloudflare (hard block on
  home/jobs/developers, challenge on login/signup), yet robots.txt
  and a genuine llms.txt serve openly. The wall is total for people
  shaped like agents and irrelevant to the files written for
  machines.
- **Fiverr** — the uniform wall: PerimeterX challenges all four app
  paths identically; robots.txt and a genuine llms.txt open.
- **Guru** — the wave's only whole-domain wall: Imperva blocks all
  six reachable paths including robots.txt and llms.txt; the
  sitemap connection was killed outright.
- **eBay** — Akamai walls home, search, and the developer portal.
  The sign-in host flips between deny and serve (see matrix note).
- **Medium** — Cloudflare walls the web surface (home, sign-in,
  topic, llms) while the API root and robots.txt serve.
- **Monster** — DataDome challenges content paths; the legacy login
  path is simply gone (404); a genuine llms.txt serves.
- **NYTimes** — DataDome challenges the reading surface; the
  developer portal and API root serve; the sitemap is bare-403
  walled (W2-005).
- **npmjs** — the deepest wall: Cloudflare challenges every www
  path including robots.txt; the registry API — the actual product
  surface for machines — is wide open.
- **Contra** — no wall anywhere (the control behaves like a
  control). Its /login answers a 404-status app page to this
  non-JS client; recorded OPEN 404.
- **LinkedIn / Indeed** — open webs with honest login gates:
  served login pages (LinkedIn direct, Indeed via its SSO host),
  everything else open; Indeed also publishes a genuine llms.txt.
