#!/usr/bin/env python3
"""Wave 2 path runner: probe key subpaths per platform, one honest
fetch per URL, via the wallcheck CLI. If a platform answers 429, the
rest of that platform's paths are SKIPPED without fetching (back off
entirely, per wave discipline).

Usage: python3 run_paths.py <paths.txt> <results.json>
"""
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))


def load_paths(path):
    rows = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            platform, label, url = line.split("|", 2)
            rows.append({"platform": platform, "label": label, "url": url})
    return rows


def main():
    paths_file, out_path = sys.argv[1], sys.argv[2]
    rows = load_paths(paths_file)
    env = dict(os.environ, PYTHONPATH=os.path.join(ROOT, "src"))
    throttled = {}  # platform -> url that returned 429
    results = []
    for i, row in enumerate(rows, 1):
        platform = row["platform"]
        if platform in throttled:
            r = {"url": row["url"], "final_url": row["url"], "status": None,
                 "verdict": "SKIPPED", "vendor": None,
                 "evidence": ["BACKED_OFF_AFTER_429: %s" % throttled[platform]],
                 "elapsed_ms": 0, "redirect_chain": []}
        else:
            try:
                p = subprocess.run(
                    [sys.executable, "-m", "wallcheck", "probe", row["url"],
                     "--json"],
                    capture_output=True, text=True, timeout=90, cwd=ROOT,
                    env=env)
                r = json.loads(p.stdout)
            except Exception as e:
                r = {"url": row["url"], "final_url": row["url"],
                     "status": None, "verdict": "RUNNER_ERROR",
                     "vendor": None,
                     "evidence": ["RUNNER: %s: %s" % (type(e).__name__, e)],
                     "elapsed_ms": 0, "redirect_chain": []}
            if r["verdict"] == "RATE_LIMITED":
                throttled[platform] = row["url"]
            time.sleep(0.25)
        r["platform"] = platform
        r["label"] = row["label"]
        results.append(r)
        print("[%d/%d] %-9s %-13s %-12s %-12s %s" % (
            i, len(rows), platform, row["label"], r["verdict"],
            r["vendor"] or "-", r["status"]), flush=True)
        # save incrementally: a dead runner must not lose the wave
        with open(out_path, "w") as f:
            json.dump(results, f, indent=2, sort_keys=True)
    print("saved %d results to %s" % (len(results), out_path))


if __name__ == "__main__":
    main()
