# Wave 21 — Battery v13: Problems found and fixed

Battery v13: 37 shapes, hand-classified first in HANDCLASS-13.md.
First run: 11 failures, all 11 predicted gaps, zero surprises.
After fixes: 37/37 green. Plus one hand-correction (N4a).

## Defects fixed (all test-first, generalized)

- **W21-N1 — object/embed routing species missed (N1b).**
  No rule read <object> data URLs or <embed> src attributes,
  so a content-free page embedding a login target read OPEN.
  Fix, in the redirect-target family: object data URLs and
  embed sources join meta refresh, JS location, Refresh header,
  Location header, form actions, and iframe sources as a routing
  species, under the same markers_count gate and the same
  login/challenge token rules. N1a (object to a challenge
  target) already read CHALLENGED via the bare captcha token —
  the routing evidence now corroborates it; the verdict is
  unchanged. Content targets stay routing (N1c); served-page
  gate protects articles (N1d/g); object fallback text stays
  body text, not routing (N1e/f).
- **W21-N2 — traffic-overload throttle cause missed (N2a).**
  The Retry-After throttle rule's cause list ("too many
  requests" / rate-limit phrasing) did not include overload
  wording, so a 503 with Retry-After + "unusually high
  traffic, please try again later" read UNREACHABLE. Fix:
  "high traffic" joins _THROTTLE_PHRASES. The rule's shape is
  unchanged (cause phrase + Retry-After header, wall branches
  keep precedence), and F4e's "temporarily unavailable"
  (no cause phrase) still reads UNREACHABLE, F4f's "Access
  denied" still reads WALLED.
- **W21-N3 — authenticator-app passcode prompts missed
  (N3a/e).** No existing auth rule named the authenticator
  step: code-entry needs a code-named input, delivery needs
  digit boxes plus a delivery channel, email-Continue needs an
  email input plus a Continue button. Fix: new
  _is_authenticator_prompt sibling — authenticator wording in
  rendered visible text PLUS a TOTP-style code input
  (name/id containing "totp" or "authenticator") — with the
  visible-text discipline and served-page size gate from
  birth (the Waves 17–20 lesson: script filenames like
  authenticator.js and stylesheet classes like
  .authenticator-prompt are configuration, not prompts —
  N3c/d pins). Wording without an input stays prose (N3f);
  the gate protects served articles (N3b).
- **W21-N6 — non-HTTP-scheme sitemap locs counted as URLs
  (N6a/c).** _has_nonempty_loc counted any non-empty,
  non-fragment <loc> content, so a sitemap whose locs were
  all mailto: or javascript: URLs read PASS. Fix: a loc
  counts only when it names a crawlable destination — http://
  or https://, or a schemeless reference resolving against
  the sitemap's URL. One crawlable loc still suffices (N6b).
- **W21-N7 — Tamil, Telugu, Marathi, Punjabi challenge
  phrases missing (N7a/b/c/d).** Four full "confirm you are
  not a robot" sentences added to _LOCALIZED_HUMAN_CHECK,
  gated like every generic marker. Fragments compose
  nothing (N7f) and served-page mentions stay OPEN (N7e).

## Hand-correction (discipline working, not a flipped test)

- **N4a.** The first draft hand-classified a mid-file
  "empty" named group (User-agent: GPTBot with no rules,
  followed by User-agent: * / Disallow: /) as WARN (GPTBot
  open). On reflection that group cannot exist: RFC 9309
  groups are one or more user-agent lines followed by rules,
  so consecutive user-agent lines with no rules between them
  are ONE group — GPTBot and * share the Disallow: /, and
  all four agents read blocked → FAIL. The parser's merge
  behavior is correct; only a trailing user-agent line (N4b)
  is a group with no rules. The test asserts FAIL; the
  correction is recorded here and in HANDCLASS-13.md so a
  future wave re-challenges it with spec evidence, not by
  re-asserting the shape.

## Pins (no defect — the classifier/audit was already right)

- N1c/d/e/f/g/h (object content targets, served-page gate,
  fallback text as body text, bare filenames); N2b/c/d
  (Retry-After alone, F4e, F4d); N3b/c/d/f/g (size gate,
  negative carriers, wording without input, login-URL
  agreement); N4b/c (trailing empty group, named Allow-only
  group); N5a/b/c (Windows-1252 artifacts, frontmatter-only,
  BOM composition); N6b (one crawlable loc suffices);
  N7e/f (served-page gate, fragments); N8a/b/c (meta
  description follows the title rule: fires when it IS the
  page, stripped when visible text exists).

## Residual edges (ledgered, not fixed)

- None new this wave. The Wave 16 split-script-boundary
  edge remains ledgered as limitation-by-design (Wave 17
  re-test: the rendered page never presents the token).
