#!/usr/bin/env python3
"""Wave 6 expansion pilot: probe the first N targets of
targets-expansion3-clean.txt (one honest fetch each, wallcheck UA,
no retries; a 429 is recorded and that target is done), incremental
save to results-expansion3-pilot.json.

Probing goes through the shipped CLI (`wallcheck probe --json`),
unmodified.

Usage: python3 run_wave6_pilot.py [N]
"""
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(HERE, "results-expansion3-pilot.json")


def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def save_json(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=2, sort_keys=True)
    os.replace(tmp, path)


def load_targets(path):
    out = []
    cat = None
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith("# category:"):
                cat = line.split(":", 1)[1].strip()
                continue
            if line.startswith("#"):
                continue
            out.append((cat, line))
    return out


def probe_cli(url, timeout=60):
    env = dict(os.environ, PYTHONPATH=os.path.join(ROOT, "src"))
    cmd = [sys.executable, "-m", "wallcheck", "probe", url, "--json"]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True,
                           timeout=timeout, cwd=ROOT, env=env)
        return json.loads(p.stdout)
    except Exception as e:
        return {"url": url, "final_url": url, "status": None,
                "verdict": "RUNNER_ERROR", "vendor": None,
                "evidence": ["RUNNER: %s: %s" % (type(e).__name__, e)],
                "elapsed_ms": 0, "redirect_chain": []}


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    targets = load_targets(os.path.join(HERE, "targets-expansion3-clean.txt"))[:n]
    done = {r.get("url") for r in json.load(open(OUT))} if os.path.exists(OUT) else set()
    results = json.load(open(OUT)) if os.path.exists(OUT) else []
    for cat, url in targets:
        if url in done:
            print("skip (done):", url, flush=True)
            continue
        r = probe_cli(url)
        r["category"] = cat
        r["round"] = "wave6-pilot"
        r["ts"] = now_iso()
        results.append(r)
        save_json(OUT, results)
        print("%-42s %s %s %s" % (url, r.get("status"), r.get("verdict"),
                                  r.get("vendor") or "-"), flush=True)
        time.sleep(2)  # politeness gap between distinct hosts
    print("pilot done: %d rows in %s" % (len(results), OUT))


if __name__ == "__main__":
    main()
