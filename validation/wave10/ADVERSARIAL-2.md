# Wave 10 — Adversarial Battery v2 (Leg B)

32 hand-classified shapes, all NEW relative to Wave 6's battery
(`validation/wave6/HANDCLASS.md` — no S1–S6 repeats). Hand verdicts
in `validation/wave10/HANDCLASS-2.md`, pinned in
`tests/test_adversarial2.py`. First run: **24 pass, 8 mismatches —
all 8 were genuine classifier/audit defects, all fixed test-first
with generalized rules.** No honest limitations had to be ledgered:
every mismatch had a clean generalized fix.

## Defects and fixes

**W10-001 — 200 geo-block page read OPEN (B3b).** A stub page whose
entire content refuses service by country was OPEN because the
classifier equated 2xx with served. Generalized fix: geo-refusal
phrasing (negated forms only — "not available in your region /
country / location", "is unavailable in your region / country",
"service not available in your region / country") on a stub-sized
page (< 4 KB, inside the served-page gate) ⇒ WALLED. The 4 KB bound
is deliberate: a product page noting one item's regional
availability is content, not a refusal page. Verdict-only signal
(no vendor): a geo refusal is a refusal, not a bot-wall brand.

**W10-002 — 451 read OPEN (B3c).** HTTP 451 (Unavailable For Legal
Reasons, RFC 7725) fell through the status ladder to OPEN.
Generalized fix: 451 ⇒ WALLED, the 444 rule's sibling — a
deliberate refusal code is a refusal, not a served page and not a
server failure.

**W10-003 — meta-refresh to a challenge read OPEN (B4a).** A page
whose whole content routes the client to /challenge/ was OPEN: the
classifier only recognized captcha refresh targets (Wave 6 S2c).
Generalized fix: any declared redirect target (meta refresh or JS
location assignment) carrying a challenge token (captcha,
challenge, verify-human, bot-check, human-check) on a non-served
page ⇒ CHALLENGED / Generic.

**W10-004 — meta-refresh to login read OPEN (B4b).** Same
reference principle, login side: a page whose whole content routes
the client to /login ⇒ LOGIN_GATED. Content targets (B4d, refresh
to /home) stay OPEN — the boundary is the target, not the
mechanism.

**W10-005 — JS redirect to a verification challenge read OPEN
(B4c).** The S2c principle in JS form: `window.location.href =
"/challenge/verify-human"` ⇒ CHALLENGED / Generic, via the same
redirect-target rule as W10-003.

**W10-006 — vendor leaked onto a 5xx UNREACHABLE (B6c).** A
Cloudflare 522 page (origin down) read UNREACHABLE / Cloudflare:
the verdict claimed no wall, but the vendor field named one.
Generalized fix: UNREACHABLE verdicts now carry vendor None, like
OPEN verdicts and like the fetch-error path already did. A 522 is
an origin failure wearing vendor branding, not a wall.

**W10-007 — /llms.txt serving a JSON error document read PASS
(B9a, audit tool).** The llms check's HTML gate did not catch
`{"error": "not found"}` served as text/plain. Generalized fix: a
body that parses as JSON carrying an `error`/`errors` key ⇒ FAIL
(JSON_ERROR_DOC). The gate is error-key presence only, not format
policing — a JSON index without an error key is not failed.

**W10-008 — /robots.txt serving an HTML error page read PASS
(B9d, audit tool).** The robots check lacked the HTML gate the
llms check has: an HTML soft-404 parsed as an (empty, permissive)
robots file. Generalized fix: mirror the llms HTML gate into the
robots check (SOFT_404_HTML ⇒ FAIL).

## Pins that held (no classifier change needed)

- Mixed vendors: CF presence + DataDome wall ⇒ DataDome (B1a);
  edgesuite + kpsdk ⇒ Akamai (B1c); Imperva marker + DataDome
  header ⇒ DataDome (B1d); three-vendor contradiction with
  cf-mitigated ⇒ Cloudflare (B10a) — the ordered wall-signal
  precedence holds in all four directions.
- Login hybrids: 401 at /login ⇒ LOGIN_GATED (B2a); 403 at /login
  with a plain form ⇒ WALLED, the Wave 8 served-page rule (B2b);
  401/403 JSON at /api ⇒ LOGIN_GATED / WALLED (B2c/B2d).
- Consent boundaries: consent banner on a served page ⇒ OPEN
  (B5a); a consent-only stub ⇒ OPEN — consent is a legal gate,
  not a bot wall (B5b, deliberate pin); consent + human-check
  prose ⇒ CHALLENGED (B5c).
- Cloudflare variants: Attention Required ⇒ WALLED / Cloudflare
  (B6a); Error 1000 ⇒ WALLED / Cloudflare (B6b); Error 522 ⇒
  UNREACHABLE (B6c, verdict was already right — only the vendor
  leaked, fixed by W10-006).
- App gates: PX captcha + app wording ⇒ CHALLENGED / PerimeterX
  (B7a); app-only gate with no markers ⇒ WALLED, vendor none
  (B7b).
- DataDome variants: delivery-host script ⇒ CHALLENGED (B8a);
  x-datadome header alone ⇒ CHALLENGED (B8b); sensor cookie on a
  served page ⇒ OPEN, vendor none (B8c).
- Audit pins: llms redirect to homepage HTML ⇒ FAIL (B9b); empty
  robots.txt ⇒ PASS — empty is valid and permissive, not missing
  (B9c); sitemap HTML 200 ⇒ WARN (B9e).

## Verification

- 32/32 battery fixtures pass; full suite **152/152** (120
  pre-existing pins all green — zero regressions).
- Corpus check: new classifier vs the 44 wave1–7 real captures —
  no verdict changed. The three captures carrying refresh/location
  patterns (npmjs, kickstarter, duolingo) were individually
  verified: npmjs still CHALLENGED / Cloudflare (vendor branches
  outrank redirect evidence), kickstarter and duolingo still OPEN
  (their redirect targets are content targets, so no redirect
  evidence fires). The other 41 captures contain none of the new
  rules' trigger shapes, so their verdicts are unchanged by
  construction.
- SPEC.md updated: geo-refusal rule, 451, redirect-target rules,
  UNREACHABLE vendor rule, audit JSON-error and robots-HTML gates.

## Saturation consequence

This wave found **8 genuine defects** (6 classifier, 2 audit-tool).
Under the overnight saturation test, the clock resets: Wave 10 is
NOT a clean wave, and the two-wave clean pair must restart from
the next defect-free measurement wave.
