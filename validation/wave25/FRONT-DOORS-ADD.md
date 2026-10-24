# Wave 25 — FRONT-DOORS huggingface.co Row (Leg C)

`campaign/FRONT-DOORS.md` had **no huggingface.co entry** (the
Wave 24 Leg C finding, recorded in DOCS-SPOT-4.md with no row
edit). Wave 25 closes that gap: three honest fetches, one each
(`validation/wave25/probe_huggingface.py`, results in
`huggingface-probes.json`), then the row written from the
evidence.

## Probe evidence (2026-10-24)

| Target | Status | Verdict | Note |
|--------|--------|---------|------|
| https://huggingface.co | 200 | OPEN | agrees with the standing Index row (OPEN in every round) |
| https://huggingface.co/api | 404 | OPEN | the site's HTML 404 page (52 KB) — the bare path is not an API document; endpoints live under the documented API, so the row sends callers to the docs |
| https://huggingface.co/.well-known/http-message-signatures-directory | 401 | LOGIN_GATED | confirms the Wave 23 spot-check finding (401 LOGIN_GATED, 2026-10-24) — the census-era hard wall on the directory path is now a gate, not an opening |

## The row added

A new "## Wave 25 addition" section in FRONT-DOORS.md, before
the seed scoreboard, in the file's standard per-platform
format:

- **Hugging Face (huggingface.co) — OPEN (200); signed-agent
  directory LOGIN_GATED (401).** Sanctioned route: YES — the
  official Hub API (public REST API for models, datasets,
  Spaces; token-authenticated writes, open public reads),
  sourced to the platform's own API documentation
  (https://huggingface.co/docs/hub/api). **Status: VERIFIED.**
- The signed-agent directory is recorded as NOT PUBLISHED
  (login-gated) with both dated readings (Wave 23 + Wave 25)
  cited in the entry.
- The edition label now reads "Seed edition, extended Wave 8,
  Wave 25 addition, 2026-10-24"; a one-row "Scoreboard —
  Wave 25 addition" table was added after the Wave 8 tally,
  and the combined count updated: **66 platforms — 40
  VERIFIED, 20 NO ROUTE FOUND, 6 UNVERIFIED** (the Wave 8
  tally sentence itself is historical and untouched).

## Not touched

- `campaign/LAUNCH-POST.md` — Wave 1 numbers are launch copy,
  refreshed only at ship time (launch hold).
