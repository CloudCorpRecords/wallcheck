# Wave 18 — Adversarial Battery v10: Hand Classifications

Discipline (as Waves 6, 10, 11, 12, 13, 14, 15, 16, 17): every shape below was
classified BY HAND against SPEC's verdict definitions BEFORE the
classifier was allowed to see it. All shapes are NEW relative to Wave 6
(S1–S6), Wave 10 (B1–B10), Wave 11 (C1–C8), Wave 12 (D1–D9), Wave 13
(E1–E10), Wave 14 (F1–F8), Wave 15 (G1–G10), Wave 16 (H1–H10), and Wave 17
(J1–J9). Deltas stated explicitly so they are not mistaken for repeats:
Wave 16's H3 covered CSS `content:` declarations and stylesheet text
(K1 here covers CSS *custom properties* — values that exist only as
`--name` declarations, consumed or not); Wave 17's J8 covered
*full-screen* overlay modals (K2 here covers *sticky banners* — bars
that sit over content without taking the screen); Wave 10's B5 covered
cookie-consent banners (K2 covers banners carrying a *challenge*, not
a consent note); Wave 15's G6 covered code-entry forms in general
(K3 here covers *delivery-channel* code prompts — SMS/email codes in
digit-box inputs, which G6's input-name list does not name); Wave 17's
J5 covered *commented* Sitemap lines (K4 here covers *declared but
dead* Sitemap URLs); Wave 12's D7 covered llms format variants (K5
here covers llms reached only through a *trailing-slash redirect*);
Wave 16's H8 covered sitemapindex circularity (K6 here covers
*relative* `<loc>` entries and *empty* `<loc>` elements); Wave 17's
J7 covered Nordic phrases (K7 here covers PT-BR, Indonesian,
Vietnamese, and Thai); Wave 14's F2 covered alt/title attribute text
(K8 here covers *aria-label* text, which has different presentation
semantics per element type). Any mismatch is a defect candidate: fix
generalized with a capture-built fixture, or ledger it as a genuine
honest limitation with the reason. No silent passes, no per-shape
special cases.

Reference — SPEC verdicts: OPEN = the resource was served; CHALLENGED =
an interactive human-verification challenge was presented; WALLED = a
hard block page, no challenge offered; LOGIN_GATED = content exists
behind authentication; RATE_LIMITED = a throttle; UNREACHABLE = the
fetch itself failed. Audit grades: PASS / WARN / FAIL per check.

## K1 — challenge markers ONLY in CSS custom properties (classifier)

A CSS custom property (`--name: value`) is stylesheet configuration:
it renders nothing by itself. It renders only when a `content:` (or
other) declaration *consumes* it via `var()`. The H3 principle
(configuration vs presented content) therefore splits two ways: an
unconsumed property value is configuration like any other stylesheet
text (H3b/H3e species), while a value consumed by a `content:` rule
on a gate element IS presented text (H3a species) — but only when
the value is whole. A phrase *split across two properties* and
reassembled only by `var()` substitution is rendered whole to the
reader yet exists nowhere as one substring to a static scan — the
H1 concatenated-text principle in CSS form, and the question is
whether a substring scanner can honestly claim it.

- **K1a** — 200, small real article paragraph PLUS
  `<style>:root{--notice:"verify you are human"}</style>`,
  the property never consumed by any rule. → **OPEN**. The
  article is served; an unconsumed property value is stylesheet
  configuration, never rendered. Pin (H3b species in property
  form): the style-block strip already covers it.
- **K1b** — 200, small page, only a `<div class="gate">` plus
  `<style>.gate::before{content:"verify you are human"}</style>`.
  → **CHALLENGED / Generic**. Pin (H3a species): the CSS content
  is the page's only presented text.
- **K1c** — 200, small page, only a `<div class="gate">` plus
  `<style>:root{--a:"verify you are "; --b:"human"}
  .gate::before{content:var(--a) var(--b)}</style>`.
  → **CHALLENGED / Generic**. The rendered `::before` text is
  exactly "verify you are human" — a presented challenge, however
  the stylesheet spells it. Predicted gap: no scan resolves
  `var()` substitution, and the style strip removes the property
  text from every variant, so the classifier reads OPEN.
  Fix-or-limitation question, stated now: resolving this needs a
  CSS cascade/content model (parse `content:` value lists, resolve
  `var()` chains, concatenate string tokens per CSS rendering
  rules) — a regex substitution does NOT suffice, because the
  nospace variant's text would still carry the declaration
  punctuation between the halves. If no bounded fix exists, this
  is ledgered as an honest limitation in the same family as the
  Wave 3 silent-JS-proof boundary, not papered over.
- **K1d** — 200, small real article paragraph PLUS
  `<style>:root{--vendor:"perimeterx"}</style>`, unconsumed.
  → **OPEN**. Pin (H3e species in property form): a vendor name
  in stylesheet configuration is not a fired wall.
- **K1e** — 200, small page, only a style block with a custom
  property holding the bare token "captcha", never consumed.
  → **CHALLENGED / Generic**. Pin (H3f species): with no visible
  content, the stylesheet is the page's only text.
- **K1f** — 200, 20 KB article PLUS a custom property holding a
  human-check phrase, consumed by a `::before` rule on a
  decorative note element (no gate, no interaction demanded).
  → **OPEN**. Pin (H3b species): a decorative pseudo-element
  string is not an interactive challenge, and the size gate
  protects the article either way.

## K2 — pages where the challenge is a sticky banner over real content (classifier)

J8 settled full-screen overlays: a modal that blocks content is a
presented challenge whatever the page size. A sticky banner is the
same species at smaller scale: a fixed-position bar carrying an
interactive check, sitting *over* content the reader came for. The
distinguishing keys are the same two — a banner-marked container
PLUS a human-check or JS-proof phrase inside it. A banner without
a challenge phrase is furniture (cookie bars, newsletter bars),
and a banner that merely sits in the document flow is prose layout,
not an overlay — the size gate still protects it.

- **K2a** — 200, 20 KB article PLUS a sticky banner div
  (`class="announcement-banner"`, `position:fixed`) containing
  "Verify you are human" + a checkbox. → **CHALLENGED /
  Generic**. The banner presents an interactive check over the
  article; full-screen-ness was never the load-bearing property
  of J8, blocking presentation was. Predicted gap: the overlay
  tag list (overlay/modal/popup/lightbox/dialog) has no banner
  marker, so the size gate suppresses the phrase and the
  classifier reads OPEN.
- **K2b** — 200, 20 KB article PLUS a sticky banner containing
  only cookie text. → **OPEN**. Guard (J8b species): a banner
  without a challenge phrase is furniture.
- **K2c** — 200, 20 KB article PLUS a sticky newsletter banner
  ("Subscribe to our newsletter"). → **OPEN**. Guard: same
  principle, subscription furniture.
- **K2d** — 200, small page PLUS a sticky banner with a
  human-check phrase. → **CHALLENGED / Generic**. Pin: the
  small-page path already fires; the banner rule must agree.
- **K2e** — 200, 20 KB article PLUS a sticky banner containing
  a JS_PROOF phrase ("Checking your browser"). → **CHALLENGED /
  Generic**. Same signal in the JS_PROOF branch; predicted gap
  same as K2a.
- **K2f** — 200, 20 KB article PLUS an in-flow banner div (no
  fixed/sticky positioning, no overlay marker) containing a
  human-check phrase. → **OPEN**. Guard (J8c species): a banner
  that does not sit over content is layout, and the size gate
  protects prose mentions.

## K3 — login walls presenting an SMS/email code prompt in digit-box inputs (classifier)

G6's code-entry rule names its inputs: otp/2fa/auth-code/
verification-code/security-code/one-time-code, or exactly "code".
Real SMS/email code prompts do not use those names: they use a row
of digit boxes (`digit-1` … `digit-6`) and delivery wording ("the
code we texted/emailed to you"). A digit box is presented barrier
machinery exactly like a named code input — the ceremony is the
same, only the input names differ — so the auth species must be
keyed on *delivery wording + digit-box inputs*, not on G6's list.
The guards that keep G6 honest apply here too: delivery wording
without a code/digit input is prose, and a phone-number request
form is not yet a code prompt.

- **K3a** — 200, page whose only content is "Enter the 6-digit
  code we texted to •••1234" + six inputs named `digit-1` …
  `digit-6`, at a non-login URL. → **LOGIN_GATED**. The page's
  only content is an authentication barrier. Predicted gap:
  `digit-N` matches no G6 input name, so the classifier reads
  OPEN.
- **K3b** — 200, page whose only content is "Enter the
  verification code sent via SMS" + an input named "code".
  → **LOGIN_GATED**. Pin: G6 already fires (named input +
  "verification code" wording).
- **K3c** — 200, SMS code prompt (digit boxes + texted wording)
  at a login URL. → **LOGIN_GATED**. Pin: the login heuristic.
- **K3d** — 200, article ABOUT SMS verification codes (prose
  explaining how texted codes work, no form). → **OPEN**.
  Guard: prose about codes is content, not a prompt.
- **K3e** — 200, page whose only content is "Enter the code we
  emailed to you" + six digit-box inputs, at a non-login URL.
  → **LOGIN_GATED**. Same family as K3a in the email channel;
  predicted gap same as K3a.
- **K3f** — 200, page whose only content is "Enter your phone
  number to receive a code" + a phone input, no code/digit
  input. → **OPEN**. Guard: a request form is not a code prompt
  — the barrier (the code entry) is not presented yet.

## K4 — robots.txt files whose Sitemap: line points to a 404 (audit tool)

A declared-but-dead sitemap is a broken promise, not an absent
file — but the grade question is narrower: the audit already falls
through declared lines in order (Wave 14) and grades the sitemap
the site actually publishes. The new ground is *evidence*: when no
sitemap serves anywhere, does the audit record that the site
*declared* one and it is dead, or does a dead declaration look
exactly like no declaration at all? Grades below follow the
existing fallthrough; the evidence question is where a gap may
live.

- **K4a** — robots.txt open (no disallows) + `Sitemap:
  https://x.example/sitemap.xml`; /sitemap.xml 404s; no other
  sitemap. → robots **PASS**; sitemap **WARN** (STATUS_404).
  Evidence question: the WARN names the 404 but not the dead
  declaration — a reader cannot tell "declared and dead" from
  "never declared". Predicted gap (evidence only): no
  DECLARED_SITEMAP_DEAD evidence exists.
- **K4b** — robots declares a sitemap URL that 404s, but
  /sitemap.xml serves a real urlset. → sitemap **PASS**. Pin:
  the conventional path serves; a dead declaration elsewhere
  does not demote a serving sitemap.
- **K4c** — robots declares two sitemaps: the first 404s, the
  second serves a urlset. → sitemap **PASS** via the second.
  Pin (Wave 14 fallthrough species).
- **K4d** — robots declares a sitemap URL that 404s, and
  /sitemap.xml answers 200 with HTML (not XML). → sitemap
  **WARN** (STATUS_200_NOT_XML). Pin: neither candidate is a
  sitemap document.
- **K4e** — robots with NO sitemap declaration + /sitemap.xml
  404. → sitemap **WARN** (STATUS_404), with no dead-declaration
  evidence — correctly, since nothing was declared. Pin
  distinguishing K4a's evidence question.

## K5 — llms.txt served through a trailing-slash redirect (audit tool)

The audit's fetcher follows redirects (urllib redirect handler
with a recorded chain), so a trailing-slash hop should be
transparent: the grade follows the final document, not the hop.
All five shapes are expected pins — the redirect is new ground
for the llms check, but the machinery already handles it — included
because a redirect that *changes* the grade would be a silent
misgrade, and pins are cheaper than regressions.

- **K5a** — /llms.txt 301 → /llms.txt/ serving a real markdown
  index. → **PASS**. The final document is the index.
- **K5b** — /llms.txt 301 → /llms.txt/ serving an HTML shell.
  → **FAIL** (SOFT_404_HTML). The final document is a shell.
- **K5c** — /llms.txt 301 → /llms.txt/ 404. → **WARN**
  (STATUS_404). The final answer is absence.
- **K5d** — /llms.txt 301 → https://docs.x.example/llms serving
  a real index (cross-host hop). → **PASS**. The fetcher
  follows; the grade follows the final document.
- **K5e** — /llms.txt 301 → itself (redirect loop). → **WARN**
  (fetch failure / non-200 status). A loop serves no file.

## K6 — sitemap.xml files with relative <loc> entries (audit tool)

A `<loc>` is a URL reference, and relative references are valid:
root-relative (`/docs/page`) and document-relative (`docs/page`)
both resolve against the sitemap's URL, so both name destinations
exactly like absolute URLs (H8's counting rule, extended to
reference form). The genuinely new question is the *empty*
`<loc>`: the current check tests `<loc` tag presence, not loc
*content* — so a sitemap whose entries name nothing may pass a
test meant to catch "names no URLs" (Wave 15, W15-010).

- **K6a** — urlset with `<loc>/docs/page1</loc>` and
  `<loc>/docs/page2</loc>` (root-relative). → **PASS**. Pin:
  relative references name destinations.
- **K6b** — urlset with `<loc>docs/page1</loc>`
  (document-relative). → **PASS**. Pin: same rule, other form.
- **K6c** — urlset whose ONLY entries are empty
  `<loc></loc>` elements. → **WARN** (SITEMAP_NO_URLS species:
  the document names no URLs). Predicted gap: the check tests
  `<loc` presence, and empty elements match it, so the file
  reads PASS.
- **K6d** — urlset whose ONLY entries are whitespace-only
  `<loc>   </loc>` elements. → **WARN**. Same gap, same fix:
  a loc counts only when its content is non-empty.
- **K6e** — sitemapindex with a relative
  `<loc>/sitemap-posts.xml</loc>`. → **PASS**. Pin (H8a
  species in relative form): the check counts loc entries, it
  does not follow them.

## K7 — challenge pages in Portuguese (BR), Indonesian, Vietnamese, and Thai (classifier)

Wave 6 (ES/DE/FR/JA/PT), Wave 11 (IT/NL/KO), Wave 12 (PL/TR/AR/ZH/RU),
and Wave 17 (FI/NO/DA/SE) built the localized list one family at a
time; the principle generalizes, and these four languages are the
next family. Each phrase is an interactive human-verification
demand in that language, matched like the English markers, gated
like every generic marker. Note the PT-BR delta: the European-PT
"não sou um robô" already covers the fuller Brazilian form by
substring, so only the distinct "Confirme…" demand is new.

- **K7a** — 403, small page, Brazilian Portuguese only:
  "Confirme que você não é um robô." → **CHALLENGED / Generic**.
  Predicted gap: the phrase is not in the localized list.
- **K7b** — 403, small page, Brazilian Portuguese: "Eu não sou
  um robô." → **CHALLENGED / Generic**. Pin: the existing PT
  phrase "não sou um robô" already matches it by substring.
- **K7c** — 403, small page, Indonesian only: "Konfirmasi bahwa
  Anda bukan robot." → **CHALLENGED / Generic**. Predicted gap.
- **K7d** — 403, small page, Indonesian only: "Saya bukan robot."
  → **CHALLENGED / Generic**. Predicted gap.
- **K7e** — 403, small page, Vietnamese only: "Xác nhận bạn không
  phải là robot." → **CHALLENGED / Generic**. Predicted gap.
- **K7f** — 403, small page, Vietnamese only: "Tôi không phải là
  robot." → **CHALLENGED / Generic**. Predicted gap.
- **K7g** — 403, small page, Thai only: "ยืนยันว่าคุณไม่ใช่หุ่นยนต์"
  → **CHALLENGED / Generic**. Predicted gap.
- **K7h** — 403, small page, Thai only: "ฉันไม่ใช่หุ่นยนต์"
  → **CHALLENGED / Generic**. Predicted gap.
- **K7i** — 200, 20 KB article about bots quoting a Thai phrase.
  → **OPEN**. Pin: the served-page gate — a quoted phrase on a
  real article is content about checks, not a check.
- **K7j** — 403, small page, code-switched fragments: "Confirme /
  bukan robot" (half a PT-BR phrase, half an Indonesian phrase,
  neither complete). → **WALLED, vendor none**. Pin (J7g
  species): fragments across languages compose no listed phrase.

## K8 — challenge phrases ONLY in aria-label attributes (classifier)

Wave 14 (F2) settled alt/title attribute text: alt is rendered
fallback text, title is hover text — both ARE page text. Aria-label
splits by element type, and that split is the new ground: an
aria-label on an *interactive* element (button, link, input) IS the
element's accessible name — announced to assistive-technology users,
presented text by any honest definition — while an aria-label on a
*non-interactive* element (a div, a span) is ignored by assistive
technology entirely: metadata, not presentation. The data-*/style
principle (configuration is not content when the page has visible
text) therefore applies to non-interactive aria-labels, and the F2
principle applies to interactive ones.

- **K8a** — 200, small page, only an icon button
  `<button aria-label="Verify you are human">✓</button>`, no other
  text. → **CHALLENGED / Generic**. Pin: with no visible content
  the raw scan fires on the label (and the label is the button's
  presented name in any case).
- **K8b** — 200, small real article paragraph PLUS a button with
  `aria-label="Verify you are human"`. → **CHALLENGED /
  Generic**. The button's accessible name is presented text to
  AT users, and the small-page rule fires on presented challenge
  phrases. Pin (via the raw scan, which already reads attribute
  values — the path is noted, the verdict is what matters).
- **K8c** — 200, 20 KB article PLUS a button with
  `aria-label="Verify you are human"`. → **OPEN**. Pin: the
  served-page gate — a named button on a real article is not a
  wall.
- **K8d** — 200, small real article paragraph PLUS a plain
  `<div aria-label="perimeterx">` (non-interactive, no text).
  → **OPEN**. The div's label is ignored by assistive technology
  and seen by nobody — metadata, like a data-* attribute.
  Predicted gap: the vendor scan strips data-*/style/head/
  noscript text but not aria-label values, so it answers
  CHALLENGED / PerimeterX.
- **K8e** — 200, small page, only an `<img>` with
  `aria-label="Verify you are human"` (no alt, no text).
  → **CHALLENGED / Generic**. Pin (F2 species): an image's
  accessible name is its rendered fallback text.
