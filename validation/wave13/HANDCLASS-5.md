# Wave 13 — Adversarial Battery v5: Hand Classifications

Discipline (as Waves 6, 10, 11, 12): every shape below was classified BY HAND
against SPEC's verdict definitions BEFORE the classifier was allowed to
see it. All shapes are NEW relative to Wave 6 (S1–S6), Wave 10 (B1–B10),
Wave 11 (C1–C8), and Wave 12 (D1–D9): no repeats of soft-404 variants,
redirect-chain walls in meta-refresh/JS-location/form-action form (but
see E8, which tests CHAIN LENGTH to a login final and a fired wall AT
a login final — chain-context combinations, not the redirect species),
202 JS-proof stubs with vendor tokens, multi-vendor stacks, login
hybrids in widget form, geo-blocks, consent boundaries, Cloudflare
error variants, app interstitials, DataDome variants, audit soft-404
variants, localized phrases, countdown interstitials, browser-check
wording, consent hybrids, form-action/login-yield splits, robots
carve-out semantics, llms format variants, gzip sitemaps, or chain
lengths to wall/content finals. Any mismatch is a defect candidate:
fix generalized with a capture-built fixture, or ledger it as a
genuine honest limitation with the reason. No silent passes, no
per-shape special cases.

Reference — SPEC verdicts: OPEN = the resource was served; CHALLENGED =
an interactive human-verification challenge was presented; WALLED = a
hard block page, no challenge offered; LOGIN_GATED = content exists
behind authentication; RATE_LIMITED = plain 429 throttle; UNREACHABLE =
the fetch itself failed. Audit grades: PASS / WARN / FAIL per check.

## E1 — image-only captcha pages (classifier, no text at all)

C3a covered alt text and C3b covered a no-signal SVG. These are the
<img> mechanisms: filename signal, attribute signal, and no signal.

- **E1a** — 403, small page, only content
  `<img src="/captcha/image.png" alt="">`, no text anywhere. →
  **CHALLENGED / Generic**. The image filename names the challenge
  mechanism: the page's sole content is a captcha image, served at
  a refusal status. The word "captcha" in the resource path is a
  readable signal (like alt text, unlike pixels).
- **E1b** — 403, small page, only content
  `<img src="/img/a7f3.png" alt="">`, no text, no tokens. →
  **WALLED, vendor none**. Pin (C3b species, img mechanism): no
  readable signal exists — the refusal owns the verdict, and
  guessing "captcha" from an opaque image filename would be
  fabrication, not detection.
- **E1c** — 403, small page, only content
  `<img src="/img/a7f3.png" title="Please verify you are human">`,
  no other text. → **CHALLENGED / Generic**. Element attribute
  text is page text: the title names the human check, and the raw
  body scan reads attributes.

## E2 — noscript-only pages (classifier)

A page whose only content sits inside <noscript>: does the
noscript wrapper change anything? It must not — the classifier
scans the raw body, and noscript text is text.

- **E2a** — 200, body only a noscript block: "This site requires
  JavaScript. Please enable JavaScript to continue." → **CHALLENGED
  / Generic**. Pin: the phrase is in the JS_PROOF list, and the
  noscript wrapper does not hide it — the page's only content is
  a JS proof the agent cannot perform.
- **E2b** — 200, body only a noscript block: "This site requires
  JavaScript to run. Please enable JavaScript to run this app."
  → **OPEN**. Pin (Wave 6 S3c species, noscript form): a
  capability note is not a wall — "to run this app" is not a
  JS_PROOF phrase, and the noscript wrapper does not promote it
  into one.
- **E2c** — 200, body only a noscript block: "Please enable
  JavaScript and verify you are human to continue." →
  **CHALLENGED / Generic**. Pin: human-check prose inside noscript
  still counts — stripping noscript content before scanning
  would blind the classifier to real challenge pages.

## E3 — human-check wording ONLY in the <title> (classifier)

- **E3a** — 200, small page, `<title>Verify you are human</title>`,
  body only a spinner div, no other text. → **CHALLENGED /
  Generic**. The title is the page's only content and it names
  the check; a small page whose only text is a human-check title
  is a challenge page, not served content.
- **E3b** — 200, 20 KB article about verification UX, title
  "Verify you are human: how sites check visitors". → **OPEN**.
  Pin: the served-page gate — a title phrase on a real article
  is content about checks, not a check.

## E4 — challenge cookie + served content (classifier)

- **E4a** — 200, full article, response sets a `_pxvid` cookie
  (PerimeterX sensor presence), no wall signals in the body. →
  **OPEN**. Pin (Wave 1 PX-cookie demotion): a presence cookie
  on served content is not a wall — the cookie rides along, the
  content is served.
- **E4b** — 200, small stub "Please wait while we check your
  browser" + a `_pxvid` cookie. → **CHALLENGED / Generic**.
  Pin: the stub is a JS_PROOF challenge ("checking your browser"
  is in the phrase list); the cookie is presence only and does
  NOT upgrade the vendor to PerimeterX — vendor attribution
  needs a wall signal, not a sensor.

## E5 — robots.txt: all-agents vs one-agent blocks (audit tool)

Post-Wave-11 semantics (FAIL = every tracked agent blocked).
These shapes test the NO-WILDCARD variants the earlier batteries
never exercised (C8/D6 always paired named groups with a
wildcard).

- **E5a** — robots.txt: only group `User-agent: *` Disallow: `/`.
  → **FAIL** (all four tracked agents blocked by the wildcard).
  Pin.
- **E5b** — robots.txt: only group `User-agent: GPTBot`
  Disallow: `/`, no wildcard group at all. → **WARN** (GPTBot
  blocked; ClaudeBot, CCBot, Google-Extended open — the file
  does not block everything, and there is no wildcard to
  short-circuit on).
- **E5c** — robots.txt: four named groups, each Disallow: `/`,
  no wildcard group. → **FAIL** (every tracked agent blocked —
  FAIL must not require a wildcard rule to exist; the four named
  blocks add up to a total block).

## E6 — title-only llms.txt (audit tool)

- **E6a** — /llms.txt served as text/plain, body
  "# Welcome to Example Corporation" (one line, no links, no
  paths, no URLs). → **WARN**. A title line is not an index:
  it points nowhere and summarizes nothing an agent can use.
  The middle grade fits (served-but-useless, like EMPTY_BODY):
  PASS would claim a real index exists, FAIL would claim
  deception. Predicted gap: the length gate (20 chars) passes
  any long title line, since it checks length, not content.
- **E6b** — /llms.txt body "# My Site\n\n- [Docs](/docs)\n".
  → **PASS**. Pin: a minimal index with one real link is a real
  index — the E6a fix must not punish short-but-linked files.

## E7 — one-URL sitemaps (audit tool)

- **E7a** — /sitemap.xml is a `<urlset>` containing exactly one
  `<url>`. → **PASS**. Pin: a one-URL sitemap is still a sitemap
  — the check grades the document kind, not its size.
- **E7b** — /sitemap.xml is a `<sitemapindex>` containing
  exactly one child sitemap. → **PASS**. Pin (extends C7a):
  a one-child index is still an index.

## E8 — multi-hop redirect chains ending at a login page (classifier)

D9b covered a 2-hop chain to a login final. These are the
chain-context combinations: longer chains, a widget-carrying
login final, and a fired wall AT the login final.

- **E8a** — chain [site → /a → /b → /c → /login], final 200
  login page, no wall signals. → **LOGIN_GATED**. Pin (D9b
  extended to 4 hops): chain length changes nothing; the served
  login final owns the verdict.
- **E8b** — chain [site → /challenge → /login], final 200 login
  page carrying a Turnstile widget for its own sign-in form. →
  **LOGIN_GATED / Cloudflare**. Pin (C2c species in chain
  context): the loader-only login yield survives a challenge URL
  earlier in the chain — the chain must not outrank the served
  login final. CORRECTION (battery run, not a defect): the first
  draft of this line said vendor None; the C2c precedent already
  establishes that a loader-only login page keeps its loader
  vendor (LOGIN_GATED, Cloudflare) — the yield changes the
  verdict, not the attribution, and only the Generic leak is
  nulled on LOGIN_GATED. The hand classification was wrong, the
  classifier was right.
- **E8c** — chain [site → /a → /login], final page at the login
  URL is a fired "Just a moment" wall (cf-ray + cf-mitigated
  challenge). → **CHALLENGED / Cloudflare**. Pin (Wave 6 S5a
  species in chain form): a fired wall AT the login URL is a
  wall, not a login — the login yield covers served login
  pages, never fired walls.

## E9 — vendor markers ONLY inside HTML comments (classifier)

Comments are developer metadata, not rendered content and not
executed code. A marker that exists only in a comment is not a
fired wall and not attribution.

- **E9a** — 200, small page, visible text a short real article
  paragraph, plus an HTML comment containing "Cloudflare Ray
  ID" and "Just a moment". → **OPEN**. The visible page is
  served content; the comment markers are not content, not a
  challenge, and not a wall. Predicted gap: the classifier
  scans the raw body including comments, so it will read
  CF_JUST_A_MOMENT and answer CHALLENGED.
- **E9b** — 403, small page, visible text "Access denied" only,
  plus an HTML comment containing "perimeterx" and a px
  marker. → **WALLED, vendor none**. The refusal owns the
  verdict; comment-only vendor evidence is not trusted for
  attribution. Predicted gap: same comment-scanning issue —
  the classifier will read PX_BODY_MARKER and name PerimeterX.

## E10 — vendor markers in mixed case (classifier)

- **E10a** — 403, small page, "JUST A MOMENT" + cf-ray header.
  → **CHALLENGED / Cloudflare**. Pin: matching is on the
  lowered body, so case cannot matter.
- **E10b** — 403, small page, "PERIMETERX" + "Please verify you
  are NOT A ROBOT". → **WALLED / PerimeterX**. Pin: the
  PerimeterX deny-page rule (marker + 403 = WALLED) is
  case-insensitive like every other body marker.
- **E10c** — 403, small page, "DaTaDoMe" body marker +
  "Access denied". → **CHALLENGED / DataDome**. Pin: the
  DataDome body marker is matched on the lowered body.
