# fix-kit — staged fixes for our own properties

*The campaign audits its own house first. Wave 3's `wallcheck
audit` graded clipwise.replit.app **D** and reneturcios.replit.app
**F**; Wave 5 staged the fixes. Nothing here is deployed yet —
deployment happens on Replit, by hand, per the steps below (this
wave does not deploy).*

## What was measured (2026-10-23, Wave 5)

| File | clipwise.replit.app | reneturcios.replit.app |
|---|---|---|
| `/robots.txt` | 200, real text — but minimal: no Sitemap line, no named-agent policy | **404** |
| `/sitemap.xml` | 200 but the **SPA shell HTML** (soft-404 — the W3-001 trap, on our own site) | **404** |
| `/llms.txt` | 200 but the **SPA shell HTML** (soft-404) | **404** |

The staged files in this directory fix exactly those rows. Their
content is written from the live sites' own text (titles, meta
descriptions, project lists, page inventory) — nothing invented.

## Deploy: reneturcios.replit.app (static site)

1. In the Repl, copy the three files from
   `reneturcios.replit.app/` here into the site root, next to
   `index.html` (alongside `blog.html`, `privacy.html`, …).
2. Redeploy the Repl.
3. Verify: `wallcheck audit reneturcios.replit.app` — robots_txt,
   llms_txt and sitemap should all PASS (grade rises from F (3/12)
   to C (7/12); B additionally needs the feed and the signed-agent
   directory — see `campaign/FIX-KIT.md` §7a. An earlier version of
   this line promised "at least B"; corrected in Wave 8.)

## Deploy: clipwise.replit.app (SPA)

The app is a single-page application: its catch-all route serves
`index.html` for every unknown path, which is why `/llms.txt` and
`/sitemap.xml` currently return HTML. The fix is placement, not
code:

1. Put `llms.txt` and `sitemap.xml` from `clipwise.replit.app/`
   here into the folder the Repl serves static files from
   verbatim — for a Vite/React app that is `public/`; the test is
   simple: after deploy, `curl https://clipwise.replit.app/llms.txt`
   must return the markdown as `text/plain`, not the app shell.
2. Replace the existing `/robots.txt` contents with the staged
   version (it already serves as real text; the staged file adds
   the Sitemap line and the explicit named-agent policy).
3. Redeploy the Repl.
4. Verify: `wallcheck audit clipwise.replit.app` — llms_txt and
   sitemap should flip FAIL → PASS.

## Why no source edits were made in this wave

Neither app's source repository exists in this workspace (searched
2026-10-23: the only Clipwise directories here are campaign /
outreach material, and no file in the tree carries the portfolio
site's markup — both apps live only on Replit). So the deliverable
is these staged files plus the steps above; the deploy itself is a
two-minute job inside each Repl, and the audit is the receipt.

## cloudcorprecords.github.io (added at the ship-readiness pass)

No kit existed for the Pages property, and no repository exists
for it yet — so this directory is a complete minimal site, built
at the pass: `index.html` (with the RSS discovery tag), `feed.xml`,
`robots.txt`, `llms.txt`, `sitemap.xml`, `.nojekyll` (so Pages
serves the dot-directory verbatim), and
`.well-known/http-message-signatures-directory` — a real Web Bot
Auth directory rendered by wallcheck's own `directory_document()`
from a fresh Ed25519 key (kid
`cloudcorprecords.github.io-2026-10`). The PRIVATE key file is
NOT in this kit and must never be committed: it lives at
`validation/ship-pass/cloudcorprecords-directory-key.json`
(owner-only permissions).

Predicted grade once deployed, verified against the audit's own
evaluation core on the kit files: **B (10/12)** — robots, llms,
sitemap, feed, and signed_agents PASS; api FAIL is the honest
documented absence (a static site has no API; campaign/FIX-KIT.md
§7b: a documented absence beats a fake spec).

One build note, kept because it is the campaign's own trap caught
on our own page: the first draft of `index.html` contained the
phrase "no CAPTCHA solving" — and wallcheck classified the
1.9 KB homepage itself as CHALLENGED (Generic, GENERIC_CAPTCHA):
a small page naming the challenge reads as a challenge stub. The
clause now reads "no evasion tooling"; the homepage classifies
OPEN.

Deploy = create the repository `CloudCorpRecords/
cloudcorprecords.github.io`, push these files as-is, confirm
Pages serves the root, then verify:
`wallcheck audit cloudcorprecords.github.io`.
