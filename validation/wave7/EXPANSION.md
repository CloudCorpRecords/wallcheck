# Wave 7, Leg A — Index Expansion toward 500 (DONE)

221 candidates listed; 70 dropped as already indexed (mechanical
dedupe against INDEX.md hostnames); 151 survived dedupe and
DNS-checked clean; capped to **105** by per-category caps
(jobs 20, saas 15, news 15, civic 14, finance 10, travel 14,
health 10, education 7) to land the index at ~500 rather than
overshooting to 545. All 105 probed once (honest wallcheck UA,
no retries); raw results: `results-expansion4.json`; merged
into INDEX.md (394 → 499 rows; header count corrected — see
PROBLEMS.md W7-004).

## Distribution (105 new rows)

| Verdict | Count |
|---|---|
| OPEN | 79 |
| WALLED | 9 |
| CHALLENGED | 5 |
| RATE_LIMITED | 2 |
| UNREACHABLE | 10 |

## Non-OPEN rows (all hand-checked or rule-verified)

**WALLED (9):** catho.com.br (bare nginx 403, unattributed —
W7-002), news.sky.com (Akamai), haaretz.com (Varnish 403 +
cache error ID, unattributed — W7-002), sec.gov (Akamai),
bls.gov (Akamai), citizensbank.com (Akamai), easyjet.com
(Akamai), emirates.com (Akamai), unitedhealthcare.com (AWS
CloudFront).

**CHALLENGED (5):** careerjet.com (Cloudflare Turnstile
verification interstitial — investigated as a suspected defect
and CORRECTED, see PROBLEMS.md W7-001: the capture's visible
text is only the verification page, so the verdict stands),
monster.ca (DataDome), careerbuilder.ca (DataDome),
tripadvisor.com (DataDome), viator.com (DataDome).

**RATE_LIMITED (2):** orbitz.com, travelocity.com (plain 429s).

**UNREACHABLE (10, recorded not retried — W7-003):** timeouts
(irishjobs.ie, jobs.ie, magento.com, washingtonpost.com,
cbc.ca, airfrance.com, klm.com) and connection drops (doj.gov,
block.com, getyourguide.com).

## What this wave changed in the index

- **Akamai tightens its grip on civic + travel:** sec.gov and
  bls.gov join the walled-civic set (ssa.gov, nyc.gov, ftc.gov
  were already there); easyjet + emirates join the walled-airline
  set. Civic walled count rises while civic overall stays mostly
  open — the exceptions are now a pattern (financial/regulatory
  + identity-adjacent agencies), not noise.
- **DataDome owns travel discovery:** tripadvisor + viator
  challenge via DataDome while the booking engines throttle
  (orbitz/travelocity 429s) — an agent planning a trip meets a
  different wall at every step of the funnel.
- **News splits again:** sky news walled (Akamai), haaretz
  walled (Varnish) — the Wave 6 media-wall story extends to
  international outlets, while most new news rows serve.
- **No new vendors, no classifier defects.** The one suspected
  defect (careerjet) dissolved on proper reading of the capture
  (PROBLEMS.md W7-001) — the classifier's vocabulary survived
  105 new sites untouched. That, plus the clean round-5 sheet,
  is what the saturation test counts (see OVERNIGHT.md).
