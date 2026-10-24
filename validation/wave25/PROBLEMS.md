# Wave 25 — Problems Ledger

Three defect families found by battery v17, all predicted in
HANDCLASS-17.md before the battery ran (T8d was written as a
pin on the doctrine and the classifier failed it), all fixed
generalized with the battery fixtures as the capture-built
tests. One hand-classification error (T2), caught by the
Wave 6 suite before any fix shipped. Three harness errors of
mine during the first runs (wrong audit check names, the
grade key, and a fixture whose form action masked its own
gap) — all mine, none the classifier's, each corrected and
re-run before the failure list above was trusted.

## W25-T3 — employee-ID sign-in prompts had no signal (fixed)

- **Defect:** a page whose only content is an employee-ID
  sign-in form (workforce identifier + password field) read
  OPEN; every other credential ceremony in the auth family
  had a named signal.
- **Fix:** `_is_employee_id_prompt` in the auth elif chain
  (`EMPLOYEE_ID_PROMPT` evidence → LOGIN_GATED), two-keyed
  from birth: workforce-identifier wording in rendered
  visible text + credential machinery (password input or
  form). The siblings' served-page size gate applies via
  the chain.
- **Negative fixtures (held):** asset filename
  (employee-id.js), stylesheet class (.employee-id-field),
  script-string wording beside a real password input — all
  OPEN. Prose without machinery (T3e) stays OPEN by design:
  the machinery key is load-bearing, the R3e/N3f species.

## W25-T7 — SR/MK/LV/LT challenge phrases missing (fixed)

- **Defect:** `_LOCALIZED_HUMAN_CHECK` had no Serbian,
  Macedonian, Latvian, or Lithuanian entry; a 403 challenge
  page in any of the four read WALLED instead of CHALLENGED.
- **Fix:** eight phrases added (demand + checkbox per
  language), grep-verified absent before writing. Serbian
  kept in Cyrillic (Croatian W24-R7c is Latin); Macedonian
  kept distinct from Bulgarian W24-R7a ("дека" ≠ ", че",
  "сум" ≠ "съм").
- **Guards (held):** served-page gate (LV on article →
  OPEN), fragment rule ("robotas" alone → OPEN), style-block
  suppression (MK in `<style>` → OPEN).
- **Fixtures:** T7a–T7d (one per language), T7e–T7g guards.

## W25-T8d — placeholder-only phrase drove CHALLENGED (fixed)

- **Defect:** a challenge phrase living ONLY in a
  `placeholder` attribute fired GENERIC_HUMAN_CHECK on a
  page with real visible content. A placeholder is a hint —
  ghost text in an empty field — not presented content, but
  no strip named the attribute, so both the raw scan and
  the corroboration variant read it as page text.
- **Fix:** `_PLACEHOLDER_ATTR_RE` stripped alongside
  `_DATA_ATTR_RE` in both survival variants
  (`bl_noscript_clean`, `bl_generic_clean`) — the W16-002/
  003 data-attribute doctrine extended to the one attribute
  species it had not named. Content-free pages still fire
  via the raw scan (the configuration-is-the-page rule).
- **Fixtures:** T8d (the defect), T8a/T8b/T8c (textarea
  default text is presented — fires/gates like a paragraph),
  T8e (innocuous textarea is furniture).

## Hand-correction — T2 (HTTP 410) is NOT a defect

- **Error (mine):** HANDCLASS-17 originally classified 410
  Gone as WALLED under a "deliberate refusal" reading, and
  a STATUS_410 branch was briefly added on that basis.
- **Caught by:** the existing suite — Wave 6's pin
  `test_s1c_410_gone` failed against the new branch on the
  first full-suite run.
- **Why the pin is right:** 410 is a definitive answer about
  the resource (the 404 species: Wave 2 W2-002, Wave 6
  W6-S1c pinned 410 → OPEN), universal to all clients; the
  refusal family (444/451/418/402) declines THIS requester
  for content that exists. 410 also sits outside
  GENERIC_OK_STATUSES, so a phrase in a 410 body does not
  fire (W6-S1b at 404). The branch was reverted; no
  classifier change ships for T2; the corrected
  classification is recorded in HANDCLASS-17.md.

## Saturation note

Wave 25 is NOT clean: three genuine defect families. The
two-consecutive-clean-waves clock **resets again** — Wave 26
becomes clean-wave candidate #1 if defect-free.
