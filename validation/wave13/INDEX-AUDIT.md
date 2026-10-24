# Wave 13 — INDEX.md Records Audit (Leg C, no re-probing)

Auditor: `validation/wave13/audit_index.py` (re-runnable).
Reference round: round 8 (Wave 12), the latest completed round
at audit time; round 9 was still probing and is NOT used here.

## Result: no verdict drift

- **499 rows parsed** (after fixing the auditor's own strict
  regex, which first missed the two note-suffixed rows — see
  below), distribution **OPEN 414 · CHALLENGED 25 · WALLED 34 ·
  RATE_LIMITED 7 · UNREACHABLE 18 · LOGIN_GATED 1**, matching
  the INDEX.md header claim exactly.
- **Round-8 history: 499 unique lines, 0 duplicates, 0 index
  URLs missing** from round 8.
- **Spot-check: 44 rows** (every 13th row + the four round-8
  diff rows + the LOGIN_GATED row) across **19 categories**,
  compared on verdict, vendor, and status against their round-8
  history lines: **0 mismatches**. The two documented Wave 12
  holds both confirmed in place: npmjs.com held CHALLENGED /
  Cloudflare against a round-8 UNREACHABLE (known transport
  pattern), webex.com held OPEN against a round-8 WALLED /
  Akamai (single uncorroborated edge deny).
- **Amazon note ‡ current through round 8**: the note states
  CHALLENGED as of Wave 12 round 8 with the full oscillation
  record, matching STABILITY-7.md. (Round 9 may extend it;
  that is STABILITY-8.md's job, not this audit's.)

## Auditor bug found and fixed (not index drift)

The first audit run parsed only 497 rows and reported
CHALLENGED 23 vs the header's 25. Cause: the row regex
required `) |` immediately after the URL, but two rows carry
a note suffix in the Site cell:
`[www.npmjs.com](...) — see note †` and
`[www.amazon.com](...) — see note ‡`. The regex was relaxed
to allow note text between the link and the verdict column;
the re-run parses all 499 rows and matches the header exactly.
The index was right; the auditor was wrong — recorded here so
the next auditor does not re-litigate it.

## Surgical fixes applied to INDEX.md (4 rows)

Four WALLED rows carried vendor "—" with no explicit
attribution. All four are bare 403s with vendor None in
history rounds 5–8 (and catho.com.br already in round 9) and
are documented as unattributed in Wave 8's PATHS-2.md — but
the table itself did not say so, and "—" on a WALLED row is
ambiguous between "no signature" and "not checked". Each
vendor cell now reads `unattributed (bare 403)` (verdicts,
statuses, and last-checked columns untouched):

- www.catho.com.br (jobs) — WALLED, 403, W7 expansion
- www.haaretz.com (news) — WALLED, 403, W7 expansion
- www.hyatt.com (travel) — WALLED, 403, W5 expansion
- www.state.gov (civic) — WALLED, 403, W5 expansion

Re-run after the edits: **WALLED/CHALLENGED rows missing a
vendor: 0**. The Wave 5/7 capture corpus corroborates: hyatt,
state, catho, and haaretz captures all classify WALLED with
vendor None.
