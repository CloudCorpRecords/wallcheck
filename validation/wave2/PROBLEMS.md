# Wave 2 — Problems Ledger

Discipline: same as Wave 1 — every wrong or shaky verdict is ledgered,
hand-checked against a captured response shape (captures/*.json)
before any fix; fixes generalize the signal (no per-site special
cases) and land test-first with a regression fixture.

Round 1: 77 path probes across 11 platforms. Hand-triage found one
defect family with three faces (W2-001), one false wall (W2-002), and
one under-call (W2-003). Round 2 re-probed the 6 affected paths after
the fixes; `results-paths.json` is the merged final set
(`results-paths-round1.json` preserved).

---

## W2-001 — the login-URL heuristic pre-empts walls and invents gates

Three round-1 verdicts, one root cause: `_is_login(final_url)` ran
before the wall rules finished and before the bare-403 rule, on any
status.

- **guru.com/login — LOGIN_GATED, truth WALLED (Imperva).** Capture
  (captures/guru-login.json): an 883-byte Incapsula deny page on 403
  at the /login URL itself — the wall fired before any login form
  existed. Worse, Imperva had *no verdict rule at all* in v0.1: guru's
  homepage only reached WALLED via the bare-403 fallthrough, which
  the login heuristic pre-empted here.
- **ebay.com/signin/ — LOGIN_GATED on a 403 Akamai deny.** Capture
  (captures/ebay-signin.json): AkamaiGHost "Error Page | eBay" with a
  `bm_so` Bot Manager cookie at signin.ebay.com. Not a login form — a
  deny. (Across attempts this host flips: the merged final records a
  served 200 login form, LOGIN_GATED — both shapes are real; Bot
  Manager scoring varies per request.)
- **monster.com/profile/login + contra.com/login — LOGIN_GATED on
  404s.** Captures: Monster's real "Page Not Found" page (64 KB) and
  Contra's "Page not found" page, both definitive 404s at
  login-marked URLs. A 404 is a served answer, not a gate
  (Wave 1 precedent, W1-007).

**Generalized fixes (all in classify.py):**

1. Imperva gets a verdict rule: IMPERVA_BODY_MARKER on 401/403 →
   WALLED, alongside the DataDome/Akamai rules.
2. Akamai Bot Manager deny shape: status 403 + AKAMAI_SERVER_HEADER +
   a BM cookie → WALLED. Both signals required and the status pinned
   to 403, so served pages and plain 401 auth responses that merely
   carry BM cookies are untouched.
3. The login heuristic no longer applies on error statuses where it
   was guessing: it is skipped on 403 (a wall rule or the bare-403
   default owns the verdict), 404, and 410. Served login pages (2xx)
   and redirect chains landing on login URLs still classify
   LOGIN_GATED (fixtures pin both directions, including
   bare-403-at-login-URL → WALLED).

**Regression fixtures:** guru login shape → WALLED Imperva; ebay
signin shape → WALLED Akamai; monster 404-at-login shape → OPEN with
STATUS_404 (DataDome marker kept as evidence); bare 403 at a login
URL → WALLED.

## W2-002 — nytimes.com/llms.txt: CHALLENGED on a 404 page (FALSE WALL)

- **Observed:** CHALLENGED (Generic), status 404, evidence
  GENERIC_CAPTCHA only.
- **Hand-check (captures/nytimes-llms.json):** NYT's real "Not Found"
  page, 47 KB; the word "captcha" appears in page scripts. Nothing
  challenged anyone — the file does not exist and the server said so.
- **Root cause:** generic markers are the weakest signal in the
  classifier (a bare keyword), and they verdict-drove on *any*
  status, including definitive ones.
- **Generalized fix:** generic captcha/human-check markers only drive
  a CHALLENGED verdict on wall-plausible statuses — 401, 403, 429,
  503, or a 2xx interstitial (the served-page gate already excludes
  full 2xx pages). On 404/410 the response falls through to the
  status rules. The evidence code is still recorded; it just can't
  manufacture a wall out of a not-found page.
- **Regression fixtures:** large 404 with a captcha mention → OPEN,
  STATUS_404; generic captcha on 403 → still CHALLENGED.

## W2-003 — indeed.com login: OPEN on a served SSO sign-in page (under-call)

- **Observed (round 1):** OPEN, 200. Final URL
  `https://secure.indeed.com/auth;jsessionid=...` — capture
  (captures/indeed-login.json) title: "Sign In | Indeed Accounts".
  A real login wall, served politely.
- **Root cause:** `_is_login` used substring markers (`/login`,
  `/auth/login`, …); Indeed's SSO path segment is `auth` with a
  `;jsessionid` path parameter, which matches none of them.
- **Generalized fix:** segment-based matching — a path segment that is
  exactly `auth` (path params stripped) or contains a login word
  marks a login URL. Pinned against over-matching: `/author/...` and
  `/authenticate/...` classify OPEN.
- **Regression fixtures:** indeed auth-segment shape → LOGIN_GATED;
  author/authenticate shapes → OPEN.

## W2-004 — connection kills on walled domains (observed, not a defect)

guru.com/sitemap.xml, nytimes.com/section/world, and
npmjs.com/search each died with `RemoteDisconnected` (server closed
the connection without responding) — the same shape as Wave 1's
W1-005 (npmjs round 1). Per SPEC the verdict is UNREACHABLE and no
wall verdict is claimed; recorded here so the pattern stays visible:
3 of 3 kills happened on domains that wall this client on every
comparable path.

## W2-005 — nytimes.com/sitemap.xml: WALLED, vendor unattributed (by design)

A bare 403 on the sitemap with no vendor signal on the response (no
DataDome header this time, unlike the homepage). The bare-403 rule
verdicts WALLED and no vendor is claimed — attribution without
evidence would be invention. Notable as data (PATHS.md): the one file
built for machines is blocked while robots.txt serves.

## W2-006 — operations: first runner died mid-wave (recovered)

The first Wave 2 run's detached process was reaped after 26 of 77
probes and its end-of-run JSON write never happened. The wave was
re-run in full as a tracked foreground process, and the runner now
saves results incrementally after every probe. Round-1 file labels in
this directory refer to the full re-run.
