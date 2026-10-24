# Wave 24 — Problems Ledger

Three defect families found by battery v16, all predicted in
HANDCLASS-16.md before the battery ran, all fixed generalized
with the battery fixtures as the capture-built tests. No
hand-classification errors this wave (28 of 36 shapes were
pins, and every pin held on the first run).

## W24-R2 — HTTP 402 fell through to OPEN (fixed)

- **Defect:** no 402 branch in the status chain; a Payment
  Required response with no other wall signal reached the
  final else (WALLED only for 401/403) and read OPEN.
- **Species:** the W23-Q2 (418) fallthrough, one code over.
  The deliberate-refusal family was 444/451/418; 402 was
  the one remaining deliberate-refusal code no battery had
  used.
- **Fix:** `elif status == 402` branch with `STATUS_402`
  evidence → WALLED, placed after 418 in the refusal family.
  Body evidence still names the vendor (402 + challenge
  phrase → WALLED/Generic); a fired vendor challenge still
  outranks the bare status (402 + Cloudflare → CHALLENGED).
- **Fixtures:** R2a (paywall body), R2b (challenge-phrase
  body), R2c (Cloudflare pin), R2d (empty body).

## W24-R3 — push-approval sign-in prompts had no signal (fixed)

- **Defect:** a page whose only content is "Approve this
  sign-in on your device" + prompt machinery read OPEN.
  Every other auth ceremony (code entry, passkey, magic
  link, delivery code, email-Continue, authenticator, SSO,
  QR) had a named signal; push approval had none.
- **Fix:** `_is_push_approval_prompt` in the auth elif
  chain (`PUSH_APPROVAL_PROMPT` evidence → LOGIN_GATED),
  two-keyed from birth: full sign-in-approval phrase in
  rendered visible text + a `<button>`/`<form>` marker.
  The siblings' served-page size gate applies via the chain.
- **Negative fixtures (held):** asset filename
  (push-approve.js), stylesheet class
  (.push-approval-prompt), script-string wording — all OPEN.
- **Honest limitation (accepted at birth, by design):** a
  push-approval waiting page carrying NEITHER a button nor
  a form is prose to this rule and stays OPEN (R3e pins the
  boundary deliberately). Real push waiting pages carry
  resend/cancel/other-options machinery in practice; the
  narrow birth follows the family rule (N3f species: the
  machinery key is load-bearing against prose false-fires).
  Revisit only on live evidence.

## W24-R7 — BG/SK/HR/SL challenge phrases missing (fixed)

- **Defect:** `_LOCALIZED_HUMAN_CHECK` had no Bulgarian,
  Slovak, Croatian, or Slovenian entry; a 403 challenge
  page in any of the four read WALLED (or OPEN on 200)
  instead of CHALLENGED.
- **Fix:** eight phrases added (demand + checkbox per
  language), grep-verified absent before writing. Slovak
  kept distinct from Czech W23-Q7b ("nie ste" ≠ "nejste").
- **Guards (held):** served-page gate (BG on article →
  OPEN), fragment rule ("робот" alone → OPEN), style-block
  suppression (BG in `<style>` → OPEN).
- **Fixtures:** R7a–R7d (one per language), R7e–R7g guards.

## Saturation note

Wave 24 is NOT clean: three genuine defect families. The
two-consecutive-clean-waves clock **resets again** — Wave 25
becomes clean-wave candidate #1 if defect-free.
