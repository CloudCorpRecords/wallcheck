# Wave 8 — Depth wave 2: problems ledger

One classifier defect found by the 322-probe path wave, fixed
test-first with a generalized rule. Everything else below was
reviewed as a suspect and cleared, with the reason on the record —
cleared suspects are not defects, and re-reporting them as defects
in a later wave would be an error.

## W8-001 — Login heuristic fired on a 444 Akamai deny (FIXED)

**Shape.** Delta's `/login` probe returned status 444 with Akamai
deny evidence (`AKAMAI_SERVER_HEADER`, `AKAMAI_REFERENCE`) and an
empty redirect chain — no redirect happened. The classifier
returned LOGIN_GATED.

**Cause.** The login-heuristic branch excluded only statuses
(403, 404, 410) — the Wave 2 (W2-001) set. 444 was not in it, so a
login-URL 444 fell into LOGIN_GATED instead of the 444 branch
below it (WALLED). The `REDIRECT_TO_LOGIN` evidence on the row was
appended by the verdict branch itself, not observed: the chain was
empty and the final URL was the requested URL. A 5xx at a login
URL had the same hole (it would also have read LOGIN_GATED).

**Fix (generalized, not a status added to a list).** The branch
now requires a served page: `200 <= status < 400`. Any 4xx/5xx at
a login URL takes the error's verdict — 444 → WALLED, 5xx →
UNREACHABLE, 403 → WALLED, 404/410 → OPEN — exactly as the
branches below already define. The 401 branch above is untouched
(a 401 is a genuine auth-required response).

**Tests.** Two new tests in `tests/test_classify.py`, written
before the fix, both failing before and passing after:
`test_444_at_login_url_is_walled_not_gated` (delta shape, expects
WALLED/Akamai) and
`test_500_at_login_url_is_unreachable_not_gated` (expects
UNREACHABLE). Full suite after the fix: 114/114 (was 112/112).

**Live verification.** Delta `/login` re-probed once with the
fixed classifier: WALLED, Akamai, 444, evidence
`AKAMAI_SERVER_HEADER + AKAMAI_REFERENCE + STATUS_444`. The row
in `results-paths2.json` was corrected to the re-probed verdict;
the original probe time is retained on the row. Post-fix wave
distribution: OPEN 94 · WALLED 145 · CHALLENGED 54 ·
RATE_LIMITED 20 · UNREACHABLE 6 · LOGIN_GATED 3.

**SPEC.** `SPEC.md` verdict-precedence note updated: the login
heuristic fires only on served pages (2xx/3xx).

## Reviewed and cleared (not defects)

**CareerBuilder `/api` → UNREACHABLE at status 500.** Correct per
SPEC: UNREACHABLE covers "the fetch itself failed … or the server
returned 5xx." A served 500 claims no wall verdict. The row stands.

**Zillow `/robots.txt` → CHALLENGED (PerimeterX) at status 200.**
A PerimeterX challenge body served with 200 at the robots path.
This is the Wave 6 JS-proof-stub rule working as designed (a proof
page is a challenge whatever status it carries), not a false
positive — and it is the wave's only control anomaly: zillow's
homepage serves 200 while its robots.txt is challenge-gated for
this client. Noted in PATHS-2.md, not fixed.

**Uber Eats `/api` → CHALLENGED (Cloudflare) at status 404.**
Cloudflare challenge-platform markers on a 404-status response:
the challenge fired on a nonexistent path. Vendor wall evidence
outranks status by design. Correct.

**CareerJet home → CHALLENGED (Cloudflare) at status 200.**
Same JS-proof-stub shape as zillow robots. Correct per the Wave 6
rule; careerjet's login page itself serves a genuine 200 form.

**Bare-403 unattributed walls (state.gov, hyatt, haaretz — all 7
paths each; Expedia-family sitemap/llms paths).** Bodies carry no
vendor signals at all, only STATUS_403. The classifier correctly
reports vendor None: attribution requires evidence, and a bare
deny supplies none. These are a story (denial without
identification), not a classification failure. The index already
records state.gov as a custom deny and hyatt/haaretz as
unattributed.

**UNREACHABLE scatter (6 rows: bls.gov home + sitemap, hilton
signup, emirates login, homedepot signup, careerbuilder api is the
500 above — counted separately).** Five transport failures plus
one served 500, spread across hosts and paths with no clustering
by host, path, or time window. No runner defect indicated (contrast
Wave 7's 52-row proxy-poisoning window, which clustered and
carried proxy errors). Each stands as UNREACHABLE per SPEC.

**Chewy home → RATE_LIMITED (Kasada) with an Akamai BM cookie
present.** The Wave 5 Kasada-precedence fix holds: the Kasada
marker outranks Akamai CDN presence. Correct, and a confirming
re-test of the Wave 5 fix.
