# Wave 26 — Problems Ledger

Three defect families found by battery v18, all predicted in
HANDCLASS-18.md before the battery ran (7 first-run failures:
U3a, U6c, U6d, U7a–U7d), all fixed generalized with the
battery fixtures as the capture-built tests. The other 34
shapes were pins and held on the first run. No hand-
classification errors this wave, and no older pin vetoed any
fix — the full suite ran 788/788 after the fixes (747 + 41),
and each fix was checked against the older pins in its area
before it shipped (the Wave 25 lesson): the U6 authority test
against K6/L6/N6/Q6 loc pins, the U7 additions against the
Spanish/Finnish substring boundaries, the U3 two-key design
against the T3e/R3e prose-guard species.

## W26-U3 — badge-tap sign-in prompts had no signal (fixed)

- **Defect:** a page whose only content is a badge-tap
  sign-in prompt ("Tap your badge on the reader to sign in."
  plus a retry button) read OPEN; every other credential
  ceremony in the auth family had a named signal, but the
  physical one — no password, no code, nothing typed — had
  none.
- **Fix:** `_is_badge_tap_prompt` in the auth elif chain
  (`BADGE_TAP_PROMPT` evidence → LOGIN_GATED), two-keyed
  from birth: a full badge-tap phrase in rendered visible
  text (never the bare word "badge") + prompt machinery
  (a <button> or <form>). The siblings' served-page size
  gate applies via the branch.
- **Negative fixtures (held):** asset filename
  (badge-tap.js), stylesheet class (.badge-tap-prompt),
  script-string wording beside a real button and form — all
  OPEN. Prose without machinery (U3e, a building-access
  note) stays OPEN by design: the machinery key is
  load-bearing, the T3e/R3e species. Accepted narrow
  boundary, ledgered at birth (the R3 species): a badge
  waiting page carrying neither a button nor a form is
  prose to this rule.

## W26-U6 — percent-encoded sitemap hosts counted (fixed)

- **Defect:** `_has_nonempty_loc` accepted any non-empty
  http(s) loc, so a urlset whose only locs carried
  percent-encoded hosts (`https://%65xample.com/a`) passed
  the sitemap check — although the WHATWG host parser
  rejects "%" in hosts of special schemes, so the loc does
  not parse as a URL at all under standard URL parsing and
  names no crawlable destination.
- **Fix:** in `_has_nonempty_loc`, for absolute locs the
  authority component is extracted and a "%" in the host
  (after any userinfo) skips the entry. Path
  percent-encoding is normal URL practice and untouched.
- **Fixtures:** U6c/U6d (the defect), U6a (path encoding
  passes), U6b (one good loc suffices).
- **Pin check (Wave 25 lesson):** K6 relative/query locs
  carry no "://" and skip the authority test; L6 fragment
  locs are rejected earlier; N6 non-HTTP schemes are
  rejected earlier; Q6 uppercase-scheme locs split on "://"
  and carry no "%" in the host. Full suite green.

## W26-U7 — CA/ET/HY/KA challenge phrases missing (fixed)

- **Defect:** `_LOCALIZED_HUMAN_CHECK` had no Catalan,
  Estonian, Armenian, or Georgian entry; a 403 challenge
  page in any of the four read WALLED instead of CHALLENGED.
- **Fix:** eight phrases added (demand + checkbox per
  language), grep-verified absent before writing. Catalan
  kept distinct from Spanish ("soc" ≠ "soy"), Estonian
  from Finnish ("ei ole robot" ≠ "en ole robotti");
  Armenian and Georgian are unique scripts.
- **Guards (held):** served-page gate (ET on article →
  OPEN), fragment rule ("robot" alone → OPEN), style-block
  suppression (HY in `<style>` → OPEN).
- **Fixtures:** U7a–U7d (one per language), U7e–U7g guards.

## Saturation note

Wave 26 is NOT clean: three genuine defect families. The
two-consecutive-clean-waves clock **resets again** — Wave 27
becomes clean-wave candidate #1 if defect-free.
