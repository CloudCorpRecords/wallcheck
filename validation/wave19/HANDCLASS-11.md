# Wave 19 — Adversarial Battery v11: Hand Classifications

Discipline (as Waves 6, 10, 11, 12, 13, 14, 15, 16, 17, 18): every shape
below was classified BY HAND against SPEC's verdict definitions BEFORE
the classifier was allowed to see it. All shapes are NEW relative to Wave 6
(S1–S6), Wave 10 (B1–B10), Wave 11 (C1–C8), Wave 12 (D1–D9), Wave 13
(E1–E10), Wave 14 (F1–F8), Wave 15 (G1–G10), Wave 16 (H1–H10), Wave 17
(J1–J9), and Wave 18 (K1–K8). Deltas stated explicitly so they are not
mistaken for repeats: Wave 14's F2 covered alt text as page text (L2
here covers a phrase SPLIT across several images' alt attributes, which
no single-attribute scan can see); Wave 16's H10 covered email forms
whose purpose is stated as a link delivery (L3 here covers an
email-only Continue step with NO link/code wording at all — the auth
purpose must come from the page's sign-in context, not from a delivery
promise); Wave 18's K4 covered declared-but-dead sitemaps (L4 here
covers declared sitemaps that LOOK usable to the fallthrough but are
stubs by the grade's own test — a prolog-only document, a urlset of
empty locs); Wave 16's H7 covered charset/BOM variations (L5 here
covers LINE-ENDING variations — CRLF throughout, CR-only throughout);
Wave 18's K6 covered relative and empty locs (L6 here covers locs whose
content is a fragment or a bare query — references that do or do not
name a crawlable URL); Wave 12's D1 covered TR/AR and Wave 11's C4
covered KO (L7 here covers HE/FA/UR/BN — TR/AR/KO are already pinned
and are NOT re-claimed as new); Wave 17's J8 covered overlays named by
class/id markers (L8 here covers the NATIVE <dialog> element itself —
no class/id marker at all — and the open attribute that decides
whether it renders). Any mismatch is a defect candidate: fix
generalized with a capture-built fixture, or ledger it as a genuine
honest limitation with the reason. No silent passes, no per-shape
special cases. Per the Wave 17–18 pattern (passkey, QR), every new
signal in this battery carries visible-text gating and a served-page
size gate from birth, and every new signal family gets a negative
fixture in which the signal appears ONLY in an asset filename, a
script identifier, or a stylesheet class.

Reference — SPEC verdicts: OPEN = the resource was served; CHALLENGED =
an interactive human-verification challenge was presented; WALLED = a
hard block page, no challenge offered; LOGIN_GATED = content exists
behind authentication; RATE_LIMITED = a throttle; UNREACHABLE = the
fetch itself failed. Audit grades: PASS / WARN / FAIL per check.

## L1 — challenge markers ONLY inside <template> elements (classifier)

A <template> element's contents are inert: the browser parses them
but renders nothing until a script clones them into the document.
Template text is therefore configuration, not presented content —
the script-JSON (F1), data-attribute (H2), and style-block (H3)
species, not the noscript species (noscript text IS rendered for
clients without JS). The family conditioning applies unchanged:
when the page has visible text, template text is metadata; when
the page has no visible text at all, the blob IS the page and still
fires (the content-free fallback every suppression in this family
carries).

- **L1a** — 200, small real article paragraph PLUS a <template>
  containing "Verify you are human". → **OPEN**. The paragraph is
  served; the template renders nothing. Predicted gap: no template
  strip exists anywhere (not in _visible_text, not in the survival
  test, not in the vendor scan), so the template phrase drives
  GENERIC_HUMAN_CHECK and the classifier reads CHALLENGED.
- **L1b** — 200, small page whose ONLY content is a <template>
  containing "Verify you are human". → **CHALLENGED / Generic**.
  Pin (blob-is-the-page): with no visible text, the template is
  the page's only text and still fires — the fix must strip
  templates only when visible text exists, exactly like
  noscript/data/style.
- **L1c** — 200, 20 KB article PLUS a <template> containing the
  bare vendor token "perimeterx". → **OPEN**. Pin: the size gate
  already suppresses it; the template strip must agree.
- **L1d** — 200, small real article paragraph PLUS a <template>
  containing the bare vendor token "perimeterx". → **OPEN**. The
  paragraph is served; a vendor name in inert markup is metadata,
  like a data-* attribute (H2). Predicted gap: the vendor scan
  reads template text (no strip), so the classifier reads
  CHALLENGED / PerimeterX.
- **L1e** — 200, small real article paragraph PLUS
  `<script src="/templates/verify-human.js">` (asset-filename
  carrier). → **OPEN**. Guard: script blocks are already stripped
  from the survival test; the template fix must not disturb it.
- **L1f** — 200, small real article paragraph PLUS a <template>
  containing a JS-proof phrase ("Checking your browser").
  → **OPEN**. Same species as L1a in the JS_PROOF branch;
  predicted gap same as L1a.

## L2 — a challenge phrase SPLIT across several images' alt attributes (classifier)

F2 settled single-attribute alt text: an alt value IS page text
(the reader gets it when the image carries no text). A phrase split
across images is the H1 concatenated-text principle in attribute
form: no single attribute holds the phrase, but the images in
document order present it whole — exactly as spans present a split
word. Alt values in document order, joined with spaces, are
therefore a presented-text variant, like the concatenated-text
scan. The J7g boundary applies unchanged: fragments in different
languages compose no listed phrase.

- **L2a** — 403, small page, only content two images:
  alt="verify you are" + alt="human". → **CHALLENGED / Generic**.
  The images in order present "verify you are human". Predicted
  gap: the concatenated-text scan removes whole tags (alt values
  included), and the raw scan holds no single phrase, so the
  classifier reads WALLED (bare 403).
- **L2b** — 403, small page, only content
  `<input type="image" alt="verify you are human">`. → **CHALLENGED
  / Generic**. Pin (F2a species): a single alt value already
  fires via the raw scan; the alt-join variant must agree.
- **L2c** — 403, small page, only content an image map
  `<area alt="verify you are human">`. → **CHALLENGED / Generic**.
  Pin: same single-attribute species (area is interactive; its
  alt is its accessible name).
- **L2d** — 200, 20 KB article, an image whose alt reads "verify
  you are human". → **OPEN**. Pin (F2c species): the served-page
  gate — attribute text on a real article is content about
  checks, not a check.
- **L2e** — 403, small page, only content two images:
  alt="verify you are" + alt="kein roboter" (EN half + DE
  fragment). → **WALLED, vendor none**. Guard (J7g species):
  fragments across languages compose no listed phrase.
  Correction record: the first draft used alt="ich bin kein
  roboter" as the second half, but that IS a complete DE phrase
  (Wave 6) on its own, so the classifier rightly read CHALLENGED
  — the fixture, not the classifier, was wrong. Corrected to a
  true fragment ("kein roboter" is no listed phrase).
- **L2f** — 200, small real article paragraph PLUS a <script>
  block preloading `["verify you are", "human"]` (script-identifier
  carrier). → **OPEN**. Guard: script blocks are configuration
  when the page has visible text (F1); the alt-join variant must
  read attributes of rendered elements only, never script text.

## L3 — login walls presenting an email-only "Continue" step (classifier)

H10's magic-link rule needs link wording; G6's code-entry rule
needs a code input; the login heuristic needs a login URL. A
modern sign-in flow's first step is none of those: an email input
plus a Continue button, where the auth purpose lives in the page's
sign-in context ("Sign in" heading) rather than in any delivery
promise. That is the code-entry rule's next sibling, with the same
two-key discipline plus the button: (1) an email input, (2) a
Continue button, (3) auth-purpose wording ("sign in" / "log in" /
"authenticate") in rendered visible text. All three keys, from
birth, with the served-page size gate the siblings carry. Signup
wording ("create account", "sign up") is deliberately NOT an auth
purpose here: a newsletter's "sign up" step with an email input
and a Continue button must not fire, and the signup-form boundary
is ledgered separately (see L3g).

- **L3a** — 200, page whose only content is a "Sign in" heading
  + an email input + a "Continue" button, at a non-login URL.
  → **LOGIN_GATED**. The page's only content is an
  authentication barrier. Predicted gap: no rule names it (no
  link wording, no code input, no login URL), so the classifier
  reads OPEN.
- **L3b** — 200, page whose only content is an email input + a
  "Continue" button, NO auth wording (checkout email capture).
  → **OPEN**. Guard: an email capture without auth purpose is
  not a barrier — the auth-purpose key is load-bearing.
- **L3c** — 200, email input + "Continue" button at a login URL.
  → **LOGIN_GATED**. Pin: the login heuristic already fires.
- **L3d** — 200, newsletter form: email input + "Subscribe"
  button, plus a "Sign in" link in the nav (no form, no input
  for it). → **OPEN**. Guard: Subscribe is not Continue, and a
  bare sign-in link is not a barrier (H10d species) — the
  Continue key is load-bearing.
- **L3e** — 200, small real article paragraph PLUS a <script>
  block with identifier `continueSignIn` and a newsletter form
  (email input + "Subscribe" button), no auth wording in visible
  text. → **OPEN**. Guard (script-identifier carrier): the auth
  purpose must appear in rendered visible text, never in script
  text — the rubygems/QR lesson, applied from birth.
- **L3f** — 200, 20 KB article PLUS a "Sign in" section (heading
  + email input + "Continue" button) embedded in the page.
  → **OPEN**. Guard: the served-page size gate — a full served
  page with an auth form is not only a form (the W17-007
  boundary, same as the siblings).
- **L3g** — 200, page whose only content is a "Create account"
  heading + an email input + a "Continue" button, at a non-login
  URL. → **OPEN** (boundary pin, not a defect). A signup form is
  arguably an auth barrier, but the classifier's auth family has
  never claimed signup forms, and admitting "create account" /
  "sign up" as auth purpose would fire on newsletter signups
  (L3d's family). Ledgered as an open boundary question, not
  papered over: the narrow rule stays narrow.

## L4 — robots-declared sitemaps that LOOK usable to the fallthrough but are stubs by the grade's own test (audit tool)

The audit's fallthrough (Wave 14) tries declared Sitemap: URLs in
order until _is_sitemap_doc says "usable". But _is_sitemap_doc
counts a bare `<?xml` prolog as usable, while _check_sitemap
grades a prolog-only document WARN (SITEMAP_NO_URLS) — and counts
a urlset/sitemapindex as usable regardless of loc content, while
the grade requires a nonempty loc (Wave 18, W18-K6c/d). The
fallthrough's usability test and the grade's usability test
disagree, so a stub document early in the declaration list blocks
a real sitemap later in the list. The fix must be one test, used
in both places: a document is usable only when it carries at
least one nonempty <loc> (urlset or sitemapindex; a prolog alone
is not a document).

- **L4a** — robots declares [prolog-only document, real urlset];
  /sitemap.xml 404s. → sitemap **PASS** via the second. Predicted
  gap: the fallthrough stops at the prolog-only doc (counts as
  usable), the grade reads WARN SITEMAP_NO_URLS, and the real
  urlset is never tried.
- **L4b** — robots declares [urlset with empty <loc> elements
  only, real urlset]; /sitemap.xml 404s. → sitemap **PASS** via
  the second. Predicted gap, same fix: the fallthrough counts a
  loc-less urlset as usable.
- **L4c** — robots declares [dead URL (404), real urlset];
  /sitemap.xml 404s. → sitemap **PASS** via the second. Pin
  (Wave 14 fallthrough species): dead declarations already fall
  through.
- **L4d** — robots declares [dead, dead, real urlset];
  /sitemap.xml 404s. → sitemap **PASS** via the third. Pin:
  the fallthrough already walks the whole list.
- **L4e** — robots declares [prolog-only document] only;
  /sitemap.xml 404s. → sitemap **WARN** (SITEMAP_NO_URLS) with
  DECLARED_SITEMAP_DEAD evidence. Pin: with nothing usable
  anywhere, the grade is already WARN and the evidence rule
  (Wave 18, W18-K4a/d) already names the dead declaration.
- **L4f** — /sitemap.xml serves a real urlset; robots declares
  a dead URL. → sitemap **PASS**. Pin: no fallthrough is needed
  when the conventional path serves.
- **L4g** — robots carries a Sitemap: line inside a comment
  (J5 species) plus a real /sitemap.xml. → sitemap **PASS**.
  Pin: commented declarations are not declarations.

## L5 — llms.txt files with CRLF / CR-only line endings (audit tool)

Line endings are not content: a CRLF file is the same document as
its LF twin, and a CR-only file is the same document too. The
frontmatter strip anchors on `\n` — CRLF is handled (`\r?\n`),
but CR-only is not, so a CR-only frontmatter-only stub keeps its
metadata URLs as content. The generalized fix is line-ending
normalization before the frontmatter anchor (CR and CRLF both
become LF), applied once at the top of the llms check — the same
"parameters are not content" principle as H7's charset/BOM rule.

- **L5a** — llms.txt with CRLF line endings throughout, real
  markdown index (heading + links). → **PASS**. Likely pin:
  the frontmatter regex and the link tests already tolerate
  `\r\n` — included because a line-ending change that silently
  regrades a real index would be a regression, and pins are
  cheaper than regressions.
- **L5b** — llms.txt with CRLF line endings, frontmatter-only
  stub (title + a `url:` field, no index content). → **WARN**
  (LLMS_STUB family). Likely pin: the frontmatter regex handles
  `\r?\n`, so the metadata URL does not count.
- **L5c** — llms.txt with CRLF line endings, HTML shell body.
  → **FAIL** (SOFT_404_HTML). Pin: the HTML gate reads the body
  regardless of line endings.
- **L5d** — llms.txt with CR-only line endings throughout,
  frontmatter-only stub (title + a `url:` field, no index
  content). → **WARN** (LLMS_STUB family). Predicted gap: the
  frontmatter regex requires `\n`, so the strip misses, the
  metadata URL counts as content, and the file reads PASS.
- **L5e** — llms.txt with CR-only line endings, real markdown
  index (heading + links). → **PASS**. Pin: link/URL tests do
  not depend on line endings, so a real index still passes —
  the normalization must not disturb it.
- **L5f** — llms.txt with CRLF line endings + a UTF-8 BOM +
  frontmatter-only stub. → **WARN** (LLMS_STUB family). Guard:
  BOM strip and line-ending normalization compose — neither may
  defeat the other (H7d species, extended to CRLF).

## L6 — sitemap.xml <loc> entries carrying only a fragment or a bare query (audit tool)

A <loc> is a URL reference. A query-string reference ("?id=1",
"/page?id=1") resolves against the sitemap's URL and names a
destination, exactly like a relative reference (K6a/b). A
fragment-only reference ("#section") names no crawlable URL at
all — fragments are client-side; a sitemap of fragments indexes
nothing. The W18 nonempty-loc test counts any non-empty content,
so fragment-only entries pass it — the same "names nothing"
hole K6c/d closed for empty elements, in a thinner disguise.

- **L6a** — urlset whose <loc> entries carry query strings
  (`/page?id=1`, `/page?id=2`). → **PASS**. Pin: query-string
  references name destinations.
- **L6b** — urlset whose ONLY entries are fragment-only
  `<loc>#section</loc>` elements. → **WARN** (SITEMAP_NO_URLS
  species: the document names no URLs). Predicted gap: the
  nonempty test counts "#section" as content, so the file reads
  PASS.
- **L6c** — urlset whose ONLY entry is a bare query
  `<loc>?id=1</loc>`. → **PASS**. A bare query resolves against
  the sitemap's URL and names a URL (the sitemap's own path
  with parameters) — a reference, not a fragment.
- **L6d** — urlset mixing fragment-only entries with one
  query-string entry. → **PASS**. Pin: one good loc suffices
  (the W15-010 one-URL principle).
- **L6e** — urlset whose ONLY entries are whitespace-only
  `<loc>   </loc>` elements. → **WARN**. Pin (K6d species):
  whitespace is not content.

## L7 — challenge pages in Hebrew, Persian, Urdu, and Bengali (classifier)

Wave 6 (ES/DE/FR/JA/PT), Wave 11 (IT/NL/KO), Wave 12 (PL/TR/AR/ZH/RU),
Wave 17 (FI/NO/DA/SE), and Wave 18 (PT-BR/ID/VI/TH) built the
localized list one family at a time; the principle generalizes,
and these four languages are the next family. Each phrase is an
interactive human-verification demand in that language, matched
like the English markers, gated like every generic marker. TR, AR,
and KO are already in the list (D1, C4) and are NOT re-claimed
here — their coverage is verified by grep, not by new fixtures.

- **L7a** — 403, small page, Hebrew only: "אמת שאינך רובוט"
  (verify you are not a robot). → **CHALLENGED / Generic**.
  Predicted gap: the phrase is not in the localized list.
- **L7b** — 403, small page, Persian only: "تأیید کنید که ربات
  نیستید" (confirm you are not a robot). → **CHALLENGED /
  Generic**. Predicted gap.
- **L7c** — 403, small page, Urdu only: "تصدیق کریں کہ آپ روبوٹ
  نہیں ہیں" (confirm you are not a robot). → **CHALLENGED /
  Generic**. Predicted gap.
- **L7d** — 403, small page, Bengali only: "আপনি রোবট নন তা
  নিশ্চিত করুন" (confirm you are not a robot). → **CHALLENGED /
  Generic**. Predicted gap.
- **L7e** — 403, small page, Hebrew only: "אני לא רובוט" (I am
  not a robot). → **CHALLENGED / Generic**. Predicted gap.
- **L7f** — 200, 20 KB article about bots quoting a Hebrew
  phrase. → **OPEN**. Pin: the served-page gate — a quoted
  phrase on a real article is content about checks, not a check.
- **L7g** — 403, small page, code-switched fragments: "אמת"
  (HE half) + "ربات نیستید" (FA half), neither complete.
  → **WALLED, vendor none**. Pin (J7g species): fragments
  across languages compose no listed phrase.

## L8 — pages where the challenge lives inside a native <dialog> element (classifier)

J8 settled overlays named by class/id markers; K2 settled sticky
banners. The native <dialog> element is the same species with no
marker at all: a <dialog open> renders as a modal over the page,
and a challenge inside it blocks the content beneath — the J8
two-key logic (blocking container + challenge phrase) with the
tag itself as the first key. The open attribute is load-bearing:
a <dialog> without open renders nothing at all, so it cannot
block anything — the fix must require it, or closed dialogs
become false overlays. The login exclusion mirrors J8: a dialog
on an identified login page is auth furniture.

- **L8a** — 200, 20 KB article PLUS `<dialog open>` containing
  "Verify you are human" + a checkbox. → **CHALLENGED /
  Generic**. The open dialog presents an interactive check over
  the article. Predicted gap: the overlay tag list matches
  class/id markers only, so a bare <dialog> tag is invisible
  to it and the size gate suppresses the phrase — the
  classifier reads OPEN.
- **L8b** — 200, 20 KB article PLUS `<dialog>` (no open
  attribute) containing "Verify you are human". → **OPEN**. A
  closed dialog renders nothing; it blocks nothing. The fix
  must require the open attribute, or this guard fails.
- **L8c** — 200, 20 KB article PLUS `<dialog open>` containing
  only cookie text. → **OPEN**. Guard: a dialog without a
  challenge phrase is furniture (J8b species).
- **L8d** — 200, small page PLUS `<dialog open>` containing a
  human-check phrase. → **CHALLENGED / Generic**. Pin: the
  small-page path already fires; the dialog rule must agree.
- **L8e** — 200, 20 KB article PLUS `<dialog open>` containing
  a JS-proof phrase ("Checking your browser"). → **CHALLENGED /
  Generic**. Same rule in the JS_PROOF branch; predicted gap
  same as L8a.
- **L8f** — 200, 20 KB article at a login URL PLUS
  `<dialog open>` containing a human-check phrase. → **LOGIN_GATED**.
  Pin: the login exclusion mirrors J8 — auth furniture on a
  login page is owned by the login heuristic.
- **L8g** — 200, 20 KB article PLUS a stylesheet class
  `.dialog-challenge` (stylesheet-class carrier) and no dialog
  element. → **OPEN**. Guard: style blocks are configuration,
  and no dialog tag exists — the rule must match the element,
  never a class name alone.
