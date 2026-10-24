#!/usr/bin/env python3
"""Wave 7 INDEX.md merge: append expansion rows to their sections,
recompute section counts + the header verdict distribution, and fix
the stale header count (W7-004). Run once, after Legs B/C and the
W7-001 fix + careerjet re-probe. Idempotent: skips URLs already in
the table (safe to re-run after a partial merge).
"""
import json
import os
import re
import sys
from urllib.parse import urlsplit

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
INDEX = os.path.join(ROOT, "INDEX.md")
EXP = os.path.join(HERE, "results-expansion4.json")


def main():
    rows = json.load(open(EXP))
    text = open(INDEX).read()

    # Careerjet correction (W7-001) is applied to the results file
    # before this runs; this merge trusts the file.
    existing = set(re.findall(r"\((https?://[^)]+)\)", text))
    new_by_cat = {}
    for r in rows:
        url = r["url"]
        if url in existing:
            continue
        host = urlsplit(url).hostname
        verdict = r["verdict"]
        vendor = r["vendor"] or "—"
        status = r["status"] if r["status"] is not None else "—"
        line = "| [%s](%s) | %s | %s | %s | W7 expansion |" % (
            host, url, verdict, vendor, status)
        new_by_cat.setdefault(r["category"], []).append(line)

    lines = text.split("\n")
    out = []
    cur_cat = None

    def flush(cat):
        # Insert pending rows directly after the section's last table
        # row (before any trailing blank line, which would split the
        # markdown table).
        if cat not in new_by_cat:
            return
        idx = None
        for j in range(len(out) - 1, -1, -1):
            if out[j].startswith("| ["):
                idx = j
                break
        if idx is None:
            out.extend(new_by_cat.pop(cat))
        else:
            for k, row in enumerate(new_by_cat.pop(cat)):
                out.insert(idx + 1 + k, row)

    for line in lines:
        m = re.match(r"^## (.+?) \(\d+\)\s*$", line)
        if m:
            if cur_cat:
                flush(cur_cat)
            cur_cat = m.group(1)
            out.append(line)
            continue
        if line.startswith("## "):
            if cur_cat:
                flush(cur_cat)
                cur_cat = None
        out.append(line)
    if cur_cat:
        flush(cur_cat)
    # Any category not found as a section (should not happen) is
    # reported, not silently dropped.
    if new_by_cat:
        print("WARNING: no section for:", new_by_cat, file=sys.stderr)

    text = "\n".join(out)
    # Recompute section counts.
    def fix_section(m):
        name = m.group(1)
        body_start = m.end()
        nxt = text.find("\n## ", body_start)
        body = text[body_start:nxt if nxt != -1 else len(text)]
        n = len(re.findall(r"^\| \[", body, re.M))
        return "## %s (%d)" % (name, n)
    text = re.sub(r"^## (.+?) \(\d+\)", fix_section, text, flags=re.M)

    # Recompute the header distribution line. The row regex must
    # tolerate trailing note text after the link (the npmjs row
    # carries "— see note †" between the link and the verdict
    # column; the strict pattern undercounted it by one).
    data_rows = re.findall(
        r"^\| \[.*?\]\(https?://[^)]+\)[^|]*\| ([A-Z_]+) \|", text, re.M)
    from collections import Counter
    c = Counter(data_rows)
    total = len(data_rows)
    dist = " · ".join("%s %d" % (v, c[v]) for v in
                       ("OPEN", "CHALLENGED", "WALLED", "LOGIN_GATED",
                        "RATE_LIMITED", "UNREACHABLE") if c[v])
    text = re.sub(r"\*\*\d+ sites\.\*\* Verdicts: [^\n]+",
                  "**%d sites.** Verdicts: %s." % (total, dist), text,
                  count=1)
    open(INDEX, "w").write(text)
    print("merged: %d data rows total" % total)
    print("distribution:", dist)


if __name__ == "__main__":
    main()
