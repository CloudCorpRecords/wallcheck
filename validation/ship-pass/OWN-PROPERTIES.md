# Ship-readiness pass — own-properties deploys (Workstream 2)

*2026-10-24, ship-readiness pass. Baselines re-measured live this
session before any deploy attempt (they match the Wave 8
re-audit): clipwise.replit.app **D (5/12)**,
reneturcios.replit.app **F (3/12)**, cloudcorprecords.github.io
**F (3/12)**. No property's grade changed this pass — all three
deploys are blocked, each by a named, external blocker, recorded
below with the exact unblock step. Nothing was faked: no grade
below is a prediction presented as a measurement (the one
prediction, for Pages, is labeled as such and was produced by
the audit's own evaluation core on the staged files).*

## 1. reneturcios.replit.app — edits applied, publish BLOCKED (billing)

- **Route attempted:** Replit connector (connected, `apps.edit`
  scope granted). App identified by publish status: "rene
  turcios portfolio", replId
  `2f89ad40-dc6a-4b25-a78b-fdffc720317e`, live at
  https://reneturcios.replit.app (deployment
  `4ee06a36-779b-403e-9f70-b76e756e53e5`).
- **What was done:** `update_app_using_prompt` accepted with the
  three staged files (robots.txt, llms.txt, sitemap.xml) embedded
  byte-for-byte, addressed to the site root next to index.html;
  Replit reported phase "updating" (turn
  `…/eca0781f-b632-4965-9de0-60dbaa7f56dc/…`).
- **What blocked it:** `publish_app` returned an account
  restriction, verbatim from Replit: *"Your payment is past due.
  Pay outstanding invoices or update your payment method in
  Billing to continue."* Publishing from the Replit website is
  subject to the same restriction. A first publish attempt's
  CLI call was killed mid-flight; publish status was inspected
  before retrying (deployment unchanged) per the connector's
  recovery rule, and the retry returned the billing block.
- **Live state now:** unchanged — old deployment still serving;
  baseline audit stands: robots FAIL (404), llms WARN (404),
  sitemap WARN (404), feed WARN, api FAIL, signed_agents FAIL →
  **F (3/12)**.
- **Expected after publish:** robots PASS, llms PASS, sitemap
  PASS → **C (7/12)** (Wave 8's corrected expectation; B would
  additionally need a feed and the signed-agent directory,
  neither of which is in the staged kit for this property).
- **Unblock (Rene):** resolve Replit billing (pay outstanding
  invoices or update the payment method at replit.com →
  Billing). Then either click Deploy in the Repl, or tell Tree —
  one `publish_app` call per app finishes it, followed by a
  verification audit.

## 2. clipwise.replit.app — edits applied, publish BLOCKED (billing)

- **Route attempted:** Replit connector. App "clipwise", replId
  `b6ceb444-917e-48f6-867b-c62547acad0a`, live at
  https://clipwise.replit.app (deployment
  `8cd4c9aa-0e1e-4123-92a7-cf0fb125ae2f`).
- **What was done:** `update_app_using_prompt` accepted with
  the three staged files embedded byte-for-byte, addressed to
  the app's `public/` folder (llms.txt + sitemap.xml new,
  robots.txt replacing), with the explicit requirement that
  they serve verbatim, not through the SPA catch-all. Phase
  "updating" (turn `…/01a130e1-90d5-749e-859c-4e863462fd08`).
- **What blocked it:** `publish_app` returned the identical
  account restriction (payment past due) — account-level, not
  app-level.
- **Live state now:** unchanged. Baseline audit stands:
  robots PASS, llms FAIL (soft-404 HTML — the W3-001 trap on
  our own site), sitemap WARN (200, not XML), feed WARN,
  api FAIL (SPA shell at the OpenAPI paths), signed_agents
  WARN (directory path serves the shell) → **D (5/12)**.
- **Expected after publish:** llms FAIL → PASS, sitemap
  WARN → PASS → **C (8/12)**.
- **Unblock (Rene):** same billing fix as above; then publish
  (his click or Tree's call) + verification audit.

## 3. cloudcorprecords.github.io — BLOCKED (repository does not exist)

- **Route attempted:** GitHub connector (connected as
  CloudCorpRecords). `GET repos/CloudCorpRecords/
  cloudcorprecords.github.io` → **404 Not Found**; repository
  search for the name and for any `*.github.io` repo under the
  account → 0 results. The Pages site 404s because there is no
  repository at all — Wave 8's "the root 404s" was this.
- **Why not fixed here:** creating the repository is outside
  this pass's boundary (the pass prepares wallcheck for ship
  and publishes nothing; repo creation is a ship-side act).
- **What is staged (complete, deploy-ready):**
  `fix-kit/cloudcorprecords.github.io/` — `index.html` (with
  the RSS discovery tag), `feed.xml` (one real item),
  `robots.txt`, `llms.txt`, `sitemap.xml`, `.nojekyll` (so
  Pages serves the dot-directory verbatim), and
  `.well-known/http-message-signatures-directory` — a real
  Web Bot Auth directory rendered by wallcheck's own
  `directory_document()` from a fresh Ed25519 key (kid
  `cloudcorprecords.github.io-2026-10`, fingerprint
  `5da40e32b87f4fd7`). The private key file is NOT in the kit
  and must never be committed; it is custodied at
  `validation/ship-pass/cloudcorprecords-directory-key.json`
  (owner-only permissions, written by `save_key`).
- **Predicted grade: B (10/12)** — produced by running the
  audit's own `evaluate_audit` over the kit files (not a live
  measurement): robots PASS, llms PASS, sitemap PASS, feed
  PASS, signed_agents PASS; api FAIL — the honest documented
  absence (a static site has no API; FIX-KIT.md §7b: a
  documented absence beats a fake spec).
- **Build note (the campaign's trap, caught on our own page):**
  the first draft of the kit's `index.html` contained the
  phrase "no CAPTCHA solving" and wallcheck classified the
  1.9 KB homepage itself CHALLENGED (Generic,
  GENERIC_CAPTCHA) — a small page naming the challenge reads
  as a challenge stub (the 16 KB served-page gate). The clause
  now reads "no evasion tooling"; the homepage classifies
  OPEN. Recorded in the fix-kit README.
- **Unblock (Rene, or Tree on his word):** create the
  repository `CloudCorpRecords/cloudcorprecords.github.io`,
  push the kit files as-is, confirm Pages serves the root,
  then run `wallcheck audit cloudcorprecords.github.io` for
  the live grade.

## Bottom line

| Property | Before | After this pass | Expected once unblocked |
|---|---|---|---|
| clipwise.replit.app | D (5/12) | D (5/12) — edits in workspace, publish blocked | C (8/12) |
| reneturcios.replit.app | F (3/12) | F (3/12) — edits in workspace, publish blocked | C (7/12) |
| cloudcorprecords.github.io | F (3/12) | F (3/12) — full site staged, repo missing | B (10/12) predicted |

Both Replit blockers are the same single account action
(Replit billing). The Pages blocker is a single repository
creation. Neither requires any new tool work.
