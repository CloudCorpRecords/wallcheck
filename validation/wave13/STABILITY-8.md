# Wave 13 — Round-9 re-probe measuring the Wave 12 fixes (Leg A)

**499/499 rows probed once each** with the Wave 12-fixed
classifier — the measurement Wave 12's STABILITY-7 deferred.
The runner (`validation/wave13/run_round9.py`, incremental +
resumable saves to `validation/wave4/history.jsonl` as round=9
and to `validation/wave13/results-round9.jsonl`) started AFTER
the Wave 12 fixes were verified present in the tree (W12-001
PL/TR/AR/ZH/RU phrases, W12-002 "browser check" JS_PROOF
phrase, W12-003 form-action/login-yield split, W12-004 JSON
llms WARN, W12-005 markdown mislabel carve-out, W12-006 gzip
sitemap decompression — all confirmed by grep before launch).
All 499 history lines parse; zero missing URLs vs the INDEX
table; zero duplicate round-9 lines. One runner incident, no
data impact: the first launch silently probed nothing because
a sed-derived resume check still read round 8 — caught from
the log ("already probed round 9: 499" with zero round-9
lines), fixed to round 9, and relaunched; the failed launch
wrote nothing (append-mode file, zero lines written).

Round-9 raw distribution: OPEN 416 · CHALLENGED 24 · WALLED 35 ·
RATE_LIMITED 7 · UNREACHABLE 17 · LOGIN_GATED 0.

## Raw diffs vs the standing table: 4, dispositioned

Every diff was hand-checked with fresh captures before merging
— no diff was merged on the round-9 reading alone. The runner
process imported the Wave 12 tree at launch, so round 9
genuinely measures the Wave 12 classifier even though Wave 13
fixes landed on disk mid-run.

| target | standing | round 9 | fresh capture(s) | disposition |
| --- | --- | --- | --- | --- |
| www.amazon.com | CHALLENGED / Generic 200 | OPEN 200 | CHALLENGED / Generic 200, twice (GENERIC_CAPTCHA + FORM_ACTION_TO_CHALLENGE) | HELD at CHALLENGED. The interstitial sat out round 9 only; two agreeing fresh readings corroborate the standing value (the Wave 12 npmjs precedent). Note ‡ extended. NOT fix-driven: the interstitial specimen was CHALLENGED under pre-Wave-11 rules too. |
| www.britishairways.com | UNREACHABLE | OPEN 200 | OPEN 200 (Akamai server header presence only) | MERGED to OPEN. Two agreeing served readings. Transport oscillation continues: timed out R6, served R7, timed out R8 ×2, served R9 + fresh. |
| www.merrilledge.com | LOGIN_GATED / Akamai 200 | OPEN 200 | OPEN 200, real Merrill Edge homepage, no login/challenge/captcha/form/refresh/location signal anywhere in the body | MERGED to OPEN. The Wave 11 login gate is GONE: the sitedown page that declared a JS redirect to a login widget no longer exists — the site serves its real homepage. Genuine target-side change, not a classifier regression (no login declaration exists in the current body for any rule to act on). The index's only LOGIN_GATED row retires; LOGIN_GATED count returns to zero. NOT fix-driven. |
| www.webex.com | OPEN 200 | WALLED / Akamai 403 | WALLED / Akamai 403 (AKAMAI_EDGESUITE) | MERGED to WALLED / Akamai. Two agreeing denies, and the second Akamai sighting after round 8 — exactly the "second sighting moves it" rule STABILITY-7 recorded. NOT fix-driven (a bare edge deny, not a phrase or form-action shape). |

## Fix-driven moves: exactly zero

Of the six Wave 12 rule families this round was built to
re-measure, none moved a live row:

- **Localized phrases (W12-001) — 0 moves.** No live row
  serves a Polish, Turkish, Arabic, Chinese, or Russian
  challenge page.
- **"Browser check" phrase (W12-002) — 0 moves.** No live row
  serves that stub wording.
- **Form-action/login-yield split (W12-003) — 0 moves.**
  Merrilledge's change is the absence of any login declaration,
  not the split; amazon's FORM_ACTION_TO_CHALLENGE evidence
  sits on an interstitial that was CHALLENGED before Wave 11.
- **JSON llms WARN (W12-004), markdown carve-out (W12-005),
  gzip sitemap (W12-006) — audit tool, not the index.** No
  index row is an audit grade.

Third consecutive round with zero fix-driven moves (Waves 11,
12, 13): the Wave 10–12 fixes are correctness insurance for
shapes live traffic has not shown this index, proven by
fixtures, unexercised by traffic.

## Merge result

**Three rows changed:** britishairways.com UNREACHABLE → OPEN,
merrilledge.com LOGIN_GATED → OPEN, webex.com OPEN → WALLED.
New INDEX distribution: OPEN 415 · CHALLENGED 25 · WALLED 35 ·
RATE_LIMITED 7 · UNREACHABLE 17 · LOGIN_GATED 0 (499 rows,
recount verified). Amazon.com held CHALLENGED, so the merged
distribution differs from the round-9 raw distribution by
exactly that one held row (raw CHALLENGED 24 / OPEN 416 →
merged CHALLENGED 25 / OPEN 415; WALLED and the rest already
equal after the three merges).
