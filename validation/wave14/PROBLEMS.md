# Wave 14 — Problems ledger

## Leg B (adversarial battery v6) — 5 defects, all fixed

- **W14-001** (classifier, fixed): generic markers appearing only
  inside `<script>` JSON blobs drove verdicts (F1b: a form's
  captcha config on a page with real visible text read
  CHALLENGED). Fix: script-only generic markers (captcha,
  human-check prose, JS-proof phrases) are suppressed when the
  page has visible text (≥20 chars after stripping head/script/
  style/tags); content-free pages still fire. Vendor markers and
  redirect targets are untouched — loader scripts and JS
  location assignments stay load-bearing. Fixtures:
  test_f1b_form_config_blob_with_visible_text, the two
  threshold guards, test_guard_script_only_js_proof_suppressed.
- **W14-002** (classifier, fixed): "Unusual traffic detected.
  Complete verification to continue." read OPEN — no rule
  covered traffic-anomaly wording. Fix: TRAFFIC_CHECK evidence —
  (unusual traffic OR suspicious activity) AND a verification
  cue (verif/captcha/prove/confirm) reads CHALLENGED / Generic,
  wired through the vendor rule, wall-signal precedence, and
  the generic verdict branch. Either half alone does not fire
  (F3a/F3d pins). Fixtures: test_f3b, test_guard_traffic_plus_
  captcha_cue.
- **W14-003** (classifier, fixed): timed throttles on non-429
  statuses misread (F4c: 403 + Retry-After + "too many requests"
  read WALLED; F4d: 503 + Retry-After + throttle wording read
  UNREACHABLE). Fix: Retry-After header + throttle wording
  ("too many requests", rate-limit phrasing, "slow down",
  "request limit exceeded") + no wall signal reads RATE_LIMITED
  on 403/503, placed after the wall/challenge branches and
  before the bare-403 rule. Header alone and overload wording
  alone do not convert (F4e/F4f pins); a fired wall with a
  Retry-After header stays a wall (guard pin). Fixtures:
  test_f4c_403_timed_throttle, test_f4d_503_timed_throttle.
- **W14-004** (audit fetch logic, fixed): audit_site consulted
  robots-declared Sitemap: URLs only when /sitemap.xml was not
  200, and only the first declared line (F6a: a 200-HTML
  /sitemap.xml hid a valid declared index; F6b: a dead first
  declaration hid a valid second). Fix: fall through the
  declared lines in order until a usable sitemap document
  serves (200 + urlset/sitemapindex/XML prolog, the same test
  the check grades on); a declared URL serving HTML is not
  accepted. Fixtures: test_f6a, test_f6b, the declared-HTML
  guard. Note: this is the first battery defect in fetch logic
  rather than grading logic — future audit shapes should run
  through audit_site, not just evaluate_audit.
- **W14-005** (audit tool, fixed): fragment-only markdown links
  in llms.txt counted as index entries (F7c: `- [Intro](#intro)`
  read PASS). Fix: a markdown link counts only when its target
  is non-empty and not a pure fragment; empty targets do not
  count. Fixtures: test_f7c, test_guard_empty_link_target.

## Leg B — correction, not a defect

- **F5c fixture corrected** (LOGIN_GATED, None → LOGIN_GATED,
  DataDome): the first draft set `datadome=abc` as the cookie,
  which no rule recognizes; the pinned DataDome cookie signal
  is `dd_cookie` (test_b8c). With the correct name the
  classifier answers exactly as hand-classified. No new cookie
  signal invented.

## Leg B — corpus regression (done)

44 stored captures replayed through the Wave 14-fixed classifier
(`validation/wave14/corpus_check.py`, `corpus-after.txt`). Zero
regressions: every real wall capture reads as its wave
established — ebay/guru/medium WALLED with vendors,
monster/nytimes CHALLENGED / DataDome, npmjs CHALLENGED /
Cloudflare, amazon CHALLENGED / Generic, booking AWS WAF, chewy
Kasada RATE_LIMITED, delta Akamai 444, w3schools/hilton Akamai,
redfin AWS CloudFront, ed.gov Azure WAF, duolingo OPEN (the
Wave 5 false-challenge fix holds), hyatt/state/catho/haaretz
WALLED vendor None (corroborating Leg C's unattributed-bare-403
finding from live captures). The script-only suppression
(W14-001) moved nothing: no real capture's wall signal lives
only in a script block on a page with visible text — real
interstitials carry visible challenge text or no visible text,
exactly as the fix assumes. One artifact, not a regression:
`validation/wave7/captures/careerjet.json` reads OPEN because
the JSON record carries an empty body (the real 10,937-byte
HTML lives in `careerjet.html`, which classifies CHALLENGED /
Cloudflare exactly as Wave 7 established).

## Leg A (round-10 reclassification) — done, zero fix-driven moves

Round 10 probed the full 499-row index with the Wave 13-fixed
classifier (see STABILITY-9.md for the full incident log: a
sed-trapped resume check that probed nothing, a contaminated
launch under the Wave 14-fixed tree whose 41 lines were killed
and purged, and the clean launch after a backup/revert/restore
cycle). Three diffs, all hand-checked with fresh captures
classified by a Wave 13-tree copy: britishairways.com HELD at
OPEN (round-10 transport failure vs two agreeing fresh served
readings), kaiserpermanente.org HELD at OPEN/302 (two agreeing
fresh redirects vs a round-10 200 routing variant), todoist.com
MERGED to OPEN (round-10 plus two agreeing fresh served
readings retire a transport failure). Zero fix-driven moves —
the fourth consecutive round (Waves 11, 12, 13, 14) in which no
measured fix moved a live row. The five battery defects above
already disqualify Wave 14 as a clean wave regardless of Leg
A's clean sheet — the saturation clock stays reset (see
OVERNIGHT.md).

## Leg C (vendor-attribution audit) — see VENDOR-AUDIT.md

Full check of all 60 WALLED/CHALLENGED rows against round-10
history + captures, not a spot-check.
