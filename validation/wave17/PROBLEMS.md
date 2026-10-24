# Wave 17 — Problems ledger

## Leg B (adversarial battery v9) — 6 defect families, all fixed

- **W17-001** (classifier, fixed): noscript fallback notes drove
  verdicts (J1a: article + noscript human-check read CHALLENGED;
  J1c: small paragraph + noscript JS-proof read CHALLENGED; J1e:
  article + noscript vendor name read CHALLENGED / PerimeterX).
  Fix: noscript blocks are stripped from the visible-text test
  and from the marker scans when the page has visible text
  (the W16-002/003 family, extended). Noscript-only pages still
  fire (the strip is conditioned on visible text, and
  _visible_text now excludes noscript, so a noscript-only page
  reads as content-free). Fixtures: test_j1a/c/e + guards
  J1b/d/f/g.
- **W17-002** (classifier, fixed): title-only wall text drove
  verdicts on small real content pages (J2a: paragraph + title
  human-check read CHALLENGED; J2c: paragraph + title vendor
  name read CHALLENGED / PerimeterX; J2d: paragraph + title
  JS-proof read CHALLENGED; J2e: refusal body + title
  anomaly wording read CHALLENGED via TRAFFIC_CHECK). Fix:
  `<head>` blocks are stripped from the generic survival
  variants, the traffic branch's raw side, and the vendor scan
  when the page has visible text. Title-only pages still fire
  (content-free fallback). Fixtures: test_j2a/c/d/e + guards
  J2b/g.
- **W17-002b** (classifier, refinement to W17-002, caught by the
  base suite): the first head-strip broke
  `test_cloudflare_challenge_page` — the real Cloudflare
  challenge fixture titles itself "Just a moment..." while its
  body performs security verification, and stripping the title
  lost the CF_JUST_A_MOMENT evidence code. Refinement: the
  vendor-scan head/noscript strip applies only when the title
  or fallback note stands ALONE — when the body itself already
  presents a wall phrase, the head/noscript marker is
  corroborating attribution and is kept. (The generic survival
  strips need no such refinement: a body-presented phrase
  survives them on its own.) Fixture: the pre-existing
  Cloudflare challenge test, green again; J2a/c/d/e still pass.
- **W17-003** (classifier, fixed): QR-code sign-in prompts read
  OPEN (J4a/J4f: QR wording + image/canvas, no signal). Fix:
  QR_PROMPT — QR wording + auth purpose + a prompt marker
  (image, canvas, button) — placed beside CODE_ENTRY_FORM,
  PASSKEY_PROMPT, and MAGIC_LINK_FORM. Fixtures: test_j4a/f +
  guards J4b/c/d/e.
- **W17-004** (audit tool, fixed): an entity-encoded JSON error
  document in llms.txt read WARN (stub) instead of FAIL
  (J6c: `{&quot;error&quot;: ...}` failed the JSON parse and
  fell through). Fix: `html.unescape` before the JSON parse
  attempt only; other content tests keep reading raw text.
  Fixtures: test_j6c/d + pins J6a/b/e.
- **W17-005** (classifier, fixed): Swedish, Finnish, Danish,
  and Norwegian challenge phrases were not in the localized
  list (J7a–d read WALLED). Fix: added the phrases to
  _LOCALIZED_HUMAN_CHECK. Fixtures: test_j7a–e + pins J7f/g.
- **W17-006** (classifier, fixed): full-screen overlay
  challenges on article pages read OPEN (J8a/J8e/J8f: the 16 KB
  served-page gate suppressed every body marker). Fix:
  OVERLAY_CHALLENGE — an overlay-marked container tag plus a
  human-check or JS-proof phrase in the following 800 chars
  (script/style stripped); not gated by page size, gated to
  2xx non-login pages. A bare "captcha" token is deliberately
  not enough (widget loaders ride in overlay markup).
  Fixtures: test_j8a/e/f + guards J8b/c/d/g/h.

## Leg B — pins and boundaries (no defect)

- **J3 (cache headers):** no-store/no-cache headers neither
  create nor suppress a verdict in any branch. Pins, not fixes.
- **J5 (commented Sitemap lines):** the robots parser already
  strips `#` comments; commented declarations are never
  recorded or routed to. Pins, not fixes.
- **J7g (code-switched fragments):** "Verify / eres humano"
  composes no listed phrase and correctly reads WALLED.
  Matching half-phrases across languages would be guessing.
- **J9a (script-boundary captcha re-test):** the Wave 16
  residual edge re-tested and SHARPENED, not fixed: a token
  split with one half in a script block and one half in body
  text still reads OPEN, and that is the correct reading —
  the rendered page never presents a "captcha" token to any
  reader. The edge stays ledgered as a limitation-by-design
  (re-tested 2026-10-24). A token assembled only by script
  execution is invisible to a static non-JS fetch by SPEC
  constraint.

## Leg B — corpus regression (done)

Stored captures replayed through the Wave 17-fixed classifier
(`validation/wave15/corpus_check.py`, output vs Wave 15's
`corpus-after.txt`). Zero regressions: diff is empty. The
noscript/head strips move nothing on real traffic, the overlay
rule touches no capture, and the QR/entity/Nordic changes
touch no capture. Same artifact as Waves 13–16 (not a
regression): `validation/wave7/captures/careerjet.json` reads
OPEN because the JSON record carries an empty body (the real
HTML lives in `careerjet.html`, which classifies CHALLENGED /
Cloudflare exactly as Wave 7 established).

## Leg A (round-13 reclassification) — see STABILITY-12.md

Round 13 re-probed the full 499-row index with the Wave 16-fixed
classifier (fixes grep-verified before launch; the Wave 17
battery fixes landed after the runner imported its tree, so
they are unmeasured on live traffic until round 14). Zero rows
merged; all three verdict diffs held on fresh captures. One
diff exposed a live defect in a Wave 16 rule, fixed this wave:

- **W17-007** (classifier, fixed): the Wave 16 PASSKEY_PROMPT
  rule misfired on rubygems.org's served homepage — the round
  read LOGIN_GATED, and two fresh captures agreed, but
  inspection proved it wrong: the 36 KB homepage's only
  "webauthn" signals are asset filenames in its import map,
  and the page carries ordinary forms. The rule as implemented
  never enforced its own design ("the page's only content is
  a prompt"): it read wording from raw body text including
  asset paths and script text, and it had no served-page gate.
  Fix, generalized to all three auth-form rules: (1)
  passkey/magic-link wording must appear in rendered visible
  text (code-entry keeps raw-body wording — its INPUT is
  itself presented barrier machinery, not a mere mention, and
  the distinction is pinned by fixture); (2) all three
  auth-form branches (code-entry, passkey, magic-link) now
  carry the served-page size gate, since "only content" and
  "full served page" contradict. Post-fix live re-probe reads
  OPEN 200. Fixtures: test_w17_rubygems_shape,
  test_w17_real_passkey_prompt_with_webauthn_assets_still_fires,
  test_w17_large_page_passkey_form_is_open,
  test_w17_newsletter_form_script_only_magic_link_wording_is_open,
  test_w17_code_input_script_only_wording_still_fires. Residual
  boundary, documented: a SMALL served page carrying a visible
  passkey button in its nav (wording in visible text, under the
  size gate) would still fire — the "only content" test is
  enforced by size, not by form isolation, and that edge is
  the Wave 14 F5 limitation's next of kin. Full suite after
  the fix: 428/428; corpus still clean.

Round-13 verdict moves, fresh-capture corroboration, and merges
are recorded in STABILITY-12.md.
