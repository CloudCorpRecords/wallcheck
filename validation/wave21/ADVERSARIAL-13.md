# Wave 21 — Adversarial Battery v13: Results

37 shapes, hand-classified first in HANDCLASS-13.md, run
against the classifier in `tests/test_adversarial13.py`.
**5 defect families, all fixed test-first and generalized;
corpus clean (44 captures, zero diff vs the Wave 15
baseline); full suite 608/608 green** (571 pre-existing +
37 new).

## Defects fixed

- **W21-N1 — object/embed routing species missed (N1b).**
  No rule read <object> data URLs or <embed> src
  attributes. Fix, in the redirect-target family: both join
  meta refresh, JS location, Refresh header, Location
  header, form actions, and iframe sources, under the same
  markers_count gate and login/challenge token rules.
  Fixtures: N1a/b/c/d/g/h.
- **W21-N2 — traffic-overload throttle cause missed
  (N2a).** The Retry-After throttle rule's cause list did
  not include overload wording. Fix: "high traffic" joins
  _THROTTLE_PHRASES; the rule's shape (cause phrase +
  Retry-After header, wall branches keep precedence) is
  unchanged, and F4e/F4f pins still hold.
- **W21-N3 — authenticator-app passcode prompts missed
  (N3a/e).** New _is_authenticator_prompt sibling:
  authenticator wording in rendered visible text plus a
  TOTP-style code input, with visible-text discipline and
  the served-page size gate from birth. Fixtures: N3a/e
  plus negative carriers N3c/d.
- **W21-N6 — non-HTTP-scheme sitemap locs counted (N6a/c).**
  _has_nonempty_loc counted any non-empty, non-fragment
  loc. Fix: a loc counts only when it names a crawlable
  destination — http/https or a schemeless reference.
  Fixtures: N6a/b/c.
- **W21-N7 — Tamil, Telugu, Marathi, Punjabi challenge
  phrases missing (N7a/b/c/d).** Four full sentences added
  to _LOCALIZED_HUMAN_CHECK, gated like every generic
  marker. Fixtures: N7a/b/c/d plus pins N7e/f.

## Hand-correction (discipline working, not a flipped test)

- **N4a.** The first draft hand-classified a mid-file
  "empty" named group as WARN (GPTBot open). On reflection
  that group cannot exist: RFC 9309 groups are one or more
  user-agent lines followed by rules, so consecutive
  user-agent lines with no rules between them are ONE
  group — GPTBot and * share the Disallow: /, and all four
  agents read blocked → FAIL. The parser's merge behavior
  is correct; only a trailing user-agent line (N4b) is a
  group with no rules. The test asserts FAIL; see
  PROBLEMS.md and the correction note in HANDCLASS-13.md.

## Pins (no defect — the classifier/audit was already right)

- N1c/d/e/f/g/h (object content targets, served-page
  gate, fallback text as body text, bare filenames);
  N2b/c/d (Retry-After alone, F4e, F4d); N3b/c/d/f/g
  (size gate, negative carriers, wording without input,
  login-URL agreement); N4b/c (trailing empty group,
  named Allow-only group); N5a/b/c (Windows-1252
  artifacts, frontmatter-only, BOM composition); N6b (one
  crawlable loc suffices); N7e/f (served-page gate,
  fragments); N8a/b/c (meta description follows the title
  rule: fires when it IS the page, stripped when visible
  text exists).

## Corpus regression

All 44 stored captures replayed through the Wave 21-fixed
classifier (`validation/wave15/corpus_check.py` output vs
Wave 15's `corpus-after.txt`): **diff is empty.** The
object/embed routing, the throttle-cause addition, the
authenticator rule, the loc-scheme check, and the language
additions touch no capture.

## Verification

- Full suite: **608/608 green** (571 pre-existing + 37 new).
- MCP smoke: all three tools pass live (see final
  verification in the wave report).
- Every Wave 21 JSON re-read and parsed; no 0-byte files.
