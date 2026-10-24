#!/usr/bin/env python3
"""Wave 4 runner, Legs A and B.

Leg A — third data point: re-probe every INDEX.md row once (honest
wallcheck UA, no retries), save the round-3 results JSON
incrementally/resumably (the W2-006 lesson) and append one line per
target to history.jsonl: {target, round=3, ts, verdict, vendor,
status}.

Leg B — signed-agent acceptance expedition: for every unique INDEX
hostname, one honest fetch of
/.well-known/http-message-signatures-directory (the audit module's
fetcher + the classifier, i.e. the same code path as a probe). A 200
whose body parses as JSON with a "keys" list = ADOPTER. Only when
the primary answer is an ambiguous 200-that-is-not-a-directory do we
spend the second allowed fetch on /.well-known/http-message-signatures.
A 429 or a wall ends that domain's turn; the verdict is the data.

Usage: python3 run_wave4.py [a|b|all]
"""
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))

ROUND = 3
PRIMARY_PATH = "/.well-known/http-message-signatures-directory"
VARIANT_PATH = "/.well-known/http-message-signatures"


def parse_index(path):
    """INDEX.md table rows -> [{url, host, category, verdict, vendor,
    status}] (the Wave 3 merged baseline)."""
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
                from urllib.parse import urlsplit
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


def save_json(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=2, sort_keys=True)
    os.replace(tmp, path)


def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------- Leg A

def leg_a(rows):
    out_path = os.path.join(HERE, "results-history.json")
    hist_path = os.path.join(HERE, "history.jsonl")
    results, done = [], set()
    if os.path.exists(out_path):
        with open(out_path) as f:
            results = json.load(f)
        done = {r["url"] for r in results}
        if done:
            print("leg A resuming: %d/%d recorded" % (len(done), len(rows)),
                  flush=True)
    hist = open(hist_path, "a")
    env = dict(os.environ, PYTHONPATH=os.path.join(ROOT, "src"))
    for i, row in enumerate(rows, 1):
        if row["url"] in done:
            continue
        try:
            p = subprocess.run(
                [sys.executable, "-m", "wallcheck", "probe", row["url"],
                 "--json"],
                capture_output=True, text=True, timeout=120, cwd=ROOT,
                env=env)
            r = json.loads(p.stdout)
        except Exception as e:
            r = {"url": row["url"], "final_url": row["url"],
                 "status": None, "verdict": "RUNNER_ERROR",
                 "vendor": None,
                 "evidence": ["RUNNER: %s: %s" % (type(e).__name__, e)],
                 "elapsed_ms": 0, "redirect_chain": []}
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

def analyze_directory(rec):
    """Classify one fetched well-known response: adopter / present-
    but-not-a-directory / absent / walled / error. The verdict comes
    from the same classifier the probe uses, over the raw fetch."""
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


def leg_b(rows):
    from wallcheck.audit import fetch_raw
    out_path = os.path.join(HERE, "results-directory.json")
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
        if done:
            print("leg B resuming: %d/%d recorded" % (len(done), len(hosts)),
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
        print("[B %d/%d] %-38s primary=%s%s" % (
            i, len(hosts), host, entry["primary"]["result"],
            " ADOPTER" if adopter else ""), flush=True)
        time.sleep(0.25)
    print("leg B saved %d hosts, %d adopters" % (
        len(results), sum(1 for r in results if r["adopter"])), flush=True)


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    rows = parse_index(os.path.join(ROOT, "INDEX.md"))
    print("parsed %d index rows" % len(rows), flush=True)
    if which in ("a", "all"):
        leg_a(rows)
    if which in ("b", "all"):
        leg_b(rows)


if __name__ == "__main__":
    main()
