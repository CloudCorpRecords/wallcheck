#!/usr/bin/env python3
"""Wave 3 runner: `wallcheck probe <url> --json` once per target,
results saved INCREMENTALLY after every probe and resumable (URLs
already present in the output with a real verdict are skipped) — the
W2-006 lesson: a runner that dies mid-wave must not lose the wave.

One honest fetch per target, no retries; a 429 is recorded and that
target is done.

Usage: python3 run_wave3.py <targets.txt> <results.json>
"""
import json
import os
import subprocess
import sys
import time

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


def save(out_path, results):
    tmp = out_path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(results, f, indent=2, sort_keys=True)
    os.replace(tmp, out_path)


def main():
    targets_path, out_path = sys.argv[1], sys.argv[2]
    targets = load_targets(targets_path)
    results, done = [], set()
    if os.path.exists(out_path):
        with open(out_path) as f:
            results = json.load(f)
        done = {r["url"] for r in results if r["verdict"] != "RUNNER_ERROR"}
        if done:
            print("resuming: %d/%d already recorded" % (len(done), len(targets)),
                  flush=True)
    env = dict(os.environ, PYTHONPATH=os.path.join(ROOT, "src"))
    for i, t in enumerate(targets, 1):
        if t["url"] in done:
            continue
        try:
            p = subprocess.run(
                [sys.executable, "-m", "wallcheck", "probe", t["url"], "--json"],
                capture_output=True, text=True, timeout=120, cwd=ROOT, env=env)
            r = json.loads(p.stdout)
        except Exception as e:
            r = {"url": t["url"], "final_url": t["url"], "status": None,
                 "verdict": "RUNNER_ERROR", "vendor": None,
                 "evidence": ["RUNNER: %s: %s" % (type(e).__name__, e)],
                 "elapsed_ms": 0, "redirect_chain": []}
        r["category"] = t["category"]
        results.append(r)
        save(out_path, results)
        print("[%d/%d] %-42s %-12s %-12s %s" % (
            i, len(targets), t["url"], r["verdict"],
            r["vendor"] or "-", r["status"]), flush=True)
        time.sleep(0.25)
    print("saved %d results to %s" % (len(results), out_path))


if __name__ == "__main__":
    main()
