# Wave 25 — Adversarial Battery v17 (37 shapes)

Hand-first discipline as in Waves 6, 10–24: HANDCLASS-17.md
was written BEFORE the battery ran. First run (after two
harness corrections of mine — wrong audit check names, then
the grade key — and one fixture correction: the employee-ID
form's `action="/auth"` fired the form-action-to-login rule
and masked the gap it was built to measure): **9 failures,
28 passes — exactly the predicted gaps in 3 families, plus 1
failure that was my own hand-classification error (T8d's
counterpart T2, below).** After the three generalized fixes:
**37/37 green**, corpus regression clean (44 captures, diff
empty vs `validation/wave15/corpus-after.txt`), full suite
**747/747** via pytest (710 at wave start + 37).

| Family | Shapes | First run | After fix |
|--------|--------|-----------|-----------|
| T1 blockquote-only markers | 4 | 4 pins held | — |
| T2 HTTP 410 | 4 | 4 pins held (after hand-correction) | — |
| T3 employee-ID login walls | 7 | **1 defect** (T3a) + 6 pins held | fixed (W25-T3) |
| T4 robots orphan rules / blank lines | 4 | 4 pins held | — |
| T5 llms sitemap link in frontmatter | 3 | 3 pins held | — |
| T6 sitemap locs with fragments | 3 | 3 pins held | — |
| T7 SR/MK/LV/LT phrases | 7 | **4 defects** (T7a–d) | fixed (W25-T7) |
| T8 textarea default text | 5 | **1 defect** (T8d) + 4 pins held | fixed (W25-T8) |

## The three defect families

**W25-T3 — employee-ID sign-in prompts had no signal.** The
auth-prompt family named every credential ceremony except the
workforce one: a page whose only content is an "Employee ID"
label, an identifier input, and a password field read OPEN.
The fix adds `_is_employee_id_prompt` to the auth elif chain
with `EMPLOYEE_ID_PROMPT` evidence, two-keyed from birth:
(1) workforce-identifier wording ("employee id", "employee
number", "staff id", "associate id") in RENDERED visible
text, (2) credential machinery — a password input or a form
element. All six guards held from the first run and remain as
pins: the form inside BIG_ARTICLE stays OPEN (the chain's
served-page gate), asset-filename (employee-id.js) and
stylesheet-class (.employee-id-field) carriers stay OPEN,
prose about employee IDs with no machinery stays OPEN (T3e —
the machinery key is load-bearing), the same form at a login
URL agrees with the heuristic (T3f), and wording carried only
by a script string stays OPEN even beside a password input
(T3g — the visible-text key is load-bearing).

**W25-T7 — Serbian, Macedonian, Latvian, Lithuanian
challenge phrases missing.** `_LOCALIZED_HUMAN_CHECK` covered
39 languages but none of these four. All eight strings were
grep-verified absent before the battery was written, with the
script distinctions that keep them collision-free: Serbian is
Cyrillic where Croatian (W24-R7c) is Latin; Macedonian is not
Bulgarian (W24-R7a) — "дека" for ", че", no ъ, checkbox "сум"
for "съм". The fix adds all eight with per-language comments.
Guards held: LV phrase on BIG_ARTICLE stays OPEN (served-page
gate), the LT fragment "robotas" stays OPEN (the fragment
rule), the MK phrase inside a `<style>` block stays OPEN
(style suppression).

**W25-T8d — a challenge phrase living only in a `placeholder`
attribute drove CHALLENGED on a served page.** The placeholder
is a hint — ghost text inside an empty field — never presented
content, but no strip named it, so the raw and corroboration
scans read the attribute as page text. The fix adds
`_PLACEHOLDER_ATTR_RE` to the survival-variant strips
alongside `_DATA_ATTR_RE` (both `bl_noscript_clean` and
`bl_generic_clean`): a phrase that cannot survive placeholder
stripping cannot corroborate a wall on a page with visible
text, while content-free pages still fire via the raw scan —
the data-attribute doctrine (W16-002/003) extended to the one
attribute species it had not named. The family's other four
shapes were pins: a textarea's DEFAULT text is presented
(fires on non-served pages, gated on served ones), and an
innocuous textarea alone is furniture.

## The hand-correction (T2, HTTP 410 — NOT a defect)

T2 was originally hand-classified WALLED under a
"deliberate refusal" reading. The battery's first run failed
the Wave 6 pin `test_s1c_410_gone` when a 410 branch was
briefly added — the suite doing exactly its job. The reading
was wrong: 410 is a definitive answer about the RESOURCE
(the 404 species — Wave 2 W2-002, Wave 6 W6-S1c pinned 410
itself → OPEN), not a requester-targeted refusal like
444/451/418/402; and 410 sits outside GENERIC_OK_STATUSES,
so a challenge phrase in a 410 body does not fire either
(the W6-S1b precedent at 404). The branch was reverted, the
hand-classification corrected in HANDCLASS-17.md with the
reasoning recorded there, and T2's four shapes now stand as
pins on the corrected classification. No classifier change
ships for T2.

## The pins that mattered

- **T1/T8a/T8b (presented text):** blockquote and textarea
  default text complete the presented-element survey —
  figcaption (R1), summary (R8), blockquote, and textarea
  values all fire on non-served pages and gate on served
  ones; the never-presented family (head, noscript, template,
  picture stray text, SVG metadata, style, data/placeholder
  attributes) is now closed on both poles.
- **T4 (robots orphans):** rules with no User-agent line bind
  nobody, and a blank line is not a group boundary — the
  parser's group grammar composes exactly as RFC 9309 reads.
- **T5 (frontmatter pointer):** a `sitemap:` field inside
  frontmatter is metadata (WARN); the same pointer as body
  content is an index entry (PASS) — the metadata/content
  line holds at the strongest pointer, not just the weakest.
- **T6 (fragment locs):** a fragment suffix does not unmake
  a URL; L6's fragment-only rejection and T6's full-URL
  acceptance are the same rule read from both sides.
