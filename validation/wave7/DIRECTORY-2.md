# Wave 7, Leg C — Signed-Agent Directory Census v2

**Method.** Every hostname in the merged 499-site index probed
once at `/.well-known/http-message-signatures-directory` (the
audit module's fetcher + the classifier — the same code path as
a probe). A 200 whose body parses as JSON with a `keys` list =
ADOPTER. Only on an ambiguous 200-that-is-not-a-directory was
the second allowed fetch spent on
`/.well-known/http-message-signatures`. A 429 or a wall ends
that domain's turn; the verdict is the data. Raw results:
`results-directory2.json` (499 hosts).

## Headline: 4 adopters of 499 (0.8%)

Wave 4 found 3 of 154 (1.9%). At full scale the adoption rate is
lower — and one adopter is new.

| Host | Document | Assessment |
|---|---|---|
| chatgpt.com | 1 Ed25519 key, `kid`, `use:"sig"`, `purpose:"ai"`, `signature_agent`, validity window (nbf 2025-01-01 → exp 2026-10-31, moved +11,699 s since Wave 5 — actively maintained) | Reference-grade (unchanged) |
| www.ahrefs.com | **NEW.** 2 Ed25519 keys, both with `kid` + `use:"sig"`; top-level fields = `keys` only (no purpose, no window) | Better than bare keys: keyed + dual-key (rotation-ready). Below reference-grade: no declared purpose, no validity window. |
| www.indeed.com | 1 Ed25519 key, bare JWKS | Unchanged |
| substack.com | 1 Ed25519 key, bare JWKS | Unchanged |

**No variant-path adopters:** the 32 ambiguous 200s spent their
variant fetch and none resolved to a directory.

## The full census

| Result | Count | Meaning |
|---|---|---|
| ABSENT (404/410) | 371 | No directory published. |
| WALLED_FETCH | 71 | The directory path itself is walled — the site does not merely lack a front door for signed agents, it walls the path where one would live. Includes Upwork, Guru, npmjs, Medium, eBay's orbit, Reuters, WSJ, and 60+ more. Up from 16 in Wave 4 (scale effect + newly-walled paths). |
| AMBIGUOUS_200 | 32 | A 200 that is not a directory document (SPA shell, homepage, error page served 200). |
| NO_ANSWER | 21 | Fetch failed or an unclassifiable status: 15 timeouts/disconnects, zoominfo 500, easyjet 503, infojobs.net + cash.app 405s, kaiserpermanente.org 302. All genuine transport/status observations — zero proxy-rot artifacts (no `Tunnel` errors anywhere in Leg C). |
| ADOPTER | 4 | Above. |

## What changed since Wave 4

- **Adoption did not grow with the index.** The 345 new hosts
  added exactly one adopter (ahrefs.com). The signed-agent web
  is still, to measurement, four sites.
- **The walled-directory-path count is the story's second
  half:** 71 of 499 domains (14%) wall the well-known path
  itself. For those domains, "publish a directory" is not a
  docs request — it is a wall-configuration request: the path
  must first be allowed through the existing ruleset.
- **chatgpt.com's document keeps moving** (expiry +11,699 s vs
  Wave 5): the reference implementation is operated, not
  abandoned — the strongest evidence in the census that a
  maintained directory is possible.
- **ahrefs.com's shape is the realistic next step for
  adopters:** two keys with kids (rotation without breakage)
  but no purpose/window metadata. The campaign's own directory
  document should beat it on metadata (purpose + window, per
  the chatgpt.com bar) while matching it on key hygiene.
