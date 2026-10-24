# Adversarial battery v19 — Wave 27 (Leg B)

43 shapes in `tests/test_adversarial19.py`, hand-classified
first in `validation/wave27/HANDCLASS-19.md` (written before any
test ran). Scope per the wave brief: challenge markers appearing
only in table cells of an otherwise served page (V1); the wall
as an HTTP 307 redirect to a maintenance page (V2 — narrowed at
hand-class time: Wave 16's H4 battery already pinned 307 →
login and 307 → challenge compositions, so only the
maintenance target is new ground); login walls with a "use your
fingerprint" biometric prompt, worded distinctly from passkey
prompts (V3); robots.txt product-token groups carrying a
version (V4); llms.txt files whose only links live inside an
HTML comment (V5); sitemap.xml files whose `<loc>` entries are
IP literals (V6); challenge phrases in eight languages verified
absent from every earlier phrase list — Albanian, Icelandic,
Kazakh, Malayalam (V7); and the challenge presented as a toast
notification over otherwise real content (V8). Every V7 phrase
and every biometric wording was grep-verified ABSENT from
classify.py before the hand-class was written.

**First run: 15 failures, 28 passes.** The 15 failures are
exactly the HANDCLASS-19 gap predictions — V3a, V4b–V4e, V5a,
V5c, V7a–V7h — and there were no surprises: every shape the
hand-class predicted would pass, passed, including all of V1,
V2, V6, and V8 and every negative-carrier guard. After the
four fixes below: **43/43 pass**, and the full suite stands at
**831/831 via pytest** (788 carried in + 43 new), with the
capture corpus regression clean (44 corpus captures, diff empty
against `validation/wave15/corpus-after.txt`).

## The four defect families (all fixed; details in PROBLEMS.md)

- **W27-V3 — biometric sign-in prompts missed.** A served-size
  login page whose only auth step was "Use your fingerprint to
  sign in" read OPEN: the Wave 16–18 machinery-passkey family
  keys on passkey wording, and a fingerprint prompt is a
  different string. Fixed with the two-keyed rule every signal
  family since Wave 17 carries from birth (`_is_biometric_prompt`
  + `BIOMETRIC_PROMPT` evidence, visible-text gated, served-page
  size gated, vendor machinery not required — the fingerprint
  prompt IS the barrier). Prose uses of the same wording without
  presented machinery stay OPEN (V3b is the cautionary pin, and
  it passes only because the two-key structure demands the
  machinery) — the prose-without-machinery boundary is ledgered
  in the code comment as limitation-by-design, the same terms
  the Wave 16 residual edge accepted.
- **W27-V4 — versioned robots product tokens missed their
  group.** `User-agent: wallcheck/1.0` built a group named
  `wallcheck/1.0` that never matched the agent `wallcheck`, so
  a Disallow-all aimed at this crawler graded PASS. RFC 9309's
  producttoken is `identifier ["/" version]` — the version is
  metadata about the token, not part of its name. Fixed in
  `parse_robots`: the group key is the identifier before the
  first `/`. Bare tokens are byte-for-byte unchanged (verified:
  no earlier test anywhere puts "/" in a UA value), and a token
  that is only a version string names no agent and is ignored.
- **W27-V5 — llms.txt links inside HTML comments counted.**
  A file whose only link lived inside `<!-- ... -->` graded
  the file real. The classifier has stripped HTML comments
  since Wave 19 (the template-block rule); the llms checker
  never did. Fixed: `_check_llms` strips comments immediately
  after the frontmatter strip, before every content test. One
  evidence-label note: V5a's hand-class named the expected
  warning `LLMS_STUB`, but a file reduced to bare prose by the
  strip actually lands on `EMPTY_BODY` — same WARN grade, same
  defect, different label; the pin records the label the code
  produces and this note records the discrepancy rather than
  smoothing it.
- **W27-V7 — eight localized human-check phrases missed.**
  Albanian, Icelandic, Kazakh, and Malayalam joins of the
  demand and checkbox patterns read OPEN. Added to
  `_LOCALIZED_HUMAN_CHECK` with the established collision
  discipline (each string grep-distinct from every existing
  list entry; Kazakh's checkbox wording differs from its
  Russian near-twin by the language-specific `емес`).

## What held without a fix

- **V1 (table cells).** A challenge phrase that exists only
  inside `<th>`/`<td>` cells of a data table on a fully served
  page is page content, not a challenge — the visible-text
  layer reads table text as content and the verdict stays OPEN
  until the phrase is joined by vendor machinery (V1d) or a
  sized challenge stub (V1e). No new rule was needed; the
  battery pins the behavior so a future text-scan widening
  cannot quietly turn documentation tables into walls.
- **V2 (307 → maintenance).** A 307 to a maintenance page reads
  OPEN / MAINTENANCE: the Wave 6 maintenance composition
  already follows the chain and classifies the final page.
  Compositions to a challenge (WALLED) and a login page
  (LOGIN_GATED) on the same status were pinned by Wave 16's
  H4; v19 adds only the maintenance cells.
- **V6 (IP-literal sitemap locs).** IPv4, IPv6 (bracketed and
  bare), and IP-with-port locs all count as sitemap entries —
  a sitemap of intranet or staging hosts is unusual, not
  unusable — while an IP as the document host stays rejected
  under the K6 host doctrine. No fix; pinned.
- **V8 (toast notifications).** A toast saying "verifying your
  browser" over a fully served page does not wall it: with no
  vendor machinery and a full page served, the toast is a
  notification, not a barrier (V8a/V8b stay OPEN); the same
  toast over a challenge-sized stub with machinery is
  CHALLENGED (V8c/V8d). The toast wording itself earns no new
  signal — it is the page geometry that decides, which is the
  doctrine every battery since v2 has enforced.

## Discipline notes

- Every mismatch was checked against older pins before any
  fix: no "/" in any earlier robots UA value (grep over all
  eighteen earlier test files), the Wave 16 H4 compositions
  narrowed V2 before a test was written, and V3's machinery
  vocabulary was checked against the passkey, badge-tap, and
  QR families for collisions.
- The four new signals were born with the Wave 17–26 pattern:
  two-keyed (signal AND machinery), visible-text gated,
  served-page size gated, and each carries negative fixtures
  on asset-filename / script-identifier / stylesheet-class
  carriers (V3d–V3f) plus prose and documentation carriers
  (V3b, V3g).
- No per-site special cases; every fix is a general rule.
  HANDCLASS-19's V2e/V2f fixtures were dropped before the
  battery was written because Wave 16 had already pinned those
  compositions — the battery does not re-test settled ground
  and call it new coverage.
