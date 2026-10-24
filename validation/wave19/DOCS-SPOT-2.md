# Wave 19 — Docs Spot-Check, Leg C (DOGFOOD addendum)

Scope (per the wave task): write the DOGFOOD.md Wave 18 addendum
that Wave 18's docs spot-check recorded as due. LAUNCH-POST.md's
Wave 1 numbers were NOT touched (launch copy, refresh at ship —
Wave 9's rule stands).

## Change made

- **DOGFOOD.md, Wave 18 addendum appended** after the Wave 17
  entry (the chain previously ended at Wave 17's battery, 423
  mid-wave count). The addendum covers: battery v10 (48 shapes,
  6 fix families), round-14 reclassification (499/499 probed,
  the 123/499 external-kill incident and the Wave 17 tree-copy
  resume, 5 merges with ubereats.com the only fix-driven move,
  7 holds including the three Wave 17 QR-prompt misfires
  rejected and fixed as W18-007), the row-500 addition
  (search.brave.com, OPEN), the docs spot-check (423-vs-428
  resolved — 428 was right at Wave 17's end), the 500-row
  distribution (OPEN 418 / CHALLENGED 21 / WALLED 35 /
  RATE_LIMITED 7 / UNREACHABLE 17 / LOGIN_GATED 2), and vendor
  shares on the 56 WALLED+CHALLENGED rows recomputed from
  INDEX.md itself (WALLED — Akamai 22, Cloudflare 5, AWS
  CloudFront 3, Imperva 1, unattributed bare-403 4; CHALLENGED —
  DataDome 14, Cloudflare 4, PerimeterX 1, Microsoft Azure WAF
  1, AWS WAF 1), and the Wave 18 final suite count (481).

## Verified current (no change needed)

- **INDEX.md header distribution** (recounted from the table
  during the vendor-share computation): OPEN 418 · CHALLENGED
  21 · WALLED 35 · RATE_LIMITED 7 · UNREACHABLE 17 ·
  LOGIN_GATED 2 = 500 rows. The header line matches exactly;
  no round-15 merges have landed yet (round 15 still probing
  at the time of writing), so no distribution change is due.
- **Directory census denominator ("4 of 499").** Kept as the
  census's own denominator: census v2 measured 499 domains, and
  the 500th row was not censused. Changing it to "4 of 500"
  would misstate the census (same ruling as Wave 18's D-05
  verification).
- **SPEC.md version stamp (0.5.0-rc).** No version files were
  touched this wave; the tree remains 0.5.0-rc + unreleased
  fixes, consistent with Wave 12's conclusion that the next
  stamp is 0.5.0 final, not another rc.

## Observation (not a correction — out of scope)

- **Wave 19's own numbers** (battery v11, round 15, suite 532)
  belong in the next docs pass, once round 15 lands; this leg's
  scope was the Wave 18 addendum only, so Wave 19 is recorded
  in validation/wave19/ (ADVERSARIAL-11.md, STABILITY-14.md
  when round 15 completes) rather than in DOGFOOD.md yet.
