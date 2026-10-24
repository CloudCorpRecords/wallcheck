# Wave 15 — Limitations Revisit (Leg C)

Every documented honest limitation across SPEC.md and the wave
PROBLEMS files, re-tested against the deterministic signals the
last six waves' fixtures added (Waves 10–15 batteries, path
matrices, directory censuses). A limitation closes only when a
NEW deterministic, generalized signal exists — never a per-site
patch. One row per limitation: still-open or closed-by-signal,
with the re-test date.

| # | limitation (origin) | re-test (Wave 15) | status |
| --- | --- | --- | --- |
| L1 | Silent JS-proof page: no vendor signature, no human-check wording → OPEN (Wave 3; re-affirmed W11 C1a) | New signals since Wave 3: JS_PROOF phrases grew ("verify your request", "check your browser", "browser check"), Refresh-header routing (W15-005), visible-text phrase scan (W15-003), form-action targets (W11-001). But a truly silent page — empty body + reload timer, no wording, no tokens, no targets — still carries NOTHING to key on: C1a deliberately stays OPEN because a reload timer alone is indistinguishable from empty pages and shells. No new deterministic signal exists for the wording-free case. | **STILL OPEN** (re-tested 2026-10-24) |
| L2 | Textless images/SVG: pixels with no text carry no verdict-driving signal (W11 C3b) | W15-003's visible-text scan closes the SPLIT-text species (markup text is now read wherever it sits), but a graphic with NO text in markup still has nothing to read — stdlib text analysis cannot see pixels, and guessing "captcha" from an opaque image would be fabrication (E1b precedent). | **STILL OPEN** (re-tested 2026-10-24) |
| L3 | Unknown vendor headers (Sucuri): a synthetic header alone does not earn a vendor rule (W11 C5b) | No live wall-page capture for any new vendor has appeared in Waves 12–15 (the vendor set is unchanged since Wave 5's Kasada/Azure/CloudFront). The policy stands by design: a vendor rule needs a live wall page, not a header. | **STILL OPEN by policy** (re-tested 2026-10-24) |
| L4 | URL-based login detection: a served page whose ONLY login signal is a sign-in form + challenge cookie reads OPEN (W14 F5) | W15-006 adds a NEW deterministic signal for one species: a one-time-code entry form (code input + auth wording, two-keyed, discount-code-guarded). The 2FA/code-entry species is now detected at any URL. The general password-sign-in-form species REMAINS open deliberately — form-text detection on password forms would false-positive on every page carrying a "sign in" link, and no narrower signal for it has appeared. | **NARROWED** — code-entry species closed by W15-006; password-form species still open (re-tested 2026-10-24) |
| L5 | Consent gates are legal gates, not bot walls (W10 B5b, reaffirmed W12 D4a) | No live capture of a consent gate that is itself bot-gated has appeared. The scope decision stands: calling consent CHALLENGED would mislabel every GDPR banner. | **STILL OPEN by design** (re-tested 2026-10-24) |
| L6 | Hop bodies are not classifier inputs (W14 F8 design boundary) | Not a gap to close: by construction, a hop wall that blocked would BE the final response. The boundary is structural, and every battery since (D9, E8, F8) confirms it holds. | **RESOLVED by construction** (not a gap) |
| L7 | Attempt-dependent verdicts / transport noise (eBay sign-in, amazon interstitial, BA transport, now forbes DataDome) | No classifier signal can settle a target that answers differently per attempt — that is target-side behavior, handled procedurally by the merge rules (corroboration triples, holds, oscillator notes), not by a rule. Round 11 added forbes.com to the oscillator set. | **STILL OPEN as measurement reality** (handled procedurally; re-tested 2026-10-24) |
| L8 | Localized-phrase treadmill: coverage is enumerative, never complete (Waves 6/11/12 language lists) | Wave 15's battery adds no new language (G-series shapes are mechanisms, not languages). The treadmill continues: the next unlisted language is always one live capture away. | **STILL OPEN** (treadmill; re-tested 2026-10-24) |
| L9 | Signed requests change nothing where the key is not trusted (Wave 5 experiment: 12/12 unchanged) | No new signal: signatures matter only where the site checks them. The directory census (3/154 in Wave 4, 4/499 in Wave 7) tracks the ecosystem, not the classifier. | **STILL OPEN** (ecosystem reality; re-tested 2026-10-24) |
| L10 | Audit API discovery is same-domain well-known paths only (Wave 3: github.com api=WARN because the API lives on api.github.com) | Widening discovery to sibling subdomains would break the audit's stated ≤10-fetch budget and its domain-scoped contract. No new signal changes the trade-off. | **STILL OPEN** (documented scope; re-tested 2026-10-24) |

## Follow-ups noted, not assumed

- **TRAFFIC_CHECK visible-text scan:** W15-003 extended the
  visible-text phrase scan to human-check and JS_PROOF phrases;
  TRAFFIC_CHECK (anomaly wording + verification cue) still scans
  raw body only, so a split "unusual traffic" phrase would miss.
  A Wave 16 battery shape should test it before any fix is
  claimed — the mechanism exists, the branch does not use it yet.
- **JS_PROOF is now visible-text-scanned** (W15-003's second
  half), pinned by a tspan-split guard — this one was closed in
  the same motion, not left as a follow-up.
