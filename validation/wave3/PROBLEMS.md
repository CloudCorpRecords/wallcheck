# Wave 3 — Problems Ledger

Discipline: same as Waves 1–2 — every wrong or shaky verdict is
ledgered, hand-checked against a captured response shape before any
fix; fixes generalize the signal (no per-site special cases) and
land test-first with a regression fixture. Target-side churn is
ledgered in STABILITY.md (Leg A) rather than here; this file is for
classifier defects.

---

## Leg A (stability re-probe) — reviewed, zero classifier defects

Both verdict flips against the Wave 1 final set (npmjs.com
CHALLENGED → UNREACHABLE; amazon.com OPEN → CHALLENGED) were
hand-checked against captures and are target-side churn: npmjs's
wall intermittently kills the connection before responding
(`RemoteDisconnected`; third sighting of the W1-005/W2-004 pattern),
and Amazon newly serves its `/errors_page/validateCaptcha`
interstitial to this client (captures/amazon.json — the
CHALLENGED verdict on that shape is correct). Full analysis:
STABILITY.md. No classifier change, no new fixtures — the fixtures
from Waves 1–2 already pin both shapes (generic marker on a small
2xx interstitial → CHALLENGED; fetch error → UNREACHABLE).

## Leg B (index expansion) — 2 defects, both fixed; 3 reviewed non-defects

## W3-001 — booking.com: OPEN on an AWS WAF challenge page (FALSE OPEN; vendor missing entirely)

- **Observed (round 1):** OPEN, status 202, evidence STATUS_202 only.
- **Expected:** CHALLENGED, vendor AWS WAF.
- **Hand-check (captures/booking.json):** a 7,033-byte page with an
  empty `<title>`, no content, and one job: the inline script runs
  `AwsWafIntegration.getToken()` / `checkForceRefresh()` and reloads
  with a `chal_t` parameter; the `<noscript>` text reads *"In order
  to continue, we need to verify that you're not a robot. This
  requires JavaScript."* This is AWS WAF Bot Control's JS token
  challenge, famously served with status 202. A non-JS agent gets
  no further. Two gaps compounded: wallcheck had **no AWS WAF
  detection at all**, and the generic human-check family ("are you
  a robot") did not cover this page's wording ("not a robot"), so
  no wall signal of any kind fired on a 2xx status.
- **Generalized fix:** (1) AWS WAF becomes a detected vendor —
  `AWS_WAF_MARKER` on the `AwsWafIntegration` body token or an
  `awswaf.com` reference, behind the served-page gate, with a
  verdict rule: marker → CHALLENGED (a JS proof is a challenge at
  any status). (2) "not a robot" joins the generic human-check
  markers, so the same wording without a vendor signature still
  challenges (fixture pins it as Generic).
- **Regression fixtures:** the captured Booking shape (202) →
  CHALLENGED (AWS WAF); the noscript wording alone (202) →
  CHALLENGED (Generic); a >16 KB 200 page *about* AWS WAF → OPEN
  (the gate covers the new vendor).
- **Round 2:** live re-probe → CHALLENGED (AWS WAF), 202. Merged
  into results-expansion.json (round 1 preserved).

## W3-002 — w3schools.com: WALLED correct, vendor under-attributed (Akamai edgesuite)

- **Observed (round 1):** WALLED, status 403, evidence STATUS_403
  only, vendor null.
- **Expected:** WALLED, vendor Akamai.
- **Hand-check (captures/w3schools.json):** a 371-byte classic
  Akamai error page — *"Access Denied … Reference #18.92620317…"*
  with an `errors.edgesuite.net` URL. No `Server: AkamaiGHost`,
  no Bot Manager cookie: none of the existing Akamai signals
  (W1-003's set) are present on this response shape. (Same failure
  family as W1-003/W1-004: a known vendor, an uninstrumented
  signal.)
- **Generalized fix:** `AKAMAI_EDGESUITE` body marker, behind the
  served-page gate — matched on the bare token `edgesuite`
  because the real page HTML-encodes the dots
  (`edgesuite&#46;net`); the first version of this fix matched
  "edgesuite.net" and failed against both the fixture and the
  live page, which is why fixtures are built from captured shapes.
  Same treatment as DataDome's captcha-delivery.com host (W1-008).
- **Regression fixture:** the captured edgesuite shape → WALLED
  (Akamai) with AKAMAI_EDGESUITE.
- **Round 2:** live re-probe → WALLED (Akamai), 403. Merged.

## W3-003 — reviewed, not defects

- **flexjobs.com UNREACHABLE (read timeout)** — reproduced on an
  independent capture minutes later (captures/flexjobs.json, same
  TimeoutError). The fetch genuinely fails from this client; per
  SPEC no wall verdict is claimed (W1-006 precedent).
- **crates.io OPEN with status 404** — the root answers this client
  a 404 with an empty body (captured). A served answer, status on
  the record; nothing wall-like intervened (W1-007 precedent).
- **expedia.com RATE_LIMITED (429)** — a plain throttle response,
  STATUS_429 the only evidence. Recorded as measured; per wave
  discipline the target was not retried.
- **Spot-checks of surprising OPENs** — airbnb.com and
  kickstarter.com both captured full 64 KB homepages with real
  titles (captures/): the OPEN verdicts are honest for this
  client, however aggressive these platforms are to others.

## Leg C (owner audit) — 1 defect in the new tool, fixed

## W3-004 — audit: a soft-404 at /openapi.json suppressed the /api fallbacks

- **Observed (first live audits):** clipwise.replit.app's api
  check failed on two `OPENAPI_NOT_SPEC` evidence lines alone —
  the `/api` and `/developers` probes were never fetched.
- **Root cause:** `audit_site` treated any 200 at the OpenAPI
  candidate paths as "spec found" and skipped the fallback
  probes. But a single-page app serves its HTML shell with 200 at
  *every* unknown path (the same soft-404 species as W3-001's
  llms trap), so the shell suppressed the fallbacks and could
  have hidden a real /api.
- **Generalized fix:** spec-found now requires the body to parse
  as an OpenAPI/Swagger document (`_is_openapi_doc`, shared by
  the router and the check so they cannot drift). The api check
  also gained the shell test: a 200 candidate whose HTML body is
  byte-identical to the homepage's body is the SPA fallback, not
  a surface (`API_ROOT_IS_APP_SHELL` / `DEV_PORTAL_IS_APP_SHELL`
  evidence). Re-audited clipwise: api FAIL stands, now on
  evidence — the shell is *named*.
- **Regression fixture:** SPA-shell site with a JSON-serving /api
  → api PASS via API_ROOT_200 (fails before the fix).
- **Known scope note (not a defect):** the audit discovers an
  API surface on the audited domain's own well-known paths.
  GitHub's API lives on api.github.com, so github.com grades
  api=WARN (developer portal) — the per-domain contract is
  documented in AUDITS.md.
