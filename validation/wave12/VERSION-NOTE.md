# Wave 12 — Version hygiene note (Leg C)

No version files were changed by this wave (per the task: Wave 13
owns the stamp if saturation is reached). This note records the
conclusion so the stamp decision is not re-litigated from scratch.

## Current stamp story

- Stamped version: **0.5.0-rc** in `__init__.py`, `pyproject.toml`,
  and `server.json` (GHCR tag), stamped in Wave 9.
- Unreleased fixes on top of the stamp: Wave 10's 8 fixes, Wave
  11's 6 fixes, Wave 12's 6 fixes — 20 classifier/audit correctness
  fixes, all fixture-pinned, all regression-clean, none of them a
  new product surface (no new CLI commands, no new MCP tools in
  Waves 10–12; the Wave 9 audit MCP tool is already in the rc).

## Conclusion: the next stamp should be 0.5.0 final, not 0.5.1-rc

Reasoning: 0.5.0 has never been released — the `-rc` line is still
open, and the launch hold means nothing at any 0.5.x version has
shipped anywhere. A `-rc` suffix marks a pre-release *of* 0.5.0; the
fixes made during the rc phase fold into 0.5.0 final by definition.
Stamping 0.5.1-rc would imply a 0.5.0 final already exists to
succeed, which is false, and would strand the rc's own history
(0.5.0-rc → 0.5.1-rc with no 0.5.0 between them reads as a skipped
release).

The only case for 0.5.1-rc would be if 0.5.0 final ships first and
then further fixes land — i.e., the stamp after the ship, not the
stamp before it. If Wave 13 reaches saturation and the ship call
comes, the stamp is: drop `-rc` everywhere (version files +
GHCR tag + README/SPEC banners), keep the version number 0.5.0,
and record the 20 unreleased fixes as the 0.5.0 release notes.
