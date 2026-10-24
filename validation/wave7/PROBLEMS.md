# Wave 7 — Problems ledger

## W7-001 (CORRECTED — not a defect) — careerjet: the classifier was right, the hand-check was wrong

**Found by:** Leg A expansion, hand-check with live capture —
then corrected by reading the capture properly.

**The shape:** `careerjet.com` classified CHALLENGED / Cloudflare at
status 200 on the evidence `CF_CHALLENGE_PLATFORM`. The first
hand-check judged from the capture's `<head>` (styles, spinner,
"Careerjet" title) that this was a served homepage embedding a
Turnstile widget for its own form — a false-positive verdict.

**The correction:** stripping scripts/styles from the capture
(`captures/careerjet.html`, 10,937 bytes) leaves ONLY this visible
text: "Careerjet / Verification required / Our systems have
detected unusual traffic from your computer network. This page
checks to see if it's really you sending the requests, and not a
robot. IP address: ..." — no search box, no listings, no homepage
content at all. This is a genuine verification interstitial. The
classifier was right; the 16 KB size gate worked as designed (an
interstitial is small *because* it is an interstitial).

**The fix that was tried and REVERTED:** blanking quoted
Turnstile-loader references for `CF_CHALLENGE_PLATFORM` (same
loader principle as recaptcha/hcaptcha). Reverted because it
solves a non-problem and weakens attribution: on a check-only
page the Turnstile loader IS the challenge mechanism, not
presence — the loader principle applies to served pages, where
the size gate already suppresses it. A revert note sits in
`classify.py` so nobody re-adds it without a served-page capture
proving the false positive. Live re-probe after the revert:
CHALLENGED / Cloudflare, confirming the Leg A row needed no
correction.

**Fixtures:** `tests/test_classify.py::TestWave7Fixtures` —
careerjet shape (CHALLENGED / Cloudflare, `CF_CHALLENGE_PLATFORM`
present) + Just-a-moment control. The fixture's comment carries
the lesson.

**Lesson (generalized, this is the durable part):** hand-checks
must read the VISIBLE TEXT (scripts/styles stripped), never the
`<head>`. A styled shell with a spinner looks like a homepage
until you strip it.

**Watch item (unobserved hypothetical, NOT a defect):** a small
login page carrying Turnstile for its own form would read
CHALLENGED via the vendor branch (the generic branch yields to
login pages per W6-002, this branch does not). No live capture
shows that shape in 499+ sites; if one ever appears, fix it then,
generalized.

## W7-002 (NOT A DEFECT, recorded) — bare-403 refusals with no vendor signature

`catho.com.br` (nginx, 118-byte bare "403 Forbidden") and
`haaretz.com` (Varnish, 403 + cache error ID) carry no vendor
marker. Per the bare-403 rule they are WALLED / unattributed —
measured, not attributed. Captures in `captures/catho.html`,
`captures/haaretz.html`.

## W7-003 (NOT A DEFECT, recorded) — 10 expansion UNREACHABLEs

Seven read timeouts (~15–17 s each): irishjobs.ie, jobs.ie,
magento.com, washingtonpost.com, cbc.ca, airfrance.com, klm.com.
Three connection drops (RemoteDisconnected): doj.gov, block.com,
getyourguide.com. Single-client observations from one honest fetch
each; recorded per discipline, not retried. Note: washingtonpost.com
timing out is a slow-server observation, not a wall claim — the
stability re-probe (Leg B) re-measures all of these independently
as part of round 5, which is a new measurement round, not a retry.

## W7-005 (RUNNER BUG, fixed) — round-5 resume keyed on the wrong field

`run_wave7.py` leg B's resume path used `r["url"]` on records
keyed by `"target"` (the history schema) — inherited from the
Wave 4 script, whose resume path never executed, so the bug
survived unnoticed until Wave 7's restart needed it. Fixed to
`r.get("url") or r.get("target")` before the restart; the
restart then resumed correctly from 329 rows. Not a classifier
defect; not a data defect (no rows were lost — the crash
happened before any write).

## W7-006 (INFRASTRUCTURE INCIDENT, repaired with evidence intact) — egress-proxy credential rotation poisoned 52 round-5 rows

Mid-round (07:15:06 UTC), the VM's egress-proxy credential
rotated under the long-lived runner: timeouts, then `Tunnel
connection failed: 403 Forbidden` on every fetch. Diagnosed by
proxy-URL hash comparison (`/proc/<pid>/environ` vs fresh
shell). Repaired per STABILITY-4.md: runner killed precisely,
52 poisoned rows removed from `results-round5.json` and
archived verbatim to `results-round5-window.json`, runner
restarted from a fresh shell, recovery values authoritative.
Lesson for future waves: long-lived probing runners must be
restarted (or re-exec'd) if a sudden all-UNREACHABLE run
appears — check the proxy credential age before doubting the
sites. The incident also validates the incremental-save design
for the third time (W2-006, Wave 4 restart, now this).

## W7-004 (STALE HEADER, fixed in merge) — INDEX.md header count

The Wave 6 merge left the INDEX.md header line at "258 sites"
while the table itself held 394 rows. The Wave 7 merge corrects the
header line to the true row count and updates the rounds-merged
paragraph; the row data itself was verified (394 data rows counted
before the merge).
