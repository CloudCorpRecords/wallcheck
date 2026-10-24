# Wave 28 problems ledger

Three defect families from battery v20, all fixed test-first
against `validation/wave28/HANDCLASS-20.md` (written before any
test ran; first battery run failed on exactly the 12 predicted
gap fixtures and nothing else). Every fix is a generalized
rule, checked against older pins before it landed; the capture
corpus regression is clean (44 captures, diff empty) and the
full suite is 885/885 via pytest.

## W28-W3 — Windows PIN / Windows Hello prompts missed the auth family

**Defect.** A served-size login page (200, real page weight)
whose only presented auth step was a Windows credential prompt
— "Enter your Windows PIN to continue." beside a button, or a
"Sign in with Windows Hello" button — read OPEN. The machinery-
auth family (Wave 16 passkeys, Wave 18 magic links, Wave 26
badge taps, Wave 27 biometrics) keys each branch on its own
wording; the Windows ceremony matches none of them (no
"passkey", no "fingerprint", no code boxes), and it is a real
barrier: a device-bound credential the agent does not hold.

**Fix.** `_is_windows_pin_prompt` + `_WINDOWS_PIN_WORDS` +
`_WINDOWS_PIN_MARKERS` in classify.py, with a `WINDOWS_PIN_PROMPT`
branch in the auth elif chain (after BIOMETRIC_PROMPT, before
QR). Two-keyed from birth, per the pattern every family since
Wave 17 carries: a Windows demand ("windows pin" / "windows
hello") in rendered visible text AND presented machinery
(`<button` / `<form`), behind the same served-page size gate
(body < 65536 bytes) as every sibling branch. Never the bare
word "windows" — every OS article and settings page says it.

**Boundary, ledgered in the code comment.** Windows sign-in
prose without presented machinery — a help article about
setting a PIN under Settings — stays OPEN (fixture W3e). That
is the prose-without-machinery boundary the family accepts for
every sibling, applied to the new family on day one.

**Fixtures.** test_adversarial20.py W3a–W3h: the defects (W3a
PIN wording, W3h Hello wording), the size-gate pin (W3b), the
prose guard (W3e), the login-URL agreement pin (W3f), and the
three negative carriers — asset filename (W3c), stylesheet
class (W3d), script string (W3g) — all OPEN.

**Pin checks.** "windows pin" / "windows hello" grep-verified
absent from src/ and tests/ before the branch was placed; the
word list is disjoint from the passkey, biometric, badge-tap,
and QR vocabularies, so the elif position cannot shadow a
sibling. Corpus regression clean.

## W28-W7 — Burmese, Sinhala, Amharic, Azerbaijani phrases missed

**Defect.** The demand and checkbox human-check joins in
Burmese ("သင်သည် စက်ရုပ်မဟုတ်ကြောင်း အတည်ပြုပါ" / "ကျွန်ုပ်သည်
စက်ရုပ်မဟုတ်ပါ"), Sinhala ("ඔබ රොබෝවෙක් නොවන බව තහවුරු කරන්න" /
"මම රොබෝවෙක් නොවේ"), Amharic ("ሮቦት እንዳልሆኑ ያረጋግጡ" / "እኔ
ሮቦት አይደለሁም"), and Azerbaijani ("robot olmadığınızı
təsdiqləyin" / "mən robot deyiləm") all read OPEN on
challenge-sized stubs — the standing first-run failure
signature of every language wave since Wave 20.

**Fix.** Eight strings added to `_LOCALIZED_HUMAN_CHECK`
after the Wave 27 Malayalam block, with per-string collision
comments. Pre-write verification: every phrase grep-verified
absent from classify.py, from all nineteen earlier HANDCLASS
files, and from tests/ (the claims of non-coverage in
HANDCLASS-20 are checked, not assumed). The Azerbaijani demand
verb "təsdiqləyin" differs from the existing Turkish near-twin
"doğrulayın" — recorded in the comment so a future dedupe
does not merge them; Burmese (Myanmar), Sinhala, and Amharic
(Ethiopic) are scripts with no other entry in the list.

**Fixtures.** test_adversarial20.py W7a–W7h: both joins ×
four languages, all CHALLENGED with the phrase in evidence;
W7i (served-page gate), W7j (fragment), W7k (style-block
carrier) pins.

## W28-W8 — ARIA modal challenges missed the overlay family

**Defect.** A challenge phrase inside a plain
`<div role="alertdialog">` over a full served article read
OPEN, as did the same phrase inside a role="dialog" container
carrying aria-modal="true". The overlay family keyed on
class/id markers (W17-J8), stickiness (W18-K2), and the
native <dialog> tag (W19-L8); an ARIA-spelled modal carries
none of those markers, so the only branch that could see the
phrase was the size-gated generic scan — and on served
content the gate (correctly) treats phrases as presence.
But an alertdialog is by spec a modal that blocks the page
until answered: the J8 geometry in different spelling.

**Fix.** `_MODAL_ROLE_TAG_RE` in classify.py (a tag carrying
role="alertdialog" or aria-modal="true") plus a fourth overlay
scan block after the native-dialog block, reusing the exact
J8 machinery: 800-char window after the container tag,
script/style/template/picture strips, human-check + JS-proof
phrase test, `OVERLAY_CHALLENGE` evidence — and, like every
overlay member, deliberately NOT size-gated (a modal that
must be passed blocks whatever is beneath it).

**Boundary, pinned not drifted.** role="alert" (Wave 27's
toast) and a bare role="dialog" without aria-modal assert no
modality and do not fire (fixture W8f); an alertdialog with
no challenge phrase inside is furniture (W8c); a phrase
riding in the container's own data attribute sits outside
the window and does not fire (W8e, the K8 carrier doctrine on
the modal species).

**Fixtures.** test_adversarial20.py W8a–W8f: the defects (W8a
alertdialog, W8b aria-modal), the no-phrase pin (W8c), the
content-free pin (W8d), the attribute-carrier pin (W8e), and
the modeless-dialog boundary pin (W8f).

**Pin checks.** The modal-role regex requires the role/aria
attribute itself, so class/id overlay fixtures are untouched
(the three earlier overlay blocks run first and are guarded
by the same `OVERLAY_CHALLENGE not in evidence` condition);
no earlier test or corpus capture carries role="alertdialog"
or aria-modal with a different expectation — full suite and
corpus both clean after the fix.

## Saturation note

Wave 28 is **not a clean wave**: battery v20 found three
genuine defect families (W28-W3, W28-W7, W28-W8). Under the
OVERNIGHT.md test, the two-consecutive-clean-waves clock —
reset by every wave since Wave 9's borderline candidacy —
resets again here. Wave 28 was clean-wave candidate #1; the
pair would have needed one further clean measurement wave,
and Rene's five-wave authorization (24–28) ends with this
wave either way. (Leg A's round-24 fix-driven tally is
recorded in STABILITY-23.md.)
