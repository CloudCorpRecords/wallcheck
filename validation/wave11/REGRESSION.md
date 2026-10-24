# Wave 11 — Full-surface regression (Leg C)

Post-Wave-10 tree (0.5.0-rc + Wave 10's 8 fixes, unreleased) plus
Wave 11's 6 battery fixes, measured against every surface.

## Full test suite

**183/183 green** — 152 pre-existing pins (Waves 1–10) all pass
with zero regressions, plus 31 new Wave 11 battery pins
(`tests/test_adversarial3.py`). Run: `PYTHONPATH=src python3 -m
pytest tests/ -q`.

## MCP smoke

`scripts/smoke_mcp.py` passes on all three tools against the stdio
server over real pipes: initialize, tools/list
[`probe_url`, `classify`, `audit`], classify → CHALLENGED /
Cloudflare, probe_url(example.com) → OPEN 200, audit(example.com)
→ grade F 3/12. The `audit` tool (Wave 9) is exercised live, not
just listed.

## Spot re-audit: the 3 C-graded Wave 7 sweep domains

Re-audited live with the post-Wave-10 audit gates (llms JSON-error
FAIL, robots HTML-error FAIL) and the Wave 11 robots FAIL
semantics. Full per-check output in `results-reaudit.json`.

| domain | Wave 7 grade | Wave 11 grade | why unchanged |
| --- | --- | --- | --- |
| hub.docker.com | C 7/12 | C 7/12 | robots PASS (real file), llms PASS (8,071-byte genuine text) — neither new gate fires; api FAIL + signed FAIL (directory path Cloudflare-walled) as before. |
| huggingface.co | C 7/12 | C 7/12 | llms FAIL is a live AWS WAF wall, not a JSON error document — the wall gate correctly fires first; robots PASS; api WARN (dev portal, no spec). |
| www.typeform.com | C 7/12 | C 7/12 | robots WARN (all 4 agents restricted, none blocked — the W11-006 change cannot move a restricted-only file); llms PASS; api WARN. |

Conclusion: the new gates change real grades correctly — they fire
only on the error documents they were built for (proven by the
B9a/B9d battery fixtures), and no live grade moved collaterally.
The three domains' failing checks are genuine owner-posture gaps
(no API surface on Docker Hub, no signed-agent directory anywhere,
all agents restricted on Typeform), not measurement artifacts.

## Corpus regression (from Leg B)

New classifier vs the 44 wave1–7 real captures: zero verdict or
vendor changes (`corpus-baseline.txt` vs `corpus-after.txt`, diff
empty). The Wave 10 risk captures (npmjs CHALLENGED / Cloudflare,
kickstarter OPEN, duolingo OPEN) and careerjet (non-login URL, so
the W11-003 loader yield cannot touch it) are all unchanged.
