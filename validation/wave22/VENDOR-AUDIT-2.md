# Wave 22 — Vendor re-audit 2 (Leg C)

Wave 14 audited every WALLED/CHALLENGED vendor cell; this
re-audit (8 waves later) re-checks all of them against
round-17 evidence, with a fresh capture for every doubtful
cell. Method: parse all 61 WALLED/CHALLENGED rows from
INDEX.md (59 plain rows + 2 annotated rows: npmjs.com †,
amazon.com ‡), join each to its round-17 probe row, and
flag any INDEX vendor cell that disagrees with the
round-17 vendor field.

## Result: ZERO corrections — 61/61 cells verified

- **59/61 agree directly.** Every plain row's INDEX vendor
  cell matches its round-17 vendor field, or matches by
  the established wording rule ("unattributed (bare 403)"
  where the round vendor is None).
- **1 mismatch explained, not a misattribution.**
  apnews.com reads INDEX CHALLENGED/Cloudflare against a
  round-17 probe failure (UNREACHABLE/None). Wave 21
  already held this row on a 1–1 fresh split (round
  failure vs fresh challenge — transport noise). A new
  fresh capture confirms the cell: 403 with CF_RAY_HEADER,
  CF_MITIGATED_CHALLENGE, SERVER_CLOUDFLARE, and
  CF_CHALLENGE_PLATFORM, zero Wave 22-rule involvement.
  The standing cell stands; the round-17 probe failure
  was transport noise, not a posture change.
- **4 "unattributed (bare 403)" cells confirmed.** Fresh
  captures for catho.com.br, haaretz.com, hyatt.com, and
  state.gov all read WALLED with vendor None and only
  STATUS_403 evidence, zero Wave 22-rule involvement.
  Wave 13 made these cells explicit; round-17 agreed
  (bare 403, no signature); the fresh captures agree a
  third time. No signature has appeared on any of the
  four in 9 waves.
- **2 annotated rows checked.** npmjs.com †
  (CHALLENGED/Cloudflare) and amazon.com ‡
  (CHALLENGED/Generic) both carry vendor cells consistent
  with their standing notes and round-17 evidence; no
  change.

## Fresh captures

`vendor_captures.py` → `vendor-captures.json` (5 targets,
one honest fetch each, Wave 22-rule involvement checked
for every capture: no SVG-metadata phrase, no SSO
machinery, no GU/KN/NE/KM phrase in any capture).

## Conclusion

No vendor cell changed. The vendor column is current as
of round 17 plus the five fresh confirmations above.
Next re-audit due when the WALLED/CHALLENGED set moves
materially or after another ~8 waves, whichever comes
first.
