# wallcheck: SPEC

**Deterministic bot-wall transparency for agent builders.**
By Rene Turcios / CloudCorpRecords. Sibling of greenlight, mcpaudit, shipcheck.

**0.5.0 final (release candidate at Wave 9, stamped final at
the ship-readiness pass), hardened through Wave 28.** Not yet
published; the launch hold stands.
Launch-readiness memo: `campaign/LAUNCH-READINESS.md`.

## The problem

Agents die silently on bot walls. A fetch returns 403, a browser session
churns through environment after environment, an upload never starts: and
nothing in the pipeline can say *what* stopped it, *whose* wall it was, or
*show the evidence*. The failure looks identical to a network error, a bug
in your own code, or the site being down, so builders burn hours debugging
the wrong layer.

This is not hypothetical. On 2026-10-23, Cloudflare's wall on a single
major platform (Upwork) cycled a working browser session through roughly
ten environment replacements, broke every file-transfer grant bound to
those browsers, and cost hours on a task as basic as publishing two
portfolio drafts: while a human with the same account walked in through
the front door. The wall never identified itself to the agent in any
machine-readable way. The agent had receipts for everything except the
thing that actually stopped it.

wallcheck exists to name the wall, show the evidence, and make the result
repeatable: same response in, same verdict out, no LLM, no guessing.

## Non-goals (hard, permanent)

wallcheck will **never**:

- solve CAPTCHAs or any other human-verification challenge,
- spoof browser fingerprints, user agents, or TLS signatures,
- bypass, evade, or defeat a bot wall, rate limit, or access control,
- rotate proxies or identities to get around a block.

The probe identifies itself honestly (`wallcheck/<version>` user agent).
The combat is **detection + evidence + standards**: walls that are visible
and measured get fixed, exempted, or routed around through legitimate
channels (official APIs, signed agent identity, owner-side configuration).
A wall an agent can *name* is a bug report; a wall it can't is a mystery.

## v0.1 scope (this build)

### CLI

```
wallcheck probe <url> [--json] [--timeout SECONDS]
```

- Fetches the URL once, with an honest wallcheck user agent (no spoofing).
- Follows at most 5 redirects, recording the chain.
- Captures status, response headers, elapsed time, and a bounded body
  sample (64 KB): enough to identify a wall, never a content scraper.
- Classifies the result deterministically (below).
- Human output: verdict, vendor, evidence list. `--json`: one stable
  machine-readable object:
  `{url, final_url, status, verdict, vendor, evidence[], elapsed_ms,
  redirect_chain[]}`.
- Exit codes: `0` = OPEN, `1` = any other verdict, `2` = usage error.

### Verdicts

| verdict | meaning |
| --- | --- |
| `OPEN` | The resource was served. An agent can read it. |
| `CHALLENGED` | An interactive human-verification challenge was presented (e.g. Cloudflare "Just a moment", a CAPTCHA page). A non-interactive agent stops here. |
| `WALLED` | A hard block page was served (e.g. Cloudflare "Sorry, you have been blocked", a PerimeterX deny page, or a bare 403). No challenge is even offered. |
| `LOGIN_GATED` | The agent was redirected to (or served) a login wall: the content exists, but only behind authentication. |
| `RATE_LIMITED` | HTTP 429 without a stronger wall signal: or a 403/503 carrying a Retry-After header *and* throttle wording ("too many requests", rate-limit phrasing; Wave 14). Slow down; this is a throttle, not a wall. |
| `UNREACHABLE` | The fetch itself failed (DNS, TLS, connection, timeout) or the server returned 5xx. No wall verdict is claimed. |

### Deterministic classifier

The classifier is a pure function of `(status, headers, body_sample,
final_url, redirect_chain)`. Same input, same output, forever: which is
what makes recorded fixtures a complete test suite and Index scans
comparable across time.

`vendor` names the wall vendor *behind the verdict*: CDN presence
markers (e.g. `cf-ray` on a served page) are recorded as evidence but do
not name a vendor on an OPEN result, and when one vendor's challenge
fires behind another vendor's CDN, the challenging vendor is named.

Vendor detection (each with named evidence codes):

- **Cloudflare**: `cf-ray` header, `cf-mitigated: challenge`,
  `server: cloudflare`, body markers "Just a moment",
  `challenges.cloudflare.com`, "Sorry, you have been blocked".
- **PerimeterX**: `_px` cookies/markers, `px-captcha`, "PerimeterX"
  body markers, its deny-page wording.
- **DataDome**: `x-datadome` header, `datadome` body/cookie markers.
- **Akamai**: `ak_bmsc` cookie, `bm-verify` markers, the GHost
  server signature, and the `edgesuite` error-page reference
  (added Wave 3, W3-002).
- **Imperva**: Incapsula/Incapsula session cookies, `incap`
  resource markers (added Wave 1, W1-003/W1-004).
- **AWS WAF**: the `AwsWafIntegration` body token / `awswaf.com`
  challenge host (added Wave 3, W3-001; its JS token challenge is
  served as a small page, famously with status 202).
- **Microsoft Azure WAF**: the `azwaf` body token (its CSS
  namespace and `/.azwaf/captcha/` asset path) / "Azure WAF" page
  title (added Wave 5, W5-002; its JS/CAPTCHA challenge page is a
  challenge at any status, like AWS WAF's).
- **Kasada**: the `KPSDK` body token / `kasada` marker (added
  Wave 5, W5-003; recorded as evidence and attribution: a sensor
  payload is presence, never a verdict by itself; when the body
  is Kasada's stub behind another vendor's cookies, Kasada is
  named).
- **AWS CloudFront**: the generated block page: "The request
  could not be satisfied" *and* "Request blocked" (added Wave 5,
  W5-004; both lines required: the first alone is also
  CloudFront's origin-error wording). Attribution only.
- **Generic**: CAPTCHA / "verify you are human" / "not a robot"
  body markers with no vendor signature. The CAPTCHA marker scans
  the body with third-party widget *loader* references blanked
  (Wave 5, W5-001): a served page embedding a reCAPTCHA/hCaptcha
  loader for its own forms is presence, not a challenge. The
  blanking is deliberately narrow (loader hosts only): quoted
  captcha *references* elsewhere: a form action like
  /errors_page/validateCaptcha, a refresh target like /px/captcha/
 : are load-bearing challenge signals on pages with no other
  served content (Wave 6: Amazon's interstitial proves it), and a
  page whose whole content routes the client to a captcha is a
  CAPTCHA page by reference.
- **Generic (JS proof)**: `JS_PROOF` (added Wave 6): the
  vendor-neutral browser-verification stub: interstitial-voice
  phrasing ("verifying your browser", "checking your browser",
  "performing security verification", "please enable javascript
  to continue", …) on a non-served page. The species behind the
  AWS/Azure WAF stubs with the vendor tokens filed off; a JS
  proof the agent cannot perform is a challenge at any status.
  Served-page gated: real pages *about* walls, and SPA capability
  notes ("enable JavaScript to run this app"), are untouched.
  Wave 11 adds request-directed wording ("verify your request",
  "verifying your request"); "verification in progress" is
  deliberately excluded: it also describes account-email
  verification flows, a different gate. Wave 20 adds localized
  JS-proof phrasing (German, French, Spanish, Portuguese,
  Japanese browser-verification sentences) on the same principle
  as the localized human-check list below: a browser-verification
  stub is a challenge whatever language it is written in.
- **Generic (localized)**: the human-check scan also matches
  interstitial-voice phrasing in Spanish, German, French,
  Japanese, and Portuguese (added Wave 6), plus Italian, Dutch,
  and Korean (added Wave 11), plus Polish, Turkish, Arabic,
  Chinese, and Russian (added Wave 12), plus Swedish, Finnish,
  Danish, and Norwegian (added Wave 17), plus Brazilian
  Portuguese, Indonesian, Vietnamese, and Thai (added Wave 18),
  plus Hebrew, Persian, Urdu, and Bengali (added Wave 19), plus
  Ukrainian, Hindi, Malay, Tagalog, and Swahili (added Wave 20),
  plus Greek, Czech, Hungarian, and Romanian (added Wave 23),
  plus Bulgarian, Slovak, Croatian, and Slovenian (added Wave 24),
  plus Serbian, Macedonian, Latvian, and Lithuanian (added
  Wave 25), plus Catalan, Estonian, Armenian, and Georgian
  (added Wave 26), plus Albanian, Icelandic, Kazakh, and
  Malayalam (added Wave 27), plus Burmese, Sinhala, Amharic, and
  Azerbaijani (added Wave 28): challenge pages are not English-only;
  a localized challenge is a challenge, not a hard block.
- **Generic (script-only suppression)**: a generic marker
  (captcha, human-check prose, JS-proof phrase) appearing ONLY
  inside `<script>` blocks is configuration JSON, not page
  content: suppressed when the page has visible text (≥20
  chars after stripping head/script/style/tags; added Wave 14,
  W14-001). A content-free page (spinner, empty body) with a
  script-only marker still fires: the blob IS the page. Vendor
  markers and redirect targets keep reading scripts: loader
  scripts and JS location assignments are load-bearing signals.
- **Generic (traffic-anomaly)**: `TRAFFIC_CHECK` (added Wave 14,
  W14-002): "unusual traffic" / "suspicious activity" wording
  PAIRED with a verification cue (verif/captcha/prove/confirm)
  is a presented challenge. Either half alone is not: anomaly
  wording without a cue stays a bare-403 refusal, and a lone
  verification word without anomaly wording is not this rule.

Verdict precedence: UNREACHABLE (fetch failed) → vendor challenge/block
signals (CHALLENGED/WALLED) → 429 RATE_LIMITED → login evidence
LOGIN_GATED → bare 403 WALLED → 2xx OPEN. Two Wave 6 refinements:
the generic-marker branch yields to an identified login page (human-check
prose on a sign-in form is part of the auth experience; vendor wall
codes keep their precedence), and the Incapsula block page is WALLED
at any status when the body carries its incident-ID line (the block
page is commonly served as 200). One Wave 8 refinement: the login
heuristic fires only on served pages (2xx/3xx): a 4xx/5xx at a login
URL takes the error's verdict (a 444 Akamai deny is WALLED, a 5xx is
UNREACHABLE), never LOGIN_GATED. Wave 10 refinements: a stub page
(< 4 KB) refusing service by region/country is WALLED (a refusal,
not served content: verdict-only, no vendor named); status 451
(Unavailable For Legal Reasons) is WALLED, the 444 rule's sibling;
a page whose whole content redirects (meta refresh or JS location)
to a challenge/captcha target is CHALLENGED by reference and to a
login target is LOGIN_GATED (the Wave 6 S2c principle, generalized
past captcha-only targets; redirects to content targets stay OPEN);
and an UNREACHABLE verdict carries no vendor (a 5xx error page
wearing vendor branding is an origin failure, not a wall). Wave 11
refinements: form actions join the redirect-target rule as its
third species, gated to served (2xx) small pages: a form is
interactive content, not a routing directive, so a 403 page
carrying a login form stays a refusal, not a gate by reference.
Wave 20 refinements: an <iframe> src joins the redirect-target
species as its fourth member: an embedded frame to a
challenge/login target names the same gate by reference, under
the same served-page gate (a frame on real content is
furniture, not a gate);
a challenge-platform loader (Turnstile) as the ONLY Cloudflare
signal on an identified login page yields to the login verdict
(the Wave 6 S5c principle in vendor form: a loader on a
check-only, non-login page is still the challenge, and a fired
wall signal at a login URL still wins); and a LOGIN_GATED verdict
whose only vendor evidence is generic carries no vendor (the
generic evidence was judged to be auth copy, not a wall: the
UNREACHABLE-vendor rule's sibling; named-vendor presence on a
login page is kept). Wave 14 refinements: a 403/503 carrying a
Retry-After header AND throttle wording, with no wall signal,
is RATE_LIMITED: the two-key rule (header alone and overload
wording alone do not convert; fired walls and challenges keep
precedence); and generic markers appearing only inside
`<script>` blocks are suppressed on pages with visible text
(see Generic (script-only suppression) above). Wave 15
refinements: vendor markers inside JSON-LD blocks are metadata,
not fired walls: stripped from the vendor scan when the page
has visible text (regular scripts keep reading: loaders are
load-bearing); a small-page (< 4 KB) "access denied" stub is
WALLED, verdict-only (the general refusal, placed after the 401
branch so auth keeps precedence and guarded to sub-500 so a 5xx
keeps UNREACHABLE); generic human-check and JS_PROOF phrases
are also matched against tag-stripped visible text, so a
sentence split across elements (SVG tspans) still fires; a
"captcha" token appearing only in an invisible-captcha widget
tag does not fire when the page has visible text (it gates
form submission, not reading); the HTTP Refresh header's url
joins meta refresh, JS location, and form actions as a
redirect-target species; a served page whose form is a
one-time-code entry (code input + auth wording, two-keyed)
reads LOGIN_GATED at any URL (narrower than general form-text
detection: discount-code forms match neither key); and
"protected by X" / "powered by X" badge phrases are blanked
from marker scans on 2xx pages only (error pages keep full
attribution). Wave 16 refinements: the configuration family is
now uniform: a signal living only in configuration is not a
presented wall when the page has visible content, and is the
page when it has none: extended from scripts and JSON-LD to
data-* attributes (name or value) and <style> blocks, in the
vendor scan and in every generic survival test; the JSON
data-block strip generalizes from ld+json to every JSON script
type (application/json, text/json), while loader scripts stay
load-bearing; phrase scans read three texts (raw markup,
tag-stripped visible text, and tags-removed concatenated text : 
inline elements add no space to rendered text, so within-word
splits across spans read whole only in the concatenated
variant), applied to human-check, JS_PROOF, TRAFFIC_CHECK
(words and cues), and the captcha token, with the survival
guards applying to the concatenated variant exactly as they do
to the spaced one; the HTTP Location header on a 3xx response
joins meta refresh, JS location, Refresh header, and form
actions as a redirect-target species (matters to offline
`classify` callers; live probes follow redirects and classify
the landing page); two new two-keyed auth barriers beside
code-entry forms: passkey/WebAuthn prompts (passkey wording
plus a button, form, input, or credentials-API reference) and
magic-link forms (an email input plus auth-link wording) : 
both read LOGIN_GATED at any URL, while prose about passkeys,
bare links, and newsletter forms cannot fire; and the llms
frontmatter strip tolerates a leading UTF-8 BOM (a BOM is not
content, and it defeated the strip's anchor). Wave 23
refinements: status 418 joins the deliberate-refusal family
(444, 451) as WALLED: a server answering 418 has declined
the request, and before this rule it fell through to OPEN
whenever no wall signal had fired; and stray text nodes
inside a <picture> element join the never-presented family
(the element renders only its <img>, so picture text is the
template species: stripped from the visible-text test and
the marker scans when the page has visible content, and
still the page when it has none; the picture's img alt is
deliberately NOT stripped: the img renders, so its alt is
presented text). Wave 24 refinements: status 402 joins the
deliberate-refusal family (444, 451, 418) as WALLED: a server
answering Payment Required has declined to serve, and before
this rule it fell through to OPEN whenever no wall signal had
fired; and push-approval sign-in prompts (a full sign-in-
approval phrase in visible text plus a button or form) join
the two-keyed auth barriers. Wave 25 refinements: employee-ID
sign-in prompts (workforce-identifier wording in visible text
plus credential machinery) join the auth barriers; and
placeholder attributes join the configuration family: a
challenge phrase living only in a placeholder is stripped in
the generic survival tests like a data-* attribute, while
content-free pages still fire on it. Wave 26 refinements:
badge-tap sign-in prompts (a badge-tap phrase in visible text
plus a button or form) join the auth barriers; and the
sitemap loc test rejects percent-encoded hosts: the WHATWG
host parser rejects "%" in hosts of special schemes, so such
a loc names no crawlable destination (path percent-encoding
is untouched). Wave 27 refinements: biometric sign-in prompts
(a fingerprint / face / biometric phrase in visible text plus
a button or form) join the auth barriers: the prompt itself
is the barrier, so no vendor machinery key is required, and
biometric prose without presented machinery stays content.
Wave 28 refinements: Windows PIN / Windows Hello sign-in
prompts (a "windows pin" / "windows hello" demand in visible
text plus a button or form) join the two-keyed auth barriers;
and the overlay family gains its ARIA species: a container
asserting role="alertdialog" or aria-modal="true" is a modal
key like the class-marked overlay, while role="alert" and a
modeless role="dialog" assert no modality and stay content.

Vendor precedence (added Wave 6, economist.com): when several vendors
are detected, the one whose wall actually fired outranks one present
only as CDN/sensor presence: the PerimeterX-over-CDN principle,
generalized. A vendor's *wall* signals are its challenge/block
markers (Cloudflare's mitigated/just-a-moment/challenge-platform/
block-sorry, PerimeterX's px-captcha/body marker, DataDome's
x-datadome/body marker, Akamai's bm-verify/edgesuite/reference
pages, Incapsula's body marker, the AWS/Azure WAF, Kasada and
CloudFront body markers, and the generic markers); its presence
signals are CDN headers and sensor cookies. First wall-signal
vendor in detection order wins; with no wall signals, the first
detected vendor stands (a bare 403 behind Cloudflare keeps
Cloudflare).

### MCP server

Stdio JSON-RPC, Python standard library only. Tools:

- `probe_url(url, timeout?)` → the classification object for a live fetch.
- `classify(status, headers, body)` → offline classification of a
  captured response; no network. For pipelines that fetch their own way
  and want the verdict + evidence codes.
- `audit(domain, timeout?)` → the owner-side agent-access audit
  (added Wave 9, v0.5.0): grade plus per-check PASS/WARN/FAIL with
  evidence and fixes. Read-only. Makes up to 10 honest GETs to the one
  domain (homepage, robots, llms, sitemap, declared sitemap if any,
  two OpenAPI paths, /api and /developers only when no spec is found,
  the signed-agent directory path), each with the probe's per-fetch
  timeout and bounded body sample, no retries. The fetch budget is
  stated in the tool description so MCP clients can rate-limit; the
  decision record is in `validation/wave9/DOCS-AUDIT.md` (Leg B).

### Constraints

- Python 3.11+ standard library **only**. No third-party dependencies,
  ever, in the core: the tool must run anywhere Python runs, including
  locked-down CI and VMs where package installs are blocked.
- One honest fetch per probe. No retries against a wall, no headless
  browser, no JavaScript execution.

## v0.2: signed agent identity (SHIPPED as prototype, Wave 2)

The standards-based answer to anonymous-bot blocking: if agents identify
themselves cryptographically, sites can allow the good ones by signature
instead of walling everyone.

**Status (v0.2.0):** the signing machinery is built, tested, and
dogfooded: full write-up in `validation/wave2/SIGNING.md`.

- [x] `wallcheck keygen`: generate a signing key. *Prototype
  deviation, documented:* Ed25519 is not in the Python standard
  library and `cryptography` is not installed on the build VM, so
  the prototype uses RFC 9421's registered `hmac-sha256`
  shared-secret algorithm (§3.3.3): real RFC 9421 signatures,
  stdlib-only. The public Web Bot Auth ecosystem runs on Ed25519
  with a public key directory; a shared secret cannot be published
  in a directory, so this covers the bilateral case (agent operator
  ↔ site owner who agreed on a secret) and owner-side testing, and
  does not claim directory compatibility.
- [x] `wallcheck probe --sign <keyfile>`: attaches RFC 9421
  `Signature-Input`/`Signature` (covered: `@authority`, plus
  `content-type` when present; params include `created`, `expires`,
  `nonce`, `tag="web-bot-auth"`) to the same single honest fetch.
- [x] Offline `verify_request` + `wallcheck verify-server`: a tiny
  local server that honors only correctly signed requests, for site
  owners testing their side.
- [x] Measured, not assumed: signed vs unsigned probes against our
  own properties changed nothing (they don't check signatures yet);
  the results are recorded in `validation/wave2/results-signed.json`.
- [x] Directory-compatible Ed25519 identity (**SHIPPED, Wave 4,
  v0.4.0**): the blocker was removed by implementing Ed25519 per
  RFC 8032 in pure Python stdlib (SHA-512 + big-int field math,
  extended coordinates) inside the signing module: verified
  against the official RFC 8032 §7.1 test vectors as unit tests
  before it shipped. `wallcheck keygen --alg ed25519`; `probe
  --sign` auto-detects the key's algorithm;
  `wallcheck.sign.directory_document()` renders the Web Bot Auth
  directory JSON (sample:
  `validation/wave4/sample-directory.json`). HMAC remains for the
  bilateral case. Full record: the Wave 4 addendum in
  `validation/wave2/SIGNING.md`.

## v0.3: owner-side audit (SHIPPED, Wave 3)

Most walls are accidents: a default Cloudflare ruleset in front of docs,
a public API, or a pricing page the owner *wants* agents to read.

**Status (v0.3.0):** `wallcheck audit <domain-or-url>` is built,
fixture-tested, and dogfooded on five domains: first live outputs
in `validation/wave3/AUDITS.md`. Six checks, each PASS/WARN/FAIL
with named evidence and one concrete fix:

- `robots_txt`: served? Named AI agents (GPTBot, ClaudeBot, CCBot,
  Google-Extended) parsed per group: open / restricted / blocked.
  An HTML soft-404 at /robots.txt FAILs (Wave 10: the llms HTML
  gate, mirrored); an empty robots file PASSes (empty is valid and
  permissive, not missing). FAIL means every tracked agent is
  blocked (Wave 11: a wildcard Disallow: / with a named-agent
  carve-out is WARN, not FAIL: the carve-out leaves that agent
  reachable; the wildcard evidence line is still recorded).
  Wave 15: an Allow: / in the applicable group cancels a
  Disallow: / (RFC 9309 tiebreak: equally specific, Allow
  wins), and a non-root Allow alongside a Disallow: / softens
  blocked to restricted (partial access, the carve-out principle
  generalized to Allow lines). Wave 27: group names are RFC 9309
  product tokens: a versioned token (wallcheck/1.0) names the
  same agent as the bare identifier, and a token that is only a
  version string names no agent.
- `llms_txt`: served as genuine text; an HTML soft-404 FAILs
  (Wave 2's lesson, enforced), and a JSON error document FAILs
  (Wave 10: error-key presence, not format policing). A title-only
  file (no links, URLs, or paths) is WARN, not PASS (Wave 13);
  markdown links count as index entries only when the target is
  non-empty and not a pure fragment (Wave 14: `[Intro](#intro)`
  points at the file itself, not at site content). Wave 15: a
  leading YAML frontmatter block is stripped before content
  analysis (metadata URLs/links are not index entries), and the
  under-20-char length gate no longer fires on bodies carrying
  a link, URL, or path ("effectively empty" means no usable
  content: stripping metadata can push a real one-link index
  under 20 chars). Wave 27: HTML comments are stripped before
  content analysis (the classifier's comment doctrine since
  Wave 19, now shared), so links or URLs that live only inside
  a comment are not index entries.
- `sitemap`: /sitemap.xml as real XML, or the robots-declared
  Sitemap: URL. The declared URLs are tried in order until a
  usable sitemap document serves (Wave 14: a 200-but-HTML
  /sitemap.xml no longer hides a valid declared index, and a
  dead first declaration no longer hides a valid second one; a
  declared URL serving HTML is not accepted). Wave 15: a sitemap
  document with zero <loc> entries reads WARN, not PASS (a
  table of contents with no contents; one <loc> suffices): and
  a bare <?xml prolog with no sitemap content, previously PASS
  via the prolog rule, now reads WARN with it.
- `feed`: RSS/Atom `<link rel="alternate">` discovery on the
  homepage.
- `api`: an OpenAPI document at conventional paths, a serving
  /api root (a 401 counts: an auth front door is a door), or a
  developer portal. SPA app shells at those paths are detected
  and named, not counted (W3-004).
- `signed_agents`: a Web Bot Auth key directory at
  /.well-known/http-message-signatures-directory. Absent almost
  everywhere today; recorded as data.

Scoring PASS=2 / WARN=1 / FAIL=0 of 12 → grades A≥11, B≥9, C≥7,
D≥5, else F. Every resource is also run through the probe
classifier: a machine file behind a wall fails *as a wall*.
CLI-only until Wave 9, which added the `audit` MCP tool with the
same bounded-fetch discipline (see the MCP server section).
Also in v0.3: AWS WAF detection (W3-001), the Akamai edgesuite
signal (W3-002), and the Bot Wall Index working table at `INDEX.md`
(see the Index section below).

## v0.5: territory-driven classifier growth (SHIPPED, Wave 5)

No new interface; the classifier learned what the Wave 5
expansion territory (civic, travel, health, real estate) actually
serves: Microsoft Azure WAF detection (W5-002), Kasada detection
and attribution precedence (W5-003), AWS CloudFront's generated
block page (W5-004), the Akamai reference-token deny page and a
verdict rule for status 444: a dropped request is a refusal,
never an OPEN (W5-005): and the generic-CAPTCHA scan now blanks
third-party widget loader references, closing the false-challenge
species the Wave 1 GitHub fixture first exposed (W5-001). All
fixes test-first from live captures; the affected rows were
re-probed and merged (`validation/wave5/PROBLEMS.md`). Wave 5
also ran the first signed-vs-unsigned experiment with the shipped
Ed25519 signer (`validation/wave5/SIGNED-EXPERIMENT.md`) and the
campaign's owner fix kit (`campaign/FIX-KIT.md`). Wave 6 hardened
the classifier against 25 adversarial shapes (4 defects fixed) and
took the index to 394; Wave 7 took it to 499, ran the second
directory census (4 adopters, ahrefs.com new) and an audit sweep
of 92 domains, with zero classifier defects; Wave 8 path-probed 46
more platforms (322 paths, 1 defect fixed) and took the front-doors
file to 65 platforms. Wave 9 (release-candidate polish) added the
`audit` MCP tool, corrected every stale doc count against measured
reality, and stamped 0.5.0-rc: see
`validation/wave9/DOCS-AUDIT.md` and
`campaign/LAUNCH-READINESS.md`.

## The Bot Wall Index (flywheel)

Modeled on the family's Agent Policy Index (which scans thousands of
repos for agent-contribution policies), the **Bot Wall Index** is a
recurring, measured scan of major platforms: freelance marketplaces,
job boards, dev platforms, docs sites: recording per target:

- verdict + vendor + evidence (from `wallcheck probe`, unmodified),
- client/network context of the scan (results are context-dependent and
  the Index says so),
- history: when a wall appeared, hardened, or came down.

Published openly on a cadence. The point is the same as the Policy
Index: a private frustration becomes public, checkable data: and
platforms that wall off legitimate agents get named with receipts,
while platforms that fix it get visibly credited. Dogfood rule: our own
properties are in the Index first.

**Status (0.5.0 final, ship-readiness pass; fixes through
Wave 28 folded in):** the working table
lives at `INDEX.md` in this repo: 500 sites merging the Wave 1
census, the Wave 3/5/6/7 expansions, stability rounds 2-24, and
the Wave 18 row-500 addition (rounds 15-24 moved six, ten,
zero, zero, two, two, three, two, one, and zero rows; the hard core of walls has reproduced in every round).
Directory census v2 (Wave 7):
4 of 499 domains publish signed-agent directories; Wave 16's,
Wave 20's, and Wave 23's spot-checks found all four still publishing. It is a *working*
document: publication stays on hold until the campaign launches on
the owner's explicit call.

## Success criteria for v0.1

- Fixture suite covers every verdict and every vendor; all green,
  fully offline.
- MCP smoke: initialize + tools/list + all three tools called, valid JSON-RPC.
- Dogfood run against real platforms recorded verbatim (DOGFOOD.md),
  including: especially: the walls.
