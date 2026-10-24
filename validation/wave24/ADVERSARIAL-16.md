# Wave 24 — Adversarial Battery v16 (36 shapes)

Hand-first discipline as in Waves 6, 10, 11, 12, 13, 14, 15, 16,
17, 18, 19, 20, 21, 22, 23: HANDCLASS-16.md was written BEFORE
the battery ran. First run: **8 failures, 28 passes — exactly the
8 predicted gaps in 3 families, zero surprises, zero
hand-corrections.** After the three generalized fixes:
**36/36 green**, corpus regression clean (44 captures, diff
empty vs `validation/wave15/corpus-after.txt`), full suite
**710/710** via pytest (674 at wave start + 36).

| Family | Shapes | First run | After fix |
|--------|--------|-----------|-----------|
| R1 figcaption-only markers | 4 | 4 pins held | — |
| R2 HTTP 402 | 4 | **3 defects** (R2a/b/d) | fixed (W24-R2) |
| R3 push-approval prompts | 7 | **1 defect** (R3a) + 6 pins held | fixed (W24-R3) |
| R4 robots mixed-case groups | 4 | 4 pins held | — |
| R5 llms duplicate H1 | 3 | 3 pins held | — |
| R6 sitemap mixed hosts | 3 | 3 pins held | — |
| R7 BG/SK/HR/SL phrases | 7 | **4 defects** (R7a–d) | fixed (W24-R7) |
| R8 summary-only phrases | 4 | 4 pins held | — |

## The three defect families

**W24-R2 — HTTP 402 fell through to OPEN.** The deliberate-
refusal family (444 Wave 5, 451 Wave 10, 418 Wave 23) had one
unvisited member: 402 Payment Required. With no 402 branch, a
paywall stub answered the final else and read OPEN whenever no
wall signal had fired — the exact W23-Q2 fallthrough species,
one code over. The fix adds the family's fourth branch
(`STATUS_402` evidence): 402 → WALLED, verdict governed by the
status, body evidence still naming the vendor (R2b →
WALLED/Generic by the Q2b/P2c composition), and a fired vendor
challenge still outranking the bare status (R2c →
CHALLENGED/Cloudflare, pin held from the first run).

**W24-R3 — push-approval sign-in prompts had no signal.** The
auth-prompt family (code entry, passkey, magic link, delivery
code, email-Continue, authenticator, SSO, QR) names every
ceremony an agent cannot complete except one: push approval,
where the page's only content asks the user to approve the
sign-in on another device. R3a read OPEN. The fix adds
`_is_push_approval_prompt` to the auth elif chain with
`PUSH_APPROVAL_PROMPT` evidence, two-keyed from birth per the
family discipline: (1) a full sign-in-approval phrase in
RENDERED visible text (never the bare word "approve"), (2) a
prompt marker — a `<button>` or `<form>` element. All six
guards held from the first run and remain as pins: prose with
the wording but no machinery stays OPEN (R3e), asset-filename
(push-approve.js, R3c) and stylesheet-class
(.push-approval-prompt, R3d) carriers stay OPEN, script-string
wording stays OPEN (R3g), a prompt inside a big served article
stays OPEN (R3b, the chain's served-page size gate), and a
prompt at a login URL agrees with the heuristic (R3f).
Accepted narrow boundary, ledgered in PROBLEMS.md: a push
waiting page carrying neither a button nor a form is prose to
this rule and stays OPEN.

**W24-R7 — Bulgarian, Slovak, Croatian, Slovenian challenge
phrases missing.** `_LOCALIZED_HUMAN_CHECK` covered 35+
languages but none of these four South-Slavic/West-Slavic
neighbours of covered Czech, Polish, and Ukrainian. All eight
strings (a "confirm you are not a robot" sentence + the
checkbox sentence per language) were grep-verified absent
before the battery was written. Slovak was deliberately
distinguished from Czech W23-Q7b: "Potvrďte, že nie ste robot"
("nie ste") vs "Potvrďte, že nejste robot" ("nejste") —
neither string contains the other, and the Slovak fixture
could not pass through the Czech entry. The fix adds all
eight phrases with per-language comments. Guards held: the
BG phrase on a big article stays OPEN (R7e, served-page
gate), the bare fragment "робот" stays OPEN (R7f, the J7g/Q7f
fragment rule), and the BG phrase inside a `<style>` block
stays OPEN (R7g, style suppression).

## The pins that mattered

- **R1 (figcaption):** the rendering-model symmetry with
  W23-Q1 is now pinned from both poles — stray text nodes
  inside `<picture>` are never presented (stripped), while
  `<figcaption>` text IS presented (fires on non-served
  pages, gated on served ones). No strip family names
  figcaption, and none should.
- **R8 (summary):** `<summary>` is presented by construction
  (it renders whether `<details>` is open or closed) — R8a
  (content-free) and R8b (closed details + paragraph) both
  fired CHALLENGED with zero code changes, extending M9a's
  details coverage from the size gate to the heading itself.
- **R4 (robots case):** RFC 9309 case-insensitivity composes
  across all three layers — an untracked `User-Agent:
  WALLCHECK` block grades PASS (the check grades tracked AI
  agents, not wallcheck itself), an uppercase agent VALUE
  (`GPTBOT`) still lands in its own group (WARN), and an
  uppercase directive NAME (`USER-AGENT: *`) still registers
  the wildcard (FAIL).
- **R5 (duplicate H1):** the llms content test is a test, not
  a style rule — a duplicated heading over a real index
  still PASSes; two title lines pointing nowhere still WARN
  (the E6a species said twice).
- **R6 (mixed sitemap hosts):** host consistency is an owner
  SEO wart, not an agent-access failure; www/non-www mixes
  PASS in urlset and index form, and locs need not share the
  sitemap's own host.
