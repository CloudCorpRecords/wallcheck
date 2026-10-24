#!/usr/bin/env python3
"""Wave 7 Leg D: audit sweep over the 50 most-walled domains.

Reads validation/wave7/audit-sweep-targets.txt (one hostname per
line), runs `wallcheck audit <host> --json` once each, saves
incrementally to results-audit-sweep.json. One honest audit per
domain; the audit tool itself fetches each machine file once.
"""
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))


def save_json(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=2, sort_keys=True)
    os.replace(tmp, path)


def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def main():
    targets = [l.strip() for l in open(
        os.path.join(HERE, "audit-sweep-targets.txt")) if l.strip()
        and not l.startswith("#")]
    out_path = os.path.join(HERE, "results-audit-sweep.json")
    results, done = [], set()
    if os.path.exists(out_path):
        with open(out_path) as f:
            results = json.load(f)
        done = {r["host"] for r in results}
        print("resuming: %d/%d recorded" % (len(done), len(targets)),
              flush=True)
    env = dict(os.environ, PYTHONPATH=os.path.join(ROOT, "src"))
    for i, host in enumerate(targets, 1):
        if host in done:
            continue
        try:
            p = subprocess.run(
                [sys.executable, "-m", "wallcheck", "audit", host, "--json"],
                capture_output=True, text=True, timeout=180, cwd=ROOT,
                env=env)
            r = json.loads(p.stdout)
        except Exception as e:
            r = {"host": host, "grade": "RUNNER_ERROR",
                 "error": "%s: %s" % (type(e).__name__, e)}
        r["host"] = host
        r["ts"] = now_iso()
        results.append(r)
        save_json(out_path, results)
        print("[D %d/%d] %-38s grade=%s" % (
            i, len(targets), host, r.get("grade")), flush=True)
        time.sleep(0.25)
    print("audit sweep saved %d results" % len(results), flush=True)


if __name__ == "__main__":
    main()
