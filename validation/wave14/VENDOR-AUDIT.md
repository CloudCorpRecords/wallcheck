# Wave 14 — Vendor-Attribution Audit (Leg C, records audit)

Auditor: `validation/wave14/audit_vendors.py` (re-runnable).
Reference round: round 10 (Wave 14 Leg A), the latest completed
round at audit time. Unlike Wave 13's 44-row spot-check, this is
a FULL check: every WALLED and CHALLENGED row's vendor cell
against its round-10 history line. Fresh captures were used only
for Leg A's three diffs (see STABILITY-9.md); no additional
re-probing was needed for this audit.

## Result: no vendor drift, no surgical fixes needed

- **499 rows parsed**, distribution **OPEN 416 · CHALLENGED 25 ·
  WALLED 35 · RATE_LIMITED 7 · UNREACHABLE 16 · LOGIN_GATED 0**,
  matching the INDEX.md header claim exactly (the header was
  updated by Leg A's todoist merge before this audit ran).
- **Round-10 history: 499 unique lines, 0 duplicates, 0 index
  URLs missing** from round 10.
- **WALLED/CHALLENGED rows missing a vendor or explicit
  unattributed note: 0.** The four Wave 13 unattributed-bare-403
  rows (catho.com.br, haaretz.com, hyatt.com, state.gov) still
  carry their explicit `unattributed (bare 403)` cells, and all
  four read vendor None in round 10 as well — the unattributed
  cells are corroborated, not stale.
- **Full vendor check: 60/60 rows agree** with round-10
  evidence on verdict, vendor, and status — **0 mismatches**.
  No vendor cell was changed by this audit, and none needed to
  be: no drift was found to fix. (The auditor's documented-hold
  entry for npmjs.com did not trigger — round 10 read
  CHALLENGED / Cloudflare, agreeing with standing, so the
  transport-pattern hold was not needed this round.)
- **Amazon note ‡ current through round 10**: the note now
  records round 10 reading CHALLENGED, agreeing with standing —
  no fresh capture was needed because round 10 itself agreed.

## What changed vs Wave 13's audit

Wave 13 audited 44 rows by spot-check against round 8 and made 4
surgical vendor-cell fixes. Wave 14 audits all 60 WALLED/
CHALLENGED rows against round 10 and makes 0 fixes — the vendor
column is stable across two consecutive full rounds, and the
unattributed cells Wave 13 introduced are holding up as honest
cells rather than gaps to fill. Explicit unattributed remains a
valid cell: no vendor was invented for any unattributed row.
