# Wave 18 — Adversarial Battery v10: Results

48 shapes, hand-classified first in HANDCLASS-10.md, run against
the classifier in `tests/test_adversarial10.py`. **6 defect
families, all fixed test-first and generalized; corpus clean
(44 captures, zero diff vs the Wave 15 baseline); full suite
476/476 green** (428 pre-existing + 48 new).

## Defects fixed

- **W18-001 — sticky-banner challenges read OPEN (K2).** A
  fixed-position banner carrying a human check over a served
  article was suppressed by the size gate: the J8 overlay tag
  list had no banner marker. Fix: a banner rule beside the
  overlay rule — a banner-marked container (class/id naming a
  banner or announcement bar) PLUS a human-check or JS-proof
  phrase in the following 800 chars, gated by a third key the
  overlay rule does not need: the banner tag must itself signal
  fixed/sticky positioning (inline style or a sticky/fixed class
  marker). The third key is load-bearing: the first attempt
  (bare banner marker, no stickiness key) broke nothing in the
  suite but misread the K2f guard — an in-flow banner is layout,
  not an overlay — and the stickiness key is what separates
  them. Fixtures: K2a/e + guards K2b/c/d/f.
- **W18-002 — SMS/email code prompts in digit-box inputs read
  OPEN (K3).** G6's code-entry rule names its inputs
  (otp/2fa/auth-code/…/code); real SMS/email prompts use digit
  boxes (`digit-1` … `digit-6`) and delivery wording ("the code
  we texted/emailed to you"). Fix: DELIVERY_CODE_PROMPT —
  digit-box input + delivery wording in rendered visible text
  (the W17-007 visible-text discipline), placed beside the
  code-entry, passkey, and magic-link rules with the same
  status and served-page gates. Fixtures: K3a/e + guards
  K3b/c/d/f.
- **W18-003 — declared-but-dead sitemaps invisible in audit
  evidence (K4).** When no sitemap served anywhere, a
  robots-declared URL that never served was indistinguishable
  from no declaration at all. Fix (evidence only, grades
  unchanged): `_check_sitemap` appends DECLARED_SITEMAP_DEAD
  (first declared URL) on its WARN paths when the robots file
  declared sitemaps — accurate because the audit's fallthrough
  has already established that no declared sitemap served.
  Fixtures: K4a/d + pins K4b/c/e.
- **W18-004 — empty `<loc>` elements passed the sitemap check
  (K6).** The check tested `<loc` tag presence, not loc
  content, so a sitemap whose entries named nothing passed the
  W15-010 "names no URLs" test. Fix: `_has_nonempty_loc` —
  at least one `<loc>` element must carry non-empty content;
  relative references still count (they resolve against the
  sitemap URL). Fixtures: K6c/d + pins K6a/b/e.
- **W18-005 — PT-BR, Indonesian, Vietnamese, and Thai challenge
  phrases missing (K7).** Four new language families added to
  `_LOCALIZED_HUMAN_CHECK`, gated like every generic marker.
  The PT-BR delta is stated in HANDCLASS-10: the fuller "eu não
  sou um robô" already matched the European-PT phrase by
  substring, so only the distinct "Confirme…" demand is new.
  Fixtures: K7a/c/d/e/f/g/h + pins K7b/i/j.
- **W18-006 — aria-labels on non-interactive elements drove
  vendor attribution (K8).** A vendor name in a plain `<div>`'s
  aria-label fired the vendor scan, though assistive technology
  ignores labels on non-interactive elements. Fix: non-
  interactive aria-label attributes are stripped from every
  body scan when the page has visible text (the data-*/style
  family, conditioned the same way — a page whose only text is
  such a label still fires, the blob-is-the-page species);
  interactive elements (a, area, button, input, select,
  textarea) keep their accessible names, which ARE presented
  text (the F2 principle). Only the attribute is stripped, never
  the tag prefix, so overlay class markers survive. Fixtures:
  K8d + pins K8a/b/c/e.

## Pins (no defect — the classifier was already right)

- **K1a/K1d (unconsumed custom properties).** Stylesheet
  configuration, never rendered — the style-block strip already
  covers the property form, exactly as H3b/H3e.
- **K1b/K1e (CSS content / property-only pages).** The CSS
  content string is the page's only presented text (H3a/H3f
  species); the content-free fallback already fires.
- **K1f (decorative content: on a big article).** The size gate
  protects the article; the CSS-content wiring added this wave
  is conditioned on content-free pages for exactly this reason
  (see the H3b regression note below).
- **K2b/K2c (cookie/newsletter banners).** No challenge phrase,
  no wall — the phrase key is load-bearing.
- **K2d (small-page banner).** The small-page path already fires;
  the banner rule agrees.
- **K3b/K3c (named-input SMS prompt; SMS prompt at a login
  URL).** G6 and the login heuristic already fire.
- **K3d/K3f (prose about codes; phone-request forms).** No
  code/digit input, no prompt — guards hold.
- **K4b/K4c/K4e (dead declaration with a serving sitemap;
  fallthrough; no declaration).** Grades already correct; only
  K4a/d's evidence was missing.
- **K5 (llms via trailing-slash redirects).** The fetcher
  follows redirects; every final-document species grades as
  its document deserves. Pins, not fixes — the redirect is new
  ground for the llms check, but the machinery already handles
  it.
- **K6a/K6b/K6e (relative locs).** Relative references name
  destinations; the counting rule already covers them.
- **K7b (fuller PT-BR form).** Substring-covered by the existing
  PT phrase. K7i (quoted Thai phrase on a big article): the
  served-page gate. K7j (code-switched fragments): no listed
  phrase composes across languages (J7g species).
- **K8a/K8b/K8c/K8e (interactive aria-labels).** Accessible
  names of interactive elements are presented text; the raw
  scan already fires on small pages, the size gate already
  protects big articles, and an image's accessible name is its
  fallback text (F2 species).

## Regression note (caught by the base suite, not the battery)

The first CSS-content wiring broke `test_h3b` (Wave 16): a
decorative `::before` string on a small article read CHALLENGED.
The wiring now applies only on content-free pages — on a page
with visible text a content: string is decorative (H3b), while
on a content-free page it IS the page's text (H3a). The
conditioning matches every other suppression in the family.
A second near-miss in the same fix: the first banner attempt
(bare banner marker, no stickiness key) misread the K2f guard
in development and was corrected before the suite ran green —
in-flow banners are layout, and the stickiness key is what
separates them from overlays.

## Corpus regression

All 44 stored captures replayed through the Wave 18-fixed
classifier (`validation/wave15/corpus_check.py` output vs
Wave 15's `corpus-after.txt`): **diff is empty.** The banner,
delivery-code, language, aria, loc, and dead-declaration changes
touch no capture; the CSS-content wiring touches no capture
(captures are final responses, not content:-assembled pages).

## Verification

- Full suite: **476/476 green** (428 pre-existing + 48 new).
- MCP smoke: all three tools pass live (`scripts/smoke_mcp.py`:
  initialize, tools/list `['probe_url', 'classify', 'audit']`,
  classify → CHALLENGED / Cloudflare, probe_url(example.com) →
  OPEN 200, audit(example.com) → F 3/12).
- Every Wave 18 JSON re-read and parsed; no 0-byte files.
