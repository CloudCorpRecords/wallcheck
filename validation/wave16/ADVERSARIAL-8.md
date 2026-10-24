# Wave 16 — Adversarial Battery v8: Results

**49 shapes, 21 mismatches before fixes, 0 after.** All 21
mismatches were predicted in HANDCLASS-8.md (zero surprises),
including the 3 extension shapes added during fix design (H2e,
H3d, H3e) and the 3 within-word-split shapes added on the
W16-001 re-run (H1f, H1g, H1h) — each was hand-classified and
run against the pre-fix tree before its fix landed, so none of
them is a post-hoc rationalization. All fixed test-first and
generalized; 28 pins held. Full suite after fixes: **375/375**
(321 prior + 49 battery pins + 5 guards). Real-capture corpus:
replayed after the fixes (see PROBLEMS.md) — no verdict/vendor
change on any real wall capture.

## Mismatches → fixes (21 defects, 8 fix families)

| shape | pre-fix | hand | fix |
| --- | --- | --- | --- |
| H1a (traffic phrase split across elements) | WALLED | CHALLENGED / Generic | W16-001: TRAFFIC_CHECK words + cues also matched against space-separated visible text (W15-003's treatment, extended to this branch). |
| H1b (verification cue split within a word) | WALLED | CHALLENGED / Generic | W16-001b: a third scan variant — tags removed entirely (no space substitution), because inline elements add no space to rendered text. Applies to TRAFFIC_CHECK, human-check, JS_PROOF, and the captcha token. |
| H1f (human-check phrase split within a word) | WALLED | CHALLENGED / Generic | W16-001b, same variant in the human-check branches. |
| H1g (JS-proof phrase split within a word) | WALLED | CHALLENGED / Generic | W16-001b, same variant in the JS_PROOF branch. |
| H1h (captcha token split within a word) | WALLED | CHALLENGED / Generic | W16-001b, same variant in the captcha branch (presence + survival). |
| H2a (human-check phrase only in a data-* attribute, on a content page) | CHALLENGED / Generic | OPEN | W16-002: data-* attributes are configuration, never rendered — the "survives stripping" test now also requires surviving data-attribute stripping, and the vendor scan strips data-* values when the page has visible text. Content-free pages still fire (H2b/H2d). |
| H2c (vendor name only in a data-* attribute, on a content page) | CHALLENGED / PerimeterX | OPEN | W16-002, vendor-scan half. |
| H2e ("captcha" token only in a data-attribute name, on a content page) | CHALLENGED / Generic | OPEN | W16-002, captcha-branch half. |
| H3b (challenge sentence only in a stylesheet, on a content page) | CHALLENGED / Generic | OPEN | W16-003: <style> blocks are configuration too — the survival test and the vendor scan strip them when the page has visible text. Content-free pages still fire (H3a/H3f). |
| H3d ("captcha" token only in a stylesheet class selector, on a content page) | CHALLENGED / Generic | OPEN | W16-003, captcha-branch half. |
| H3e (vendor name only in a stylesheet, on a content page) | CHALLENGED / PerimeterX | OPEN | W16-003, vendor-scan half. |
| H4a (307 to a challenge target) | OPEN | CHALLENGED / Generic | W16-004: the HTTP Location header on a 3xx response is collected as a redirect target with meta-refresh semantics. |
| H4b (308 to a login target) | OPEN | LOGIN_GATED | W16-004, same rule in login form. |
| H4d (302 to a challenge target) | OPEN | CHALLENGED / Generic | W16-004, generalized across 3xx codes. |
| H4e (307 to a challenge target at a login URL) | LOGIN_GATED | CHALLENGED / Generic | W16-004 + precedence: the redirect-to-challenge branch precedes the login heuristic (S5a principle in redirect form). |
| H5a (passkey prompt at a non-login URL) | OPEN | LOGIN_GATED | W16-005: PASSKEY_PROMPT — passkey/WebAuthn wording PLUS a prompt marker (button, form, input, or credentials-API reference). Two-keyed like CODE_ENTRY_FORM; prose and bare links cannot fire (H5b/H5e guards). |
| H5d (passkey button + identity wording, non-login URL) | OPEN | LOGIN_GATED | W16-005, same rule. |
| H7d (BOM + frontmatter-only llms.txt) | PASS | WARN | W16-006: a leading UTF-8 BOM is stripped before the frontmatter anchor — a BOM is not content, and it defeated the W15-009 strip. |
| H9a (vendor name in an application/json data block, on a content page) | CHALLENGED / PerimeterX | OPEN | W16-007: the W15-001 data-block strip generalizes from ld+json to every JSON script type (application/json, text/json). Loader scripts untouched (guard pin). |
| H10a (magic-link email form, non-login URL) | OPEN | LOGIN_GATED | W16-008: MAGIC_LINK_FORM — an email input PLUS auth-link wording ("sign-in link", "magic link", "password reset"). Newsletter forms and bare links cannot fire (H10b/H10d guards). |
| H10c (password-reset email form, non-login URL) | OPEN | LOGIN_GATED | W16-008, same rule. |

## Pins that held (28 shapes)

H1c/H1d/H1e (traffic splits and the contiguous case), H2b/H2d
(data-attribute-only pages), H3a/H3c/H3f (CSS content as the
page, on a large article, content-free vendor style), H4c
(redirect to content), H5b/H5c/H5e (passkey link, login-URL
prompt, passkey prose), H6a–H6e (robots absence species),
H7a/H7b/H7c/H7e (charset and BOM-with-content), H8a–H8d
(circular sitemaps), H9b (content-free JSON block), H10b/H10d
(newsletter form, bare sign-in link).

## Notable interactions

- **W16-001b is the third text model, not a second scan.**
  The classifier now reads three texts: raw markup, visible
  text (tags → spaces), and concatenated text (tags removed).
  Block-level splits need the spaced variant (H1a); within-word
  splits need the concatenated variant (H1b/H1f/H1g/H1h); raw
  markup catches everything else. No single variant is
  "rendered text" — rendered text is all three, and the
  survival guards (script/style/data stripping) apply to the
  concatenated variant exactly as they do to the spaced one,
  which is why script-only split phrases stay suppressed
  (guard pin).
- **W16-002/W16-003 complete the configuration family.**
  After script JSON (W14-001), JSON-LD (W15-001), and now
  data-* attributes and stylesheets, the rule is uniform: a
  signal that lives only in configuration is not a presented
  wall when the page has visible content — and always is the
  page when it has none. The family is now closed by
  principle; new members would be new configuration species,
  not new rules.
- **W16-004 matters to offline users, not live probes.**
  Live probes follow redirects and classify the landing page;
  the Location-header rule exists for `classify()` callers
  whose pipelines fetch their own way. The fix is still
  generalized (all 3xx, both target kinds) because the MCP
  `classify` tool promises the same verdicts as the probe.
- **W16-005/W16-008 narrow the F5 limitation further.**
  The Wave 14 F5 limitation (password sign-in forms are not
  login signals) now has three two-keyed exceptions: code-entry
  forms, passkey prompts, and magic-link forms. The general
  password-form species remains open deliberately — a password
  input plus prose is still too broad a signal, and no narrower
  key for it has appeared.

## What this wave says about saturation

Battery v8 found 21 genuine defects on shapes no earlier
battery exercised — the adversarial surface is still not
exhausted, and Wave 16 is NOT a clean wave on the battery
prong regardless of Leg A's outcome. The saturation clock,
reset by Wave 15, stays reset: a clean wave needs zero defects
in BOTH the battery and the measurement round.
