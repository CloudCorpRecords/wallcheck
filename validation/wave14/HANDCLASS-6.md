# Wave 14 — Adversarial Battery v6: Hand Classifications

Discipline (as Waves 6, 10, 11, 12, 13): every shape below was classified
BY HAND against SPEC's verdict definitions BEFORE the classifier was
allowed to see it. All shapes are NEW relative to Wave 6 (S1–S6),
Wave 10 (B1–B10), Wave 11 (C1–C8), Wave 12 (D1–D9), and Wave 13
(E1–E10): no repeats of image mechanisms, noscript forms, title-only
wording, challenge-cookie + served content, robots all-vs-one agent,
title-only llms, one-URL sitemaps, multi-hop chains to login,
comment-only markers, or mixed-case markers. Any mismatch is a defect
candidate: fix generalized with a capture-built fixture, or ledger it
as a genuine honest limitation with the reason. No silent passes, no
per-shape special cases.

Reference — SPEC verdicts: OPEN = the resource was served; CHALLENGED =
an interactive human-verification challenge was presented; WALLED = a
hard block page, no challenge offered; LOGIN_GATED = content exists
behind authentication; RATE_LIMITED = a throttle (HTTP 429, or a timed
refusal carrying a Retry-After header and throttle wording — see F4);
UNREACHABLE = the fetch itself failed. Audit grades: PASS / WARN / FAIL
per check.

## F1 — challenge markers ONLY inside <script> JSON blobs (classifier)

The classifier scans the raw body, so a marker inside a script block
reads exactly like a marker in prose. The question is whether it
SHOULD: a JSON blob can be a challenge declaration (the page's only
content) or configuration for the page's own form (presence, the Wave 1
GitHub-widget principle — a captcha that gates form submission, not
reading, is not a challenge presented to the reader).

- **F1a** — 200, small page, only content
  `<script type="application/json">{"wall":{"type":"captcha","action":"verify"}}</script>`,
  no visible text at all. → **CHALLENGED / Generic**. The blob IS
  the page's content: a challenge declaration with nothing else.
  Predicted: classifier agrees (raw scan reads "captcha").
- **F1b** — 200, small page, a real visible paragraph ("Our team
  ships every Friday…") PLUS a script JSON blob
  `{"form":{"captcha":true,"sitekey":"abc"}}` configuring the page's
  own contact form. → **OPEN**. The visible content is served; the
  blob is form configuration, not a presented challenge — the captcha
  gates submitting the form, not reading the page. Predicted gap:
  the raw-body scan reads "captcha" in the blob and answers
  CHALLENGED, because it cannot tell configuration JSON from
  challenge JSON.
- **F1c** — 200, 20 KB article, script JSON blob with captcha form
  config. → **OPEN**. Pin: the served-page gate already handles
  this (large pages don't fire generic markers).
- **F1d** — 200, small page, script JSON captcha config + only a
  spinner div (no visible text). → **CHALLENGED / Generic**. Pin
  (F1a species): with no visible content, the blob is the page —
  the F1b suppression must not fire on content-free pages.

## F2 — challenge text ONLY in image alt attributes (classifier)

E1c covered the `title` attribute; alt text is the same mechanism in
the attribute the task names (alt is what a reader — human or agent —
gets when the image itself carries no text).

- **F2a** — 403, small page, only content
  `<img src="/img/x.png" alt="Please verify you are human">`. →
  **CHALLENGED / Generic**. Attribute text is page text; with no
  other content, the alt text IS the challenge.
- **F2b** — 403, small page, only content
  `<img src="/img/x.png" alt="Access denied">`. → **WALLED, vendor
  none**. Pin (E1b species): alt text with no challenge signal is
  a refusal, not a challenge.
- **F2c** — 200, 20 KB article, an image whose alt text reads
  "verify you are human" (an article image about verification). →
  **OPEN**. Pin: the served-page gate — attribute text on a real
  article is content about checks, not a check.

## F3 — "unusual traffic" / "suspicious activity" phrasing (classifier)

Traffic-anomaly wording is the oldest challenge-adjacent phrasing on
the web (Google's "unusual traffic" page). Standing alone it is a
refusal statement; paired with a verification demand it is a
challenge. The classifier currently has no rule for either half.

- **F3a** — 403, small page, "Access denied: unusual traffic
  detected from your network." No verification demand anywhere. →
  **WALLED, vendor none**. Pin: a refusal statement with no
  challenge offered is a wall; the phrase alone must not promote
  a bare 403 to CHALLENGED.
- **F3b** — 200, small page, "Unusual traffic detected. Complete
  verification to continue." → **CHALLENGED / Generic**. The
  anomaly wording PLUS a verification demand is a presented
  challenge. Predicted gap: no current marker fires ("verification"
  alone is not in any list), so the classifier reads OPEN.
- **F3c** — 200, 20 KB article about unusual-traffic detection,
  mentioning verification throughout. → **OPEN**. Pin: the
  served-page gate — an article about traffic checks is content.
- **F3d** — 403, small page, "Suspicious activity detected. Your
  account has been suspended." No verification demand. → **WALLED,
  vendor none**. Pin (F3a species): anomaly wording without a
  verification cue stays a refusal.

## F4 — rate-limit pages carrying Retry-After (classifier)

SPEC's RATE_LIMITED is "HTTP 429 without a stronger wall signal".
The boundary question: a timed, explicitly retryable refusal on a
non-429 status — is it a throttle (retry later) or a wall (blocked)?
The Retry-After header is the server's own statement that the
refusal expires; throttle wording ("too many requests") is the
server's statement of cause. Both together, with no wall signal,
describe a throttle, not a wall. Either alone does not.

- **F4a** — 429, header `Retry-After: 60`, body "Too many requests.
  Try again later." → **RATE_LIMITED**. Pin: the classic case.
- **F4b** — 429, header `Retry-After: 60`, body "Too many requests.
  Please verify you are human to continue." → **CHALLENGED /
  Generic**. Pin: a challenge dominates a throttle — waiting does
  not clear it, verifying does.
- **F4c** — 403, header `Retry-After: 120`, body "Too many requests
  from your IP. Please retry after 120 seconds." → **RATE_LIMITED**.
  A timed IP throttle with a stated retry time is a throttle, not a
  wall: nothing is challenged, nothing is permanently refused.
  Predicted gap: the classifier's bare-403 rule answers WALLED —
  it never looks at Retry-After.
- **F4d** — 503, header `Retry-After: 60`, body "Too many requests,
  please retry in 60 seconds." → **RATE_LIMITED**. Same rule as
  F4c in 503 form: the server says "too many" and "retry after",
  which is throttle semantics, not origin failure. Predicted gap:
  the 5xx branch answers UNREACHABLE.
- **F4e** — 503, header `Retry-After: 60`, body "Service
  temporarily unavailable." No throttle wording. → **UNREACHABLE**.
  Pin (boundary): overload wording without a throttle cause stays
  a server failure — Retry-After alone does not convert a 503
  into a throttle verdict.
- **F4f** — 403, header `Retry-After: 120`, body "Access denied."
  No throttle wording. → **WALLED, vendor none**. Pin (boundary):
  a header alone does not convert a refusal — cause wording is
  required, or every timed block would read as a throttle.

## F5 — login walls served 200 with a session-challenge cookie (classifier)

A login page carrying a challenge/session cookie: does the cookie
change the verdict? No — cookies are session machinery, and the
login heuristic already owns served login pages. What matters is
that no cookie name or session signal promotes a login page into a
challenge, and no cookie demotes it into served content.

- **F5a** — 200, /login, Set-Cookie `challenge_token=abc; Path=/`,
  sign-in form. → **LOGIN_GATED**. Pin: cookie names are not
  classifier signals; the served login page owns the verdict.
- **F5b** — 200, /login, Set-Cookie `_pxvid=abc` (PerimeterX
  sensor), sign-in form. → **LOGIN_GATED**. Pin (E4a species on a
  login page): a sensor cookie is presence, not a wall.
- **F5c** — 200, /login, Set-Cookie `datadome=abc` (DataDome
  session cookie), sign-in form. → **LOGIN_GATED / DataDome**.
  Pin (Wave 6 S5b / merrilledge precedent): vendor attribution
  stands on served login pages — the cookie says whose
  infrastructure served the gate; the verdict says the gate is
  auth.
- **F5d** — 200, /login, Set-Cookie `incap_ses=abc` (Imperva
  session cookie), sign-in form. → **LOGIN_GATED / Imperva**.
  Pin (same precedent as F5c).

Limitation recorded, not a shape: login detection remains URL-based
(status + final/chain URLs). A served page whose ONLY login signal
is a sign-in form plus a challenge cookie — no login path anywhere
— reads OPEN, because form-text detection would false-positive on
every page carrying a "sign in" link. That is an accepted boundary,
not a defect: the classifier's contract is URL + status + headers +
body wall-markers, and a form is not a wall marker.

## F6 — robots.txt Sitemap: lines pointing to sitemap index files (audit tool)

The audit fetches /sitemap.xml first and only consults the
robots-declared Sitemap: URL when /sitemap.xml is not 200 — and
only the FIRST declared line. Two gaps follow: a 200-but-not-XML
/sitemap.xml (an HTML error page) hides a valid declared index,
and a dead first declaration hides a valid second one. The site's
grade should reflect the sitemap it actually publishes, via any
declared line, in order.

- **F6a** — /sitemap.xml answers 200 with an HTML error page;
  robots.txt declares `Sitemap: https://x.example/sitemap-index.xml`,
  which serves a valid `<sitemapindex>` document. → **PASS**.
  Predicted gap: audit_site never tries the declared URL because
  /sitemap.xml was 200.
- **F6b** — /sitemap.xml 404; robots.txt declares two Sitemap:
  lines, the first 404, the second a valid `<urlset>`. →
  **PASS**. Predicted gap: audit_site tries only declared[0].
- **F6c** — /sitemap.xml 404; the one declared sitemap 404s. →
  **WARN**. Pin: no sitemap anywhere is WARN, not FAIL.
- **F6d** — /sitemap.xml itself is a `<sitemapindex>` document. →
  **PASS**. Pin (E7b species at the default location).

## F7 — llms.txt with only relative links (audit tool)

E6b pinned a minimal linked file (one relative link) as PASS. The
new ground is what counts as a link: a markdown link whose target is
a pure fragment (`#section`) points at the llms.txt document itself,
not at site content — it is a table of contents for a file that
indexes nothing. And a bare domain mention without scheme, slash,
or link syntax points nowhere clickable.

- **F7a** — /llms.txt with several relative links only
  (`- [A](/a)`, `- [B](/b)`, `- [C](/c)`), no absolute URLs. →
  **PASS**. Pin (E6b extended): relative links are real index
  entries; absolute URLs are not required.
- **F7b** — /llms.txt mixing relative links and absolute URLs. →
  **PASS**. Pin.
- **F7c** — /llms.txt containing ONLY fragment links
  (`- [Intro](#intro)`, `- [Setup](#setup)`). → **WARN**
  (LLMS_STUB family). The file points at itself, not at the site.
  Predicted gap: the markdown-link regex counts any
  `[text](target)`, fragments included, so the file reads PASS.
- **F7d** — /llms.txt body "See example.com for details." (bare
  domain, no scheme, no slash, no link syntax). → **WARN**
  (LLMS_STUB). Pin: a domain mention that is not a link, URL, or
  path points nowhere an agent can follow.

## F8 — walls appearing ONLY in an intermediate redirect hop (classifier)

The probe records hop URLs, not hop bodies or hop statuses: the
classifier's chain input is a list of URLs. A hop that served a
wall body but still redirected cannot have blocked the agent — had
it blocked, the chain would end at the wall and the final response
would BE the wall. The verdict describes the final resource.

- **F8a** — chain [site → /challenge → /home], final 200 clean
  article. → **OPEN**. Pin: a challenge-URL hop that resolves to
  clean content is routing, not a wall — the agent read the
  resource.
- **F8b** — chain [site → /verify-captcha → /home], final 200
  clean article. → **OPEN**. Pin: hop URL tokens are not wall
  signals; only the final response and login-ness of chain URLs
  are inputs.
- **F8c** — chain [site → /login], final 200 login page. →
  **LOGIN_GATED**. Pin: the chain login check (a login hop that
  lands on a login page is a gate, like a login final).

Design boundary, not a defect: hop bodies are not classifier inputs
by construction. If a hop wall ever mattered — i.e. it stopped the
fetch — the probe would return the wall as the final response and
classify it there. No fixture can show a hop wall that both blocked
and did not block.
