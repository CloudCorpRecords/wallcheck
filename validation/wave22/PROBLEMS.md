# Wave 22 — Battery v14: Problems found and fixed

Battery v14: 30 shapes, hand-classified first in HANDCLASS-14.md.
First run: 8 failures — 7 predicted gaps plus 1 vendor-cell
expectation corrected, zero surprises. After fixes: 30/30 green.

## Defects fixed (all test-first, generalized)

- **W22-P1 — SVG <title>/<desc> metadata drove verdicts on
  served pages (P1c).** _visible_text strips head/script/
  style/noscript/template blocks and then all tags, but no
  strip existed for SVG <title>/<desc> blocks, so a diagram
  title reading "Verify you are human" survived into
  visible text and into every scan variant, and a small real
  paragraph carrying such a diagram read CHALLENGED. Fix,
  in the metadata family: _SVG_META_RE strips
  <title>/</title> and <desc>/</desc> blocks
  (backreferenced) from _visible_text itself and from
  every conditional (has_visible) strip block —
  bl_noscript_clean, bl_generic_noscript,
  bl_generic_nowidget, bl_generic_clean, bl_traffic, and
  b_vendor (in the not-body-wall-signal branch).
  Content-free pages still fire (P1a/d): with no body text
  the metadata IS the page, via the raw-body variant plus
  the not-has_visible survival clause. The served-page
  gate still protects articles (P1b).
- **W22-P3 — "Continue with SSO" prompts read OPEN
  (P3a/f).** No existing auth rule named single sign-on:
  code-entry needs a code-named input, delivery needs
  digit boxes plus a channel, email-Continue needs an
  email input plus a Continue button, authenticator needs
  TOTP wording plus a TOTP input. Fix: new
  _is_sso_prompt sibling — SSO wording ("continue with
  sso" / "sign in with sso" / "log in with sso" /
  "single sign-on") in rendered visible text PLUS an SSO
  button or link — placed after the authenticator branch
  with the same 2xx/3xx status bound and served-page
  size gate, and with visible-text discipline plus
  asset-filename/stylesheet-class negative carriers from
  birth (the Waves 17–21 lesson: sso.js and .sso-button
  are configuration, not prompts — P3c/d pins). Wording
  without machinery stays prose (P3e); the gate
  protects served articles (P3b); a short instruction
  paragraph does not make the prompt served content
  (P3f, N3e principle).
- **W22-P7 — Gujarati, Kannada, Nepali, Khmer challenge
  phrases missing (P7a/b/c/d).** Verified against the
  current _LOCALIZED_HUMAN_CHECK list: none of the four
  had an entry. Fix: four full "confirm you are not a
  robot" sentences added, gated like every generic
  marker. Fragments compose nothing (P7f) and
  served-page mentions stay OPEN (P7e).

## Hand-correction (discipline working, not a flipped test)

- **P2c.** The first draft asserted a 451 body carrying a
  challenge phrase reads ("WALLED", None). The verdict
  holds — the refusal code governs over challenge text
  inside a refusal document — but the vendor cell reads
  "Generic", because body evidence is recorded for every
  verdict and this refusal body carries a generic
  human-check phrase. The vendor cell records evidence;
  it does not re-attribute the refusal to a challenge
  operator. The test asserts ("WALLED", "Generic");
  the correction is recorded here and in HANDCLASS-14.md
  so a future wave re-challenges it with evidence, not
  by re-asserting the shape.

## Pins (no defect — the classifier/audit was already right)

- P1a/b/d (svg metadata IS the page when content-free,
  served-page gate); P2a/b (451 governs for a full legal
  notice and for an empty body); P3b/c/d/e (SSO gate,
  negative carriers, wording without machinery); P4a/b
  (stray robots rules ignored, Crawl-delay does not
  soften blocking); P5a/b/c (BOM + CRLF composition,
  frontmatter-only stub); P6a/b/c (empty sitemap index,
  lastmod-only urlset, nested sitemap index); P7e/f
  (served-page gate, fragments); P8a/b/c (og:description
  follows the meta description rule exactly — the
  block-level head strip covers property= carriers).

## Residual edges (ledgered, not fixed)

- None new this wave. The Wave 16 split-script-boundary
  edge remains ledgered as limitation-by-design (Wave 17
  re-test: the rendered page never presents the token).
