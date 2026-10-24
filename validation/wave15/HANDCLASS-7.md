# Wave 15 — Adversarial Battery v7: Hand Classifications

Discipline (as Waves 6, 10, 11, 12, 13, 14): every shape below was classified
BY HAND against SPEC's verdict definitions BEFORE the classifier was
allowed to see it. All shapes are NEW relative to Wave 6 (S1–S6),
Wave 10 (B1–B10), Wave 11 (C1–C8), Wave 12 (D1–D9), Wave 13 (E1–E10),
and Wave 14 (F1–F8): no repeats of script-JSON markers (but see G1,
which tests JSON-LD vendor markers — a marker class the F1 fix
deliberately left load-bearing), traffic-anomaly phrasing, Retry-After
throttles, sitemap-index fallthrough, fragment llms links, comment
markers, mixed-case markers, title-only llms, or hop walls. Any
mismatch is a defect candidate: fix generalized with a capture-built
fixture, or ledger it as a genuine honest limitation with the reason.
No silent passes, no per-shape special cases.

Reference — SPEC verdicts: OPEN = the resource was served; CHALLENGED =
an interactive human-verification challenge was presented; WALLED = a
hard block page, no challenge offered; LOGIN_GATED = content exists
behind authentication; RATE_LIMITED = a throttle (HTTP 429, or a timed
refusal carrying a Retry-After header and throttle wording);
UNREACHABLE = the fetch itself failed. Audit grades: PASS / WARN / FAIL
per check.

## G1 — challenge markers ONLY inside JSON-LD blocks (classifier)

Wave 14 (W14-001) suppressed GENERIC markers inside <script> blocks when
the page has visible text — but deliberately left VENDOR markers
load-bearing in scripts, because challenge-platform loader scripts are
real signals. JSON-LD is a different species of script content: it is
structured-data metadata about the page, not code the page runs and not
a loader. A vendor name inside a JSON-LD description is metadata, not
a fired wall — unless the JSON-LD is the page's only content, in which
case (F1a species) the blob IS the page.

- **G1a** — 200, small page, a real visible paragraph ("Our team
  ships every Friday…") PLUS a JSON-LD block whose description reads
  "Verify you are human to access this article". → **OPEN**. Pin
  (W14-001 species): the generic marker lives only in a script block
  on a page with visible text — configuration/metadata, not content.
- **G1b** — 200, small page, ONLY a JSON-LD block whose text reads
  "Verify you are human to continue", no visible text at all. →
  **CHALLENGED / Generic**. Pin (F1a species): with no visible
  content, the blob is the page — a challenge declaration.
- **G1c** — 200, small page, a real visible paragraph PLUS a JSON-LD
  block whose description mentions "perimeterx" (a vendor name in
  metadata, e.g. an article about PerimeterX). → **OPEN**. The
  visible content is served; the metadata names a vendor the page
  is ABOUT, not a wall that fired. Predicted gap: vendor markers
  read scripts regardless of visible text, so the classifier will
  answer CHALLENGED / PerimeterX (PX_BODY_MARKER on 200 reads
  CHALLENGED, not WALLED).
- **G1d** — 200, small page, ONLY a JSON-LD block mentioning
  "perimeterx", no visible text. → **CHALLENGED / PerimeterX**. Pin
  (F1a species, vendor form): with no visible content, the blob is
  the page — the vendor marker is the only signal and it fires.

## G2 — "access denied" phrasing variants (classifier)

"Access denied" is a refusal statement, not a challenge and not an
answer like a 404. The classifier has a geo-refusal rule for regional
refusals (Wave 10, 4 KB-gated) but no general refusal-phrase rule —
so a 200-status refusal stub currently reads OPEN, which claims the
resource was served when it was refused.

- **G2a** — 200, small page, only content "Access denied." → **WALLED,
  vendor none**. A refusal page was served instead of the resource,
  with no challenge and no content — the 200-status species of the
  bare-403 refusal, parallel to B3b's geo-refusal. Predicted gap: no
  refusal-phrase rule exists, so the classifier reads OPEN.
- **G2b** — 403, small page, "Access denied." → **WALLED, vendor
  none**. Pin: the bare-403 rule already owns it.
- **G2c** — 401, body "Access denied." → **LOGIN_GATED**. Pin: 401
  is an auth demand wherever it appears (B2c species) — the status
  owns auth, and a refusal-phrase rule must not pre-empt it.
- **G2d** — 200, 20 KB article that mentions "access denied" once
  (an article about permission errors). → **OPEN**. Pin: any
  refusal rule must be small-page-gated like GEO_REFUSAL, or
  articles about denials become walls.
- **G2e** — 503, body "Access denied." → **UNREACHABLE, vendor
  none**. Pin: a 5xx claims no wall even when it wears refusal
  wording (B6c species) — and "access denied" is not throttle
  wording, so the Retry-After rule cannot apply either.

## G3 — challenge text ONLY inside SVG <text> / <tspan> elements (classifier)

C3c pinned contiguous SVG text (the raw-body scan reads it). The new
ground is text SPLIT across elements: rendered text is contiguous, but
the markup is not — a phrase broken across <tspan> elements never
appears as a substring in the raw body.

- **G3a** — 403, small page, only an SVG whose <text> reads
  "Verify you are human" (contiguous). → **CHALLENGED / Generic**.
  Pin (C3c species at 403).
- **G3b** — 403, small page, only an SVG whose text is split across
  tspans: "Verify you" + "are human" (rendered: "Verify you are
  human"). → **CHALLENGED / Generic**. The reader — human or
  agent — sees one human-check sentence; the markup split is not
  a semantic split. Predicted gap: the generic phrase scan runs on
  the raw body, where the tags break the phrase, so the classifier
  reads WALLED (bare 403).
- **G3c** — 200, 20 KB article with an SVG diagram whose <text>
  reads "verify you are human" (an article about verification UX).
  → **OPEN**. Pin: the served-page gate — SVG text on a real
  article is content about checks, not a check.

## G4 — hCaptcha enterprise widget variants (classifier)

C2a pinned the standard hCaptcha widget (class + loader). Enterprise
variants add two new questions: the loader URL shape
(js.hcaptcha.com/1/api.js?render=explicit) and the INVISIBLE widget
(data-size="invisible"), which by design presents nothing to the
reader — it gates form submission, not reading, like F1b's form
configuration.

- **G4a** — 403, small page, only an hCaptcha enterprise widget
  (div class="h-captcha" + js.hcaptcha.com/1/api.js loader +
  data-sitekey), no prose. → **CHALLENGED / Generic**. Pin (C2a
  species): the widget IS the challenge mechanism; the loader
  blanking must not blank the widget class (the class string
  "h-captcha" does not contain the loader token "hcaptcha").
- **G4b** — 200, final URL https://site.example/login, a sign-in
  form carrying an hCaptcha widget. → **LOGIN_GATED**. Pin
  (S5c/C6a species): a widget on a login form is auth, not wall.
- **G4c** — 200, small page, a real visible paragraph PLUS an
  invisible hCaptcha widget (div class="h-captcha"
  data-size="invisible", no prose, no checkbox). → **OPEN**. The
  visible content is served; an invisible widget presents no
  challenge to the reader — it runs in the background for the
  form's submission, exactly the F1b principle in widget form.
  Predicted gap: the raw scan sees "captcha" in the widget class
  (not a script block, not a loader URL) and answers CHALLENGED.
- **G4d** — 403, small page, ONLY an invisible hCaptcha widget, no
  visible text. → **CHALLENGED / Generic**. Pin (F1d species):
  with no visible content, the widget is the page — a challenge
  mechanism with nothing else.

## G5 — challenge pages served with a Refresh HEADER (classifier)

Wave 10 (B4) covered meta refresh, JS location, and (Wave 11) form
actions as redirect targets — but not the HTTP `Refresh` header,
which declares the same routing in headers instead of body. The
target semantics are identical: challenge/login targets name a
gate, content targets are routing.

- **G5a** — 200, small page, empty body, header
  `Refresh: 0; url=/challenge/verify`. → **CHALLENGED / Generic**.
  The page's entire routing points at a challenge — the B4a
  principle in header form. Predicted gap: redirect targets are
  collected from body tags only, so the classifier reads OPEN.
- **G5b** — 200, small page, empty body, header
  `Refresh: 0; url=/login`. → **LOGIN_GATED**. Pin species (B4b
  in header form): the routing points at authentication.
  Predicted gap: same missing header parsing.
- **G5c** — 200, small page, empty body, header
  `Refresh: 0; url=/home` (the site's content page). → **OPEN**.
  Pin (B4d species): a redirect to content is routing, not a wall.
- **G5d** — 200, 20 KB article, header `Refresh: 0;
  url=/challenge/verify`. → **OPEN**. Pin: redirect-target
  collection is served-page-gated like every body marker — a
  header on a served article does not un-serve it.

## G6 — login walls presenting a 2FA prompt as the first screen (classifier)

The first screen of a login flow is sometimes the code-entry screen
itself (returning device, passkey-adjacent flow, or a challenge
step shown before any password field). At a login URL the heuristic
already owns it; the new ground is a code-entry form at a URL with
no login marker — where the Wave 14 F5 limitation currently says
form-only login signals read OPEN, because form-text detection
would false-positive on every "sign in" link. A one-time-code
entry form is a far narrower signal than a sign-in link: a code
input (otp/2fa/auth-code) plus auth wording ("verification code",
"6-digit code") is an authentication barrier, not a link.

- **G6a** — 200, final URL https://site.example/login, a 2FA code
  entry form only ("Enter your 6-digit code", code input, no
  password field). → **LOGIN_GATED**. Pin: served login page.
- **G6b** — 200, final URL https://site.example/login, a 2FA form
  plus "verify you are human" prose in the auth copy. →
  **LOGIN_GATED**. Pin (S5c species): human-check prose on an
  identified login page is auth, not wall.
- **G6c** — 200, final URL https://site.example/verify-2fa (no
  login path segment), a 2FA code entry form only ("Enter your
  6-digit verification code", input name="otp"). → **LOGIN_GATED**.
  The page's only content is an authentication barrier: no
  resource is served, no challenge is presented — the gate is
  auth. Predicted gap: no form-based login signal exists, so the
  classifier reads OPEN.
- **G6d** — 403, final URL https://site.example/login, a fired
  "Just a moment" wall plus a 2FA form. → **CHALLENGED /
  Cloudflare**. Pin (S5a species): a fired wall AT the login URL
  is a wall, not a login — the wall fired before any form.

## G7 — pages carrying BOTH a real article and a wall marker in the footer (classifier)

A footer badge ("Protected by PerimeterX") is page furniture, not a
fired wall — the same presence-vs-wall distinction as a sensor
cookie or a widget on a served page. The served-page gate already
handles large pages; the new ground is SMALL served pages, where
the gate does not apply and a bare vendor name in the footer
currently fires.

- **G7a** — 200, 20 KB article, footer "This site is protected by
  PerimeterX". → **OPEN**. Pin: the served-page gate — a vendor
  mention on a full page is presence.
- **G7b** — 200, 2 KB real article paragraph, footer "This site is
  protected by PerimeterX", no challenge text, no refusal. →
  **OPEN**. The article is served; the footer badge names the
  site's protection vendor the way a copyright line names its
  owner — it is not a challenge offered and not a block.
  Predicted gap: the bare PX_BODY_MARKER fires on small pages
  regardless of content, so the classifier answers CHALLENGED /
  PerimeterX (PX_BODY_MARKER on 200 reads CHALLENGED).
- **G7c** — 200, small page, ONLY a footer badge "Protected by
  DataDome", no other content. → **OPEN**. Pin: a badge alone is
  neither served content nor a challenge — and the DataDome
  branch fires CHALLENGED only on 401/403, so a 200 badge page
  already reads OPEN (S1d species: an empty-ish page was served).

## G8 — robots.txt with Allow-all plus one Disallow path (audit tool)

Post-Wave-11 semantics: FAIL means EVERY tracked agent is blocked.
The parser currently ignores Allow lines entirely, which is correct
for most shapes — but an Allow: / in the same group as a
Disallow: / is a tie, and RFC 9309 resolves ties in favor of Allow
(the most specific rule wins; equally specific, Allow wins). An
agent whose group both disallows and allows the root is not
blocked.

- **G8a** — robots.txt: `User-agent: *` Allow: / + Disallow:
  /private. → **WARN** (all four agents restricted to /private,
  none blocked outright). Pin: Allow: / does not erase a
  narrower Disallow — restriction stands.
- **G8b** — robots.txt: `User-agent: *` Allow: / only, no
  Disallow. → **PASS**. Pin: an allow-only file permits
  everything.
- **G8c** — robots.txt: `User-agent: *` Disallow: /private +
  `User-agent: GPTBot` Allow: /. → **WARN** (GPTBot open by its
  own group; the other three restricted). Pin: the named group
  wins for its agent.
- **G8d** — robots.txt: `User-agent: *` Disallow: / + Allow: /.
  → **PASS** (no tracked agent blocked or restricted: the tie
  resolves to Allow per RFC 9309, so the root is open and no
  other path is disallowed). Predicted gap: the parser ignores
  Allow lines, so it reads the Disallow: / as a total block and
  answers FAIL.

## G9 — llms.txt files with YAML frontmatter before the content (audit tool)

YAML frontmatter (--- ... --- at the top of the file) is document
metadata, not index content — the same configuration-vs-content
distinction as Wave 14's script JSON. The llms check scans the
whole body for links/URLs/paths, so metadata containing a URL or
a link currently counts as index content.

- **G9a** — /llms.txt with YAML frontmatter (title, date) followed
  by a real markdown index (section links). → **PASS**. Pin: the
  content after the frontmatter is a real index.
- **G9b** — /llms.txt containing ONLY frontmatter (title + a
  `url:` field pointing at the site, no index content below it).
  → **WARN** (LLMS_STUB family). The file points nowhere an agent
  can follow: its only URL is metadata about the document, not an
  index entry. Predicted gap: the URL regex matches the
  frontmatter `url:` field, so the file reads PASS.
- **G9c** — /llms.txt with frontmatter followed by one relative
  link (`- [Docs](/docs)`). → **PASS**. Pin: a minimal linked
  index is a real index (E6b species) — the frontmatter fix must
  not punish short-but-linked files.
- **G9d** — /llms.txt with frontmatter whose description field
  contains a markdown link, and no index content below it. →
  **WARN** (LLMS_STUB family). Same principle as G9b: a link in
  metadata is not an index entry. Predicted gap: the link regex
  matches the frontmatter link, so the file reads PASS.

## G10 — sitemap.xml entries carrying only lastmod (audit tool)

The sitemap check grades the document kind (urlset/sitemapindex),
not its entries — so a sitemap that names no URLs at all currently
passes. A sitemap whose entries carry only <lastmod> (no <loc>)
names no destinations: it is a table of contents with no contents,
the sitemap species of the llms STUB.

- **G10a** — /sitemap.xml is a <urlset> whose entries carry only
  <lastmod> (no <loc> anywhere). → **WARN** (a sitemap naming no
  URLs is not a usable sitemap). Predicted gap: the check sees
  <urlset and answers PASS without counting entries.
- **G10b** — /sitemap.xml is a <urlset> whose entries carry <loc>
  + <lastmod>. → **PASS**. Pin: a normal sitemap with dates.
- **G10c** — /sitemap.xml is a <sitemapindex> whose entries carry
  only <lastmod> (no <loc>). → **WARN**. Same rule as G10a in
  index form.
- **G10d** — /sitemap.xml is a <urlset> with one <loc> entry and
  the rest lastmod-only. → **PASS**. Pin: at least one
  destination makes it a usable sitemap — the fix must count
  entries, not demand that every entry carry a <loc>.
