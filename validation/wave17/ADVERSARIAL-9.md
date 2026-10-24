# Wave 17 — Adversarial Battery v9: Results

48 shapes, hand-classified first in HANDCLASS-9.md, run against
the classifier in `tests/test_adversarial9.py`. **6 defect
families, all fixed test-first and generalized; corpus clean
(44 captures, zero diff vs the Wave 15 baseline); full suite
423/423 green** (375 pre-existing + 48 new).

## Defects fixed

- **W17-001 — noscript fallback notes drove verdicts (J1).** A
  human-check or vendor marker living only inside a `<noscript>`
  block fired on pages that also serve real body content. Fix:
  noscript blocks are stripped from the visible-text test and
  from the marker scans when the page has visible text — the
  W16-002/003 family, extended. Noscript-only pages still fire
  (the strip is conditioned on visible text, and _visible_text
  now excludes noscript, so a noscript-only page reads as
  content-free and the fallback rules fire). Fixtures: J1a/c/e
  + guards J1b/d/f/g.
- **W17-002 — title-only wall text drove verdicts (J2).** A
  human-check, JS-proof, vendor, or traffic-anomaly marker
  living only in the `<title>` fired on small real content
  pages (neither the E3a spinner pin nor the 16 KB size gate
  decides there). Fix: `<head>` blocks are stripped from the
  generic survival variants and the traffic branch's raw side,
  and from the vendor scan, when the page has visible text.
  Title-only pages still fire (content-free fallback).
  Fixtures: J2a/c/d/e + guards J2b/g.
- **W17-002b — corroboration refinement to W17-002 (caught by
  the base suite, not the battery).** The first head-strip
  broke `test_cloudflare_challenge_page`: the real Cloudflare
  challenge fixture titles itself "Just a moment..." while its
  body performs security verification, and stripping the title
  lost the CF_JUST_A_MOMENT evidence code. Refinement: the
  vendor-scan head/noscript strip applies only when the title
  or fallback note stands ALONE — when the body itself already
  presents a wall phrase, the head/noscript marker is
  corroborating attribution and is kept. A title marker on a
  page whose body shows no wall signal is still suppressed
  (J2a/c/d/e all still pass). This is the same distinction
  the survival tests already draw, applied to vendor
  attribution.
- **W17-003 — QR-code sign-in prompts read OPEN (J4).** No QR
  signal existed. Fix: QR_PROMPT — QR wording + auth purpose
  ("sign in" / "log in" / "authenticate") + a prompt marker
  (image, canvas, button) — placed beside CODE_ENTRY_FORM,
  PASSKEY_PROMPT, and MAGIC_LINK_FORM with the same status
  guard and precedence. Prose, app-download codes, and bare
  links cannot fire. Fixtures: J4a/f + guards J4b/c/d/e.
- **W17-004 — entity-encoded JSON error documents misgraded
  (J6).** An llms.txt body of `{&quot;error&quot;: ...}` failed
  the JSON parse and fell through to the stub gate (WARN) instead
  of the error gate (FAIL). Fix: `html.unescape` before the JSON
  parse attempt only — other content tests keep reading raw
  text, so an escaped anchor's URL still counts and an
  entity-encoded slash still is not a path. Fixtures: J6c/d +
  pins J6a/b/e.
- **W17-005 — Nordic challenge phrases missing (J7).** Swedish,
  Finnish, Danish, and Norwegian human-check phrases were not in
  the localized list. Fix: added the phrases (Swedish
  "bekräfta att du inte är en robot" / "jag är inte en robot",
  Finnish "vahvista, ettet ole robotti" / "en ole robotti",
  Danish "bekræft, at du ikke er en robot", Norwegian "bekreft
  at du ikke er en robot", shared "jeg er ikke en robot").
  Fixtures: J7a–e + pins J7f/g.
- **W17-006 — full-screen overlay challenges read OPEN (J8).**
  The 16 KB served-page gate suppressed every body marker on
  article pages, including a modal that blocks the article.
  Fix: OVERLAY_CHALLENGE — an overlay-marked container tag
  (class/id naming an overlay, modal, popup, lightbox, or
  dialog) plus a human-check or JS-proof phrase in the following
  800 chars (script/style stripped). NOT gated by page size;
  gated to 2xx non-login pages, with the login exclusion
  mirroring the generic branch. A bare "captcha" token is
  deliberately not enough (widget loaders ride in overlay
  markup). Fixtures: J8a/e/f + guards J8b/c/d/g/h.

## Pins (no defect — the classifier was already right)

- **J3 (cache headers).** No-store/no-cache headers neither
  create nor suppress a verdict in any branch; all four shapes
  pass unmodified. Cache directives are not wall signals.
- **J5 (commented Sitemap lines).** The robots parser already
  strips `#` comments, so commented declarations are never
  recorded, never routed to, and never suppress a real
  declaration. All four shapes pass unmodified.
- **J7g (code-switched fragments).** "Verify / eres humano"
  composes no listed phrase in any language and correctly
  reads WALLED (a refusal with no complete challenge evidence).
  Matching half-phrases across languages would be guessing.
- **J9a (script-boundary captcha re-test).** The Wave 16
  residual edge re-tested: a token split with one half in a
  script block and one half in body text still reads OPEN —
  and that is the CORRECT reading, sharpened by the re-test:
  the rendered page never presents a "captcha" token to any
  reader, so a static non-JS fetch cannot and should not claim
  one. The edge stays ledgered as a limitation-by-design
  (re-tested 2026-10-24), not a defect. A token assembled only
  by script execution is invisible to this tool by SPEC
  constraint (no JS execution).

## Corpus regression

All 44 stored captures replayed through the Wave 17-fixed
classifier (`validation/wave15/corpus_check.py` output vs
Wave 15's `corpus-after.txt`): **diff is empty.** The
noscript/head strips move nothing on real traffic (no stored
capture carries a noscript block; the one head-title challenge
fixture is covered by the W17-002b corroboration rule), the
overlay rule touches no capture (captures are final responses,
not article-plus-modal pages), and the QR/entity/Nordic
changes touch no capture.

## Verification

- Full suite: **423/423 green** (375 pre-existing + 48 new).
- MCP smoke: all three tools pass live (`scripts/smoke_mcp.py`:
  initialize, tools/list `['probe_url', 'classify', 'audit']`,
  classify → CHALLENGED / Cloudflare, probe_url(example.com) →
  OPEN 200, audit(example.com) → F 3/12).
- Every Wave 17 JSON re-read and parsed; no 0-byte files.
