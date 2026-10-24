# Wave 28 — Adversarial Battery v20: Hand Classifications

Discipline (as Waves 6, 10–27): every shape below was classified BY
HAND against SPEC's verdict definitions BEFORE the classifier was
allowed to see it. All shapes are NEW relative to Wave 6 (S1–S6),
Wave 10 (B1–B10), Wave 11 (C1–C8), Wave 12 (D1–D9), Wave 13
(E1–E10), Wave 14 (F1–F8), Wave 15 (G1–G10), Wave 16 (H1–H10),
Wave 17 (J1–J9), Wave 18 (K1–K8), Wave 19 (L1–L8), Wave 20
(M1–M10), Wave 21 (N1–N8), Wave 22 (P1–P8), Wave 23 (Q1–Q8),
Wave 24 (R1–R8), Wave 25 (T1–T8), Wave 26 (U1–U8), and Wave 27
(V1–V8). Deltas stated explicitly so they are not mistaken for
repeats: the presented-element survey (figcaption R1, summary R8,
blockquote T1, textarea T8, label U1, button U8, table cells V1,
slot Q6, picture text Q1) has never put a marker inside an
`<output>` element — W1 closes that survey's last common form
element. P2 classified bare 451s and U2 the 451 + Retry-After
composition; W2 adds the RFC 7725 `Link: rel="blocked-by"` header
to the status — a header no branch reads today. The auth family
names code entry (G6), passkey/WebAuthn (H5), magic link (H10),
delivery codes (K3), email-Continue (L3), authenticator (N3),
SSO (P3), push approval (R3), QR (J4), employee ID (T3),
badge-tap (U3), and biometric (V3); W3 covers the Windows PIN /
Windows Hello prompt, whose wording matches none of them (grep:
"windows pin" and "windows hello" appear nowhere in src/ or
tests/ before this wave). V4 (Wave 27) covered the version suffix
on a robots product token; W4 covers the token's separator
characters themselves — underscore vs hyphen — a different
composition (RFC 9309 tokens match exactly; the characters are
not interchangeable). E6 classified the title-ONLY llms.txt;
W5 classifies the table-of-contents llms.txt — headings and
section prose, structurally richer than a title line, still
pointing nowhere. R6 pinned mixed www/non-www (same registrable
domain) sitemap locs and V6 pinned IP literals; W6 covers locs
on a different TLD entirely. The localized list stands at 55
language groups; W7's four (Burmese, Sinhala, Amharic,
Azerbaijani) were grep-verified absent from classify.py, every
HANDCLASS file, and tests/ before writing (below). J8 named the
class/id-marked overlay, K2 the sticky banner, L8 the native
<dialog>; W8 covers the ARIA species — role="alertdialog" (and
aria-modal="true") on a plain div with no overlay class at all.
Any mismatch is a defect candidate: fix generalized with a
capture-built fixture, or ledger it as a genuine honest
limitation with the reason — and per Wave 25's lesson, check
every mismatch against the older pins before fixing (a Wave 6
pin vetoed Wave 25's 410 "fix"; a mismatch against an old pin is
a hand-classification question first, a defect second). No
silent passes, no per-shape special cases. Per the Waves 17–27
pattern, every new signal family carries visible-text gating and
a served-page size gate from birth, with a negative fixture per
family using an asset-filename, script-identifier, or
stylesheet-class carrier.

Reference — SPEC verdicts: OPEN = the resource was served;
CHALLENGED = an interactive human-verification challenge was
presented; WALLED = a hard block page, no challenge offered;
LOGIN_GATED = content exists behind authentication; RATE_LIMITED
= a throttle; UNREACHABLE = the fetch itself failed. Audit
grades: PASS / WARN / FAIL per check.

## W1 — challenge markers ONLY inside `<output>` elements (classifier)

An `<output>` element's text is rendered content — it is the
form's result region, presented in place exactly like a table
cell (V1) or a label (U1): no strip names it, and none should —
tag-stripping removes the tag and keeps its text.

- **W1a** — 200, content-free page, only
  `<output>Verify you are human</output>`. → **CHALLENGED /
  Generic**. The output is the page's only text and it is
  presented. Pin expected.
- **W1b** — 200, small real paragraph PLUS an `<output>` phrase.
  → **CHALLENGED / Generic**. Presented text on a non-served
  page fires. Pin expected.
- **W1c** — 200, BIG_ARTICLE PLUS an `<output>` phrase. →
  **OPEN**. Pin: the served-page size gate.
- **W1d** — 403, small page, only an `<output>` phrase. →
  **CHALLENGED / Generic**. Pin: 403 is a GENERIC_OK status and
  the phrase is presented.
- **W1e** — 200, content-free page, only
  `<output>42 results found</output>`. → **OPEN**. Pin: an
  output element alone is furniture; without a phrase nothing
  fires.
- **W1f** — 200, BIG_ARTICLE containing a real form whose
  `<output name="result">` default text is the phrase. →
  **OPEN**. Pin: output text inside a working form on a served
  page is content, the form-result species of W1c.

## W2 — HTTP 451 carrying a Link header to a policy page (classifier)

RFC 7725 §3 invites a 451 response to carry
`Link: <policy-uri>; rel="blocked-by"` naming who imposed the
legal block. The 451 verdict is status-governed (W10-B3c; P2
pinned the bare species, U2 the Retry-After composition): the
header documents the refusal, it does not soften, sharpen, or
reroute it. A Link header is also NOT a redirect species — the
redirect-target family is Location, Refresh, meta refresh, JS
location, form actions, iframe/object/embed sources; a Link
names documentation about the response, never a route the
client is sent to, and must not become one.

- **W2a** — 451, small legal-refusal body, header
  `Link: <https://example.com/legal>; rel="blocked-by"`. →
  **WALLED** (STATUS_451). Pin expected.
- **W2b** — 451, same Link header, body carrying a human-check
  phrase. → **WALLED / Generic**. Pin: the P2c composition —
  the status governs the verdict, the vendor cell records the
  body evidence.
- **W2c** — 451, same Link header, full served-article body
  with no wall phrase. → **WALLED**. Pin: status governs over
  served-looking content (the U2 doctrine).
- **W2d** — 200, BIG_ARTICLE, blocked-by Link header present.
  → **OPEN**. Pin: the header alone on a served page is
  metadata, never a wall.
- **W2e** — 451, Link header whose target is a login URL
  (`<https://site.example/login>; rel="blocked-by"`). →
  **WALLED**. Pin: a Link target is not a redirect target; no
  LOGIN_GATED conversion.
- **W2f** — 451, blocked-by Link header PLUS a Retry-After
  header. → **WALLED**. Pin: composes with U2 (451 +
  Retry-After stays WALLED); the Link header changes nothing.

## W3 — login walls asking for a Windows PIN (classifier, NEW signal)

The Windows credential ceremony is the one device sign-in the
auth family does not name: the page's only step is "Enter your
Windows PIN" or a "Sign in with Windows Hello" button — a
device-bound credential the agent does not hold, presented with
none of the family's existing vocabularies (no "passkey", no
"fingerprint", no code boxes). It is an authentication barrier
exactly like its siblings. Two keys, from birth (the family
discipline): (1) a Windows-PIN/Hello demand in RENDERED visible
text — "windows pin" or "windows hello", never the bare word
"windows" (every OS article says "windows"); (2) prompt
machinery — a <button> or <form>, the page's actionable
apparatus. Prose ABOUT Windows sign-in carries the wording
without the ceremony's machinery; configuration carriers
(asset filenames, script identifiers, stylesheet classes) are
not rendered wording.

- **W3a** — 200, page whose only content is a heading "Sign
  in", the text "Enter your Windows PIN to continue.", and a
  `<button>Continue</button>`, at a non-login URL. →
  **LOGIN_GATED**. Predicted gap: no Windows-PIN signal
  exists, so the classifier reads OPEN.
- **W3b** — 200, the same prompt embedded in BIG_ARTICLE. →
  **OPEN**. Pin on the fix: the served-page size gate (the
  siblings' gate, from birth).
- **W3c** — 200, small real paragraph PLUS
  `<script src="/js/windows-hello.js"></script>`
  (asset-filename carrier), no Windows wording in visible
  text. → **OPEN**. Negative carrier. Pin.
- **W3d** — 200, small real paragraph PLUS
  `<style>.windows-pin-prompt{border:0}</style>`
  (stylesheet-class carrier). → **OPEN**. Negative carrier.
  Pin.
- **W3e** — 200, small page whose only content is prose:
  "On Windows, you can set a Windows PIN under Settings >
  Accounts after you sign in with your password." — NO button,
  NO form. → **OPEN**. Guard: wording without prompt
  machinery is a help article, not a sign-in ceremony — the
  machinery key is load-bearing (the T3e/R3e/U3e/V3e species).
- **W3f** — 200, Windows PIN prompt (wording + <form>) at a
  login URL. → **LOGIN_GATED**. Pin: the login heuristic
  already fires; the new rule must agree.
- **W3g** — 200, small real paragraph + a real `<button>Cancel
  </button>` in a comment form + a script block whose string
  reads "enter your windows pin" (script-string carrier). →
  **OPEN**. Negative carrier: the wording must appear in
  RENDERED visible text — script text is stripped from
  visible text (the rubygems/QR lesson). Pin on the fix.
- **W3h** — 200, page whose only content is "Sign in with
  Windows Hello" plus a `<button>Sign in</button>`, at a
  non-login URL. → **LOGIN_GATED**. Predicted gap (same
  family): the Hello wording key is the same missing signal.

## W4 — robots.txt underscore vs hyphen product tokens (audit tool)

RFC 9309's product token is a name, and names match exactly:
"_" and "-" are different characters, so `wall_check`,
`wall-check`, and `wallcheck` are three different products, and
a group addresses only the product it names. The parser stores
tokens verbatim (lowercased, version stripped per W27-V4) and
matches by exact membership; no fuzzy normalization exists,
and none should be added — a matcher that merged separators
would attribute one product's refusal to another product,
which is a worse error than missing a refusal aimed at a
near-namesake the audit does not track. The tracked agents are
GPTBot, ClaudeBot, CCBot, and Google-Extended (the last itself
hyphenated, which is exactly why separator discipline matters).

- **W4a** — `User-agent: wall_check` + `Disallow: /`, nothing
  else. → robots **PASS**. Pin: the underscore token names a
  different, untracked product; no tracked agent is refused.
- **W4b** — `User-agent: GPT-Bot` + `Disallow: /`, nothing
  else. → robots **PASS**. Pin: the hyphenated token is not
  GPTBot, so GPTBot reads open. (The discipline pin — a fuzzy
  matcher would WARN here, wrongly.)
- **W4c** — `User-agent: gpt_bot` + `Disallow: /`, nothing
  else. → robots **PASS**. Pin (same doctrine, underscore
  species).
- **W4d** — `User-agent: GPTBot` + `Disallow: /`, plus a
  separate group `User-agent: GPT_Bot` + `Allow: /`. → robots
  **WARN** (AI_BLOCKED: GPTBot). Pin: the underscore group's
  Allow belongs to a different product and does not reach
  GPTBot — the W15 tie rule composes only within the same
  token.
- **W4e** — `User-agent: Claude-Bot` + `Disallow: /private`,
  plus a wildcard group with `Allow: /`. → robots **PASS**.
  Pin: ClaudeBot (unhyphenated) has no group and the wildcard
  is permissive; the hyphenated restriction binds nobody the
  audit tracks.
- **W4f** — `User-agent: wallcheck/1.0` + `Disallow: /`, plus
  `User-agent: wall_check` + `Disallow: /`. → robots
  **PASS**. Pin: composes with W27-V4 — version stripping must
  not merge the underscore token into the bare one either.

## W5 — llms.txt that is a table of contents with no links (audit tool)

The W13-E6a doctrine: a body that points nowhere — no markdown
link, no URL, no path — is not an index, whatever its length;
E6 pinned the single title line. A table of contents is the
same answer at greater length: headings and section prose
describe the site's structure but give an agent nothing to
follow. Two edge pins guard the doctrine's borders: fragment-
only TOC entries are not links (Wave 14 — a fragment points at
the file itself), and the weak path test (`/[A-Za-z0-9_.-]+`)
is load-bearing for D7b's plain-text index lines, so incidental
slashes inside prose words count as paths BY DOCTRINE — pinned
here, not re-decided.

- **W5a** — 200 llms, `# Site Guide` + three `##` section
  headings + prose paragraphs, no links, URLs, or paths
  anywhere. → **WARN** (LLMS_STUB). Pin expected: E6a
  generalized from title line to TOC.
- **W5b** — the same TOC PLUS one real markdown link. →
  **PASS**. Pin: one usable entry carries the file.
- **W5c** — TOC whose entries are markdown links to fragments
  only (`[Install](#install)`, `[Config](#config)`). →
  **WARN** (LLMS_STUB). Pin: the Wave 14 fragment rule —
  fragment targets are not index entries.
- **W5d** — TOC with prose containing incidental slashes
  ("CI/CD pipelines", "pros/cons") and no links. → **PASS BY
  DOCTRINE**. Pin: the path regex fires on "/CD" — recorded
  as the standing weak-path doctrine (W13-E6a/D7b), not a
  defect candidate; narrowing the path test would break the
  plain-text index lines D7b pins.
- **W5e** — TOC whose headings are plain-text paths
  (`## /docs`, `## /api`). → **PASS**. Pin: the D7b species —
  plain-text path lines are index entries.
- **W5f** — TOC reduced to `# Guide` + `## Soon` only (under
  20 chars of content, no links). → **WARN** (EMPTY_BODY).
  Pin: the length-gate species of the same family.

## W6 — sitemap.xml <loc> entries on a different TLD (audit tool)

The loc test (K6/L6/N6/Q6/U6) asks one question: does the
entry name a crawlable destination? It has never compared the
entry's host to the document's — R6 pinned mixed www/non-www
hosts PASS, V6 pinned IP-literal hosts PASS, and the family's
doctrine is that the audit grades whether the sitemap names
destinations, not whether the destination is a good idea. A
loc on a different TLD names a destination exactly as a
cross-subdomain loc does; cross-domain sitemap indexes are
additionally a documented, legitimate publishing pattern.
The sitemap fixture's own host is https://x.example.

- **W6a** — urlset whose only loc is
  `https://other.example.net/page`. → **PASS**. Pin expected.
- **W6b** — urlset mixing `https://x.example/a` and
  `https://other.example.net/b`. → **PASS**. Pin.
- **W6c** — urlset whose only loc is
  `https://%65xample.net/a` (percent-encoded host on a foreign
  TLD). → **WARN** (SITEMAP_NO_URLS). Pin: U6's host test is
  per-loc and TLD-blind — the bad loc is skipped and no good
  loc remains.
- **W6d** — sitemapindex whose only child loc is
  `https://other.example.net/sitemap.xml`. → **PASS**. Pin:
  a sitemapindex's loc IS its child sitemap; cross-domain
  children are legitimate, and the loc test reads the child
  as a destination.
- **W6e** — urlset whose only loc is
  `https://x.example.evil.net/a` (the sitemap's host carried
  as a subdomain label of a foreign TLD). → **PASS BY
  DOCTRINE**. Pin: the loc test never parses the document
  host, so a look-alike host is simply a destination;
  host-similarity judgment is not the loc test's job —
  recorded as doctrine, not a defect candidate.

## W7 — challenge phrases in Burmese, Sinhala, Amharic, Azerbaijani (classifier)

Same principle as every prior language wave: challenge pages
are not English-only. Verified against the current
_LOCALIZED_HUMAN_CHECK list before writing — grep returned 0
for every string below in classify.py, in all nineteen prior
HANDCLASS files, and in tests/, and the four language names
appear nowhere in src/, validation/, or tests/. Deliberate
distinctions: Azerbaijani "robot olmadığınızı təsdiqləyin"
differs from the Turkish entry "robot olmadığınızı
doğrulayın" in the verb (təsdiqləyin ≠ doğrulayın) — neither
string contains the other; the AZ checkbox "mən robot
deyiləm" shares no string with the TR "robot değilim".
Burmese (Myanmar script), Sinhala, and Amharic (Ethiopic) are
scripts with no entry anywhere in the list. Each language
gets the demand sentence plus the checkbox sentence, as in
the two-string waves.

- **W7a MY** — 403, small page, "သင်သည် စက်ရုပ်မဟုတ်ကြောင်း
  အတည်ပြုပါ" → **CHALLENGED / Generic**. Predicted gap.
- **W7b MY** — 403, small page, "ကျွန်ုပ်သည် စက်ရုပ်မဟုတ်ပါ"
  → **CHALLENGED / Generic**. Predicted gap.
- **W7c SI** — 403, small page, "ඔබ රොබෝවෙක් නොවන බව තහවුරු
  කරන්න" → **CHALLENGED / Generic**. Predicted gap.
- **W7d SI** — 403, small page, "මම රොබෝවෙක් නොවේ"
  → **CHALLENGED / Generic**. Predicted gap.
- **W7e AM** — 403, small page, "ሮቦት እንዳልሆኑ ያረጋግጡ"
  → **CHALLENGED / Generic**. Predicted gap.
- **W7f AM** — 403, small page, "እኔ ሮቦት አይደለሁም"
  → **CHALLENGED / Generic**. Predicted gap.
- **W7g AZ** — 403, small page, "Robot olmadığınızı
  təsdiqləyin" → **CHALLENGED / Generic**. Predicted gap.
- **W7h AZ** — 403, small page, "Mən robot deyiləm"
  → **CHALLENGED / Generic**. Predicted gap.
- **W7i** — 200, MY phrase on BIG_ARTICLE → **OPEN**. Pin:
  the served-page gate.
- **W7j** — 200, small page with only the fragment "စက်ရုပ်"
  ("robot" alone) → **OPEN**. Pin (the J7g/Q7f/R7f/T7f/U7f/
  V7j species): fragments do not fire.
- **W7k** — 200, AZ phrase ONLY inside a <style> block + a
  small real paragraph → **OPEN**. Pin (the Q7g/R7g/T7g/U7g/
  V7k species): style-block suppression — the family's
  negative carrier.

## W8 — challenge in a modal with role="alertdialog" on a plain div (classifier)

The overlay family has three members: class/id-marked
containers (J8), sticky banners (K2), and the native
<dialog open> (L8). The ARIA species is missing: a plain
`<div role="alertdialog">` carries no overlay class or id and
is not a <dialog> tag, yet an alertdialog is by spec a modal
that interrupts the page until it is answered — the content
beneath it is blocked, which is exactly the J8 geometry and
exactly why the overlay rule is not size-gated. The modality
key is the ARIA assertion itself: role="alertdialog", or
aria-modal="true" on a dialog container. role="alert" (V8's
toast) is NOT modal and stays content; a role="dialog"
container with no aria-modal asserts no modality and stays
content — the boundary is deliberate.

- **W8a** — 200, BIG_ARTICLE PLUS
  `<div role="alertdialog"><p>Verify you are human</p></div>`
  (no class, no id). → **CHALLENGED / Generic**. PREDICTED
  GAP: no overlay key matches a bare role attribute, and the
  generic branch is size-gated on served content, so the
  page reads OPEN today.
- **W8b** — 200, BIG_ARTICLE PLUS
  `<div role="dialog" aria-modal="true"><p>Verify you are
  human</p></div>`. → **CHALLENGED / Generic**. Predicted
  gap (same family): aria-modal is the same modality
  assertion in its other spelling.
- **W8c** — 200, BIG_ARTICLE PLUS a role="alertdialog" div
  containing only a cookie-consent text (no challenge
  phrase). → **OPEN**. Pin: the phrase key is load-bearing —
  a modal is furniture without a challenge inside it.
- **W8d** — 200, content-free page, only
  `<div role="alertdialog">Verify you are human</div>`. →
  **CHALLENGED / Generic**. Pin: the generic branch fires on
  a non-served page regardless of the container species.
- **W8e** — 200, BIG_ARTICLE PLUS an alertdialog div whose
  phrase rides only in the container's own data attribute
  (`data-text="Verify you are human"`) with innocuous visible
  text ("Session notice"). → **OPEN**. Pin on the fix: the
  overlay window scan starts after the container tag, so the
  carrier attribute is outside the window (the K8 carrier
  doctrine on the modal species).
- **W8f** — 200, BIG_ARTICLE PLUS `<div role="dialog">`
  WITHOUT aria-modal, carrying the phrase. → **OPEN**. Pin:
  a modeless dialog role asserts no modality — the new key's
  boundary, recorded deliberately so a future widening must
  argue with it, not drift past it.
