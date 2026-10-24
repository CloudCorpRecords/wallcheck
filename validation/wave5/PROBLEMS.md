# Wave 5 — Problems Ledger

Discipline: same as Waves 1–4 — every wrong or shaky verdict is
ledgered, hand-checked against a captured response shape before
any fix; fixes generalize the signal (no per-site special cases)
and land test-first with a regression fixture built from the
capture. Target-side churn is ledgered in STABILITY-3.md (Leg A)
rather than here; this file is for classifier defects and the
hand-checks that cleared the classifier.

Wave 5's territory (104 new real-task surfaces) produced **five
defects, all fixed**, and the fixes added three vendors to the
classifier's vocabulary. All five were verified against the live
targets after the fix; the affected rows were re-probed (round 2)
and merged into `results-expansion2.json` (round 1 preserved in
`results-expansion2-round1.json`).

---

## Leg A (round 4 stability) — reviewed, zero classifier defects

153 of 154 verdicts identical to round 3; the single flip
(npmjs.com CHALLENGED → UNREACHABLE) is the known transport
pattern, hand-checked and held at CHALLENGED in the index per the
established merge rule. Full analysis: STABILITY-3.md. No
classifier change from Leg A — every Wave 5 defect came from the
new territory in Leg B, which is what expansion is for.

## Leg B (expansion 2) — 5 defects, all fixed

## W5-001 — duolingo.com: CHALLENGED on a fully served homepage (FALSE CHALLENGE)

- **Observed (round 1):** CHALLENGED, vendor Generic, status 200,
  evidence GENERIC_CAPTCHA only.
- **Expected:** OPEN.
- **Hand-check (captures/duolingo.json):** a real 11,219-byte
  homepage — full document, navigation, product copy — served 200
  by `duo-api`. The word "captcha" appears exactly twice, both
  inside one quoted string: the page loads
  `https://www.recaptcha.net/recaptcha/enterprise.js?render=…`
  for its own forms. This is the Wave 1 GitHub species (a served
  page embedding a captcha widget) in a new shape: the W1 fix was
  the 16 KB served-page gate, and at 11 KB this homepage slips
  under it. A widget *include* is not a challenge; nothing asked
  this agent to solve anything.
- **Generalized fix:** the generic-CAPTCHA scan now runs on the
  body with quoted strings that reference third-party captcha
  *loader* hosts blanked out (`_CAPTCHA_LOADER_RE`: quoted spans
  containing `recaptcha` or `hcaptcha`). The word in prose is
  untouched and still verdict-drives (pinned); loader includes
  for reCAPTCHA Enterprise, reCAPTCHA, and hCaptcha are presence.
- **Regression fixtures:** the captured shape (small 200 +
  recaptcha.net enterprise loader) → OPEN; an hCaptcha loader
  script tag on a served page → OPEN; prose "complete the captcha
  below" on a small 200 → still CHALLENGED (Generic).
- **Round 2:** live re-probe → OPEN, 200. Merged.

## W5-002 — ed.gov: CHALLENGED correct, vendor missing entirely (Microsoft Azure WAF)

- **Observed (round 1):** CHALLENGED, vendor Generic (GENERIC_CAPTCHA),
  status 403.
- **Expected:** CHALLENGED, vendor Microsoft Azure WAF.
- **Hand-check (captures/ed.json):** the page titles itself
  "Azure WAF"; its visible text is "Please enable JavaScript to
  run this application" plus a reference ID; its styles live in
  the `--azwaf-*` CSS namespace (32 hits) and its scripts load
  from `/.azwaf/captcha/proxied/…` — Azure WAF's JS/CAPTCHA
  challenge page. The verdict was right by accident (the generic
  marker matched "captcha" in the asset paths); the vendor —
  a top-three cloud WAF — was not in wallcheck's vocabulary at
  all. Same gap family as W3-001 (AWS WAF).
- **Generalized fix:** Azure WAF becomes a detected vendor —
  `AZURE_WAF_MARKER` on the `azwaf` body token or "Azure WAF"
  wording, behind the served-page gate, with a verdict rule
  parallel to AWS WAF's: marker → CHALLENGED (a JS proof page is
  a challenge at any status).
- **Regression fixtures:** the captured shape (403) →
  CHALLENGED (Microsoft Azure WAF); a >16 KB 200 page *about*
  azwaf → OPEN (gate covers the new vendor).
- **Round 2:** live re-probe → CHALLENGED (Microsoft Azure WAF),
  403. Merged.

## W5-003 — chewy.com: RATE_LIMITED correct, vendor misattributed (Kasada unrecorded)

- **Observed (round 1):** RATE_LIMITED, vendor Akamai, status 429,
  evidence AKAMAI_BM_COOKIE + STATUS_429.
- **Expected:** RATE_LIMITED, vendor Kasada.
- **Hand-check (captures/chewy.json):** the 429's whole body
  (677 bytes) is Kasada's payload — `window.KPSDK={}…` and its
  sensor script. Akamai is present only as a Bot Manager cookie:
  a sensor that rode along (presence, per the W1 PX-cookie
  demotion). The wall that answered is Kasada's; Kasada was not
  in the vocabulary.
- **Generalized fix:** `KASADA_MARKER` on the `kpsdk`/`kasada`
  body token (served-page gated like every body marker — Kasada
  sensors ride real pages too). Attribution: in classify()'s
  vendor-semantics step, a Kasada marker overrides an
  Akamai attribution that rests on presence signals alone — the
  PerimeterX-over-CDN principle (the wall that fired outranks the
  sensor that rode along). A genuine Akamai deny shape
  (edgesuite page, bm-verify) keeps Akamai. The verdict is NOT
  changed: a sensor payload is presence, never a verdict (the
  PX_COOKIE precedent) — Kasada's verdict semantics on non-429
  statuses are an open question, deliberately not legislated from
  a single 429 specimen.
- **Regression fixture:** the captured shape (429 + ak_bmsc
  cookie + KPSDK stub) → RATE_LIMITED (Kasada), both evidence
  codes present.
- **Round 2:** live re-probe → RATE_LIMITED (Kasada), 429. Merged.

## W5-004 — redfin.com: WALLED correct, vendor unattributed (AWS CloudFront block page)

- **Observed (round 1):** WALLED, vendor null, status 403,
  evidence STATUS_403 only.
- **Expected:** WALLED, vendor AWS CloudFront.
- **Hand-check (captures/redfin.json):** a 919-byte page served
  by CloudFront: "ERROR: The request could not be satisfied …
  Request blocked. We can't connect to the server for this app
  or website at this time." — CloudFront's generated block page.
  (Same attribution family as W3-002's edgesuite page: a known
  vendor, an uninstrumented signature.)
- **Generalized fix:** `AWS_CLOUDFRONT_BLOCK` on the body
  containing **both** "request could not be satisfied" and
  "request blocked" — the first phrase alone is also
  CloudFront's origin-error wording, so the pair is the block
  signature. Attribution only; the bare-403 rule already owns
  the verdict.
- **Regression fixtures:** the captured shape → WALLED
  (AWS CloudFront); the same page minus the "Request blocked"
  line → WALLED, vendor null (over-match pin).
- **Round 2:** live re-probe → WALLED (AWS CloudFront), 403.
  Merged.

## W5-005 — delta.com: OPEN on an Akamai deny page served as 444 (FALSE OPEN — the wave's worst)

- **Observed (round 1):** OPEN, status 444, evidence
  AKAMAI_SERVER_HEADER + STATUS_444.
- **Expected:** WALLED, vendor Akamai.
- **Hand-check (captures/delta.json):** the body is Akamai's
  classic deny page — "Access Denied / You don't have
  permission to access this server. / Reference
  0.116bdc17.1792816805.402e199e" — served by AkamaiGHost with
  status **444**. Two generalized gaps compounded: (1) the
  Akamai deny attribution knew the edgesuite page (W3-002) but
  not the dotted-reference page, and the W2-001 deny verdict
  rule is pinned to 403 + BM cookies, neither of which is here;
  (2) status 444 fell through the verdict chain to the final
  else and came out OPEN — but 444 means the server closed the
  request without serving content, so OPEN ("the resource was
  served") is definitionally false for it. An agent trusting
  this verdict would believe Delta served it a page it was
  explicitly denied.
- **Generalized fix:** (1) `AKAMAI_REFERENCE` body marker — the
  dotted reference token (`reference\s+#?\d+\.[0-9a-f]{4,}`) on a
  non-served page attributes the deny to Akamai. (2) A verdict
  rule for 444 itself: `STATUS_444 → WALLED` (a deliberate drop
  is a refusal), placed after the login branch and before the
  2xx/3xx OPEN branch.
- **Regression fixtures:** the captured shape (444 + GHost +
  reference page) → WALLED (Akamai) with AKAMAI_REFERENCE; a
  bare 444 with no signals → WALLED, vendor null.
- **Round 2:** live re-probe → WALLED (Akamai), 444. Merged.
- **Open question, recorded not legislated:** other nonstandard
  refusal statuses (e.g. 451) still fall through to the legacy
  else. No specimen this wave; the rule changes when a capture
  demands it.

## W5-006 — reviewed, not defects

- **state.gov WALLED, vendor null (captures/state.json)** — a
  64 KB custom "Technical Difficulties" page served from S3 on a
  403. No vendor signature exists in the response; bare-403 →
  WALLED is exactly SPEC's rule, and inventing an attribution
  would be worse than none.
- **hyatt.com WALLED, vendor null (captures/hyatt.json)** — a
  custom multilingual deny page ("We're sorry. Your browser did
  something unexpected…"), 403, no vendor signals. Same
  reasoning as state.gov.
- **hilton.com UNREACHABLE (round 1) → WALLED (round 2)** — the
  round-1 probe read-timed-out at 15 s; the hand-check capture
  (25 s budget) was answered 403 by an Akamai-fronted branded
  deny page, and the standard-contract re-probe then returned
  WALLED (Akamai) 403 inside 15 s. Target-side instability
  (a slow wall is still a wall); merged at round 2 with the
  round-1 record preserved. Not a classifier defect.
- **etrade.com, united.com, kroger.com UNREACHABLE** — read
  timeouts reproduced on independent captures at a 25 s budget
  (captures/etrade.json, united.json, kroger.json). The fetches
  genuinely fail from this client; per SPEC no wall verdict is
  claimed (flexjobs precedent, W3-003).
- **hotels.com, vrbo.com, realtor.com RATE_LIMITED (429)** —
  plain throttle responses, STATUS_429 the only evidence.
  Recorded as measured; per wave discipline the targets were
  not retried (expedia precedent).
- **Spot-check of a surprising OPEN — zillow.com** (captures/
  zillow.json): a full 64 KB real homepage served 200. The OPEN
  is honest for this client, in the same index where Redfin,
  Apartments.com and Homes.com wall — the real-estate split is
  the targets' policy difference, not classifier noise.

## Leg C — no defects

The signed-vs-unsigned experiment ran clean; its one surprise
was operational, not classificatory: see SIGNED-EXPERIMENT.md.
Its npmjs.com data point also fed STABILITY-3.md (the wall
served its challenge properly to the experiment's fetches).

## Leg D — one defect, in our own house (not the classifier)

The owner audit's Wave 3 grades were re-confirmed by hand in
Wave 5: clipwise.replit.app serves its SPA shell at both
`/llms.txt` and `/sitemap.xml` (a live soft-404 on our own
property), and reneturcios.replit.app 404s all three machine
files. The fixes are staged in `fix-kit/` with deploy steps in
`fix-kit/README.md`; deployment itself is out of this wave's
hands (the sources live only on Replit — see
`fix-kit/README.md`).
