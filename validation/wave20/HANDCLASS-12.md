# Wave 20 — Battery v12: Hand classifications (written BEFORE running any shape)

Shapes are hand-classified here first; the test file then checks
the classifier against these verdicts. A mismatch is either a
classifier defect (fix test-first, generalized) or a hand
correction (justified in PROBLEMS.md, never a silent flip).

Conventions: ARTICLE/BIG_ARTICLE as in test_adversarial11.py
(BIG_ARTICLE > 16 KB, so the served-page gate applies).
"Small page" = a stub page, no real content.

## M1 — iframe-src challenge (routing species, new)

An <iframe> src is a routing directive like a meta refresh, a JS
location, a Refresh header, or a form action (Waves 10/11/12/15):
a page whose only content routes the client to a challenge is a
challenge by reference, and to a login is a gate by reference.
The served-page gate protects real pages embedding frames.

- M1a: content-free page, single iframe
  src="https://challenge.example/captcha/verify", no other text
  → CHALLENGED (the frame IS the page; it routes to a challenge).
- M1b: small page, iframe src="https://content.example/article"
  → OPEN (a content target is routing, not a gate).
- M1c: BIG_ARTICLE embedding an iframe with a captcha src
  → OPEN (served-page gate: the frame is furniture on real
  content, like a comment-form captcha loader).
- M1d: content-free page, single iframe src="/login"
  → LOGIN_GATED (the frame routes to a login; the login species
  of M1a).

## M2 — localized JS-proof phrases (new language ground)

A browser-verification stub is a challenge whatever language it
is written in — the Wave 6/11/12/17/19 localized human-check
principle, applied to the JS_PROOF family, which is still
English-only. Each phrase is a full interstitial sentence, not a
fragment.

- M2a DE: small page "Wir überprüfen Ihren Browser, bitte
  warten." → CHALLENGED.
- M2b FR: small page "Nous vérifions votre navigateur, veuillez
  patienter." → CHALLENGED.
- M2c ES: small page "Estamos verificando su navegador, por
  favor espere." → CHALLENGED.
- M2d PT: small page "Estamos verificando o seu navegador,
  aguarde." → CHALLENGED.
- M2e JA: small page "ブラウザを確認しています。お待ちください。"
  → CHALLENGED.
- M2f DE phrase on BIG_ARTICLE → OPEN (served-page gate: a
  mention on real content is presence, not a stub).

## M3 — new localized human-check languages

Same principle as M2, for the human-check family: challenge
pages are not English-only, and the list still misses whole
language families.

- M3a UK: small page "Підтвердіть, що ви не робот"
  → CHALLENGED.
- M3b HI: small page "कृपया पुष्टि करें कि आप रोबोट नहीं हैं"
  → CHALLENGED.
- M3c MS: small page "sahkan bahawa anda bukan robot"
  → CHALLENGED.
- M3d TL: small page "kumpirmahin na hindi ka robot"
  → CHALLENGED.
- M3e SW: small page "thibitisha kuwa wewe si roboti"
  → CHALLENGED.
- M3f UK phrase on BIG_ARTICLE → OPEN (served-page gate).
- M3g small page with only the fragment "не робот" (no listed
  phrase — a fragment, not a sentence) → OPEN (fragments do not
  fire; the J7g guessing boundary).

## M4 — identity-verification interstitials

"Verify your identity" is a human-verification demand, not an
account login: no credentials are entered, no account is named.
It belongs with the human-check family (cf. Wave 11 "verify
your request" → JS_PROOF), not with the login family — unless
it appears on a login page or with a sign-in step, where the
login yield owns it.

- M4a: small page "Please verify your identity to continue."
  → CHALLENGED.
- M4b: the same phrase on a page at a login URL
  → LOGIN_GATED (login yield: auth copy on a sign-in page).
- M4c: the phrase inside BIG_ARTICLE (an article about
  identity verification) → OPEN (served-page gate).
- M4d: small page "Please verify your identity to continue."
  plus a "Continue" button but NO email input and NO auth
  form → CHALLENGED (a button alone is not a sign-in step;
  the L3 rule needs the email input).

## M5 — challenge phrase in an iframe title attribute

Title attributes are presented text (Wave 14, F2: alt/title
text IS page text), unlike data-* attributes (configuration).

- M5a: content-free page, iframe title="Verify you are human"
  → CHALLENGED (the attribute is the page's only text).
- M5b: BIG_ARTICLE with an iframe title="Verify you are human"
  → OPEN (served-page gate).

## M6 — overlay/dialog challenges on error statuses

A modal challenge blocks content whatever status carried it;
the generic branch already covers error statuses, so these are
expected to hold, not to break.

- M6a: 403 page, overlay-marked div + "Verify you are human"
  in the following text → CHALLENGED.
- M6b: 403 page, <dialog open> + "Verify you are human"
  → CHALLENGED.

## M7 — audit edges (robots / sitemap / llms)

- M7a: robots.txt with wildcard "Disallow: /" FIRST, then a
  named-agent group "User-agent: GPTBot / Allow: /"
  → robots check WARN for GPTBot (a named carve-out after the
  wildcard still leaves that agent reachable; group order does
  not cancel a carve-out — the Wave 11 principle, order-free).
- M7b: robots declares a sitemapindex; the index lists two
  child sitemaps (locs are crawlable URLs) → sitemap check
  PASS (an index with locs is a usable sitemap document by
  the Wave 19 usability test).
- M7c: llms.txt with a title and one markdown link with an
  EMPTY target "[Guide]()"
  → llms check WARN (title-only: an empty target names no
  index entry, the Wave 14 fragment-only principle applied to
  empty targets).
- M7d: llms.txt with BOM + CR-only line endings + frontmatter
  carrying a metadata URL + one real markdown link
  → llms check PASS (BOM strip, CR normalization, and
  frontmatter strip compose; the real link is content).
- M7e: robots.txt wildcard "Allow: /" plus "Disallow: /private"
  → robots check WARN for the tracked agents (partial access:
  the root is open, a path is closed — restricted, not
  blocked, the Wave 15 Allow-tiebreak family).

## M8 — precedence pins

- M8a: 401 + human-check phrase, small page → CHALLENGED
  (a fired wall precedes auth; the 401 branch sits below the
  generic branch).
- M8b: 429 + human-check phrase, small page → CHALLENGED
  (same precedence: challenge beats throttle).
- M8c: 503 + JS-proof phrase, small page → CHALLENGED.
- M8d: final_url is a login URL, body is a small page with a
  human-check phrase → LOGIN_GATED (the generic branch yields
  to an identified login page; vendor None — the Wave 11
  generic-only leak rule).
- M8e: meta refresh to a challenge target on a page at a login
  URL → CHALLENGED (the redirect-to-challenge species has no
  login exclusion in the Wave 10 rule: routing to a challenge
  is a challenge, and the login form is not what the page
  serves).

## M9 — inline-content and accessible-name pins

- M9a: BIG_ARTICLE with an open <details> element containing
  "Verify you are human" → OPEN (<details> is inline
  collapsible content, not a modal: it blocks nothing, and
  the served-page gate applies).
- M9b: content-free page, <button aria-label="Verify you are
  human"> → CHALLENGED (an interactive element's aria-label
  IS its accessible name — presented text, Wave 18 K8d).
- M9c: BIG_ARTICLE with such a button → OPEN (served-page
  gate).

## M10 — JSON captcha-error body

- M10a: 200 JSON body '{"error": "captcha required", "code":
  "challenge"}', small → CHALLENGED (the document's whole
  content is a captcha demand; a bare "captcha" token in a
  served document is a presented challenge, not a widget).
