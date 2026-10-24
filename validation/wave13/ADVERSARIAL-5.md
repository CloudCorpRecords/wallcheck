# Wave 13 — Adversarial Battery v5: Results

**25 shapes, 6 mismatches before fixes, 0 after.** Three genuine
defects, all fixed test-first and generalized; two hand-classification
corrections (the classifier was right); one fixture bug (an article
under the served-page gate). Full suite after fixes: **236/236**
(210 prior + 26 new: 25 battery cases + 1 guard pin). Real-capture
corpus: 44 captures replayed, no verdict/vendor change on any real
wall capture (see PROBLEMS.md for the careerjet.json empty-body
artifact and the hyatt/state/catho/haaretz corroboration).

## Mismatches → fixes (3 defects)

| shape | pre-fix | hand | fix |
| --- | --- | --- | --- |
| E9a/E9b (comment-only vendor markers) | CHALLENGED / Cloudflare; CHALLENGED / PerimeterX | OPEN; WALLED, vendor none | W13-001: HTML comments stripped before every body scan in `_detect_vendor` |
| E4b ("Please wait while we check your browser" stub) | OPEN | CHALLENGED / Generic | W13-002: "check your browser" joins the JS_PROOF phrase list (small-page gated) |
| E6a (title-only llms.txt) | PASS | WARN | W13-003: LLMS_STUB — an llms body with no link, URL, or path reads WARN, not PASS |

## Corrections, not defects (2)

- **E8b hand vendor corrected** (LOGIN_GATED, None → LOGIN_GATED,
  Cloudflare): the Wave 11 C2c precedent already establishes that a
  loader-only login page keeps its loader vendor; the yield changes
  the verdict, not the attribution, and only the Generic leak is
  nulled on LOGIN_GATED. Same family as the Wave 7 careerjet
  correction: the hand classification was wrong, the classifier
  was right.
- **E3b fixture bug**: the first draft's article was 15,600 bytes —
  under the 16,384 served-page gate — so the title phrase
  legitimately fired. Lengthened past the gate (with an assert);
  the shape then pins correctly. Fixture sizes must clear the gate
  they test, or the test tests the gate, not the shape.

## Pins that held (19 shapes)

E1a/E1b/E1c (image mechanisms: filename signal counts, opaque
image is no signal, attribute text counts), E2a/E2b/E2c (noscript
changes nothing — JS_PROOF phrase, capability note, and human-check
prose all behave exactly as their unwrapped equivalents), E3a
(title-only human-check page is a challenge), E4a (PX cookie on
served content is presence, not a wall), E5a/E5b/E5c (robots
no-wildcard variants: wildcard-only FAIL, single-named WARN,
all-named FAIL — FAIL never required a wildcard), E6b (minimal
linked llms passes — the E6a fix does not punish short files),
E7a/E7b (one-URL sitemaps pass in both urlset and index form),
E8a/E8c (4-hop chain to login; fired wall at a login URL is a
wall), E10a/E10b/E10c (mixed-case markers match — matching is on
the lowered body throughout).

## Notable interactions

- **W13-001 is a scope fix, not a phrase fix.** Comments are
  metadata, not content and not code: stripping them before all
  body scans (markers, redirect targets, generic phrases) is one
  change that removes a whole class of false attribution. The
  E9b pin guards the other direction: a real refusal with only
  comment evidence must not gain a vendor it never earned.
- **W13-002's guard pin matters.** Adding "check your browser"
  to JS_PROOF without the served-page guard would be reckless;
  the 20 KB article pin proves the gate still holds the new
  phrase, exactly as D3b did for "browser check" in Wave 12.
- **W13-003 refines the length gate, not reverses it.** Bodies
  under 20 chars still read EMPTY_BODY; the stub rule only
  catches longer bodies that point nowhere. D7b's plain-text
  index lines (with a path) and every linked fixture still pass.

## What this wave says about saturation

Battery v5 found 3 genuine defects on shapes no earlier battery
exercised — the adversarial surface is still not exhausted, and
Wave 13 is NOT a clean wave on the battery prong. Combined with
Leg A (round 9, still running at the time of this writing), the
saturation assessment lives in STABILITY-8.md and the OVERNIGHT
log: any defect in either leg resets the clock again.
