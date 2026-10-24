#!/usr/bin/env python3
"""Scrub key-like values out of wallcheck validation captures.

Captures store raw response bodies of probed sites. Those bodies routinely
embed the *site's own* key material — public client-side identifiers
(Google frontend keys, WeChat mini-program app IDs, Next.js public env
values) and, rarely, things that should never have been public at all.
None of it belongs in a public repo, and GitHub's secret scanning flags
it (4 alerts on the 0.5.0 ship commit). Run this before publishing any
new capture wave:

    python3 scripts/scrub_captures.py [files...]

The redaction table is DERIVED from the exposure scanner's pattern
table (src/wallcheck/exposure.py) — every pattern the scanner can find,
candidate and public alike — so the scrubber can never fall behind the
scanner again. Only the captured *value* of each match is replaced,
with a REDACTED-<PATTERN-NAME> marker; surrounding context (variable
names, field names, URL shapes) survives for evidence value. Values
that are already placeholders or markers are left alone, so scrubbing
is idempotent.

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
sys.path.insert(0, str(ROOT / "src"))

from wallcheck.exposure import PATTERNS as EXPOSURE_PATTERNS  # noqa: E402
from wallcheck.exposure import PLACEHOLDER  # noqa: E402

# A private-key block is the one place where replacing just the matched
# header (all the scanner's private_key_block pattern captures) is not
# enough: the base64 body lines would be left behind. Sweep whole
# BEGIN...END blocks first; the table pass below still covers a bare
# header with no END line.
_PEM_BLOCK = re.compile(
    r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"
    r".*?-----END (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
    re.S,
)


def _marker(pattern_name: str) -> str:
    return "REDACTED-" + pattern_name.upper().replace("_", "-")


def _variants(pat):
    """Yield the scanner pattern, plus — when it uses quote classes —
    a variant tolerant of JSON-escaped quotes. Captures store bodies
    as JSON strings, so a quote inside a body appears as \\" in the
    raw file: the scanner sees the decoded body, the scrubber works
    on raw file text and needs the backslash-tolerant twin. The
    variant is derived from the scanner's own pattern source (quote
    classes gain an optional backslash; the value class stops before
    a backslash so a closing \\" is never eaten into the marker)."""
    yield pat
    src = pat.pattern.replace('[\\"\']', '\\\\?[\\"\']')
    src = src.replace('[^\\"\']', '[^\\"\'\\\\]')
    if src != pat.pattern:
        yield re.compile(src, pat.flags)


def _redact(text: str):
    """Return (scrubbed_text, values_redacted) using the scanner's table."""
    total = 0

    text, n = _PEM_BLOCK.subn("REDACTED-PRIVATE-KEY-BLOCK", text)
    total += n

    for name, _cls, pat in EXPOSURE_PATTERNS:
        marker = _marker(name)

        def repl(m, marker=marker):
            nonlocal total
            value = m.groupdict().get("v")
            if value is None or PLACEHOLDER.search(value):
                return m.group(0)
            total += 1
            start, end = m.span("v")
            base = m.start()
            return (m.group(0)[: start - base] + marker
                    + m.group(0)[end - base:])

        for variant in _variants(pat):
            text = variant.sub(repl, text)
    return text, total


def scrub_file(path: pathlib.Path) -> int:
    text = path.read_text(errors="ignore")
    out, total = _redact(text)
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
