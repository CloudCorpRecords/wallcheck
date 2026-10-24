# Wave 16 — Adopter Spot-Check (Leg C)

Spot-check, not census v3: the 4 known adopters re-fetched, plus
the directory path re-probed on 10 of the 71 Wave 7
walled-directory-path domains. Runner:
`validation/wave16/run_adopter_spot.py`; results:
`validation/wave16/results-adopter-spot.json`. One honest fetch
per URL.

## Adopters: 4/4 still publishing, 3/4 byte-identical keys

| domain | parses | keys | vs Wave 7 | verdict |
| --- | --- | --- | --- | --- |
| chatgpt.com | yes | 1 Ed25519, kid `ArwjqcCqtA5oxEWkzXGC-To_0A9whHmajCHtfe8I9aY`, use `sig`, purpose `ai`, signature_agent, nbf 2025-01-01, exp 2026-10-31 10:55 UTC | **MOVED again**: same key (same kid, same x prefix `P_1c4SX6fCav`), exp moved **+11,956 s** vs Wave 7's 1793432154 — the same slow-drift pattern as Wave 5→7 (+11,699 s). The reference directory is operated, not abandoned. Still reference-grade. | unchanged in shape, window extended |
| www.indeed.com | yes | 1 Ed25519, bare JWKS (no kid, no use, no window) | Unchanged: same x prefix `JrQLj5P_89iX` as Wave 7. | unchanged |
| substack.com | yes | 1 Ed25519, bare JWKS (no kid, no use, no window) | Unchanged: same x prefix `o5kcuyjl063D` as Wave 7. | unchanged |
| www.ahrefs.com | yes | 2 Ed25519, kids `e3vpiy0B6M1Wdxnizw3dqRSgpqS6SXM2qiQ6HtUwZ5g` + `0227KWFT1389RBnlR8TLhbMaA_Of2MbNPhmlNICS7eI`, use `sig`, top-level fields = `keys` only | Unchanged: same kids and x prefixes (`0g1xFRWdVlSO`, `v02owuOay4qE`) as Wave 7. **Did NOT gain purpose/window metadata** — still below reference-grade on metadata, still rotation-ready on keys. | unchanged |

Note on the runner's "missing kid" flags for Indeed/Substack:
those are this script's strictness, not regressions — bare JWKS
keys without kids are the pre-existing shape Wave 7 recorded.
All four keys validate structurally (OKP/Ed25519, 43-char
base64url x).

## Runner incident (caught before any conclusion)

The first version of the spot-check script read `r["body"]`
from `probe_url`'s result — but `probe_url` returns only the
classification object, no body field. All four first-run
"body is not JSON" readings were the runner's own artifact, not
adopter changes. The script was fixed to fetch with
`audit.fetch_raw` (which returns the body) and re-run; the
bogus first output file was overwritten by the corrected run,
and the x-prefix verification above is a second independent
fetch confirming the corrected results. Lesson, same family as
the Wave 13/14 sed-trap: a tool that returns no body cannot
evidence a body claim — check the return shape before reading
the result as data.

## Walled directory paths: 9/10 still walled

| domain | directory-path verdict | vs Wave 7 |
| --- | --- | --- |
| www.upwork.com | WALLED / Cloudflare 403 | still walled |
| www.guru.com | WALLED / Imperva 403 | still walled |
| www.npmjs.com | UNREACHABLE (fetch failed this attempt; first spot attempt read CHALLENGED / Cloudflare 403) | transport noise, not a posture change — npmjs's intermittent connection-drop pattern (6th+ sighting across rounds); the path is not open |
| medium.com | WALLED / Cloudflare 403 | still walled |
| www.glassdoor.com | WALLED / Cloudflare 403 | still walled |
| hub.docker.com | WALLED / Cloudflare 403 | still walled |
| www.reddit.com | WALLED 403 (unattributed) | still walled |
| www.w3schools.com | WALLED / Akamai 403 | still walled |
| www.reuters.com | WALLED 403 (unattributed) | still walled |
| www.wsj.com | WALLED 403 (unattributed) | still walled |

No walled-directory path opened. The Wave 7 story stands: for
14% of the index, publishing a directory is a wall-configuration
request first, a docs request second.
