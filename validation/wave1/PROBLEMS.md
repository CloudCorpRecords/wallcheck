# Wave 1 — Problems Ledger

Discipline: every wrong or shaky verdict from round 1 is ledgered here,
hand-checked against a captured response shape (captures/*.json) before
any fix. Fixes must generalize the signal — no per-site special cases —
and each lands with a regression fixture built from the captured shape.

Round 1: 58 targets, verdicts OPEN 44 / CHALLENGED 6 / WALLED 4 /
UNREACHABLE 4. Client context: this VM, datacenter egress, honest
wallcheck UA, one fetch per target.

---

## W1-001 — techcrunch.com: CHALLENGED on a served 200 page (FALSE WALL)

- **Observed:** CHALLENGED (Cloudflare), status 200, evidence
  CF_CHALLENGE_PLATFORM only.
- **Expected:** OPEN.
- **Hand-check (captures/techcrunch.json):** status 200, 64 KB+ of the
  real homepage (title "TechCrunch | Startup and Technology News").
  `challenges.cloudflare.com` appears only as a `<link rel=dns-prefetch>`
  hint — a connection hint for a widget the page *may* load, not a
  challenge that fired.
- **Root cause:** Cloudflare *body* markers (CF_JUST_A_MOMENT,
  CF_CHALLENGE_PLATFORM, CF_BLOCK_SORRY) are verdict-driving at any
  status/size. The v0.1 dogfood fix gated only the *generic* markers.
- **Generalized fix:** one served-page gate for all body-derived wall
  markers — they count only when the response is not a full served page
  (not 2xx-with-large-body). Header signals (cf-mitigated: challenge)
  stay authoritative at any size.
- **Regression fixture:** large 200 page with Cloudflare headers and a
  challenges.cloudflare.com dns-prefetch → OPEN.

## W1-002 — walmart.com, target.com: CHALLENGED on served 200 pages (FALSE WALL)

- **Observed:** both CHALLENGED (PerimeterX), status 200. Walmart via
  PX_BODY_MARKER; Target via PX_COOKIE alone.
- **Expected:** OPEN (both).
- **Hand-check (captures/walmart.json, captures/target.json):** both
  200 with 64 KB+ of the real homepages. Walmart's "perimeterx" string
  is a Content-Security-Policy domain allowlist entry
  (`*.perimeterx.net`); Target's only signal is an `_pxhd` cookie —
  sensor presence on a fully served page, the same class as the
  `ak_bmsc` cookie v0.1 already treats as presence-only.
- **Root cause:** PX body markers not gated (same gap as W1-001), and
  PX_COOKIE alone drives a CHALLENGED verdict.
- **Generalized fix:** PX_CAPTCHA / PX_BODY_MARKER go behind the same
  served-page gate; PX_COOKIE becomes presence-only evidence (never
  verdict-driving on its own), matching the Akamai cookie treatment.
  A small 200 interstitial with a real px-captcha container still
  classifies CHALLENGED (fixture pins this).
- **Regression fixtures:** large 200 with CSP perimeterx mention → OPEN;
  200 with only an _pxhd cookie → OPEN with PX_COOKIE as presence
  evidence; small 200 px-captcha interstitial → CHALLENGED.

## W1-003 — ebay.com: WALLED correct, vendor under-attributed

- **Observed:** WALLED, status 403, vendor null (evidence STATUS_403
  only).
- **Hand-check (captures/ebay.json):** 403 Akamai error page —
  `Server: AkamaiGHost` and a `bm_so` cookie (Akamai Bot Manager).
- **Root cause:** Akamai detection only knows the `ak_bmsc` cookie and
  `bm-verify` body marker.
- **Generalized fix:** add the standard Akamai signals to the evidence
  set: server header containing "akamai" (AKAMAI_SERVER_HEADER) and Bot
  Manager cookies `bm_so` / `bm_sv` (AKAMAI_BM_COOKIE).
- **Regression fixture:** the captured eBay shape → WALLED, Akamai.

## W1-004 — guru.com: WALLED correct, vendor missing entirely (Imperva)

- **Observed:** WALLED, status 403, vendor null.
- **Hand-check (captures/guru.json):** 403 block page loading
  `/_Incapsula_Resource?...` with an incident iframe, `incap_ses_*`
  cookie set — this is Imperva (Incapsula). wallcheck has no Imperva
  detection at all.
- **Generalized fix:** add Imperva detection: `incap_ses` / `visid_incap`
  cookies (IMPERVA_COOKIE), "incapsula" body/resource markers
  (IMPERVA_BODY_MARKER, behind the served-page gate) → vendor "Imperva".
- **Regression fixture:** the captured Guru shape → WALLED, Imperva.

## W1-005 — npmjs.com: round-1 UNREACHABLE was transient; the site is CHALLENGED

- **Observed (round 1):** UNREACHABLE, `RemoteDisconnected` at ~0.8 s.
- **Hand-check (captures/npmjs.json, minutes later):** full Cloudflare
  challenge page — 403, `cf-mitigated: challenge`, "Just a moment...",
  which the *current* classifier already verdicts CHALLENGED
  (Cloudflare) correctly.
- **Disposition:** not a classifier defect; the wall killed the first
  connection before responding. Final verdict deferred to the round-2
  re-probe. Ledgered so the round-1 UNREACHABLE is never quoted as the
  site's state.

## W1-006 — replit.com, discord.com, bestbuy.com: UNREACHABLE, reproducible

- **Observed:** UNREACHABLE (15 s timeouts) in round 1 *and* again on
  independent diagnostic captures minutes later (bestbuy: read timeout;
  replit/discord: connect/read timeout).
- **Disposition:** reviewed, verdict honest per SPEC — the fetch
  genuinely fails from this client; no wall verdict is claimed. Not a
  classifier defect. Round-2 re-probe included for stability; the Index
  records whatever the final round observes, with the error as evidence.

## W1-007 — cloudcorprecords.github.io: 404 classified OPEN (reviewed, kept)

- **Observed:** OPEN, status 404 (GitHub Pages serves its 404 page; no
  user site is published at the root).
- **Disposition:** reviewed and kept. Nothing wall-like stops the agent;
  the response was served. SPEC's OPEN covers a served response, and the
  Index seed carries the raw status column, so the 404 is on the record,
  not smoothed over. Not a defect.

## W1-008 — DataDome body signal misses its own captcha host (hardening)

- **Observed:** nytimes.com / monster.com verdicts are correct
  (CHALLENGED, DataDome, 403) but rest entirely on the `x-datadome`
  header; both captured bodies reference `geo.captcha-delivery.com`
  (DataDome's captcha host) without the string "datadome", so
  DD_BODY_MARKER never fires. If a proxy strips the header, vendor
  attribution would be lost.
- **Generalized fix:** treat `captcha-delivery.com` in the body as a
  DataDome body marker (behind the served-page gate).
- **Regression fixture:** 403 with a captcha-delivery.com body reference
  and no DataDome header → CHALLENGED, DataDome.
