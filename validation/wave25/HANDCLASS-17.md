# Wave 25 — Adversarial Battery v17: Hand Classifications

Discipline (as Waves 6, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
21, 22, 23, 24): every shape below was classified BY HAND against
SPEC's verdict definitions BEFORE the classifier was allowed to see
it. All shapes are NEW relative to Wave 6 (S1–S6), Wave 10 (B1–B10),
Wave 11 (C1–C8), Wave 12 (D1–D9), Wave 13 (E1–E10), Wave 14 (F1–F8),
Wave 15 (G1–G10), Wave 16 (H1–H10), Wave 17 (J1–J9), Wave 18
(K1–K8), Wave 19 (L1–L8), Wave 20 (M1–M10), Wave 21 (N1–N8), Wave 22
(P1–P8), Wave 23 (Q1–Q8), and Wave 24 (R1–R8). Deltas stated
explicitly so they are not mistaken for repeats: no prior battery
has put a marker inside a <blockquote> (R1 figcaption and R8 summary
are the nearest presented-text poles). The deliberate-refusal family
stands at 444 (Wave 5), 451 (Wave 10), 418 (Wave 23), 402 (Wave 24)
— T2 here covers 410, the one remaining deliberate-refusal code no
battery has used. The auth-prompt family names code entry (G6),
passkey (H5), magic link (H10), delivery codes (K3), email-Continue
(L3), authenticator (N3), SSO (P3), push approval (R3), and QR (J4)
— T3 here covers the employee-ID sign-in, a credential ceremony
keyed on a workforce identifier rather than an email. N4 (Wave 21)
pinned robots groups with NO rules (consecutive User-agent lines
merge); T4 here covers rules with NO User-agent line at all
(orphan rules before the first group) and groups whose rules are
separated from their User-agent line by blank lines. G9 (Wave 15)
pinned frontmatter carrying a `url:` field (G9b) and a markdown
link in a description field (G9d); T5 here covers a `sitemap:`
field — the pointer an agent would most want to follow — plus the
mirror composition (a bare sitemap URL as the body's only content).
L6 (Wave 19) covered fragment-ONLY locs and bare-query locs; T6
here covers full URLs carrying a fragment suffix. No prior battery
has used a <textarea>'s default text as the phrase carrier (T8);
the placeholder attribute is its attribute-carrier sibling (the
W18-K8 aria-label species). Any mismatch is a defect candidate:
fix generalized with a capture-built fixture, or ledger it as a
genuine honest limitation with the reason. No silent passes, no
per-shape special cases. Per the Waves 17–24 pattern, every new
signal family carries visible-text gating and a served-page size
gate from birth, with a negative fixture per family using an
asset-filename, script-identifier, or stylesheet-class carrier.

Reference — SPEC verdicts: OPEN = the resource was served;
CHALLENGED = an interactive human-verification challenge was
presented; WALLED = a hard block page, no challenge offered;
LOGIN_GATED = content exists behind authentication; RATE_LIMITED =
a throttle; UNREACHABLE = the fetch itself failed. Audit grades:
PASS / WARN / FAIL per check.

## T1 — challenge markers ONLY inside <blockquote> content (classifier)

A <blockquote> is ordinary rendered body text — quoted material a
reader reads, in the same presented family as <figcaption> (R1)
and <summary> (R8). No strip family names blockquote, and none
should: a challenge phrase there is presented text and must behave
exactly like the same phrase in a paragraph.

- **T1a** — 200, content-free page, only a blockquote:
  `<blockquote>Verify you are human</blockquote>`. →
  **CHALLENGED / Generic**. The quote is the page's only text and
  it is presented. Pin expected (no strip exists; the raw and
  visible scans both keep quoted text).
- **T1b** — 200, small real paragraph PLUS a blockquote reading
  "Verify you are human". → **CHALLENGED / Generic**. Presented
  text on a non-served page fires — the J2/N8 metadata rule does
  NOT apply, because a quote is body content, not head metadata.
  Pin expected.
- **T1c** — 200, BIG_ARTICLE PLUS a blockquote phrase. →
  **OPEN**. Pin: the served-page size gate.
- **T1d** — 200, content-free page, only a blockquote with a
  scenic quote ("The city is a poem in stone."), no phrase. →
  **OPEN**. Pin: a quote is content, not a wall.

## T2 — HTTP 410 responses (classifier)

**HAND-CORRECTION (recorded during the battery run, before any
fix was kept):** this family was originally classified WALLED
under a "deliberate refusal" reading. That reading is wrong
against the campaign's own controlling precedent, and the
battery's first run exposed the error through the Wave 6 pin
test_s1c_410_gone. The corrected classification below governs.

410 Gone is a definitive answer about the RESOURCE, not a
decision about the requester: the server states the resource
is permanently removed — for every client, browsers included.
That is the 404 species (Wave 2, W2-002: "a definitive 404 is
an answer, not a challenge — nothing in the fetch is actually
gated; the status is the verdict"; Wave 6, W6-S1c pinned 410
itself → OPEN, "Definitive answer"). The deliberate-refusal
family (444/451/418/402) is the opposite species: codes a
server aims at THIS requester to decline serving content that
exists. A 410 has nothing to wall — there is no content behind
it. The chain's own W8-001 comment groups 410 with 404/403 as
statuses the login heuristic must never pre-empt, the same
grouping. And the generic-marker branch's GENERIC_OK_STATUSES
(401, 403, 429, 503) excludes 410, so a challenge phrase in a
410 body does not fire either (the W6-S1b precedent at 404:
phrase body, still OPEN).

The original (superseded) reading was: 410 Gone is a deliberate
refusal: the server states the resource is permanently removed
and declines to serve it. Not served
content, not an interactive challenge, not an authentication
demand, not an origin failure (the server answered, precisely).
It was originally grouped with the deliberate-refusal family
(444/451/418/402); the correction above supersedes that
grouping.

- **T2a** — 410, small body "This page has been permanently
  removed." → **OPEN, vendor none**. Pin (W6-S1c): a
  definitive answer.
- **T2b** — 410, body "Verify you are human to continue." →
  **OPEN, vendor none**. Pin (W6-S1b species at 410): the
  phrase does not convert a definitive answer into a wall;
  410 is outside GENERIC_OK_STATUSES.
- **T2c** — 410, cf-ray header + "Just a moment" body →
  **CHALLENGED / Cloudflare**. Pin: a fired vendor challenge
  outranks the bare status (the vendor branches sit above the
  status chain).
- **T2d** — 410, empty body → **OPEN, vendor none**. Pin
  (W6-S1c species): nothing served, nothing gated.

## T3 — login walls asking for an employee ID (classifier, NEW signal)

The employee-ID sign-in is the one credential ceremony the auth
family does not name: the page's only content asks for a workforce
identifier (employee ID / employee number / staff ID) — typically
with a password field — instead of an email address. It is an
authentication barrier exactly like its siblings (code entry G6,
passkey H5, magic link H10, delivery code K3, email-Continue L3,
authenticator N3, SSO P3, push approval R3, QR J4): content exists
behind authentication the agent cannot complete. Two keys, from
birth (the family discipline): (1) employee-ID wording in
RENDERED visible text — a workforce-identifier phrase ("employee
id", "employee number", "staff id"), never a bare form field;
(2) credential machinery — a password input or a form element,
the page's actionable authentication apparatus. Prose ABOUT
employee IDs carries no credential machinery; configuration
carriers (asset filenames, script identifiers, stylesheet
classes) are not rendered wording.

- **T3a** — 200, page whose only content is a form: label
  "Employee ID", a text input, a password input, and a "Sign
  in" button, at a non-login URL. → **LOGIN_GATED**. The page's
  only content is an authentication barrier. Predicted gap: no
  employee-ID signal exists, so the classifier reads OPEN.
- **T3b** — 200, the same form embedded in BIG_ARTICLE. →
  **OPEN**. Pin on the fix: the served-page size gate (the
  siblings' gate, from birth).
- **T3c** — 200, small real paragraph PLUS
  `<script src="/js/employee-id.js"></script>` (asset-filename
  carrier), no employee-ID wording in visible text. → **OPEN**.
  Negative carrier: a filename is configuration, not a prompt.
  Pin.
- **T3d** — 200, small real paragraph PLUS
  `<style>.employee-id-field{border:0}</style>`
  (stylesheet-class carrier). → **OPEN**. Negative carrier: a
  stylesheet class is configuration (the venmo QR lesson).
  Pin.
- **T3e** — 200, small page whose only content is prose:
  "Your employee ID is printed on your badge. Use it together
  with your network password at the terminal in the lobby."
  — NO form, NO input. → **OPEN**. Guard: wording without
  credential machinery is prose — the machinery key is
  load-bearing (the R3e/N3f species).
- **T3f** — 200, employee-ID form (wording + password input)
  at a login URL. → **LOGIN_GATED**. Pin: the login heuristic
  already fires; the new rule must agree.
- **T3g** — 200, small real paragraph + a password input in a
  comment form + a script block whose string reads "employee
  id" (script-identifier carrier). → **OPEN**. Negative
  carrier: the wording must appear in RENDERED visible text
  (the rubygems/QR lesson) — script text is stripped from
  visible text, so the phrase is not a prompt. Pin on the fix.

## T4 — robots.txt orphan rules and blank-line-separated groups (audit tool)

RFC 9309 groups are one or more User-agent lines followed by
rules (the N4 principle). A rule line that appears BEFORE any
User-agent line belongs to no group — there is no agent it can
bind — and a blank line is not a group boundary in the grammar:
the group continues until the next User-agent line after rules
(the parser's established composition, R4/N4 species).

- **T4a** — robots.txt containing ONLY orphan rules
  (`Disallow: /` with no User-agent line anywhere). → robots
  **PASS**. No group exists; no tracked agent is bound by a
  rule with no agent. Pin expected: the parser only records
  rules inside a group.
- **T4b** — `User-agent: *` / (blank line) / `Disallow: /`. →
  robots **FAIL**. The blank line does not end the group; the
  wildcard group carries the rule and all four tracked agents
  are blocked. Pin expected.
- **T4c** — orphan `Disallow: /private` BEFORE the first group,
  then `User-agent: *` / `Allow: /`. → robots **PASS**. The
  orphan is ignored; the wildcard group allows everything.
  Pin expected.
- **T4d** — orphan `Disallow: /` first, then `User-agent:
  GPTBot` with NO rules. → robots **PASS**. The orphan binds
  nobody; GPTBot's own group is empty (the N4 empty-group
  composition), so GPTBot is open, and the other three fall
  back to a wildcard group that does not exist — open. Pin
  expected.

## T5 — llms.txt carrying a sitemap link ONLY inside frontmatter (audit tool)

YAML frontmatter is document metadata, stripped before the
content test (W15-009; G9 pinned the `url:` field and the
description-link species). A `sitemap:` field is the strongest
pointer an llms file could carry — and it is still metadata:
stripped with the rest of the frontmatter, it leaves the file
with no index content. The mirror composition matters too: the
same pointer as BODY content is an index entry an agent can
follow (the D7b plain-text species).

- **T5a** — /llms.txt containing ONLY frontmatter with a
  `sitemap: https://example.com/sitemap.xml` field, no body.
  → **WARN** (LLMS_STUB family). The file points nowhere an
  agent can follow once its metadata is set aside. Pin
  expected (G9b species, sitemap-field variant).
- **T5b** — /llms.txt with frontmatter (title only) followed
  by a body whose ONLY content is the bare line
  `Sitemap: https://example.com/sitemap.xml`. → **PASS**. The
  pointer is body content here: a plain-text line carrying a
  URL an agent can follow (D7b species). Pin expected.
- **T5c** — /llms.txt with a frontmatter `sitemap:` field PLUS
  a body carrying a real index (`- [Docs](/docs)`). →
  **PASS**. Pin: the frontmatter strip must not punish a real
  index below it (G9c species).

## T6 — sitemap.xml <loc> entries containing URL fragments (audit tool)

A fragment suffix on a full URL does not unmake the URL: the
fragment is client-side, and the reference still names a
crawlable destination — the mirror of L6, where a fragment
ALONE names nothing. The W18/W19 loc test asks whether an entry
names a destination; "https://example.com/a#section" names one.

- **T6a** — urlset whose locs are full URLs with fragments
  (`https://example.com/a#top`, `https://example.com/b#s2`).
  → **PASS**. Pin expected: both locs name crawlable URLs.
- **T6b** — urlset mixing one fragment-only loc (`#section`)
  with one full URL carrying a fragment
  (`https://example.com/a#top`). → **PASS**. Pin (L6d
  composition): the fragment-only entry names nothing, the
  full one names a destination; one good loc suffices.
- **T6c** — urlset whose only loc is a relative reference
  with a fragment (`/guide#install`). → **PASS**. Pin (K6a +
  L6 composition): relative references resolve against the
  sitemap's URL and name destinations; the fragment rides
  along harmlessly.

## T7 — challenge phrases in Serbian, Macedonian, Latvian, Lithuanian (classifier)

Same principle as every prior language wave: challenge pages
are not English-only. Verified against the current
_LOCALIZED_HUMAN_CHECK list before writing (grep returned 0
for all eight strings): Serbian, Macedonian, Latvian, and
Lithuanian have NO entry. Deliberate distinctions: Serbian is
CYRILLIC ("Потврдите да нисте робот") where Croatian W24-R7c
is Latin ("Potvrdite da niste robot") — different script, and
the checkbox strings differ likewise ("Нисам робот" vs
"nisam robot"). Macedonian "Потврдете дека не сте робот" is
NOT Bulgarian W24-R7a "потвърдете, че не сте робот" (no ъ,
"дека" for ", че"), and its checkbox "не сум робот" is not
Bulgarian "не съм робот" (сум ≠ съм) — neither Macedonian
string contains a Bulgarian one, nor the reverse. Each phrase
is a full "confirm you are not a robot" sentence, plus the
checkbox sentence.

- **T7a SR** — 403, small page, "Потврдите да нисте робот"
  → **CHALLENGED / Generic**. Predicted gap.
- **T7b MK** — 403, small page, "Потврдете дека не сте
  робот" → **CHALLENGED / Generic**. Predicted gap.
- **T7c LV** — 403, small page, "Apstipriniet, ka neesat
  robots" → **CHALLENGED / Generic**. Predicted gap.
- **T7d LT** — 403, small page, "Patvirtinkite, kad nesate
  robotas" → **CHALLENGED / Generic**. Predicted gap.
- **T7e** — 200, LV phrase on BIG_ARTICLE → **OPEN**. Pin:
  the served-page gate.
- **T7f** — 200, small page with only the fragment "robotas"
  → **OPEN**. Pin (J7g/Q7f/R7f species): fragments do not
  fire.
- **T7g** — 200, MK phrase ONLY inside a <style> block + a
  small real paragraph → **OPEN**. Pin (Q7g/R7g species):
  style-block suppression — the family's negative carrier.

## T8 — challenge phrase ONLY as a <textarea>'s default text (classifier)

A <textarea>'s default text is its initial VALUE, rendered in
the field where a reader sees it — presented text, in the
family of <figcaption> (R1), <summary> (R8), and <blockquote>
(T1). No strip family names textarea, and none should: the tag
is stripped, its text remains, exactly like a paragraph. Its
siblings mark the boundaries: the `placeholder` ATTRIBUTE is
tag furniture (removed with the tag — the W18-K8 attribute
species), and a textarea's innocuous default text is ordinary
form content.

- **T8a** — 200, content-free page, only
  `<textarea>Verify you are human</textarea>`. →
  **CHALLENGED / Generic**. The default text is the page's
  only text and it is presented. Pin expected.
- **T8b** — 200, small real paragraph PLUS a textarea whose
  default text reads "Verify you are human". →
  **CHALLENGED / Generic**. Presented text on a non-served
  page fires. Pin expected.
- **T8c** — 200, BIG_ARTICLE PLUS a textarea phrase. →
  **OPEN**. Pin: the served-page size gate.
- **T8d** — 200, small real paragraph PLUS
  `<textarea placeholder="Verify you are human"></textarea>`
  (phrase ONLY in the placeholder attribute, empty default
  text). → **OPEN**. Pin: the attribute is removed with the
  tag; no presented phrase exists.
- **T8e** — 200, content-free page, only a textarea with
  innocuous default text ("Tell us about your project").
  → **OPEN**. Pin: a form field alone is furniture, not a
  wall.
