#!/usr/bin/env python3
"""Wave 5 runner, Legs A, B and C.

Leg A — round 4: re-probe every INDEX.md row once (honest wallcheck
UA, no retries; a 429 is recorded and that target is done), save
results incrementally/resumably to results-history.json, and append
one line per newly probed target to ../wave4/history.jsonl in the
established schema ({target, round, ts, verdict, vendor, status}).

Leg B — expansion 2: probe targets-expansion2.txt once each, same
discipline, incremental save to results-expansion2.json.

Leg C — signed-vs-unsigned experiment: for each experiment target,
one unsigned probe and one Ed25519-signed probe (RFC 9421,
tag="web-bot-auth", keyfile passed as argv[2] when running leg c).
Incremental save to results-signed-experiment.json.

All probing goes through the shipped CLI (`wallcheck probe --json`),
unmodified — the same code path the Index has always used.

Usage: python3 run_wave5.py [a|b|c|all] [keyfile-for-leg-c]
"""
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from urllib.parse import urlsplit

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
HISTORY = os.path.join(HERE, "..", "wave4", "history.jsonl")
ROUND = 4


def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def save_json(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=2, sort_keys=True)
    os.replace(tmp, path)


def probe_cli(url, sign_key=None, timeout=120):
    env = dict(os.environ, PYTHONPATH=os.path.join(ROOT, "src"))
    cmd = [sys.executable, "-m", "wallcheck", "probe", url, "--json"]
    if sign_key:
        cmd += ["--sign", sign_key]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True,
                           timeout=timeout, cwd=ROOT, env=env)
        return json.loads(p.stdout)
    except Exception as e:
        return {"url": url, "final_url": url, "status": None,
                "verdict": "RUNNER_ERROR", "vendor": None,
                "evidence": ["RUNNER: %s: %s" % (type(e).__name__, e)],
                "elapsed_ms": 0, "redirect_chain": []}


# ---------------------------------------------------------------- Leg A

def parse_index(path):
    """INDEX.md table rows -> [{url, host, category, verdict, vendor,
    status}] (the merged baseline; same parser as the Wave 4 runner)."""
    rows, category = [], None
    row_re = re.compile(
        r"^\| \[([^\]]+)\]\((https?://[^)]+)\)[^|]*\| ([A-Z_]+) \| "
        r"([^|]+) \| ([^|]+) \|")
    cat_re = re.compile(r"^## (.+?) \(\d+\)\s*$")
    with open(path) as f:
        for line in f:
            m = cat_re.match(line)
            if m:
                category = m.group(1)
                continue
            m = row_re.match(line)
            if m:
                vendor = m.group(4).strip()
                status = m.group(5).strip()
                rows.append({
                    "url": m.group(2),
                    "host": urlsplit(m.group(2)).hostname,
                    "category": category,
                    "verdict": m.group(3).strip(),
                    "vendor": None if vendor in ("—", "-") else vendor,
                    "status": (None if status in ("—", "-")
                               else int(status)),
                })
    return rows


def leg_a(rows):
    out_path = os.path.join(HERE, "results-history.json")
    results, done = [], set()
    if os.path.exists(out_path):
        with open(out_path) as f:
            results = json.load(f)
        done = {r["url"] for r in results}
        if done:
            print("leg A resuming: %d/%d recorded" % (len(done),
                                                      len(rows)),
                  flush=True)
    hist = open(HISTORY, "a")
    for i, row in enumerate(rows, 1):
        if row["url"] in done:
            continue
        r = probe_cli(row["url"])
        rec = {"target": row["url"], "category": row["category"],
               "baseline_verdict": row["verdict"],
               "baseline_vendor": row["vendor"], "round": ROUND,
               "ts": now_iso(), "verdict": r["verdict"],
               "vendor": r["vendor"], "status": r["status"],
               "final_url": r["final_url"], "evidence": r["evidence"],
               "elapsed_ms": r["elapsed_ms"]}
        results.append(rec)
        save_json(out_path, results)
        hist.write(json.dumps({"target": row["url"], "round": ROUND,
                               "ts": rec["ts"], "verdict": r["verdict"],
                               "vendor": r["vendor"],
                               "status": r["status"]},
                              sort_keys=True) + "\n")
        hist.flush()
        print("[A %d/%d] %-42s %-12s %-12s %s (was %s)" % (
            i, len(rows), row["url"], r["verdict"], r["vendor"] or "-",
            r["status"], row["verdict"]), flush=True)
        time.sleep(0.25)
    hist.close()
    print("leg A saved %d results" % len(results), flush=True)


# ---------------------------------------------------------------- Leg B

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


def leg_b():
    targets = load_targets(os.path.join(HERE, "targets-expansion2.txt"))
    out_path = os.path.join(HERE, "results-expansion2.json")
    results, done = [], set()
    if os.path.exists(out_path):
        with open(out_path) as f:
            results = json.load(f)
        done = {r["url"] for r in results}
        if done:
            print("leg B resuming: %d/%d recorded" % (len(done),
                                                     len(targets)),
                  flush=True)
    for i, t in enumerate(targets, 1):
        if t["url"] in done:
            continue
        r = probe_cli(t["url"])
        rec = {"url": t["url"], "category": t["category"],
               "round": ROUND, "ts": now_iso(),
               "verdict": r["verdict"], "vendor": r["vendor"],
               "status": r["status"], "final_url": r["final_url"],
               "evidence": r["evidence"], "elapsed_ms": r["elapsed_ms"]}
        results.append(rec)
        save_json(out_path, results)
        print("[B %d/%d] %-42s %-12s %-12s %s" % (
            i, len(targets), t["url"], r["verdict"], r["vendor"] or "-",
            r["status"]), flush=True)
        time.sleep(0.25)
    print("leg B saved %d results" % len(results), flush=True)


# ---------------------------------------------------------------- Leg C

EXPERIMENT_TARGETS = [
    # the three directory adopters (Wave 4, Leg B)
    ("https://chatgpt.com", "adopter"),
    ("https://www.indeed.com", "adopter"),
    ("https://substack.com", "adopter"),
    # walled / challenged
    ("https://www.upwork.com", "walled"),
    ("https://www.fiverr.com", "challenged"),
    ("https://www.guru.com", "walled"),
    ("https://www.npmjs.com", "challenged"),
    ("https://medium.com", "walled"),
    ("https://www.ebay.com", "walled"),
    # our own properties (controls)
    ("https://clipwise.replit.app", "own-control"),
    ("https://reneturcios.replit.app", "own-control"),
    ("https://cloudcorprecords.github.io", "own-control"),
]


def leg_c(keyfile):
    out_path = os.path.join(HERE, "results-signed-experiment.json")
    results, done = [], set()
    if os.path.exists(out_path):
        with open(out_path) as f:
            results = json.load(f)
        done = {r["url"] for r in results}
        if done:
            print("leg C resuming: %d/%d recorded" % (
                len(done), len(EXPERIMENT_TARGETS)), flush=True)
    for i, (url, group) in enumerate(EXPERIMENT_TARGETS, 1):
        if url in done:
            continue
        unsigned = probe_cli(url)
        time.sleep(0.5)
        signed = probe_cli(url, sign_key=keyfile)
        rec = {"url": url, "group": group, "round": ROUND,
               "ts": now_iso(),
               "unsigned": {"verdict": unsigned["verdict"],
                            "vendor": unsigned["vendor"],
                            "status": unsigned["status"],
                            "final_url": unsigned["final_url"],
                            "evidence": unsigned["evidence"],
                            "elapsed_ms": unsigned["elapsed_ms"]},
               "signed": {"verdict": signed["verdict"],
                          "vendor": signed["vendor"],
                          "status": signed["status"],
                          "final_url": signed["final_url"],
                          "evidence": signed["evidence"],
                          "elapsed_ms": signed["elapsed_ms"]},
               "verdict_changed": (unsigned["verdict"],
                                    unsigned["status"]) != (
                                        signed["verdict"],
                                        signed["status"])}
        results.append(rec)
        save_json(out_path, results)
        print("[C %d/%d] %-38s unsigned=%s/%s signed=%s/%s %s" % (
            i, len(EXPERIMENT_TARGETS), url,
            unsigned["verdict"], unsigned["status"],
            signed["verdict"], signed["status"],
            "CHANGED" if rec["verdict_changed"] else ""), flush=True)
        time.sleep(0.25)
    print("leg C saved %d results" % len(results), flush=True)


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    keyfile = sys.argv[2] if len(sys.argv) > 2 else None
    if which in ("a", "all"):
        rows = parse_index(os.path.join(ROOT, "INDEX.md"))
        print("parsed %d index rows" % len(rows), flush=True)
        leg_a(rows)
    if which in ("b", "all"):
        leg_b()
    if which in ("c", "all"):
        if not keyfile:
            print("leg C needs the keyfile as argv[2]", flush=True)
            return 2
        leg_c(keyfile)
    return 0


if __name__ == "__main__":
    sys.exit(main())
