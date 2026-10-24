# Wave 27 — Adversarial Battery v19: Hand Classifications

Discipline (as Waves 6, 10–26): every shape below was classified BY
HAND against SPEC's verdict definitions BEFORE the classifier was
allowed to see it. All shapes are NEW relative to Wave 6 (S1–S6),
Wave 10 (B1–B10), Wave 11 (C1–C8), Wave 12 (D1–D9), Wave 13
(E1–E10), Wave 14 (F1–F8), Wave 15 (G1–G10), Wave 16 (H1–H10),
Wave 17 (J1–J9), Wave 18 (K1–K8), Wave 19 (L1–L8), Wave 20
(M1–M10), Wave 21 (N1–N8), Wave 22 (P1–P8), Wave 23 (Q1–Q8),
Wave 24 (R1–R8), Wave 25 (T1–T8), and Wave 26 (U1–U8). Deltas
stated explicitly so they are not mistaken for repeats: the
presented-element survey (figcaption R1, summary R8, blockquote
T1, textarea default text T8, label text U1, button text U8) has
never put a marker inside a TABLE CELL — V1 closes the survey.
No prior battery has classified a maintenance page at all (grep:
"maintenance" appears nowhere in src/ or tests/ before this
wave); B4/D5 covered redirect-to-challenge and redirect-to-login
targets, and W16-004 collected the Location header as a target —
V2 asks what a 307 to a MAINTENANCE target means. The auth family
names code entry (G6), passkey/WebAuthn (H5), magic link (H10),
delivery codes (K3), email-Continue (L3), authenticator (N3), SSO
(P3), push approval (R3), QR (J4), employee ID (T3), and badge-tap
(U3); V3 covers the biometric prompt — "use your fingerprint" —
which is not WebAuthn wording (grep: "fingerprint" appears only
in sign.py's key_fingerprint, never in the classifier). U4 (Wave
26) covered whitespace INSIDE a robots User-agent value; V4
covers the version suffix on the product token, a different
composition (RFC 9309 producttoken = identifier ["/" version]).
No prior battery has put content inside an HTML comment in an
LLMS file (the comment-strip pins are classifier-side: E-family
comment-only vendor markers, J9's commented overlay); the
classifier strips comments before every body scan, and V5 asks
whether the audit's llms check does the same. K6/L6/N6/Q6/U6
covered empty, fragment, relative, query, non-HTTP-scheme,
uppercase-scheme, and percent-encoded-host locs; V6 covers IP
literals. The localized list stands at 51 language groups; V7's
four were grep-verified absent from the full list before writing
(below). J8 (full-screen overlay) and K2 (sticky banner) named
the blocking-overlay species; V8's toast is neither — a transient
corner notification with no overlay marker and no stickiness.
Any mismatch is a defect candidate: fix generalized with a
capture-built fixture, or ledger it as a genuine honest
limitation with the reason — and per Wave 25's lesson, check
every mismatch against the older pins before fixing (a Wave 6
pin vetoed Wave 25's 410 "fix"; a mismatch against an old pin is
a hand-classification question first, a defect second). No
silent passes, no per-shape special cases. Per the Waves 17–26
pattern, every new signal family carries visible-text gating and
a served-page size gate from birth, with a negative fixture per
family using an asset-filename, script-identifier, or
stylesheet-class carrier.

Reference — SPEC verdicts: OPEN = the resource was served;
CHALLENGED = an interactive human-verification challenge was
presented; WALLED = a hard block page, no challenge offered;
LOGIN_GATED = content exists behind authentication; RATE_LIMITED
= a throttle; UNREACHABLE = the fetch itself failed. Audit
grades: PASS / WARN / FAIL per check.

## V1 — challenge markers ONLY inside table cells (classifier)

A table cell's text is rendered content — it is what the reader
reads, in the presented family with <label> text (U1) and
<button> text (U8): no strip names it, and none should — the tag
is removed by tag-stripping, its text remains. This family
closes the presented-element survey.

- **V1a** — 200, content-free page, only
  `<table><tr><td>Verify you are human</td></tr></table>`. →
  **CHALLENGED / Generic**. The cell is the page's only text and
  it is presented. Pin expected.
- **V1b** — 200, small real paragraph PLUS a table whose `<th>`
  reads "Verify you are human". → **CHALLENGED / Generic**.
  Presented text on a non-served page fires. Pin expected.
- **V1c** — 200, BIG_ARTICLE PLUS a `<td>` phrase. → **OPEN**.
  Pin: the served-page size gate.
- **V1d** — 403, small page, only a `<td>` phrase. →
  **CHALLENGED / Generic**. Pin: 403 is a GENERIC_OK status and
  the phrase is presented.
- **V1e** — 200, content-free page, only a table with ordinary
  cell text ("Quarterly revenue results"). → **OPEN**. Pin: a
  table alone is furniture; without a phrase nothing fires.

## V2 — HTTP 307 redirects to a maintenance page (classifier)

A 307 is a redirect, and the redirect doctrine is settled: the
hop is routing (W16-004 collects the Location target), and the
verdict belongs to the target — a challenge target is a
challenge by reference (B4a), a login target a login gate
(B4b), a content target is routing (B4d). A maintenance target
names neither a gate nor a wall: a maintenance page is the same
answer for every client — the site declaring downtime, not an
access decision against agents — so it carries no redirect
evidence, and the landing page is classified on its own
posture. The status-declared species of the same condition
already exists: a 503 IS the maintenance status, and the 5xx
doctrine (Wave 10) reads it UNREACHABLE — the server declared
itself unavailable, no wall claimed. A SERVED maintenance page
(200) is a page the server chose to serve; wallcheck names
walls and access posture, not downtime, so it reads OPEN
exactly as any other served stub does. Maintenance wording is
not a wall signal at any status.

- **V2a** — 307, `Location: /maintenance`, empty body. →
  **OPEN** (STATUS_307). Pin expected: the Location target is
  collected, names no gate, and a bare 3xx falls through to the
  served/routing reading — live probes never see this shape
  (they follow the hop and classify the landing, V2b).
- **V2b** — 200, small maintenance page ("Scheduled
  maintenance — we will be back soon.") at a /maintenance
  final URL. → **OPEN**. Pin: the landing is served content;
  downtime is not a wall.
- **V2c** — 503, maintenance page body. → **UNREACHABLE**.
  Pin: the 5xx doctrine — the fetch-level answer is that the
  origin is unavailable; no vendor is named.
- **V2d** — 200, maintenance page at the root URL, no redirect
  anywhere. → **OPEN**. Pin (control for V2b): the redirect is
  not what makes it served; the page is.

Scope note: the 307-to-login and 307-to-challenge compositions
are NOT in this battery — Wave 16's H4a/H4b already pinned
307 + Location to challenge/login targets (and H4c the content
target). V2's only new delta on H4 is the maintenance target: a
target naming neither a gate nor a wall.

## V3 — login walls asking for a fingerprint (classifier, NEW signal)

The biometric sign-in prompt is the one device-credential
ceremony the auth family does not name: the page's only content
instructs the user to authenticate with a fingerprint (or face)
— "Use your fingerprint to sign in" — with no password, no code,
and no WebAuthn wording (no "passkey", no "webauthn": consumer
biometric prompts deliberately avoid the standard's vocabulary).
It is an authentication barrier exactly like its siblings: the
content exists behind an act of physical authentication the
agent cannot perform. Two keys, from birth (the family
discipline): (1) a full biometric demand in RENDERED visible
text — "use your fingerprint", "scan your fingerprint", "use
your face", "biometric authentication" — never the bare word
"fingerprint" (fingerprinting articles, privacy policies, and
phone reviews all say "fingerprint"); (2) prompt machinery — a
<button> or <form>, the page's actionable apparatus. Prose ABOUT
biometrics carries the wording without the ceremony's machinery;
configuration carriers (asset filenames, script identifiers,
stylesheet classes) are not rendered wording.

- **V3a** — 200, page whose only content is a heading "Sign
  in", the text "Use your fingerprint to sign in.", and a
  `<button>Try again</button>`, at a non-login URL. →
  **LOGIN_GATED**. Predicted gap: no biometric signal exists,
  so the classifier reads OPEN.
- **V3b** — 200, the same prompt embedded in BIG_ARTICLE. →
  **OPEN**. Pin on the fix: the served-page size gate (the
  siblings' gate, from birth).
- **V3c** — 200, small real paragraph PLUS
  `<script src="/js/fingerprint-signin.js"></script>`
  (asset-filename carrier), no biometric wording in visible
  text. → **OPEN**. Negative carrier. Pin.
- **V3d** — 200, small real paragraph PLUS
  `<style>.fingerprint-prompt{border:0}</style>`
  (stylesheet-class carrier). → **OPEN**. Negative carrier.
  Pin.
- **V3e** — 200, small page whose only content is prose:
  "On your phone, use your fingerprint to unlock the app after
  you sign in with your password." — NO button, NO form. →
  **OPEN**. Guard: wording without prompt machinery is a help
  article, not a sign-in ceremony — the machinery key is
  load-bearing (the T3e/R3e/U3e species).
- **V3f** — 200, fingerprint prompt (wording + button) at a
  login URL. → **LOGIN_GATED**. Pin: the login heuristic
  already fires; the new rule must agree.
- **V3g** — 200, small real paragraph + a real `<button>Cancel
  </button>` in a comment form + a script block whose string
  reads "use your fingerprint" (script-identifier carrier). →
  **OPEN**. Negative carrier: the wording must appear in
  RENDERED visible text — script text is stripped from visible
  text (the rubygems/QR lesson). Pin on the fix.

## V4 — robots.txt product-token groups carrying a version (audit tool)

RFC 9309's producttoken is `identifier ["/" version]`: the
identifier is the crawler's name; the version is the build it
happens to be running. A group line `User-agent: GPTBot/2.0`
addresses the crawler NAMED GPTBot — the version refines, it
does not rename — and deployed crawlers present exactly this
way (GPTBot's own user agent carries a version). A robots file
that refuses GPTBot only under a versioned token has still
refused GPTBot: the audit's question is whether the named agent
is refused, and an unambiguous address to that name answers it.
The parser currently stores the full value ("gptbot/2.0") and
matches agent names by exact membership, so a versioned group
is invisible: its rules bind nobody the audit tracks. (Checked
against the older pins before classifying: no prior battery
places a "/" inside a User-agent value — U4's trailing spaces
are the only value-composition pin, and trimming composes with
name extraction; the wildcard "*" carries no version and must
survive normalization untouched.)

- **V4a** — `User-agent: wallcheck/1.0` + `Disallow: /`,
  nothing else. → robots **PASS**. Pin: the versioned token
  names an agent the audit does not track; the four tracked
  agents have no group and no wildcard, so none is refused.
- **V4b** — `User-agent: GPTBot/2.0` + `Disallow: /`, nothing
  else. → robots **WARN** (AI_BLOCKED: GPTBot). Predicted gap:
  the versioned group is invisible to the matcher, so GPTBot
  reads open and the check passes.
- **V4c** — four versioned groups (GPTBot/1.0, ClaudeBot/2.0,
  CCBot/1.1, Google-Extended/1.0), each with `Disallow: /`. →
  robots **FAIL**. Predicted gap (same family): all four read
  open today.
- **V4d** — `User-agent: GPTBot` + `Disallow: /`, then a
  separate group `User-agent: GPTBot/2.0` + `Allow: /`. →
  robots **PASS**. Predicted gap, pin on the fix: under
  name-matching both groups are GPTBot's, their rules merge
  (the parser already merges multiple groups per agent), and
  the Allow: / cancels the Disallow: / (the W15-008 tie rule).
  Today the versioned Allow is invisible, so GPTBot reads
  blocked (WARN).
- **V4e** — `User-agent: ClaudeBot/3.1` + `Disallow: /private`,
  plus a wildcard group with `Allow: /`. → robots **WARN**
  (AI_RESTRICTED: ClaudeBot). Predicted gap (same family): the
  versioned restriction is invisible today and ClaudeBot falls
  back to the permissive wildcard.

## V5 — llms.txt whose only links live inside an HTML comment (audit tool)

An HTML comment is not content — in the classifier it is the
never-presented family (comments are stripped before every body
scan; the E-family pins exist because comment-only vendor
markers fired). An llms.txt is markdown text, and markdown's
HTML comments are exactly as unrendered there: agents ingesting
the file follow its links, and a link inside a comment is
invisible to a markdown reader exactly as it is to an HTML
reader. The W15-009 doctrine — document metadata is not index
content — has this as its next species: commented-out links are
the file's scratchpad, not its index. The llms check currently
runs its content tests (`_has_usable_link`, the URL and path
regexes) on a body from which only frontmatter has been
stripped, so a commented link counts as the file's one usable
link.

- **V5a** — 200 llms, body `# Site Index` + a commented
  markdown link (`<!-- [Docs](https://example.com/docs) -->`)
  and nothing else. → **WARN** (LLMS_STUB: no usable links,
  URLs, or paths outside the comment). Predicted gap: the
  commented link counts today, so the check passes.
- **V5b** — 200 llms, body `# Site Index`, the same commented
  link, PLUS one real markdown link. → **PASS**. Pin: the real
  link carries the file whichever way V5a is decided — the fix
  must not overreach.
- **V5c** — 200 llms, body is ONLY a comment carrying a bare
  URL (`<!-- see https://example.com/map -->`). → **WARN**
  (EMPTY_BODY after the comment is stripped: nothing remains).
  Predicted gap (same family): the commented URL satisfies the
  URL test today, so the check passes.

## V6 — sitemap.xml <loc> entries that are IP literals (audit tool)

The loc test (K6/L6/N6/Q6/U6) asks one question: does the
entry name a crawlable destination? An IP-literal host names
one exactly as a DNS name does — `http://192.0.2.10/page` is a
complete, parseable, crawlable URL; the audit grades whether
the sitemap names destinations, not whether the destination is
a good idea (loopback and documentation-range addresses are
the site's own addressing choices, not a format failure). The
U6 authority test must not misfire here: a plain IPv6 literal
carries no "%" in its host (zone IDs would, and a zoned
literal is out of scope for this family).

- **V6a** — urlset whose only loc is
  `http://192.0.2.10/sitemap.xml`. → **PASS**. Pin expected.
- **V6b** — urlset whose only loc is
  `http://[2001:db8::10]/page`. → **PASS**. Pin: the bracketed
  IPv6 authority parses through the U6 host test untouched
  (no "%", colons are not the test's business).
- **V6c** — urlset whose only loc is `https://127.0.0.1/admin`.
  → **PASS**. Pin: loopback names a destination; reachability
  policy is not the audit's question.
- **V6d** — urlset with locs `https://%65xample.com/a`
  (percent-encoded host, the U6c defect species) and
  `http://192.0.2.10/b` (IP literal). → **PASS**. Pin: one good
  loc suffices — the IP literal carries the file, composing
  with U6 exactly as U6b composed within its own family.

## V7 — challenge phrases in Albanian, Icelandic, Kazakh, Malayalam (classifier)

Same principle as every prior language wave: challenge pages
are not English-only. Verified against the current
_LOCALIZED_HUMAN_CHECK list before writing (grep returned 0 for
all eight strings): Albanian, Icelandic, Kazakh, and Malayalam
have NO entry. Deliberate distinctions: Albanian "konfirmoni që
nuk jeni robot" contains no Catalan or Spanish entry ("nuk
jeni" is neither "no ets" nor "no eres"); Icelandic
"staðfestu að þú sért ekki vélmenni" uses ð/þ and "vélmenni",
no Scandinavian entry contains it (the Nordic entries say
"robot"); Kazakh "робот емес екеніңізді растаңыз" and "мен
робот емеспін" are Cyrillic but contain neither the Russian
("подтвердите, что вы не робот", "я не робот"), Ukrainian,
Bulgarian, Serbian, nor Macedonian entries (Kazakh-specific
letters ң, ү, ұ, ғ and the "емес" negation); Malayalam is a
unique script with no Tamil/Telugu collision (different script
entirely). Each language gets the demand sentence plus the
checkbox sentence, as in the two-string waves.

- **V7a SQ** — 403, small page, "Konfirmoni që nuk jeni robot"
  → **CHALLENGED / Generic**. Predicted gap.
- **V7b SQ** — 403, small page, "Unë nuk jam një robot"
  → **CHALLENGED / Generic**. Predicted gap.
- **V7c IS** — 403, small page, "Staðfestu að þú sért ekki
  vélmenni" → **CHALLENGED / Generic**. Predicted gap.
- **V7d IS** — 403, small page, "Ég er ekki vélmenni"
  → **CHALLENGED / Generic**. Predicted gap.
- **V7e KK** — 403, small page, "Робот емес екеніңізді
  растаңыз" → **CHALLENGED / Generic**. Predicted gap.
- **V7f KK** — 403, small page, "Мен робот емеспін"
  → **CHALLENGED / Generic**. Predicted gap.
- **V7g ML** — 403, small page, "നിങ്ങൾ ഒരു റോബോട്ട് അല്ലെന്ന്
  സ്ഥിരീകരിക്കുക" → **CHALLENGED / Generic**. Predicted gap.
- **V7h ML** — 403, small page, "ഞാൻ ഒരു റോബോട്ട് അല്ല"
  → **CHALLENGED / Generic**. Predicted gap.
- **V7i** — 200, SQ phrase on BIG_ARTICLE → **OPEN**. Pin:
  the served-page gate.
- **V7j** — 200, small page with only the fragment "vélmenni"
  → **OPEN**. Pin (the J7g/Q7f/R7f/T7f/U7f species): fragments
  do not fire.
- **V7k** — 200, ML phrase ONLY inside a <style> block + a
  small real paragraph → **OPEN**. Pin (the Q7g/R7g/T7g/U7g
  species): style-block suppression — the family's negative
  carrier.

## V8 — challenge presented as a toast notification (classifier)

A toast is a transient corner notification: it appears, it is
dismissible, it does not cover the page. It belongs to neither
blocking species — it has no overlay marker (J8 requires an
overlay-marked container whose following text carries the
phrase) and no stickiness (K2 requires a banner/announcement
marker PLUS fixed/sticky positioning as the third key). What
remains is the generic rule, and the generic rule is
size-gated: on a served page a human-check phrase is presence,
not presentation (the U1c/U8c species). On a NON-served page
the same toast text is simply the page's presented text — a
page whose only content is a toast carrying a challenge phrase
presents that challenge, exactly as a page whose only content
is a paragraph carrying it does.

- **V8a** — 200, BIG_ARTICLE PLUS `<div class="toast"
  role="alert">Verify you are human to continue</div>`. →
  **OPEN**. Pin: the toast does not convert served content
  into a challenge; neither overlay nor banner key is present.
- **V8b** — 200, content-free page, only
  `<div class="toast">Verify you are human</div>`. →
  **CHALLENGED / Generic**. Pin: the toast is the page's only
  presented text and it is a challenge phrase.
- **V8c** — 200, BIG_ARTICLE PLUS a toast div whose phrase
  rides only in a data attribute
  (`data-toast-text="Verify you are human"`) with innocuous
  visible text ("Welcome back"). → **OPEN**. Pin: the
  attribute carrier family (K8/W25-T8d) on the toast species.
- **V8d** — 200, content-free page, only a toast reading
  "Item added to your cart". → **OPEN**. Pin: a toast alone is
  furniture without a phrase.
