# The Bot Wall Index: working document

*wallcheck's running census of how the public web answers a
plainly-identified, non-browser agent: one honest fetch, no
spoofing, no challenge-solving: the answer recorded, never
forced. This is the unpublished working index behind the
campaign (LAUNCH HOLD); it merges every measurement round so far
into one current table.*

**Method in one paragraph.** Each site gets one GET of its public
root from the `wallcheck` user agent (which names itself and the
project). Verdicts: **OPEN** (the real page served), **CHALLENGED**
(a human-check interstitial answered instead), **WALLED** (refused
:  401/403/denied), **LOGIN_GATED** (served only a sign-in),
**RATE_LIMITED** (429), **UNREACHABLE** (the fetch itself failed;
no wall verdict is claimed). The vendor column names the wall
operator when the response carries its signature. Evidence for
every row lives in the wave results files under `validation/`.

**Rounds merged here.** Wave 1 (58 sites, the seed census) as
re-measured by the Wave 3 stability re-probe: 56 of 58 verdicts
identical across rounds; the two flips were target-side churn
(amazon.com raised a captcha gate; npmjs.com's wall intermittently
drops connections) and are documented in
`validation/wave3/STABILITY.md`. Wave 3 expansion (96 sites) is
the first measurement for its rows. Wave 2's per-path findings
(API vs web surface, llms.txt) live in `validation/wave2/PATHS.md`
and are not folded into this root-level table. **Wave 4 round 3**
re-probed all 154: 150 verdicts unchanged; the four flips were all
target-side churn (replit.com and discord.com serve again;
amazon.com's interstitial sat this round out; npmjs.com dropped
the connection a fourth time: held at CHALLENGED per the note
below), documented in `validation/wave4/STABILITY-2.md`, with the
machine-readable history in `validation/wave4/history.jsonl`.
**Wave 5 round 4** re-probed all 154 again: 153 verdicts
identical; the single flip was npmjs.com's connection-drop
pattern a fifth time: held at CHALLENGED per the note below
(`validation/wave5/STABILITY-3.md`, history appended to the same
`history.jsonl`). **Wave 5 expansion** added 104 sites where
agent access matters for real tasks (civic, finance, travel,
health, education, commerce, real estate, jobs-adjacent); five
classifier defects found in the new territory were fixed
test-first and the affected rows re-probed
(`validation/wave5/PROBLEMS.md`). **Wave 6 expansion** added 136
long-tail sites (regional job boards, SaaS, news) and fixed one
vendor-race defect (economist.com); **Wave 7 round 5** re-probed
all 499: 496 verdicts identical; the three flips were all churn
or transport (otta.com and careerbuilder.com timed out once : 
standing verdicts held, since UNREACHABLE claims no verdict;
amazon.com's intermittent captcha interstitial returned after
sitting out two rounds: merged CHALLENGED with its oscillation
documented in `validation/wave7/STABILITY-4.md`). Round 5 also
filled two vendor attributions (npmjs.com → Cloudflare,
realtor.com's 429 → Kasada). **Wave 7 expansion** added 105
sites (regional job boards, SaaS, news, civic, finance, travel,
health, education); one suspected defect (careerjet.com) was
investigated and CORRECTED: the capture's visible text proves a
genuine verification interstitial, so the classifier was right
and no fix was made (`validation/wave7/PROBLEMS.md`, W7-001).
Mid-round, the VM's egress-proxy credential rotated and poisoned
52 consecutive round-5 fetches (timeouts, then proxy 403s);
those rows were removed, archived to
`validation/wave7/results-round5-window.json`, and re-probed
after a fresh-shell restart: the recovery values are the
round-5 record, and `history.jsonl` carries both the failed
attempt lines and the recovery lines for those targets, as
documented in `validation/wave7/STABILITY-4.md`.

**Wave 10 round 6** re-probed all 499: 492 verdicts identical to
the standing table; 7 raw-history flips, of which 5 were
hand-checked with fresh captures: four one-round flaps
(chicagotribune, forbes, webex, amazon's intermittent
interstitial sitting round 6 out) held at their standing verdicts,
and one reproduced transport failure (britishairways.com timed
out in round 6 and again on a fresh capture) merged to
UNREACHABLE; otta.com and careerbuilder.com round-5 timeouts were
already-held transport noise whose standing verdicts round 6
corroborates (`validation/wave10/STABILITY-5.md`).

**Wave 11 round 7** re-probed all 499 with the Wave 10-fixed
classifier (the fix-driven reclassification Wave 10 deferred):
496 verdicts identical to the standing table; 3 flips, all
merged on fresh-capture corroboration: amazon.com's captcha
interstitial sat round 7 out AND the fresh capture out (merged
OPEN, oscillation preserved in note ‡ below), britishairways.com
served 200 in round 7 and again on a fresh capture (merged OPEN,
recovered from the Wave 10 timeout), and merrilledge.com moved
OPEN → LOGIN_GATED, fix-driven by the Wave 10 redirect-to-login
rule (its sitedown page declares a JS redirect to a login
widget, verified in the page body): plus npmjs.com held at
CHALLENGED / Cloudflare on a fresh 403 capture
(`validation/wave11/STABILITY-6.md`).

**500 sites.** Verdicts: OPEN 415 · CHALLENGED 26 · WALLED 36 · RATE_LIMITED 7 · UNREACHABLE 16 · LOGIN_GATED 0. (Wave 12 round 8 moves two rows: amazon.com to CHALLENGED on two agreeing interstitial readings against a round-8 sat-out, britishairways.com to UNREACHABLE on two agreeing timeouts; npmjs.com held CHALLENGED (6th transport-pattern sighting), webex.com held OPEN (a single uncorroborated Akamai 403); no row moved under the Wave 11 classifier rules.) (Wave 13 round 9 moves three rows: britishairways.com to OPEN on two agreeing served readings, merrilledge.com to OPEN on two agreeing served homepages (its Wave 11 login gate is gone: see note below), webex.com to WALLED / Akamai on two agreeing edgesuite denies, the second Akamai sighting after round 8: recount verified; amazon.com held CHALLENGED on two agreeing fresh interstitial readings against a round-9 sat-out; no row moved under the Wave 12 classifier rules.) (Wave 14 round 10 moves one row: todoist.com to OPEN on round-10 plus two agreeing fresh served readings; britishairways.com held OPEN on two agreeing fresh served readings against a round-10 transport failure; kaiserpermanente.org held OPEN/302 on two agreeing fresh redirects against a round-10 200 routing variant; amazon.com and npmjs.com both read agreeing with standing in round 10; no row moved under the Wave 13 classifier rules.) (Wave 15 round 11 moves one row: britishairways.com to UNREACHABLE on round-11 plus two agreeing fresh fetch failures (the mirror of the Wave 14 hold: this time the fresh captures corroborate the failure); forbes.com held OPEN on two agreeing fresh served readings against a round-11 DataDome challenge, with a later spot-check reading CHALLENGED again: forbes is now a documented intermittent oscillator, held at its standing served verdict on a 2-2 split; webex.com held WALLED / Akamai on two agreeing fresh edgesuite denies against a round-11 served reading; amazon.com and npmjs.com both read agreeing with standing in round 11; no row moved under the Wave 14 classifier rules.) (Wave 16 round 12 moves zero rows: 499/499 probed with the Wave 15-fixed classifier (imported at launch, before the Wave 16 battery fixes landed, so the Wave 16 rules are unmeasured until round 13); five verdict diffs, all hand-checked with fresh captures and all held: npmjs.com held CHALLENGED on a fresh 403 against a round-12 connection drop (7th transport-pattern sighting), apnews.com held CHALLENGED the same way (first transport-noise sighting for apnews), france24.com held OPEN on two agreeing served readings against a single round-12 Akamai 403, forbes.com held OPEN on two agreeing served readings against a round-12 DataDome challenge (oscillator record extends), britishairways.com held UNREACHABLE on a 1-1 fresh split (no corroboration triple for either side: the strict rule holds the row, the served-leaning evidence is noted for round 13); four further rows differed only in vendor-cell wording (standing "unattributed (bare 403)" vs round vendor None, same WALLED verdict); no row moved under the Wave 15 classifier rules: the sixth consecutive round with zero fix-driven moves.) (Wave 17 round 13 moves zero rows: 499/499 probed with the Wave 16-fixed classifier; three verdict diffs all held on fresh captures (rubygems.org LOGIN_GATED rejected as a Wave 16 passkey-rule false positive on a served homepage, fixed same wave as W17-007; britishairways.com served-leaning 2-1 held UNREACHABLE; forbes.com challenged-leaning 2-1 held OPEN, oscillator extends); no row moved under the Wave 16 classifier rules.) (Wave 18 round 14 moves five rows: claude.ai to LOGIN_GATED / Cloudflare on round + 2 agreeing login-redirect readings (challenge replaced by a login redirect, target-side); amazon.com to OPEN on round + 2 agreeing served readings (interstitial sat out, note ‡ extends); fda.gov to LOGIN_GATED / Akamai on round + 2 agreeing 401 readings; goodrx.com to OPEN on round + 2 agreeing served readings (PerimeterX wall gone, target-side); ubereats.com to OPEN on round + 2 agreeing served readings: the round's ONLY fix-driven move, under the Wave 17 head-strip rule (the page's only Cloudflare challenge-platform references are CSP host-list entries in <head>); seven diffs held (abc.net.au OPEN, britishairways.com UNREACHABLE, forbes.com OPEN, kroger.com UNREACHABLE on 1-1 fresh splits or overturning fresh readings; remoteok.com, td.com, venmo.com OPEN: three Wave 17 QR-prompt misfires rejected and fixed same wave as W18-007, post-fix re-probes read OPEN); plus row 500, search.brave.com OPEN, in the search section.) (Wave 19 round 15 moves six rows: ed.gov to UNREACHABLE on round + 2 agreeing fetch failures (the britishairways.com Wave 15 pattern: three consecutive failures retire a stale challenged row); forbes.com to CHALLENGED / DataDome on round + 2 agreeing DataDome 403 readings (the merge triple the oscillator's earlier 2-1 splits never met: the oscillator note extends, it does not exempt the row); irishjobs.ie, jobs.ie, and totaljobs.com to OPEN on round + 2 agreeing served readings (three recovered rows); jobrapido.com to RATE_LIMITED on round + 2 agreeing 429 readings; four diffs held (apnews.com CHALLENGED on a 1-1 fresh split: round failure vs fresh challenge, transport noise; abc.net.au OPEN on two agreeing served readings against a round Akamai 403, the Wave 18 hold repeated; lowes.com OPEN on a 1-1 fresh split; npmjs.com CHALLENGED on two agreeing fresh Cloudflare challenges against a round connection drop, the 8th transport-pattern sighting); all five spotlights held (ubereats.com OPEN: the Wave 17 head-strip move holds; remoteok.com, td.com, venmo.com OPEN: no Wave 17 QR misfire recurs under the Wave 18 tree; rubygems.org OPEN: the W17-007 passkey fix holds); no row moved under the Wave 18 classifier rules: the zero-fix-driven-move run resumes after round 14's single move.) (Wave 20 round 16 moves ten rows: claude.ai to CHALLENGED / Cloudflare on round + 2 agreeing 403 challenges (its Wave 18 login gate is replaced by a wall, target-side); amazon.com to CHALLENGED / Generic on round + 2 agreeing interstitial readings (oscillator note ‡ extends; a served triple would move it back); ed.gov to CHALLENGED / Microsoft Azure WAF on round + 2 agreeing 403 readings (answering again after its Wave 19 failure merge); fda.gov to OPEN on round + 2 agreeing served readings (its Wave 18 401 gate is gone: the LOGIN_GATED watch empties); goodrx.com to CHALLENGED / PerimeterX on round + 2 agreeing 403 readings (the Wave 20 iframe-rule flag on its fresh evidence is non-determinative: PX_CAPTCHA/PX_BODY_MARKER drive the verdict, and the round-16 Wave 19-tree reading already agreed); irishjobs.ie, jobs.ie, and totaljobs.com to UNREACHABLE on round + 2 agreeing fetch failures (the Wave 19 OPEN merges reversed: all three down again); jobrapido.com to OPEN on round + 2 agreeing served readings (throttle lifted); ubereats.com to CHALLENGED / Cloudflare on round + 2 agreeing 403 challenges (the Wave 17 head-strip OPEN move is superseded by a live wall, target-side, not a rule move); three diffs held (npmjs.com CHALLENGED on two agreeing fresh Cloudflare challenges against a round connection drop, the 9th transport-pattern sighting; wayfair.com OPEN on two agreeing fresh served readings against a round PerimeterX 429, a transient throttle; webex.com WALLED / Akamai on a 1-1 fresh split: no corroboration triple); spotlights held except ubereats (remoteok.com, td.com, venmo.com OPEN: no QR misfire recurs; rubygems.org OPEN: the W17-007 passkey fix holds; forbes.com CHALLENGED / DataDome holds its Wave 19 merge); no row moved under the Wave 19 classifier rules.) (Wave 21 round 17 moves zero rows: 500/500 probed with the Wave 20-fixed classifier (imported at launch, before the Wave 21 battery fixes landed, so the Wave 21 rules are unmeasured until round 18); four verdict diffs, all hand-checked with fresh captures and all held: apnews.com CHALLENGED on a 1-1 fresh split (round failure vs fresh challenge, transport noise); amazon.com CHALLENGED on two agreeing fresh interstitial readings against a round served reading (oscillator note ‡ extends; a served triple would move it back); npmjs.com CHALLENGED on two agreeing fresh Cloudflare challenges against a round connection drop, the 10th transport-pattern sighting; wayfair.com OPEN on two agreeing fresh served readings against a round PerimeterX 429 (transient throttle, the Wave 20 hold repeated); no row moved under the Wave 20 classifier rules.) (Wave 22 round 18 moves zero rows: 500/500 probed with the Wave 21-fixed classifier (imported at launch, before the Wave 22 battery fixes landed, so the Wave 22 rules are unmeasured until round 19); two verdict diffs, both hand-checked with fresh captures and both held: chicagotribune.com held OPEN on two agreeing fresh served readings against a round 403 (transient refusal); forbes.com held CHALLENGED / DataDome on a 1-1 fresh split (round served reading plus one fresh served reading against one fresh challenge: served-leaning 2-1, no corroboration triple, oscillator record extends); all ten Wave 20 merges agree with round 18; no row moved under the Wave 21 classifier rules.) (Wave 23 round 19 moves two rows: britishairways.com to OPEN on round + 2 agreeing served readings (recovered from its Wave 15 failure merge; the row oscillates on transport, not posture), todoist.com to UNREACHABLE on round + 2 agreeing fetch failures (the same three-consecutive-failures pattern that retired britishairways in round 11); webex.com held WALLED / Akamai on a 1-1 fresh split (one edgesuite deny against one served reading: no corroboration triple, its second split-hold); npmjs.com read CHALLENGED / Cloudflare directly this round (no connection drop) and amazon.com read CHALLENGED / Generic, both agreeing with standing; the two merges cancel in the distribution, which is unchanged; no row moved under the Wave 22 classifier rules: round 19 measured the Wave 22 fixes on live traffic with zero live effect, and no index row answered 418 or 451.) (Wave 24 round 20 moves two rows: wayfair.com to CHALLENGED / PerimeterX on round + 2 agreeing 429 challenge readings (the transient throttle held in rounds 16-17 is now the standing answer across three consecutive readings; a served triple would move it back); apnews.com to UNREACHABLE on round + 2 agreeing fetch failures (the britishairways Wave 15 / ed.gov Wave 19 pattern: three consecutive failures retire a stale challenged row); britishairways.com held OPEN on a 1-1 fresh split (one failure against one served reading: no corroboration triple, its second split-hold after round 12); npmjs.com read CHALLENGED / Cloudflare directly (no connection drop) and amazon.com read CHALLENGED / Generic, both agreeing with standing; no row moved under the Wave 23 classifier rules: round 20 measured the Wave 23 fixes on live traffic with zero live effect (no index row answered 418 or 451 in the round, and no fresh capture carried a picture-block or Greek/Czech/Hungarian/Romanian phrase). Two rows answered 402: telegraph.co.uk and usatoday.com: and read OPEN under the Wave 23 tree; both answer 402 with small refusal stubs on fresh captures and read WALLED under the Wave 24 tree, so round 21 is their measurement round.) (Wave 25 round 21 moves three rows: telegraph.co.uk and usatoday.com to WALLED on round + 2 agreeing 402 readings, both small refusal stubs: the round's TWO fix-driven moves, under the Wave 24 W24-R2 402 rule, the first fix-driven moves since round 14's single move; todoist.com to OPEN on round + 2 agreeing served readings, recovered from its round-19 failure merge; britishairways.com held OPEN on two agreeing fresh served readings against a round transport failure (the Wave 14 hold pattern); npmjs.com read CHALLENGED / Cloudflare and amazon.com read CHALLENGED / Generic, both agreeing with standing; the Wave 24 push-approval and BG/SK/HR/SL fixes measured zero live effect.) (Wave 26 round 22 moves two rows: apnews.com to CHALLENGED / Cloudflare on round + 2 agreeing 403 challenge readings (recovered from its Wave 24 failure merge; round 20's three failures were delivery failures, the challenge was standing behind them); webex.com to OPEN on round + 2 agreeing served readings (its Akamai wall, standing since round 9, has lifted: closing the split round 19 held); forbes.com held CHALLENGED / DataDome on two agreeing fresh DataDome 403 readings against a round served reading (the documented oscillator oscillating: the fresh evidence agrees with standing, not the round); npmjs.com read CHALLENGED / Cloudflare and amazon.com read CHALLENGED / Generic, both agreeing with standing; no row moved under the Wave 25 classifier rules: round 22 measured the Wave 25 fixes on live traffic with zero live effect, and no fresh capture carried an employee-ID prompt, a Serbian / Macedonian / Latvian / Lithuanian phrase, or a placeholder-carried phrase.) (Wave 27 round 23 moves one row: forbes.com to OPEN on round + 2 agreeing served readings, both fresh captures carrying the DataDome header while the page served: the oscillator finally meets the served triple its rounds 11-22 splits never met, reversing its Wave 19 challenge merge; three diffs held (chicagotribune.com OPEN on two agreeing fresh served readings against a round 403: the Wave 18 transient-refusal hold repeated; hilton.com WALLED / Akamai on two agreeing fresh 403 readings against a round fetch failure, transport noise; webex.com OPEN on a 1-1 fresh split: one edgesuite deny against one served reading, no corroboration triple); npmjs.com read CHALLENGED / Cloudflare and amazon.com read CHALLENGED / Generic, both agreeing with standing; no row moved under the Wave 26 classifier rules: round 23 measured the Wave 26 fixes on live traffic with zero live effect, and no fresh capture carried a badge-tap prompt or a Catalan / Estonian / Armenian / Georgian phrase.) (Wave 28 round 24 moves zero rows: 500/500 probed with the Wave 27-fixed classifier (imported at launch, before the Wave 28 battery fixes landed, so the Wave 28 rules are unmeasured until a future round); one verdict diff, hand-checked with fresh captures and held: npmjs.com held CHALLENGED / Cloudflare on a 1-1 fresh split (one fresh Cloudflare challenge against one fresh fetch failure, against the round's connection drop: the 11th transport-pattern sighting, no corroboration triple for either side); amazon.com read CHALLENGED / Generic, agreeing with standing; four rows differed only in vendor-cell wording (standing "unattributed (bare 403)" vs round vendor None, same WALLED verdict and status); no row moved under the Wave 27 classifier rules: round 24 measured the Wave 27 fixes on live traffic with zero live effect.)

Wave 8 path-probed 46 platforms (322 paths) without changing these root rows; see `validation/wave8/PATHS-2.md`.

## freelance (13)

| Site | Verdict | Vendor | Status | Last checked |
|---|---|---|---|---|
| [arc.dev](https://arc.dev) | OPEN |: | 200 | W3 expansion |
| [contra.com](https://contra.com) | OPEN |: | 200 | W3 stability |
| [gun.io](https://gun.io) | WALLED | Cloudflare | 403 | W3 expansion |
| [www.99designs.com](https://www.99designs.com) | OPEN |: | 200 | W3 expansion |
| [www.bark.com](https://www.bark.com) | OPEN |: | 200 | W3 expansion |
| [www.fiverr.com](https://www.fiverr.com) | CHALLENGED | PerimeterX | 403 | W3 stability |
| [www.freelancer.com](https://www.freelancer.com) | OPEN |: | 200 | W3 stability |
| [www.guru.com](https://www.guru.com) | WALLED | Imperva | 403 | W3 stability |
| [www.lemon.io](https://www.lemon.io) | OPEN |: | 200 | W3 expansion |
| [www.peopleperhour.com](https://www.peopleperhour.com) | OPEN |: | 200 | W3 stability |
| [www.thumbtack.com](https://www.thumbtack.com) | OPEN |: | 200 | W3 expansion |
| [www.toptal.com](https://www.toptal.com) | OPEN |: | 200 | W3 stability |
| [www.upwork.com](https://www.upwork.com) | WALLED | Cloudflare | 403 | W3 stability |

## jobs (59)

| Site | Verdict | Vendor | Status | Last checked |
|---|---|---|---|---|
| [builtin.com](https://builtin.com) | OPEN |: | 200 | W3 expansion |
| [otta.com](https://otta.com) | OPEN |: | 200 | W3 expansion |
| [remoteok.com](https://remoteok.com) | OPEN |: | 200 | W3 stability |
| [wellfound.com](https://wellfound.com) | OPEN |: | 200 | W3 stability |
| [weworkremotely.com](https://weworkremotely.com) | OPEN |: | 200 | W3 expansion |
| [www.careerbuilder.com](https://www.careerbuilder.com) | CHALLENGED | DataDome | 403 | W5 expansion |
| [www.dice.com](https://www.dice.com) | OPEN |: | 200 | W3 stability |
| [www.flexjobs.com](https://www.flexjobs.com) | UNREACHABLE |: |: | W3 expansion |
| [www.glassdoor.com](https://www.glassdoor.com) | OPEN |: | 200 | W3 stability |
| [www.himalayas.app](https://www.himalayas.app) | OPEN |: | 200 | W3 expansion |
| [www.indeed.com](https://www.indeed.com) | OPEN |: | 200 | W3 stability |
| [www.levels.fyi](https://www.levels.fyi) | OPEN |: | 200 | W3 expansion |
| [www.linkedin.com](https://www.linkedin.com) | OPEN |: | 200 | W3 stability |
| [www.monster.com](https://www.monster.com) | CHALLENGED | DataDome | 403 | W3 stability |
| [www.salary.com](https://www.salary.com) | OPEN |: | 200 | W5 expansion |
| [www.simplyhired.com](https://www.simplyhired.com) | OPEN |: | 200 | W5 expansion |
| [www.snagajob.com](https://www.snagajob.com) | OPEN |: | 200 | W5 expansion |
| [www.themuse.com](https://www.themuse.com) | OPEN |: | 200 | W5 expansion |
| [www.workingnomads.com](https://www.workingnomads.com) | OPEN |: | 200 | W3 expansion |
| [www.ycombinator.com](https://www.ycombinator.com) | OPEN |: | 200 | W3 expansion |
| [www.ziprecruiter.com](https://www.ziprecruiter.com) | OPEN |: | 200 | W3 stability |
| [remotive.com](https://remotive.com) | OPEN |: | 200 | W6 expansion |
| [jobspresso.co](https://jobspresso.co) | OPEN |: | 200 | W6 expansion |
| [authenticjobs.com](https://authenticjobs.com) | OPEN |: | 200 | W6 expansion |
| [theladders.com](https://theladders.com) | OPEN |: | 200 | W6 expansion |
| [hired.com](https://hired.com) | OPEN |: | 200 | W6 expansion |
| [powertofly.com](https://powertofly.com) | OPEN |: | 200 | W6 expansion |
| [idealist.org](https://idealist.org) | OPEN |: | 200 | W6 expansion |
| [coolworks.com](https://coolworks.com) | OPEN |: | 200 | W6 expansion |
| [www.instawork.com](https://www.instawork.com) | OPEN |: | 200 | W6 expansion |
| [wonolo.com](https://wonolo.com) | OPEN |: | 200 | W6 expansion |
| [www.jobcase.com](https://www.jobcase.com) | OPEN |: | 200 | W6 expansion |
| [talent.com](https://talent.com) | OPEN |: | 200 | W6 expansion |
| [www.adzuna.com](https://www.adzuna.com) | WALLED | AWS CloudFront | 403 | W6 expansion |
| [www.totaljobs.com](https://www.totaljobs.com) | UNREACHABLE |: |: | W20 round-16 |
| [www.reed.co.uk](https://www.reed.co.uk) | OPEN |: | 200 | W6 expansion |
| [www.seek.com.au](https://www.seek.com.au) | OPEN |: | 200 | W6 expansion |
| [www.mediabistro.com](https://www.mediabistro.com) | OPEN |: | 200 | W6 expansion |
| [www.journalismjobs.com](https://www.journalismjobs.com) | OPEN |: | 200 | W6 expansion |
| [www.careerjet.com](https://www.careerjet.com) | CHALLENGED | Cloudflare | 200 | W7 expansion |
| [www.jooble.org](https://www.jooble.org) | OPEN |: | 200 | W7 expansion |
| [www.monster.ca](https://www.monster.ca) | CHALLENGED | DataDome | 403 | W7 expansion |
| [www.jobrapido.com](https://www.jobrapido.com) | OPEN |: | 200 | W20 round-16 |
| [www.neuvoo.ca](https://www.neuvoo.ca) | OPEN |: | 404 | W7 expansion |
| [www.careerbuilder.ca](https://www.careerbuilder.ca) | CHALLENGED | DataDome | 403 | W7 expansion |
| [www.workopolis.com](https://www.workopolis.com) | OPEN |: | 200 | W7 expansion |
| [www.jobbank.gc.ca](https://www.jobbank.gc.ca) | OPEN |: | 200 | W7 expansion |
| [www.glassdoor.ca](https://www.glassdoor.ca) | OPEN |: | 200 | W7 expansion |
| [www.irishjobs.ie](https://www.irishjobs.ie) | UNREACHABLE |: |: | W20 round-16 |
| [www.jobs.ie](https://www.jobs.ie) | UNREACHABLE |: |: | W20 round-16 |
| [www.stepstone.de](https://www.stepstone.de) | OPEN |: | 200 | W7 expansion |
| [www.xing.com](https://www.xing.com) | OPEN |: | 200 | W7 expansion |
| [www.jobteaser.com](https://www.jobteaser.com) | OPEN |: | 200 | W7 expansion |
| [www.hellowork.com](https://www.hellowork.com) | OPEN |: | 200 | W7 expansion |
| [www.pole-emploi.fr](https://www.pole-emploi.fr) | OPEN |: | 200 | W7 expansion |
| [www.infojobs.net](https://www.infojobs.net) | OPEN |: | 405 | W7 expansion |
| [www.computrabajo.com](https://www.computrabajo.com) | OPEN |: | 200 | W7 expansion |
| [www.bumeran.com](https://www.bumeran.com) | OPEN |: | 200 | W7 expansion |
| [www.catho.com.br](https://www.catho.com.br) | WALLED | unattributed (bare 403) | 403 | W7 expansion |
## dev (12)

| Site | Verdict | Vendor | Status | Last checked |
|---|---|---|---|---|
| [bitbucket.org](https://bitbucket.org) | OPEN |: | 200 | W3 stability |
| [github.com](https://github.com) | OPEN |: | 200 | W3 stability |
| [gitlab.com](https://gitlab.com) | OPEN |: | 200 | W3 stability |
| [hub.docker.com](https://hub.docker.com) | OPEN |: | 200 | W3 stability |
| [huggingface.co](https://huggingface.co) | OPEN |: | 200 | W3 stability |
| [pypi.org](https://pypi.org) | OPEN |: | 200 | W3 stability |
| [replit.com](https://replit.com) | OPEN |: | 200 | W4 history |
| [sourceforge.net](https://sourceforge.net) | OPEN |: | 200 | W3 stability |
| [stackoverflow.com](https://stackoverflow.com) | OPEN |: | 200 | W3 stability |
| [vercel.com](https://vercel.com) | OPEN |: | 200 | W3 stability |
| [www.netlify.com](https://www.netlify.com) | OPEN |: | 200 | W3 stability |
| [www.npmjs.com](https://www.npmjs.com): see note † | CHALLENGED | Cloudflare | 403 | W7 round-5 |

## social (9)

| Site | Verdict | Vendor | Status | Last checked |
|---|---|---|---|---|
| [discord.com](https://discord.com) | OPEN |: | 200 | W4 history |
| [www.facebook.com](https://www.facebook.com) | OPEN |: | 200 | W3 stability |
| [www.instagram.com](https://www.instagram.com) | OPEN |: | 200 | W3 stability |
| [www.reddit.com](https://www.reddit.com) | OPEN |: | 200 | W3 stability |
| [www.threads.com](https://www.threads.com) | OPEN |: | 200 | W3 stability |
| [www.tiktok.com](https://www.tiktok.com) | OPEN |: | 200 | W3 stability |
| [www.twitch.tv](https://www.twitch.tv) | OPEN |: | 200 | W3 stability |
| [www.youtube.com](https://www.youtube.com) | OPEN |: | 200 | W3 stability |
| [x.com](https://x.com) | OPEN |: | 200 | W3 stability |

## docs-news (9)

| Site | Verdict | Vendor | Status | Last checked |
|---|---|---|---|---|
| [arstechnica.com](https://arstechnica.com) | OPEN |: | 200 | W3 stability |
| [dev.to](https://dev.to) | OPEN |: | 200 | W3 stability |
| [en.wikipedia.org](https://en.wikipedia.org) | OPEN |: | 200 | W3 stability |
| [medium.com](https://medium.com) | WALLED | Cloudflare | 403 | W3 stability |
| [news.ycombinator.com](https://news.ycombinator.com) | OPEN |: | 200 | W3 stability |
| [substack.com](https://substack.com) | OPEN |: | 200 | W3 stability |
| [techcrunch.com](https://techcrunch.com) | OPEN |: | 200 | W3 stability |
| [www.bbc.com](https://www.bbc.com) | OPEN |: | 200 | W3 stability |
| [www.nytimes.com](https://www.nytimes.com) | CHALLENGED | DataDome | 403 | W3 stability |

## big-web (10)

| Site | Verdict | Vendor | Status | Last checked |
|---|---|---|---|---|
| [www.amazon.com](https://www.amazon.com): see note ‡ | CHALLENGED | Generic | 200 | W20 round-16 |
| [www.apple.com](https://www.apple.com) | OPEN |: | 200 | W3 stability |
| [www.bestbuy.com](https://www.bestbuy.com) | UNREACHABLE |: |: | W3 stability |
| [www.cloudflare.com](https://www.cloudflare.com) | OPEN |: | 200 | W3 stability |
| [www.ebay.com](https://www.ebay.com) | WALLED | Akamai | 403 | W3 stability |
| [www.google.com](https://www.google.com) | OPEN |: | 200 | W3 stability |
| [www.microsoft.com](https://www.microsoft.com) | OPEN |: | 200 | W3 stability |
| [www.netflix.com](https://www.netflix.com) | OPEN |: | 200 | W3 stability |
| [www.target.com](https://www.target.com) | OPEN |: | 200 | W3 stability |
| [www.walmart.com](https://www.walmart.com) | OPEN |: | 200 | W3 stability |

## own (3)

| Site | Verdict | Vendor | Status | Last checked |
|---|---|---|---|---|
| [clipwise.replit.app](https://clipwise.replit.app) | OPEN |: | 200 | W3 stability |
| [cloudcorprecords.github.io](https://cloudcorprecords.github.io) | OPEN |: | 404 | W3 stability |
| [reneturcios.replit.app](https://reneturcios.replit.app) | OPEN |: | 200 | W3 stability |

## dev-infra (24)

| Site | Verdict | Vendor | Status | Last checked |
|---|---|---|---|---|
| [anaconda.org](https://anaconda.org) | OPEN |: | 200 | W3 expansion |
| [aws.amazon.com](https://aws.amazon.com) | OPEN |: | 200 | W3 expansion |
| [azure.microsoft.com](https://azure.microsoft.com) | OPEN |: | 200 | W3 expansion |
| [bun.sh](https://bun.sh) | OPEN |: | 200 | W3 expansion |
| [cloud.google.com](https://cloud.google.com) | OPEN |: | 200 | W3 expansion |
| [codeberg.org](https://codeberg.org) | OPEN |: | 200 | W3 expansion |
| [crates.io](https://crates.io) | OPEN |: | 404 | W3 expansion |
| [deno.com](https://deno.com) | OPEN |: | 200 | W3 expansion |
| [firebase.google.com](https://firebase.google.com) | OPEN |: | 200 | W3 expansion |
| [fly.io](https://fly.io) | OPEN |: | 200 | W3 expansion |
| [hex.pm](https://hex.pm) | OPEN |: | 200 | W3 expansion |
| [packagist.org](https://packagist.org) | OPEN |: | 200 | W3 expansion |
| [pkg.go.dev](https://pkg.go.dev) | OPEN |: | 200 | W3 expansion |
| [pub.dev](https://pub.dev) | OPEN |: | 200 | W3 expansion |
| [railway.app](https://railway.app) | OPEN |: | 200 | W3 expansion |
| [registry.terraform.io](https://registry.terraform.io) | OPEN |: | 200 | W3 expansion |
| [render.com](https://render.com) | OPEN |: | 200 | W3 expansion |
| [repo.maven.apache.org](https://repo.maven.apache.org) | OPEN |: | 200 | W3 expansion |
| [rubygems.org](https://rubygems.org) | OPEN |: | 200 | W3 expansion |
| [supabase.com](https://supabase.com) | OPEN |: | 200 | W3 expansion |
| [www.digitalocean.com](https://www.digitalocean.com) | OPEN |: | 200 | W3 expansion |
| [www.heroku.com](https://www.heroku.com) | OPEN |: | 200 | W3 expansion |
| [www.linode.com](https://www.linode.com) | OPEN |: | 200 | W3 expansion |
| [www.nuget.org](https://www.nuget.org) | OPEN |: | 200 | W3 expansion |

## ai (15)

| Site | Verdict | Vendor | Status | Last checked |
|---|---|---|---|---|
| [ai.google.dev](https://ai.google.dev) | OPEN |: | 200 | W3 expansion |
| [chatgpt.com](https://chatgpt.com) | OPEN |: | 200 | W3 expansion |
| [claude.ai](https://claude.ai) | CHALLENGED | Cloudflare | 403 | W20 round-16 |
| [cohere.com](https://cohere.com) | OPEN |: | 200 | W3 expansion |
| [deepmind.google](https://deepmind.google) | OPEN |: | 200 | W3 expansion |
| [groq.com](https://groq.com) | OPEN |: | 200 | W3 expansion |
| [mistral.ai](https://mistral.ai) | OPEN |: | 200 | W3 expansion |
| [ollama.com](https://ollama.com) | OPEN |: | 200 | W3 expansion |
| [openai.com](https://openai.com) | OPEN |: | 200 | W3 expansion |
| [replicate.com](https://replicate.com) | OPEN |: | 200 | W3 expansion |
| [runwayml.com](https://runwayml.com) | OPEN |: | 200 | W3 expansion |
| [stability.ai](https://stability.ai) | OPEN |: | 200 | W3 expansion |
| [together.ai](https://together.ai) | OPEN |: | 200 | W3 expansion |
| [www.anthropic.com](https://www.anthropic.com) | OPEN |: | 200 | W3 expansion |
| [www.perplexity.ai](https://www.perplexity.ai) | OPEN |: | 200 | W3 expansion |

## commerce (25)

| Site | Verdict | Vendor | Status | Last checked |
|---|---|---|---|---|
| [gumroad.com](https://gumroad.com) | OPEN |: | 200 | W3 expansion |
| [sellercentral.amazon.com](https://sellercentral.amazon.com) | OPEN |: | 200 | W3 expansion |
| [stripe.com](https://stripe.com) | OPEN |: | 200 | W3 expansion |
| [woocommerce.com](https://woocommerce.com) | OPEN |: | 200 | W3 expansion |
| [www.bigcommerce.com](https://www.bigcommerce.com) | OPEN |: | 200 | W3 expansion |
| [www.chewy.com](https://www.chewy.com) | RATE_LIMITED | Kasada | 429 | W5 expansion |
| [www.costco.com](https://www.costco.com) | OPEN |: | 200 | W5 expansion |
| [www.doordash.com](https://www.doordash.com) | OPEN |: | 200 | W5 expansion |
| [www.etsy.com](https://www.etsy.com) | CHALLENGED | DataDome | 403 | W3 expansion |
| [www.homedepot.com](https://www.homedepot.com) | WALLED | Akamai | 403 | W5 expansion |
| [www.ikea.com](https://www.ikea.com) | OPEN |: | 200 | W5 expansion |
| [www.instacart.com](https://www.instacart.com) | OPEN |: | 200 | W5 expansion |
| [www.kroger.com](https://www.kroger.com) | UNREACHABLE |: |: | W5 expansion |
| [www.lowes.com](https://www.lowes.com) | OPEN |: | 200 | W5 expansion |
| [www.macys.com](https://www.macys.com) | WALLED | Akamai | 403 | W5 expansion |
| [www.mercari.com](https://www.mercari.com) | OPEN |: | 200 | W5 expansion |
| [www.nike.com](https://www.nike.com) | OPEN |: | 200 | W5 expansion |
| [www.nordstrom.com](https://www.nordstrom.com) | OPEN |: | 200 | W5 expansion |
| [www.offerup.com](https://www.offerup.com) | OPEN |: | 200 | W5 expansion |
| [www.poshmark.com](https://www.poshmark.com) | OPEN |: | 200 | W5 expansion |
| [www.shopify.com](https://www.shopify.com) | OPEN |: | 200 | W3 expansion |
| [www.squarespace.com](https://www.squarespace.com) | OPEN |: | 200 | W3 expansion |
| [www.ubereats.com](https://www.ubereats.com) | CHALLENGED | Cloudflare | 403 | W20 round-16 |
| [www.wayfair.com](https://www.wayfair.com) | CHALLENGED | PerimeterX | 429 | W24 round-20 |
| [www.wix.com](https://www.wix.com) | OPEN |: | 200 | W3 expansion |

## media-forums (14)

| Site | Verdict | Vendor | Status | Last checked |
|---|---|---|---|---|
| [bsky.app](https://bsky.app) | OPEN |: | 200 | W3 expansion |
| [mastodon.social](https://mastodon.social) | OPEN |: | 200 | W3 expansion |
| [slack.com](https://slack.com) | OPEN |: | 200 | W3 expansion |
| [soundcloud.com](https://soundcloud.com) | OPEN |: | 200 | W3 expansion |
| [vimeo.com](https://vimeo.com) | OPEN |: | 200 | W3 expansion |
| [www.eventbrite.com](https://www.eventbrite.com) | OPEN |: | 200 | W3 expansion |
| [www.kickstarter.com](https://www.kickstarter.com) | OPEN |: | 200 | W3 expansion |
| [www.meetup.com](https://www.meetup.com) | OPEN |: | 200 | W3 expansion |
| [www.patreon.com](https://www.patreon.com) | OPEN |: | 200 | W3 expansion |
| [www.pinterest.com](https://www.pinterest.com) | OPEN |: | 200 | W3 expansion |
| [www.producthunt.com](https://www.producthunt.com) | OPEN |: | 200 | W3 expansion |
| [www.quora.com](https://www.quora.com) | OPEN |: | 200 | W3 expansion |
| [www.spotify.com](https://www.spotify.com) | OPEN |: | 200 | W3 expansion |
| [zoom.com](https://zoom.com) | OPEN |: | 200 | W3 expansion |

## reference (9)

| Site | Verdict | Vendor | Status | Last checked |
|---|---|---|---|---|
| [archive.org](https://archive.org) | OPEN |: | 200 | W3 expansion |
| [arxiv.org](https://arxiv.org) | OPEN |: | 200 | W3 expansion |
| [developer.mozilla.org](https://developer.mozilla.org) | OPEN |: | 200 | W3 expansion |
| [readthedocs.org](https://readthedocs.org) | OPEN |: | 200 | W3 expansion |
| [www.coursera.org](https://www.coursera.org) | OPEN |: | 200 | W3 expansion |
| [www.gutenberg.org](https://www.gutenberg.org) | OPEN |: | 200 | W3 expansion |
| [www.khanacademy.org](https://www.khanacademy.org) | OPEN |: | 200 | W3 expansion |
| [www.udemy.com](https://www.udemy.com) | OPEN |: | 200 | W3 expansion |
| [www.w3schools.com](https://www.w3schools.com) | WALLED | Akamai | 403 | W3 expansion |

## news (78)

| Site | Verdict | Vendor | Status | Last checked |
|---|---|---|---|---|
| [www.bloomberg.com](https://www.bloomberg.com) | OPEN |: | 200 | W3 expansion |
| [www.reuters.com](https://www.reuters.com) | CHALLENGED | DataDome | 401 | W3 expansion |
| [www.theguardian.com](https://www.theguardian.com) | OPEN |: | 200 | W3 expansion |
| [www.theverge.com](https://www.theverge.com) | OPEN |: | 200 | W3 expansion |
| [www.wired.com](https://www.wired.com) | OPEN |: | 200 | W3 expansion |
| [www.wsj.com](https://www.wsj.com) | CHALLENGED | DataDome | 401 | W3 expansion |
| [www.vox.com](https://www.vox.com) | OPEN |: | 200 | W6 expansion |
| [www.engadget.com](https://www.engadget.com) | OPEN |: | 200 | W6 expansion |
| [gizmodo.com](https://gizmodo.com) | OPEN |: | 200 | W6 expansion |
| [kotaku.com](https://kotaku.com) | OPEN |: | 200 | W6 expansion |
| [www.polygon.com](https://www.polygon.com) | OPEN |: | 200 | W6 expansion |
| [www.gamespot.com](https://www.gamespot.com) | OPEN |: | 200 | W6 expansion |
| [www.ign.com](https://www.ign.com) | OPEN |: | 200 | W6 expansion |
| [www.pcgamer.com](https://www.pcgamer.com) | OPEN |: | 200 | W6 expansion |
| [www.eurogamer.net](https://www.eurogamer.net) | OPEN |: | 200 | W6 expansion |
| [pitchfork.com](https://pitchfork.com) | OPEN |: | 200 | W6 expansion |
| [www.rollingstone.com](https://www.rollingstone.com) | OPEN |: | 200 | W6 expansion |
| [www.billboard.com](https://www.billboard.com) | OPEN |: | 200 | W6 expansion |
| [variety.com](https://variety.com) | OPEN |: | 200 | W6 expansion |
| [www.hollywoodreporter.com](https://www.hollywoodreporter.com) | OPEN |: | 200 | W6 expansion |
| [deadline.com](https://deadline.com) | OPEN |: | 200 | W6 expansion |
| [www.indiewire.com](https://www.indiewire.com) | OPEN |: | 200 | W6 expansion |
| [www.vulture.com](https://www.vulture.com) | OPEN |: | 200 | W6 expansion |
| [slate.com](https://slate.com) | OPEN |: | 200 | W6 expansion |
| [www.salon.com](https://www.salon.com) | OPEN |: | 200 | W6 expansion |
| [www.independent.co.uk](https://www.independent.co.uk) | OPEN |: | 200 | W6 expansion |
| [www.telegraph.co.uk](https://www.telegraph.co.uk) | WALLED |: | 402 | W25 round-21 |
| [www.ft.com](https://www.ft.com) | CHALLENGED | Cloudflare | 403 | W6 expansion |
| [www.latimes.com](https://www.latimes.com) | OPEN |: | 200 | W6 expansion |
| [www.chicagotribune.com](https://www.chicagotribune.com) | OPEN |: | 200 | W6 expansion |
| [www.bostonglobe.com](https://www.bostonglobe.com) | OPEN |: | 200 | W6 expansion |
| [www.sfgate.com](https://www.sfgate.com) | OPEN |: | 200 | W6 expansion |
| [www.sfchronicle.com](https://www.sfchronicle.com) | OPEN |: | 200 | W6 expansion |
| [nypost.com](https://nypost.com) | OPEN |: | 200 | W6 expansion |
| [www.usatoday.com](https://www.usatoday.com) | WALLED |: | 402 | W25 round-21 |
| [www.axios.com](https://www.axios.com) | OPEN |: | 200 | W6 expansion |
| [www.politico.com](https://www.politico.com) | OPEN |: | 200 | W6 expansion |
| [thehill.com](https://thehill.com) | OPEN |: | 200 | W6 expansion |
| [www.huffpost.com](https://www.huffpost.com) | OPEN |: | 200 | W6 expansion |
| [www.buzzfeed.com](https://www.buzzfeed.com) | OPEN |: | 200 | W6 expansion |
| [www.businessinsider.com](https://www.businessinsider.com) | OPEN |: | 200 | W6 expansion |
| [www.fastcompany.com](https://www.fastcompany.com) | CHALLENGED | DataDome | 403 | W6 expansion |
| [www.inc.com](https://www.inc.com) | CHALLENGED | DataDome | 403 | W6 expansion |
| [www.entrepreneur.com](https://www.entrepreneur.com) | OPEN |: | 200 | W6 expansion |
| [fortune.com](https://fortune.com) | OPEN |: | 200 | W6 expansion |
| [www.economist.com](https://www.economist.com) | CHALLENGED | DataDome | 403 | W6 expansion |
| [apnews.com](https://apnews.com) | CHALLENGED | Cloudflare | 403 | W26 round-22 |
| [www.pbs.org](https://www.pbs.org) | OPEN |: | 200 | W6 expansion |
| [www.aljazeera.com](https://www.aljazeera.com) | OPEN |: | 200 | W6 expansion |
| [www.dw.com](https://www.dw.com) | OPEN |: | 200 | W6 expansion |
| [www.france24.com](https://www.france24.com) | OPEN |: | 200 | W6 expansion |
| [www.scmp.com](https://www.scmp.com) | WALLED | Cloudflare | 403 | W6 expansion |
| [www.straitstimes.com](https://www.straitstimes.com) | OPEN |: | 200 | W6 expansion |
| [www.japantimes.co.jp](https://www.japantimes.co.jp) | OPEN |: | 200 | W6 expansion |
| [www.techmeme.com](https://www.techmeme.com) | OPEN |: | 200 | W6 expansion |
| [www.theinformation.com](https://www.theinformation.com) | OPEN |: | 200 | W6 expansion |
| [www.semafor.com](https://www.semafor.com) | OPEN |: | 200 | W6 expansion |
| [www.404media.co](https://www.404media.co) | OPEN |: | 200 | W6 expansion |
| [defector.com](https://defector.com) | OPEN |: | 200 | W6 expansion |
| [www.thecut.com](https://www.thecut.com) | OPEN |: | 200 | W6 expansion |
| [www.npr.org](https://www.npr.org) | OPEN |: | 200 | W6 expansion |
| [www.theatlantic.com](https://www.theatlantic.com) | WALLED | Cloudflare | 403 | W6 expansion |
| [www.newyorker.com](https://www.newyorker.com) | OPEN |: | 200 | W6 expansion |
| [www.cnn.com](https://www.cnn.com) | OPEN |: | 200 | W7 expansion |
| [www.washingtonpost.com](https://www.washingtonpost.com) | UNREACHABLE |: |: | W7 expansion |
| [www.cnbc.com](https://www.cnbc.com) | OPEN |: | 200 | W7 expansion |
| [www.forbes.com](https://www.forbes.com) | OPEN |: | 200 | W27 round-23 |
| [www.euronews.com](https://www.euronews.com) | OPEN |: | 200 | W7 expansion |
| [news.sky.com](https://news.sky.com) | WALLED | Akamai | 403 | W7 expansion |
| [www.cbc.ca](https://www.cbc.ca) | UNREACHABLE |: |: | W7 expansion |
| [www.abc.net.au](https://www.abc.net.au) | OPEN |: | 200 | W7 expansion |
| [www.stuff.co.nz](https://www.stuff.co.nz) | OPEN |: | 200 | W7 expansion |
| [www.nzherald.co.nz](https://www.nzherald.co.nz) | OPEN |: | 200 | W7 expansion |
| [www.koreaherald.com](https://www.koreaherald.com) | OPEN |: | 200 | W7 expansion |
| [www.hindustantimes.com](https://www.hindustantimes.com) | OPEN |: | 200 | W7 expansion |
| [timesofindia.indiatimes.com](https://timesofindia.indiatimes.com) | OPEN |: | 200 | W7 expansion |
| [www.dawn.com](https://www.dawn.com) | OPEN |: | 200 | W7 expansion |
| [www.haaretz.com](https://www.haaretz.com) | WALLED | unattributed (bare 403) | 403 | W7 expansion |
## travel (33)

| Site | Verdict | Vendor | Status | Last checked |
|---|---|---|---|---|
| [www.airbnb.com](https://www.airbnb.com) | OPEN |: | 200 | W3 expansion |
| [www.alaskaair.com](https://www.alaskaair.com) | OPEN |: | 200 | W5 expansion |
| [www.americanairlines.com](https://www.americanairlines.com) | WALLED | Akamai | 403 | W5 expansion |
| [www.amtrak.com](https://www.amtrak.com) | WALLED | Akamai | 403 | W5 expansion |
| [www.booking.com](https://www.booking.com) | CHALLENGED | AWS WAF | 202 | W3 expansion |
| [www.delta.com](https://www.delta.com) | WALLED | Akamai | 444 | W5 expansion |
| [www.expedia.com](https://www.expedia.com) | RATE_LIMITED |: | 429 | W3 expansion |
| [www.hilton.com](https://www.hilton.com) | WALLED | Akamai | 403 | W5 expansion |
| [www.hotels.com](https://www.hotels.com) | RATE_LIMITED |: | 429 | W5 expansion |
| [www.hyatt.com](https://www.hyatt.com) | WALLED | unattributed (bare 403) | 403 | W5 expansion |
| [www.jetblue.com](https://www.jetblue.com) | OPEN |: | 200 | W5 expansion |
| [www.kayak.com](https://www.kayak.com) | OPEN |: | 200 | W5 expansion |
| [www.lyft.com](https://www.lyft.com) | OPEN |: | 200 | W5 expansion |
| [www.marriott.com](https://www.marriott.com) | WALLED | Akamai | 403 | W5 expansion |
| [www.priceline.com](https://www.priceline.com) | OPEN |: | 200 | W5 expansion |
| [www.southwest.com](https://www.southwest.com) | OPEN |: | 200 | W5 expansion |
| [www.uber.com](https://www.uber.com) | OPEN |: | 200 | W5 expansion |
| [www.united.com](https://www.united.com) | UNREACHABLE |: |: | W5 expansion |
| [www.vrbo.com](https://www.vrbo.com) | RATE_LIMITED |: | 429 | W5 expansion |
| [www.skyscanner.com](https://www.skyscanner.com) | OPEN |: | 200 | W7 expansion |
| [www.orbitz.com](https://www.orbitz.com) | RATE_LIMITED |: | 429 | W7 expansion |
| [www.travelocity.com](https://www.travelocity.com) | RATE_LIMITED |: | 429 | W7 expansion |
| [www.tripadvisor.com](https://www.tripadvisor.com) | CHALLENGED | DataDome | 403 | W7 expansion |
| [www.lonelyplanet.com](https://www.lonelyplanet.com) | OPEN |: | 200 | W7 expansion |
| [www.viator.com](https://www.viator.com) | CHALLENGED | DataDome | 403 | W7 expansion |
| [www.getyourguide.com](https://www.getyourguide.com) | UNREACHABLE |: |: | W7 expansion |
| [www.ryanair.com](https://www.ryanair.com) | OPEN |: | 200 | W7 expansion |
| [www.easyjet.com](https://www.easyjet.com) | WALLED | Akamai | 403 | W7 expansion |
| [www.lufthansa.com](https://www.lufthansa.com) | OPEN |: | 200 | W7 expansion |
| [www.britishairways.com](https://www.britishairways.com) | OPEN |: | 200 | W23 round-19 |
| [www.airfrance.com](https://www.airfrance.com) | UNREACHABLE |: |: | W7 expansion |
| [www.klm.com](https://www.klm.com) | UNREACHABLE |: |: | W7 expansion |
| [www.emirates.com](https://www.emirates.com) | WALLED | Akamai | 403 | W7 expansion |

## search (3)

| Site | Verdict | Vendor | Status | Last checked |
|---|---|---|---|---|
| [duckduckgo.com](https://duckduckgo.com) | OPEN |: | 200 | W3 expansion |
| [www.bing.com](https://www.bing.com) | OPEN |: | 200 | W3 expansion |
| [search.brave.com](https://search.brave.com) | OPEN |: | 200 | W18 row-500 |

## civic (33)

| Site | Verdict | Vendor | Status | Last checked |
|---|---|---|---|---|
| [www.benefits.gov](https://www.benefits.gov) | OPEN |: | 200 | W5 expansion |
| [www.ca.gov](https://www.ca.gov) | OPEN |: | 200 | W5 expansion |
| [www.consumerfinance.gov](https://www.consumerfinance.gov) | OPEN |: | 200 | W5 expansion |
| [www.ed.gov](https://www.ed.gov) | CHALLENGED | Microsoft Azure WAF | 403 | W20 round-16 |
| [www.ftc.gov](https://www.ftc.gov) | WALLED | Akamai | 403 | W5 expansion |
| [www.grants.gov](https://www.grants.gov) | OPEN |: | 200 | W5 expansion |
| [www.healthcare.gov](https://www.healthcare.gov) | OPEN |: | 200 | W5 expansion |
| [www.irs.gov](https://www.irs.gov) | OPEN |: | 200 | W5 expansion |
| [www.nyc.gov](https://www.nyc.gov) | WALLED | Akamai | 403 | W5 expansion |
| [www.sf.gov](https://www.sf.gov) | OPEN |: | 200 | W5 expansion |
| [www.ssa.gov](https://www.ssa.gov) | WALLED | Akamai | 403 | W5 expansion |
| [www.state.gov](https://www.state.gov) | WALLED | unattributed (bare 403) | 403 | W5 expansion |
| [www.treasury.gov](https://www.treasury.gov) | OPEN |: | 200 | W5 expansion |
| [www.usa.gov](https://www.usa.gov) | OPEN |: | 200 | W5 expansion |
| [www.usajobs.gov](https://www.usajobs.gov) | OPEN |: | 200 | W5 expansion |
| [www.usps.com](https://www.usps.com) | OPEN |: | 200 | W5 expansion |
| [www.va.gov](https://www.va.gov) | OPEN |: | 200 | W5 expansion |
| [www.vote.gov](https://www.vote.gov) | OPEN |: | 200 | W5 expansion |
| [www.weather.gov](https://www.weather.gov) | OPEN |: | 200 | W5 expansion |
| [www.medicare.gov](https://www.medicare.gov) | OPEN |: | 200 | W7 expansion |
| [www.sec.gov](https://www.sec.gov) | WALLED | Akamai | 403 | W7 expansion |
| [www.federalreserve.gov](https://www.federalreserve.gov) | OPEN |: | 200 | W7 expansion |
| [www.bls.gov](https://www.bls.gov) | WALLED | Akamai | 403 | W7 expansion |
| [www.census.gov](https://www.census.gov) | OPEN |: | 200 | W7 expansion |
| [www.nasa.gov](https://www.nasa.gov) | OPEN |: | 200 | W7 expansion |
| [www.loc.gov](https://www.loc.gov) | OPEN |: | 200 | W7 expansion |
| [www.whitehouse.gov](https://www.whitehouse.gov) | OPEN |: | 200 | W7 expansion |
| [www.congress.gov](https://www.congress.gov) | OPEN |: | 200 | W7 expansion |
| [www.supremecourt.gov](https://www.supremecourt.gov) | OPEN |: | 200 | W7 expansion |
| [www.dhs.gov](https://www.dhs.gov) | OPEN |: | 200 | W7 expansion |
| [www.doj.gov](https://www.doj.gov) | UNREACHABLE |: |: | W7 expansion |
| [www.epa.gov](https://www.epa.gov) | OPEN |: | 200 | W7 expansion |
| [www.energy.gov](https://www.energy.gov) | OPEN |: | 200 | W7 expansion |

## finance (28)

| Site | Verdict | Vendor | Status | Last checked |
|---|---|---|---|---|
| [www.americanexpress.com](https://www.americanexpress.com) | OPEN |: | 200 | W5 expansion |
| [www.bankofamerica.com](https://www.bankofamerica.com) | OPEN |: | 200 | W5 expansion |
| [www.capitalone.com](https://www.capitalone.com) | OPEN |: | 200 | W5 expansion |
| [www.chase.com](https://www.chase.com) | OPEN |: | 200 | W5 expansion |
| [www.citi.com](https://www.citi.com) | OPEN |: | 200 | W5 expansion |
| [www.coinbase.com](https://www.coinbase.com) | OPEN |: | 200 | W5 expansion |
| [www.discover.com](https://www.discover.com) | OPEN |: | 200 | W5 expansion |
| [www.etrade.com](https://www.etrade.com) | UNREACHABLE |: |: | W5 expansion |
| [www.fidelity.com](https://www.fidelity.com) | OPEN |: | 200 | W5 expansion |
| [www.paypal.com](https://www.paypal.com) | OPEN |: | 200 | W5 expansion |
| [www.robinhood.com](https://www.robinhood.com) | OPEN |: | 200 | W5 expansion |
| [www.schwab.com](https://www.schwab.com) | OPEN |: | 200 | W5 expansion |
| [www.sofi.com](https://www.sofi.com) | OPEN |: | 200 | W5 expansion |
| [www.truist.com](https://www.truist.com) | OPEN |: | 200 | W5 expansion |
| [www.usbank.com](https://www.usbank.com) | OPEN |: | 200 | W5 expansion |
| [www.vanguard.com](https://www.vanguard.com) | OPEN |: | 200 | W5 expansion |
| [www.venmo.com](https://www.venmo.com) | OPEN |: | 200 | W5 expansion |
| [www.wellsfargo.com](https://www.wellsfargo.com) | OPEN |: | 200 | W5 expansion |
| [www.pnc.com](https://www.pnc.com) | OPEN |: | 200 | W7 expansion |
| [www.td.com](https://www.td.com) | OPEN |: | 200 | W7 expansion |
| [www.citizensbank.com](https://www.citizensbank.com) | WALLED | Akamai | 403 | W7 expansion |
| [www.ally.com](https://www.ally.com) | OPEN |: | 200 | W7 expansion |
| [www.marcus.com](https://www.marcus.com) | OPEN |: | 200 | W7 expansion |
| [www.merrilledge.com](https://www.merrilledge.com) | OPEN |: | 200 | W13 round-9 |
| [www.interactivebrokers.com](https://www.interactivebrokers.com) | OPEN |: | 200 | W7 expansion |
| [www.webull.com](https://www.webull.com) | OPEN |: | 200 | W7 expansion |
| [www.block.com](https://www.block.com) | UNREACHABLE |: |: | W7 expansion |
| [cash.app](https://cash.app) | OPEN |: | 200 | W7 expansion |

## health (23)

| Site | Verdict | Vendor | Status | Last checked |
|---|---|---|---|---|
| [www.cdc.gov](https://www.cdc.gov) | OPEN |: | 200 | W5 expansion |
| [www.clevelandclinic.org](https://www.clevelandclinic.org) | OPEN |: | 200 | W5 expansion |
| [www.cvs.com](https://www.cvs.com) | OPEN |: | 200 | W5 expansion |
| [www.fda.gov](https://www.fda.gov) | OPEN |: | 200 | W20 round-16 |
| [www.goodrx.com](https://www.goodrx.com) | CHALLENGED | PerimeterX | 403 | W20 round-16 |
| [www.healthline.com](https://www.healthline.com) | OPEN |: | 200 | W5 expansion |
| [www.hopkinsmedicine.org](https://www.hopkinsmedicine.org) | OPEN |: | 200 | W5 expansion |
| [www.mayoclinic.org](https://www.mayoclinic.org) | WALLED | Akamai | 403 | W5 expansion |
| [www.nih.gov](https://www.nih.gov) | OPEN |: | 200 | W5 expansion |
| [www.riteaid.com](https://www.riteaid.com) | OPEN |: | 200 | W5 expansion |
| [www.walgreens.com](https://www.walgreens.com) | OPEN |: | 200 | W5 expansion |
| [www.webmd.com](https://www.webmd.com) | OPEN |: | 200 | W5 expansion |
| [www.zocdoc.com](https://www.zocdoc.com) | CHALLENGED | DataDome | 403 | W5 expansion |
| [www.kaiserpermanente.org](https://www.kaiserpermanente.org) | OPEN |: | 302 | W7 expansion |
| [www.unitedhealthcare.com](https://www.unitedhealthcare.com) | WALLED | AWS CloudFront | 403 | W7 expansion |
| [www.aetna.com](https://www.aetna.com) | OPEN |: | 200 | W7 expansion |
| [www.cigna.com](https://www.cigna.com) | OPEN |: | 200 | W7 expansion |
| [www.humana.com](https://www.humana.com) | OPEN |: | 200 | W7 expansion |
| [www.anthem.com](https://www.anthem.com) | OPEN |: | 200 | W7 expansion |
| [www.oscar.com](https://www.oscar.com) | OPEN |: | 200 | W7 expansion |
| [www.questdiagnostics.com](https://www.questdiagnostics.com) | OPEN |: | 200 | W7 expansion |
| [www.labcorp.com](https://www.labcorp.com) | OPEN |: | 200 | W7 expansion |
| [www.roman.co](https://www.roman.co) | OPEN |: | 200 | W7 expansion |

## education (17)

| Site | Verdict | Vendor | Status | Last checked |
|---|---|---|---|---|
| [www.berkeley.edu](https://www.berkeley.edu) | OPEN |: | 200 | W5 expansion |
| [www.duolingo.com](https://www.duolingo.com) | OPEN |: | 200 | W5 expansion |
| [www.edx.org](https://www.edx.org) | OPEN |: | 200 | W5 expansion |
| [www.harvard.edu](https://www.harvard.edu) | OPEN |: | 200 | W5 expansion |
| [www.masterclass.com](https://www.masterclass.com) | OPEN |: | 200 | W5 expansion |
| [www.mit.edu](https://www.mit.edu) | OPEN |: | 200 | W5 expansion |
| [www.pluralsight.com](https://www.pluralsight.com) | OPEN |: | 200 | W5 expansion |
| [www.skillshare.com](https://www.skillshare.com) | OPEN |: | 200 | W5 expansion |
| [www.stanford.edu](https://www.stanford.edu) | OPEN |: | 200 | W5 expansion |
| [www.udacity.com](https://www.udacity.com) | OPEN |: | 200 | W5 expansion |
| [www.ox.ac.uk](https://www.ox.ac.uk) | OPEN |: | 200 | W7 expansion |
| [www.cam.ac.uk](https://www.cam.ac.uk) | OPEN |: | 200 | W7 expansion |
| [www.codecademy.com](https://www.codecademy.com) | OPEN |: | 200 | W7 expansion |
| [www.datacamp.com](https://www.datacamp.com) | OPEN |: | 200 | W7 expansion |
| [www.brilliant.org](https://www.brilliant.org) | OPEN |: | 200 | W7 expansion |
| [www.futurelearn.com](https://www.futurelearn.com) | OPEN |: | 200 | W7 expansion |
| [www.teachable.com](https://www.teachable.com) | OPEN |: | 200 | W7 expansion |

## real-estate (7)

| Site | Verdict | Vendor | Status | Last checked |
|---|---|---|---|---|
| [www.apartments.com](https://www.apartments.com) | WALLED | Akamai | 403 | W5 expansion |
| [www.compass.com](https://www.compass.com) | OPEN |: | 200 | W5 expansion |
| [www.homes.com](https://www.homes.com) | WALLED | Akamai | 403 | W5 expansion |
| [www.realtor.com](https://www.realtor.com) | RATE_LIMITED | Kasada | 429 | W7 round-5 |
| [www.redfin.com](https://www.redfin.com) | WALLED | AWS CloudFront | 403 | W5 expansion |
| [www.trulia.com](https://www.trulia.com) | OPEN |: | 200 | W5 expansion |
| [www.zillow.com](https://www.zillow.com) | OPEN |: | 200 | W5 expansion |

## saas (76)

| Site | Verdict | Vendor | Status | Last checked |
|---|---|---|---|---|
| [www.typeform.com](https://www.typeform.com) | OPEN |: | 200 | W6 expansion |
| [www.jotform.com](https://www.jotform.com) | OPEN |: | 200 | W6 expansion |
| [www.surveymonkey.com](https://www.surveymonkey.com) | OPEN |: | 200 | W6 expansion |
| [mailchimp.com](https://mailchimp.com) | OPEN |: | 200 | W6 expansion |
| [www.constantcontact.com](https://www.constantcontact.com) | OPEN |: | 200 | W6 expansion |
| [sendgrid.com](https://sendgrid.com) | OPEN |: | 200 | W6 expansion |
| [convertkit.com](https://convertkit.com) | OPEN |: | 200 | W6 expansion |
| [ghost.org](https://ghost.org) | OPEN |: | 200 | W6 expansion |
| [webflow.com](https://webflow.com) | OPEN |: | 200 | W6 expansion |
| [www.paddle.com](https://www.paddle.com) | OPEN |: | 200 | W6 expansion |
| [www.chargebee.com](https://www.chargebee.com) | OPEN |: | 200 | W6 expansion |
| [www.zendesk.com](https://www.zendesk.com) | OPEN |: | 200 | W6 expansion |
| [www.freshdesk.com](https://www.freshdesk.com) | OPEN |: | 200 | W6 expansion |
| [www.hubspot.com](https://www.hubspot.com) | OPEN |: | 200 | W6 expansion |
| [www.salesforce.com](https://www.salesforce.com) | OPEN |: | 200 | W6 expansion |
| [www.pipedrive.com](https://www.pipedrive.com) | OPEN |: | 200 | W6 expansion |
| [www.apollo.io](https://www.apollo.io) | OPEN |: | 200 | W6 expansion |
| [www.outreach.io](https://www.outreach.io) | OPEN |: | 200 | W6 expansion |
| [www.salesloft.com](https://www.salesloft.com) | OPEN |: | 200 | W6 expansion |
| [www.gong.io](https://www.gong.io) | OPEN |: | 200 | W6 expansion |
| [www.zoominfo.com](https://www.zoominfo.com) | OPEN |: | 200 | W6 expansion |
| [hunter.io](https://hunter.io) | OPEN |: | 200 | W6 expansion |
| [www.lusha.com](https://www.lusha.com) | OPEN |: | 200 | W6 expansion |
| [rocketreach.co](https://rocketreach.co) | OPEN |: | 200 | W6 expansion |
| [neon.tech](https://neon.tech) | OPEN |: | 200 | W6 expansion |
| [clerk.com](https://clerk.com) | OPEN |: | 200 | W6 expansion |
| [auth0.com](https://auth0.com) | OPEN |: | 200 | W6 expansion |
| [workos.com](https://workos.com) | OPEN |: | 200 | W6 expansion |
| [mixpanel.com](https://mixpanel.com) | OPEN |: | 200 | W6 expansion |
| [amplitude.com](https://amplitude.com) | OPEN |: | 200 | W6 expansion |
| [segment.com](https://segment.com) | OPEN |: | 200 | W6 expansion |
| [coda.io](https://coda.io) | OPEN |: | 200 | W6 expansion |
| [www.smartsheet.com](https://www.smartsheet.com) | OPEN |: | 200 | W6 expansion |
| [monday.com](https://monday.com) | OPEN |: | 200 | W6 expansion |
| [clickup.com](https://clickup.com) | OPEN |: | 200 | W6 expansion |
| [todoist.com](https://todoist.com) | OPEN |: | 200 | W25 round-21 |
| [linear.app](https://linear.app) | OPEN |: | 200 | W6 expansion |
| [basecamp.com](https://basecamp.com) | OPEN |: | 200 | W6 expansion |
| [www.wrike.com](https://www.wrike.com) | OPEN |: | 200 | W6 expansion |
| [www.zoho.com](https://www.zoho.com) | OPEN |: | 200 | W6 expansion |
| [evernote.com](https://evernote.com) | OPEN |: | 200 | W6 expansion |
| [www.box.com](https://www.box.com) | OPEN |: | 200 | W6 expansion |
| [www.dropbox.com](https://www.dropbox.com) | OPEN |: | 200 | W6 expansion |
| [www.figma.com](https://www.figma.com) | OPEN |: | 200 | W6 expansion |
| [www.canva.com](https://www.canva.com) | OPEN |: | 200 | W6 expansion |
| [miro.com](https://miro.com) | OPEN |: | 200 | W6 expansion |
| [www.mural.co](https://www.mural.co) | OPEN |: | 200 | W6 expansion |
| [www.framer.com](https://www.framer.com) | OPEN |: | 200 | W6 expansion |
| [cal.com](https://cal.com) | OPEN |: | 200 | W6 expansion |
| [savvycal.com](https://savvycal.com) | OPEN |: | 200 | W6 expansion |
| [www.drift.com](https://www.drift.com) | OPEN |: | 200 | W6 expansion |
| [www.intercom.com](https://www.intercom.com) | OPEN |: | 200 | W6 expansion |
| [crisp.chat](https://crisp.chat) | OPEN |: | 200 | W6 expansion |
| [www.tawk.to](https://www.tawk.to) | OPEN |: | 200 | W6 expansion |
| [www.livechat.com](https://www.livechat.com) | OPEN |: | 200 | W6 expansion |
| [www.webex.com](https://www.webex.com) | OPEN |: | 200 | W26 round-22 |
| [www.gotomeeting.com](https://www.gotomeeting.com) | OPEN |: | 200 | W6 expansion |
| [www.airtable.com](https://www.airtable.com) | OPEN |: | 200 | W6 expansion |
| [asana.com](https://asana.com) | OPEN |: | 200 | W6 expansion |
| [trello.com](https://trello.com) | OPEN |: | 200 | W6 expansion |
| [www.notion.so](https://www.notion.so) | OPEN |: | 200 | W6 expansion |
| [www.monday.com](https://www.monday.com) | OPEN |: | 200 | W7 expansion |
| [www.clickup.com](https://www.clickup.com) | OPEN |: | 200 | W7 expansion |
| [www.calendly.com](https://www.calendly.com) | OPEN |: | 200 | W7 expansion |
| [buffer.com](https://buffer.com) | OPEN |: | 200 | W7 expansion |
| [www.hootsuite.com](https://www.hootsuite.com) | OPEN |: | 200 | W7 expansion |
| [sproutsocial.com](https://sproutsocial.com) | OPEN |: | 200 | W7 expansion |
| [www.semrush.com](https://www.semrush.com) | OPEN |: | 200 | W7 expansion |
| [www.ahrefs.com](https://www.ahrefs.com) | OPEN |: | 200 | W7 expansion |
| [moz.com](https://moz.com) | OPEN |: | 200 | W7 expansion |
| [www.woocommerce.com](https://www.woocommerce.com) | OPEN |: | 200 | W7 expansion |
| [www.magento.com](https://www.magento.com) | UNREACHABLE |: |: | W7 expansion |
| [www.prestashop.com](https://www.prestashop.com) | OPEN |: | 200 | W7 expansion |
| [www.opencart.com](https://www.opencart.com) | OPEN |: | 200 | W7 expansion |
| [www.klarna.com](https://www.klarna.com) | OPEN |: | 200 | W7 expansion |
| [www.afterpay.com](https://www.afterpay.com) | OPEN |: | 200 | W7 expansion |

## Notes

† **npmjs.com** is listed at its Wave 1 verdict (CHALLENGED,
Cloudflare). In the Wave 3 stability round the same fetch was
dropped mid-handshake (UNREACHABLE, remote disconnect): the wall
intermittently refuses the connection itself instead of serving
its challenge. The root verdict stays CHALLENGED with this
instability on the record; see `validation/wave3/STABILITY.md`.
**Wave 4 update:** the disconnect recurred in round 3 (fourth
sighting of the pattern, including the Wave 4 directory census) : 
verdict unchanged, instability now a habit; see
`validation/wave4/STABILITY-2.md`.
**Wave 5 update:** round 4 made it a fifth sighting: and the
same round's signed-experiment leg, minutes later, was served
the real Cloudflare challenge (CHALLENGED, 403). The wall's
posture is not in doubt; its transport manners are; see
`validation/wave5/STABILITY-3.md`.

‡ **amazon.com** is listed CHALLENGED as of Wave 12 round 8, with its
oscillation on the record: the captcha interstitial ("continue
shopping" challenge, Generic) was raised in Wave 3, sat out
rounds 4 and 6, returned in round 5 (merged CHALLENGED), sat out
round 6 again (held CHALLENGED on a fresh capture showing the
interstitial), sat out round 7 AND its fresh capture (both
served 200, merged OPEN), and returned in round 8 AND its fresh
capture (both served the interstitial, evidence GENERIC_CAPTCHA +
REDIRECT_TO_CHALLENGE): the current CHALLENGED is two agreeing
readings, not a claim the gate is permanent. See
`validation/wave12/STABILITY-7.md`. **Wave 13 round 9 update:**
the interstitial sat out round 9 (round-9 reading OPEN), but two
fresh captures immediately after both served it again (evidence
GENERIC_CAPTCHA + FORM_ACTION_TO_CHALLENGE): held CHALLENGED on
the two agreeing fresh readings; see
`validation/wave13/STABILITY-8.md`. **Wave 14 round 10 update:**
round 10 reads CHALLENGED, agreeing with standing: no fresh
capture needed, no change; see
`validation/wave14/STABILITY-9.md`. britishairways.com oscillates
the same way on transport, not walls: timed out in round 6 (merged
UNREACHABLE), served in round 7 (merged OPEN), timed out in round
8 AND its fresh capture (TimeoutError twice, merged UNREACHABLE),
served in round 9 AND its fresh capture (both 200, merged OPEN).
**Wave 14 round 10 update:** round 10 failed the fetch, but two
fresh captures immediately after both served the real homepage
(both 200, Akamai server header presence only): held OPEN on
the two agreeing fresh readings; the oscillation continues, and
the row is not moved on a single uncorroborated transport
failure. See `validation/wave14/STABILITY-9.md`.
**Wave 15 round 11 update:** round 11 failed the fetch again : 
and this time the two fresh captures failed it too, so the row
moves to UNREACHABLE on corroborated transport failure (the
mirror image of the Wave 14 hold, same rule, opposite evidence).
The oscillation continues: a served round-12 reading would move
it back, exactly as todoist.com recovered in round 10. See
`validation/wave15/STABILITY-10.md`.
**Wave 16 round 12 update:** the round served the real homepage
(200, OPEN), but the two fresh captures split 1-1 (one timeout,
one served 200): no corroboration triple for either side, so
the strict rule holds the row at UNREACHABLE; the served-leaning
evidence (round + 1 fresh served vs 1 fresh failure) is noted
for round 13. See
`validation/wave16/STABILITY-11.md`. forbes.com joins the
oscillators in round 11: the round read CHALLENGED / DataDome
(403), two fresh captures immediately after both served the real
homepage (200, OPEN), and a later spot-check read CHALLENGED /
DataDome again: a 2-2 split across four recent observations, so
the standing OPEN row holds (no corroboration triple for either
side) and forbes is flagged for re-check next round.
**Wave 16 round 12 update:** the round read CHALLENGED / DataDome
again, but two fresh captures immediately after both served the
real homepage (200, OPEN, DataDome header presence only): held
OPEN on the two agreeing fresh readings; the oscillation
continues, and the row is not moved on a single uncorroborated
challenge reading. See
`validation/wave16/STABILITY-11.md`. **Wave 19 round 15 update:**
the round read CHALLENGED / DataDome, and this time the two fresh
captures agreed with the round (both CHALLENGED / DataDome 403) : 
the corroboration triple the earlier 2-1 splits never met: so
the row moves to CHALLENGED / DataDome. The oscillator record
extends, it does not exempt the row: a served round-16 triple
would move it back, exactly as the amazon.com note's oscillation
works. See `validation/wave19/STABILITY-14.md`. **Wave 20 round 16 update:**
round 16 reads CHALLENGED / DataDome, agreeing with standing : 
no diff, no fresh capture needed, no change; the Wave 19 merge
holds. See `validation/wave20/STABILITY-15.md`. webex.com
oscillates the same way: round 11 served its homepage (200,
OPEN), but two fresh captures immediately after both served the
Akamai edgesuite deny (403, WALLED): held WALLED on the two
agreeing fresh readings. See
`validation/wave15/STABILITY-10.md`.
merrilledge.com's Wave 11 LOGIN_GATED row is retired in round 9:
the sitedown page that declared a JS redirect to a login widget
is gone: round 9 and its fresh capture both serve the real
Merrill Edge homepage with no login, challenge, or redirect
signal at all, so the row merges to OPEN and the index's
LOGIN_GATED count returns to zero.

**Category headlines after Wave 3.** Freelance remains the
most-walled working category in the index: of 13 freelance
platforms, Upwork, Fiverr and Guru are WALLED and gun.io joins
them (WALLED, Cloudflare), while Contra serves agents openly.
Developer infrastructure is the most open category measured
(registries and docs serve; the notable exception is w3schools,
WALLED behind Akamai). AI-company roots mostly serve, but
claude.ai challenges (Cloudflare). Commerce carries the widest
variety: Etsy's DataDome challenge, Booking's AWS WAF challenge,
Expedia's plain 429. News is split: Reuters and the Wall Street
Journal challenge via DataDome while other outlets serve.

**Category headlines after Wave 5.** The expansion into
real-world task surfaces changed the picture: **travel is the
hardest category in the index**: of 19 travel rows, American
Airlines, Amtrak, Marriott, Hilton and Hyatt are WALLED behind
Akamai (Delta too, on a 444 drop), Expedia/Hotels.com/Vrbo
throttle, and only the aggregators and Airbnb reliably serve.
**Real estate** splits down the middle: Zillow, Trulia and
Compass serve while Redfin (AWS CloudFront), Apartments.com and
Homes.com wall and Realtor.com throttles: an agent house-hunting
for its user gets a different web depending on which portal it
knocks on. **Civic** is mostly open (USA.gov, IRS, USPS, VA all
serve) with pointed exceptions: SSA, NYC.gov and FTC are walled
behind Akamai, State.gov behind a custom deny, and Ed.gov
challenges via Microsoft Azure WAF: a vendor new to the index.
**Finance public pages are the most open new surface** (17 of 18
serve; E*TRADE simply never answered). Education serves
universally. Wave 5 also added two more wall vendors to the
classifier's vocabulary: Kasada (Chewy's 429 payload) and Azure
WAF: because the territory demanded them, not by anticipation.

**What this index is not.** Not a bypass list, not a blocklist,
and not a ranking of virtue: a wall in front of authenticated or
abuse-prone surfaces is legitimate, and OPEN is a measurement,
not a compliment. The campaign's claims from this data are
limited to what the evidence rows support, per the rules in
`campaign/WAR-PLAN.md`.
