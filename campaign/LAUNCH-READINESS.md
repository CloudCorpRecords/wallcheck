# wallcheck — Launch Readiness (0.5.0, ship-readiness pass)

**Status: 0.5.0 stamped final, NOT shipped.** The launch
hold stands: nothing in this document publishes anything. This
memo states what is proven, what is not, and exactly what the ship
decision still needs from Rene — nothing else. No new approvals
are smuggled in here.

*Refreshed in Wave 28 (see
`validation/wave28/LAUNCH-READINESS-REFRESH.md` for the change
record) and again at the ship-readiness pass (see
`validation/ship-pass/SHIP-SUMMARY.md`): the version is stamped
0.5.0 final, the launch post is refreshed, and the own-property
deploys were attempted — both Replit publishes are blocked by an
account billing restriction and the Pages repository does not
exist; see the unproven list below. The Wave 9 original made the
same three-part argument against the Wave 9 state; the structure
and the ship-decision framing are unchanged.*

## What is proven (with wave citations)

- **The classifier is deterministic and heavily pinned.** 885
  tests, all green via pytest, fully offline fixtures: every
  verdict (OPEN / CHALLENGED / WALLED / LOGIN_GATED /
  RATE_LIMITED / UNREACHABLE) and every vendor (Cloudflare,
  PerimeterX, DataDome, Akamai, Imperva, AWS WAF, Microsoft Azure
  WAF, Kasada, AWS CloudFront, plus Generic / JS-proof /
  localized markers — the localized human-check list now covers
  59 language groups). Twenty adversarial batteries (Waves 6,
  10–28) and 24 rounds of live captures back the fixtures; the
  44-capture corpus regression is clean. (Waves 1–28.)
- **The Bot Wall Index is real, current, and historically
  tracked.** 500 sites, distribution OPEN 415 · CHALLENGED 26 ·
  WALLED 36 · RATE_LIMITED 7 · UNREACHABLE 16 · LOGIN_GATED 0,
  re-verified at every merge (INDEX.md's header recounts each
  round). Twenty-four stability rounds: the hard core of walls
  reproduces every round; flips are documented as churn or
  transport, never smoothed over — the index's oscillators
  (forbes.com, amazon.com, npmjs.com) carry their full split
  histories in the header notes. (Waves 1–28; INDEX.md.)
- **Signed agent identity is standards-real.** Ed25519 per RFC
  8032 in pure-Python stdlib, verified against the official RFC
  8032 §7.1 test vectors; RFC 9421 signatures with
  `tag="web-bot-auth"`; `wallcheck keygen --alg ed25519` mints a
  directory-compatible key and `directory_document()` renders a
  publishable Web Bot Auth directory. (Wave 4.)
- **The signed-agent census is measured at full scale.** 4 of
  500 domains publish a directory (chatgpt.com reference-grade,
  ahrefs.com keyed dual-key, indeed.com and substack.com bare
  JWKS); 71 domains wall the directory path itself. The
  spot-check record (Waves 16, 20, 23) found all four still
  publishing with keys byte-identical every time; chatgpt.com's
  document is actively operated — its expiry drifted forward on
  all three spot-checks (+11,956 s by Wave 16, again by Wave 20,
  +12,555 s by Wave 23) — while ahrefs.com has never gained
  purpose/window metadata. The campaign therefore knows both the
  adoption floor and the wall in front of it. (Wave 7 census v2;
  Waves 16, 20, 23 spot-checks.)
- **Vendor attribution is measured, not asserted.** Shares
  recomputed from the standing table in Wave 26
  (`validation/wave26/VENDOR-SHARES.md`): of 37 WALLED rows,
  Akamai 22, Cloudflare 5, unattributed (bare 403) 4, AWS
  CloudFront 3, unattributed (402 pair) 2, Imperva 1; of 26
  CHALLENGED rows, DataDome 15, Cloudflare 5, PerimeterX 3,
  AWS WAF 1, Microsoft Azure WAF 1, Generic 1. (Round 23 has
  since moved one CHALLENGED row — forbes.com — to OPEN.) The
  five vendor report cards were corrected against these shares
  in Wave 26; their grades were not touched.
- **The owner side works.** `wallcheck audit` grades six checks
  with evidence and fixes; the fix kit's vendor steps are
  citation-checked against current vendor docs; the audit caught
  real problems on our own properties first. The `audit` MCP
  tool ships in 0.5.0 with a stated, tested fetch budget
  (≤10 GETs). (Waves 3, 5, 8, 9.)
- **The campaign pack is complete.** War plan, front-doors index
  (66 platforms: 40 VERIFIED / 20 NO ROUTE FOUND / 6 UNVERIFIED,
  Wave 27 count), five vendor report cards, fix kit, launch post
  draft. Every vendor claim in the report cards is tagged
  [MEASURED] / [VENDOR] / [SOURCE] / [POSITION].
- **MCP surface is verified live.** Smoke driver: initialize +
  tools/list (3 tools) + classify + probe_url + audit calls, all
  green against the stdio server over real pipes, re-run in
  Wave 28 (`scripts/smoke_mcp.py`; validation/wave27/mcp_smoke.py
  driver).

## What is NOT proven — read before shipping

- **Own-properties grades are still failing live — but the
  deploys were attempted, and the blockers are now exact.**
  clipwise.replit.app D (5/12), reneturcios.replit.app F (3/12),
  cloudcorprecords.github.io F (3/12) — Wave 8 re-audit,
  unchanged through Wave 28 and re-measured at the
  ship-readiness pass. At the pass, the staged files were
  applied to both Replit workspaces via the Replit connector,
  but publishing is blocked account-wide by a billing
  restriction ("Your payment is past due"); expected on publish:
  Clipwise C (8/12), portfolio C (7/12). The Pages property
  turns out to have no repository at all (verified 404 via the
  GitHub connector); a complete site is now staged in
  `fix-kit/cloudcorprecords.github.io/` and scores a predicted
  B (10/12) on the audit's own core, key directory published
  with the private key custodied outside the kit. Full record:
  `validation/ship-pass/OWN-PROPERTIES.md`. Shipping a
  transparency tool while our own house grades D/F is honest —
  the audit found it first — but it is also the first thing a
  critic will check, and the remaining blockers are Rene's
  account actions, not the tool's.
- **Ed25519 is not constant-time.** The pure-Python implementation
  is correct against the RFC vectors but is documented in its own
  module as not constant-time, at tens of ms per signature. Fine
  for one signed request per probe; not a library for
  high-throughput signing, and the docs must not imply otherwise.
- **All measurements are single-client observations.** One
  datacenter egress IP, one honest non-browser user agent, one
  fetch per URL per round. Walls are context-sensitive by design:
  a residential IP or a full browser may score differently, and
  every wave report says so. The Index is evidence from this
  client, not a universal claim about a site.
- **Signed requests are unconsulted by walls today.** The Wave 5
  experiment (12/12 verdicts unchanged) and Wave 2's own-property
  probes show that an unregistered signature changes nothing —
  because no wall in the index trusts our key. The passport is
  proven machinery, not proven acceptance. The campaign's identity
  front has to move adoption (4 of 500) before any site honors a
  wallcheck signature in practice.
- **Adoption is 4 of 500 (0.8%).** The "signed agents get through"
  story is a future the campaign is arguing for, not a present
  any reader can verify on most sites.
- **The classifier has never saturated.** Across Waves 10–28,
  every adversarial battery found at least one genuine defect
  family — 3 to 21 per wave, all fixed test-first — and the
  two-consecutive-clean-waves pair the campaign set for itself
  has never completed. The honest reading cuts both ways: the
  batteries keep finding real edge cases (ARIA-spelled modals,
  Windows PIN prompts, four more languages in Wave 28 alone),
  and the live index has been essentially still for seven rounds
  (rounds 18–24 merged 0, 2, 2, 3, 2, 1, 0 rows, with exactly two
  fix-driven moves in that span, both the Wave 24 402 rule in
  round 21). The tool is measurably stable on real traffic and
  measurably unfinished on adversarial ground. Both halves belong
  in the ship decision.
- **The launch post is refreshed.** `campaign/LAUNCH-POST.md`
  was updated at the ship-readiness pass from Wave 1 numbers to
  the current verified state (500 sites, 415 open, 62 walled or
  challenged, 885 tests, census 4/500, FRONT-DOORS 66), with one
  framing correction: the "freelance is the worst category"
  superlative no longer holds against the current table (travel
  is harder) and was re-framed honestly. Before/after record:
  `validation/ship-pass/LAUNCH-POST-REFRESH.md`. It remains a
  draft in Rene's voice; nothing was posted.

## What the ship decision still needs from Rene — and only this

1. **The ship call itself.** Publish the repo (GitHub),
   npm/GHCR/MCP Registry listings, the Index page, and the launch
   post — or any subset — only on Rene's explicit word, per the
   standing launch hold. The ship-readiness pass prepared the
   0.5.0 candidate; it did not ship it.
2. **The launch-post refresh — DONE at the ship-readiness
   pass.** The post now carries the 500-site numbers and the
   current state (record:
   `validation/ship-pass/LAUNCH-POST-REFRESH.md`). It is ready
   to post with the ship, pending Rene's channel choice and any
   copy edits. (He may also choose to hold the post until the
   own-property publishes land — see below.)
3. **The own-property account actions.** The staged fixes are
   already applied inside both Repls; what remains is Rene's:
   resolve the Replit billing block so the two publishes can run
   (Clipwise to C (8/12), the portfolio to C (7/12)), and —
   ship-side — create the `cloudcorprecords.github.io`
   repository so the staged Pages site (predicted B) can go
   live. Not blockers the tool imposes — credibility choices
   only Rene can make.

Nothing else is needed: no new tool, no new wave, no new approval
is hidden in this memo. If Rene says ship, the candidate is
**0.5.0** as stamped at the ship-readiness pass in
`pyproject.toml`, `src/wallcheck/__init__.py`, `server.json`
(GHCR tag `0.5.0`), the README/SPEC banners, and `CHANGELOG.md`
— carrying the unreleased Waves 10–28 fixes, folded into the
final stamp per the Wave 12 version note (0.5.0-rc was never
released, so no 0.5.1 exists). The ordered publish steps and
what each needs from him are in
`validation/ship-pass/SHIP-SUMMARY.md`.

## Saturation status (final, Wave 28)

**Not met — after 28 waves.** The overnight test requires two
consecutive waves with zero classifier defects, zero new
vendors/signals, and zero new coverage. Wave 9 was borderline
(clean defect sheet, but it grew the product surface); every
wave since has found genuine defects — Wave 28's battery v20
found three families (Windows PIN prompts, four localized
phrase sets, ARIA modal challenges) even as its stability round
merged zero rows for the third time in seven rounds. The clock
therefore stands reset at the end of Rene's five-wave
authorization (Waves 24–28, ordered 2026-10-24 08:07 PT): the
pair never completed, and no honest reading of the ledger says
otherwise. What the 28 waves did prove is narrower and stronger
than saturation: the verdict table over 500 real sites is
reproducible round after round, every known defect class is
pinned by a fixture, and the remaining finds are new species in
known families, not instability in the core. Whether that is
"working well" enough to ship is — as it has been since Wave 9 —
Rene's call, and only Rene's.
