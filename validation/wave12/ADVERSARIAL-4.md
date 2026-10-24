# Wave 12 — Adversarial Battery v4: Results

**27 shapes, 11 mismatches before fixes, 0 after.** Every mismatch
was a genuine defect (no honest limitations this wave); every fix
was generalized and pinned in `tests/test_adversarial4.py`. Full
suite after fixes: **210/210** (183 prior + 27 new). Real-capture
corpus: zero verdict/vendor changes.

## Mismatches → fixes (6 defects)

| shape | pre-fix | hand | fix |
| --- | --- | --- | --- |
| D1a–D1e (PL/TR/AR/ZH/RU challenges) | WALLED | CHALLENGED / Generic | W12-001: localized list gains 2 phrases per language |
| D3a ("Browser check in progress" stub) | OPEN | CHALLENGED / Generic | W12-002: "browser check" joins the JS_PROOF list (small-page gated) |
| D5a (login form action → challenge endpoint) | CHALLENGED / Generic | LOGIN_GATED | W12-003: form-action targets split into their own evidence code, yielding to identified login pages |
| D7c (JSON-LD at /llms.txt) | PASS | WARN | W12-004: non-error JSON bodies read WARN, not PASS |
| D7d (markdown body, text/html content-type) | FAIL | PASS | W12-005: markdown-body carve-out in the llms check only |
| D8a/D8b (gzipped sitemaps, direct + declared) | WARN | PASS | W12-006: audit fetcher decompresses gzip bodies |

## Pins that held (16 shapes)

D2a/D2b/D2c (countdown interstitials — timer adds nothing; the
redirect/form target decides), D3b (20 KB article mentioning
"browser check" stays OPEN — the served-page gate holds the new
phrase), D4a/D4b (consent hybrids — the B5b boundary holds even
when the gate says it blocks content; human-check prose still
owns the challenge), D5b (stub form action still CHALLENGED —
guards the W12-003 split), D6a/D6b/D6c (robots carve-out
semantics from Wave 11 hold), D7a/D7b (markdown/plain-text llms
pass), D9a–D9d (3+ hop chains — the final answer owns the
verdict at any chain length).

## Notable interactions

- **W12-003 is a rule-interaction fix, not a phrase fix.** One
  evidence code (REDIRECT_TO_CHALLENGE) was carrying two species
  with different yield rules — routing stubs (never yield) and
  form actions (yield on login pages). The fix splits the code,
  which is the smallest change that expresses both rules. The
  D5b pin exists specifically to catch over-correction.
- **W12-004 refines, not reverses, Wave 10 B9a.** B9a's comment
  said a non-error JSON body is "not failed here" — it still is
  not failed. WARN is the grade B9a left unconsidered, between
  its FAIL (error documents) and the old PASS.
- **W12-005's carve-out is deliberately narrow.** Only the llms
  check consults it, and only for bodies with markdown structure
  and zero HTML tags. A file mixing markdown with raw HTML still
  fails — the conservative side stays FAIL.

## What this wave says about saturation

Battery v4 found 6 genuine defects on shapes no earlier battery
exercised — the adversarial surface is not exhausted. Combined
with Leg A's zero fix-driven moves, the picture is: the
classifier is correct on every shape live traffic has shown it,
and still wrong on shapes it has not yet been shown. That is
exactly why the saturation test requires defect-free waves, not
just clean stability rounds — and why Wave 12 resets the clock
(see OVERNIGHT.md).
