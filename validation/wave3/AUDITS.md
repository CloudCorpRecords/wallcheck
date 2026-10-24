# Wave 3 — owner audits (v0.3 prototype, first live runs)

`wallcheck audit <domain>` grades a site's agent-access posture the
way SPEC.md defines the owner audit: six checks (robots.txt +
named-AI-agent directives, llms.txt sanity, sitemap, feed
discovery, API discovery, signed-agent readiness), PASS=2 / WARN=1
/ FAIL=0 across 12 points, graded A≥11, B≥9, C≥7, D≥5, else F.
Every check runs its fetched resources back through the probe
classifier, so a machine file behind a wall fails *as a wall*.
One honest fetch per resource; the outputs below are the tool's
actual output on 2026-10-23 (raw JSON alongside in `audits/`).

Headline of the first run: **github.com grades highest (C) and
every other audited site — including all three of ours — grades D
or F.** The signed-agent check fails or warns on all five: nobody
publishes a Web Bot Auth directory yet, which is the baseline the
signed-identity front of the campaign has to move. And the audit's
first dogfood catch is ours: clipwise.replit.app serves its SPA
shell as /llms.txt (200, HTML) — the soft-404 failure the Wave 2
path table taught us to test for, live on our own property.

## clipwise.replit.app — grade D (5/12)

```
audit clipwise.replit.app -> grade D (5/12)
  [PASS] robots_txt — robots.txt served; no tracked AI agent is blocked or restricted.
      - ROBOTS_200
  [FAIL] llms_txt — /llms.txt returns 200 but serves HTML (a soft-404 error page or the homepage) — worse than absent: agents ingest it as if it were the real index.
      - SOFT_404_HTML
  [WARN] sitemap — Sitemap URL answers 200 but the body is not sitemap XML.
      - STATUS_200_NOT_XML
  [WARN] feed — Homepage carries no RSS/Atom <link rel="alternate"> discovery tag.
      - NO_FEED_LINK
  [FAIL] api — No OpenAPI document, serving /api root, or developer portal discovered.
      - OPENAPI_NOT_SPEC: https://clipwise.replit.app/openapi.json status 200, not an OpenAPI document
      - OPENAPI_NOT_SPEC: https://clipwise.replit.app/.well-known/openapi.json status 200, not an OpenAPI document
      - DEV_PORTAL_IS_APP_SHELL
  [WARN] signed_agents — The directory URL answers 200 but the body is not a JWKS-style key set.
      - DIRECTORY_UNPARSEABLE
  fixes:
    - Publish a genuine /llms.txt (plain text/markdown index of your key pages) — and never let the route fall through to an HTML error page.
    - Serve /sitemap.xml (or declare Sitemap: in robots.txt) and keep bot walls off it: it is the file you publish *for* machines.
    - Add <link rel="alternate" type="application/rss+xml"> (or Atom) discovery tags to the homepage, or publish a feed — feeds are the lowest-cost agent channel there is.
    - Publish a machine-readable API surface: an OpenAPI document (conventionally /openapi.json) or a documented /api — agents integrate against specs, not markup.
    - Publish your Web Bot Auth key directory at /.well-known/http-message-signatures-directory and, on the receiving side, exempt verified signed agents from managed challenges on public paths (authenticated paths keep full protection).
```

## reneturcios.replit.app — grade F (3/12)

```
audit reneturcios.replit.app -> grade F (3/12)
  [FAIL] robots_txt — No robots.txt served (status 404): crawlers and agents get no directives at all.
      - STATUS_404
  [WARN] llms_txt — No /llms.txt (honest 404). Agents get no curated map of the site's content.
      - STATUS_404
  [WARN] sitemap — No sitemap at https://reneturcios.replit.app/sitemap.xml (status 404).
      - STATUS_404
  [WARN] feed — Homepage carries no RSS/Atom <link rel="alternate"> discovery tag.
      - NO_FEED_LINK
  [FAIL] api — No OpenAPI document, serving /api root, or developer portal discovered.
      - NO_API_SURFACE
  [FAIL] signed_agents — No Web Bot Auth key directory published (status 404) — the site gives signed agents no way to be recognized. Expected almost everywhere today; recorded as data.
      - STATUS_404
  fixes:
    - Publish/maintain /robots.txt and scope any Disallow rules to the paths that need them; a blanket block of named AI agents also blocks the agents your own users send.
    - Publish a genuine /llms.txt (plain text/markdown index of your key pages) — and never let the route fall through to an HTML error page.
    - Serve /sitemap.xml (or declare Sitemap: in robots.txt) and keep bot walls off it: it is the file you publish *for* machines.
    - Add <link rel="alternate" type="application/rss+xml"> (or Atom) discovery tags to the homepage, or publish a feed — feeds are the lowest-cost agent channel there is.
    - Publish a machine-readable API surface: an OpenAPI document (conventionally /openapi.json) or a documented /api — agents integrate against specs, not markup.
    - Publish your Web Bot Auth key directory at /.well-known/http-message-signatures-directory and, on the receiving side, exempt verified signed agents from managed challenges on public paths (authenticated paths keep full protection).
```

## cloudcorprecords.github.io — grade F (3/12)

```
audit cloudcorprecords.github.io -> grade F (3/12)
  [FAIL] robots_txt — No robots.txt served (status 404): crawlers and agents get no directives at all.
      - STATUS_404
  [WARN] llms_txt — No /llms.txt (honest 404). Agents get no curated map of the site's content.
      - STATUS_404
  [WARN] sitemap — No sitemap at https://cloudcorprecords.github.io/sitemap.xml (status 404).
      - STATUS_404
  [WARN] feed — Homepage answered status 404; no feed discovery performed.
      - STATUS_404
  [FAIL] api — No OpenAPI document, serving /api root, or developer portal discovered.
      - NO_API_SURFACE
  [FAIL] signed_agents — No Web Bot Auth key directory published (status 404) — the site gives signed agents no way to be recognized. Expected almost everywhere today; recorded as data.
      - STATUS_404
  fixes:
    - Publish/maintain /robots.txt and scope any Disallow rules to the paths that need them; a blanket block of named AI agents also blocks the agents your own users send.
    - Publish a genuine /llms.txt (plain text/markdown index of your key pages) — and never let the route fall through to an HTML error page.
    - Serve /sitemap.xml (or declare Sitemap: in robots.txt) and keep bot walls off it: it is the file you publish *for* machines.
    - Add <link rel="alternate" type="application/rss+xml"> (or Atom) discovery tags to the homepage, or publish a feed — feeds are the lowest-cost agent channel there is.
    - Publish a machine-readable API surface: an OpenAPI document (conventionally /openapi.json) or a documented /api — agents integrate against specs, not markup.
    - Publish your Web Bot Auth key directory at /.well-known/http-message-signatures-directory and, on the receiving side, exempt verified signed agents from managed challenges on public paths (authenticated paths keep full protection).
```

## github.com — grade C (7/12)

```
audit github.com -> grade C (7/12)
  [WARN] robots_txt — robots.txt is served, but named AI agents are refused: GPTBot restricted, ClaudeBot restricted, CCBot restricted, Google-Extended restricted.
      - ROBOTS_200
      - SITEMAP_DECLARED: https://github.com/sitemap_marketing.xml
      - AI_RESTRICTED: GPTBot
      - AI_RESTRICTED: ClaudeBot
      - AI_RESTRICTED: CCBot
      - AI_RESTRICTED: Google-Extended
  [PASS] llms_txt — /llms.txt served as genuine text (28658 bytes captured).
      - LLMS_TEXT 28658 bytes
  [PASS] sitemap — Sitemap served as XML — agents can enumerate public content without scraping.
      - SITEMAP_XML
      - VIA_ROBOTS_DECLARATION
  [WARN] feed — Homepage carries no RSS/Atom <link rel="alternate"> discovery tag.
      - NO_FEED_LINK
  [WARN] api — A developer portal page serves, but no machine-readable API spec was discovered.
      - DEV_PORTAL_200
  [FAIL] signed_agents — No Web Bot Auth key directory published (status 404) — the site gives signed agents no way to be recognized. Expected almost everywhere today; recorded as data.
      - STATUS_404
  fixes:
    - Publish/maintain /robots.txt and scope any Disallow rules to the paths that need them; a blanket block of named AI agents also blocks the agents your own users send.
    - Add <link rel="alternate" type="application/rss+xml"> (or Atom) discovery tags to the homepage, or publish a feed — feeds are the lowest-cost agent channel there is.
    - Publish a machine-readable API surface: an OpenAPI document (conventionally /openapi.json) or a documented /api — agents integrate against specs, not markup.
    - Publish your Web Bot Auth key directory at /.well-known/http-message-signatures-directory and, on the receiving side, exempt verified signed agents from managed challenges on public paths (authenticated paths keep full protection).
```

## example.com — grade F (3/12)

```
audit example.com -> grade F (3/12)
  [FAIL] robots_txt — No robots.txt served (status 404): crawlers and agents get no directives at all.
      - STATUS_404
  [WARN] llms_txt — No /llms.txt (honest 404). Agents get no curated map of the site's content.
      - STATUS_404
  [WARN] sitemap — No sitemap at https://example.com/sitemap.xml (status 404).
      - STATUS_404
  [WARN] feed — Homepage carries no RSS/Atom <link rel="alternate"> discovery tag.
      - NO_FEED_LINK
  [FAIL] api — No OpenAPI document, serving /api root, or developer portal discovered.
      - NO_API_SURFACE
  [FAIL] signed_agents — No Web Bot Auth key directory published (status 404) — the site gives signed agents no way to be recognized. Expected almost everywhere today; recorded as data.
      - STATUS_404
  fixes:
    - Publish/maintain /robots.txt and scope any Disallow rules to the paths that need them; a blanket block of named AI agents also blocks the agents your own users send.
    - Publish a genuine /llms.txt (plain text/markdown index of your key pages) — and never let the route fall through to an HTML error page.
    - Serve /sitemap.xml (or declare Sitemap: in robots.txt) and keep bot walls off it: it is the file you publish *for* machines.
    - Add <link rel="alternate" type="application/rss+xml"> (or Atom) discovery tags to the homepage, or publish a feed — feeds are the lowest-cost agent channel there is.
    - Publish a machine-readable API surface: an OpenAPI document (conventionally /openapi.json) or a documented /api — agents integrate against specs, not markup.
    - Publish your Web Bot Auth key directory at /.well-known/http-message-signatures-directory and, on the receiving side, exempt verified signed agents from managed challenges on public paths (authenticated paths keep full protection).
```

## Notes on the five

- **github.com (C, 7/12)** — the strongest posture of the five: a
  genuine llms.txt (28,658 bytes) and a robots-declared sitemap
  both PASS. Its robots.txt restricts all four tracked AI agents
  by path (WARN). The api check grades WARN on the developer
  portal: the audit discovers API surfaces on the audited
  domain's own well-known paths, and GitHub's API lives on
  api.github.com — a per-domain scope limit, documented here
  rather than silently "fixed". signed_agents FAILs: no
  directory published.
- **clipwise.replit.app (D, 5/12)** — robots.txt PASSes, then the
  SPA fallback does the damage: /llms.txt and /sitemap.xml return
  the app shell (soft-404 HTML → llms FAIL, sitemap WARN), the
  OpenAPI candidates return the shell (named as
  OPENAPI_NOT_SPEC / DEV_PORTAL_IS_APP_SHELL after the W3-004
  fix), and even the signatures directory returns an unparseable
  200 shell (WARN). The fixes list is a real work list for
  Front 4 (owner fixes), starting with a genuine /llms.txt.
- **reneturcios.replit.app (F, 3/12)** — clean 404s everywhere:
  no robots.txt, no llms.txt, no sitemap, no API surface, no
  directory. Honest absences, graded as absences.
- **cloudcorprecords.github.io (F, 3/12)** — same absences, plus
  the homepage itself answered 404: the GitHub Pages root serves
  nothing today. Another Front-4 work item the audit surfaced.
- **example.com (F, 3/12)** — the control case: a deliberately
  minimal site grades F, which is the correct read of a page that
  offers agents no machine surface of any kind.

## Grading nuances recorded for the next wave

- signed_agents grades a clean 404 FAIL (definitively unpublished)
  but an unparseable 200 WARN (ambiguous: a misconfigured
  directory could sit there). Both mean "not ready today"; the
  distinction is kept so longitudinal data can watch junk 200s
  resolve in either direction.
- A site whose SPA shell answers everything (clipwise) scores
  *worse* on llms.txt than an honest 404 (reneturcios): FAIL vs
  WARN. That asymmetry is deliberate — a soft-404 actively feeds
  agents wrong data.
