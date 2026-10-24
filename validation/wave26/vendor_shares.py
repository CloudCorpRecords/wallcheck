"""Wave 26 Leg C: vendor shares across the standing INDEX's
WALLED and CHALLENGED rows, parsed from the INDEX.md table.
Prints per-verdict vendor counts so each share can be verified
against the rows themselves."""

import collections
import os
import re

BASE = os.path.join(os.path.dirname(__file__), "..", "..")
INDEX = os.path.join(BASE, "INDEX.md")
ROW = re.compile(r"^\| \[([^\]]+)\]\((https?://[^)]+)\) \| (\w+) \| "
                 r"([^|]+) \| (\S+) \|")


def main():
    counts = collections.defaultdict(collections.Counter)
    rows = collections.defaultdict(list)
    total = collections.Counter()
    with open(INDEX) as f:
        for line in f:
            m = ROW.match(line.strip())
            if not m:
                continue
            name, url, verdict, vendor, status = m.groups()
            vendor = vendor.strip()
            total[verdict] += 1
            if verdict in ("WALLED", "CHALLENGED"):
                key = vendor if vendor not in ("—", "-") else "NONE"
                counts[verdict][key] += 1
                rows[(verdict, key)].append(name)
    for verdict in ("WALLED", "CHALLENGED"):
        print("=== %s: %d rows ===" % (verdict, total[verdict]))
        for vendor, n in counts[verdict].most_common():
            print("  %-28s %d" % (vendor, n))
    print("totals: %s" % dict(total))
    print("--- WALLED rows by vendor ---")
    for (verdict, vendor), names in sorted(rows.items()):
        if verdict == "WALLED":
            print("%s: %s" % (vendor, ", ".join(sorted(names))))


if __name__ == "__main__":
    main()
