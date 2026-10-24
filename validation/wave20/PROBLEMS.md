# Wave 20 — Problems ledger

## Leg B (adversarial battery v12) — 3 defect families, all fixed

- **W20-001** (classifier, fixed): an iframe src to a login
  target on a content-free page read OPEN (M1d) — no rule read
  iframe sources. Fix: iframe sources join the redirect-target
  species (meta refresh, JS location, Refresh/Location headers,
  form actions) under the same markers_count gate and the same
  login/challenge token rules. Fixtures: M1a/b/c/d.
- **W20-002** (classifier, fixed): German, French, Spanish,
  Portuguese, and Japanese browser-verification stubs read
  OPEN (M2a–e) — the JS_PROOF family was English-only. Fix:
  five full interstitial sentences added to _JS_PROOF_PHRASES,
  gated like every phrase there. Fixtures: M2a/b/c/d/e + pin
  M2f.
- **W20-003** (classifier, fixed): Ukrainian, Hindi, Malay,
  Tagalog, and Swahili challenge phrases read OPEN (M3a–e).
  Fix: added to _LOCALIZED_HUMAN_CHECK, gated like every
  generic marker. Fixtures: M3a/b/c/d/e + pins M3f/g.

## Leg B — hand-correction (discipline working)

- **M4a/M4d.** "Please verify your identity to continue" was
  first hand-classified CHALLENGED, then corrected to OPEN
  before any fix landed: the demand is auth-ambiguous
  (account recovery vs bot gate), the same reason Wave 11
  excluded "verification in progress" from JS_PROOF, and
  adding it would misfire on auth-recovery pages the
  auth-form branches are designed to catch. M4b/M4c stand as
  pins. See ADVERSARIAL-12.md.

## Leg B — corpus regression (done)

Stored captures replayed through the Wave 20-fixed classifier
(`validation/wave15/corpus_check.py`, output vs Wave 15's
`corpus-after.txt`). Zero regressions: diff is empty.

## Leg C (adopter spot-check + INDEX recount) — done

- **Adopters 4/4 still publishing:** chatgpt.com, indeed.com,
  substack.com, ahrefs.com directories all serve 200 OPEN
  (`results-adopter-spot.json`). No adopter lost.
- **INDEX recount verified:** 500 rows, distribution OPEN 419 /
  CHALLENGED 21 / WALLED 35 / RATE_LIMITED 8 / UNREACHABLE 15 /
  LOGIN_GATED 2 — exact match to the Wave 19 header. (Two
  rows carry "— see note" suffixes after their links — npmjs
  CHALLENGED †, amazon OPEN ‡ — which a naive verdict-cell
  regex misses; the recount parser accounts for them.)

## Leg A (round-16 reclassification) — DONE (see STABILITY-15.md)

- **Runner:** fresh runner, single ROUND constant, fully
  detached (setsid nohup, resumable, log-monitored) — no
  incident, 500/500 probes, zero missing, zero dupes. The
  runner imported the Wave 19 tree at launch (12:23:43 UTC,
  before any Wave 20 battery edit at 12:26:35 UTC), so round
  16 measures the Wave 19 tree end to end; the Wave 20 battery
  fixes are unmeasured until round 17.
- **13 diffs, all hand-checked with two fresh captures each:**
  10 merged (claude.ai to CHALLENGED / Cloudflare, amazon.com
  to CHALLENGED / Generic, ed.gov to CHALLENGED / Microsoft
  Azure WAF, fda.gov to OPEN, goodrx.com to CHALLENGED /
  PerimeterX, irishjobs.ie / jobs.ie / totaljobs.com to
  UNREACHABLE, jobrapido.com to OPEN, ubereats.com to
  CHALLENGED / Cloudflare), 3 held (npmjs.com CHALLENGED on
  two agreeing fresh challenges against a round connection
  drop — the 9th transport-pattern sighting; wayfair.com OPEN
  on two agreeing fresh served readings against a round
  PerimeterX 429; webex.com WALLED / Akamai on a 1–1 fresh
  split — no corroboration triple).
- **Fix-driven moves: zero.** All eight Wave 19 rule families
  moved no live row; spotlights held except ubereats.com, whose
  move is a target-side wall replacing the Wave 17 head-strip
  page, not a rule move. The LOGIN_GATED watch empties: both
  standing LOGIN_GATED rows moved (claude.ai to CHALLENGED,
  fda.gov to OPEN), leaving LOGIN_GATED 0.
- **Fresh-capture method note:** probe_url returns no body, so
  the script uses fetch_raw + classify (the Wave 16 spot-check
  hit the same discovery). Because fresh captures ran on the
  Wave 20 tree while the round measured the Wave 19 tree, every
  capture carries a Wave 20-rule involvement check — all 26
  report zero determinative flags (goodrx.com's
  REDIRECT_TO_CHALLENGE flag is non-determinative: PX_CAPTCHA /
  PX_BODY_MARKER drive its verdict, and the Wave 19-tree round
  reading already agreed), so the corroborations are
  tree-comparable. INDEX distribution after merges: OPEN 415 /
  CHALLENGED 26 / WALLED 35 / RATE_LIMITED 7 / UNREACHABLE 17 /
  LOGIN_GATED 0 (500 rows, recount verified).
