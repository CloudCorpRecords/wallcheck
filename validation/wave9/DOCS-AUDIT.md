# Wave 9 — Docs consistency audit (Leg A) + MCP surface decision (Leg B)

Wave 9 read SPEC.md, README.md, DOGFOOD.md, INDEX.md, every
campaign/*.md, and the validation/wave*/ report headers, and
checked every version number, test count, index count, verdict
distribution, vendor list, directory adopter count, and
own-properties grade against measured reality. Corrections below
are surgical: each names the file, the before, and the after.
Items marked VERIFIED were checked and needed no change; they are
listed so a later wave does not re-report them as problems.

## Corrections made

### C-01 — INDEX.md: Wave 5 defect count (six → five)
- Before: "six classifier defects found in the new territory were
  fixed test-first" (INDEX.md header, Wave 5 expansion paragraph).
- After: "five classifier defects found in the new territory were
  fixed test-first".
- Evidence: `validation/wave5/PROBLEMS.md` ledger header reads
  "Leg B (expansion 2) — 5 defects, all fixed" and lists exactly
  W5-001…W5-005. The "six" likely counted the separate Leg D
  audit-tool defect (in our own house, not the classifier) as a
  sixth classifier defect; it is not one.

### C-02 — README.md: Wave 5 fix count (six → five)
- Before: "All six Wave 5 fixes are test-first from live captures".
- After: "All five Wave 5 defects are fixed test-first from live
  captures".
- Evidence: same ledger as C-01. (W5-005 spans two facets — the
  Akamai reference-token deny page and the 444 verdict rule —
  which is where a "six fixes" count could come from; the defect
  count is five either way, and the ledger is the authority.)

### C-03 — README.md: index size (258 → 499)
- Before: "The index now covers 258 sites" (New in v0.5 section).
- After: "The index now covers 499 sites (Waves 6–7 expansion)".
- Evidence: INDEX.md header + independent row count (499 data
  rows; see C-08).

### C-04 — README.md: v0.3 section index size (154 → 499)
- Before: "merges the census into the Bot Wall Index working table
  (154 sites)".
- After: "(499 sites after the Waves 6–7 expansion)".
- Note: the sentence describes Wave 3's merge, so 154 was true
  for Wave 3; the parenthetical now states the table's current
  size instead of freezing it at the Wave 3 value.

### C-05 — README.md: vendor list incomplete
- Before: intro names "(Cloudflare, PerimeterX, DataDome, Akamai,
  Imperva, AWS WAF)".
- After: adds "Microsoft Azure WAF, Kasada, AWS CloudFront".
- Evidence: SPEC.md vendor section (W5-002…W5-004) and server.json
  description, which already listed all nine.

### C-06 — SPEC.md: Bot Wall Index status (258 → 499)
- Before: "258 sites merging the Wave 1 census, the Wave 3/5
  expansions, and stability rounds 2–4 (150+ verdicts re-measured…".
- After: "499 sites merging the Wave 1 census, the Wave 3/5/6/7
  expansions, and stability rounds 2–5 (round 5 re-probed all 499
  with 496 identical…). Directory census v2 (Wave 7): 4 of 499
  domains publish signed-agent directories."
- Evidence: INDEX.md header; `validation/wave7/DIRECTORY-2.md`.

### C-07 — campaign/REPORT-CARD-AKAMAI.md: stale index claim
- Before: "Akamai holds two of the six WALLED verdicts in our
  154-row index" (presented as current).
- After: qualified as the Wave 4-era statement, plus the current
  count: "Akamai holds 21 of the 34 WALLED rows" in the 499-row
  index.
- Evidence: INDEX.md recount (WALLED by vendor: Akamai 21,
  Cloudflare 5, CloudFront 3, Imperva 1, unattributed 4).

### C-08 — Version stamp split (0.5.0 vs 0.5.0-dev → 0.5.0-rc)
- Before: `src/wallcheck/__init__.py`, `pyproject.toml`, and
  `server.json` recorded 0.5.0 while `validation/OVERNIGHT.md`
  called the line v0.5.0-dev.
- After: all three files plus the server.json GHCR tag record
  0.5.0-rc; README.md and SPEC.md carry a 0.5.0-rc banner line.
- Note: the Dockerfile carries no version tag (the GHCR tag lives
  in server.json); its image description vendor list was updated
  to the full nine vendors for consistency, not as a version bump.

### C-09 — DOGFOOD.md: missing Waves 4–8
- Before: the dogfood log's addenda stopped at Wave 3 (59 tests)
  while five waves had run since.
- After: a Waves 4–8 addendum appended in chronological order
  (after the Wave 3 addendum), each wave's headline numbers cited
  to its own report. No new live runs are claimed in the addendum;
  it is a summary of the wave reports, and says so.

### C-10 — SPEC.md: MCP surface (two tools → three)
- Before: "MCP smoke: initialize + tools/list + both tools called";
  v0.3 section: "CLI-only (the MCP tool list stays exactly
  `probe_url`/`classify`)".
- After: smoke calls "all three tools"; v0.3 section reads
  "CLI-only until Wave 9, which added the `audit` MCP tool".
- Evidence: Leg B implementation (below); `scripts/smoke_mcp.py`
  now asserts three tools and calls all three live.

### C-11 — README.md: MCP tools list (two → three)
- Before: tools list showed `probe_url` and `classify` only.
- After: adds `audit(domain, timeout?)` with its fetch budget
  stated (up to 10 honest GETs).

### C-12 — campaign/FRONT-DOORS.md: edition label
- Before: header "Seed edition, 2026-10-24".
- After: "Seed edition, extended Wave 8, 2026-10-24".
- Evidence: the file's own Wave 8 scoreboard (65 platforms: 39
  VERIFIED, 20 NO ROUTE FOUND, 6 UNVERIFIED); the label was the
  only stale part.

### C-13 — README.md: wave summary (Wave 4 → Waves 5–8)
- Before: the closing wave summary ended at Wave 4.
- After: one sentence covering Waves 5–8 (territory growth,
  signed-vs-unsigned experiment, fix kit; 25 adversarial shapes;
  index to 499, census v2, audit sweep; 46-platform path matrix,
  front-doors to 65 platforms).
- Note: README.md's Wave 3/4 sentences are historical statements
  about those waves and were left as written.

### C-14 — INDEX.md header: Wave 8 note added
- Before: the "Rounds merged" narrative ended at Wave 7 round 5.
- After: a sentence noting Wave 8 path-probed 46 platforms (322
  paths) without changing root rows, pointing at
  `validation/wave8/PATHS-2.md`. No row values changed.

## VERIFIED — checked, no correction needed

- **V-01 — INDEX.md header counts.** Independent recount: 499
  data rows; OPEN 416 · CHALLENGED 25 · WALLED 34 · RATE_LIMITED 7
  · UNREACHABLE 17 — exactly the header. (An earlier strict regex
  missed the npmjs.com row because its site cell carries a
  "— see note †" suffix; the row is real and counted. The Wave 7
  header-count bug stays fixed.)
- **V-02 — Directory adopter counts.** Wave 4: 3/154
  (chatgpt.com, indeed.com, substack.com). Wave 7 census v2: 4/499
  (ahrefs.com added). `campaign/FIX-KIT.md`'s "4 adopters in 499"
  matches. No doc still claims 3/154 as current.
- **V-03 — Own-properties grades.** Wave 8 re-audit unchanged:
  clipwise.replit.app D (5/12), reneturcios.replit.app F (3/12),
  cloudcorprecords.github.io F (3/12) — consistent across
  `campaign/FIX-KIT.md` §7, `fix-kit/README.md`, and OVERNIGHT.md.
  The staged three-file deploy buys C (7/12), not B, everywhere
  it is now stated; the Wave 5 "at least B" line survives only
  inside a quoted correction note.
- **V-04 — Wave 6 shape count.** `validation/wave6/ADVERSARIAL.md`
  says "24 synthetic edge shapes" while OVERNIGHT.md says "25
  hand-classified edge shapes pinned" and `tests/test_adversarial.py`
  has 25 tests. Reconciled, not a correction: 24 synthetic shapes
  plus the Amazon interstitial shape derived from a real capture
  (HANDCLASS.md S2c) = 25 fixtures. The 4-defect count (W6-001…
  W6-004) plus the expansion's W6-005 = 5 Wave 6 defects total,
  consistent with OVERNIGHT.md.
- **V-05 — Wave 7 fixtures.** "2 new W7 fixtures" (OVERNIGHT.md,
  110 → 112 tests) covers the careerjet corrected-classification
  pin and the round-5 recovery pins; the zero-defect claim stands
  (W7-001 was CORRECTED, not a defect).
- **V-06 — Test-count chain.** 17 (v0.1) → 24 → 46 → 59 → 75 →
  85 → 110 → 112 → 114 → 120 (Wave 9). Each step matches its
  wave report; no doc claims a count the suite does not have.
- **V-07 — FRONT-DOORS scoreboard.** 65 platforms, 39 VERIFIED /
  20 NO ROUTE / 6 UNVERIFIED — matches the Wave 8 scoreboard and
  the file's own section counts.
- **V-08 — Vendor list in server.json.** Already complete (all
  nine vendors); only the version and GHCR tag needed the rc bump.

## NOT corrected — intentionally left, with reason

- **N-01 — campaign/LAUNCH-POST.md cites Wave 1 numbers** ("58
  sites", "47 open"). It is launch copy in Rene's voice, written
  at Wave 1 time — not a measurement document. Rewriting his voice
  copy before ship would be worse than leaving it: it must be
  refreshed with the 499-site numbers at ship time, and
  `campaign/LAUNCH-READINESS.md` lists that refresh as a
  ship-checklist item.
- **N-02 — Historical wave sentences.** README.md's "New in v0.2 /
  v0.3 / v0.4" sections and SPEC.md's version sections describe
  what those versions shipped; they were left as history except
  where a number had become the doc's current claim (C-03…C-06).

## Leg B — MCP surface decision: YES, add the `audit` tool

**Decision: the `audit` MCP tool ships in 0.5.0-rc.** The
alternative (leave audit CLI-only, document why) was rejected on
evidence:

1. **Surface consistency.** server.json already advertises the
   audit ("Ships a Web Bot Auth signer and an owner-side
   agent-access audit"), yet the MCP server did not expose it —
   the flagship owner-facing tool was reachable only by shelling
   out. A release candidate should not advertise a tool its own
   server lacks.
2. **Security / fetch budget — bounded and stated.** `audit_site`
   makes at most 10 sequential GETs to the one domain (homepage,
   robots, llms, sitemap, declared sitemap only when the default
   404s, two OpenAPI paths, /api + /developers only when no spec
   is found, the signed-agent directory path). Each fetch reuses
   the probe's discipline: honest wallcheck user agent, per-fetch
   timeout (default 15 s), bounded body sample (BODY_CAP), no
   retries, no state change (GET only). The budget is stated in
   the tool description itself so MCP clients can rate-limit; a
   counting-fetch test pins it (`test_audit_site_fetch_budget`:
   9 fetches on an all-404 site, hard cap 10). Loop-abuse risk
   exists for `probe_url` too and is of the same kind; audit's is
   ~10x per call, which is why the budget is disclosed rather
   than hidden.
3. **Client usefulness.** MCP clients are agent builders and site
   owners — exactly the audience for a graded agent-access audit
   with fixes. Keeping it CLI-only forced every MCP consumer to
   shell out for the campaign's owner-facing workflow.

**Implementation (stdlib only, no new dependencies):**
`src/wallcheck/server.py` gains the `audit` tool (schema requires
`domain`, optional `timeout`) dispatching to `audit_site`;
`tests/test_server.py` (new, 5 tests) pins tools/list = 3 tools,
the schema, classify dispatch, audit dispatch via a stub, and
unknown-tool errors; `tests/test_audit.py` gains the fetch-budget
test; `scripts/smoke_mcp.py` now asserts three tools and makes a
live audit call (example.com → grade F 3/12, six checks present).
SPEC.md's MCP section, v0.3 section, and success criteria, plus
README.md's MCP tools list, were updated to match.

**What was NOT changed:** the probe's single-fetch discipline, the
classifier, the audit's checks or scoring, and the CLI. The MCP
server still serves no state-changing operation.
