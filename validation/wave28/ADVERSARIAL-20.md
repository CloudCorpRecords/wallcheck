# Adversarial battery v20 — Wave 28 (Leg B)

54 shapes in `tests/test_adversarial20.py`, hand-classified
first in `validation/wave28/HANDCLASS-20.md` (written before any
test ran). Scope per the wave brief: challenge markers appearing
only inside an `<output>` element (W1); the wall as an HTTP 451
carrying a `Link: rel="blocked-by"` header to a policy page
(W2); login walls asking for a Windows PIN (W3); robots.txt
product tokens distinguishing underscore vs hyphen
(`wall_check` vs `wallcheck`) (W4); llms.txt files that are a
table of contents with no links at all (W5); sitemap.xml `<loc>`
entries on a different TLD than the sitemap's own host (W6);
challenge phrases in Burmese, Sinhala, Amharic, and Azerbaijani
— grep-verified absent from the full phrase list, every prior
HANDCLASS file, and tests/ before writing (W7); and the
challenge presented as a modal with role="alertdialog" on a
plain div over otherwise real content (W8).

**First run: 12 failures, 42 passes.** The 12 failures are
exactly the HANDCLASS-20 gap predictions — W3a, W3h, W7a–W7h,
W8a, W8b — and there were no surprises: every shape the
hand-class predicted would pass, passed, including all of W1,
W2, W4, W5, W6 and every negative-carrier guard. After the
three fixes below: **54/54 pass**, and the full suite stands at
**885/885 via pytest** (831 carried in + 54 new), with the
capture corpus regression clean (44 corpus captures, diff
empty against `validation/wave15/corpus-after.txt`).

## The three defect families (all fixed; details in PROBLEMS.md)

- **W28-W3 — Windows PIN / Windows Hello sign-in prompts
  missed.** A served-size login page whose only auth step was
  "Enter your Windows PIN to continue." (or a "Sign in with
  Windows Hello" button) read OPEN: every auth sibling keys on
  its own vocabulary, and the Windows credential ceremony
  matches none of them. Fixed with the two-keyed rule every
  signal family since Wave 17 carries from birth
  (`_is_windows_pin_prompt` + `WINDOWS_PIN_PROMPT` evidence,
  visible-text gated, served-page size gated, button/form
  machinery keyed — prose about Windows sign-in without
  machinery stays OPEN, ledgered in the code comment).
- **W28-W7 — eight localized human-check phrases missed.**
  Burmese, Sinhala, Amharic, and Azerbaijani joins of the
  demand and checkbox patterns read OPEN. Added to
  `_LOCALIZED_HUMAN_CHECK` with the established collision
  discipline (the Azerbaijani demand verb "təsdiqləyin" is a
  distinct string from the Turkish entry's "doğrulayın";
  Burmese, Sinhala, and Amharic are scripts with no entry
  anywhere in the list).
- **W28-W8 — ARIA modal challenges missed.** A challenge
  inside a plain `<div role="alertdialog">` (or a
  role="dialog" container with aria-modal="true") over a full
  served article read OPEN: the overlay family keyed on
  class/id markers (J8), stickiness (K2), and the native
  <dialog> tag (L8) — none of which an ARIA-spelled modal
  carries. Fixed by adding the modality assertion itself as
  the container key (`_MODAL_ROLE_TAG_RE`), with the same
  800-char window, strips, and phrase test as every overlay
  member, and deliberately NOT matching role="alert" (Wave
  27's toast) or a modeless role="dialog" — the boundary is
  pinned, not drifted past.

## What held without a fix

- **W1 (<output> elements).** An `<output>` element's text is
  presented content like a table cell's: a phrase alone inside
  one fires on a non-served page (W1a/W1b/W1d), the size gate
  holds it on served pages (W1c/W1f), and ordinary output text
  fires nothing (W1e). No strip was needed and none was added;
  the battery closes the presented-element survey's last
  common form element.
- **W2 (451 + blocked-by Link header).** The status governs
  in every composition: bare (W2a), with a challenge phrase
  in the body (W2b — the P2c composition, WALLED/Generic),
  over a full served-looking article (W2c), with Retry-After
  (W2f). The header alone on a served 200 is metadata (W2d),
  and a Link target pointing at a login URL converts nothing
  (W2e): a Link header documents a refusal, it is not a
  redirect species, and no branch was added to make it one.
- **W4 (robots separator discipline).** Underscore and hyphen
  tokens name different products and the audit's exact-match
  grading already honors that in both directions: near-name
  refusals do not block tracked agents (W4a–W4c, W4e), a
  near-name Allow does not cancel a real block (W4d), and
  version stripping does not merge separators either (W4f).
  No normalization was added — over-normalizing would
  attribute one product's refusal to another.
- **W5 (TOC-only llms.txt).** The W13-E6a doctrine generalizes
  from title line to table of contents: headings + prose
  pointing nowhere is LLMS_STUB (W5a), one real link carries
  it (W5b), fragment-only entries are not entries (W5c), and
  the tiny file lands on EMPTY_BODY (W5f). Two PASSes are
  pinned BY DOCTRINE, not by oversight: incidental slashes in
  prose ("CI/CD") fire the deliberately weak path test that
  D7b's plain-text index lines depend on (W5d), and plain-
  text path headings are entries (W5e).
- **W6 (cross-TLD sitemap locs).** The loc test has never
  compared hosts, and the family's doctrine — the audit
  grades whether a sitemap names destinations, not whether
  the destination is a good idea — covers the TLD case:
  cross-TLD locs PASS (W6a/W6b), a cross-domain sitemapindex
  child PASSes (W6d), a look-alike host is simply a
  destination (W6e, by doctrine), and the one bad loc in the
  family is bad for a per-loc reason that has nothing to do
  with TLDs (W6c, the U6 percent-encoded host).

## Discipline notes

- Every mismatch was checked against older pins before any
  fix: the W2 verdicts against P2/U2, the W5 PASSes against
  the W13-E6a/D7b doctrine, the W6 PASSes against the R6/V6
  doctrine, and the W8 boundary against V8's toast (role=
  "alert" must not become modal by drift). No older pin moved.
- The three new signals were born with the Wave 17–27
  pattern: two-keyed or container+phrase keyed, visible-text
  gated, size-gated where the family is size-gated (W3) and
  deliberately not where it is not (W8, the overlay rule),
  each with negative fixtures on asset-filename /
  script-string / stylesheet-class carriers (W3c/W3d/W3g,
  W7k) and prose guards (W3e).
- No per-site special cases; every fix is a general rule.
  SPEC.md updated for all three Wave 28 classifier changes
  (status line, localized list, Wave 28 refinements).
