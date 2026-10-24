# Wave 16 — Adversarial Battery v8: Hand Classifications

Discipline (as Waves 6, 10, 11, 12, 13, 14, 15): every shape below was
classified BY HAND against SPEC's verdict definitions BEFORE the
classifier was allowed to see it. All shapes are NEW relative to Wave 6
(S1–S6), Wave 10 (B1–B10), Wave 11 (C1–C8), Wave 12 (D1–D9), Wave 13
(E1–E10), Wave 14 (F1–F8), and Wave 15 (G1–G10): no repeats of script-JSON
markers (but see H9, which tests whether the G1 ld+json fix generalized
to other JSON script types), refusal stubs, SVG tspan splits, invisible
widgets, Refresh headers, 2FA forms, footer badges, robots Allow
tiebreaks, frontmatter, or lastmod-only sitemaps. Any mismatch is a
defect candidate: fix generalized with a capture-built fixture, or
ledger it as a genuine honest limitation with the reason. No silent
passes, no per-shape special cases.

Reference — SPEC verdicts: OPEN = the resource was served; CHALLENGED =
an interactive human-verification challenge was presented; WALLED = a
hard block page, no challenge offered; LOGIN_GATED = content exists
behind authentication; RATE_LIMITED = a throttle; UNREACHABLE = the
fetch itself failed. Audit grades: PASS / WARN / FAIL per check.

## H1 — TRAFFIC_CHECK anomaly phrase SPLIT across body parts (classifier)

Wave 15's follow-up, stated in LIMITATIONS-REVISIT.md: W15-003 gave
the visible-text scan to human-check and JS_PROOF phrases, but
TRAFFIC_CHECK still scans the raw body only. A rendered sentence
split across elements is one sentence to the reader and two
fragments to a substring scan — the G3 principle applied to the
one branch that never got it.

- **H1a** — 403, small page, the anomaly sentence split across
  paragraphs: "We noticed unusual" in one `<p>`, "traffic from
  your device." in the next, plus "Please verify to continue."
  (a verification cue, but NOT the human-check phrase "verify
  you are human"). → **CHALLENGED / Generic**. The server names
  the anomaly AND asks the agent to prove itself — the F3b
  species, rendered whole. Predicted gap: TRAFFIC_CHECK needs
  "unusual traffic" as a raw substring, which the markup split
  breaks, so the classifier reads WALLED (bare 403).
- **H1b** — 403, small page, the traffic phrase contiguous
  ("unusual traffic from your network") but the verification
  cue split across elements: "ver" in one `<span>`, "ify" in
  the next ("Please ver-ify your connection" rendered as
  "Please verify your connection"). → **CHALLENGED / Generic**.
  The cue is present in the rendered sentence. Predicted gap:
  the cue scan is raw-body only too, so "verif" never appears
  as a substring and the classifier reads WALLED.
- **H1c** — 200, 20 KB article mentioning split "unusual /
  traffic" wording plus a verification cue (an article about
  traffic-anomaly detection). → **OPEN**. Pin: the served-page
  gate — anomaly wording on a real article is content about
  checks, not a check.
- **H1d** — 403, small page, contiguous "unusual traffic" +
  "Please verify to continue." → **CHALLENGED / Generic**. Pin
  (F3b species): the unsplit case already works.
- **H1e** — 403, small page, split "unusual / traffic" wording
  with NO verification cue anywhere. → **WALLED, vendor none**.
  Pin (F3a species): anomaly wording alone is a refusal
  statement, not a presented challenge — splitting does not
  change that.
- **H1f** — 403, small page, a human-check sentence split
  WITHIN a word across spans: "Ver<span>ify</span> you are
  human". → **CHALLENGED / Generic**. Inline elements add no
  space to rendered text, so the reader sees "Verify you are
  human" whole. Predicted gap (found on the W16-001 re-run):
  the space-separated visible-text scan reads "Ver ify you are
  human", so neither scan finds the phrase and the classifier
  reads WALLED. (Shape added during the fix: the within-word
  split is the same family as H1b's split cue, one level
  deeper.)
- **H1g** — 403, small page, a JS-proof sentence split within
  a word: "Brow<span>ser</span> check in progress". →
  **CHALLENGED / Generic**. Same rendered-text principle, JS_PROOF
  branch. Predicted gap: same miss, classifier reads WALLED.
- **H1h** — 403, small page, the captcha token split within a
  word: "Please complete the cap<span>tcha</span> to
  continue." → **CHALLENGED / Generic**. Same principle,
  captcha branch. Predicted gap: the token scan reads markup,
  not rendered text, so the classifier reads WALLED.

## H2 — challenge markers ONLY in data-* attributes (classifier)

F2 established that alt/title attribute text IS page text (alt is
rendered fallback text; title is hover text). data-* attributes
are the opposite species: pure configuration, never rendered to
any reader — the same configuration-vs-content distinction as
script JSON (W14-001) and JSON-LD (W15-001), in attribute form.
A data-* value naming a check is metadata about the page, not a
presented challenge — unless it is the page's only text, in
which case (F1a/F2a species) the blob is the page.

- **H2a** — 200, small real article paragraph PLUS
  `<div data-message="verify you are human">`. → **OPEN**. The
  article is served; the data-* value is configuration the
  reader never sees. Predicted gap: the raw scan reads
  attribute values, so the classifier answers CHALLENGED.
- **H2b** — 403, small page, ONLY
  `<div data-challenge="verify you are human">`, no visible
  text. → **CHALLENGED / Generic**. Pin (F2a species): with no
  visible content, the attribute is the page's only text — a
  challenge declaration.
- **H2c** — 200, small real article paragraph PLUS
  `<div data-vendor="perimeterx">`. → **OPEN**. The visible
  content is served; a vendor name in a data attribute is
  metadata about the page's protection, not a fired wall —
  the G1c species in attribute form. Predicted gap: the vendor
  scan reads raw attribute values, so the classifier answers
  CHALLENGED / PerimeterX.
- **H2d** — 403, small page, ONLY
  `<div data-vendor="perimeterx">`, no visible text. →
  **CHALLENGED / PerimeterX**. Pin (G1d species): with no
  visible content, the blob is the page.

- **H2e** — 200, small real article paragraph PLUS
  `<div data-captcha="true"></div>` (the "captcha" token lives
  only in a data-attribute NAME, no widget, no prose). → **OPEN**.
  The attribute is configuration, not a presented challenge.
  Predicted gap: the captcha branch reads attribute names, so
  the classifier answers CHALLENGED. (Shape added during the
  fix design: the H2 principle covers the captcha branch as
  well as the human-check and vendor branches, so it earns its
  own pin.)

## H3 — wall text rendered via CSS content (classifier)

CSS `content:` declarations ARE rendered text — a ::before
pseudo-element's string shows on the page — so a challenge
sentence that exists only as CSS content is genuinely presented
to the reader, unlike script JSON or data attributes. The new
ground is the reverse: a stylesheet declaration on a page whose
real content is served. A stylesheet is configuration; a
decorative pseudo-element string is not an interactive
challenge, and no interaction is demanded of the reader.

- **H3a** — 403, small page, only a `<div class="gate">` plus
  `<style>.gate::before{content:"Verify you are human"}</style>`.
  → **CHALLENGED / Generic**. Pin: the CSS content is the
  page's only presented text, and it is a human-check sentence
  — the raw scan reading it is correct here.
- **H3b** — 200, small real article paragraph PLUS a decorative
  `<style>.note::before{content:"Verify you are human"}</style>`
  on a non-interactive note element; the article is fully
  readable, no form, no checkbox, no interaction demanded. →
  **OPEN**. The resource was served; a stylesheet declaration
  is not a presented interactive challenge. Predicted gap: the
  raw scan reads style-block text, so the classifier answers
  CHALLENGED.
- **H3c** — 200, 20 KB article PLUS the same decorative CSS
  content rule. → **OPEN**. Pin: the served-page gate.
- **H3d** — 200, small real article paragraph PLUS
  `<style>.captcha-box{border:1px solid red}</style>` (the
  "captcha" token lives only in a stylesheet class selector).
  → **OPEN**. A stylesheet is configuration, not a presented
  challenge. Predicted gap: the captcha branch reads style
  text, so the classifier answers CHALLENGED. (Added during
  fix design: the H3 principle covers the captcha branch too.)
- **H3e** — 200, small real article paragraph PLUS
  `<style>.px-note{content:"perimeterx"}</style>` (a vendor
  name lives only in a stylesheet). → **OPEN**. Same
  principle in vendor form. Predicted gap: the vendor scan
  reads style text, so the classifier answers CHALLENGED /
  PerimeterX.
- **H3f** — 200, small page, ONLY the
  `<style>.px-note{content:"perimeterx"}</style>` rule, no
  visible text. → **CHALLENGED / PerimeterX**. Pin (G1d
  species): with no visible content, the stylesheet is the
  page's only text — the fix must be conditioned on visible
  text, like every other suppression in this family.

## H4 — 307/308 redirects to challenge/login targets (classifier)

Wave 10 (B4) covered body-declared redirects, Wave 15 (G5) the
Refresh header — but not the HTTP `Location` header on a 3xx
response itself. Live probes follow redirects, so this shape
only bites offline classify users (pipelines that fetch their
own way, the MCP `classify` tool) — but for them a bare
redirect response to a challenge currently reads OPEN, which
claims routing when the routing points at a gate. The B4
principle generalizes: a response whose whole content routes
the client to a challenge IS a challenge by reference, whatever
mechanism declares the route.

- **H4a** — 307, `Location: /challenge/verify`, empty body. →
  **CHALLENGED / Generic**. Predicted gap: Location is never
  collected as a redirect target, so the classifier reads OPEN
  (3xx falls into the 200–400 OPEN branch).
- **H4b** — 308, `Location: /login`, empty body. →
  **LOGIN_GATED**. Predicted gap: same missing collection.
- **H4c** — 307, `Location: /home`, empty body. → **OPEN**.
  Pin: a redirect to content is routing, not a wall.
- **H4d** — 302, `Location: /challenge/verify`, empty body. →
  **CHALLENGED / Generic**. Predicted gap: tests that the fix
  generalizes across 3xx codes, not just 307/308.
- **H4e** — 307, `Location: /challenge/verify`, final URL is a
  login URL (`https://site.example/login`). → **CHALLENGED /
  Generic**. The routing declares a challenge before any login
  form is reached — the S5a precedence (a fired wall at a login
  URL is a wall, not a login) in redirect form. Predicted gap:
  with no redirect evidence, the login heuristic fires and the
  classifier reads LOGIN_GATED.

## H5 — login walls with passkey/WebAuthn prompts (classifier)

Wave 15 (G6) covered 2FA code-entry forms; passkeys are the
next auth species. A passkey prompt is an authentication barrier
exactly like a code-entry form: the page's only content is a
ceremony the agent cannot complete. The signal must be two-keyed
like CODE_ENTRY_FORM — passkey/WebAuthn wording PLUS a prompt
marker (button, form, input, or a credentials-API reference) —
so prose ABOUT passkeys and bare links cannot fire it.

- **H5a** — 200, page whose only content is "Sign in with your
  passkey" plus a button and a WebAuthn ceremony script
  (`navigator.credentials.get`), at a non-login URL
  (`https://site.example/passkey`). → **LOGIN_GATED**. The
  page's only content is an authentication barrier. Predicted
  gap: no passkey signal exists, so the classifier reads OPEN.
- **H5b** — 200, small real article PLUS a header nav link
  "Sign in with a passkey" (a bare `<a>` link, no button/form).
  → **OPEN**. Pin (F5 species): a link is not a barrier — the
  article is the content.
- **H5c** — 200, passkey prompt (button + wording) at a login
  URL. → **LOGIN_GATED**. Pin: the login heuristic.
- **H5d** — 200, page whose only content is a passkey button
  plus "Verify your identity to continue" wording, at a
  non-login URL. → **LOGIN_GATED**. Predicted gap: same missing
  signal as H5a, with identity wording instead of a ceremony
  script.
- **H5e** — 200, article ABOUT passkeys ("How passkeys work: a
  WebAuthn explainer", prose only, no button/form/input). →
  **OPEN**. Guard: prose about passkeys is content, not a
  prompt — the fix must require a prompt marker, not a mere
  mention.

## H6 — robots.txt with no User-agent groups at all (audit tool)

Absence of directives is not a block: a robots file that says
nothing about agents restricts nothing. The parser must not
read "no groups" as "blocked" — and the sitemap-only, empty,
and comment-only species all test the same absence in different
clothing. All pins: the current parser already returns "open"
for every agent when no disallows exist.

- **H6a** — robots.txt containing ONLY
  `Sitemap: https://x.example/sitemap.xml`. → **PASS** (robots
  check). No agent directives exist; the sitemap declaration is
  graded by the sitemap check, not this one.
- **H6b** — robots.txt completely empty. → **PASS**. An empty
  file permits everything.
- **H6c** — robots.txt containing only comments
  (`# nothing here`). → **PASS**. Comments are not directives.
- **H6d** — robots.txt with a User-agent group carrying ONLY
  `Crawl-delay: 10` (no Disallow, no Allow). → **PASS**. A
  crawl delay is a rate hint, not a restriction.
- **H6e** — robots.txt with `User-agent: *` plus an EMPTY
  `Disallow:` value. → **PASS**. Per RFC 9309 an empty
  Disallow permits everything; the parser already filters empty
  values from the disallow list.

## H7 — llms.txt served with charset/BOM variations (audit tool)

Content-type parameters are not content: a charset suffix does
not change what the body is, and a UTF-8 byte-order mark is not
content either. The charset species should all pin — but the BOM
species interacts with the W15-009 frontmatter strip, whose
anchor assumes the file starts with `---`.

- **H7a** — real markdown index, Content-Type
  `text/plain; charset=utf-8`. → **PASS**. Pin: the charset
  parameter does not affect content analysis.
- **H7b** — real markdown index, Content-Type
  `text/markdown; charset=utf-8`. → **PASS**. Pin.
- **H7c** — real markdown index, Content-Type
  `application/octet-stream`. → **PASS**. Pin (D7d principle):
  content, not the header, decides — the check gates on HTML
  bodies, not on content-type exactness.
- **H7d** — llms.txt with a UTF-8 BOM prefix followed by
  frontmatter ONLY (title + a `url:` field, no index content).
  → **WARN** (LLMS_STUB family). The file points nowhere an
  agent can follow: its only URL is metadata. Predicted gap:
  the frontmatter strip anchors on `---` at the start, the BOM
  survives `lstrip()`, so the strip misses and the metadata
  URL counts as content — the file reads PASS.
- **H7e** — llms.txt with a UTF-8 BOM prefix followed by a
  real markdown index. → **PASS**. Pin: the BOM does not break
  real content detection (links still found).

## H8 — sitemap.xml files that reference each other circularly (audit tool)

The sitemap check grades the ONE fetched document; it never
follows sitemapindex references (the audit's ≤10-fetch budget
and domain-scoped contract forbid graph-walking). Circularity
therefore cannot loop the check — but the shapes verify that
claim rather than assuming it, and pin the "names destinations"
rule for index documents whose destinations are other sitemaps.

- **H8a** — sitemapindex whose `<loc>` entries point at two
  sitemap files that reference each other (A lists B, B lists
  A). → **PASS**. The fetched document names destinations;
  the check does not follow them, so no loop is possible.
- **H8b** — sitemapindex with a single `<loc>` pointing back
  at itself. → **PASS**. Same rule: one destination suffices,
  self-reference included.
- **H8c** — sitemapindex with zero `<loc>` entries. → **WARN**
  (SITEMAP_NO_URLS). Pin (W15-010 species).
- **H8d** — urlset whose `<loc>` entries are all sitemap files
  rather than content URLs. → **PASS**. Pin: the check counts
  `<loc>` entries; it does not validate what they point at.

## H9 — challenge markers ONLY inside application/json script blocks (classifier)

Wave 15 (W15-001) stripped ld+json blocks from the vendor scan
when the page has visible text — but the strip regex is typed
to `application/ld+json`. A plain `application/json` data block
is the same species (structured-data metadata, not code the
page runs, not a loader), so the fix's generalization is the
question, not the principle.

- **H9a** — 200, small real article paragraph PLUS
  `<script type="application/json">{"description": "perimeterx
  protects this site"}</script>`. → **OPEN**. The visible
  content is served; the vendor name in a data block is
  metadata about the page, not a fired wall — the G1c species
  in a non-LD type. Predicted gap: the vendor scan strips
  ld+json only, so the classifier answers CHALLENGED /
  PerimeterX.
- **H9b** — 200, small page, ONLY an application/json block
  mentioning "perimeterx", no visible text. → **CHALLENGED /
  PerimeterX**. Pin (G1d species): with no visible content,
  the blob is the page.

## H10 — magic-link / email sign-in forms (classifier)

The CODE_ENTRY_FORM sibling: an email-entry form whose only
purpose is to send an authentication link is a two-keyed auth
barrier — an email input PLUS auth-link wording ("sign-in
link", "magic link", "password reset link") — exactly as
narrow as the code-entry rule, and immune to the F5 limitation's
false-positive worry (a bare "sign in" link has no email input
and no link wording; a newsletter form has no auth wording).

- **H10a** — 200, page whose only content is an email input
  plus "We'll send you a sign-in link" and a button, at a
  non-login URL. → **LOGIN_GATED**. The page's only content is
  an authentication barrier. Predicted gap: no magic-link
  signal exists, so the classifier reads OPEN.
- **H10b** — 200, newsletter signup: email input plus
  "Subscribe to our newsletter", no auth wording. → **OPEN**.
  Guard: the email input alone is not auth.
- **H10c** — 200, page whose only content is an email input
  plus "Send me a password reset link" and a button, at a
  non-login URL. → **LOGIN_GATED**. A reset link is an auth
  credential delivery, same family as H10a. Predicted gap.
- **H10d** — 200, page with only a "Sign in" link (no form, no
  input). → **OPEN**. Pin (F5 species): a link is not a
  barrier.
