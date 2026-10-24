# Wave 26 — Vendor-Share Refresh (Leg C)

Recomputed from the standing INDEX.md table (500 rows) with
`validation/wave26/vendor_shares.py`, each share verified
against the rows themselves. The two annotated rows (npmjs.com
†, amazon.com ‡) do not match the row regex — their link cells
carry the note marker — and were counted by hand from the raw
table, the standing analyzer-invisible pair every wave checks.

## Current shares

**WALLED — 37 rows**

| Vendor | Rows | Share |
|--------|------|-------|
| Akamai | 22 | 59% |
| Cloudflare | 5 | 14% |
| unattributed (bare 403) | 4 | 11% |
| AWS CloudFront | 3 | 8% |
| unattributed (402 pair, vendor none) | 2 | 5% |
| Imperva | 1 | 3% |

**CHALLENGED — 26 rows**

| Vendor | Rows | Share |
|--------|------|-------|
| DataDome | 15 | 58% |
| Cloudflare | 5 (incl. npmjs.com †) | 19% |
| PerimeterX | 3 | 12% |
| AWS WAF | 1 | 4% |
| Microsoft Azure WAF | 1 | 4% |
| Generic | 1 (amazon.com ‡) | 4% |

Movement since the Wave 17 correction (Akamai 22/35): the
WALLED denominator grew 35 → 37 on round 21's two fix-driven
402 merges (telegraph.co.uk, usatoday.com — vendor none), and
CHALLENGED composition shifted across rounds 14–21 (wayfair.com
and goodrx.com joined PerimeterX in round 20/21 readings;
forbes.com joined DataDome in round 15). DataDome's challenged
set stands at 15 properties, not the five the card named when
it was written against the smaller index.

## Corrections made (before → after)

1. **campaign/REPORT-CARD-AKAMAI.md** — "Current index
   (499 rows, Wave 17 re-verified): Akamai holds 22 of the 35
   WALLED rows" → "Current index (500 rows, Wave 26
   re-verified): Akamai holds 22 of the 37 WALLED rows". The
   Akamai count (22) was still right; the denominator and the
   index size were stale.
2. **campaign/REPORT-CARD-DATADOME.md** (scorecard) — "Five
   major properties in our index challenge the identified
   agent" → "Fifteen properties in our index challenge the
   identified agent". (Body) — "Five properties, all answering
   an honestly identified, one-shot agent request with a
   challenge (HTTP 403 or 401):" → "15 of the 26 CHALLENGED
   rows. Fifteen properties, all answering … ; the five
   majors:" — the five named properties (monster.com,
   nytimes.com, etsy.com, reuters.com, wsj.com) all still stand
   as DataDome CHALLENGED rows; they are now presented as the
   majors of fifteen, not the whole set.
3. **campaign/REPORT-CARD-PERIMETERX.md** (scorecard) — "The
   one PerimeterX property in our index is a top freelance
   marketplace" → "Three properties in our index are
   challenged by PerimeterX, including a top freelance
   marketplace". (Body) — "Our index's PerimeterX row is not a
   scraper farm. It is **Fiverr**" → "Our index's best-known
   PerimeterX row is not a scraper farm. It is **Fiverr** …
   (the current index also records PerimeterX challenges at
   wayfair.com and goodrx.com)". Fiverr's own row is unchanged
   (CHALLENGED / PerimeterX / 403).

## Verified current — no correction

- **campaign/REPORT-CARD-IMPERVA.md** — "The one Imperva
  property in our index" is still exactly true: guru.com is
  the index's only Imperva row (WALLED / Imperva / 403).
- **campaign/REPORT-CARD-CLOUDFLARE.md** — cites no index
  vendor share (its numbers are the Upwork incident narrative,
  not index shares); nothing to correct. For the record,
  Cloudflare currently holds 5 WALLED + 5 CHALLENGED rows.
- Grades were not touched anywhere: this leg corrects cited
  shares, it does not re-grade.

## Not touched

- `campaign/LAUNCH-POST.md` — Wave 1 numbers are launch copy,
  refreshed only at ship time (launch hold).
