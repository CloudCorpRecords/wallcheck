#!/usr/bin/env python3
"""Wave runner: run `wallcheck probe <url> --json` once per target and
save the raw results. One honest fetch per target, no retries — a 429
means that target is done for the round, per wave discipline.

Usage: python3 run_wave.py <targets.txt> <results.json> [only-substring]
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))


def load_targets(path):
    targets, category = [], None
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith("#"):
                if "category:" in line:
                    category = line.split("category:", 1)[1].strip()
                continue
            targets.append({"url": line, "category": category})
    return targets


def main():
    targets_path, out_path = sys.argv[1], sys.argv[2]
    only = sys.argv[3] if len(sys.argv) > 3 else None
    targets = load_targets(targets_path)
    if only:
        targets = [t for t in targets if only in t["url"]]
    env = dict(os.environ, PYTHONPATH=os.path.join(ROOT, "src"))
    results = []
    for i, t in enumerate(targets, 1):
        try:
            p = subprocess.run(
                [sys.executable, "-m", "wallcheck", "probe", t["url"], "--json"],
                capture_output=True, text=True, timeout=90, cwd=ROOT, env=env)
            r = json.loads(p.stdout)
        except Exception as e:  # CLI itself failed to emit JSON
            r = {"url": t["url"], "final_url": t["url"], "status": None,
                 "verdict": "RUNNER_ERROR", "vendor": None,
                 "evidence": ["RUNNER: %s: %s" % (type(e).__name__, e)],
                 "elapsed_ms": 0, "redirect_chain": []}
        r["category"] = t["category"]
        results.append(r)
        print("[%d/%d] %-40s %-12s %-12s %s" % (
            i, len(targets), t["url"], r["verdict"],
            r["vendor"] or "-", r["status"]), flush=True)
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2, sort_keys=True)
    print("saved %d results to %s" % (len(results), out_path))


if __name__ == "__main__":
    main()
