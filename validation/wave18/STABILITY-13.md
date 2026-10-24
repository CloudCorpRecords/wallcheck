# Wave 18 — Round-14 re-probe measuring the Wave 17 fixes (Leg A)

**499/499 rows probed once each** with the Wave 17-fixed
classifier — the measurement Wave 17's STABILITY-12 deferred.
The runner (`validation/wave18/run_round14.py`, written fresh
for round 14 with the round number in exactly one constant)
imported the Wave 17 tree at launch: all Wave 17 fixes were
grep-verified present before probing (W17-001 noscript strip,
W17-002 head strip, W17-002b corroboration refinement, W17-003
QR_PROMPT, W17-004 entity-encoded JSON, W17-005 Nordic phrases,
W17-006 OVERLAY_CHALLENGE, W17-007 visible-text passkey/magic-
link + served-page gates). All 499 history lines parse; zero
missing URLs vs the INDEX table; zero duplicate round-14 lines.

**Runner incident (see PROBLEMS.md):** the first launch died at
123/499 with no traceback (external kill; supervisor restarts in
the same window). The resume (`run_round14_resume.py`) imports
a reconstructed Wave 17 tree (`validation/wave18/src-wave17-tree/`,
all Wave 18 edits reverted in the copy only, verified by diff
and by behavior probes) — NOT the current tree, which already
carries Wave 18 battery fixes — so round 14 measures ONE tree
end to end. The Wave 18 battery fixes are unmeasured on live
traffic until round 15. **Fresh captures used the Wave 17 tree**
(the same tree the round measured), so corroboration is
comparable to the round reading.

Round-14 raw distribution: OPEN 413 · CHALLENGED 22 · WALLED 37 ·
RATE_LIMITED 7 · UNREACHABLE 15 · LOGIN_GATED 5.

## The 12 verdict diffs, all hand-checked with fresh captures

Every verdict diff was hand-checked with two fresh captures
(`validation/wave18/fresh_captures.py`, results in
`fresh-captures.json`) before merging — no diff was merged on
the round-14 reading alone. The strict rule: merge only on
round + 2 agreeing fresh; a 1–1 fresh split holds the row.

| target | standing | round 14 | fresh capture(s) | disposition |
| --- | --- | --- | --- | --- |
| claude.ai | CHALLENGED / Cloudflare | LOGIN_GATED / Cloudflare 200 (REDIRECT_TO_LOGIN) | LOGIN_GATED / Cloudflare 200, twice | **MERGED to LOGIN_GATED / Cloudflare.** The homepage now redirects to claude.ai/login; the body carries no challenge marker at all. Target-side change (challenge replaced by a login redirect), NOT fix-driven: no Wave 17 rule touches redirect-to-login evidence, and the body inspection confirms no marker was stripped. Cloudflare stands as vendor via header presence (the S5b pattern). |
| remoteok.com | OPEN 200 | LOGIN_GATED / Cloudflare 200 (QR_PROMPT) | LOGIN_GATED / Cloudflare 200, twice (QR_PROMPT) | **HELD at OPEN — the round's move is REJECTED, not merged.** Investigation of the live homepage showed the QR_PROMPT firing is a FALSE POSITIVE of the Wave 17 rule: the page's only QR signal is a script filename (`/qrcode.js`), and the visible text carries no QR wording at all. The Wave 17 QR rule read wording from the raw body (assets, scripts, styles) and had no served-page gate — the same failure mode W17-007 fixed for its passkey and magic-link siblings. Fixed this wave as W18-007 (visible-text wording + size gate); post-fix live re-probe reads **OPEN 200**. NOT a fix-driven move: the row does not change. |
| www.abc.net.au | OPEN 200 | WALLED / Akamai 403 | OPEN 200, twice | **HELD at OPEN.** The round's Akamai 403 is overturned by two agreeing fresh served readings — a transient deny, not a wall. |
| www.amazon.com | CHALLENGED / Generic | OPEN 200 | OPEN 200, twice | **MERGED to OPEN.** The intermittent captcha interstitial sat this round out again (round + 2 agreeing served readings). Note ‡ extends: the oscillator record now spans rounds 8–14. NOT fix-driven: no Wave 17 rule touches the Generic interstitial. |
| www.britishairways.com | UNREACHABLE | OPEN 200 | Timeout (UNREACHABLE) + OPEN 200 | **HELD at UNREACHABLE.** The fresh evidence splits 1–1 (round + 1 fresh served vs 1 fresh failure) — no corroboration triple for either side, so the strict rule holds the row, exactly as Waves 16–17's splits did. The served-leaning evidence (2 readings vs 1) is noted for round 15. |
| www.fda.gov | OPEN 200 | LOGIN_GATED / Akamai 401 | LOGIN_GATED / Akamai 401, twice | **MERGED to LOGIN_GATED / Akamai.** The site now answers 401 (the 401 branch, not a Wave 17 rule); Akamai stands via server-header presence. Target-side change. |
| www.forbes.com | OPEN 200 | CHALLENGED / DataDome 403 | CHALLENGED / DataDome 403 + timeout (UNREACHABLE) | **HELD at OPEN.** Challenged readings number round + 1 fresh (2 of 3), not the round + 2 agreeing fresh the merge bar requires — no triple, so the standing row holds. The oscillator record extends: rounds 11–13 held on the same pattern, and the challenged-leaning evidence is noted for round 15. NOT fix-driven: no Wave 17 rule touches DataDome detection. |
| www.goodrx.com | CHALLENGED / PerimeterX | OPEN 200 | OPEN 200, twice | **MERGED to OPEN.** The live homepage carries no PerimeterX marker at all — the wall is gone, not stripped. Target-side change, NOT fix-driven (body inspection confirms no marker for any strip to suppress). |
| www.kroger.com | UNREACHABLE | WALLED / Akamai 403 (edgesuite) | WALLED / Akamai 403 + timeout (UNREACHABLE) | **HELD at UNREACHABLE.** Round + 1 fresh walled vs 1 fresh failure — no triple, so the strict rule holds the row. The walled-leaning evidence (edgesuite deny, second sighting shape) is noted for round 15. |
| www.td.com | OPEN 200 | LOGIN_GATED 200 (QR_PROMPT) | LOGIN_GATED 200, twice (QR_PROMPT) | **HELD at OPEN — REJECTED, same W18-007 misfire as remoteok.com.** The page's only QR signal is a script identifier (`qrCode` in a Branch analytics token list); visible text carries no QR wording. Post-fix live re-probe reads **OPEN 200**. NOT a fix-driven move. |
| www.ubereats.com | CHALLENGED / Cloudflare | OPEN 200 | OPEN 200, twice (CF headers only) | **MERGED to OPEN — the round's ONLY fix-driven move.** Body inspection: the page's only Cloudflare challenge-platform references are three `challenges.cloudflare.com` URLs inside a `<head>` CSP host list — metadata, not a fired challenge. Under the Wave 16 tree the vendor scan read head text and fired CF_CHALLENGE_PLATFORM; under the Wave 17 tree the W17-002 head strip removes them (title stands alone, body presents no wall phrase) and the page serves. The W17-002 rule correctly moves a live row. |
| www.venmo.com | OPEN 200 | LOGIN_GATED 200 (QR_PROMPT) | LOGIN_GATED 200, twice (QR_PROMPT) | **HELD at OPEN — REJECTED, same W18-007 misfire.** The page's only QR signals are stylesheet class names (`.qr-code-image-container` rules for an app-download code); visible text carries no QR wording and no auth purpose for a sign-in prompt. Post-fix live re-probe reads **OPEN 200**. NOT a fix-driven move. |

## Fix-driven moves: exactly one

- **Head strip (W17-002) — 1 move.** ubereats.com CHALLENGED →
  OPEN, verified by body inspection (CSP host list in `<head>`).
  This ends the zero-fix-driven-move run: rounds 8–13 moved no
  live row correctly, and round 14 moves one — and it moves it
  by *removing* a false challenge, the direction the strips were
  built for.
- **QR prompt (W17-003) — 0 moves, 3 misfires rejected.** The
  rule fired on remoteok.com, td.com, and venmo.com and was
  proven wrong on inspection all three times; the rule itself
  was fixed (W18-007). Rejected misfires are not moves.
- **Noscript strip (W17-001) — 0 moves.** No live row's verdict
  depended on a noscript marker.
- **Corroboration refinement (W17-002b) — 0 moves.** No live
  row's verdict depended on a corroborating title marker.
- **Entity JSON (W17-004) — 0 moves.** Audit tool, not the
  index.
- **Nordic phrases (W17-005) — 0 moves.** No live row serves a
  Nordic challenge page.
- **Overlay challenge (W17-006) — 0 moves.** No live row serves
  an overlay challenge at its root.
- **Passkey/magic-link gates (W17-007) — 0 moves.**
  rubygems.org reads OPEN under the Wave 17 tree (the W17-007
  fix holds: no passkey misfire on the served homepage), and no
  other live row serves an auth-form prompt at its root.

## Merge result

**5 rows changed** (claude.ai, amazon.com, fda.gov, goodrx.com,
ubereats.com) plus the Wave 18 row-500 addition (search.brave.com,
OPEN — see Leg C). INDEX distribution after merges, before the
row-500 addition: OPEN 417 · CHALLENGED 21 · WALLED 35 ·
RATE_LIMITED 7 · UNREACHABLE 17 · LOGIN_GATED 2 (499 rows).
After row 500: OPEN 418 · CHALLENGED 21 · WALLED 35 ·
RATE_LIMITED 7 · UNREACHABLE 17 · LOGIN_GATED 2 (500 rows,
recount verified). The merged distribution differs from the
round-14 raw distribution by exactly the seven holds above.
