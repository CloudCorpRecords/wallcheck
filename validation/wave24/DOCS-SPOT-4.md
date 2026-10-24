# Wave 24 — Docs + Front-Doors Spot Check (Leg C)

## Corrections made

1. **README.md — suite counts were two waves stale.** The
   "New in 0.5.0-rc" paragraph's test chain ended at "Wave
   21's battery v13 took it to 608" and the Family section
   said "Waves 10–21 … took the suite to 608 tests". Both
   now run through Wave 24: the chain reads 638 (Wave 22) →
   674 (Wave 23) → **710 (Wave 24)**, and the Family section
   reads "Waves 10–24 ran fifteen more stability rounds
   (rounds 6–20) and adversarial batteries v2–v16, took the
   suite to 710 tests". Verified against the actual final
   count: **710/710 via pytest** (674 at wave start + 36
   battery v16 fixtures).
2. **SPEC.md — status line.** "**Release candidate 0.5.0-rc
   (Wave 9).**" now reads "**Release candidate 0.5.0-rc
   (Wave 9), hardened through Wave 24.**" The version stamp
   itself does not move — 0.5.0 final is stamped at ship
   time, per the launch hold.

## Front-doors check (huggingface.co)

`campaign/FRONT-DOORS.md` contains **no huggingface.co
entry** (grep: zero matches) — so there is no documented
directory-path posture to update with the Wave 23 evidence
(their directory path answering 401 LOGIN_GATED instead of
the census-era hard wall). Per the wave brief, the check is
noted here and no FRONT-DOORS edit was made. If a
huggingface row is ever added, it should be written from
the Wave 23 reading (401 LOGIN_GATED, 2026-10-24), not
from census-era data.

## Not touched

- `campaign/LAUNCH-POST.md` — Wave 1 numbers are launch
  copy, refreshed only at ship time (launch hold).
