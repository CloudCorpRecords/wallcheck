# wallcheck: Changelog

## Unreleased

- The exposure layer lands as a capability, not just a script: the
  pattern table and classifier moved into a pure library
  (`src/wallcheck/exposure.py`) shared by the sweep script, the
  capture scrubber, the probe and the server. `probe_url` gains an
  opt-in `include_exposure`, the MCP server gains a fourth tool
  (`scan_exposure`, one honest GET), and the CLI gains
  `wallcheck probe --exposure`. Findings stay fingerprint-only.
  Method and disclosure rules: campaign/EXPOSURE-LAYER.md.
- `scripts/scrub_captures.py` rewritten on the shared table: it now
  redacts every class the scanner can find — all candidate classes
  (live secret keys, platform tokens, private-key blocks including
  the PEM body, credentialed DB URLs, secret JSON fields, JWTs)
  plus the public classes other scanners flag — replacing only the
  captured value with a REDACTED-<PATTERN> marker, idempotently.
  Previously it covered 3 patterns and would have passed most
  candidate classes straight into a published capture.
- `.gitignore` now protects private disclosure material:
  `validation/monster-finding/` (a live finding under a
  responsible-disclosure hold) and `validation/exposure-wave*/`
  (candidate findings naming companies not yet contacted) can
  never enter the repository by accident.
- CI: a tests workflow now runs the Python unittest suite and the
  Node launcher tests on push and pull_request; previously the
  Python suite ran nowhere automatically.

## 0.5.0: 2026-10-24 (stamped final at the ship-readiness pass; published 2026-10-24 on Rene's ship call)

The audit release, hardened by nineteen waves of adversarial
testing after the release candidate.

- The owner-side `audit` joins the MCP server as a third tool
  (probe_url, classify, audit), with a stated, tested fetch
  budget of at most 10 honest GETs per call.
- The Bot Wall Index stands at 500 sites with 24 stability
  rounds behind it; the signed-agent directory census measures
  4 adopters in 500.
- Waves 10-28 folded in: twenty adversarial batteries and
  hundreds of capture-built fixtures fixed every defect family
  they found, test-first: among them the deliberate-refusal
  status family (444/451/418/402), split-phrase and
  split-markup challenge text, auth-prompt species (code entry,
  passkey, magic link, delivery code, email-continue,
  authenticator app, SSO, push approval, employee ID, badge
  tap, QR, biometric, Windows PIN), localized human-check
  phrases in 59 language groups, ARIA modal challenges, and
  gzip/encoding correctness in the audit's sitemap and llms
  checks. Suite: 885 tests, all green.
- Release candidate stamped at Wave 9; 0.5.0 was never
  published in rc form, so the Waves 10-28 fixes fold directly
  into this final stamp. Shipped 2026-10-24 on Rene's
  explicit call.

## 0.4.0: Wave 4

- Ed25519 signing in pure-Python stdlib (RFC 8032, verified
  against the official test vectors): keys are now Web Bot
  Auth directory-compatible, removing the v0.2 standards
  blocker.
- Second signed-agent directory census; four vendor report
  cards (Cloudflare, PerimeterX, DataDome, Akamai; Imperva
  followed).

## 0.3.0: Wave 3

- `wallcheck audit <domain>`: the owner-side audit: six
  checks (robots, llms, sitemap, feed, api, signed agents)
  graded A-F with evidence and fixes.
- AWS WAF named as a vendor; index grown to 154 sites.

## 0.2.0: Wave 2

- Signed agent identity (prototype): RFC 9421 HTTP Message
  Signatures with `tag="web-bot-auth"` (HMAC-SHA256),
  `wallcheck keygen`, `probe --sign`, and a verify-server for
  owners to test their side.
- Login/API path probing: sanctioned machine routes measured
  separately from the marketing surface.

## 0.1.0: Wave 1

- First build: deterministic probe + classifier (CLI and
  stdio MCP server), Python standard library only. Verdicts
  OPEN / CHALLENGED / WALLED / LOGIN_GATED / RATE_LIMITED /
  UNREACHABLE; vendors Cloudflare, PerimeterX, DataDome,
  Akamai, Imperva.
- The 58-site seed census that became the Bot Wall Index.
