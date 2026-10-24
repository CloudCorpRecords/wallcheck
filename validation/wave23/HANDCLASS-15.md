# Wave 23 — Battery v15: Hand classifications (written BEFORE running any shape)

Shapes are hand-classified here first; the test file then checks
the classifier against these verdicts. A mismatch is either a
classifier defect (fix test-first, generalized) or a hand
correction (justified in PROBLEMS.md, never a silent flip).

Conventions: BIG_ARTICLE as in test_adversarial14.py
(> 16 KB, so the served-page gate applies). "Small page" = a
stub page, no real content. Every new signal family in this
battery carries visible-text gating and a served-page size gate
from birth (the Waves 17–22 lesson: each new signal family
misfired on live traffic through asset filenames, script
identifiers, or stylesheet classes), with a negative fixture
per family using an asset-filename, script-identifier, or
stylesheet-class carrier.

Collision check: each family below was checked against all
fourteen prior HANDCLASS files (Waves 6, 10–22) before
writing. Near-misses found and deliberately distinguished:
Wave 19 L2 covered challenge phrases in img ALT attributes
(presented text — screen readers and broken-image rendering);
Q1 covers stray TEXT NODES inside <picture> instead, which
no browser renders (the picture element renders only its
<img>). Wave 13 E1 covered image-only captcha pages; Wave 22
P1 covered SVG <title>/<desc> metadata (Q1 is the picture
element, a different tag with a different rendering model).
Wave 10 B3c / Wave 22 P2 covered 451; Wave 5 covered 444;
no prior battery used 418 (Q2). Wave 11 C8g covered a named
robots group FIRST; Q3 puts the wildcard group mid-file and
last, and duplicates it. Wave 15 G9 / Wave 19 L5 / Wave 22
P5 covered frontmatter stripping, CR endings, and BOM+CRLF;
Q4 puts MARKDOWN inside the frontmatter fields. Wave 21 N6
covered non-HTTP-scheme sitemap locs; Q5 covers scheme CASE.
Wave 19 L1 covered <template> (inert); Q6 covers <slot>,
whose fallback content RENDERS in a plain document — the
opposite rendering model, deliberately. Wave 14 F4 /
Wave 21 N2 covered Retry-After with second values; Q8 uses
an HTTP-date value.

## Q1 — challenge text ONLY as stray text nodes inside <picture> (classifier)

Per the HTML standard, <picture>'s content model is <source>
elements plus one <img> plus script-supporting elements;
stray text nodes inside <picture> are not rendered by any
browser — the element renders only the chosen image. That
makes picture text the <template> family (never-presented
content), NOT the img-alt family (alt text IS presented:
screen readers, image-failure rendering). The configuration
family is uniform since Wave 16: a signal living only in
never-presented content is not a presented wall when the
page has visible content, and is the page when it has none.

- Q1a: small real paragraph + <picture> with a stray text
  node "Verify you are human" → OPEN (the phrase is never
  rendered; the paragraph is the page). Predicted gap:
  _visible_text strips tags but keeps text nodes, and no
  picture strip exists, so the phrase currently reads as
  body text → CHALLENGED.
- Q1b: content-free page, ONLY a <picture> whose stray
  text reads "Verify you are human" → CHALLENGED
  (never-presented content IS the page when nothing else
  exists — the P1a survival principle). Pin either way.
- Q1c: BIG_ARTICLE + <picture> stray text phrase → OPEN
  (served-page gate). Pin.
- Q1d: content-free page, <picture> with <source
  srcset="gate.jpg"> and an <img alt="A scenic photo">
  and NO stray text and no phrase anywhere → OPEN (a
  picture element alone is content, not a wall). Pin.
- Q1e: BIG_ARTICLE + <picture><source
  srcset="verify-you-are-human.png"><img
  src="verify-you-are-human.png" alt="A scenic photo">
  → OPEN (asset filenames are configuration — the
  negative carrier for this family). Pin.

## Q2 — HTTP 418 responses (classifier)

418 (RFC 9110 §15.5.19, reserved from the RFC 2324 joke) is
used in the wild as a deliberate refusal code — including
specifically to refuse non-browser clients. It is neither a
served page, nor a challenge, nor a login, nor a server
failure: it belongs to the deliberate-refusal family with
444 (Wave 5) and 451 (Wave 10). A 418 must never read OPEN.

- Q2a: 418, small body "I'm a teapot. This server is a
  teapot; it declines to brew your request." → WALLED,
  vendor None. Predicted gap: no 418 branch exists, and
  the final fallthrough reads any status outside
  (401, 403) as OPEN.
- Q2b: 418, body "Verify you are human" + challenge
  wording → WALLED, vendor Generic (the P2c principle:
  the refusal code governs the verdict; body evidence
  still names the vendor). Predicted gap or precedence
  defect, per the run.
- Q2c: 418, cf-ray header + "Just a moment" body →
  CHALLENGED, Cloudflare (a fired vendor challenge
  outranks a bare status — vendor branches precede the
  status chain). Pin.
- Q2d: 418, empty body → WALLED, vendor None. Predicted
  gap (same fallthrough as Q2a).

## Q3 — robots.txt wildcard group placement (audit tool)

RFC 9309 group selection is by agent match, not file
position: an agent's own group governs wherever it sits,
and the wildcard group is the fallback. parse_robots
closes a group when a User-agent line follows rules, and
_agent_state flattens ALL applicable groups' rules.

- Q3a: `User-agent: GPTBot / Disallow: /` FIRST, then
  `User-agent: * / Allow: /` → WARN (GPTBot blocked by
  its own group; the other three tracked agents open
  via the wildcard). Pin.
- Q3b: `User-agent: * / Disallow: /` FIRST, then
  `User-agent: ClaudeBot / Allow: /` → WARN (ClaudeBot
  open via its own later group; the other three blocked
  via the wildcard — not all four, so not FAIL). Pin.
- Q3c: GPTBot group (Disallow: /), then `User-agent: * /
  Allow: /` MID-FILE, then CCBot group (Disallow: /)
  → WARN (GPTBot + CCBot blocked; ClaudeBot +
  Google-Extended open via the mid-file wildcard). Pin.
- Q3d: TWO wildcard groups — `User-agent: * /
  Disallow: /` then later `User-agent: * / Allow: /`
  → PASS (_agent_state flattens both wildcard groups;
  the Wave 15 RFC 9309 tiebreak: Allow: / cancels
  Disallow: /). Pin.

## Q4 — llms.txt YAML frontmatter containing markdown (audit tool)

Wave 15 strips the frontmatter block before content
analysis, and SPEC states metadata URLs/links are not
index entries. These shapes test that the strip is a
block strip — markdown INSIDE the frontmatter fields
must not leak into the content analysis.

- Q4a: frontmatter whose description field carries two
  markdown links, body after the strip is ONLY a title
  line → WARN (title-only after strip, the E6a/W15
  shape; if the frontmatter links leaked, this would
  read PASS). Pin.
- Q4b: frontmatter with markdown links + a real
  markdown index body → PASS (the body governs). Pin.
- Q4c: frontmatter ONLY (title + description with
  markdown links, no body at all) → WARN (frontmatter-
  only is a stub — the G9b shape; leaked links would
  read PASS). Pin.
- Q4d: frontmatter with markdown links + body carrying
  exactly one real markdown link → PASS (one usable
  body link is content — the Wave 15 length-gate
  refinement: a body carrying a link passes however
  short). Pin.

## Q5 — sitemap <loc> entries with an uppercase scheme (audit tool)

RFC 3986: scheme names are case-insensitive. Wave 21 N6
made a loc count only for http/https/schemeless
destinations; _has_nonempty_loc lowercases the scheme
before comparing (audit.py line ~413), so these are
pins validating the case handling composes.

- Q5a: urlset with one <loc>HTTPS://EXAMPLE.COM/PAGE
  </loc> → PASS. Pin.
- Q5b: sitemapindex with <loc>HTTPS://EXAMPLE.COM/
  SITEMAP-1.XML</loc> → PASS. Pin.
- Q5c: urlset with <loc>HtTpS://example.com/x</loc>
  → PASS. Pin.
- Q5d: urlset whose only <loc> is FTP://EXAMPLE.COM/
  FILE → WARN (an uppercase NON-http scheme still
  does not count — case-insensitivity is not scheme
  blindness). Pin.

## Q6 — challenge text inside a <slot> element (classifier)

<slot> is the Web Components distribution element: its
fallback content renders whenever no nodes are assigned,
and in a plain document (no shadow tree) a slot's
children render as ordinary content. That is the
OPPOSITE rendering model from <template> (Wave 19 L1,
inert until cloned). Slot fallback text is presented
text and must behave like body text.

- Q6a: content-free page, only <slot>Verify you are
  human</slot> → CHALLENGED (the fallback is the page,
  and it is presented). Pin — no slot strip exists.
- Q6b: BIG_ARTICLE + <slot> with the phrase → OPEN
  (served-page gate). Pin.
- Q6c: small real paragraph + <slot name="gate">
  Verify you are human</slot> → CHALLENGED (presented
  challenge text on a non-served page fires — this is
  body text, not metadata; the J1 noscript strip does
  not apply because slot content renders). Pin.
- Q6d: <template><slot>Verify you are human</slot>
  </template> + a small real paragraph → OPEN (the
  template strip removes the whole inert block,
  slot included — composition pin). Pin.

## Q7 — challenge phrases in Greek, Czech, Hungarian, Romanian (classifier)

Same principle as every prior language wave: challenge
pages are not English-only. Verified against the current
_LOCALIZED_HUMAN_CHECK list before writing: Greek,
Czech, Hungarian, and Romanian have NO entry (grep for
each phrase below returned 0 in classify.py). Each
phrase is a full "confirm you are not a robot" sentence,
not a fragment.

- Q7a EL: small page "Επιβεβαιώστε ότι δεν είστε
  ρομπότ" → CHALLENGED. Predicted gap.
- Q7b CS: small page "Potvrďte, že nejste robot"
  → CHALLENGED. Predicted gap.
- Q7c HU: small page "Kérjük, erősítse meg, hogy Ön
  nem robot" → CHALLENGED. Predicted gap.
- Q7d RO: small page "Confirmați că nu sunteți un
  robot" → CHALLENGED. Predicted gap.
- Q7e EL phrase on BIG_ARTICLE → OPEN (served-page
  gate). Pin.
- Q7f 200, small page with only the fragment "ρομπότ"
  → OPEN (fragments do not fire; the J7g guessing
  boundary). Pin. HAND CORRECTION (recorded in
  PROBLEMS.md): the first draft used status 403, which
  is a bare refusal and reads WALLED regardless of the
  fragment (the J7g precedent itself) — the fragment
  pin belongs on a served page, as in P7f.
- Q7g EL phrase ONLY inside a <style> block + a small
  real paragraph → OPEN (Wave 16 style-block
  suppression — the negative carrier for this family:
  a stylesheet is configuration, not a prompt). Pin.

## Q8 — 429/403/503 with an HTTP-date Retry-After (classifier)

RFC 9110 allows Retry-After as delay-seconds OR an
HTTP-date. The Wave 14 rule keys on header PRESENCE plus
throttle wording and never parses the value, and 429
needs no value at all — so the date form must behave
identically to the seconds form.

- Q8a: 429, `Retry-After: Wed, 21 Oct 2015 07:28:00
  GMT`, body "Too many requests." → RATE_LIMITED. Pin.
- Q8b: 403, `Retry-After: Wed, 21 Oct 2015 07:28:00
  GMT`, body "Too many requests. Please slow down."
  → RATE_LIMITED (RETRY_AFTER_THROTTLE is
  format-independent). Pin.
- Q8c: 503, `Retry-After: Wed, 21 Oct 2015 07:28:00
  GMT`, body "Too many requests." → RATE_LIMITED.
  Pin.
- Q8d: 403, `Retry-After: Wed, 21 Oct 2015 07:28:00
  GMT`, body "Access denied." → WALLED (the F4f
  principle: the header alone, in any format, does
  not convert a refusal without throttle wording).
  Pin.
