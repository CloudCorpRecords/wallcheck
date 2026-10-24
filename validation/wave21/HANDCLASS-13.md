# Wave 21 — Battery v13: Hand classifications (written BEFORE running any shape)

Shapes are hand-classified here first; the test file then checks
the classifier against these verdicts. A mismatch is either a
classifier defect (fix test-first, generalized) or a hand
correction (justified in PROBLEMS.md, never a silent flip).

Conventions: ARTICLE/BIG_ARTICLE as in test_adversarial12.py
(BIG_ARTICLE > 16 KB, so the served-page gate applies).
"Small page" = a stub page, no real content. Every new signal
family in this battery carries visible-text gating and a
served-page size gate from birth (the Waves 17–20 lesson: each
new signal family misfired on live traffic through asset
filenames, script identifiers, or stylesheet classes), with a
negative fixture per family using an asset-filename, script-
identifier, or stylesheet-class carrier.

## N1 — object/embed routing species (classifier, W20-001 extension)

An <object> data URL and an <embed> src are embedded routing
directives exactly like an <iframe> src (Wave 20, W20-M1): a
page whose only content is an object/embed routing to a
challenge/login target routes the client there. Content
targets are routing; the served-page gate (markers_count)
protects real pages embedding objects. Object fallback text
is body text (visible-text extraction keeps it: _visible_text
strips no object blocks), so fallback phrases behave like any
body phrase — pins, not defects.

- N1a: content-free page, single <object
  data="https://challenge.example/captcha/verify"></object>
  → CHALLENGED (the object IS the page; it routes to a
  challenge). Predicted gap: no rule reads object data.
- N1b: content-free page, single <embed
  src="/login"> → LOGIN_GATED (the embed routes to a login).
  Predicted gap: no rule reads embed src.
- N1c: small page, <object data="https://content.example/
  article"></object> → OPEN (a content target is routing).
- N1d: BIG_ARTICLE embedding an <object> with a captcha
  data URL → OPEN (served-page gate: furniture).
- N1e: content-free page, <object> fallback text "Verify
  you are human" → CHALLENGED (fallback text is presented
  body text). Pin: _visible_text keeps it.
- N1f: BIG_ARTICLE with an <object> whose fallback text is
  "Verify you are human" → OPEN (served-page gate). Pin.
- N1g: BIG_ARTICLE embedding an <embed src="/login">
  → OPEN (served-page gate). Pin.
- N1h: content-free page, <object data="player.swf">
  (a bare filename, no challenge/login token) → OPEN
  (routing to content, not a gate). Pin.

## N2 — 503 throttle / traffic wording (classifier, F4 extension)

Wave 14, F4: a timed, explicitly retryable refusal on a
non-429 status is a throttle when the server states BOTH a
cause and a retry; either alone does not convert it (F4e:
503 + Retry-After + "Service temporarily unavailable" stays
UNREACHABLE; F4f: 403 + Retry-After + "Access denied" stays
WALLED). The open question is what counts as a throttle
cause: "too many requests" (F4c/d) is one; overload wording
paired with a retry instruction is the same semantics in
other words.

- N2a: 503, header `Retry-After: 60`, body "We are
  experiencing unusually high traffic. Please try again
  later." → RATE_LIMITED (cause + retry instruction +
  Retry-After header: throttle semantics, not origin
  failure). Predicted gap: the throttle-cause wording list
  may not include traffic-overload phrasing, so the 5xx
  branch may answer UNREACHABLE.
- N2b: 503, header `Retry-After: 60`, empty body
  → UNREACHABLE (a header alone converts nothing — F4e
  principle with no wording at all). Pin.
- N2c: 503, header `Retry-After: 60`, body "Service
  temporarily unavailable." → UNREACHABLE (F4e exactly).
  Pin.
- N2d: 503, header `Retry-After: 60`, body "Too many
  requests, please retry in 60 seconds."
  → RATE_LIMITED (F4d exactly). Pin.

## N3 — authenticator-app passcode prompts (classifier, new signal)

A sign-in step asking for the code from an authenticator
app is an authentication barrier in the code-entry family
(Waves 15/18/19), but no existing rule names it: code-entry
needs a code-named input (otp/2fa/auth-code/...), delivery
needs digit boxes plus a delivery channel (texted/emailed),
email-Continue needs an email input plus a Continue button.
An authenticator prompt uses a TOTP field (name="totp") and
authenticator wording — neither existing key fires. Two
keys, from birth: authenticator wording in rendered visible
text PLUS a TOTP-style code input. The visible-text
discipline and served-page size gate apply from birth
(the Waves 17–20 lesson).

- N3a: small page, "Enter the code from your
  authenticator app." + <input name="totp"> → LOGIN_GATED.
  Predicted gap: no authenticator rule exists.
- N3b: the same wording + totp input on BIG_ARTICLE
  → OPEN (served-page size gate). Pin.
- N3c: served article page whose only "authenticator"
  signal is a script filename (authenticator.js)
  → OPEN (an asset filename is configuration, not a
  prompt). Negative carrier fixture.
- N3d: served article page whose only "authenticator"
  signal is a stylesheet class (.authenticator-prompt)
  → OPEN (a stylesheet class is configuration). Negative
  carrier fixture.
- N3e: authenticator wording + totp input on a small page
  that ALSO carries a short real paragraph (visible text
  below the served-page minimum but real content)
  → LOGIN_GATED (the page's only content is the prompt;
  a paragraph of instructions does not make it served
  content). Pin on the size gate's lower edge.
- N3f: small page, authenticator wording but NO input
  at all → OPEN (wording without barrier machinery is
  prose). Pin.
- N3g: authenticator wording + totp input on a page at a
  login URL → LOGIN_GATED (login heuristic agrees).
  Pin.

## N4 — robots.txt empty named groups (audit tool)

RFC 9309: a group with no rules allows everything for its
agents. The parser (audit.py parse_robots) appends a group
when a new User-agent line starts ONLY if it already has
rules — so a mid-file empty group is dropped and its agents
fall back to the wildcard group — but appends the final
group unconditionally, so a trailing empty group survives.
That asymmetry is the gap: identical groups grade
differently by position.

- N4a: robots.txt `User-agent: GPTBot` (no rules),
  then `User-agent: *` / `Disallow: /` → WARN (GPTBot
  open by its own empty group; the other three blocked).
  Predicted gap: the mid-file empty group is dropped, so
  GPTBot falls back to the wildcard and all four read
  blocked → FAIL.
  CORRECTION (before any fix landed): the hand
  classification was wrong, not the parser. RFC 9309
  groups are one or more user-agent lines followed by
  rules, so consecutive user-agent lines with no rules
  between them are ONE group — GPTBot and * share the
  Disallow: /, and all four agents read blocked → FAIL.
  A mid-file "empty group" cannot exist; only a trailing
  user-agent line (N4b) is a group with no rules. The
  test asserts FAIL; see PROBLEMS.md.
- N4b: robots.txt `User-agent: *` / `Disallow: /`,
  then `User-agent: GPTBot` (no rules, trailing)
  → WARN (GPTBot open; the trailing empty group
  survives). Pin documenting the asymmetry N4a fixes.
- N4c: robots.txt `User-agent: GPTBot` / `Allow: /`,
  then `User-agent: *` / `Disallow: /` → WARN (GPTBot
  open by its own group; G8c principle). Pin.

## N5 — llms.txt Windows-1252 artifacts (audit tool)

The audit decodes bodies as UTF-8 with errors="replace"
(audit.py _decode_body): Windows-1252 bytes become
replacement characters, but markdown links and URLs are
ASCII and survive. Content, not encoding, decides (the
Wave 16 H7c principle, extended from charset parameters
to legacy-encoding artifacts). Curly quotes here stand in
for Windows-1252 smart quotes (U+201C/U+201D as decoded
by a UTF-8 reader's replacement path is approximated by
the literal curly characters in these fixtures).

- N5a: real markdown index whose link text carries curly
  quotes (“Docs”) → PASS (encoding artifacts do not
  break link detection). Pin.
- N5b: frontmatter-only file (title + a `url:` field
  wrapped in curly quotes, no index content)
  → WARN (LLMS_STUB family: the metadata URL is not an
  index entry, curly quotes or not — G9b principle).
  Pin.
- N5c: UTF-8 BOM + curly quotes + real markdown index
  → PASS (BOM strip, artifact tolerance, and link
  detection compose). Pin.

## N6 — sitemap.xml non-HTTP-scheme locs (audit tool)

_has_nonempty_loc counts any non-empty, non-fragment
<loc> content — including mailto: and javascript: URLs,
which name no crawlable destination. A sitemap naming
only such locs is a table of contents with no contents
(the Wave 15 W15-010 principle, extended from empty
locs to uncrawlable-scheme locs).

- N6a: urlset whose locs are all mailto: addresses
  → WARN (SITEMAP_NO_URLS family). Predicted gap: the
  counter does not check scheme, so the file reads PASS.
- N6b: urlset with one https loc plus mailto: locs
  → PASS (one crawlable URL suffices). Pin.
- N6c: urlset whose locs are all javascript: URLs
  → WARN (same family as N6a, second scheme).
  Predicted gap, same fix.

## N7 — challenge phrases in Tamil, Telugu, Marathi, Punjabi (classifier)

Same principle as M3 (Wave 20) and L7 (Wave 19): challenge
pages are not English-only, and the list still misses
whole language families. Each phrase is a full "confirm
you are not a robot" sentence, not a fragment.

- N7a TA: small page "நீங்கள் ரோபோ இல்லை என்பதை
  உறுதிப்படுத்தவும்" → CHALLENGED. Predicted gap.
- N7b TE: small page "మీరు రోబో కాదని నిర్ధారించండి"
  → CHALLENGED. Predicted gap.
- N7c MR: small page "तुम्ही रोबोट नाही याची पुष्टी करा"
  → CHALLENGED. Predicted gap.
- N7d PA: small page "ਤੁਸੀਂ ਰੋਬੋਟ ਨਹੀਂ ਹੋ ਇਸ ਦੀ ਪੁਸ਼ਟੀ ਕਰੋ"
  → CHALLENGED. Predicted gap.
- N7e TA phrase on BIG_ARTICLE → OPEN (served-page
  gate). Pin.
- N7f small page with only a fragment ("ரோபோ" alone,
  no listed phrase) → OPEN (fragments do not fire;
  the J7g guessing boundary). Pin.

## N8 — challenge phrases only in meta descriptions (classifier)

A meta description is <head> metadata like <title>
(Wave 13 E3, Wave 17 J2): on a page with visible text the
head strip removes it from scans (J2); on a content-free
page the head is not stripped and the phrase fires (E3).
Meta descriptions follow the title rule exactly — pins,
not defects, validating that the head-strip family covers
all head metadata carriers.

- N8a: content-free page, <meta name="description"
  content="Verify you are human"> and no other text
  → CHALLENGED (head metadata IS the page when there is
  no body content — E3 principle). Pin.
- N8b: BIG_ARTICLE with a meta description "Verify you
  are human" → OPEN (head stripped when visible text
  exists — J2 principle). Pin.
- N8c: small real content page (a short real paragraph
  plus the meta description phrase) → OPEN (visible
  text exists, so the head strip applies). Pin.
