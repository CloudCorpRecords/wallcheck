# Wave 26 — Stability Round 22

Round 22 re-probed all 500 index rows with the Wave 25-fixed
classifier (imported at launch, before any Wave 26 battery edit
landed — the round measures one tree, the Wave 25 tree, end to
end; the Wave 26 rules are unmeasured until round 23). All 500
probes completed in a single run, no runner incident. Wave 25's
three fixes were grep-verified present in the tree before
launch (W25-T3 `_is_employee_id_prompt`, W25-T7 SR/MK/LV/LT
phrases, W25-T8d `_PLACEHOLDER_ATTR_RE`).

Results: 497 rows agree with standing; 3 verdict diffs, each
hand-checked with two fresh captures under the strict rule
(1–1 split holds the row). **Two merges, one hold, zero
fix-driven moves.** Fresh-capture evidence lives in
`validation/wave26/fresh-captures.json`; every fresh capture
recorded zero Wave 25-rule involvement and zero Wave 26-rule
involvement, so no corroboration is tree-contaminated.

## Merged (2)

| Row | Before | Round 22 | Fresh ×2 | After | Class |
|-----|--------|----------|----------|-------|-------|
| apnews.com | UNREACHABLE / — / — | CHALLENGED / Cloudflare / 403 | CHALLENGED / Cloudflare / 403 ×2 | **CHALLENGED / Cloudflare / 403** | transport recovery |
| www.webex.com | WALLED / Akamai / 403 | OPEN / — / 200 | OPEN / — / 200 ×2 | **OPEN / — / 200** | target-side |

- **apnews.com** — round 20's three consecutive failures
  retired this row to UNREACHABLE (the britishairways Wave 15
  pattern); round 22 answered with the Cloudflare challenge
  that stood behind the failures all along, and both fresh
  captures agree (CF_MITIGATED_CHALLENGE evidence). A delivery
  recovery, not a posture change and not a rule move.
- **www.webex.com** — the Akamai wall that arrived in round 9
  (and produced split-holds in rounds 17 and 19) has lifted:
  round 22 and both fresh captures serve the real page
  (STATUS_200 only). Target-side; no rule involved on either
  pole.

## Held (1)

| Row | Standing | Round 22 | Fresh ×2 | Disposition |
|-----|----------|----------|----------|-------------|
| www.forbes.com | CHALLENGED / DataDome / 403 | OPEN / — / 200 | CHALLENGED / DataDome / 403 ×2 | **held CHALLENGED** |

forbes.com is the index's documented intermittent oscillator
(rounds 11, 12, 13, 18 leanings both ways; merged CHALLENGED
in round 15 on the corroboration triple). Round 22 caught a
served window; both fresh captures answered the DataDome
challenge, agreeing with standing rather than the round — no
corroboration triple for OPEN, so the row holds. The
oscillator record extends; it does not exempt the row, and a
future served triple would move it back.

## Hand-checked, agreeing with standing (2)

- **npmjs.com** — CHALLENGED / Cloudflare / 403 in round 22,
  agreeing with standing (the † row; its transport-pattern
  sightings continue in the background but this round read
  the challenge directly).
- **amazon.com** — CHALLENGED / Generic / 200 in round 22,
  agreeing with standing (the ‡ row; oscillator note extends,
  no merge either way this round).

## Fix-driven moves under the Wave 25 rules: zero

The Wave 25 fixes measured **zero live effect** in round 22:
no diff's fresh evidence carries an employee-ID prompt, a
Serbian / Macedonian / Latvian / Lithuanian phrase, or a
challenge phrase carried only by a placeholder attribute,
and no other row moved. The fixes stand as battery-proven
rules awaiting their traffic, the Wave 22/23/24 pattern.

## Distribution after merges

OPEN 414 · CHALLENGED 27 · WALLED 36 · RATE_LIMITED 7 ·
UNREACHABLE 16 · LOGIN_GATED 0 (500 rows; recount verified
against the table).
