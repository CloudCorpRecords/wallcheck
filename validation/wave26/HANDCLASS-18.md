# Wave 26 — Adversarial Battery v18: Hand Classifications

Discipline (as Waves 6, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
21, 22, 23, 24, 25): every shape below was classified BY HAND against
SPEC's verdict definitions BEFORE the classifier was allowed to see
it. All shapes are NEW relative to Wave 6 (S1–S6), Wave 10 (B1–B10),
Wave 11 (C1–C8), Wave 12 (D1–D9), Wave 13 (E1–E10), Wave 14 (F1–F8),
Wave 15 (G1–G10), Wave 16 (H1–H10), Wave 17 (J1–J9), Wave 18
(K1–K8), Wave 19 (L1–L8), Wave 20 (M1–M10), Wave 21 (N1–N8), Wave 22
(P1–P8), Wave 23 (Q1–Q8), Wave 24 (R1–R8), and Wave 25 (T1–T8).
Deltas stated explicitly so they are not mistaken for repeats: no
prior battery has put a marker inside a <label> element (T8's
placeholder ATTRIBUTE on a textarea is the attribute-carrier
sibling; K8's aria-label is an attribute on other elements — the
label ELEMENT's text is a different carrier). The deliberate-refusal
family stands at 444 (Wave 5), 451 (Wave 10), 418 (Wave 23), 402
(Wave 24); P2 (Wave 22) pinned 451 with a legal notice and with a
challenge phrase — U2 here is the one composition P2 did not use:
451 carrying a Retry-After header, with and without throttle
wording. The auth-prompt family names code entry (G6), passkey
(H5), magic link (H10), delivery codes (K3), email-Continue (L3),
authenticator (N3), SSO (P3), push approval (R3), QR (J4), and
employee ID (T3) — U3 here covers the badge-tap sign-in, a physical
credential ceremony keyed on a workplace badge rather than anything
typed. T4 (Wave 25) pinned robots orphan rules and blank lines;
U4 here covers whitespace INSIDE the User-agent value itself.
L5 (Wave 19) pinned CR-only and CRLF-only llms files and the BOM
composition; U5 here mixes LF and CRLF in the SAME file. K6/L6/N6
(Waves 18/19/21) covered empty, fragment-only, relative, query, and
non-HTTP-scheme locs, and Q6 (Wave 23) covered the uppercase scheme;
U6 here covers percent-encoding, split by component (path vs host).
Any mismatch is a defect candidate: fix generalized with a
capture-built fixture, or ledger it as a genuine honest limitation
with the reason — and per Wave 25's lesson, check every mismatch
against the older pins before fixing (a Wave 6 pin vetoed Wave 25's
410 "fix"; a mismatch against an old pin is a hand-classification
question first, a defect second). No silent passes, no per-shape
special cases. Per the Waves 17–25 pattern, every new signal
family carries visible-text gating and a served-page size gate
from birth, with a negative fixture per family using an
asset-filename, script-identifier, or stylesheet-class carrier.

Reference — SPEC verdicts: OPEN = the resource was served;
CHALLENGED = an interactive human-verification challenge was
presented; WALLED = a hard block page, no challenge offered;
LOGIN_GATED = content exists behind authentication; RATE_LIMITED =
a throttle; UNREACHABLE = the fetch itself failed. Audit grades:
PASS / WARN / FAIL per check.

## U1 — challenge markers ONLY inside <label> elements (classifier)

A <label> element's text is rendered text — it is the visible,
clickable name of a form control, read by every reader exactly
like a paragraph. It belongs to the presented family
(<figcaption> R1, <summary> R8, <blockquote> T1, textarea default
text T8), not the metadata family: no strip names it, and none
should — the tag is removed by tag-stripping, its text remains.

- **U1a** — 200, content-free page, only
  `<label for="cb">Verify you are human</label>` plus a checkbox
  input. → **CHALLENGED / Generic**. The label is the page's only
  text and it is presented. Pin expected (the phrase scans read
  visible text; label text survives tag-stripping).
- **U1b** — 200, small real paragraph PLUS a label reading
  "Verify you are human". → **CHALLENGED / Generic**. Presented
  text on a non-served page fires. Pin expected.
- **U1c** — 200, BIG_ARTICLE PLUS a label phrase. → **OPEN**.
  Pin: the served-page size gate.
- **U1d** — 403, small page, only a label phrase. →
  **CHALLENGED / Generic**. Pin: 403 is a GENERIC_OK status and
  the phrase is presented.
- **U1e** — 200, content-free page, only a label reading "Your
  email address" plus an email input. → **OPEN**. Pin: a label
  alone is form furniture copy; without a challenge phrase
  nothing fires.

## U2 — HTTP 451 responses carrying a Retry-After header (classifier)

451's semantics are the verdict (W10-B3c; W22-P2 pins): the server
deliberately refuses for legal reasons — content that exists,
declined for this requester class, with the reason stated. The
throttle rule (W14-F4c/F4d) is deliberately scoped to 403/503 —
the two statuses genuinely ambiguous between wall and throttle —
and requires BOTH the expiry (Retry-After) and a stated throttle
cause. A Retry-After on a 451 is duration metadata about the
refusal (how long the legal block lasts), not a reclassification
of it: the status is the server's most deliberate signal, and
451 is not an ambiguous status. The deliberate-refusal family
(444/451/418/402) has never yielded to a header.

- **U2a** — 451, `Retry-After: 3600`, body a legal notice ("This
  content is unavailable for legal reasons in your region.").
  → **WALLED**, vendor none (STATUS_451). Pin expected.
- **U2b** — 451, `Retry-After: 120`, body mixing the legal
  notice with throttle wording ("…and a rate limit is in effect
  for this resource."). → **WALLED**, vendor none. Pin: the
  temptation shape — the throttle branch's 403/503 scope and the
  451 branch's precedence both hold; throttle wording in a 451
  body is the server explaining the refusal's administration,
  not converting it into a 429 species.
- **U2c** — 451, `Retry-After: 3600`, body "Verify you are human
  to continue." → **WALLED / Generic**. Pin (W22-P2c species):
  the verdict governs (STATUS_451), the vendor cell records the
  body evidence (GENERIC_HUMAN_CHECK names Generic).
- **U2d** — 451, NO Retry-After, legal-notice body. →
  **WALLED**, vendor none. Pin: the U2 control — the header is
  not what makes it a wall.

## U3 — login walls asking the user to tap an ID badge (classifier, NEW signal)

The badge-tap sign-in is the one physical credential ceremony the
auth family does not name: the page's only content instructs the
user to tap (or hold) a workplace ID badge on a reader — no
password, no code, nothing typed. It is an authentication barrier
exactly like its siblings: content exists behind an act of
physical authentication the agent cannot perform. Two keys, from
birth (the family discipline): (1) a badge-tap demand in RENDERED
visible text — a full phrase ("tap your badge", "tap your id
badge", "tap your employee badge", "hold your badge"), never the
bare word "badge" (a badge-help page, a badge product page, and
footer-badge furniture all say "badge"); (2) prompt machinery —
a <button> or <form>, the page's actionable apparatus (retry,
cancel, continue). Prose ABOUT badges carries the wording without
the ceremony's machinery; configuration carriers (asset
filenames, script identifiers, stylesheet classes) are not
rendered wording.

- **U3a** — 200, page whose only content is a heading "Sign in",
  the text "Tap your badge on the reader to sign in.", and a
  `<button>Try again</button>`, at a non-login URL. →
  **LOGIN_GATED**. Predicted gap: no badge signal exists, so the
  classifier reads OPEN.
- **U3b** — 200, the same prompt embedded in BIG_ARTICLE. →
  **OPEN**. Pin on the fix: the served-page size gate (the
  siblings' gate, from birth).
- **U3c** — 200, small real paragraph PLUS
  `<script src="/js/badge-tap.js"></script>` (asset-filename
  carrier), no badge wording in visible text. → **OPEN**.
  Negative carrier: a filename is configuration, not a prompt.
  Pin.
- **U3d** — 200, small real paragraph PLUS
  `<style>.badge-tap-prompt{border:0}</style>` (stylesheet-class
  carrier). → **OPEN**. Negative carrier: a stylesheet class is
  configuration (the venmo QR lesson). Pin.
- **U3e** — 200, small page whose only content is prose:
  "Building access: tap your badge on the reader by the door.
  If the light stays red, see the front desk." — NO button, NO
  form. → **OPEN**. Guard: wording without prompt machinery is
  prose about the building, not a sign-in ceremony — the
  machinery key is load-bearing (the T3e/R3e species).
- **U3f** — 200, badge-tap prompt (wording + button) at a login
  URL. → **LOGIN_GATED**. Pin: the login heuristic already
  fires; the new rule must agree.
- **U3g** — 200, small real paragraph + a real `<button>Cancel
  </button>` in a comment form + a script block whose string
  reads "tap your badge" (script-identifier carrier). →
  **OPEN**. Negative carrier: the wording must appear in
  RENDERED visible text — script text is stripped from visible
  text, so the phrase is not a prompt (the rubygems/QR lesson).
  Pin on the fix.

## U4 — robots.txt User-agent values carrying trailing spaces (audit tool)

RFC 9309's grammar treats field values as tokens; surrounding
whitespace is not part of the token, and the parser strips it
(value.strip() at parse). "GPTBot " IS GPTBot: trailing spaces
cannot exempt an agent from its group, nor bind one that is not
named.

- **U4a** — `User-agent: GPTBot ` (trailing spaces) followed by
  `Disallow: /`, nothing else. → robots **WARN**. Only GPTBot
  of the four tracked agents is blocked (AI_BLOCKED: GPTBot);
  the spaces change nothing. Pin expected.
- **U4b** — four groups, one per tracked agent (GPTBot,
  ClaudeBot, CCBot, Google-Extended), each UA value carrying
  trailing spaces, each with `Disallow: /`. → robots **FAIL**.
  Pin: every tracked agent is blocked; the trailing spaces do
  not exempt any of them.
- **U4c** — `User-agent: * ` (wildcard with trailing space) +
  `Disallow: /`. → robots **FAIL**. Pin: the wildcard binds
  despite the trailing space.
- **U4d** — `User-agent: GPTBot ` (trailing spaces) + `Allow: /`.
  → robots **PASS**. Pin: named, spaced, and allowed.
- **U4e** — `User-agent: *` + `Disallow: / ` (trailing space in
  the Disallow VALUE). → robots **FAIL**. Pin: the value is
  trimmed too — "/ " is "/".

## U5 — llms.txt mixing LF and CRLF line endings in the same file (audit tool)

Line endings are not content (W19-L5): the llms check normalizes
CRLF and CR-only endings to LF before the frontmatter anchor and
every content test, so a file mixing LF and CRLF behaves exactly
like either uniform twin. The frontmatter anchor itself
(`\r?\n` on both delimiters) tolerates the mix independently.

- **U5a** — frontmatter delimited with CRLF, body in LF with a
  real markdown link. → **PASS**. Pin expected.
- **U5b** — frontmatter delimited with LF, body in CRLF with a
  real markdown link. → **PASS**. Pin expected.
- **U5c** — frontmatter ONLY (title + sitemap field), opener
  CRLF, closer LF, no body. → **WARN**. Pin: the mixed-ending
  strip still works; what remains is a stub (the T5a species).
- **U5d** — no frontmatter; a CRLF title line and an LF body
  line, no links, URLs, or paths anywhere. → **WARN**
  (LLMS_STUB). Pin: mixed endings do not manufacture content.

## U6 — sitemap.xml <loc> entries with percent-encoded hosts (audit tool)

The loc test (W18-K6, W19-L6, W21-N6) asks one question: does
the entry name a crawlable destination? Percent-encoding in the
PATH is normal URL practice — `/p%61ge` names a page exactly as
`/page` does. Percent-encoding in the HOST is a different
species: the WHATWG host parser rejects "%" in hosts of special
schemes (http/https), so a loc whose host is percent-encoded
does not parse as a URL at all under standard URL parsing — it
names no destination a standard client can crawl, however
legible the encoding is to a human reader. (Checked against the
older pins before classifying: K6 relative/query locs, L6
fragments, N6 non-HTTP schemes, Q6 uppercase scheme — none
carries a percent-encoded authority, so no pin governs this
shape either way; the classification rests on the loc test's own
question.)

- **U6a** — urlset whose only loc is
  `https://example.com/%70age` (path percent-encoded). →
  **PASS**. Pin expected: path encoding names a destination.
- **U6b** — urlset with locs `https://%65xample.com/a`
  (host percent-encoded) and `https://example.com/b`. →
  **PASS**. Pin: one good loc suffices (the K6/T6 composition),
  whichever way U6c is decided.
- **U6c** — urlset whose ONLY loc is
  `https://%65xample.com/a` (host percent-encoded). →
  **WARN** (SITEMAP_NO_URLS). Predicted gap: the current loc
  test accepts any non-empty http(s) loc, so the encoded host
  counts as a destination it cannot name.
- **U6d** — urlset whose only locs are `https://example%2Ecom/a`
  and `https://%65xample.com/b` (both hosts percent-encoded).
  → **WARN** (SITEMAP_NO_URLS). Predicted gap (same family).

## U7 — challenge phrases in Catalan, Estonian, Armenian, Georgian (classifier)

Same principle as every prior language wave: challenge pages are
not English-only. Verified against the current
_LOCALIZED_HUMAN_CHECK list before writing (grep returned 0 for
all eight strings): Catalan, Estonian, Armenian, and Georgian
have NO entry. Deliberate distinctions: Catalan "no soc un
robot" is not Spanish "no soy un robot" (soc ≠ soy), and its
demand "confirma que no ets un robot" contains no Spanish or
Portuguese entry. Estonian "ma ei ole robot" is not Finnish
"en ole robotti" (ei ≠ en, robot ≠ robotti), and its demand
"kinnitage, et te ei ole robot" contains no Finnish entry.
Armenian and Georgian are unique scripts with no Cyrillic,
Greek, or Latin collisions. Each phrase is a full "confirm you
are not a robot" sentence, plus the checkbox sentence.

- **U7a CA** — 403, small page, "Confirma que no ets un robot"
  → **CHALLENGED / Generic**. Predicted gap.
- **U7b ET** — 403, small page, "Kinnitage, et te ei ole robot"
  → **CHALLENGED / Generic**. Predicted gap.
- **U7c HY** — 403, small page, "Հաստատեք, որ ռոբոտ չեք"
  → **CHALLENGED / Generic**. Predicted gap.
- **U7d KA** — 403, small page, "დაადასტურეთ, რომ რობოტი არ
  ხართ" → **CHALLENGED / Generic**. Predicted gap.
- **U7e** — 200, ET phrase on BIG_ARTICLE → **OPEN**. Pin:
  the served-page gate.
- **U7f** — 200, small page with only the fragment "robot" →
  **OPEN**. Pin (J7g/Q7f/R7f/T7f species): fragments do not
  fire.
- **U7g** — 200, HY phrase ONLY inside a <style> block + a
  small real paragraph → **OPEN**. Pin (Q7g/R7g/T7g species):
  style-block suppression — the family's negative carrier.

## U8 — challenge phrase ONLY as the text of a <button> (classifier)

A button's text is its label — rendered, read, and acted on:
presented text, in the family of <label> text (U1) and textarea
default text (T8). No strip names button text; the tag is
stripped, the label remains. On a served page the size gate
applies as for every presented-text species.

- **U8a** — 200, content-free page, only
  `<button>Verify you are human</button>`. →
  **CHALLENGED / Generic**. The button label is the page's only
  text and it is presented. Pin expected.
- **U8b** — 200, small real paragraph PLUS a button reading
  "Verify you are human". → **CHALLENGED / Generic**. Presented
  text on a non-served page fires. Pin expected.
- **U8c** — 200, BIG_ARTICLE PLUS a button phrase. → **OPEN**.
  Pin: the served-page size gate.
- **U8d** — 403, small real paragraph PLUS a button phrase. →
  **CHALLENGED / Generic**. Pin expected.
- **U8e** — 200, content-free page, only a button reading
  "Continue". → **OPEN**. Pin: a button alone is furniture
  without a phrase.
