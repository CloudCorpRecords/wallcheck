# Wave 27 problems ledger

Four defect families from battery v19, all fixed test-first
against `validation/wave27/HANDCLASS-19.md` (written before any
test ran; first battery run failed on exactly the 15 predicted
gap fixtures and nothing else). Every fix is a generalized
rule, checked against older pins before it landed; the capture
corpus regression is clean (44 captures, diff empty) and the
full suite is 831/831 via pytest.

## W27-V3 — biometric sign-in prompts missed the auth family

**Defect.** A served-size login page (200, real page weight)
whose only presented auth step was a fingerprint prompt —
"Use your fingerprint to sign in" beside a button — read OPEN.
The machinery-auth family (Wave 16 passkeys, Wave 18 magic
links, Wave 26 badge taps) keys each branch on its own
wording; a fingerprint prompt matches none of them, and the
Wave 16 residual doctrine ("a barrier the visitor must clear
with something they carry") named exactly this shape without
covering it.

**Fix.** `_is_biometric_prompt` + `_BIOMETRIC_WORDS` +
`_BIOMETRIC_MARKERS` in classify.py, with a `BIOMETRIC_PROMPT`
branch in the auth elif chain (after BADGE_TAP_PROMPT, before
QR). Two-keyed from birth, per the pattern every family since
Wave 17 carries: a biometric phrase AND presented machinery
(`<button` / `<form`) in the visible text, behind the same
served-page size gate (body < 65536 bytes) as every sibling
branch. Vendor machinery is deliberately NOT required: unlike
a passkey (a platform API), the fingerprint prompt is itself
the barrier, so the machinery key is the presented control.

**Boundary, ledgered in the code comment.** Biometric prose
without presented machinery — help text, a settings
walkthrough, a marketing page — stays OPEN (fixture V3b).
That is the prose-without-machinery boundary the Wave 16
residual edge accepted, applied to the new family on day one,
not discovered later.

**Fixtures.** test_adversarial19.py V3a–V3g: the defect (V3a),
the prose cautionary pin (V3b), face-wording and biometric-
authentication variants (V3c, V3g), and the three negative
carriers — asset filename (V3d), script identifier (V3e),
stylesheet class (V3f) — all OPEN.

**Pin checks.** The biometric vocabulary was grep-checked
against the passkey (`PASSKEY_MARKERS` / `_PASSKEY_WORDS`),
badge-tap, and QR families for string collisions before the
branch was placed; the elif position (after badge-tap, before
QR) cannot shadow any sibling because each family's two keys
are disjoint wordings. Corpus regression clean.

## W27-V4 — versioned robots product tokens built phantom groups

**Defect.** `parse_robots` stored the raw UA value as the
group name, so `User-agent: wallcheck/1.0` created a group
named `wallcheck/1.0` that the audit's agent matching never
finds — a Disallow-all aimed squarely at this crawler graded
PASS (missing barrier), and a versioned `*` or third-party
token behaved the same.

**Fix.** audit.py `parse_robots` now stores the identifier
only: `value.lower().split("/", 1)[0].strip()` — RFC 9309
defines producttoken as `identifier ["/" version]`, so the
version is metadata about the token, never part of its name.
A value that reduces to nothing ("/1.0" alone) names no agent
and is ignored. The `ua` key in the rules output is unchanged
(it records the raw line's value for evidence).

**Pin checks.** Grep over all eighteen earlier test files and
the audit fixtures: no earlier test puts "/" in a UA value,
so no pin moves; bare-token behavior is byte-for-byte
identical (V4a). Corpus regression clean (the corpus exercises
classify, not robots parsing, but the full suite's 200+
audit tests cover the parser).

**Fixtures.** test_adversarial19.py V4a–V4e: bare-token pin
(V4a), the defect (V4b), a versioned third-party token (V4c),
a versioned wildcard staying universal (V4d), and the
version-only token naming no agent (V4e).

## W27-V5 — llms.txt links inside HTML comments counted as content

**Defect.** `_check_llms` tested the raw body for links, so a
file whose only link (or only bare URL) lived inside an HTML
comment graded the file as carrying real entries. The
classifier has stripped HTML comments since Wave 19's
template-block rule; the audit's llms checker never adopted
the same doctrine, so the two halves of the tool disagreed
about what a comment is.

**Fix.** `_HTML_COMMENT_RE` in audit.py; `_check_llms` strips
comments immediately after the frontmatter strip and before
every content test (emptiness, link presence, URL presence),
so a commented-out link is not an index entry on any branch.
A real link beside a comment still counts (V5b).

**Evidence-label note.** V5a's hand-class named the expected
warning `LLMS_STUB`; a body reduced to bare prose by the strip
actually lands on `EMPTY_BODY`. Same WARN grade, same defect —
the pin records the label the code produces and
ADVERSARIAL-19.md records the discrepancy. The label was not
bent to match the hand-class; the hand-class is what adjusts.

**Fixtures.** test_adversarial19.py V5a–V5c: comment-only link
(V5a), real link beside a comment (V5b), comment-only bare URL
(V5c).

## W27-V7 — Albanian, Icelandic, Kazakh, Malayalam phrases missed

**Defect.** The demand and checkbox human-check joins in
Albanian ("konfirmoni që nuk jeni robot" / "unë nuk jam
robot"), Icelandic ("staðfestu að þú sért ekki vélmenni" /
"ég er ekki vélmenni"), Kazakh ("робот емес екеніңізді
растаңыз" / "мен робот емеспін"), and Malayalam
("നിങ്ങൾ ഒരു റോബോട്ട് അല്ലെന്ന് സ്ഥിരീകരിക്കുക" / "ഞാൻ
ഒരു റോബോട്ട് അല്ല") all read OPEN on challenge-sized stubs —
the standing first-run failure signature of every language
wave since Wave 20.

**Fix.** Eight strings added to `_LOCALIZED_HUMAN_CHECK`
after the Wave 26 Georgian block, with per-string collision
comments. Pre-write verification: every phrase grep-verified
absent from classify.py and from all eighteen earlier
HANDCLASS files (the claims of non-coverage in HANDCLASS-19
are checked, not assumed). Kazakh's checkbox wording differs
from the existing Russian near-twin ("я не робот") by the
language-specific `емес` negation — recorded in the comment
so a future dedupe does not merge them.

**Fixtures.** test_adversarial19.py V7a–V7h: both joins ×
four languages, all CHALLENGED with the phrase in evidence.

## Saturation note

Wave 27 is **not a clean wave**: battery v19 found four
genuine defect families (W27-V3, V4, V5, V7). Under the
OVERNIGHT.md test, the two-consecutive-clean-waves clock —
already reset by Waves 24, 25, and 26 — resets again here.
Wave 28, if run, becomes clean-wave candidate #1, and one
further clean measurement wave after it would still be needed
for the pair. Round 23 also recorded zero fix-driven moves
for the Wave 26 rules (STABILITY-22.md), so neither leg of
Wave 27 supplies a clean measurement.
