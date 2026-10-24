# Wave 16 — Problems ledger

## Leg B (adversarial battery v8) — 21 defects, all fixed

- **W16-001** (classifier, fixed): TRAFFIC_CHECK scanned the
  raw body only, so a phrase split across elements missed
  (H1a: "unusual" / "traffic" across paragraphs read WALLED).
  Fix: words + cues also matched against space-separated
  visible text (W15-003's treatment, extended to this branch).
  Fixtures: test_h1a–e.
- **W16-001b** (classifier, fixed): within-word splits missed
  by BOTH raw and spaced scans (H1b: cue "ver<span>ify</span>";
  H1f: "Ver<span>ify</span> you are human"; H1g:
  "Brow<span>ser</span> check"; H1h: "cap<span>tcha</span>"
  — all read WALLED). Fix: a third scan variant with tags
  removed entirely (inline elements add no space to rendered
  text), applied to TRAFFIC_CHECK words + cues, the
  human-check and JS_PROOF first and second halves, and the
  captcha presence + survival tests. The variant derives from
  the script/style/data-stripped body, so script-only,
  style-only, widget-tag, and data-attribute tokens never reach
  it (guard: script-only split phrase + visible text stays
  OPEN). Fixtures: test_h1b/f/g/h + guard.
- **W16-002** (classifier, fixed): data-* attribute values
  drove verdicts (H2a: human-check phrase in data-message on a
  content page read CHALLENGED; H2c: vendor name in
  data-vendor read CHALLENGED / PerimeterX; H2e: "captcha" in a
  data-attribute name read CHALLENGED). Fix: data-* attributes
  (name + value) are stripped from the vendor scan when the
  page has visible text, and the "survives stripping" tests
  for human-check, JS_PROOF, and captcha require surviving
  data-attribute stripping too. Rendered attributes (alt,
  title) survive — F2's principle is untouched. Content-free
  pages still fire (H2b/H2d). Fixtures: test_h2a–e + widget
  guard.
- **W16-003** (classifier, fixed): <style> block text drove
  verdicts (H3b: challenge sentence only in a stylesheet on a
  content page read CHALLENGED; H3d: "captcha" in a stylesheet
  class selector; H3e: vendor name in a stylesheet). Fix:
  style blocks are stripped from the vendor scan and added to
  the survival tests when the page has visible text.
  Content-free pages still fire (H3a/H3f). Fixtures:
  test_h3a–f + body-challenge guard.
- **W16-004** (classifier, fixed): the HTTP Location header
  was never collected as a redirect target, so bare 3xx
  responses to gates read OPEN (H4a: 307 to challenge; H4b:
  308 to login; H4d: 302 to challenge) or fell through to the
  login heuristic (H4e: 307 to challenge at a login URL read
  LOGIN_GATED). Fix: Location on a 3xx response is collected
  with meta-refresh semantics; the redirect-to-challenge
  branch precedes the login heuristic. Fixtures: test_h4a–e.
- **W16-005** (classifier, fixed): passkey/WebAuthn prompts
  at non-login URLs read OPEN (H5a: passkey button + ceremony
  script; H5d: passkey button + identity wording). Fix:
  PASSKEY_PROMPT — passkey/WebAuthn wording PLUS a prompt
  marker (button, form, input, or credentials-API reference),
  placed beside CODE_ENTRY_FORM with the same status guard and
  precedence. Prose and bare links cannot fire (H5b/H5e).
  Fixtures: test_h5a–e.
- **W16-006** (audit tool, fixed): a UTF-8 BOM defeated the
  frontmatter strip (H7d: BOM + frontmatter-only llms.txt read
  PASS — the metadata URL counted as content). Fix: a leading
  BOM is stripped before the frontmatter anchor. BOM + real
  content still passes (H7e). Fixtures: test_h7d/e.
- **W16-007** (classifier, fixed): the W15-001 data-block
  strip was typed to ld+json only, so a vendor name in an
  application/json block on a content page read CHALLENGED /
  PerimeterX (H9a). Fix: the strip covers application/json
  and text/json too. Loader scripts untouched (guard: regular
  script + vendor marker + visible text still fires).
  Fixtures: test_h9a/b + guard.
- **W16-008** (classifier, fixed): magic-link / email sign-in
  forms at non-login URLs read OPEN (H10a: email input +
  "sign-in link"; H10c: email input + "password reset link").
  Fix: MAGIC_LINK_FORM — an email input PLUS auth-link
  wording, placed beside CODE_ENTRY_FORM. Newsletter forms
  (input, no auth wording) and bare links cannot fire (H10b/
  H10d). Fixtures: test_h10a–d + guard.

## Leg B — corpus regression (done)

Stored captures replayed through the Wave 16-fixed classifier
(`validation/wave15/corpus_check.py`, output vs Wave 15's
`corpus-after.txt`). Zero regressions: diff is empty. Every
real wall capture reads as its wave established — the
data-attribute, style-block, and nospace-variant changes move
nothing on real traffic, and the Location-header rule touches
no capture (captures are final responses, not bare redirects).
Same artifact as Waves 13–15 (not a regression):
`validation/wave7/captures/careerjet.json` reads OPEN because
the JSON record carries an empty body (the real HTML lives in
`careerjet.html`, which classifies CHALLENGED / Cloudflare
exactly as Wave 7 established).

## Leg B — residual edge, ledgered not fixed

- **Captcha tokens split across SCRIPT boundaries:** the
  nospace variant derives from the script-stripped body, so a
  "captcha" token split with one half inside a script block
  and one half in body text is still unscanned. No live capture
  or battery shape shows this species (captcha tokens travel
  in class names and URLs, not split prose), and fixing it
  would require scanning script content — which W14-001
  forbids for good reason. Revisit if a live capture shows it.

## Leg A (round-12 reclassification) — see STABILITY-11.md

## Leg C (adopter spot-check) — see ADOPTER-SPOT.md

Spot-check runner incident (caught before any conclusion): the
first script version read `r["body"]` from `probe_url`, which
returns no body field — all four first-run "body is not JSON"
readings were the runner's artifact, not adopter changes.
Fixed to `audit.fetch_raw` and re-run; the corrected results
were confirmed by a second independent fetch (x-prefix match
against Wave 7 for all four adopters).
