# Wave 22 — Battery v14: Hand classifications (written BEFORE running any shape)

Shapes are hand-classified here first; the test file then checks
the classifier against these verdicts. A mismatch is either a
classifier defect (fix test-first, generalized) or a hand
correction (justified in PROBLEMS.md, never a silent flip).

Conventions: BIG_ARTICLE as in test_adversarial13.py
(> 16 KB, so the served-page gate applies). "Small page" = a
stub page, no real content. Every new signal family in this
battery carries visible-text gating and a served-page size gate
from birth (the Waves 17–21 lesson: each new signal family
misfired on live traffic through asset filenames, script
identifiers, or stylesheet classes), with a negative fixture
per family using an asset-filename, script-identifier, or
stylesheet-class carrier.

Collision check: each family below was grepped against all
thirteen prior HANDCLASS files (Waves 6, 10–21) before
writing. Near-misses found and deliberately distinguished:
Wave 10 B3c covered 451 + a short "Unavailable for legal
reasons" stub (P2 extends it to a full notice and to a
challenge-phrase body); Wave 14 C8a covered Crawl-delay-only
robots (P4b pairs it with a blocking rule); Wave 21 N8
covered name="description" meta (P8 extends it to
property="og:description"); Wave 15 G3 covered SVG <text> /
<tspan> (P1 covers SVG <title> / <desc> metadata instead).

## P1 — SVG <title> / <desc> metadata (classifier)

Wave 15 G3 pinned contiguous SVG <text> (the raw-body scan
reads it) and split <tspan> text. But <title> and <desc>
inside an <svg> are accessibility metadata, not rendered
body text — the same family as <head> metadata (Wave 17 J2,
Wave 21 N8): metadata IS the page when content-free, and
must be stripped from scans when visible body text exists.
_visible_text strips head/script/style/noscript/template
blocks and then all tags — it does NOT strip svg title/desc
blocks, so their text survives into visible text.

- P1a: content-free page, only an <svg> with
  <title>Verify you are human</title> → CHALLENGED
  (metadata IS the page — E3/N8a principle). Pin.
- P1b: BIG_ARTICLE with an <svg> whose <title> reads
  "Verify you are human" → OPEN (served-page gate). Pin.
- P1c: small real paragraph + an <svg> whose <title>
  reads "Verify you are human" → OPEN (the metadata rule:
  svg title/desc text must be stripped from scans when
  visible body text exists, exactly like head metadata).
  Predicted gap: no svg-metadata strip exists, so the
  title text reads as body text → CHALLENGED.
- P1d: content-free page, only an <svg> with
  <desc>Verify you are human</desc> → CHALLENGED
  (same family as P1a). Pin.

## P2 — HTTP 451 variants (classifier)

Wave 10 B3c: 451 + "Unavailable for legal reasons" →
WALLED (451 is a deliberate refusal code, RFC 7725, not a
served page and not a server failure). Open questions: does
the 451 rule hold for a full-length legal notice (not a
stub), and what wins when a 451 body also presents a
challenge phrase?

- P2a: 451, multi-paragraph legal notice body (~3 KB of
  real legal explanation text) → WALLED (the refusal code
  governs regardless of body size; a long refusal is
  still a refusal, not served content).
- P2b: 451, empty body → WALLED (B3c family). Pin.
- P2c: 451, body "Verify you are human" + challenge
  wording → WALLED (precedence: the server's refusal
  code governs over challenge text inside a refusal
  document; the page is refused, not checkable).
  Predicted question, not gap: if the classifier reads
  CHALLENGED, that is a precedence defect to fix (or a
  reasoned ledger entry if the precedence argument
  reverses on inspection).

## P3 — "Continue with SSO" prompts (classifier, new signal)

No existing auth rule names single-sign-on: code-entry
needs a code-named input, delivery needs digit boxes plus
a channel, email-Continue needs an email input plus a
Continue button, authenticator needs TOTP wording + a TOTP
input. An SSO step uses SSO wording plus an SSO button or
link that starts the flow. Two keys, from birth: SSO
wording in rendered visible text PLUS an SSO button/link.
Visible-text discipline and served-page size gate apply
from birth (the Waves 17–21 lesson).

- P3a: small page, "Continue with SSO" + <button>
  Continue with SSO</button> → LOGIN_GATED. Predicted
  gap: no SSO rule exists.
- P3b: BIG_ARTICLE with an SSO button → OPEN
  (served-page size gate). Pin.
- P3c: served article page whose only "sso" signal is a
  script filename (sso.js) → OPEN (an asset filename
  is configuration, not a prompt). Negative carrier.
- P3d: served article page whose only "sso" signal is a
  stylesheet class (.sso-button) → OPEN (a stylesheet
  class is configuration). Negative carrier.
- P3e: small page, SSO wording in prose but NO button
  or link → OPEN (wording without barrier machinery
  is prose). Pin.
- P3f: small page, SSO wording + button + a short real
  paragraph → LOGIN_GATED (the page's only content is
  the prompt; a paragraph of instructions does not make
  it served content — N3e principle). Pin on the size
  gate's lower edge.

## P4 — robots.txt stray rules and Crawl-delay (audit tool)

parse_robots only appends rules while in_group is true, so
a Disallow line before the first User-agent line is
ignored; Crawl-delay is a politeness directive, not a
blocking rule (Wave 14 C8a: Crawl-delay-only → PASS).
Both compositions are pins validating that neither fact
changes when paired with a real group.

- P4a: robots.txt with `Disallow: /private` BEFORE any
  User-agent line, then `User-agent: *` / `Allow: /`
  → PASS (the stray rule is ignored; the * group
  allows everything). Pin.
- P4b: robots.txt `User-agent: *` / `Disallow: /` /
  `Crawl-delay: 10` → FAIL (Crawl-delay does not
  soften a blocking rule). Pin.

## P5 — llms.txt BOM + CRLF composition (audit tool)

Wave 19 W19-L5 normalized CR-only frontmatter; Wave 21
N5c composed BOM + curly quotes. The remaining
composition is BOM + CRLF line endings together.

- P5a: UTF-8 BOM + CRLF line endings + real markdown
  index → PASS (BOM strip and CR normalization
  compose). Pin.
- P5b: BOM + CRLF + frontmatter-only (title + url
  field, no index content) → WARN (LLMS_STUB family).
  Pin.
- P5c: CRLF-only real markdown index → PASS. Pin.

## P6 — sitemap index composition (audit tool)

_check_sitemap requires _has_nonempty_loc, and Wave 21
W21-N6 made a loc count only for http/https/schemeless
destinations. These shapes validate that the loc rule
composes with sitemapindex documents and with entries
that carry no loc at all.

- P6a: sitemapindex document with zero <loc> entries
  → WARN (SITEMAP_NO_URLS family). Pin.
- P6b: urlset whose <url> entries carry only <lastmod>
  (no <loc>) → WARN (W15-010 principle). Pin.
- P6c: sitemapindex whose <loc> entries point to child
  sitemap indexes → PASS (index locs name crawlable
  destinations; an index of indexes is still a sitemap).
  Pin.

## P7 — challenge phrases in Gujarati, Kannada, Nepali, Khmer (classifier)

Same principle as M3 (Wave 20) and N7 (Wave 21): challenge
pages are not English-only, and the list still misses
whole language families. Verified against the current
_LOCALIZED_HUMAN_CHECK list: Gujarati, Kannada, Nepali,
and Khmer have no entry. Each phrase is a full "confirm
you are not a robot" sentence, not a fragment.

- P7a GU: small page "તમે રોબોટ નથી તેની ખાતરી કરો"
  → CHALLENGED. Predicted gap.
- P7b KN: small page "ನೀವು ರೋಬೋಟ್ ಅಲ್ಲ ಎಂದು ಖಚಿತಪಡಿಸಿ"
  → CHALLENGED. Predicted gap.
- P7c NE: small page "तपाईं रोबोट होइन भनेर पुष्टि गर्नुहोस्"
  → CHALLENGED. Predicted gap.
- P7d KM: small page "បញ្ជាក់ថាអ្នកមិនមែនជាមនុស្សយន្ត"
  → CHALLENGED. Predicted gap.
- P7e GU phrase on BIG_ARTICLE → OPEN (served-page
  gate). Pin.
- P7f small page with only a fragment ("રોબોટ" alone,
  no listed phrase) → OPEN (fragments do not fire;
  the J7g guessing boundary). Pin.

## P8 — challenge phrases only in og:description (classifier)

Wave 21 N8: a meta description follows the title rule
exactly — it fires when it IS the page, stripped when
visible text exists — because the conditional head strip
removes the whole <head> block, not one attribute. An
og:description is the same block-level metadata with a
property= carrier instead of name=, so it must behave
identically. All three shapes are pins validating that
the head-strip family covers property= carriers.

- P8a: content-free page, <meta property="og:description"
  content="Verify you are human"> and no other text
  → CHALLENGED (head metadata IS the page when there is
  no body content — E3/N8a principle). Pin.
- P8b: BIG_ARTICLE with an og:description "Verify you
  are human" → OPEN (head stripped when visible text
  exists — J2 principle). Pin.
- P8c: small real content page (a short real paragraph
  plus the og:description phrase) → OPEN (visible
  text exists, so the head strip applies — N8c
  principle). Pin.
