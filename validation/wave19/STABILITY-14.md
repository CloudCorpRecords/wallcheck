# Wave 19 — Round-15 re-probe measuring the Wave 18 fixes (Leg A)

**500/500 rows probed once each** with the Wave 18-fixed
classifier — the measurement Wave 18's STABILITY-13 deferred.
The runner (`validation/wave19/run_round15.py`, written fresh
for round 15 with the round number in exactly one constant)
imported the Wave 18 tree at launch (11:57 UTC, before any Wave
19 battery edit landed — verified by process start time vs file
mtimes): all Wave 18 fixes were grep-verified present before
probing (W18-001 sticky-banner rule with stickiness third key,
W18-002 DELIVERY_CODE_PROMPT, W18-003 DECLARED_SITEMAP_DEAD
evidence, W18-004 nonempty-loc requirement, W18-005 PT-BR/ID/VI/
TH phrases, W18-006 non-interactive aria-label strip, W18-007
visible-text QR wording + served-page gate). The runner ran
fully detached (setsid nohup, resumable, monitored via its log)
after Wave 18's first launch died at 123/499 — no incident this
wave: 500 new probes, zero missing URLs vs the INDEX table,
zero duplicate round-15 lines. All 500 history lines parse.

**Method note on fresh captures:** the round measured the Wave
18 tree, but fresh captures necessarily ran on the current
(Wave 19-fixed) tree. Every fresh capture therefore carries a
Wave 19-rule involvement check (template blocks, dialog tags,
Continue-step forms, HE/FA/UR/BN phrases, EMAIL_CONTINUE_PROMPT
evidence). All 20 fresh captures report zero involvement flags —
the corroborations below are tree-comparable. Fetch failures
are tree-independent (no response was classified). One runner
discovery, same family as Wave 16's: probe_url does not return
the body, so the fresh-capture script uses fetch_raw + classify
(the probe_url equivalent with the body retained).

Round-15 raw distribution: OPEN 417 · CHALLENGED 19 · WALLED 36 ·
RATE_LIMITED 8 · UNREACHABLE 18 · LOGIN_GATED 2.

## The 10 verdict diffs, all hand-checked with fresh captures

Every verdict diff was hand-checked with two fresh captures
(`validation/wave19/fresh_captures.py`, results in
`fresh-captures.json`) before merging — no diff was merged on
the round-15 reading alone. The strict rule: merge only on
round + 2 agreeing fresh; a 1–1 fresh split holds the row.

| target | standing | round 15 | fresh capture(s) | disposition |
| --- | --- | --- | --- | --- |
| apnews.com | CHALLENGED / Cloudflare | UNREACHABLE (fetch failure) | CHALLENGED / Cloudflare + UNREACHABLE (fetch failure) | **HELD at CHALLENGED.** 1–1 fresh split — no corroboration triple for either side. Transport noise (the Wave 16 apnews sighting, same pattern). |
| www.abc.net.au | OPEN 200 | WALLED / Akamai 403 | OPEN 200, twice | **HELD at OPEN.** The round's Akamai 403 is overturned by two agreeing fresh served readings — a transient deny, the Wave 18 hold repeated. |
| www.ed.gov | CHALLENGED / Microsoft Azure WAF | UNREACHABLE (fetch failure) | UNREACHABLE, twice | **MERGED to UNREACHABLE.** Round + 2 agreeing failures — the britishairways.com Wave 15 pattern: three consecutive failures retire a stale challenged row. NOT fix-driven: no response was classified. |
| www.forbes.com | OPEN 200 | CHALLENGED / DataDome 403 | CHALLENGED / DataDome 403, twice | **MERGED to CHALLENGED / DataDome.** Round + 2 agreeing fresh — the corroboration triple the oscillator's earlier 2–1 splits never met. The oscillator note extends (a served round-16 triple would move it back); it does not exempt the row. NOT fix-driven: DataDome detection, no Wave 18 rule touches it. |
| www.irishjobs.ie | UNREACHABLE | OPEN 200 | OPEN 200, twice | **MERGED to OPEN.** Round + 2 agreeing served readings — the site recovered. NOT fix-driven. |
| www.jobrapido.com | OPEN 200 | RATE_LIMITED 429 | RATE_LIMITED 429, twice | **MERGED to RATE_LIMITED.** Round + 2 agreeing throttle readings. NOT fix-driven. |
| www.jobs.ie | UNREACHABLE | OPEN 200 | OPEN 200, twice | **MERGED to OPEN.** Round + 2 agreeing served readings — recovered. NOT fix-driven. |
| www.lowes.com | OPEN 200 | UNREACHABLE (fetch failure) | OPEN 200 + UNREACHABLE (fetch failure) | **HELD at OPEN.** 1–1 fresh split — no triple. |
| www.npmjs.com | CHALLENGED / Cloudflare | UNREACHABLE (fetch failure) | CHALLENGED / Cloudflare, twice | **HELD at CHALLENGED.** The round's connection drop is overturned by two agreeing fresh challenged readings — the 8th transport-pattern sighting for npmjs.com. |
| www.totaljobs.com | UNREACHABLE | OPEN 200 | OPEN 200, twice | **MERGED to OPEN.** Round + 2 agreeing served readings — recovered. NOT fix-driven. |

## Fix-driven moves: zero

- **Sticky-banner rule (W18-001) — 0 moves.** No live row's
  verdict depended on a banner challenge.
- **Delivery-code prompt (W18-002) — 0 moves.** No live row
  serves a digit-box code prompt at its root.
- **Declared-sitemap evidence (W18-003) — 0 moves.** Audit
  tool, not the index.
- **Nonempty-loc requirement (W18-004) — 0 moves.** Audit
  tool, not the index.
- **PT-BR/ID/VI/TH phrases (W18-005) — 0 moves.** No live row
  serves a challenge page in those languages.
- **Non-interactive aria-label strip (W18-006) — 0 moves.** No
  live row's verdict depended on a non-interactive label.
- **QR visible-text + size gate (W18-007) — 0 moves, 3 holds.**
  remoteok.com, td.com, and venmo.com all read OPEN under the
  Wave 18 tree — no QR misfire recurs. The holds are
  confirmations, not moves.
- **Spotlights:** ubereats.com reads OPEN under the Wave 18
  tree (the Wave 17 head-strip move holds); rubygems.org reads
  OPEN (the W17-007 passkey fix holds).

The zero-fix-driven-move run resumes: rounds 8–13 moved no live
row correctly, round 14 moved one (ubereats.com), round 15 moves
none. The Wave 19 battery fixes landed after the runner
imported its tree, so they are unmeasured on live traffic until
round 16.

## Merge result

**6 rows changed** (ed.gov, forbes.com, irishjobs.ie,
jobrapido.com, jobs.ie, totaljobs.com) and 4 held (apnews.com,
abc.net.au, lowes.com, npmjs.com). INDEX distribution after
merges: OPEN 419 · CHALLENGED 21 · WALLED 35 · RATE_LIMITED 8 ·
UNREACHABLE 15 · LOGIN_GATED 2 (500 rows, recount verified).
The merged distribution differs from the round-15 raw
distribution by exactly the four holds above. The forbes.com
oscillator note in INDEX.md gained a Wave 19 round-15 update
(the triple that moved the row, and the move-back condition).
