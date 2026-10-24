# wallcheck — Overnight Operations (Fri Oct 23 → Sat Oct 24, 07:00 PT)

Rene's order (2026-10-23 22:22 PT): keep working until 07:00 PT chasing
perfection and edge cases. If the tool genuinely saturates — no more honest
improvements to make — stopping early is fine. LAUNCH HOLD stays absolute:
nothing is published anywhere; ship only on Rene's explicit call.

## Hard lines (permanent)

- Never: CAPTCHA solving, fingerprint/UA spoofing, challenge automation,
  bypass/evasion. Probing = single honest fetches, identified wallcheck UA,
  back off entirely on 429.
- Honest ledger discipline: test-first defect fixes with capture-built
  fixtures, generalized rules only (no per-site special cases), churn is
  not a defect, transport noise is not a posture change.
- VM exec write-guard truncates files: state/results writes via file
  tools; verify every JSON parses and no file is 0-byte before claiming
  a leg done.

## Coordination

Waves run either as main-chat subagents or as runs of the
`wallcheck-overnight` cron. This file is the shared state. Before starting
a wave: read this file + the latest wave report. Mark the wave
IN_PROGRESS with a timestamp; on completion mark DONE with the headline
numbers. If a wave is IN_PROGRESS and its outputs are still growing
(mtime < 90 min), do not duplicate it — verify or wait.

## Wave log

- Ship-readiness pass (DONE 2026-10-24, Rene's order 10:22 PT after the five-wave run ended without saturation): PREPARED everything, PUBLISHED NOTHING — launch hold intact. (1) STAMP: version 0.5.0-rc → 0.5.0 final in pyproject.toml, src/wallcheck/__init__.py, server.json (version + GHCR tag), README banner/history, SPEC banner/status; historical rc mentions in wave logs/DOGFOOD kept as history; no test pinned the rc string; CHANGELOG.md created (0.5.0 entry + grounded 0.1.0–0.4.0 history). Suite after stamp: 885/885 via pytest; MCP smoke green on all three tools. (2) OWN-PROPERTY DEPLOYS — attempted, all three BLOCKED honestly (record: validation/ship-pass/OWN-PROPERTIES.md): baselines re-measured live first (Clipwise D 5/12, reneturcios F 3/12, Pages F 3/12, matching Wave 8); the staged three-file kits were APPLIED to both Replit workspaces via the Replit connector (reneturcios app 2f89ad40, clipwise app b6ceb444), but publish_app on both returned "Your payment is past due" — account-level Replit billing block; expected on publish: reneturcios C (7/12), Clipwise C (8/12), live grades unchanged. Pages: repository CloudCorpRecords/cloudcorprecords.github.io verified NONEXISTENT via the GitHub connector (404; no *.github.io repo anywhere); complete minimal site built and staged in fix-kit/cloudcorprecords.github.io/ (index/feed/robots/llms/sitemap/.nojekyll + a real signed-agent directory rendered by wallcheck's own directory_document() from a fresh Ed25519 key — kid cloudcorprecords.github.io-2026-10, fingerprint 5da40e32b87f4fd7; private key custodied ONLY at validation/ship-pass/cloudcorprecords-directory-key.json, never in the kit); predicted grade B (10/12) computed with the audit's own evaluate_audit on the kit (labeled prediction); build catch recorded: the homepage's first draft self-classified CHALLENGED (its own "no CAPTCHA solving" clause under the 16 KB served-page gate) — clause reworded, homepage now OPEN. Unblocks: Rene resolves Replit billing (then one publish per app), create the Pages repo and push the kit. (3) LAUNCH POST refreshed (record: validation/ship-pass/LAUNCH-POST-REFRESH.md): 58 → 500 sites, 47 → 415 open, 8 → 62 walled/challenged, 885 tests added, Akamai 22-of-37 added, census 4/500 + chatgpt drift note added, FRONT-DOORS 66 (40/20/6) added; freelance superlative CORRECTED — verified against the current table: 4 of 13 freelance platforms wall/challenge (upwork/guru/gun.io WALLED, fiverr CHALLENGED; contra OPEN), but travel is harder (9 of 19), so the post now frames freelance as "the category that hit me" with travel credited; post remains a DRAFT, posted nowhere. (4) SHIP SUMMARY written (validation/ship-pass/SHIP-SUMMARY.md): candidate 0.5.0, 885 tests, index/census state, own-property before/after + blockers, unproven list carried (Ed25519 not constant-time, single-client measurement, signatures unconsulted 12/12, adoption 0.8%, saturation never met in 28 waves, own properties still D/F/F live), and the ordered publish steps Rene's ship call triggers (GitHub repo → Pages repo → GHCR → npm (2FA tap risk noted) → MCP Registry → launch post (his channel/copy call) → Replit publishes after billing). LAUNCH-READINESS.md state lines updated to match. NO Wave 29; the ship waits for Rene's separate explicit call.
- Wave 28 (DONE 2026-10-24 ~11:05 PT): SATURATION VERDICT — NOT MET, clock RESET again (3 battery defect families); the five-wave authorization (24–28) ends here — no Wave 29 spawned. Leg A round-24: 500/500 probed with the Wave 27-fixed classifier (runner detached + resumable, no incident; imported the Wave 27 tree at launch, so the Wave 28 fixes are unmeasured until a future round; all four W27 fixes grep-verified present pre-probe; completion verified from the runner's own completion line + on-disk counts, the Wave 27 lesson; history round=24 exactly 500 lines, no dupes); ZERO verdict diffs across the 498 regex-visible rows and ZERO merges: the one diff was the analyzer-invisible pair's npmjs.com (round connection drop vs standing CHALLENGED / Cloudflare), held CHALLENGED on a 1–1 fresh split (one fresh Cloudflare challenge against one fresh fetch failure — no corroboration triple, the 11th transport-pattern sighting); amazon.com read CHALLENGED / Generic, agreeing; four vendor-cell diffs were the standing "unattributed (bare 403)" annotation wording only; ZERO fix-driven moves (the Wave 27 biometric/robots-token/llms-comment/SQ-IS-KK-ML fixes measured zero live effect; the two audit-side fixes are untestable by this leg). Leg B battery v20: 54 shapes, 12 first-run failures = exactly the predicted gaps in 3 families, ALL fixed generalized (W28-W3: Windows PIN / Windows Hello sign-in prompts — new _is_windows_pin_prompt, Windows demand in visible text + button/form machinery keys from birth behind the served-page size gate, asset-filename/script-string/stylesheet-class negative carriers pinned, prose-without-machinery boundary ledgered; W28-W7: Burmese, Sinhala, Amharic, Azerbaijani phrases added — all eight strings grep-verified absent from the full list, every HANDCLASS file, and tests/ before writing, AZ demand verb kept distinct from the Turkish near-twin; W28-W8: ARIA modal challenges — _MODAL_ROLE_TAG_RE makes role="alertdialog" / aria-modal="true" a modal container key with the J8 window machinery, deliberately NOT size-gated like every overlay member, role="alert" and modeless role="dialog" pinned as the non-modal boundary) + 42 pins held (all of W1 <output> — the presented-element survey closes; W2 451 + blocked-by Link compositions — the header documents a refusal, it is not a redirect species; W4 robots separator discipline in both directions; W5 TOC-only llms incl. two PASSes pinned BY DOCTRINE under W13-E6a/D7b; W6 cross-TLD locs under the R6/V6 doctrine) — every mismatch checked against older pins before fixing, no pin moved; corpus clean (44 captures, diff empty); 885 tests final via pytest. Leg C: campaign/LAUNCH-READINESS.md refreshed from Wave 9 state (885 tests, 500-row index with current distribution, census 4/500 with the three-spot-check drift record, FRONT-DOORS 66 platforms, Wave 26 vendor shares, unproven list carried forward re-verified + the never-saturated item added, saturation section rewritten to the final NOT MET verdict) with the change record in validation/wave28/LAUNCH-READINESS-REFRESH.md; LAUNCH-POST untouched. SPEC updated (status "hardened through Wave 28", localized list + Wave 28 refinements, index status to rounds 2–24); INDEX header gains the round-24 parenthetical, distribution unchanged. MCP smoke green on all three tools (probe_url example.com OPEN; classify → CHALLENGED / Cloudflare; audit example.com F, 6 checks). Index at 500 rows: OPEN 415 / CHALLENGED 26 / WALLED 36 / RATE_LIMITED 7 / UNREACHABLE 16 / LOGIN_GATED 0 (unchanged; no row line edited). SATURATION: NOT MET — battery v20 found 3 genuine defect families (W28-W3 Windows PIN prompts, W28-W7 MY/SI/AM/AZ phrases, W28-W8 ARIA modal challenges), so Wave 28 is not a clean wave; it was clean-wave candidate #1 and the pair would still need one further clean measurement wave — but the five-wave authorization ends here either way, and the main chat reports the five-wave outcome to Rene.
- Wave 27 (DONE 2026-10-24 ~10:05 PT): SATURATION VERDICT — NOT MET, clock RESET again (4 battery defect families). Leg A round-23: 500/500 probed with the Wave 26-fixed classifier (runner imported the tree at launch, before any Wave 27 battery edit landed, so the round measures the Wave 26 tree end to end and the Wave 27 rules are unmeasured until round 24; all three W26 fixes grep-verified present pre-probe; history round=23 exactly 500 lines, no dupes); 4 verdict diffs, 0 vendor-only diffs, 1 merged, 3 held, ZERO fix-driven moves: forbes.com to OPEN (round + 2 agreeing served readings, both fresh captures carrying the DataDome header while the page served — the documented oscillator finally meets the served triple its rounds 11–22 splits never met, reversing its Wave 19 challenge merge); chicagotribune.com held OPEN (two agreeing fresh served readings against a round 403 — the Wave 18 transient-refusal hold repeated), hilton.com held WALLED / Akamai (two agreeing fresh 403s against a round fetch failure, transport noise), webex.com held OPEN on a 1–1 fresh split (one edgesuite deny against one served reading, no corroboration triple); npmjs.com read CHALLENGED / Cloudflare and amazon.com CHALLENGED / Generic, both agreeing with standing; every fresh capture recorded zero Wave 26-rule AND zero Wave 27-rule involvement — the Wave 26 fixes measured ZERO live effect (the percent-encoded sitemap fix is audit-side and untestable by this leg). One process incident, ledgered in STABILITY-22: a backgrounded watcher's result was rendered mid-round claiming completion at ~250 rows; disk verification disproved it instantly and all analysis waited for the runner's own completion line — files over renderings. Leg B battery v19: 43 shapes, 15 first-run failures = exactly the predicted gaps in 4 families, ALL fixed generalized (W27-V3: biometric sign-in prompts — new _is_biometric_prompt, fingerprint/face/biometric phrase in visible text + button/form machinery keys from birth behind the served-page size gate, asset-filename/script-identifier/stylesheet-class negative carriers pinned, prose-without-machinery boundary ledgered; W27-V4: robots versioned product tokens — parse_robots stores the RFC 9309 identifier before the first "/", so wallcheck/1.0 names the wallcheck group; verified no earlier test puts "/" in a UA value; W27-V5: llms.txt HTML comments stripped before content analysis — the classifier's Wave 19 doctrine adopted by the audit side; V5a's evidence lands on EMPTY_BODY rather than the hand-class's LLMS_STUB, same WARN grade, discrepancy recorded not smoothed; W27-V7: SQ/IS/KK/ML phrases added — Albanian, Icelandic, Kazakh, Malayalam, all grep-verified absent before writing) + 28 pins held (all of V1 table-cells, V2 307→maintenance — scope narrowed at hand-class time because Wave 16's H4 already pinned the 307→login/challenge compositions, V6 IP-literal sitemap locs, V8 toast notifications, and every negative-carrier guard) + corpus clean (44 captures, diff empty); 831 tests final via pytest. Leg C: DOGFOOD.md Waves 19–26 addendum appended and verified (file now 670 lines, 23 wave entries, staging copy removed); DOCS-SPOT-5 records README chain extended through 831 and rounds 6–23, SPEC status "hardened through Wave 27" with the language list, refinements chain, robots product-token bullet, and llms comment bullet all updated; FRONT-DOORS verified at 66 platforms (40 VERIFIED / 20 NO ROUTE / 6 UNVERIFIED); LAUNCH-POST untouched. MCP smoke green on all three tools (probe_url example.com OPEN; classify → CHALLENGED / Cloudflare; audit example.com F, 6 checks). Index at 500 rows: OPEN 415 / CHALLENGED 26 / WALLED 36 / RATE_LIMITED 7 / UNREACHABLE 16 / LOGIN_GATED 0 (recount verified, annotated pair hand-counted). SATURATION: NOT MET — battery v19 found 4 genuine defect families (W27-V3 biometric prompts, W27-V4 robots versioned tokens, W27-V5 llms comment-only links, W27-V7 SQ/IS/KK/ML phrases), so Wave 27 is not a clean wave and the two-consecutive-clean-waves clock resets again; Wave 28 becomes clean-wave candidate #1, and one further clean measurement wave after it would still be needed for the pair. No Wave 28 spawned per this wave's brief (main chat chains Waves 24–28).
- Wave 26 (DONE 2026-10-24 ~09:35 PT): SATURATION VERDICT — NOT MET, clock RESET again (3 battery defect families). Leg A round-22: 500/500 probed with the Wave 25-fixed classifier (imported at launch, before any Wave 26 battery edit landed, so the round measures the Wave 25 tree end to end and the Wave 26 rules are unmeasured until round 23; single detached run, no incident); 3 verdict diffs, 2 merged, 1 held, ZERO fix-driven moves: apnews.com to CHALLENGED / Cloudflare (round + 2 agreeing 403 readings — recovered from its round-20 failure merge, delivery failures not posture), webex.com to OPEN (round + 2 agreeing served readings — the Akamai wall standing since round 9 has lifted, closing the split round 19 held), forbes.com held CHALLENGED / DataDome (two agreeing fresh DataDome 403s against a round served reading; the documented oscillator oscillating, fresh evidence agrees with standing); npmjs.com read CHALLENGED / Cloudflare and amazon.com CHALLENGED / Generic, both agreeing with standing; every fresh capture recorded zero Wave 25-rule involvement — the Wave 25 fixes measured ZERO live effect. Leg B battery v18: 41 shapes, 7 first-run failures = exactly the predicted gaps in 3 families, ALL fixed generalized (W26-U3: badge-tap sign-in prompts — new _is_badge_tap_prompt, badge-tap phrase in rendered visible text + button/form machinery keys from birth, asset-filename/stylesheet-class/script-string negative carriers pinned, prose-without-machinery guard held; W26-U6: percent-encoded sitemap hosts — _has_nonempty_loc now skips locs whose authority host carries "%", the WHATWG host rule, path encoding untouched, checked against K6/L6/N6/Q6 pins before fixing; W26-U7: CA/ET/HY/KA phrases added, Catalan "no soc" kept distinct from Spanish "no soy", Estonian kept distinct from Finnish) + 34 pins held (label-element and button text are presented — fire on non-served, gate on served, completing the presented-element survey; 451 + Retry-After stays WALLED, the throttle rule's 403/503 scope holds; robots UA/Disallow trailing whitespace binds exactly as trimmed; mixed LF/CRLF llms behaves like either uniform twin) + corpus clean (44 captures, diff empty); 788 tests final via pytest. Leg C vendor-share refresh (recomputed from the table, each share verified against the rows; npmjs/amazon hand-counted as the analyzer-invisible pair): WALLED 37 = Akamai 22 / Cloudflare 5 / unattributed (bare 403) 4 / AWS CloudFront 3 / unattributed (402 pair) 2 / Imperva 1; CHALLENGED 26 = DataDome 15 / Cloudflare 5 / PerimeterX 3 / AWS WAF 1 / Azure WAF 1 / Generic 1. THREE report-card corrections (before/after in validation/wave26/VENDOR-SHARES.md): Akamai card "499 rows, 22 of 35" → "500 rows, Wave 26, 22 of 37"; DataDome card "five properties" → fifteen (scorecard + body, the five named now presented as the majors); PerimeterX card "the one PerimeterX property" → three properties (fiverr + wayfair + goodrx). Imperva card verified current (guru.com still the only Imperva row); Cloudflare card cites no index share. Grades untouched; LAUNCH-POST untouched. SPEC status line now reads "hardened through Wave 26", localized list extended through Wave 26, Wave 24–26 refinements paragraph added; README suite line corrected to 788 (batteries v2–v18, rounds 6–22). MCP smoke green on all three tools (probe_url example.com OPEN; classify → CHALLENGED / Cloudflare; audit example.com F, 6 checks). Index at 500 rows: OPEN 414 / CHALLENGED 27 / WALLED 36 / RATE_LIMITED 7 / UNREACHABLE 16 / LOGIN_GATED 0 (recount verified). SATURATION: NOT MET — Wave 26 found 3 genuine defect families, so the two-consecutive-clean-waves clock resets again; Wave 27 becomes clean-wave candidate #1 if defect-free. No Wave 27 spawned per this wave's brief (main chat chains Waves 24–28).
- Wave 25 (DONE 2026-10-24 ~08:55 PT): SATURATION VERDICT — NOT MET, clock RESET again (3 battery defect families). Leg A round-21: 500/500 probed with the Wave 24-fixed classifier (runner detached + resumable, no incident; imported the Wave 24 tree at launch, so the Wave 25 fixes are unmeasured until round 22); 4 verdict diffs, 3 merged, 1 held: telegraph.co.uk and usatoday.com to WALLED (round + 2 agreeing 402 readings, STATUS_402 on every capture — the round's TWO fix-driven moves under W24-R2, the first fix-driven moves since round 14's single move; both rows are the 402 watch pair flagged forward in Wave 24's STABILITY-19, postures unchanged, only the reading is new), todoist.com to OPEN (round + 2 agreeing served readings — recovered from its round-19 failure merge), britishairways.com held OPEN (two agreeing fresh served readings overturn the round transport failure, the Wave 14 hold pattern); the W24 push-approval and BG/SK/HR/SL fixes measured ZERO live effect (no capture carried either shape); npmjs read CHALLENGED / Cloudflare directly (no drop), amazon CHALLENGED / Generic, both agreeing; vendor-only diffs zero. Leg B battery v17: 37 shapes, 9 first-run failures = the predicted gaps in 3 families, ALL fixed generalized (W25-T3: employee-ID sign-in prompts — new _is_employee_id_prompt, visible-text wording + password-input/form machinery keys from birth, asset-filename/script-identifier/stylesheet-class negative carriers pinned, prose-without-machinery guard held; W25-T7: SR/MK/LV/LT phrases added, Serbian Cyrillic kept distinct from Croatian Latin, Macedonian "дека/сум" kept distinct from Bulgarian ", че/съм"; W25-T8d: a challenge phrase living only in a placeholder attribute drove CHALLENGED on a served page — _PLACEHOLDER_ATTR_RE now stripped alongside _DATA_ATTR_RE in both survival variants, the W16 data-attribute doctrine extended to the last unnamed attribute species) + 28 pins held (blockquote and textarea default text are presented — fire on non-served, gate on served; robots orphan rules bind nobody and blank lines are not group boundaries; an llms `sitemap:` field in frontmatter is metadata (WARN) while the same pointer as body content is an index entry (PASS); a fragment suffix does not unmake a sitemap loc) + ONE HAND-CORRECTION (T2: HTTP 410 was originally classified WALLED under a deliberate-refusal reading; the Wave 6 pin test_s1c_410_gone failed against a briefly-added 410 branch and the pin is right — 410 is a definitive answer about the resource, the 404 species per W2-002/W6-S1c, and sits outside GENERIC_OK_STATUSES per W6-S1b; branch reverted, no classifier change ships for T2, corrected classification recorded in HANDCLASS-17) + corpus clean (44 captures, diff empty); 747 tests final. Leg C: FRONT-DOORS huggingface.co row ADDED (new "Wave 25 addition" section + one-row scoreboard; root 200 OPEN, /api bare path serves the site's HTML 404, directory path 401 LOGIN_GATED confirming the Wave 23 finding the same day; Hub API route VERIFIED from the platform's public docs; combined file count now 66 platforms — 40 VERIFIED / 20 NO ROUTE FOUND / 6 UNVERIFIED); SPEC status line now reads "hardened through Wave 25"; LAUNCH-POST untouched. MCP smoke green on all three tools (probe_url example.com OPEN; classify → CHALLENGED / Cloudflare; audit example.com F 3/12). Index at 500 rows: OPEN 413 / CHALLENGED 26 / WALLED 37 / RATE_LIMITED 7 / UNREACHABLE 17 / LOGIN_GATED 0 (recount verified). SATURATION: NOT MET — Wave 25 found 3 genuine defect families, so the two-consecutive-clean-waves clock resets again; Wave 26 becomes clean-wave candidate #1 if defect-free. No Wave 26 spawned per this wave's brief.
- Wave 24 (DONE 2026-10-24 ~08:52 PT): SATURATION VERDICT — NOT MET, clock RESET again (3 battery defect families). Rene ordered up to 5 more waves (24–28) at 08:07 PT; main chat chains them, this wave did not spawn the next. Leg A round-20: 500/500 probed with the Wave 23-fixed classifier; a mid-round service restart killed the runner at 276/500 — the three Wave 24 fixes were temporarily reverted (verified absent by grep AND by the battery re-failing on exactly the same 8 gaps), the runner relaunched against the pristine Wave 23 tree and resumed at 276, and the fixed file was then restored and sha256-verified; 3 verdict diffs, 2 merged, 1 held: wayfair.com to CHALLENGED / PerimeterX (round + 2 agreeing 429 challenge readings — the rounds 16–17 transient throttle is now the standing answer; a served triple would move it back), apnews.com to UNREACHABLE (round + 2 agreeing fetch failures — three consecutive failures retire the stale challenged row), britishairways.com held OPEN on a 1–1 fresh split (its second split-hold); ZERO fix-driven moves (no row answered 418 or 451; no fresh capture carried a W23 shape); npmjs read CHALLENGED directly (no drop), amazon CHALLENGED, both agreeing. NEW 402 WATCH: telegraph.co.uk and usatoday.com answered 402 in the round, read OPEN under the Wave 23 tree, and read WALLED on fresh captures under the Wave 24 tree (both small refusal stubs, bodies inspected — telegraph 1,028-byte security refusal, usatoday 254-byte "Access Restricted"); round 21 is their measurement round. Leg B battery v16: 36 shapes, 8 first-run failures = exactly the predicted gaps in 3 families, ALL fixed generalized (W24-R2: HTTP 402 joins the 444/451/418 deliberate-refusal family with STATUS_402; W24-R3: push-approval sign-in prompts — new _is_push_approval_prompt, visible-text phrase + button/form marker keys from birth, asset-filename/script-identifier/stylesheet-class negative carriers pinned, prose-without-machinery boundary ledgered; W24-R7: BG/SK/HR/SL phrases added, Slovak "nie ste" kept distinct from Czech "nejste") + 28 pins held (figcaption and summary are presented text and fire on non-served pages; robots case-insensitivity composes — WALLCHECK-only group PASS, GPTBOT caps value WARN, USER-AGENT caps field FAIL; duplicate-H1 llms is a content test, not a style test; mixed www/non-www sitemap locs PASS) + corpus clean (44 captures, diff empty); 710 tests final. Leg C: README counts corrected to 710 (stale at 608, chain extended 638 → 674 → 710 in both spots), SPEC status line now reads "hardened through Wave 24"; FRONT-DOORS contains NO huggingface.co entry, so the Wave 23 evidence (directory path now 401 LOGIN_GATED, 2026-10-24) is noted in DOCS-SPOT-4.md with no row edit; LAUNCH-POST untouched. MCP smoke green on all three tools (classify 402 → WALLED/STATUS_402; probe_url example.com OPEN; audit example.com grade F, 6 checks). Index at 500 rows: OPEN 414 / CHALLENGED 26 / WALLED 35 / RATE_LIMITED 7 / UNREACHABLE 18 / LOGIN_GATED 0 (recount verified). SATURATION: NOT MET — Wave 24 found 3 genuine defect families, so the two-consecutive-clean-waves clock resets again; Wave 25 becomes clean-wave candidate #1 if defect-free. No Wave 25 spawned per this wave's brief.
- Wave 23 (DONE 2026-10-24 ~08:35 PT): SATURATION VERDICT — NOT MET, clock stays RESET. Rene personally ordered this extra round after the 07:00 close (overnight cron stays disabled). Leg A round-19: 500/500 probed with the Wave 22-fixed classifier (runner detached + resumable, no incident; imported the Wave 22 tree at launch, so the Wave 23 fixes are unmeasured until round 20); 2 rows merged, both transport (britishairways.com to OPEN on round + 2 agreeing served readings — recovered from its Wave 15 failure merge; todoist.com to UNREACHABLE on round + 2 agreeing fetch failures — three consecutive failures retire the stale served row), 1 held (webex.com WALLED/Akamai on a 1–1 fresh split, its second split-hold; the fresh served reading's sso-mention is non-determinative); ZERO fix-driven moves (no row answered 418 or 451; no capture carried a W22 shape); npmjs read CHALLENGED directly (no drop), amazon CHALLENGED, both agreeing. Leg B battery v15: 36 shapes, 3 defect families ALL fixed test-first (stray <picture> text nodes — the never-presented family gains the picture species, alt scan deliberately exempt; HTTP 418 read OPEN — joins the 444/451 deliberate-refusal family as WALLED; EL/CS/HU/RO phrases) + 1 hand-correction (Q7f fragment pin belongs on a served page, J7g precedent) + corpus clean; 674 tests final. Leg C adopter spot-check v3: 4/4 adopters still publishing, all keys byte-identical; chatgpt.com exp drifted forward a third time (+12,555 s vs Wave 16's recorded JSON — still operated, still reference-grade); ahrefs still no purpose/window metadata; walled directory paths 15/15 still serve no directory (13 WALLED outright, npmjs transport-failed — its standing pattern, huggingface.co now answers a 401 LOGIN_GATED instead of a hard wall — a gate, not an opening). SPEC updated for the Wave 23 classifier changes. Index unchanged in distribution at 500 rows: OPEN 415 / CHALLENGED 26 / WALLED 35 / RATE_LIMITED 7 / UNREACHABLE 17 / LOGIN_GATED 0 (the two merges cancel; recount verified). SATURATION: Wave 23 found 3 defect families, so it is NOT a clean wave; the two-wave clean pair restarts from the next defect-free wave. No Wave 24 spawned per this wave's brief.
- Wave 22 (DONE 2026-10-24 ~06:48 PT): SATURATION VERDICT — NOT MET, clock stays RESET. Leg A round-18: 500/500 probed with the Wave 21-fixed classifier (runner detached + resumable, no incident; imported the Wave 21 tree at launch, so the Wave 22 fixes are unmeasured until round 19); ZERO rows merged, 2 held (chicagotribune.com OPEN on two agreeing fresh served readings against a round 403, transient refusal; forbes.com CHALLENGED/DataDome on a 1–1 fresh split, served-leaning 2–1 with no triple, oscillator extends); ZERO fix-driven moves (all ten Wave 20 merges agree; rubygems/remoteok/td/venmo/forbes spotlights hold). Leg B battery v14: 30 shapes, 3 defect families ALL fixed test-first (SVG title/desc metadata strip, SSO-continue prompts, GU/KN/NE/KM phrases) + 1 hand-correction (P2c vendor cell reads Generic — body evidence, not a re-attribution) + corpus clean; 638 tests final. Leg C vendor re-audit 2: 61/61 cells verified, ZERO corrections (apnews Cloudflare confirmed by fresh capture; four "unattributed (bare 403)" cells confirmed a third time). Index unchanged at 500 rows: OPEN 415 / CHALLENGED 26 / WALLED 35 / RATE_LIMITED 7 / UNREACHABLE 17 / LOGIN_GATED 0. SATURATION: Wave 22 found 3 defect families, so it is NOT a clean wave; the two-wave clean pair restarts from the next defect-free wave. The 07:00 morning-report run closes the night; no Wave 23 spawned from this wave per its brief.
- Wave 21 (DONE 2026-10-24 ~06:15 PT): SATURATION VERDICT — NOT MET, clock stays RESET. Leg A round-17: 500/500 probed with the Wave 20-fixed classifier (runner detached + resumable, no incident; imported the Wave 20 tree at launch, so the Wave 21 fixes are unmeasured until round 18); ZERO rows merged, 4 held (apnews.com CHALLENGED on a 1–1 fresh split, transport noise; amazon.com CHALLENGED on two agreeing fresh interstitials against a round served reading, oscillator note ‡ extends; npmjs.com CHALLENGED on two agreeing fresh challenges against a round connection drop, 10th transport-pattern sighting; wayfair.com OPEN on two agreeing fresh served readings against a round PerimeterX 429, transient throttle, Wave 20 hold repeated); ZERO fix-driven moves (all ten Wave 20 merges agree with round 17; forbes, remoteok/td/venmo, rubygems spotlights hold). Leg B battery v13: 37 shapes, 5 defect families ALL fixed test-first (object/embed routing species, high-traffic throttle cause, authenticator-app prompts, non-HTTP-scheme sitemap locs, TA/TE/MR/PA phrases) + 1 hand-correction (N4a mid-file "empty" robots group cannot exist per RFC 9309 grouping — corrected to FAIL, parser correct) + corpus clean; 608 tests final. Leg C path-matrix on the 10 Wave 20 merges: 50/50 probes, no contradictions (ed.gov walled on all five paths; the three UNREACHABLE job boards answer robots.txt 200 while origins fail — origin-down, not domain-dead). Leg D docs spot-check: README counts corrected (532/571/608 chain), SPEC status to Wave 21, INDEX distribution verified exact. Index unchanged at 500 rows: OPEN 415 / CHALLENGED 26 / WALLED 35 / RATE_LIMITED 7 / UNREACHABLE 17 / LOGIN_GATED 0. SATURATION: Wave 21 found 5 defect families, so it is NOT a clean wave; the two-wave clean pair restarts from the next defect-free wave. The 07:00 morning-report run closes the night; no Wave 22 spawned from this wave per its brief.
- Wave 20 (DONE 2026-10-24 ~05:50 PT): SATURATION VERDICT — NOT
  MET, clock stays RESET. Leg A round-16: 500/500 probed with
  the Wave 19-fixed classifier (runner detached + resumable, no
  incident; imported the Wave 19 tree at launch, so the Wave 20
  fixes are unmeasured until round 17); 10 rows merged
  (claude.ai CHALLENGED/CF, amazon CHALLENGED/Generic, ed.gov
  CHALLENGED/Azure, fda.gov OPEN, goodrx CHALLENGED/PX,
  irishjobs/jobs/totaljobs UNREACHABLE, jobrapido OPEN,
  ubereats CHALLENGED/CF), 3 held (npmjs CHALLENGED, 9th
  transport-pattern sighting; wayfair OPEN; webex WALLED on a
  1–1 fresh split); ZERO fix-driven moves; LOGIN_GATED watch
  empties (both standing LOGIN_GATED rows moved). Leg B battery
  v12: 39 shapes, 3 defect families ALL fixed test-first
  (iframe-src routing targets, localized JS-proof phrases
  DE/FR/ES/PT/JA, localized human-check UK/HI/MS/TL/SW) + 1
  hand-correction (identity-verification phrase is
  auth-ambiguous, corrected to OPEN) + corpus clean; 571 tests
  final. Leg C adopter spot-check 4/4 still publishing +
  INDEX recount exact. Index now 500 rows: OPEN 415 /
  CHALLENGED 26 / WALLED 35 / RATE_LIMITED 7 / UNREACHABLE 17 /
  LOGIN_GATED 0. SATURATION: Wave 20 found 3 defect families,
  so it is NOT a clean wave; the two-wave clean pair restarts
  from the next defect-free wave. Wave 21 next; ~1h remains to
  07:00.
- Wave 19 (DONE 2026-10-24 ~05:55 PT): SATURATION VERDICT — NOT MET, clock stays RESET. Leg A round-15: 500/500 probed with the Wave 18-fixed classifier (runner detached + resumable, no incident; imported the Wave 18 tree at launch, so the Wave 19 fixes are unmeasured until round 16); 6 rows merged (ed.gov UNREACHABLE on round + 2 failures; forbes.com CHALLENGED/DataDome on round + 2 agreeing challenges — the triple the oscillator's splits never met; irishjobs.ie, jobs.ie, totaljobs.com OPEN on round + 2 served; jobrapido.com RATE_LIMITED on round + 2 agreeing 429s), 4 held (apnews.com, abc.net.au, lowes.com on splits/overturns; npmjs.com CHALLENGED, 8th transport-pattern sighting); ZERO fix-driven moves (all five spotlights held: ubereats.com OPEN, remoteok/td/venmo OPEN, rubygems.org OPEN). Leg B battery v11: 51 shapes, 8 defect families ALL fixed test-first (template blocks, split alt phrases, email-Continue steps, fallthrough usability, CR-only frontmatter, fragment-only locs, HE/FA/UR/BN phrases, native dialog elements) + corpus clean; one Wave 16 guard superseded with independent justification (the guard's shape IS an email-Continue step under the new rule) and one hand-correction (L2e's DE half was a complete phrase on its own); 532 tests final. Leg C DOGFOOD Wave 18 addendum written (vendor shares recomputed from INDEX.md). Leg D LOGIN_GATED watch: claude.ai still a real login redirect, fda.gov still a 401 — no softening. Index now 500 rows: OPEN 419 / CHALLENGED 21 / WALLED 35 / RATE_LIMITED 8 / UNREACHABLE 15 / LOGIN_GATED 2. SATURATION: Wave 19 found 8 defect families, so it is NOT a clean wave; the two-wave clean pair restarts from the next defect-free wave. Wave 20 next; ~1h remains to 07:00.
- Wave 1 (DONE): 58-site census. OPEN 47 / WALLED 4 / CHALLENGED 4 /
  UNREACHABLE 3. 24/24 tests.
- Wave 2 (DONE): 77-path depth probing; RFC 9421 HMAC signer prototype.
  46/46 tests. v0.2.0.
- Wave 3 (DONE): stability 56/58; index merged at 154; owner audit
  shipped; AWS WAF + Akamai edgesuite detection. 59/59 tests. v0.3.0.
- Wave 4 (DONE): round-3 stability clean (4 flips, all churn); directory
  census 3/154 adopters (chatgpt.com, indeed, substack); pure-Python
  Ed25519 shipped vs RFC 8032 vectors; 4 vendor report cards. 75/75
  tests. v0.4.0.
- Wave 5 (DONE ~21:48 PT): round-4 stability — 1 flip of 154 (npmjs transport
  churn, merged unchanged OPEN 136 / CHALLENGED 9 / WALLED 6 / RATE_LIMITED 1 /
  UNREACHABLE 2); expansion round 2 toward ~250 — 5 classifier defects all
  fixed test-first (duolingo captcha-widget false-CHALLENGE, ed.gov Azure WAF
  unattributed, chewy.com Kasada misattributed as Akamai, redfin AWS CloudFront
  block page, delta.com Akamai deny served 444 FALSE OPEN); signed-vs-unsigned
  experiment 12/12 unchanged — unregistered signatures not consulted by walls;
  chatgpt.com directory verified reference-grade and actively maintained;
  owner FIX-KIT + staged fixes for our own properties. 85/85 tests. v0.4.0→v0.5.0-dev.
- Wave 6 (DONE ~00:35 PT 2026-10-24): adversarial hardening —
  Leg A DONE (battery of 25 hand-classified edge shapes pinned in
  tests/test_adversarial.py; 4 defects fixed generalized — JS_PROOF
  marker for vendor-neutral 202/JS-proof stubs, generic-marker branch
  yields to login pages, localized ES/DE/FR/JA/PT human-check phrases,
  Incapsula incident-ID ⇒ WALLED at any status; one hand-classification
  corrected by the Amazon interstitial; 110/110 tests, 41-capture corpus
  clean, SPEC.md updated; report validation/wave6/ADVERSARIAL.md).
  Leg B DONE (index expansion toward 500): 136 clean long-tail
  candidates deduped against INDEX.md + DNS-checked; all probed once
  and merged — index 258 → 394 rows (jobs +18, new saas section +61,
  news +57). Distribution: OPEN 126 / CHALLENGED 5 / WALLED 3 /
  UNREACHABLE 2. One more defect surfaced by the expansion itself
  (W6-005): vendor-race ordering let Cloudflare CDN presence outrank
  economist.com's fired DataDome wall — fixed with generalized
  wall-signal precedence, re-probed CHALLENGED/DataDome, row corrected;
  report validation/wave6/EXPANSION.md. Saturation test: NOT met
  (5 defects this wave + new coverage) — Wave 7 next.
- Wave 7 (DONE ~01:12 PT 2026-10-24): index 394 → 499 rows
  (105 expansion: OPEN 79 / WALLED 9 / CHALLENGED 5 / RATE_LIMITED 2 /
  UNREACHABLE 10); round-5 stability 496/499 identical (3 flips,
  all churn/transport; amazon.com's intermittent interstitial
  returned, merged CHALLENGED); vendor fills (npmjs → Cloudflare,
  realtor 429 → Kasada); directory census v2: 4/499 adopters
  (NEW: ahrefs.com, 2 keyed Ed25519 keys) + 71 domains wall the
  directory path itself; audit sweep of 92 most-walled domains
  (F 71 / D 18 / C 3) with top-5 systemic owner mistakes.
  ZERO classifier defects — the one suspect (careerjet) was
  CORRECTED on proper reading (genuine verification interstitial;
  classifier right). Incident: egress-proxy credential rotation
  poisoned 52 round-5 rows; diagnosed by proxy-hash comparison,
  rows archived + re-probed after fresh-shell restart (see
  STABILITY-4.md). 112/112 tests (2 new W7 fixtures). v0.5.0-dev
  unchanged (no classifier change). Saturation test: NOT met on
  the "zero new coverage" prong (expansion + census v2 + audit
  sweep are new coverage), but ZERO defects across all four legs
  is the first clean defect sheet on a full wave — Wave 8 (depth
  wave 2) is the saturation decider.
- Wave 11 (DONE 2026-10-24 ~03:30 PT): SATURATION VERDICT — NOT
  MET, clock RESET again. Leg A round-7 reclassification: 499/499
  probed with the Wave 10-fixed classifier; 3 flips, all merged
  on fresh-capture corroboration (amazon CHALLENGED→OPEN on two
  agreeing sat-outs, note ‡ preserves the oscillation;
  britishairways UNREACHABLE→OPEN, recovered from the W10
  timeout; merrilledge OPEN→LOGIN_GATED, the round's ONLY
  fix-driven move — W10-004 redirect-to-login rule, sitedown
  page declares a JS redirect to a login widget, verified in the
  body; geo-refusal, 451, and UNREACHABLE-vendor rules moved
  zero live rows). Index now OPEN 416 / CHALLENGED 24 / WALLED 34
  / RATE_LIMITED 7 / UNREACHABLE 17 / LOGIN_GATED 1 (first standing
  LOGIN_GATED row). Leg B battery v3: 31 new shapes, 6 genuine
  defects ALL fixed test-first (form-action redirect targets,
  "verify your request" JS-proof phrasing, Turnstile-loader-only
  login yield, IT/NL/KO localized phrases, Generic-vendor leak
  onto login verdicts, robots wildcard FAIL semantics) + 44-
  capture corpus clean; 183/183 tests. Leg C regression: suite
  183/183, MCP smoke on all 3 tools, spot re-audit of
  hub.docker.com / huggingface.co / typeform.com all hold C 7/12
  (correctly unchanged — none serves the new-gate error
  documents). SATURATION: Wave 11 found 6 defects, so it is NOT
  a clean wave; the two-wave clean pair restarts from the next
  defect-free measurement wave. NOTE: round 7 ran the Wave 10-
  fixed classifier (runner started before the W11 fixes landed),
  so the W11 fixes themselves are unmeasured on live traffic
  until the next round.
- Wave 11 (IN_PROGRESS 2026-10-24 ~01:52 PT): Leg A round-7
  fix-driven reclassification re-probe of the full 499-row index
  with the Wave 10-fixed classifier, Leg B adversarial battery v3,
  Leg C full-surface regression + spot re-audit of 3 C-graded
  sweep domains. Clean here = saturation candidate #1.
- Wave 12 (IN_PROGRESS 2026-10-24 ~02:10 PT): Leg A round-8
  re-probe of the full 499-row index with the Wave 11-fixed
  classifier (fixes verified present before probing), Leg B
  adversarial battery v4 (new shapes: PL/TR/AR/ZH/RU pages,
  countdown interstitials, tokenless browser-check pages,
  consent-gating hybrids, captcha-widget login forms with
  challenge-endpoint form actions, per-agent robots carve-outs,
  llms format variants, sitemap.xml.gz, 3+ hop redirect chains
  to walls), Leg C version hygiene note + signed spot-check on
  chatgpt.com + ahrefs.com. Clean here = saturation candidate
  #1 (Wave 11 reset the clock).
- Wave 12 (DONE 2026-10-24 ~02:45 PT): SATURATION VERDICT — NOT
  MET, clock RESET again. Leg A round-8: 499/499 probed with the
  Wave 11-fixed classifier; ZERO fix-driven moves (all six Wave
  11 rule families moved no live row); 2 merges, both
  corroborated churn (amazon CHALLENGED on two agreeing
  interstitial readings, britishairways UNREACHABLE on two
  agreeing timeouts); npmjs held CHALLENGED (6th transport-
  pattern sighting), webex held OPEN (single uncorroborated
  Akamai 403). Index now OPEN 414 / CHALLENGED 25 / WALLED 34 /
  RATE_LIMITED 7 / UNREACHABLE 18 / LOGIN_GATED 1. Leg B battery
  v4: 27 shapes, 6 genuine defects ALL fixed test-first
  (PL/TR/AR/ZH/RU phrases, "browser check" JS_PROOF phrase,
  form-action/login-yield split, JSON llms WARN, markdown
  mislabel carve-out, gzip sitemap decompression) + corpus clean;
  210/210 tests. Leg C: version note concludes next stamp is
  0.5.0 final (not 0.5.1-rc; no version files touched); signing
  spot-check 2/2 unchanged (chatgpt.com, ahrefs.com). SATURATION:
  Wave 12 found 6 defects, so it is NOT a clean wave; the
  two-wave clean pair restarts from the next defect-free wave.
  Wave 13 (measurement + battery v5) is next; ~4h remain to 07:00.
- Wave 13 (IN_PROGRESS 2026-10-24 ~02:30 PT): Leg A round-9
  re-probe of the full 499-row index with the Wave 12-fixed
  classifier (all six W12 fixes grep-verified present before
  probing), Leg B adversarial battery v5 (new shapes: image-only
  captcha, noscript-only pages, title-only human-check wording,
  challenge-cookie + served content, robots all-vs-one agent,
  title-only llms.txt, one-URL sitemaps, multi-hop chains to
  login, comment-only vendor markers, mixed-case markers),
  Leg C INDEX.md records audit (30+ row spot-check vs history,
  vendor-or-unattributed on every WALLED/CHALLENGED row, Amazon
  note ‡ current through round 8). Clean here = saturation
  candidate #1 (Wave 12 reset the clock).
- Wave 14 (DONE 2026-10-24 ~03:50 PT): SATURATION VERDICT — NOT
  MET, clock stays RESET. Leg A round-10: 499/499 probed with the
  Wave 13-fixed classifier (clean launch after a documented
  sed-trap no-op launch and a contaminated launch whose 41
  lines were killed and purged); 3 diffs, all hand-checked with
  fresh captures under a Wave 13-tree copy — todoist.com merged
  to OPEN, britishairways.com held OPEN, kaiserpermanente.org
  held OPEN/302; ZERO fix-driven moves (fourth straight round).
  Index now OPEN 416 / CHALLENGED 25 / WALLED 35 / RATE_LIMITED 7
  / UNREACHABLE 16 / LOGIN_GATED 0. Leg B battery v6: 32 shapes,
  5 genuine defects ALL fixed test-first (script-only generic
  markers, traffic-anomaly challenges, Retry-After throttles,
  declared-sitemap fallthrough, fragment-only llms links) + 1
  fixture correction (F5c cookie name) + corpus clean; 270/270
  tests. Leg C vendor audit: all 60 WALLED/CHALLENGED rows vs
  round-10 evidence, 0 mismatches, 0 fixes needed. SATURATION:
  Wave 14 found 5 defects, so it is NOT a clean wave; the
  two-wave clean pair restarts from the next defect-free wave.
  Wave 15 next; ~3h remain to 07:00.
- Wave 18 (DONE 2026-10-24 ~04:54 PT): SATURATION VERDICT — NOT MET, clock stays RESET. Leg A round-14: 499/499 probed with the Wave 17-fixed classifier (first launch died at 123/499 with no traceback, external kill; resume imported a reconstructed Wave 17 tree copy so the round measures ONE tree); 5 rows merged (claude.ai LOGIN_GATED/CF, amazon OPEN, fda LOGIN_GATED/Akamai, goodrx OPEN, ubereats OPEN), 7 held (abc OPEN, britishairways UNREACHABLE, forbes OPEN, kroger UNREACHABLE on splits/overturns; remoteok/td/venmo OPEN — three Wave 17 QR-prompt misfires rejected); EXACTLY ONE fix-driven move (ubereats, W17-002 head strip on a <head> CSP host list) — the first fix-driven move in rounds 8–14. Leg B battery v10: 48 shapes, 6 defect families ALL fixed test-first (sticky banners, SMS/email digit-box prompts, dead-declaration evidence, empty locs, PT-BR/ID/VI/TH phrases, non-interactive aria-labels) + corpus clean; 476 tests at battery end. Leg A live catch W18-007: the Wave 17 QR rule misfired on three served homepages (script filename, script identifier, stylesheet classes) — fixed (visible-text wording + size gate), post-fix re-probes read OPEN; 481 tests final. Leg C row 500: search.brave.com OPEN (search section was thinnest at 2 rows). Leg D docs spot-check: 423-vs-428 resolved (428 was right at Wave 17 end; 423 was the mid-wave battery count), README/SPEC/INDEX corrected, header recount exact. Index now 500 rows: OPEN 418 / CHALLENGED 21 / WALLED 35 / RATE_LIMITED 7 / UNREACHABLE 17 / LOGIN_GATED 2. SATURATION: Wave 18 found 7 defect families (6 battery + 1 live catch), so it is NOT a clean wave; the two-wave clean pair restarts from the next defect-free wave. Wave 19 next; ~2h remain to 07:00.
- Wave 18 (IN_PROGRESS 2026-10-24 ~04:26 PT): Leg A round-14 re-probe of the full 499-row index with the Wave 17-fixed classifier (W17 fixes grep-verified before probing), Leg B adversarial battery v10 (CSS custom properties, sticky-banner challenges, SMS-code login prompts, robots Sitemap→404, llms trailing-slash redirect, relative-loc sitemaps, PT-BR/ID/VI/TH phrases, aria-label-only challenge phrases), Leg C the 500th index row, Leg D docs spot-check (README suite count 423 vs 428). Clean here = saturation candidate #1 (Wave 17 reset the clock).
- Wave 17 (DONE 2026-10-24 ~04:50 PT): SATURATION VERDICT — NOT MET, clock stays RESET. Leg A round-13: 499/499 probed with the Wave 16-fixed classifier (grep-verified before launch; Wave 17 battery fixes unmeasured until round 14); ZERO rows merged — 3 diffs all held on fresh captures (rubygems.org LOGIN_GATED rejected as a Wave 16 passkey-rule false positive on a served homepage, fixed same wave as W17-007; britishairways.com served-leaning 2–1 held UNREACHABLE; forbes.com challenged-leaning 2–1 held OPEN, oscillator extends); ZERO fix-driven moves (rounds 8–13). Index unchanged: OPEN 415 / CHALLENGED 25 / WALLED 35 / RATE_LIMITED 7 / UNREACHABLE 17 / LOGIN_GATED 0. Leg B battery v9: 48 shapes, 6 fix families ALL fixed test-first (noscript/title metadata suppression + corroboration rule, QR prompts, entity JSON, Nordic phrases, overlay challenges) + pins (cache headers, commented Sitemaps, script-boundary captcha re-test, code-switched fragments) + corpus clean; 423 tests at battery end. Leg C docs re-audit: 6 corrections (README suite count + wave list, SPEC status, INDEX round-8 narrative, Akamai share 22/35, DOGFOOD Waves 9–17 addendum). W17-007 live fix adds 5 fixtures. Final: 428/428 tests, MCP smoke on all 3 tools. SATURATION: Wave 17 found 7 defect families (6 battery + 1 live catch), so it is NOT a clean wave; the two-wave clean pair restarts from the next defect-free wave. Wave 18 next; ~2h remain to 07:00.
- Wave 16 (DONE 2026-10-24 ~04:30 PT): SATURATION VERDICT — NOT
  MET, clock stays RESET. Leg A round-12: 499/499 probed with
  the Wave 15-fixed classifier (imported at launch, before the
  Wave 16 fixes landed — the Wave 16 rules are unmeasured until
  round 13); ZERO merges (5 verdict diffs all held on fresh
  captures: npmjs + apnews held CHALLENGED on transport noise,
  france24 + forbes held OPEN on two agreeing served readings,
  britishairways held UNREACHABLE on a 1–1 fresh split with no
  corroboration triple); ZERO fix-driven moves (sixth straight
  round). Index unchanged: OPEN 415 / CHALLENGED 25 / WALLED 35
  / RATE_LIMITED 7 / UNREACHABLE 17 / LOGIN_GATED 0. Leg B
  battery v8: 49 shapes, 21 genuine defects ALL fixed
  test-first (TRAFFIC_CHECK visible-text + concatenated-text
  scans, data-attribute + style-block suppression, Location-
  header redirect targets, passkey prompts, magic-link forms,
  BOM-tolerant frontmatter, JSON data-block generalization)
  + corpus clean; 375/375 tests. Leg C adopter spot-check:
  4/4 adopters still publishing (chatgpt.com's exp moved
  +11,956 s since Wave 7 — still operated; ahrefs gained no
  purpose/window metadata); 9/10 walled directory paths still
  walled (npmjs transport noise, not an opening). SATURATION:
  Wave 16 found 21 defects, so it is NOT a clean wave; the
  two-wave clean pair restarts from the next defect-free wave.
  Wave 17 next; ~2.5h remain to 07:00.
- Wave 15 (DONE 2026-10-24 ~04:10 PT): SATURATION VERDICT — NOT
  MET, clock stays RESET. Leg A round-11: 499/499 probed with the
  Wave 14-fixed classifier (clean launch — runner written fresh
  with a single ROUND constant, output growth verified before
  walking away, no sed-trap incident this wave); 3 diffs, all
  hand-checked with fresh captures — forbes.com HELD at OPEN
  (round-11 DataDome challenge overturned by two fresh served
  readings; a later spot-check read CHALLENGED again, so forbes
  is now a documented intermittent oscillator on a 2–2 split),
  britishairways.com MERGED to UNREACHABLE (round-11 plus two
  agreeing fresh fetch failures — the mirror of the Wave 14
  hold), webex.com HELD at WALLED / Akamai (round-11 served
  reading overturned by two fresh edgesuite denies); ZERO
  fix-driven moves (fifth straight round). Index now OPEN 415 /
  CHALLENGED 25 / WALLED 35 / RATE_LIMITED 7 / UNREACHABLE 17 /
  LOGIN_GATED 0. Leg B battery v7: 39 shapes, 13 genuine defects
  ALL fixed test-first (JSON-LD vendor suppression,
  refusal-phrase rule, visible-text phrase scan, invisible-widget
  suppression, Refresh-header targets, code-entry login signal,
  footer-badge suppression, robots Allow tiebreak, llms
  frontmatter stripping + length-gate refinement, sitemap loc
  requirement) + corpus clean; 321/321 tests. Leg C limitations
  revisit: 10 limitations re-tested — 1 narrowed (F5 form-signal
  gains the code-entry species), 1 resolved by construction (hop
  bodies), 8 still open (incl. the Wave 3 silent-JS-proof
  boundary, which survives: a wording-free, token-free proof page
  still carries no deterministic signal). SATURATION: Wave 15
  found 13 defects, so it is NOT a clean wave; the two-wave
  clean pair restarts from the next defect-free wave. Wave 16
  next; ~2.5h remain to 07:00.
- Wave 14 (IN_PROGRESS 2026-10-24 ~02:50 PT): Leg A round-10
  re-probe of the full 499-row index with the Wave 13-fixed
  classifier (all three W13 fixes grep-verified present before
  probing), Leg B adversarial battery v6 (new shapes: script-JSON
  markers, alt-attribute-only text, unusual/suspicious phrasing,
  Retry-After throttles, session-challenge login cookies, sitemap
  indexes, relative-link-only llms, walls only in redirect hops),
  Leg C vendor-attribution audit of all 60 WALLED/CHALLENGED
  rows. Clean here = saturation candidate #1 (Wave 13 reset the
  clock).
- Wave 13 (DONE 2026-10-24 ~03:30 PT): SATURATION VERDICT — NOT
  MET, clock RESET again. Leg A round-9: 499/499 probed with the
  Wave 12-fixed classifier; ZERO fix-driven moves (third straight
  round); 3 merges, all corroborated by fresh captures
  (britishairways UNREACHABLE→OPEN, merrilledge LOGIN_GATED→OPEN
  — its Wave 11 login gate is gone, the site serves its real
  homepage — webex OPEN→WALLED/Akamai, the second sighting after
  round 8); amazon held CHALLENGED on two agreeing fresh
  interstitial readings against a round-9 sat-out. Index now OPEN
  415 / CHALLENGED 25 / WALLED 35 / RATE_LIMITED 7 / UNREACHABLE
  17 / LOGIN_GATED 0. Leg B battery v5: 25 shapes, 3 genuine
  defects ALL fixed test-first (comment-only vendor markers
  stripped before body scans, "check your browser" JS_PROOF
  phrase, title-only llms.txt WARN) + 2 hand corrections (E8b
  vendor, E3b fixture size) + corpus clean; 236/236 tests. Leg C
  index audit: 499 rows, distribution matches header, 44-row
  stratified spot-check vs round 8 with zero mismatches, Amazon
  note ‡ current through round 8 (extended with round-9
  sat-out); 4 surgical vendor-cell fixes (unattributed bare-403
  notes for catho/haaretz/hyatt/state.gov). SATURATION: Wave 13
  found 3 defects, so it is NOT a clean wave; the two-wave clean
  pair restarts from the next defect-free wave. Wave 14 next;
  ~3.5h remain to 07:00.
- Wave 8 (next): depth wave 2 — path probing for the Wave 5
  civic/finance/travel additions; front-doors updates for any
  new walled platform; fix-kit v2 informed by audit patterns.
- Wave 8 (IN_PROGRESS 2026-10-24 ~01:15 PT): Leg A path matrix
  (46 platforms × 7 paths), Leg B front-doors update, Leg C
  fix-kit v2 + own-properties re-audit.
- Wave 8 (DONE 2026-10-24 ~01:30 PT): Leg A — 322/322 path probes,
  final OPEN 94 / WALLED 145 / CHALLENGED 54 / RATE_LIMITED 20 /
  UNREACHABLE 6 / LOGIN_GATED 3. Stories: 21 whole-domain walls
  (vs 1 in Wave 2's cohort) vs 8 homepage-only walls; /api serves
  nothing real (27 walled/challenged, 14 honest 404s); genuine
  llms.txt on only 3 platforms (careerbuilder, catho, expedia);
  Expedia-family 429 throttle is app-path-scoped; bare-403
  unattributed trio (state.gov, hyatt, haaretz). ONE classifier
  defect, fixed test-first and generalized (W8-001: login heuristic
  fired on delta's 444 Akamai deny — now requires a served page,
  2xx/3xx; 2 new tests; delta login re-probed live WALLED Akamai
  444, row corrected). Leg B — FRONT-DOORS.md +55 rows (31
  VERIFIED / 19 NO ROUTE FOUND / 5 UNVERIFIED), file now 65
  platforms. Leg C — FIX-KIT.md §7 (two-step signed-agent fix,
  API-surface fix, huggingface C→B→A worked example); own
  re-audit unchanged (clipwise D 5/12, portfolio F 3/12, Pages F
  3/12); Wave 5 "portfolio to at least B" claim corrected to C
  (staged deploy buys 7/12; B needs feed + directory), and
  cloudcorprecords.github.io flagged as never staged. 114/114
  tests (2 new W8 tests), MCP smoke passes, all JSON re-parsed,
  no 0-byte files. Saturation test: NOT met — Wave 8 found a real
  defect (breaks the zero-defect prong vs Wave 7) and added new
  coverage (path matrix for 46 platforms, 55 front-doors rows,
  fix-kit §7). Wave 9 (release-candidate polish) is next; the
  two-wave saturation clock resets and needs two consecutive
  clean waves from here.
- Wave 9 (IN_PROGRESS 2026-10-24 ~01:28 PT): Leg A docs
  consistency audit, Leg B MCP audit-tool decision, Leg C
  0.5.0-rc release candidate + launch-readiness memo.
- Wave 10 (DONE 2026-10-24 ~02:25 PT): SATURATION DECIDER — verdict: NOT MET, clock RESET. Leg A round-6 stability: 499/499 probed, 7 raw flips, 5 hand-checked, only britishairways.com merged (reproduced timeout → UNREACHABLE); index now OPEN 415 / CHALLENGED 25 / WALLED 34 / RATE_LIMITED 7 / UNREACHABLE 18. Leg B adversarial battery v2: 32 new shapes, 8 genuine defects ALL fixed test-first (geo-refusal 200 → WALLED, 451 → WALLED, redirect-to-challenge → CHALLENGED, redirect-to-login → LOGIN_GATED, 5xx UNREACHABLE vendor reset, llms JSON-error FAIL, robots HTML soft-404 FAIL) + corpus 44 captures zero regressions; 152/152 tests. Leg C signing regression on 0.5.0-rc: 7/7 unchanged, self-verify ok, tamper rejected — no regression. SATURATION VERDICT: reset — Wave 10 found 8 defects, so the two-wave clean pair must restart from the next defect-free measurement wave; Wave 10 is NOT a clean wave despite Leg A's clean sheet.
- Wave 9 (DONE 2026-10-24 ~01:50 PT): Leg A — 14 doc corrections
  (C-01…C-14: Wave 5 defect count six→five in INDEX.md + README.md,
  README/SPEC index sizes 258→499, vendor list completed, Akamai
  card qualified to Wave 4 era + current 21/34 WALLED, version split
  resolved, DOGFOOD Waves 4–8 addendum, SPEC/README MCP surface,
  FRONT-DOORS edition label, INDEX Wave 8 note) + 8 VERIFIED items
  (INDEX header recount 499 exact, adopter counts, own grades,
  Wave 6 shape count reconciled, test-count chain) + 2 intentional
  non-corrections (LAUNCH-POST Wave 1 numbers — refresh at ship;
  historical wave sentences). INDEX.md header re-verified row by
  row: 499 rows, distribution matches exactly. Leg B — MCP decision
  YES: `audit` tool shipped (≤10 honest GETs, stated + tested
  fetch budget; 5 new server tests + 1 budget test; smoke driver
  now calls all 3 tools live, example.com audit F 3/12). Leg C —
  0.5.0-rc stamped in __init__/pyproject/server.json (GHCR tag) +
  README/SPEC banners; suite 120/120; all 78 validation JSON files
  re-parsed whole-document (an earlier per-line check false-
  alarmed on pretty-printed JSON — files are strict JSON, not
  repr); no 0-byte files; campaign/LAUNCH-READINESS.md written
  (proven / not-proven / ship needs only: the ship call, the
  launch-post refresh, optionally the own-property deploys).
  Saturation assessment: Wave 9 is defect-free with no new
  vendors/signals and no new measurement coverage, BUT it grew
  the product surface (audit MCP tool), so the strict two-wave
  test is not met by Wave 9 alone — it is clean-wave candidate
  #1 on the defect prong only. Wave 10 (measurement wave) is the
  decider: clean there completes the pair; any defect or new
  ground resets the clock. NOTHING PUBLISHED — launch hold holds.

## Roadmap after Wave 5

- Wave 6 — Adversarial hardening: fixture battery of obfuscated/edge
  wall shapes (soft-404 variants, redirect-chain walls, 202 JS-proof
  pages without vendor tokens, multi-vendor stacks, login walls behind
  challenges, localized challenge pages EN/ES/DE/FR/JA), each classified
  by hand first, then pinned; classifier gaps fixed generalized.
  Plus: index expansion toward 500 begins (long tail: regional job
  boards, SaaS tools, media).
- Wave 7 — Index to ~500: complete the expansion; round-5 re-probe of
  the full set + history append; directory census v2 across all ~500;
  audit sweep of the 50 most-walled domains (owner grades at scale).
- Wave 8 — Depth wave 2: path probing (login/signup/API/robots/llms)
  for the Wave 5 civic/finance/travel additions; front-doors updates
  for any new walled platform; fix-kit v2 informed by audit patterns.
- Wave 9 — Release-candidate polish (STILL UNLAUNCHED): docs pass,
  README/DOGFOOD/SPEC consistency audit, MCP surface review (consider
  an audit MCP tool), full-suite + smoke verification, version bump to
  0.5.0-rc, and a launch-readiness memo in campaign/ stating exactly
  what is proven, what is not, and what the ship decision needs.

## Saturation test

Declare saturation only when TWO consecutive waves both produce: zero
classifier defects, zero new vendors/signals, and zero new coverage
(site categories or path types) — then write the final overnight
report and stop. Churn-only stability rounds do not count toward
saturation by themselves; each wave must also attempt new coverage or
new adversarial ground.

## Morning report (07:00 PT)

Compile from this file + wave reports: final version, test count,
index size + verdict distribution, stability record, directory census,
what is launch-ready, what remains unproven. Deliver to the main chat.
