# Wave 24 — Adversarial Battery v16: Hand Classifications

Discipline (as Waves 6, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
21, 22, 23): every shape below was classified BY HAND against SPEC's
verdict definitions BEFORE the classifier was allowed to see it. All
shapes are NEW relative to Wave 6 (S1–S6), Wave 10 (B1–B10), Wave 11
(C1–C8), Wave 12 (D1–D9), Wave 13 (E1–E10), Wave 14 (F1–F8), Wave 15
(G1–G10), Wave 16 (H1–H10), Wave 17 (J1–J9), Wave 18 (K1–K8),
Wave 19 (L1–L8), Wave 20 (M1–M10), Wave 21 (N1–N8), Wave 22
(P1–P8), and Wave 23 (Q1–Q8). Deltas stated explicitly so they are
not mistaken for repeats: Wave 23's Q1 covered stray TEXT NODES
inside <picture> (never rendered — the element renders only its
<img>); R1 here covers <figcaption>, which is the opposite pole —
rendered caption text. Wave 22's P2 / Wave 10's B3c covered 451 and
Wave 23's Q2 covered 418 (R2 here covers 402, the one remaining
deliberate-refusal code no battery has used). Wave 16's H5 covered
passkey prompts and Wave 21's N3 authenticator prompts (R3 here
covers push-approval prompts — a sign-in approved on ANOTHER
device, with no code, key, or form field of its own). Wave 11's C8e
pinned a lowercase agent VALUE (R4 here covers mixed-case group
names, a mixed-case directive NAME, and an untracked WALLCHECK
group). Wave 13's E6a covered a title-only llms file (R5 here
covers DUPLICATE H1 headings — one title said twice). Wave 18's
K6 covered relative/empty locs (R6 here covers locs split across
www and non-www HOSTS). Wave 20's M9a pinned <details> content on a
big article via the size gate (R8 here covers the <summary>
element — the always-rendered heading of a details, on small
pages). Any mismatch is a defect candidate: fix generalized with
a capture-built fixture, or ledger it as a genuine honest
limitation with the reason. No silent passes, no per-shape
special cases. Per the Waves 17–23 pattern, every new signal
family carries visible-text gating and a served-page size gate
from birth, with a negative fixture per family using an
asset-filename, script-identifier, or stylesheet-class carrier.

Reference — SPEC verdicts: OPEN = the resource was served;
CHALLENGED = an interactive human-verification challenge was
presented; WALLED = a hard block page, no challenge offered;
LOGIN_GATED = content exists behind authentication; RATE_LIMITED =
a throttle; UNREACHABLE = the fetch itself failed. Audit grades:
PASS / WARN / FAIL per check.

## R1 — challenge markers ONLY inside <figcaption> content (classifier)

A <figcaption> is the caption of a <figure>: ordinary rendered
body text, read by every reader — the opposite rendering model
from <picture> stray text nodes (W23-Q1, never rendered) and
<template> contents (W19-L1, inert). No strip family names
figcaption, and none should: a caption is content, so a challenge
phrase there is presented text and must behave exactly like the
same phrase in a paragraph.

- **R1a** — 200, content-free page, only a figure:
  `<figure><img src="/img/x.png"><figcaption>Verify you are
  human</figcaption></figure>`. → **CHALLENGED / Generic**. The
  caption is the page's only text and it is presented. Pin
  expected (no strip exists; the raw and visible scans both
  keep caption text).
- **R1b** — 200, small real paragraph PLUS a figure whose
  figcaption reads "Verify you are human". → **CHALLENGED /
  Generic**. Presented text on a non-served page fires — the
  J2/N8 metadata rule does NOT apply, because a caption is body
  content, not head metadata. Pin expected.
- **R1c** — 200, BIG_ARTICLE PLUS a figcaption phrase. →
  **OPEN**. Pin: the served-page gate.
- **R1d** — 200, content-free page, only a figure with a scenic
  caption ("The bay at dawn, from Pier 9."), no phrase. →
  **OPEN**. Pin: a figure with a caption is content, not a
  wall.

## R2 — HTTP 402 responses (classifier)

402 Payment Required is a deliberate refusal to serve without
payment: not served content, not an interactive challenge, not
an authentication demand (no credentials are entered), and not
an origin failure. It belongs to the deliberate-refusal family
with 444 (Wave 5), 451 (Wave 10), and 418 (Wave 23) — the codes
a server chooses specifically to decline a request. No battery
has used 402 before.

- **R2a** — 402, small body "Payment required. Subscribe to
  access this content." → **WALLED, vendor none**. Predicted
  gap: no 402 branch exists, so the final else (WALLED only
  for 401/403) reads OPEN — the W23-Q2 fallthrough species,
  one code over.
- **R2b** — 402, body "Verify you are human to continue." →
  **WALLED, vendor Generic**. The Q2b/P2c composition: the
  refusal code governs the verdict; body evidence still names
  the vendor. Predicted gap (same fallthrough).
- **R2c** — 402, cf-ray header + "Just a moment" body →
  **CHALLENGED / Cloudflare**. Pin (Q2c species): a fired
  vendor challenge outranks the bare status.
- **R2d** — 402, empty body → **WALLED, vendor none**.
  Predicted gap (same fallthrough as R2a).

## R3 — login walls with an "approve this sign-in on your device" push prompt (classifier, NEW signal)

Push approval is the next auth species after code entry (G6),
passkey (H5), magic link (H10), delivery codes (K3),
email-Continue (L3), authenticator (N3), SSO (P3), and QR (J4):
the page's only content asks the user to approve the sign-in on
another device — an authentication ceremony the agent cannot
complete, with no code to enter, no key to present, and no form
field of its own. Two keys, from birth (the family discipline):
(1) approval wording in RENDERED visible text — a full
sign-in-approval phrase ("approve this sign-in", "approve the
sign-in request", …), never the bare word "approve"; (2) a
prompt marker — a <button> or <form> element, the page's
actionable machinery (resend/cancel/continue). Prose ABOUT
push approval carries no prompt machinery; configuration
carriers (asset filenames, script identifiers, stylesheet
classes) are not rendered wording.

- **R3a** — 200, page whose only content is "Approve this
  sign-in on your device to continue." + a <button>Resend
  notification</button>, at a non-login URL. → **LOGIN_GATED**.
  The page's only content is an authentication barrier.
  Predicted gap: no push-approval signal exists, so the
  classifier reads OPEN.
- **R3b** — 200, the same prompt (wording + button) embedded
  in BIG_ARTICLE. → **OPEN**. Pin on the fix: the served-page
  size gate (the siblings' gate, from birth).
- **R3c** — 200, small real paragraph PLUS
  `<script src="/js/push-approve.js"></script>` (asset-filename
  carrier), no approval wording in visible text. → **OPEN**.
  Negative carrier: a filename is configuration, not a prompt.
  Pin.
- **R3d** — 200, small real paragraph PLUS
  `<style>.push-approval-prompt{border:0}</style>`
  (stylesheet-class carrier). → **OPEN**. Negative carrier: a
  stylesheet class is configuration (the venmo QR lesson).
  Pin.
- **R3e** — 200, small page whose only content is prose:
  "To sign in, approve this sign-in on your device when
  prompted. This page explains how the process works." — NO
  button, NO form. → **OPEN**. Guard: wording without prompt
  machinery is prose — the marker key is load-bearing, like
  the authenticator rule's input key (N3f species). (A real
  push waiting page that carries neither a button nor a form
  is the family's accepted narrow boundary, ledgered with
  the fix if it lands.)
- **R3f** — 200, push prompt (wording + button) at a login
  URL. → **LOGIN_GATED**. Pin: the login heuristic already
  fires; the new rule must agree.
- **R3g** — 200, small real paragraph + a nav <button>Menu
  </button> + a script block whose string reads "approve
  this sign-in" (script-identifier carrier). → **OPEN**.
  Negative carrier: the wording must appear in RENDERED
  visible text (the rubygems/QR lesson) — script text is
  stripped from visible text, so the phrase is not a prompt.
  Pin on the fix.

## R4 — robots.txt mixed-case group names (audit tool)

RFC 9309 names and tokens are case-insensitive: the field name
("User-Agent"), the agent value, and the group a rule lands in
must all match case-insensitively. parse_robots lowercases the
field and the agent value, and _agent_state compares lowered —
so these are pins validating that the case handling composes,
plus the brief's named shape: a group spelled for WALLCHECK,
which is not one of the four tracked agents (GPTBot, ClaudeBot,
CCBot, Google-Extended) the robots check grades.

- **R4a** — robots.txt with only `User-Agent: WALLCHECK` /
  `Disallow: /`. → robots **PASS**. The group names an
  untracked agent; no wildcard group exists, so every tracked
  agent is open. The check grades tracked AI agents, not
  itself. Pin.
- **R4b** — robots.txt with only `User-Agent: GPTBOT` /
  `Disallow: /`. → robots **WARN** (GPTBot blocked by its own
  group; the other three open). The C8e species mirrored to
  uppercase: agent VALUE matching is case-insensitive. Pin.
- **R4c** — robots.txt with only `USER-AGENT: *` /
  `Disallow: /` (directive NAME in caps). → robots **FAIL**
  (the wildcard group registers; all four tracked agents
  blocked). Pin: field-name matching is case-insensitive.
- **R4d** — robots.txt `User-Agent: Wallcheck` / `Disallow: /`
  followed by `User-agent: *` / `Allow: /`. → robots **PASS**.
  Pin (R4a + Q3d composition): the untracked WALLCHECK block
  does not leak onto tracked agents, and the wildcard allows
  the rest.

## R5 — llms.txt files with duplicate H1 headings (audit tool)

The llms grade is a content test — does the file point
somewhere an agent can follow (E6a, W15-009) — not a style
test. A heading repeated is still a heading: twice a title is
not an index, and a duplicate heading over a real index does
not unmake it.

- **R5a** — /llms.txt body `# Site Guide\n# Site Guide\n-
  [Docs](/docs)`. → **PASS**. The file carries a real index
  entry; the duplicated heading is a cosmetic flaw the grade
  does not police. Pin.
- **R5b** — /llms.txt body `# Site Guide\n# Site Guide` only
  (no links, no URLs, no paths). → **WARN** (LLMS_STUB
  family). Two title lines point nowhere — the E6a species
  said twice. Pin.
- **R5c** — /llms.txt body `# Guide\n# Guide\n\nFull docs at
  /docs and the API map at /api.` → **PASS**. Pin (D7b
  species): plain-text index lines carrying paths are
  content, duplicate heading or not.

## R6 — sitemap.xml files mixing www and non-www <loc> hosts (audit tool)

The sitemap check grades the document kind and whether it
names crawlable URLs (W15-010, W18-K6, W19-L6, W21-N6); it
has never graded host consistency, and a www/non-www mix is
an owner SEO wart, not an agent-access failure — every loc
still resolves against the web, and cross-host sitemaps are
legal when declared.

- **R6a** — urlset with `<loc>https://example.com/a</loc>`
  and `<loc>https://www.example.com/b</loc>`. → **PASS**.
  Pin: both locs name crawlable URLs.
- **R6b** — sitemapindex whose children mix
  `https://example.com/s1.xml` and
  `https://www.example.com/s2.xml`. → **PASS**. Pin (R6a
  species in index form).
- **R6c** — urlset whose locs are ALL on www.example.com
  while the sitemap itself is served from example.com. →
  **PASS**. Pin: the check does not require locs to share
  the sitemap's own host.

## R7 — challenge phrases in Bulgarian, Slovak, Croatian, Slovenian (classifier)

Same principle as every prior language wave: challenge pages
are not English-only. Verified against the current
_LOCALIZED_HUMAN_CHECK list before writing (grep returned 0
for all eight strings): Bulgarian, Slovak, Croatian, and
Slovenian have NO entry. Deliberate distinction: Slovak
"Potvrďte, že nie ste robot" is NOT Czech W23-Q7b "Potvrďte,
že nejste robot" — "nie ste" ≠ "nejste", neither string
contains the other, so the Slovak fixture cannot pass through
the Czech entry. Each phrase is a full "confirm you are not
a robot" sentence, plus the checkbox sentence.

- **R7a BG** — 403, small page, "Потвърдете, че не сте
  робот" → **CHALLENGED / Generic**. Predicted gap.
- **R7b SK** — 403, small page, "Potvrďte, že nie ste robot"
  → **CHALLENGED / Generic**. Predicted gap.
- **R7c HR** — 403, small page, "Potvrdite da niste robot"
  → **CHALLENGED / Generic**. Predicted gap.
- **R7d SL** — 403, small page, "Potrdite, da niste robot"
  → **CHALLENGED / Generic**. Predicted gap.
- **R7e** — 200, BG phrase on BIG_ARTICLE → **OPEN**. Pin:
  the served-page gate.
- **R7f** — 200, small page with only the fragment "робот"
  → **OPEN**. Pin (J7g/Q7f species): fragments do not fire.
- **R7g** — 200, BG phrase ONLY inside a <style> block +
  a small real paragraph → **OPEN**. Pin (Q7g species):
  style-block suppression — the family's negative carrier.

## R8 — challenge phrase ONLY inside a <summary> element (classifier)

<summary> is the always-rendered heading of a <details>
element: presented text by construction, whether the details
is open or closed — unlike the details' remaining content,
which hides until opened (M9a pinned that content on a big
article via the size gate, not via any strip). No strip
family names summary, and none should: a summary is content.

- **R8a** — 200, content-free page, only
  `<details open><summary>Verify you are human</summary>
  </details>`. → **CHALLENGED / Generic**. The summary is
  the page's only text and it is presented. Pin expected.
- **R8b** — 200, small real paragraph PLUS
  `<details><summary>Verify you are human</summary>
  <p>Extra text.</p></details>` (details CLOSED). →
  **CHALLENGED / Generic**. The summary renders whether
  the details is open or closed — presented text on a
  non-served page fires. Pin expected.
- **R8c** — 200, BIG_ARTICLE PLUS a summary phrase. →
  **OPEN**. Pin (M9a species): the served-page gate.
- **R8d** — 200, content-free page, only
  `<details><summary>Site navigation</summary></details>`,
  no phrase. → **OPEN**. Pin: a summary alone is content
  furniture, not a wall.
