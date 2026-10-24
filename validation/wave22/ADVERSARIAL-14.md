# Wave 22 — Adversarial Battery v14: Results

30 shapes, hand-classified first in HANDCLASS-14.md, run
against the classifier in `tests/test_adversarial14.py`.
**3 defect families, all fixed test-first and generalized;
corpus clean (44 captures, zero diff vs the Wave 15
baseline); full suite 638/638 green** (608 pre-existing +
30 new).

## Defects fixed

- **W22-P1 — SVG <title>/<desc> metadata drove verdicts on
  served pages (P1c).** _visible_text strips head/script/
  style/noscript/template blocks and then all tags — but
  not SVG <title>/<desc> blocks, so their text survived
  into visible text and into every scan variant. Fix, in
  the metadata family: a new _SVG_META_RE strips
  <title>/</title> and <desc>/</desc> blocks (backreferenced,
  so the two tags stay distinct) from _visible_text itself
  and from every conditional (has_visible) strip block —
  bl_noscript_clean, bl_generic_noscript, bl_generic_nowidget,
  bl_generic_clean, bl_traffic, and b_vendor (in the
  not-body-wall-signal branch). Content-free pages still
  fire: with no body text the metadata IS the page (P1a/d
  pins hold via the raw-body variant plus the
  not-has_visible survival clause).
- **W22-P3 — "Continue with SSO" prompts read OPEN (P3a/f).**
  No existing auth rule named single sign-on. Fix: a new
  _is_sso_prompt sibling — SSO wording in rendered visible
  text PLUS an SSO button or link — placed after the
  authenticator branch with the same 2xx/3xx status bound
  and served-page size gate, and with visible-text
  discipline plus asset-filename/stylesheet-class negative
  carriers from birth (P3c/d pins).
- **W22-P7 — Gujarati, Kannada, Nepali, Khmer challenge
  phrases missing (P7a/b/c/d).** Four full "confirm you are
  not a robot" sentences added to _LOCALIZED_HUMAN_CHECK,
  gated like every generic marker. Fragments compose
  nothing (P7f) and served-page mentions stay OPEN (P7e).

## Hand-correction (discipline working, not a flipped test)

- **P2c.** The first draft asserted a 451 body carrying a
  challenge phrase reads ("WALLED", None). The verdict is
  WALLED — the refusal code governs — but the vendor cell
  reads "Generic": the refusal body also carries a generic
  human-check phrase, and body evidence is recorded for
  every verdict. The vendor cell records evidence, it does
  not re-attribute the refusal. The test asserts
  ("WALLED", "Generic"); see PROBLEMS.md.

## Pins (no defect — the classifier/audit was already right)

- P1a/b/d (svg metadata IS the page when content-free,
  served-page gate); P2a/b (451 governs for a full legal
  notice and for an empty body — B3c extended, not
  softened); P3b/c/d/e (SSO gate, negative carriers,
  wording without machinery); P4a/b (stray robots rules
  ignored, Crawl-delay does not soften blocking); P5a/b/c
  (BOM + CRLF composition, frontmatter-only stub);
  P6a/b/c (empty sitemap index, lastmod-only urlset,
  nested sitemap index); P7e/f (served-page gate,
  fragments); P8a/b/c (og:description follows the meta
  description rule exactly — the block-level head strip
  covers property= carriers, not just name=).

## Corpus regression

All 44 stored captures replayed through the Wave 22-fixed
classifier (`validation/wave15/corpus_check.py` output vs
Wave 15's `corpus-after.txt`): **diff is empty.** The
svg-metadata strip, the SSO rule, and the language
additions touch no capture.

## Verification

- Full suite: **638/638 green** (608 pre-existing + 30 new).
- MCP smoke: all three tools pass live (see final
  verification in the wave report).
- Every Wave 22 JSON re-read and parsed; no 0-byte files.
