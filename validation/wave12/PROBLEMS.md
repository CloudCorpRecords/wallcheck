# Wave 12 — Problems ledger

## Leg B (adversarial battery v4) — 6 defects, all fixed

- **W12-001** (classifier, fixed): Polish, Turkish, Arabic,
  Chinese, and Russian challenge pages read WALLED (bare-403
  fall-through). Fix: localized phrase list gains two phrases per
  language (a "confirm you are not a robot" form + a "not a
  robot" form, matching the existing per-language style).
  Fixtures: test_d1a/b/c/d/e.
- **W12-002** (classifier, fixed): "Browser check in progress"
  stub read OPEN. Fix: "browser check" joins the JS_PROOF phrase
  list, gated to small pages like every phrase there (the D3b
  20 KB article pin proves the served-page gate holds).
  Fixture: test_d3a_browser_check_in_progress.
- **W12-003** (classifier, fixed): a login form whose action is
  a challenge endpoint read CHALLENGED. Fix: form-action targets
  get their own evidence code (FORM_ACTION_TO_CHALLENGE), and the
  verdict branch for that code yields to identified login pages
  — the form is the sign-in form and its action is the form's own
  submission endpoint (Wave 6 S5c), while meta-refresh / JS
  location targets keep REDIRECT_TO_CHALLENGE and its precedence.
  The split is the fix: one evidence code could not express two
  different yield rules. Fixtures: test_d5a (login yields),
  test_d5b (stub still CHALLENGED — guards the split).
- **W12-004** (audit tool, fixed): a JSON-LD document at /llms.txt
  read PASS ("served as genuine text"). Fix: a JSON body without
  an error key now reads WARN (JSON_NOT_LLMS) — machine-readable
  data in the wrong format at the llms.txt location. This refines
  the Wave 10 B9a stance without contradicting it: B9a said a
  non-error JSON body is "not failed here" — and it still is not
  failed; WARN is the middle grade between B9a's FAIL (error
  documents) and the old PASS. Fixture: test_d7c_jsonld_llms.
- **W12-005** (audit tool, fixed): a genuine markdown body served
  as Content-Type text/html read FAIL (SOFT_404_HTML). Fix: the
  llms check now carves out markdown bodies (a heading or link
  pattern, no HTML tags in the first kilobyte) before failing on
  the HTML gate — agents ingest the body, not the header. The
  carve-out is scoped to the llms check only; the shared HTML
  gate still catches real HTML bodies everywhere else (robots,
  api shells). Fixture: test_d7d_markdown_mislabeled_html.
- **W12-006** (audit tool, fixed): a gzip-compressed sitemap read
  WARN (binary garbage to the XML check). Fix: the audit fetcher
  now decompresses Content-Encoding: gzip bodies (stdlib gzip,
  decompressed output capped at BODY_CAP like any other sample,
  corrupt bodies fall back to raw bytes instead of crashing).
  Both the direct path and the robots-declaration fallback path
  pass after the fix. Fixtures: test_d8a/d8b (live localhost
  servers, not synthetic records).

All fixes generalized (no per-shape or per-site special cases) and
regression-checked against the full suite (210/210) and the real-
capture corpus (zero verdict/vendor changes).

## Leg B — pins (no defect)

- **D2a/D2b/D2c**: countdown interstitials behave exactly as the
  existing rules predict (content target → OPEN; form-action and
  refresh targets → CHALLENGED). A timer adds no wall signal.
- **D4a**: a consent gate that says out loud that it blocks
  content still reads OPEN — the Wave 10 B5b boundary holds under
  pressure.
- **D6a/D6b/D6c**: the Wave 11 robots FAIL semantics hold across
  two-carve-out, all-restricted, and all-blocked shapes.
- **D7a/D7b**: markdown and plain-text llms.txt pass as before.
- **D9a–D9d**: 3+ hop chains behave exactly as the final-answer
  rule predicts; chain length changes nothing.

## Leg A (round-8 reclassification) — zero fix-driven moves

See STABILITY-7.md. The Wave 11 fixes moved no live row; the two
merged moves are target-side oscillation (amazon interstitial,
britishairways timeouts) and the two held diffs are a known
transport pattern (npmjs) and a single uncorroborated edge deny
(webex). No new vendors, no new signals from live traffic.

## Leg C — no issues

Version hygiene: see VERSION-NOTE.md (conclusion: next stamp is
0.5.0 final, not 0.5.1-rc; no version files touched by this wave).
Signing spot-check: see SIGNED-SPOT.md (2/2 unchanged, self-
verify ok, tamper rejected).
