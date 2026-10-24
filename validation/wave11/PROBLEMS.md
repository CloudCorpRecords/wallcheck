# Wave 11 — Problems ledger

## Leg B (adversarial battery v3) — 6 defects, all fixed

- **W11-001** (classifier, fixed): form-action redirect to a
  challenge read OPEN. Fix: form actions join the redirect-target
  rule, gated to served (2xx) small pages. Fixture:
  test_c1b_form_action_to_challenge.
- **W11-002** (classifier, fixed): "verify your request" stub read
  OPEN. Fix: "verify your request" / "verifying your request"
  join the JS_PROOF phrase list ("verification in progress"
  deliberately excluded — it also describes account-email flows).
  Fixture: test_c1c_verify_your_request_stub.
- **W11-003** (classifier, fixed): Turnstile widget on a login form
  read CHALLENGED. Fix: a challenge-platform loader as the ONLY
  Cloudflare signal on an identified login page yields to the
  login verdict (careerjet non-login case and Just-a-moment-at-
  login case both unchanged). Fixture:
  test_c2c_turnstile_on_login_form_yields.
- **W11-004** (classifier, fixed): Italian, Dutch, Korean challenge
  pages read WALLED (bare-403 fall-through). Fix: localized
  phrase list gains IT, NL, KO. Fixtures: test_c4b/c/d.
- **W11-005** (classifier, fixed): LOGIN_GATED verdict carried a
  Generic vendor (hCaptcha widget + prose on a login form). Fix:
  a LOGIN_GATED verdict with a Generic-only vendor is nulled
  (named-vendor presence untouched). Fixture:
  test_c6b_hcaptcha_widget_plus_prose_on_login.
- **W11-006** (audit tool, fixed): robots wildcard block with a
  named-agent carve-out read FAIL. Fix: FAIL means every tracked
  agent is blocked; a carve-out drops to WARN. Fixtures:
  test_c8b/c/g.

All fixes generalized (no per-shape or per-site special cases) and
regression-checked against the full suite (183/183) and the 44
real-capture corpus (zero verdict/vendor changes).

## Leg B — honest limitations (pins, not defects)

- **C1a**: a reload-timer-only empty page reads OPEN — no
  deterministic signal exists (the Wave 3 boundary, re-affirmed).
- **C3b**: a textless SVG graphic on a 403 reads WALLED, vendor
  none — pixels with no text carry no verdict-driving signal.
- **C5b**: an unknown vendor's header (Sucuri) is not claimed —
  a synthetic header alone does not earn a vendor rule; a live
  capture of its wall page would.

## Leg C (regression) — no regression

Full suite 183/183 (152 prior + 31 new battery pins); MCP smoke
passes on all three tools (probe_url, classify, audit); spot
re-audit of hub.docker.com, huggingface.co, typeform.com all hold
at C 7/12 — correctly unchanged, since none serves the new-gate
error documents (see REGRESSION.md).

## Leg A (round-7 reclassification) — pending runner completion

See STABILITY-6.md when the round-7 runner finishes. NOTE: Leg B
fixes landed AFTER the round-7 runner started (it imports its
modules once at start), so round 7 measures the Wave 10-fixed
classifier — which is exactly what the task specified (the
fix-driven reclassification Wave 10 deferred). The Wave 11 fixes
will be measured by the next round.
