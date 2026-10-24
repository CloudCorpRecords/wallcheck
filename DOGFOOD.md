# DOGFOOD: live runs, recorded verbatim

First live runs of wallcheck v0.1.0, from this build VM, 2026-10-24
~02:30 UTC. Command per target:

```
PYTHONPATH=src python3 -m wallcheck probe <url> --json
```

**Context, honestly stated:** these results reflect *this* client on
*this* network (a datacenter egress IP, 104.29.194.33 at run time) with
an honest non-browser user agent. Bot walls are context-sensitive by
design: the same URL from a residential IP or a full browser may score
differently. That dependence is the reason the Bot Wall Index (SPEC.md)
records scan context alongside every result. Nothing below was massaged,
retried into a different answer, or hand-edited; elapsed times are from
the recorded run.

## Results

### https://www.upwork.com: WALLED (Cloudflare), 403

```json
{
  "elapsed_ms": 502,
  "evidence": [
    "CF_RAY_HEADER",
    "SERVER_CLOUDFLARE",
    "CF_BLOCK_SORRY"
  ],
  "final_url": "https://www.upwork.com",
  "redirect_chain": [],
  "status": 403,
  "url": "https://www.upwork.com",
  "vendor": "Cloudflare",
  "verdict": "WALLED"
}
```

The point of the tool, in one object: Upwork serves this network a
Cloudflare "Sorry, you have been blocked" page: no challenge offered,
no content. (Exit code 1.)

### https://www.fiverr.com: CHALLENGED (PerimeterX), 403

```json
{
  "elapsed_ms": 701,
  "evidence": [
    "CF_RAY_HEADER",
    "SERVER_CLOUDFLARE",
    "PX_CAPTCHA",
    "PX_BODY_MARKER"
  ],
  "final_url": "https://www.fiverr.com",
  "redirect_chain": [],
  "status": 403,
  "url": "https://www.fiverr.com",
  "vendor": "PerimeterX",
  "verdict": "CHALLENGED"
}
```

Two vendors in one response, correctly separated: Cloudflare fronts the
site (cf-ray / server evidence), but the wall that fires is
PerimeterX's captcha challenge: so `vendor` names PerimeterX and the
Cloudflare presence stays in the evidence list. (Exit code 1.)

### https://contra.com: OPEN, 200

```json
{
  "elapsed_ms": 709,
  "evidence": [
    "CF_RAY_HEADER",
    "SERVER_CLOUDFLARE",
    "STATUS_200"
  ],
  "final_url": "https://contra.com",
  "redirect_chain": [],
  "status": 200,
  "url": "https://contra.com",
  "vendor": null,
  "verdict": "OPEN"
}
```

Cloudflare-fronted and fully served. Presence is not a wall: `vendor`
is null because no wall signal fired. (Exit code 0.)

### https://github.com: OPEN, 200

```json
{
  "elapsed_ms": 652,
  "evidence": [
    "STATUS_200"
  ],
  "final_url": "https://github.com",
  "redirect_chain": [],
  "status": 200,
  "url": "https://github.com",
  "vendor": null,
  "verdict": "OPEN"
}
```

(Exit code 0.)

### https://example.com: OPEN, 200

```json
{
  "elapsed_ms": 379,
  "evidence": [
    "CF_RAY_HEADER",
    "SERVER_CLOUDFLARE",
    "STATUS_200"
  ],
  "final_url": "https://example.com",
  "redirect_chain": [],
  "status": 200,
  "url": "https://example.com",
  "vendor": null,
  "verdict": "OPEN"
}
```

(Exit code 0.)

## What the first run caught in wallcheck itself

Dogfood rule: real targets before claims. The very first live pass
(2026-10-24 ~02:2x UTC) produced one false verdict:

- **github.com → CHALLENGED (Generic)** on a 200: GitHub's homepage
  embeds a captcha widget for its signup form, and the naive
  body-keyword rule fired on a full content page.

Fixed before v0.1 was called done, in the deterministic core (not by
special-casing GitHub): generic captcha/human-check markers only count
on non-200 responses or small interstitial-sized bodies
(`GENERIC_GATE_BYTES = 16384`), and two regression fixtures now pin the
behavior: a large 200 page mentioning "captcha" classifies OPEN, and
the Fiverr-style PerimeterX-behind-Cloudflare case names PerimeterX.
The runs recorded above are the post-fix binaries, re-run fresh.

---

## Addendum: Validation Wave 1 (2026-10-24, overnight)

First stress wave: 58 targets (freelance, job boards, dev platforms,
social, docs/news, big web, plus our own properties), same client
context as above, one honest fetch per target per round. Full
artifacts: `validation/wave1/`: `targets.txt`, `results-round1.json`,
`results-round2.json` (final merged set), `PROBLEMS.md` (ledger
W1-001…W1-008), `captures/` (raw response shapes behind every fix),
`INDEX-SEED.md` (the Bot Wall Index seed).

**Rounds.** Round 1 (all 58): OPEN 44 / CHALLENGED 6 / WALLED 4 /
UNREACHABLE 4. Hand-triage of every shaky verdict against captured
response shapes found **3 false walls**: wallcheck challenging pages
that were fully served. Round 2 re-probed the 14 affected targets after
the fixes: final distribution **OPEN 47 / WALLED 4 / CHALLENGED 4 /
UNREACHABLE 3**, with sanity checks unchanged (Upwork still WALLED
Cloudflare; Fiverr still CHALLENGED PerimeterX).

**What Wave 1 caught in wallcheck (all fixed test-first, 17 → 24
tests, each with a regression fixture from the real captured shape):**

- **W1-001/W1-002: the 16 KB gate was only half-applied.** The v0.1
  dogfood fix gated *generic* markers, but Cloudflare and PerimeterX
  body markers were still verdict-driving at any size: TechCrunch got
  CHALLENGED over a `dns-prefetch` hint on a 64 KB homepage, Walmart
  over a CSP allowlist string, Target over an `_pxhd` sensor cookie
  alone. Fix, generalized: **one served-page gate for every
  body-derived wall marker** (2xx + large body = served page; mentions
  on it are presence, not walls), header signals stay authoritative,
  and PX_COOKIE is now presence-only evidence: the same treatment
  `ak_bmsc` already had. A pin fixture keeps small 200 PX-captcha
  interstitials CHALLENGED.
- **W1-003: Akamai under-attributed.** eBay's 403 was WALLED with no
  vendor; the capture shows `Server: AkamaiGHost` + a `bm_so` Bot
  Manager cookie. Added both standard signals
  (AKAMAI_SERVER_HEADER, AKAMAI_BM_COOKIE).
- **W1-004: a whole vendor was missing.** Guru's 403 is Imperva
  (Incapsula): `/_Incapsula_Resource` block page, `incap_ses` cookie.
  wallcheck had no Imperva detection; it does now.
- **W1-008: DataDome attribution hardening.** NYT/Monster verdicts
  were right but rested on one header; their block bodies reference
  DataDome's `captcha-delivery.com` host, now a DD body marker.

**Honest non-fixes.** npmjs round-1 UNREACHABLE was a transient
connection kill: the diagnostic capture minutes later got the full
Cloudflare challenge, and round 2 records CHALLENGED (Cloudflare).
replit.com, discord.com, and bestbuy.com timed out on three separate
attempts each and stay UNREACHABLE: the fetch fails from this client,
so no wall verdict is claimed (W1-006). cloudcorprecords.github.io's
404 stays OPEN with the status on the record (W1-007).

**Headline from the seed:** 8 of 58 targets wall an identified agent,
across 5 vendors: and freelance is the most-walled category (3 of 7:
Upwork, Fiverr, Guru), the exact wall that started this project.

---

## Addendum: Validation Wave 2 (2026-10-24, overnight)

Two legs, full artifacts in `validation/wave2/` (`paths.txt`,
`results-paths.json`, `PATHS.md`, `PROBLEMS.md` W2-001…W2-006,
`captures/`, `SIGNING.md`, `results-signed.json`).

**Leg A: depth probing.** 77 path probes (login, signup, search,
dev/API, robots, sitemap, llms.txt) across the 8 walled platforms
plus Contra, LinkedIn, Indeed. Final: OPEN 38 / WALLED 17 /
CHALLENGED 16 / LOGIN_GATED 3 / UNREACHABLE 3. The stories:
registry.npmjs.org and api.medium.com serve OPEN while their webs
are walled; genuine llms.txt files serve OPEN on Upwork, Fiverr,
Monster, and Indeed; Guru is the only whole-domain wall (Imperva,
robots.txt included); npmjs is the deepest (even robots.txt is
challenged). Only 3 of 11 login paths are real login pages: the
rest are walls in front of the login page, or 404s. Wave 2 caught
three classifier defects in its own first round: the login-URL
heuristic pre-empting walls (W2-001), generic markers challenging a
404 page (W2-002), and SSO `/auth` segments missed entirely
(W2-003): all fixed test-first with capture-built fixtures
(8 new classifier fixtures), the 6 affected paths re-probed live,
and the fixes verified in the merged results.

**Leg B: v0.2 passport prototype.** RFC 9421 request signing
shipped (`wallcheck keygen`, `probe --sign`, `verify-server`):
`hmac-sha256` shared-secret variant, because Ed25519 is not in the
Python stdlib and `cryptography` is not installed: the limitation
(shared secrets can't join the public Ed25519 Web Bot Auth
directory) is documented, not hidden. 14 signing tests including a
localhost verify-server end-to-end; signed vs unsigned probes
against our own three properties changed nothing, as expected : 
they don't check signatures yet. Suite total: **46 tests, all
green**; MCP smoke still passes.

## Addendum: Validation Wave 3 (2026-10-24, overnight)

**Leg A: stability.** The 58 Wave 1 roots were re-probed:
**56 verdicts identical**, 2 flips, both target-side churn and
zero classifier defects. amazon.com took up a Generic captcha
gate between waves (capture-verified: CHALLENGED is the correct
current read); npmjs.com's wall intermittently drops the
connection outright instead of serving its challenge (recorded
UNREACHABLE for the round; the Index keeps CHALLENGED with an
instability note). The three standing UNREACHABLEs (replit.com,
discord.com, bestbuy.com) reproduced a third time.
`validation/wave3/STABILITY.md` has the flip table.

**Leg B: index expansion.** 96 new targets brought the census to
**154 sites**, merged into the repo-root `INDEX.md` working table:
OPEN 133 · CHALLENGED 10 · WALLED 6 · RATE_LIMITED 1 ·
UNREACHABLE 4. New to the wall column: a fourth freelance platform,
gun.io (WALLED, Cloudflare); AWS WAF appears as a vendor (below);
DataDome challenges at Etsy, Reuters, and the Wall Street
Journal; Expedia answers a plain 429. Developer infrastructure
is the most open category measured; freelance remains the most
walled. The wave caught two classifier defects in its own first
round: an AWS WAF challenge page classified OPEN because the
vendor wasn't detected at all and the generic markers missed its
"not a robot" wording (W3-001, booking.com), and an Akamai
`edgesuite` error page whose vendor went unattributed for want of
one body signal (W3-002, w3schools.com): both fixed test-first
with capture-built fixtures; the affected targets re-probed live
(booking → CHALLENGED/AWS WAF, w3schools → WALLED/Akamai).

**Leg C: v0.3 owner audit.** `wallcheck audit` shipped: six
checks (robots.txt AI directives, llms.txt sanity, sitemap, feed,
API, signed-agent readiness), PASS/WARN/FAIL + evidence + fixes,
graded A-F. First live audits: github.com C (7/12): our own
clipwise.replit.app D (5/12), reneturcios.replit.app F,
cloudcorprecords.github.io F, example.com F. The audit's first
catch was on our own property (clipwise serves its SPA shell as
/llms.txt: a live soft-404), and its second was in itself: a
soft-404 at /openapi.json suppressed the /api fallbacks until the
router required a real spec document and the api check learned to
name app shells (W3-004). Signed-agent readiness: **zero of five**
domains publish a Web Bot Auth directory: the baseline Front 2
has to move. Suite total: **59 tests, all green**; MCP smoke
still passes. Nothing published; the launch hold stands.

## Addendum: Validation Waves 4-8 (2026-10-24, overnight)

The dogfood log stopped at Wave 3 while the waves kept running;
this addendum closes the gap from the wave reports (no new live
runs are claimed here: every number below is the wave's own
record, cited).

**Wave 4.** Round-3 stability: all 154 index roots re-probed, 4
flips, all target-side churn, zero classifier defects: the first
clean defect sheet on a stability leg. Directory census: 3 of 154
domains publish a signed-agent directory (chatgpt.com
reference-grade, indeed.com and substack.com bare JWKS); 16 wall
even the directory path itself. Ed25519 shipped in pure-Python
stdlib, verified against the official RFC 8032 §7.1 test vectors.
Four vendor report cards (PerimeterX, DataDome, Akamai, Imperva).
Suite: **75 tests, all green.**

**Wave 5.** Round-4 stability: 153 of 154 identical (npmjs.com's
connection-drop pattern, held CHALLENGED). Expansion round 2
(+104 civic/finance/travel/health sites, index to 258) found 5
classifier defects (W5-001…W5-005: captcha-loader false challenge,
Azure WAF, Kasada attribution, CloudFront block page, the 444
false OPEN), all fixed test-first. Signed-vs-unsigned experiment:
12 of 12 verdicts unchanged: unregistered signatures are not
consulted by walls. Owner fix kit shipped with staged fixes for
our own properties. Suite: **85 tests, all green.**

**Wave 6.** Adversarial battery: 25 fixtures (24 synthetic shapes
plus the Amazon interstitial that corrected a hand classification),
4 classifier defects fixed generalized (vendor-neutral JS-proof
stubs, generic markers yielding to login pages, localized
challenge phrases, Incapsula incident-ID ⇒ WALLED at any status).
Expansion round 3 (+136 long-tail sites, index to 394) surfaced
one more defect (W6-005: vendor race let Cloudflare CDN presence
outrank economist.com's fired DataDome wall). Suite: **110 tests,
all green.**

**Wave 7.** Expansion round 4 (+105 sites, index to 499). Round-5
stability: 496 of 499 identical, 3 flips all churn/transport;
vendor fills (npmjs.com → Cloudflare, realtor.com's 429 →
Kasada). Directory census v2: 4 of 499 adopters (ahrefs.com new,
2 keyed Ed25519 keys); 71 domains wall the directory path itself.
Audit sweep of 92 most-walled domains: F 71 / D 18 / C 3. One
infrastructure incident: an egress-proxy credential rotation
poisoned 52 consecutive round-5 fetches; the rows were archived
and re-probed after a fresh-shell restart, evidence intact. Zero
classifier defects. Suite: **112 tests, all green.**

**Wave 8.** Depth wave 2: 322 path probes across 46 platforms
(OPEN 94 / WALLED 145 / CHALLENGED 54 / RATE_LIMITED 20 /
UNREACHABLE 6 / LOGIN_GATED 3); 21 whole-domain walls (vs 1 in
Wave 2's cohort); genuine llms.txt on only 3 platforms. One
classifier defect (W8-001: the login heuristic fired on delta's
444 Akamai deny), fixed with a generalized rule: a gate must be
a served page (2xx/3xx). Front-doors file +55 rows (65
platforms). Fix-kit §7 added. Own-properties re-audit unchanged
(clipwise D 5/12, portfolio F 3/12, Pages F 3/12); the Wave 5
claim that the staged deploy buys the portfolio a B was corrected
to C (7/12; B needs feed + directory). Suite: **114 tests, all
green.**

**Waves 9-17 addendum (Wave 17 docs re-audit).** The wave reports
under `validation/` are the primary record from Wave 9 on; this
addendum keeps the suite-count chain continuous.

**Wave 9.** Release-candidate polish: 0.5.0-rc stamped
(`__init__`/`pyproject`/`server.json`), the `audit` MCP tool
shipped (≤10 honest GETs, tested fetch budget), 14 doc
corrections, and `campaign/LAUNCH-READINESS.md` (proven /
not-proven / ship needs only). Suite: **120 tests, all green.**

**Wave 10.** Round-6 stability: 499/499 probed, 7 raw flips, 5
hand-checked, only britishairways.com merged (reproduced timeout
→ UNREACHABLE). Adversarial battery v2: 32 shapes, 8 defects
fixed test-first (geo-refusal 200 → WALLED, 451 → WALLED,
redirect-to-challenge/login, 5xx vendor reset, llms JSON-error
FAIL, robots HTML soft-404 FAIL). Signing regression on
0.5.0-rc: 7/7 unchanged. Suite: **152 tests, all green.**

**Wave 11.** Round-7 reclassification with the Wave 10-fixed
classifier: 3 flips, all merged on fresh-capture corroboration
(amazon.com's interstitial sat round 7 out, merged OPEN;
britishairways.com served, merged OPEN; merrilledge.com moved
OPEN → LOGIN_GATED, fix-driven by the redirect-to-login rule : 
the round's only fix-driven move). Battery v3: 31 shapes, 6
defects fixed test-first. Suite: **183 tests, all green.**

**Wave 12.** Round-8 reclassification with the Wave 11-fixed
classifier: zero fix-driven moves; 2 merges, both corroborated
churn (amazon.com CHALLENGED on two agreeing interstitial
readings, britishairways.com UNREACHABLE on two agreeing
timeouts). Battery v4: 27 shapes, 6 defects fixed test-first.
Signing spot-check on chatgpt.com + ahrefs.com: 2/2 unchanged.
Suite: **210 tests, all green.**

**Wave 13.** Round-9 reclassification: 3 moves (britishairways.com
to OPEN, merrilledge.com to OPEN: its Wave 11 login gate is
gone: webex.com to WALLED / Akamai, the second sighting after
round 8); amazon.com held CHALLENGED on two agreeing fresh
interstitial readings against a round-9 sat-out. Battery v5: 25
shapes, 3 defects fixed test-first. Index audit: 499 rows,
distribution matches header. Suite: **236 tests, all green.**

**Wave 14.** Round-10 reclassification: 3 diffs, all hand-checked
:  todoist.com merged to OPEN; britishairways.com held OPEN;
kaiserpermanente.org held OPEN/302; zero fix-driven moves (fourth
straight round). Battery v6: 32 shapes, 5 defects fixed
test-first. Vendor audit of all 60 WALLED/CHALLENGED rows: 0
mismatches. Suite: **270 tests, all green.**

**Wave 15.** Round-11 reclassification: 3 diffs, all hand-checked
:  britishairways.com merged to UNREACHABLE (round + two agreeing
fresh failures); forbes.com held OPEN on a 2-2 split (round
challenge + later spot-check challenge vs two fresh served
readings: documented intermittent oscillator); webex.com held
WALLED / Akamai. Battery v7: 39 shapes, 13 defects fixed
test-first. Limitations revisit: 1 narrowed, 1 resolved by
construction, 8 still open (including the Wave 3 silent-JS-proof
boundary, which survives). Suite: **321 tests, all green.**

**Wave 16.** Round-12 reclassification: zero rows moved; 5 diffs,
all held on fresh captures (npmjs.com + apnews.com transport
noise, france24.com + forbes.com served readings,
britishairways.com 1-1 fresh split: strict rule holds the row).
Battery v8: 49 shapes, 21 defects fixed test-first
(concatenated-text scans, data-attribute + style suppression,
Location-header routing, passkey/magic-link signals, BOM-tolerant
frontmatter, JSON generalization). Adopter spot-check: 4/4
adopters still publishing. Suite: **375 tests, all green.**

**Wave 17.** Battery v9: 48 shapes, 6 fix families shipped
test-first (noscript + title metadata suppression on served
pages with a corroboration rule for body-presented walls,
QR-code sign-in prompts, entity-encoded JSON error documents,
Nordic challenge phrases, full-screen overlay challenges) plus
pins (cache headers, commented Sitemap lines, the script-boundary
captcha re-test, code-switched fragments). Corpus regression:
44 captures, zero diff vs the Wave 15 baseline. Round-13
reclassification with the Wave 16-fixed classifier: 499/499
probed, zero rows merged: all three diffs held on fresh
captures (britishairways.com served-leaning 2-1, forbes.com
challenged-leaning 2-1, neither meeting the corroboration
triple): and one diff caught a live Wave 16 misfire:
rubygems.org's served homepage misread as a passkey prompt
(asset filenames, not a prompt), fixed the same wave
(visible-text wording + served-page gate on all three
auth-form branches). Docs re-audit: 6 corrections. Suite: **428
tests, all green.**

**Wave 18.** Battery v10: 48 shapes, 6 fix families shipped
test-first (sticky-banner challenges with a stickiness third
key, SMS/email digit-box code prompts, declared-but-dead
sitemap evidence, empty-loc sitemaps, PT-BR/ID/VI/TH challenge
phrases, non-interactive aria-label suppression) plus pins
(unconsumed custom properties, CSS content on content-free
pages, llms via trailing-slash redirects, relative locs).
Round-14 reclassification with the Wave 17-fixed classifier:
499/499 probed (first launch died at 123/499 with no
traceback: external kill: resumed against a reconstructed
Wave 17 tree copy so the round measures one tree end to end);
5 rows merged (claude.ai to LOGIN_GATED/Cloudflare on a login
redirect, amazon.com to OPEN, fda.gov to LOGIN_GATED/Akamai
on a 401, goodrx.com to OPEN, ubereats.com to OPEN: the
round's ONLY fix-driven move, under the Wave 17 head strip);
7 held, including three Wave 17 QR-prompt misfires rejected
(remoteok.com, td.com, venmo.com: script filenames,
identifiers, and stylesheet classes, not prompts), fixed the
same wave (visible-text wording + served-page gate on the QR
branch). Index row 500 added (search.brave.com, OPEN: the
search section was thinnest at 2 rows). Docs spot-check: the
423-vs-428 question resolved (428 was right at Wave 17's end;
423 was the mid-wave battery count). Index now 500 rows: OPEN
418 / CHALLENGED 21 / WALLED 35 / RATE_LIMITED 7 /
UNREACHABLE 17 / LOGIN_GATED 2: vendor shares on the 56
WALLED+CHALLENGED rows: WALLED: Akamai 22, Cloudflare 5,
AWS CloudFront 3, Imperva 1, unattributed (bare 403) 4;
CHALLENGED: DataDome 14, Cloudflare 4, PerimeterX 1,
Microsoft Azure WAF 1, AWS WAF 1. Suite: **481 tests, all
green.**

**Wave 19.** Round-15 reclassification with the Wave 18-fixed
classifier: 500/500 probed, 6 rows merged (ed.gov to
UNREACHABLE on three consecutive failures; forbes.com to
CHALLENGED/DataDome on the corroboration triple the
oscillator's earlier splits never met; irishjobs.ie, jobs.ie,
and totaljobs.com to OPEN; jobrapido.com to RATE_LIMITED on
two agreeing 429s), 4 held; zero fix-driven moves: all five
spotlights held (ubereats.com OPEN under the Wave 17 head
strip; remoteok.com, td.com, venmo.com OPEN with no QR
misfire; rubygems.org OPEN under the passkey fix). Battery
v11: 51 shapes, 8 defect families shipped test-first
(template blocks join the never-presented family, challenge
phrases split across image alt attributes, email-only
Continue sign-in steps, sitemap usability fallthrough,
CR-only frontmatter normalization, fragment-only sitemap
locs, HE/FA/UR/BN challenge phrases, native <dialog>
challenge elements) plus one Wave 16 guard superseded with
independent justification and one hand-correction. DOGFOOD
addendum for Waves 9-18 written (this chain). LOGIN_GATED
watch: claude.ai still a real login redirect, fda.gov still
a 401: no softening. Index now 500 rows: OPEN 419 /
CHALLENGED 21 / WALLED 35 / RATE_LIMITED 8 / UNREACHABLE 15 /
LOGIN_GATED 2. Suite: **532 tests, all green.**

**Wave 20.** Round-16 reclassification with the Wave 19-fixed
classifier: 500/500 probed, 10 rows merged (claude.ai to
CHALLENGED/Cloudflare: its login gate replaced by a wall;
amazon.com to CHALLENGED/Generic; ed.gov to CHALLENGED/Azure
WAF, answering again; fda.gov to OPEN: its 401 gate gone;
goodrx.com to CHALLENGED/PerimeterX; irishjobs.ie, jobs.ie,
totaljobs.com to UNREACHABLE, reversing Wave 19's OPEN
merges; jobrapido.com to OPEN; ubereats.com to
CHALLENGED/Cloudflare: a live wall superseding the Wave 17
head-strip move, target-side), 3 held; zero fix-driven moves;
the LOGIN_GATED watch empties: zero LOGIN_GATED rows for
the first time since Wave 13. Battery v12: 39 shapes, 3
defect families shipped test-first (iframe-src redirect
routing targets, localized JS-proof phrases DE/FR/ES/PT/JA,
localized human-check phrases UK/HI/MS/TL/SW) plus one
hand-correction (an identity-verification phrase is
auth-ambiguous, corrected to OPEN). Adopter spot-check: 4/4
still publishing. Index now 500 rows: OPEN 415 / CHALLENGED
26 / WALLED 35 / RATE_LIMITED 7 / UNREACHABLE 17 /
LOGIN_GATED 0. Suite: **571 tests, all green.**

**Wave 21.** Round-17 reclassification with the Wave 20-fixed
classifier: 500/500 probed, zero rows merged: 4 diffs all
held on fresh captures (apnews.com CHALLENGED on a 1-1 split;
amazon.com CHALLENGED on two agreeing interstitials;
npmjs.com CHALLENGED on two agreeing challenges against a
connection drop, the 10th transport-pattern sighting;
wayfair.com OPEN against a PerimeterX 429, transient
throttle); zero fix-driven moves; all ten Wave 20 merges
agree with round 17. Battery v13: 37 shapes, 5 defect
families shipped test-first (object/embed routing species,
"high traffic" joins the throttle causes, authenticator-app
passcode prompts, non-HTTP-scheme sitemap locs, TA/TE/MR/PA
challenge phrases) plus one hand-correction (a mid-file
"empty" robots group cannot exist under RFC 9309 grouping : 
the parser was right, the test now asserts FAIL). Path
matrix on the 10 Wave 20 merged rows: 50/50 probes, no
contradictions (the three UNREACHABLE job boards answer
robots.txt 200 while their origins fail: origin-down, not
domain-dead). Docs spot-check: README counts corrected.
Index unchanged: OPEN 415 / CHALLENGED 26 / WALLED 35 /
RATE_LIMITED 7 / UNREACHABLE 17 / LOGIN_GATED 0. Suite:
**608 tests, all green.**

**Wave 22.** Round-18 reclassification with the Wave 21-fixed
classifier: 500/500 probed, zero rows merged: 2 diffs both
held (chicagotribune.com OPEN on two agreeing served
readings against a round 403, transient refusal; forbes.com
CHALLENGED/DataDome on a 1-1 fresh split: served-leaning
2-1, no triple, the oscillator's first served-leaning
split); zero fix-driven moves. Battery v14: 30 shapes, 3
defect families shipped test-first (SVG <title>/<desc>
metadata stripped from the presented-text scans,
"Continue with SSO" sign-in prompts, GU/KN/NE/KM challenge
phrases) plus one hand-correction (a 451 body carrying a
challenge phrase reads WALLED/Generic: the vendor cell
records body evidence, not a re-attribution). Vendor
re-audit 2: all 61 WALLED/CHALLENGED cells verified against
fresh evidence, zero corrections (apnews.com's Cloudflare
confirmed by capture; the four "unattributed (bare 403)"
cells confirmed a third time). Index unchanged at 500 rows:
OPEN 415 / CHALLENGED 26 / WALLED 35 / RATE_LIMITED 7 /
UNREACHABLE 17 / LOGIN_GATED 0. Suite: **638 tests, all
green.**

**Wave 23.** Rene ordered this extra round personally after
the 07:00 close (the overnight cron stays disabled).
Round-19 reclassification with the Wave 22-fixed classifier:
500/500 probed, 2 rows merged, both transport
(britishairways.com to OPEN, recovered from its Wave 15
failure merge; todoist.com to UNREACHABLE on three
consecutive failures: the two cancel in the distribution),
1 held (webex.com WALLED/Akamai on a 1-1 fresh split, its
second split-hold); zero fix-driven moves (no row answered
418 or 451; no capture carried a Wave 22 shape). Battery
v15: 36 shapes, 3 defect families shipped test-first (stray
<picture> text nodes join the never-presented family, the
alt scan deliberately exempt; HTTP 418 joins the 444/451
deliberate-refusal family as WALLED; EL/CS/HU/RO challenge
phrases) plus one hand-correction (a fragment pin belongs on
a served page, the J7g precedent). Adopter spot-check v3:
4/4 still publishing, all keys byte-identical: chatgpt.com's
expiry drifted forward a third consecutive time (+12,555 s
vs the Wave 16 record, still operated, still
reference-grade); 15/15 walled directory paths still serve
no directory (huggingface.co now answers 401 LOGIN_GATED
instead of the census-era hard wall: a gate, not an
opening). Index unchanged at 500 rows: OPEN 415 /
CHALLENGED 26 / WALLED 35 / RATE_LIMITED 7 / UNREACHABLE 17 /
LOGIN_GATED 0. Suite: **674 tests, all green.**

**Wave 24.** First of up to five Rene-ordered waves (24-28).
Round-20 reclassification with the Wave 23-fixed classifier:
500/500 probed; a mid-round service restart killed the
runner at 276/500: the three Wave 24 fixes were temporarily
reverted (verified absent by grep AND by the battery
re-failing on exactly the same 8 gaps), the runner
relaunched against the pristine Wave 23 tree and resumed, and
the fixed file was restored and sha256-verified, so the
round measures one tree end to end. 2 rows merged
(wayfair.com to CHALLENGED/PerimeterX: the rounds 16-17
transient throttle is now the standing answer across three
readings; apnews.com to UNREACHABLE on three consecutive
failures), 1 held (britishairways.com OPEN on a 1-1 split);
zero fix-driven moves. New 402 watch: telegraph.co.uk and
usatoday.com answered 402 in the round (OPEN under the Wave
23 tree, WALLED on fresh captures under the Wave 24 tree) : 
round 21 is their measurement round. Battery v16: 36
shapes, 3 defect families shipped test-first (HTTP 402 joins
the 444/451/418 deliberate-refusal family with STATUS_402
evidence; push-approval sign-in prompts; BG/SK/HR/SL
challenge phrases, Slovak "nie ste" kept distinct from
Czech "nejste") plus 28 pins. Docs spot-check: README chain
extended 638 → 674 → 710. Index now 500 rows: OPEN 414 /
CHALLENGED 26 / WALLED 35 / RATE_LIMITED 7 / UNREACHABLE 18 /
LOGIN_GATED 0. Suite: **710 tests, all green.**

**Wave 25.** Round-21 reclassification with the Wave 24-fixed
classifier: 500/500 probed, 3 rows merged (telegraph.co.uk
and usatoday.com to WALLED on round + 2 agreeing 402
readings: the round's TWO fix-driven moves under W24-R2,
the first fix-driven moves since round 14's single move;
todoist.com to OPEN, recovered from its round-19 failure
merge), 1 held (britishairways.com OPEN on two agreeing
served readings against a round transport failure); the
push-approval and BG/SK/HR/SL fixes measured zero live
effect. Battery v17: 37 shapes, 3 defect families shipped
test-first (employee-ID sign-in prompts; SR/MK/LV/LT
challenge phrases, Serbian Cyrillic kept distinct from
Croatian Latin and Macedonian "дека/сум" from Bulgarian;
challenge phrases living only in placeholder attributes
join the configuration family) plus 28 pins and ONE
HAND-CORRECTION: HTTP 410 was briefly classified WALLED
under a deliberate-refusal reading, but the Wave 6 pin
test_s1c_410_gone vetoed it and the pin was right: 410 is a
definitive answer about the resource, the 404 species, and
the branch was reverted with no classifier change. FRONT-
DOORS gains the huggingface.co row (root OPEN, directory
path 401 LOGIN_GATED confirming the Wave 23 finding; the
combined file now holds 66 platforms: 40 VERIFIED / 20 NO
ROUTE FOUND / 6 UNVERIFIED). Index now 500 rows: OPEN 413 /
CHALLENGED 26 / WALLED 37 / RATE_LIMITED 7 / UNREACHABLE 17 /
LOGIN_GATED 0. Suite: **747 tests, all green.**

**Wave 26.** Round-22 reclassification with the Wave 25-fixed
classifier: 500/500 probed in a single run, no incident; 2
rows merged (apnews.com to CHALLENGED/Cloudflare, recovered
from its round-20 failure merge: the failures were
delivery failures, the challenge stood behind them;
webex.com to OPEN: the Akamai wall standing since round 9
has lifted, closing the split round 19 held), 1 held
(forbes.com CHALLENGED/DataDome: the documented oscillator
oscillating, fresh evidence agreeing with standing); zero
fix-driven moves: no fresh capture carried an employee-ID
prompt, an SR/MK/LV/LT phrase, or a placeholder-carried
phrase. Battery v18: 41 shapes, 3 defect families shipped
test-first (badge-tap sign-in prompts: the physical
credential ceremony, two-keyed from birth with
asset-filename, stylesheet-class, and script-string negative
carriers pinned; percent-encoded sitemap hosts rejected : 
the WHATWG host parser rejects "%" in hosts of special
schemes, path encoding untouched; CA/ET/HY/KA challenge
phrases, Catalan "no soc" kept distinct from Spanish "no
soy") plus 34 pins (label-element and button text complete
the presented-element survey; 451 + Retry-After stays
WALLED, the throttle rule's 403/503 scope holds; robots
value whitespace binds as trimmed). Vendor-share refresh
recomputed from the table: WALLED: Akamai 22, Cloudflare
5, unattributed (bare 403) 4, AWS CloudFront 3,
unattributed (402 pair) 2, Imperva 1; CHALLENGED : 
DataDome 15, Cloudflare 5, PerimeterX 3, AWS WAF 1,
Microsoft Azure WAF 1, Generic 1; three report-card
corrections (Akamai's share restated 22 of 37, DataDome's
five properties corrected to fifteen, PerimeterX's one
property corrected to three). Round 22's two merges then
moved one row each way (webex.com's Akamai row out of
WALLED, apnews.com's Cloudflare row into CHALLENGED).
FRONT-DOORS stands at 66 platforms. Index now 500 rows:
OPEN 414 / CHALLENGED 27 / WALLED 36 / RATE_LIMITED 7 /
UNREACHABLE 16 / LOGIN_GATED 0. Suite: **788 tests, all
green.**
