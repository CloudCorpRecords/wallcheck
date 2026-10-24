# wallcheck — Ship-Decision Summary (ship-readiness pass, 2026-10-24)

**One page. Everything below is verified this session unless
labeled a prediction. NOTHING WAS PUBLISHED. The launch hold
stands; the ship waits for Rene's separate explicit call.**

## The candidate

- **Version: 0.5.0 final** — stamped this pass in
  `pyproject.toml`, `src/wallcheck/__init__.py`, `server.json`
  (version + GHCR tag), README and SPEC banners; `CHANGELOG.md`
  created with the 0.1.0–0.5.0 history. Historical mentions of
  the rc (wave logs, DOGFOOD) were left as history. No test
  pinned the rc string.
- **Tests: 885/885 green via pytest after the stamp**; MCP
  smoke green on all three tools (probe_url, classify, audit).
- **Index:** 500 rows — OPEN 415 · CHALLENGED 26 · WALLED 36 ·
  RATE_LIMITED 7 · UNREACHABLE 16 · LOGIN_GATED 0; 24 stability
  rounds; round 24 merged zero rows.
- **Census:** 4 of 500 domains publish a signed-agent directory
  (chatgpt.com reference-grade and actively maintained — its
  expiry renewed forward on all three spot-checks; ahrefs.com,
  indeed.com, substack.com); 71 domains wall the directory
  path itself.
- **Campaign pack:** war plan, front-doors index (66 platforms:
  40 VERIFIED / 20 NO ROUTE FOUND / 6 UNVERIFIED), five vendor
  report cards (shares recomputed Wave 26), fix kit,
  launch-readiness memo (refreshed), launch post (refreshed
  this pass, still a draft).

## Own properties (detail: validation/ship-pass/OWN-PROPERTIES.md)

| Property | Before | Now | Once unblocked |
|---|---|---|---|
| clipwise.replit.app | D (5/12) | D (5/12) — staged files applied to the Repl workspace; publish blocked | C (8/12) |
| reneturcios.replit.app | F (3/12) | F (3/12) — staged files applied to the Repl workspace; publish blocked | C (7/12) |
| cloudcorprecords.github.io | F (3/12) | F (3/12) — complete site staged in fix-kit; repository does not exist | B (10/12), predicted on the audit's own core |

Blockers, exactly: **(1)** Replit reports *"Your payment is
past due"* — publishing is account-blocked until Rene resolves
billing at replit.com; the edits are already in both workspaces,
so one publish per app then finishes it. **(2)** No
`CloudCorpRecords/cloudcorprecords.github.io` repository exists
(verified 404 via the GitHub connector); creating it is a
ship-side act outside this pass.

## What remains unproven (carried honestly)

- **Ed25519 is not constant-time** (pure-Python, correct
  against the RFC 8032 vectors; fine per-probe, not a
  high-throughput signing library).
- **Single-client measurement:** one datacenter egress IP, one
  honest UA, one fetch per URL per round — the Index is
  evidence from this client, not a universal claim.
- **Signatures are unconsulted:** the Wave 5 experiment was
  12/12 unchanged; no wall in the index trusts our key yet.
- **Adoption is 0.8%** (4 of 500) — the signed-agent story is
  the campaign's argument, not a present fact.
- **Saturation was never met in 28 waves:** every battery
  found genuine defect families (all fixed test-first), while
  the live index stayed essentially still for the last seven
  rounds. Both halves are true; the ship decision owns the
  tension.
- **Own properties still grade D/F/F live** until the two
  blockers above clear — the first thing a critic will check,
  and the fixes are ready on both sides of each blocker.

## What Rene's ship call triggers (in order)

1. **GitHub repo** — make `CloudCorpRecords/wallcheck` public
   with this tree (0.5.0 as stamped). *Needs from Rene:
   nothing but the call — Tree has connector access; if the
   repo must be created under a different owner/name, the name.*
2. **GitHub Pages property** (can ride along) — create
   `CloudCorpRecords/cloudcorprecords.github.io`, push the
   staged kit, verify the audit live. *Needs: the same call
   covers it, or a separate word.*
3. **GHCR image** — build the Dockerfile and push
   `ghcr.io/cloudcorprecords/wallcheck:0.5.0` (the Dockerfile
   already carries the MCP Registry OCI label). *Needs:
   nothing extra if the connector/PAT path used for the repo
   covers packages; otherwise a packages-permission tap.*
4. **npm** — publish the npm wrapper/package per the packages
   program convention. *Needs from Rene: npm 2FA approval tap
   if his account prompts (past npm 2FA trouble is on record —
   the resubmit path may need his authenticated session).*
5. **MCP Registry** — submit `server.json` (already stamped
   0.5.0, OCI package pointing at the GHCR tag) via the
   registry publish flow. *Needs: GitHub-authenticated publish
   — covered by the same identity as step 1.*
6. **Launch post** — post `campaign/LAUNCH-POST.md` (refreshed
   draft, numbers current) to Rene's channels. *Needs from
   Rene: which channels, and any copy edits — it is his voice;
   Tree does not post it unapproved.*
7. **Replit publishes** (independent of the ship, unblocks the
   D/F grades) — *Needs from Rene first: resolve the Replit
   billing block; then his Deploy clicks or one word to Tree.*

## Bottom line

The tool, the index, the docs, and the launch copy are ready;
the version is stamped final at 0.5.0 with 885 green tests.
What is not ready is only what was never Tree's to finish: two
account actions (Replit billing, Pages repo creation) and the
ship call itself.
