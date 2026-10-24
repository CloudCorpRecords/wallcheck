# Wave 10 — Problems ledger

## Leg B (adversarial battery v2) — 8 defects, all fixed

- **W10-001** (classifier, fixed): 200 geo-block stub read OPEN.
  Fix: geo-refusal phrasing on < 4 KB pages ⇒ WALLED (verdict-only
  signal). Fixture: test_b3b_200_geo_block_page.
- **W10-002** (classifier, fixed): 451 read OPEN. Fix: 451 ⇒ WALLED
  (STATUS_451), parallel to 444. Fixture: test_b3c_451_legal.
- **W10-003** (classifier, fixed): meta-refresh to /challenge/
  read OPEN. Fix: redirect-target challenge tokens ⇒ CHALLENGED.
  Fixture: test_b4a_refresh_to_challenge.
- **W10-004** (classifier, fixed): meta-refresh to /login read
  OPEN. Fix: redirect-target login path ⇒ LOGIN_GATED. Fixture:
  test_b4b_refresh_to_login.
- **W10-005** (classifier, fixed): JS redirect to a verification
  challenge read OPEN. Fix: same redirect-target rule as W10-003.
  Fixture: test_b4c_js_redirect_to_verify.
- **W10-006** (classifier, fixed): 5xx UNREACHABLE carried a vendor
  (Cloudflare 522). Fix: UNREACHABLE ⇒ vendor None. Fixture:
  test_b6c_error_522.
- **W10-007** (audit tool, fixed): /llms.txt JSON error document
  read PASS. Fix: JSON body with error/errors key ⇒ FAIL
  (JSON_ERROR_DOC). Fixture: test_b9a_llms_json_error.
- **W10-008** (audit tool, fixed): /robots.txt HTML soft-404 read
  PASS. Fix: HTML gate mirrored into the robots check
  (SOFT_404_HTML ⇒ FAIL). Fixture: test_b9d_robots_html_soft404.

All fixes generalized (no per-shape or per-site special cases) and
regression-checked against the full suite (152/152) and the 44
real-capture corpus (zero verdict changes).

## Leg A (round-6 stability) — churn only, 1 row merged

499/499 probed; 7 raw-history flips, 5 hand-checked with fresh
captures (see STABILITY-5.md): four one-round flaps
(chicagotribune, forbes, webex, amazon's intermittent
interstitial) held at standing verdicts; britishairways.com's
timeout reproduced twice → merged UNREACHABLE (transport, not a
wall); otta.com and careerbuilder.com round-5 timeouts were
already-held transport noise corroborated by round 6. Zero
classifier defects in this leg. Classifier-version note: round 6
ran with the pre-Wave-10 classifier (runner started before the
fixes landed), so round 5 vs round 6 is apples-to-apples; a
fix-driven reclassification of the index is round 7's job.

## Leg C (signing regression) — no regression

Fresh Ed25519 key on the 0.5.0-rc path: self-verify ok, tamper
rejected, directory document renders. Signed vs unsigned on 4
adopters + 3 walled controls: 7/7 unchanged (see SIGNED-RC.md).
No version bump for the Wave 10 fixes (unreleased fixes on the
rc tree, not a new rc).
