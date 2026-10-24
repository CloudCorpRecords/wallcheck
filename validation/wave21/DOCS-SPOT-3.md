# Wave 21 — Docs consistency spot-check (Leg D)

Checked README.md, SPEC.md, and INDEX.md against measured
reality at Wave 21's end (suite 608/608, index 500 rows,
rounds 2–17 merged).

## Corrections made

- **README.md suite count (two spots):** the Wave 9–18 chain
  (120 → 428 → 481) had gone stale — Waves 19 and 20 never
  updated it. Corrected: Wave 19's battery v11 took it to
  532, Wave 20's battery v12 to 571, Wave 21's battery v13
  to 608 (verified: full suite 608/608 green). The wave-list
  paragraph now reads Waves 10–21, rounds 6–17, batteries
  v2–v13, suite 608.
- **SPEC.md status line:** Wave 18 → Wave 21 (0.5.0-rc +
  unreleased fixes), stability rounds 2–14 → 2–17, rounds
  15–17 moves noted (six, ten, zero), adopter spot-checks
  noted as Wave 16's and Wave 20's (both 4/4 still
  publishing).
- **INDEX.md header distribution:** verified, no change
  needed — "500 sites. Verdicts: OPEN 415 · CHALLENGED 26 ·
  WALLED 35 · RATE_LIMITED 7 · UNREACHABLE 17 · LOGIN_GATED
  0" matches the post-round-17 recount exactly (Wave 21
  merged zero rows). The Wave 21 round-17 narrative
  parenthetical was appended to the header's round chain.

## Verified current (no change)

- INDEX.md round-chain parentheticals through round 17;
  the †/‡ notes; the 9-vendor list; 4/499 adopters from
  census v2 (index has since grown to 500 rows — the
  census denominator is historical, not an error).
- LAUNCH-POST.md's Wave 1 numbers untouched per Wave 9's
  rule (launch copy, refresh at ship).

## Known lag (not a factual error)

- SPEC.md's per-section semantic notes stop at Wave 20
  (iframe routing, localized JS-proof/human-check). Wave
  21's semantics (object/embed routing, authenticator
  prompts, high-traffic throttle cause, non-HTTP-scheme
  locs, TA/TE/MR/PA phrases) are documented in
  validation/wave21/PROBLEMS.md and in code comments; the
  status line's "unreleased fixes" covers them. A future
  docs pass may fold them into SPEC's sections.
