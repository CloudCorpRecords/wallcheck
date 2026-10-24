#!/usr/bin/env python3
"""Wave 7 runner: Leg A (expansion probe), Leg B (round-5 stability
re-probe + history.jsonl append), Leg C (directory census v2).

Method (same discipline as Waves 4/6): one honest fetch per target,
wallcheck UA, no retries, back off on 429 (a 429 ends that target's
turn). Incremental saves after every row so a restart resumes
without re-probing (the W2-006 lesson).

Usage: python3 run_wave7.py [a|b|c|all]
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
sys.path.insert(0, os.path.join(ROOT, "src"))

ROUND = 5
PRIMARY_PATH = "/.well-known/http-message-signatures-directory"
VARIANT_PATH = "/.well-known/http-message-signatures"


def save_json(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=2, sort_keys=True)
    os.replace(tmp, path)


def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_index(path):
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


def load_targets(path):
    out, cat = [], None
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


def probe_cli(url, timeout=120):
    env = dict(os.environ, PYTHONPATH=os.path.join(ROOT, "src"))
    try:
        p = subprocess.run(
            [sys.executable, "-m", "wallcheck", "probe", url, "--json"],
            capture_output=True, text=True, timeout=timeout, cwd=ROOT,
            env=env)
        return json.loads(p.stdout)
    except Exception as e:
        return {"url": url, "final_url": url, "status": None,
                "verdict": "RUNNER_ERROR", "vendor": None,
                "evidence": ["RUNNER: %s: %s" % (type(e).__name__, e)],
                "elapsed_ms": 0, "redirect_chain": []}


# ---------------------------------------------------------------- Leg A

def leg_a():
    out_path = os.path.join(HERE, "results-expansion4.json")
    targets = load_targets(os.path.join(HERE, "targets-expansion4-final.txt"))
    results, done = [], set()
    if os.path.exists(out_path):
        with open(out_path) as f:
            results = json.load(f)
        done = {r["url"] for r in results}
        print("leg A resuming: %d/%d recorded" % (len(done), len(targets)),
              flush=True)
    for i, (cat, url) in enumerate(targets, 1):
        if url in done:
            continue
        r = probe_cli(url)
        r["category"] = cat
        r["round"] = "wave7-expansion"
        r["ts"] = now_iso()
        results.append(r)
        save_json(out_path, results)
        print("[A %d/%d] %-42s %-12s %-12s %s" % (
            i, len(targets), url, r["verdict"], r["vendor"] or "-",
            r["status"]), flush=True)
        time.sleep(0.25)
    print("leg A saved %d results" % len(results), flush=True)
    return results


# ---------------------------------------------------------------- Leg B

def leg_b(expansion_results):
    out_path = os.path.join(HERE, "results-round5.json")
    hist_path = os.path.join(ROOT, "validation", "wave4", "history.jsonl")
    rows = parse_index(os.path.join(ROOT, "INDEX.md"))
    exp_by_url = {r["url"]: r for r in expansion_results}
    for cat, url in load_targets(os.path.join(
            HERE, "targets-expansion4-final.txt")):
        r = exp_by_url.get(url)
        rows.append({
            "url": url, "host": urlsplit(url).hostname, "category": cat,
            "verdict": r["verdict"] if r else None,
            "vendor": r["vendor"] if r else None,
            "status": r["status"] if r else None,
        })
    results, done = [], set()
    if os.path.exists(out_path):
        with open(out_path) as f:
            results = json.load(f)
        # Round-5 records key the target as "target" (history schema),
        # not "url" — the Wave 4 resume path this was copied from
        # never executed, so its r["url"] bug survived unnoticed.
        done = {r.get("url") or r.get("target") for r in results}
        print("leg B resuming: %d/%d recorded" % (len(done), len(rows)),
              flush=True)
    hist = open(hist_path, "a")
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
        print("[B %d/%d] %-42s %-12s %-12s %s (was %s)" % (
            i, len(rows), row["url"], r["verdict"], r["vendor"] or "-",
            r["status"], row["verdict"]), flush=True)
        time.sleep(0.25)
    hist.close()
    print("leg B saved %d results" % len(results), flush=True)
    return rows


# ---------------------------------------------------------------- Leg C

def analyze_directory(rec):
    from wallcheck.classify import classify
    out = {"status": rec["status"], "final_url": rec["final_url"],
           "fetch_error": rec["error"]}
    cls = classify(rec["status"], rec["headers"], rec["body"],
                   final_url=rec["final_url"],
                   redirect_chain=rec["redirect_chain"],
                   error=rec["error"])
    out["verdict"] = cls["verdict"]
    out["vendor"] = cls["vendor"]
    out["evidence"] = cls["evidence"]
    body = rec["body"] or ""
    if rec["status"] == 200:
        try:
            doc = json.loads(body)
        except Exception:
            doc = None
        if isinstance(doc, dict) and isinstance(doc.get("keys"), list):
            out["result"] = "ADOPTER"
            out["top_level_fields"] = sorted(doc.keys())
            out["purpose"] = doc.get("purpose")
            out["keys"] = [{
                "kty": k.get("kty"), "crv": k.get("crv"),
                "kid": k.get("kid"), "alg": k.get("alg"),
                "nbf": k.get("nbf"), "exp": k.get("exp"),
                "x_prefix": (k.get("x") or "")[:16],
            } for k in doc["keys"] if isinstance(k, dict)]
            out["body_excerpt"] = body[:2048]
        else:
            out["result"] = "AMBIGUOUS_200"
            out["content_type"] = rec["headers"].get(
                "Content-Type") or rec["headers"].get("content-type")
            out["body_excerpt"] = body[:256]
    elif rec["status"] in (404, 410):
        out["result"] = "ABSENT"
    elif cls["verdict"] in ("WALLED", "CHALLENGED", "RATE_LIMITED",
                            "LOGIN_GATED"):
        out["result"] = "WALLED_FETCH"
    else:
        out["result"] = "NO_ANSWER"
    return out


def leg_c(rows):
    from wallcheck.audit import fetch_raw
    out_path = os.path.join(HERE, "results-directory2.json")
    hosts, seen = [], set()
    for r in rows:
        if r["host"] not in seen:
            seen.add(r["host"])
            hosts.append(r["host"])
    results, done = [], set()
    if os.path.exists(out_path):
        with open(out_path) as f:
            results = json.load(f)
        done = {r["host"] for r in results}
        print("leg C resuming: %d/%d recorded" % (len(done), len(hosts)),
              flush=True)
    for i, host in enumerate(hosts, 1):
        if host in done:
            continue
        entry = {"host": host, "ts": now_iso(), "round": ROUND}
        entry["primary"] = analyze_directory(
            fetch_raw("https://%s%s" % (host, PRIMARY_PATH)))
        entry["variant"] = None
        if entry["primary"]["result"] == "AMBIGUOUS_200":
            entry["variant"] = analyze_directory(
                fetch_raw("https://%s%s" % (host, VARIANT_PATH)))
        adopter = entry["primary"]["result"] == "ADOPTER" or (
            entry["variant"] and entry["variant"]["result"] == "ADOPTER")
        entry["adopter"] = bool(adopter)
        results.append(entry)
        save_json(out_path, results)
        print("[C %d/%d] %-38s primary=%s%s" % (
            i, len(hosts), host, entry["primary"]["result"],
            " ADOPTER" if adopter else ""), flush=True)
        time.sleep(0.25)
    print("leg C saved %d hosts, %d adopters" % (
        len(results), sum(1 for r in results if r["adopter"])), flush=True)


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    exp = None
    if which in ("a", "all"):
        exp = leg_a()
    if which in ("b", "all"):
        if exp is None:
            exp = json.load(open(os.path.join(HERE,
                                              "results-expansion4.json")))
        rows = leg_b(exp)
    if which in ("c", "all"):
        if which != "all":
            rows = parse_index(os.path.join(ROOT, "INDEX.md"))
            for cat, url in load_targets(os.path.join(
                    HERE, "targets-expansion4-final.txt")):
                rows.append({"url": url, "host": urlsplit(url).hostname,
                             "category": cat})
        leg_c(rows)


if __name__ == "__main__":
    main()
