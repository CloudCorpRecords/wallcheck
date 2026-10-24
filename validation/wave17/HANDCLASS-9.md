# Wave 17 — Adversarial Battery v9: Hand Classifications

Discipline (as Waves 6, 10, 11, 12, 13, 14, 15, 16): every shape below was
classified BY HAND against SPEC's verdict definitions BEFORE the
classifier was allowed to see it. All shapes are NEW relative to Wave 6
(S1–S6), Wave 10 (B1–B10), Wave 11 (C1–C8), Wave 12 (D1–D9), Wave 13
(E1–E10), Wave 14 (F1–F8), Wave 15 (G1–G10), and Wave 16 (H1–H10). Two
near-miss deltas are stated explicitly so they are not mistaken for
repeats: Wave 13's E2 covered noscript text as a page's ONLY content
(J1 here covers noscript markers on pages that ALSO serve real
content); Wave 13's E3 covered human-check wording ONLY in the <title>
on a spinner page or a 20 KB article (J2 here covers title-only wording
on a SMALL real content page, where neither the spinner pin nor the
size gate decides). Any mismatch is a defect candidate: fix generalized
with a capture-built fixture, or ledger it as a genuine honest
limitation with the reason. No silent passes, no per-shape special
cases.

Reference — SPEC verdicts: OPEN = the resource was served; CHALLENGED =
an interactive human-verification challenge was presented; WALLED = a
hard block page, no challenge offered; LOGIN_GATED = content exists
behind authentication; RATE_LIMITED = a throttle; UNREACHABLE = the
fetch itself failed. Audit grades: PASS / WARN / FAIL per check.

## J1 — challenge markers ONLY inside <noscript> blocks, on pages that also serve content (classifier)

Wave 13 (E2) settled noscript-as-only-content: noscript text IS text,
and a challenge page whose only content is a noscript block is a
challenge page. The untested pole is the reverse: a page that serves
real body content AND carries a challenge note only inside a noscript
fallback block. A noscript block is a fallback for clients without JS —
it does not gate, replace, or block the body content the server also
served. The W16-002/003 principle (configuration/metadata that is not
presented content does not drive a verdict when the page has visible
text) extends to noscript fallbacks: the note is ancillary to served
content, not a presented challenge. The guard that keeps E2 honest:
when the page has NO visible body content, the noscript block IS the
page, and the fallback rule must not apply.

- **J1a** — 200, real article paragraph (~600 chars of body text)
  PLUS `<noscript>Please enable JavaScript and verify you are human
  to continue.</noscript>`. → **OPEN**. The article was served; the
  noscript note is a fallback annotation, not a gate on the article.
  Predicted gap: the raw scan reads noscript text and the survival
  test passes it (noscript is stripped nowhere), so the classifier
  answers CHALLENGED.
- **J1b** — 200, body ONLY a noscript block: "Please enable
  JavaScript and verify you are human to continue." → **CHALLENGED
  / Generic**. Pin (E2c species): with no visible body content, the
  noscript block is the page's only text — a presented challenge.
- **J1c** — 200, small real paragraph (two sentences, ~150 chars)
  PLUS a noscript JS-proof note ("This site requires JavaScript.
  Please enable JavaScript to continue."). → **OPEN**. Same
  principle as J1a in the JS_PROOF branch: a fallback note on
  served content is not a presented proof demand.
  Predicted gap: same miss, classifier answers CHALLENGED.
- **J1d** — 200, body only a spinner div ("Loading...") PLUS a
  noscript human-check note. → **CHALLENGED / Generic**. A spinner
  is not content (under the 20-char visible-text floor), so the
  noscript block is the page's only real text — the E2c species
  again, with a spinner instead of an empty body.
- **J1e** — 200, real article paragraph PLUS a noscript block
  containing only a vendor name ("perimeterx"). → **OPEN**. The
  vendor scan must treat noscript text the same way it treats
  data-* attributes and style blocks: metadata, not a fired wall,
  when the page has visible text. Predicted gap: the vendor scan
  reads noscript text, so the classifier answers
  CHALLENGED / PerimeterX.
- **J1f** — 403, small page, noscript-only "verify you are human",
  no other text. → **CHALLENGED / Generic**. Pin (E2c species on
  an error status): content-free pages fire on their only text.

## J2 — wall text ONLY in the <title> element, on a small real content page (classifier)

Wave 13 (E3) settled the two poles: title-only + spinner →
CHALLENGED (the title is the page's only content); 20 KB article +
title phrase → OPEN (the served-page size gate). The untested middle
is a SMALL real content page (a paragraph or two, under the 16 KB
gate) whose only wall signal is a title phrase. A <title> is document
metadata — tab text, not page content — and the W16-002/003 principle
says metadata-only markers do not drive a verdict when the page has
visible text. The title is not nothing (E3a stands: with no visible
content, the title is the page), but on a page with visible content
it is not a presented challenge either.

- **J2a** — 200, small real content page (~900 bytes, a real
  paragraph) + `<title>Verify you are human</title>`, no other
  markers. → **OPEN**. The paragraph was served; the title phrase
  is metadata about the page, not a challenge presented in it.
  Predicted gap: the generic survival test passes title text
  (head is stripped nowhere in the survival variants), so the
  classifier answers CHALLENGED.
- **J2b** — 200, title-only human-check title + spinner div, no
  other text. → **CHALLENGED / Generic**. Pin (E3a species):
  with no visible content, the title is the page.
- **J2c** — 200, real content page + `<title>PerimeterX
  protection</title>` (a vendor name only in the title). →
  **OPEN**. Same principle in vendor form: a vendor name in
  document metadata is not a fired wall. Predicted gap: the vendor
  scan reads head text, so the classifier answers
  CHALLENGED / PerimeterX.
- **J2d** — 200, real content page + `<title>Checking your
  browser</title>` (a JS_PROOF phrase only in the title). →
  **OPEN**. Same principle in the JS_PROOF branch. Predicted gap:
  classifier answers CHALLENGED via JS_PROOF.
- **J2e** — 403, body "Access denied. Your request was blocked by
  our security policy." (a real refusal paragraph, 66 chars) +
  `<title>Unusual traffic from your network — please
  verify</title>`. → **WALLED, vendor none**. The served body is
  a refusal; the title's anomaly-plus-cue wording is metadata
  about a check, not a challenge presented in the body — it must
  not upgrade a refusal into a challenge. Predicted gap: the
  TRAFFIC_CHECK branch reads the raw body including the title,
  so the classifier answers CHALLENGED.

## J3 — challenge pages served with no-store/no-cache headers as their only header signal (classifier)

Cache directives are not wall signals: `Cache-Control: no-store,
no-cache` is routine on dynamic, authenticated, and interstitial
pages alike, and no vendor's challenge is identified by it. A header
that appears on both walls and ordinary pages cannot name a wall,
and it cannot suppress a wall either. All four shapes are expected
pins — the classifier never reads cache-control — included because
"headers as the only signal" is a plausible future misread, and pins
are cheaper than regressions.

- **J3a** — 200, small stub "Please wait, loading your content..."
  + `Cache-Control: no-store, no-cache`. → **OPEN**. No challenge
  evidence exists; a loading note plus cache directives is not a
  wall.
- **J3b** — 403, empty body + `Cache-Control: no-store`. →
  **WALLED, vendor none**. The status owns the verdict; the header
  adds nothing and names nobody.
- **J3c** — 200, small challenge page "Verify you are human" +
  no-store headers. → **CHALLENGED / Generic** via the body. The
  headers neither create nor suppress the verdict.
- **J3d** — 200, small stub "Please wait while we check your
  browser" + no-store headers. → **CHALLENGED / Generic** via the
  JS_PROOF body phrase. Same point in the JS_PROOF branch.

## J4 — login walls presenting a QR-code prompt (classifier)

Wave 15 (G6) covered code-entry forms and Wave 16 (H5) passkey
prompts; QR-code sign-in is the next auth species. A QR prompt is an
authentication barrier exactly like a code form: the page's only
content is a ceremony the agent cannot complete. The signal must be
two-keyed like its siblings — QR wording PLUS an auth purpose PLUS
a prompt marker (an image, canvas, or button carrying the code) —
so prose ABOUT QR login, app-download QR codes, and bare links
cannot fire it.

- **J4a** — 200, page whose only content is "Scan the QR code with
  your phone to sign in" + `<img src="/qr.png">`, at a non-login
  URL. → **LOGIN_GATED**. The page's only content is an
  authentication barrier. Predicted gap: no QR signal exists, so
  the classifier reads OPEN.
- **J4b** — 200, article ABOUT QR login ("How QR code sign-in
  works", prose only, no image/button). → **OPEN**. Guard: prose
  about QR sign-in is content, not a prompt.
- **J4c** — 200, content page "Scan the QR code to download our
  app" + QR image. → **OPEN**. Guard: an app-download QR code
  has no auth purpose — the auth wording key is absent.
- **J4d** — 200, QR prompt (wording + image) at a login URL. →
  **LOGIN_GATED**. Pin: the login heuristic.
- **J4e** — 200, page whose only content is "Scan the QR code to
  sign in" plus a bare `<a>` link "Get the app" (no image, canvas,
  or button). → **OPEN**. Guard (F5 species): a link is not a
  prompt marker — the code itself is not presented.
- **J4f** — 200, page whose only content is "Scan to sign in" +
  a `<canvas>` QR element. → **LOGIN_GATED**. A canvas-rendered
  code is a presented code, like an image.

## J5 — robots.txt files carrying Sitemap: lines inside comments (audit tool)

robots.txt comments start with `#` and are not directives — the
parser already strips them (Wave 16 H6c pins comment-only files).
The untested question is the SITEMAP side: a commented Sitemap
line must not be reported as a declaration, must not route the
sitemap check to a URL the site never declared, and must not
suppress a real declaration elsewhere in the file. All four shapes
are expected pins — the comment strip already handles them —
included because a commented declaration is exactly the kind of
phantom evidence an audit must not invent.

- **J5a** — robots.txt containing ONLY `# Sitemap:
  https://x.example/sitemap.xml` (commented), no real Sitemap
  line; /sitemap.xml answers 404. → robots **PASS** (no agent
  directives exist); sitemap **WARN** (no declaration claimed,
  no sitemap served — the commented line is not evidence).
- **J5b** — robots.txt with a commented Sitemap line PLUS a real
  `Sitemap: https://x.example/s2.xml`; /sitemap.xml 404s but the
  declared s2 serves a urlset. → sitemap **PASS** with
  VIA_ROBOTS_DECLARATION for s2 only. The commented line must
  not appear in the declared set.
- **J5c** — robots.txt `Disallow: /private # Sitemap:
  https://x.example/trap.xml` (an inline comment after a real
  directive). → the Disallow stands; NO sitemap declaration is
  recorded from the comment. Robots grade follows the Disallow
  alone.
- **J5d** — robots.txt with a commented-out `# Disallow: /` plus
  an open `User-agent: *` group. → robots **PASS**. Pin (H6c
  species): a commented directive is not a directive.

## J6 — llms.txt files with HTML entities in the body (audit tool)

An llms.txt is plain text, not HTML — but bodies in the wild carry
HTML entities (`&amp;`, `&lt;`, `&#47;`), and the check's content
tests (markdown links, URLs, paths, JSON detection) all read raw
text. Entities that merely spell ordinary characters must not hide
real content, and entities that merely spell markup must not
create content that is not there. The one genuinely new question
is the JSON gate: an error document entity-encoded is still an
error document, and the check that reads it as text will misgrade
it.

- **J6a** — real markdown index whose link targets contain
  `&amp;` (`[Docs](/docs?a=1&amp;b=2)`). → **PASS**. Pin: the
  entity does not break the link — the target is non-empty and
  not a fragment.
- **J6b** — body is ONLY escaped markup
  `&lt;a href="https://example.com/docs"&gt;Click
  here&lt;/a&gt;`. → **PASS**. The URL is present as plain text
  an agent can follow; entity encoding does not hide the
  destination. (The file is ugly, not useless — the URL rule
  decides, as it does for unescaped text.)
- **J6c** — body is an entity-encoded JSON error document:
  `{&quot;error&quot;: &quot;not found&quot;}`. → **FAIL**
  (JSON_ERROR_DOC species, entity-encoded). The file's content
  is an error document, not an index — encoding does not change
  what it is. Predicted gap: the JSON gate parses raw text, the
  parse fails, and the body falls through to the stub gate
  (WARN) — the error is misgraded as a stub.
- **J6d** — body is an entity-encoded JSON data document with no
  error key: `{&quot;title&quot;: &quot;Docs&quot;}`. →
  **WARN** (JSON_NOT_LLMS species). Same unescape question in
  the non-error form: the grade stays WARN either way, but the
  evidence must name the format, not a stub.
- **J6e** — body whose only path is entity-encoded:
  `Visit &#47;docs for the index`. → **WARN** (LLMS_STUB). As
  plain text the file contains no literal path, link, or URL —
  an agent reading the file as text finds nothing to follow.
  Entities are not decoded into paths: the stub grade is the
  honest reading for a text file.

## J7 — multi-language challenge text within a single page, in languages new to the list (classifier)

Wave 6 (ES/DE/FR/JA/PT), Wave 11 (IT/NL/KO), and Wave 12
(PL/TR/AR/ZH/RU) built the localized list one language family at
a time; the principle generalizes, and the Nordic languages are
the next family. Each new language earns its phrases the same way:
an interactive human-verification demand in that language, matched
like the English markers, gated like every generic marker. The
mixed-language shapes test that the list composes (two complete
phrases in two new languages) and that it does not overreach
(fragments code-switched across languages compose nothing).

- **J7a** — 403, small page, Swedish only: "Bekräfta att du inte
  är en robot." → **CHALLENGED / Generic**. Predicted gap:
  Swedish is not in the localized list, so the classifier reads
  WALLED.
- **J7b** — 403, small page, Finnish only: "Vahvista, ettet ole
  robotti." → **CHALLENGED / Generic**. Predicted gap: same.
- **J7c** — 403, small page, Danish only: "Bekræft, at du ikke
  er en robot." → **CHALLENGED / Generic**. Predicted gap: same.
- **J7d** — 403, small page, Norwegian only: "Bekreft at du ikke
  er en robot." → **CHALLENGED / Generic**. Predicted gap: same.
- **J7e** — 403, small page, Swedish + Finnish phrases mixed
  (both complete). → **CHALLENGED / Generic**. Pin after the
  list addition: two complete phrases compose; either alone
  would suffice.
- **J7f** — 200, 20 KB article about robots quoting a Swedish
  phrase. → **OPEN**. Pin: the served-page gate — a quoted
  phrase on a real article is content about checks, not a check.
- **J7g** — 403, small page, code-switched fragments: "Verify /
  eres humano" (half an English phrase, half a Spanish phrase,
  neither complete). → **WALLED, vendor none**. Honest boundary,
  not a defect: fragments across languages compose no listed
  phrase, and matching half-phrases across languages would be
  guessing. A refusal with no complete challenge evidence is
  WALLED.

## J8 — pages where the challenge is a full-screen overlay div over otherwise real content (classifier)

The served-page size gate (16 KB) exists because wall mentions on
a full served page are presence, not a fired wall. An overlay is
the exception that proves the gate: a full-screen modal carrying
a human check BLOCKS the real content beneath it — the reader
cannot read the article without passing the check. The signal
must be two-keyed: an overlay-marked container (class/id naming
an overlay, modal, popup, lightbox, or dialog) PLUS a human-check
or JS-proof phrase inside it. Overlay furniture without a
challenge phrase (cookie banners, newsletter modals) is not a
wall, and a challenge phrase in ordinary prose is still gated.

- **J8a** — 200, 20 KB article + a full-screen overlay div
  (`class="overlay-modal"`, fixed positioning) containing
  "Verify you are human" + a checkbox. → **CHALLENGED /
  Generic**. The overlay blocks the article; the check is
  presented, not mentioned. Predicted gap: the size gate
  suppresses every body marker on the 20 KB page, so the
  classifier reads OPEN.
- **J8b** — 200, 20 KB article + an overlay div containing only
  cookie text ("We use cookies to improve your experience").
  → **OPEN**. Guard: an overlay without a challenge phrase is
  furniture.
- **J8c** — 200, 20 KB article + inline prose mention "This site
  uses verification to prevent bots" (no overlay). → **OPEN**.
  Guard: the size gate still protects prose mentions — the
  overlay key is load-bearing, not decorative.
- **J8d** — 200, small page + overlay div containing a
  human-check phrase. → **CHALLENGED / Generic**. Pin: the
  small-page path already fires; the overlay rule must agree.
- **J8e** — 200, 20 KB article + overlay div containing a
  JS_PROOF phrase ("Checking your browser"). → **CHALLENGED /
  Generic**. Same signal in the JS_PROOF branch.
- **J8f** — 200, 20 KB article + a `class="modal-content"` div
  (modal marker, no inline fixed positioning — positioned by
  stylesheet) containing a human-check phrase. → **CHALLENGED /
  Generic**. The class marker is the signal; inline positioning
  is not required, since real overlays position via stylesheet.
- **J8g** — 200, 20 KB article + a `class="modal"` div containing
  only "Subscribe to our newsletter". → **OPEN**. Guard: a
  modal without a challenge phrase is furniture, like J8b.

## J9 — residual edge re-test: captcha tokens split across script boundaries (classifier)

Wave 16 ledgered this as an edge, not a fix: the nospace variant
derives from the script-stripped body, so a "captcha" token split
with one half inside a script block and one half in body text is
unscanned, and fixing it would require scanning script content —
which Wave 14 (W14-001) forbids for good reason. Re-tested this
wave with a faithful shape:

- **J9a** — 200, small page, visible text "Please complete the
  cap" + a script block containing the string "tcha" (so naive
  source concatenation would read "captcha"). → **OPEN**. The
  re-test CONFIRMS the ledger entry and sharpens it: the rendered
  page never presents a "captcha" token to any reader — the
  second half lives only in script configuration — so OPEN is
  not a miss but the correct reading for a static, non-JS fetch.
  A token assembled only by script execution is invisible to
  this tool by design (no JS execution, SPEC constraint), and
  claiming otherwise would be guessing. The edge stays ledgered
  as a limitation-by-design, re-tested 2026-10-24, not a defect.
