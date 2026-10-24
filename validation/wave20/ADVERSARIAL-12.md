# Wave 20 — Adversarial Battery v12: Results

39 shapes, hand-classified first in HANDCLASS-12.md, run against
the classifier in `tests/test_adversarial12.py`. **3 defect
families, all fixed test-first and generalized; corpus clean
(44 captures, zero diff vs the Wave 15 baseline); full suite
571/571 green** (532 pre-existing + 39 new).

## Defects fixed

- **W20-001 — iframe-src routing targets missed (M1d).** An
  <iframe> src to a login target on a content-free page read
  OPEN: no rule read iframe sources, so the page's only content
  — a frame routing to a login — named no gate. Fix, in the
  redirect-target family: iframe sources join meta refresh, JS
  location, Refresh header, Location header, and form actions
  as a routing species, under the same markers_count gate and
  the same login/challenge token rules. A frame to a content
  target stays routing (M1b); a frame on a served article stays
  furniture (M1c); a frame to a challenge target was already
  CHALLENGED via the captcha token and now also carries the
  redirect evidence (M1a). Fixtures: M1a/b/c/d.
- **W20-002 — localized JS-proof phrases missing (M2).** The
  JS_PROOF family was English-only: German, French, Spanish,
  Portuguese, and Japanese browser-verification stubs all read
  OPEN. Fix: five full interstitial sentences added to
  _JS_PROOF_PHRASES, gated like every phrase there (small
  pages; served-page mentions stay OPEN, M2f). The addition
  flows into the overlay/dialog windows and the body-wall-
  signal set with the English phrases, by construction.
  Fixtures: M2a/b/c/d/e + pin M2f.
- **W20-003 — localized human-check languages missing (M3).**
  Ukrainian, Hindi, Malay, Tagalog, and Swahili challenge
  phrases were not in the localized list; all five read OPEN.
  Fix: added to _LOCALIZED_HUMAN_CHECK, gated like every
  generic marker. Fragments compose nothing (M3g) and served-
  page mentions stay OPEN (M3f). Fixtures: M3a/b/c/d/e + pins
  M3f/g.

## Hand-correction (discipline working, not a flipped test)

- **M4a/M4d.** The first draft hand-classified "Please verify
  your identity to continue" as CHALLENGED. On reflection
  that demand is auth-ambiguous: it describes account-recovery
  and identity-proofing flows as readily as bot gates — the
  same reason Wave 11 deliberately excluded "verification in
  progress" from the JS_PROOF list. Without a challenge or
  vendor signal, the classifier's conservative OPEN claims no
  wall, and adding the phrase would misfire on auth-recovery
  pages the auth-form branches are designed to catch. The
  hand classification was corrected to OPEN before any fix
  landed; M4b (login URL → LOGIN_GATED) and M4c (article
  mention → OPEN) stand as pins. The boundary is documented
  here so a future wave can re-challenge it with evidence,
  not by re-asserting the phrase.

## Pins (no defect — the classifier was already right)

- **M5a/M5b (iframe title attributes).** Title text IS page
  text (Wave 14, F2): the attribute fires on a content-free
  page and yields to the served-page gate on an article.
- **M6a/M6b (overlay/dialog on 403).** The generic branch
  covers error statuses: a modal challenge on a 403 is a
  challenge, not a refusal.
- **M7a–M7e (audit edges).** Named-agent carve-outs hold
  regardless of group order (M7a); a sitemapindex with locs is
  a usable sitemap document (M7b); an empty-target llms link
  names no index entry (M7c); BOM + CR-only endings +
  frontmatter compose to a PASS (M7d); a wildcard Allow with a
  path Disallow reads restricted, not blocked (M7e).
- **M8a–M8e (precedence).** Fired walls precede 401/429/503;
  generic evidence yields to an identified login page; a meta
  refresh to a challenge on a login page keeps the challenge
  (the redirect species has no login exclusion).
- **M9a/M9b/M9c (inline content, accessible names).**
  <details> is inline content, not a modal (M9a); an
  interactive element's aria-label IS presented text (M9b)
  and yields to the served-page gate (M9c).
- **M10a (JSON captcha error).** A document whose whole
  content is a captcha demand is a presented challenge.

## Corpus regression

All 44 stored captures replayed through the Wave 20-fixed
classifier (`validation/wave15/corpus_check.py` output vs
Wave 15's `corpus-after.txt`): **diff is empty.** The iframe
rule, the localized phrases, and the language additions touch
no capture.

## Verification

- Full suite: **571/571 green** (532 pre-existing + 39 new).
- MCP smoke: all three tools pass live (`scripts/smoke_mcp.py`:
  initialize, tools/list `['probe_url', 'classify', 'audit']`,
  classify → CHALLENGED / Cloudflare, probe_url(example.com) →
  OPEN 200, audit(example.com) → F 3/12).
- Every Wave 20 JSON re-read and parsed; no 0-byte files.
