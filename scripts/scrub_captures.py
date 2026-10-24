#!/usr/bin/env python3
"""Scrub third-party public keys out of wallcheck validation captures.

Captures store raw response bodies of probed sites. Those bodies routinely
embed the *site's own* public client-side identifiers (Google Maps/API keys
shipped to every browser, WeChat mini-program app IDs, Next.js public env
values). They are not our secrets, but GitHub secret scanning flags them and
they do not belong in a public repo. Run this before publishing any new
capture wave:

    python3 scripts/scrub_captures.py [files...]

With no arguments it scrubs every validation/*/captures/*.json in the repo.
Writes are temp-file + JSON-verify + atomic replace, so a failed write never
truncates a capture.
"""
import json
import os
import re
import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent

PATTERNS = [
    # Google API keys (public frontend keys of probed sites)
    (re.compile(r"AIza[0-9A-Za-z\-_]{20,}"), "REDACTED-GOOGLE-API-KEY"),
    # Tencent WeChat mini-program app IDs (public identifiers in page JS)
    (re.compile(r"\bwx[0-9a-f]{16}\b"), "REDACTED-WECHAT-APP-ID"),
    # Next.js server-actions encryption key when shipped as NEXT_PUBLIC_*
    (
        re.compile(
            r"(NEXT_SERVER_ACTIONS_ENCRYPTION_KEY[^A-Za-z0-9+/=]{0,12})[A-Za-z0-9+/=]{20,}"
        ),
        r"\1REDACTED-ENCRYPTION-KEY",
    ),
]


def scrub_file(path: pathlib.Path) -> int:
    text = path.read_text(errors="ignore")
    total = 0
    out = text
    for pat, repl in PATTERNS:
        out, n = pat.subn(repl, out)
        total += n
    if not total:
        return 0
    # Verify the scrubbed file is still valid JSON before touching the original.
    json.loads(out)
    tmp = path.with_suffix(path.suffix + ".scrub-tmp")
    with open(tmp, "w") as f:
        f.write(out)
        f.flush()
        os.fsync(f.fileno())
    json.loads(tmp.read_text(errors="ignore"))
    os.replace(tmp, path)
    return total


def main() -> int:
    if len(sys.argv) > 1:
        files = [pathlib.Path(a) for a in sys.argv[1:]]
    else:
        files = sorted(ROOT.glob("validation/*/captures/*.json"))
    changed = 0
    for f in files:
        n = scrub_file(f)
        if n:
            changed += 1
            print(f"{f}: {n} value(s) redacted")
    print(f"done: {changed} file(s) changed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
