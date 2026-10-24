# Wave 17 — Round-13 re-probe measuring the Wave 16 fixes (Leg A)

**499/499 rows probed once each** with the Wave 16-fixed
classifier — the measurement Wave 16's STABILITY-11 deferred.
The runner (`validation/wave17/run_round13.py`, written fresh
for round 13 with the round number in exactly one constant)
imported the Wave 16 tree at launch: all eight Wave 16 fixes
were grep-verified present before probing (W16-001/001b
concatenated-text scans, W16-002 data-* strip, W16-003
style-block strip, W16-004 Location-header routing, W16-005
PASSKEY_PROMPT, W16-006 BOM-tolerant frontmatter, W16-007 JSON
data-block generalization, W16-008 MAGIC_LINK_FORM). All 499
history lines parse; zero missing URLs vs the INDEX table; zero
duplicate round-13 lines. The launch guard was verified live:
output growth was checked at 41 lines within the first minutes
and the runner completed all 499 with no incident.

**Tree note (stated plainly, as Wave 16's note did):** the
runner imported its classifier at launch, before the Wave 17
battery fixes landed — so round 13 measures the Wave 16 tree,
exactly as this wave's task specified. The Wave 17 battery
fixes (noscript/title suppression, QR prompts, entity JSON,
Nordic phrases, overlay challenges) are unmeasured on live
traffic until round 14. **Fresh captures below used the Wave 17
tree** (post-battery, pre-W17-007-fix) — the corroboration
question is the target's live behavior, and the one place the
tree difference mattered (rubygems.org) is called out
explicitly, with a post-fix live re-probe as the deciding
evidence.

Round-13 raw distribution: OPEN 414 · CHALLENGED 26 · WALLED 35 ·
RATE_LIMITED 7 · UNREACHABLE 16 · LOGIN_GATED 1.

## The 3 verdict diffs, all hand-checked with fresh captures

Every verdict diff was hand-checked with two fresh captures
(`validation/wave17/fresh_captures.py`, results in
`fresh-captures.json`) before merging — no diff was merged on
the round-13 reading alone. No vendor-wording-only diffs exist
this round.

| target | standing | round 13 | fresh capture(s) | disposition |
| --- | --- | --- | --- | --- |
| rubygems.org | OPEN 200 | LOGIN_GATED 200 (PASSKEY_PROMPT) | LOGIN_GATED 200, twice (PASSKEY_PROMPT, pre-fix tree) | **HELD at OPEN — the round's move is REJECTED, not merged.** Investigation of the live homepage (36 KB served, status 200) showed the PASSKEY_PROMPT firing is a FALSE POSITIVE of the Wave 16 rule: the page's only "webauthn" signals are asset filenames in its import map (`webauthn-json`, `src/webauthn`), and the page carries ordinary forms — configuration plus unrelated form machinery, not a passkey prompt. The Wave 16 rule as implemented never enforced its own design ("the page's only content is a prompt"): it read wording from raw body text including asset paths, and it had no served-page gate. Fixed this wave as W17-007 (see PROBLEMS.md): passkey/magic-link wording must appear in rendered visible text, and all three auth-form branches (code-entry, passkey, magic-link) now carry the served-page size gate. Post-fix live re-probe reads **OPEN 200**. This is the first Wave 16 fix to misfire on live traffic — caught by the round it was built to measure, which is the measurement working as designed. NOT a fix-driven move: the row does not change. |
| www.britishairways.com | UNREACHABLE | OPEN 200 | OPEN 200 (Akamai server-header presence only) + timeout (UNREACHABLE) | **HELD at UNREACHABLE.** The fresh evidence splits served-leaning (round + 1 fresh served) against one fresh failure — no corroboration triple (round + 2 agreeing fresh) exists for either side, so the strict rule holds the row, exactly as Wave 16's 1–1 split did. The served-leaning evidence (2 readings vs 1) is noted for round 14. NOT fix-driven: a fetch outcome involves no classifier rule. |
| www.forbes.com | OPEN 200 | CHALLENGED / DataDome 403 | Timeout (UNREACHABLE) + CHALLENGED / DataDome 403 | **HELD at OPEN.** Challenged readings number round + 1 fresh (2 of 3), not the round + 2 agreeing fresh the merge bar requires — no triple, so the standing row holds. The oscillator record extends: round-11 2–2 split, round-12 challenge + 2 fresh served (held OPEN), round-13 challenge + fresh challenge + fresh timeout. Flagged for re-check next round. NOT fix-driven: no Wave 16 rule touches DataDome detection. |

## Fix-driven moves: exactly zero

No Wave 16 rule moved a live row correctly in round 13:

- **Concatenated-text scans (W16-001/001b) — 0 moves.** No live
  row's verdict depended on a split-markup phrase.
- **Data-attribute strip (W16-002) — 0 moves.** No live row's
  verdict depended on a data-attribute token.
- **Style-block strip (W16-003) — 0 moves.** No live row's
  verdict depended on a stylesheet token.
- **Location-header routing (W16-004) — 0 moves.** No live row
  routes via a bare 3xx Location to a gate.
- **Passkey prompt (W16-005) — 0 moves, 1 misfire rejected.**
  The rule fired on rubygems.org and was proven wrong on
  inspection (see above); the row holds at OPEN and the rule
  itself was fixed (W17-007). A rejected misfire is not a move.
- **BOM-tolerant frontmatter (W16-006) — 0 moves.** Audit tool,
  not the index.
- **JSON data-block generalization (W16-007) — 0 moves.** No
  live row's verdict depended on a JSON-block vendor name.
- **Magic-link form (W16-008) — 0 moves.** No live row serves
  a magic-link form at a non-login URL.

Rounds 8–13 (six rounds) now stand with no classifier fix
moving a live row correctly; the Wave 16 fixes, like the
Wave 10–15 fixes before them, remain correctness insurance
for shapes live traffic has not shown this index, proven by
fixtures, unexercised by traffic — except for the one shape
traffic DID show (rubygems.org), which exposed a real gap and
got fixed. (The Wave 17 battery fixes, which landed after
this round, are measured by round 14.)

## Merge result

**Zero rows changed.** INDEX distribution unchanged: OPEN 415 ·
CHALLENGED 25 · WALLED 35 · RATE_LIMITED 7 · UNREACHABLE 17 ·
LOGIN_GATED 0 (499 rows, recount verified). The merged
distribution differs from the round-13 raw distribution by
exactly three holds (the three verdict diffs above).
