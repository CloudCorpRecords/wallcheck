# Wave 11 — Round-7 fix-driven reclassification (Leg A)

**499/499 rows probed once each** with the CURRENT Wave 10-fixed
classifier — the reclassification Wave 10's STABILITY-5 deferred,
not an inference from stored verdicts (runner
`validation/wave11/run_round7.py`, incremental + resumable saves
to `validation/wave4/history.jsonl` as round=7 and to
`validation/wave11/results-round7.jsonl`). All 499 history lines
parse; zero missing URLs vs the INDEX table.

Classifier-version note (read before comparing rounds): the
runner imports its modules once at start, and it started BEFORE
the Wave 11 battery fixes (W11-001…W11-006) landed. Round 7
therefore measures exactly the Wave 10-fixed classifier — which
is what this leg specified. The Wave 11 fixes are unmeasured on
live traffic until the next round; STABILITY-5's deferred
reclassification is this round's job, and the Wave 11 fixes'
reclassification is the next round's.

Round-7 distribution: OPEN 416 · WALLED 34 · CHALLENGED 24 ·
UNREACHABLE 17 · RATE_LIMITED 7 · LOGIN_GATED 1.

## Flips vs the standing table: 3, all merged

Every flip was hand-checked with a fresh capture before merging —
no flip was merged on the round-7 reading alone.

| target | standing | round 7 | fresh capture | disposition |
| --- | --- | --- | --- | --- |
| www.amazon.com | CHALLENGED / Generic 200 | OPEN 200 | OPEN 200 | MERGED to OPEN. The captcha interstitial sat round 7 out AND the fresh capture out — two agreeing readings. The oscillation is preserved, not smoothed: the row carries note ‡ in INDEX.md (interstitial raised W3, sat out R4/R6, returned R5, sat out R6-held-on-fresh-capture, sat out R7). By Wave 10's own rule the fresh capture decides, and here it agrees with the round. |
| www.britishairways.com | UNREACHABLE (W10 timeout) | OPEN 200 | OPEN 200 | MERGED to OPEN. The Wave 10 timeout reproduced twice then; the site serves again now, twice corroborated. Transport noise resolved, not a wall verdict either way. |
| www.merrilledge.com | OPEN 200 | LOGIN_GATED / Akamai 200 | LOGIN_GATED / Akamai 200, final URL a sitedown notice page | MERGED to LOGIN_GATED. FIX-DRIVEN — the only fix-driven move this round (see below). |

npmjs.com (standing CHALLENGED / Cloudflare) is not a flip:
round 7 read CHALLENGED / Cloudflare 403 and the fresh capture
confirmed it (cf-mitigated + Just a moment + challenge platform).
The wall's posture is not in doubt; its transport manners remain
as noted (†).

## Fix-driven moves: exactly one

Of the four Wave 10 rule families this round was built to
re-measure, only one moved a live row:

- **Redirect-reference (W10-004) — 1 move.** merrilledge.com:
  round 6's pre-Wave-10 classifier read OPEN because the final
  URL is a sitedown notice page, not a login URL, so the old
  login heuristic never fired. The Wave 10 redirect-to-login
  rule fires on the page's declared JS redirect to a login
  widget (`self.location =
  "/publish/ClientLoginUI/SiteDown/SiteDownLoginWidget.htm"`),
  verified in the fetched page body — a genuine login target,
  not a trigger artifact. The site is in a scheduled-downtime
  state whose only path forward is the login widget, so
  LOGIN_GATED is the honest verdict, and Akamai is presence
  attribution (the Wave 6 S5b pattern), not a wall claim.
- **Geo-refusal stubs (W10-001) — 0 moves.** No live index row
  serves a geo-refusal stub; the rule changed no live verdict.
- **Status 451 (W10-002) — 0 moves.** No live index row serves
  a 451.
- **UNREACHABLE vendor reset (W10-006) — 0 verdict moves, by
  design.** The rule changes the vendor field only, and every
  standing UNREACHABLE row already shows vendor "—". No live
  row's verdict moved under it.

That is itself a finding: the Wave 10 fixes were validated
against all 499 live rows, and only one row was actually
misclassified under the old rules. The other three rules are
correctness insurance for shapes the live web has not yet shown
this index — proven by fixtures, unexercised by traffic.

## Merge result

**Three rows changed:** amazon.com CHALLENGED → OPEN,
britishairways.com UNREACHABLE → OPEN, merrilledge.com OPEN →
LOGIN_GATED. New INDEX distribution: OPEN 416 · CHALLENGED 24 ·
WALLED 34 · RATE_LIMITED 7 · UNREACHABLE 17 · LOGIN_GATED 1 (499
rows, recount verified). The merged distribution equals the
round-7 raw distribution exactly — every flip merged, nothing
held — because every flip carried fresh-capture corroboration.
The LOGIN_GATED verdict appears in the index for the first time
as a standing row verdict (round 7's raw distribution already
carried it; the standing table had none).
