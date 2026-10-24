# Wave 23 — Adopter + Walled-Path Spot-Check v3 (Leg C)

Spot-check, not census v3: the 4 known adopters re-fetched,
plus the directory path re-probed on 15 of the 71 Wave 7
walled-directory-path domains. Runner:
`validation/wave23/run_adopter_spot.py`; results:
`validation/wave23/results-adopter-spot.json`. One honest
fetch per URL; adopter bodies fetched with `audit.fetch_raw`
(probe_url returns no body — the Wave 16 runner lesson).

## Adopters: 4/4 still publishing, all keys byte-identical

| domain | parses | keys | vs Wave 16 | verdict |
| --- | --- | --- | --- | --- |
| chatgpt.com | yes | 1 Ed25519, kid `ArwjqcCqtA5oxEWkzXGC-To_0A9whHmajCHtfe8I9aY`, use `sig`, signature_agent, nbf 2025-01-01, exp 1793456665 (2026-10-31 ~14:24 UTC) | **MOVED again**: same key (same kid, same x prefix `P_1c4SX6fCav`), exp moved **+12,555 s** vs the Wave 16 results JSON (1793444110) — the third consecutive forward drift (Wave 7 → 16 → 23), same ~+10–12.5k s pattern. The reference directory is operated, not abandoned. Still reference-grade. | window extended again |
| www.indeed.com | yes | 1 Ed25519, bare JWKS (no kid, no use, no window) | Unchanged: same x prefix `JrQLj5P_89iX` as Waves 7/16. | unchanged |
| substack.com | yes | 1 Ed25519, bare JWKS (no kid, no use, no window) | Unchanged: same x prefix `o5kcuyjl063D` as Waves 7/16. | unchanged |
| www.ahrefs.com | yes | 2 Ed25519, kids `e3vpiy0B6M1Wdxnizw3dqRSgpqS6SXM2qiQ6HtUwZ5g` + `0227KWFT1389RBnlR8TLhbMaA_Of2MbNPhmlNICS7eI`, use `sig`, top-level fields = `keys` only | Unchanged: same kids and x prefixes (`0g1xFRWdVlSO`, `v02owuOay4qE`). **Still no purpose/window metadata** — below reference-grade on metadata, rotation-ready on keys. | unchanged |

All keys validate structurally (OKP/Ed25519, 43-char
base64url x, no problems beyond the pre-existing missing-kid
shape of the two bare JWKS documents — the runner's strictness,
not a regression, as noted in Wave 16).

## Walled directory paths: 15/15 still serve no directory

| domain | directory-path verdict | vs prior spot-checks |
| --- | --- | --- |
| www.upwork.com | WALLED / Cloudflare 403 | still walled (W16 same) |
| www.guru.com | WALLED / Imperva 403 | still walled (W16 same) |
| www.npmjs.com | UNREACHABLE (fetch failed this attempt) | transport noise, not an opening — npmjs's intermittent connection-drop pattern (10th+ sighting across rounds); W16 read the same |
| medium.com | WALLED / Cloudflare 403 | still walled (W16 same) |
| hub.docker.com | WALLED / Cloudflare 403 | still walled (W16 same) |
| www.reddit.com | WALLED 403 (unattributed) | still walled (W16 same) |
| www.wsj.com | WALLED 403 (unattributed) | still walled (W16 same) |
| www.reuters.com | WALLED 403 (unattributed) | still walled (W16 same) |
| www.glassdoor.com | WALLED / Cloudflare 403 | still walled (W16 same) |
| www.w3schools.com | WALLED / Akamai 403 | still walled (W16 same) |
| huggingface.co | LOGIN_GATED 401 (unattributed) | refusal species changed: the Wave 7 census classified this path WALLED_FETCH; it now answers an auth gate (401) instead of a hard wall. No directory is served to an unauthenticated agent either way — a gate, not an opening. First spot-check of this domain since the census. |
| www.sec.gov | WALLED / Akamai 403 | still walled (new to the spot-check; Wave 7 census: walled) |
| www.delta.com | WALLED / Akamai 444 | still walled (new to the spot-check; Wave 7 census: walled) |
| www.marriott.com | WALLED / Akamai 403 | still walled (new to the spot-check; Wave 7 census: walled) |
| gun.io | WALLED / Cloudflare 403 | still walled (new to the spot-check; Wave 7 census: walled) |

No walled-directory path opened. 13/15 read WALLED
outright; npmjs failed at transport (its standing pattern,
not a posture change); huggingface answers a login gate
instead of a wall — the front door is still closed to an
unauthenticated agent on all 15. The Wave 7 story stands:
for ~14% of the index, publishing a directory is a
wall-configuration request first, a docs request second.
