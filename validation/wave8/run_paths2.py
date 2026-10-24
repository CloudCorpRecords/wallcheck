#!/usr/bin/env python3
"""Wave 8 Leg A: depth wave 2 — path matrix for Wave 5 additions and
Wave 7's new walled/challenged rows, plus OPEN controls.

Method (Wave 2 discipline): 7 paths per platform — home, login,
signup, api/docs, robots.txt, sitemap.xml, llms.txt — one honest
fetch each via `wallcheck probe --json`, wallcheck UA, no retries,
back off on 429 (a 429 ends that platform's turn for the remaining
app paths, but machine files still get their single fetch — a 429
on a machine file is itself data).

Incremental saves after every probe (W2-006 lesson). Poison guard
(W7 lesson): if 8 consecutive probes fail at the transport layer
with proxy-looking errors, abort loudly instead of recording a
run of fake UNREACHABLEs.

Usage: python3 run_paths2.py
"""
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))

OUT = os.path.join(HERE, "results-paths2.json")
LOG = os.path.join(HERE, "run_paths2.log")

# (platform label, host, category, index verdict, index vendor,
#  login path, signup path, api path-or-full-url)
PLATFORMS = [
    # civic — Wave 5
    ("ed.gov", "www.ed.gov", "civic", "CHALLENGED", "Azure WAF",
     "/login", "/signup", "/api"),
    ("ftc.gov", "www.ftc.gov", "civic", "WALLED", "Akamai",
     "/login", "/signup", "/api"),
    ("nyc.gov", "www.nyc.gov", "civic", "WALLED", "Akamai",
     "/login", "/signup", "/api"),
    ("ssa.gov", "www.ssa.gov", "civic", "WALLED", "Akamai",
     "/login", "/signup", "/api"),
    ("state.gov", "www.state.gov", "civic", "WALLED", None,
     "/login", "/signup", "/api"),
    # civic — Wave 7
    ("sec.gov", "www.sec.gov", "civic", "WALLED", "Akamai",
     "/login", "/signup", "https://data.sec.gov/"),
    ("bls.gov", "www.bls.gov", "civic", "WALLED", "Akamai",
     "/login", "/signup", "https://api.bls.gov/"),
    # travel — Wave 5
    ("americanairlines", "www.americanairlines.com", "travel", "WALLED",
     "Akamai", "/login", "/signup", "/api"),
    ("amtrak", "www.amtrak.com", "travel", "WALLED", "Akamai",
     "/login", "/signup", "/api"),
    ("delta", "www.delta.com", "travel", "WALLED", "Akamai",
     "/login", "/signup", "/api"),
    ("hilton", "www.hilton.com", "travel", "WALLED", "Akamai",
     "/login", "/signup", "/api"),
    ("hyatt", "www.hyatt.com", "travel", "WALLED", None,
     "/login", "/signup", "/api"),
    ("marriott", "www.marriott.com", "travel", "WALLED", "Akamai",
     "/login", "/signup", "/api"),
    ("expedia", "www.expedia.com", "travel", "RATE_LIMITED", None,
     "/login", "/signup", "/api"),
    ("hotels", "www.hotels.com", "travel", "RATE_LIMITED", None,
     "/login", "/signup", "/api"),
    ("vrbo", "www.vrbo.com", "travel", "RATE_LIMITED", None,
     "/login", "/signup", "/api"),
    # travel — Wave 7
    ("easyjet", "www.easyjet.com", "travel", "WALLED", "Akamai",
     "/login", "/signup", "/api"),
    ("emirates", "www.emirates.com", "travel", "WALLED", "Akamai",
     "/login", "/signup", "/api"),
    ("orbitz", "www.orbitz.com", "travel", "RATE_LIMITED", None,
     "/login", "/signup", "/api"),
    ("travelocity", "www.travelocity.com", "travel", "RATE_LIMITED", None,
     "/login", "/signup", "/api"),
    ("tripadvisor", "www.tripadvisor.com", "travel", "CHALLENGED",
     "DataDome", "/login", "/signup", "/api"),
    ("viator", "www.viator.com", "travel", "CHALLENGED", "DataDome",
     "/login", "/signup", "/api"),
    # health — Wave 5
    ("goodrx", "www.goodrx.com", "health", "CHALLENGED", "PerimeterX",
     "/login", "/signup", "/api"),
    ("mayoclinic", "www.mayoclinic.org", "health", "WALLED", "Akamai",
     "/login", "/signup", "/api"),
    ("zocdoc", "www.zocdoc.com", "health", "CHALLENGED", "DataDome",
     "/login", "/signup", "/api"),
    # health — Wave 7
    ("unitedhealthcare", "www.unitedhealthcare.com", "health", "WALLED",
     "AWS CloudFront", "/login", "/signup", "/api"),
    # commerce — Wave 5
    ("homedepot", "www.homedepot.com", "commerce", "WALLED", "Akamai",
     "/login", "/signup", "/api"),
    ("macys", "www.macys.com", "commerce", "WALLED", "Akamai",
     "/login", "/signup", "/api"),
    ("ubereats", "www.ubereats.com", "commerce", "CHALLENGED",
     "Cloudflare", "/login", "/signup", "/api"),
    ("chewy", "www.chewy.com", "commerce", "RATE_LIMITED", "Kasada",
     "/login", "/signup", "/api"),
    # real-estate — Wave 5
    ("apartments", "www.apartments.com", "real-estate", "WALLED",
     "Akamai", "/login", "/signup", "/api"),
    ("homes", "www.homes.com", "real-estate", "WALLED", "Akamai",
     "/login", "/signup", "/api"),
    ("redfin", "www.redfin.com", "real-estate", "WALLED",
     "AWS CloudFront", "/login", "/signup", "/api"),
    # jobs — Wave 5
    ("careerbuilder", "www.careerbuilder.com", "jobs", "CHALLENGED",
     "DataDome", "/login", "/signup", "/api"),
    # jobs — Wave 7
    ("careerjet", "www.careerjet.com", "jobs", "CHALLENGED", "Cloudflare",
     "/login", "/signup", "/api"),
    ("monster.ca", "www.monster.ca", "jobs", "CHALLENGED", "DataDome",
     "/login", "/signup", "/api"),
    ("careerbuilder.ca", "www.careerbuilder.ca", "jobs", "CHALLENGED",
     "DataDome", "/login", "/signup", "/api"),
    ("catho", "www.catho.com.br", "jobs", "WALLED", None,
     "/login", "/signup", "/api"),
    # finance — Wave 7
    ("citizensbank", "www.citizensbank.com", "finance", "WALLED",
     "Akamai", "/login", "/signup", "/api"),
    # news — Wave 7
    ("sky news", "news.sky.com", "news", "WALLED", "Akamai",
     "/login", "/signup", "/api"),
    ("haaretz", "www.haaretz.com", "news", "WALLED", None,
     "/login", "/signup", "/api"),
    # OPEN controls, one per new category
    ("usa.gov", "www.usa.gov", "civic", "OPEN", None,
     "/login", "/signup", "/api"),
    ("chase.com", "www.chase.com", "finance", "OPEN", None,
     "/login", "/signup", "/api"),
    ("airbnb", "www.airbnb.com", "travel", "OPEN", None,
     "/login", "/signup", "/api"),
    ("webmd", "www.webmd.com", "health", "OPEN", None,
     "/login", "/signup", "/api"),
    ("zillow", "www.zillow.com", "real-estate", "OPEN", None,
     "/login", "/signup", "/api"),
]

PATHS = ["home", "login", "signup", "api", "robots", "sitemap", "llms"]


def save_json(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=2, sort_keys=True)
    os.replace(tmp, path)


def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def log(msg):
    print(msg, flush=True)
    with open(LOG, "a") as f:
        f.write(msg + "\n")


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


def path_url(host, login, signup, api, path):
    base = "https://%s" % host
    if path == "home":
        return base + "/"
    if path == "login":
        return base + login
    if path == "signup":
        return base + signup
    if path == "api":
        return api if api.startswith("http") else base + api
    if path == "robots":
        return base + "/robots.txt"
    if path == "sitemap":
        return base + "/sitemap.xml"
    if path == "llms":
        return base + "/llms.txt"
    raise ValueError(path)


def main():
    results, done = [], set()
    if os.path.exists(OUT):
        with open(OUT) as f:
            results = json.load(f)
        done = {(r["platform"], r["path"]) for r in results}
        log("resuming: %d/%d recorded"
            % (len(done), len(PLATFORMS) * len(PATHS)))
    total = len(PLATFORMS) * len(PATHS)
    bad_streak = 0
    for label, host, cat, idx_v, idx_vendor, login, signup, api in PLATFORMS:
        for path in PATHS:
            if (label, path) in done:
                continue
            url = path_url(host, login, signup, api, path)
            r = probe_cli(url)
            rec = {"platform": label, "host": host, "category": cat,
                   "index_verdict": idx_v, "index_vendor": idx_vendor,
                   "path": path, "url": url, "ts": now_iso(),
                   "verdict": r["verdict"], "vendor": r["vendor"],
                   "status": r["status"], "final_url": r["final_url"],
                   "evidence": r["evidence"],
                   "elapsed_ms": r["elapsed_ms"],
                   "redirect_chain": r["redirect_chain"]}
            results.append(rec)
            save_json(OUT, results)
            log("[%d/%d] %-18s %-8s %-12s %-12s %s" % (
                len(results), total, label, path, r["verdict"],
                r["vendor"] or "-", r["status"]))
            ev = " ".join(r["evidence"])
            if r["verdict"] in ("RUNNER_ERROR",) or "Tunnel" in ev:
                bad_streak += 1
            else:
                bad_streak = 0
            if bad_streak >= 8:
                log("ABORT: 8 consecutive transport/proxy failures — "
                    "possible egress-credential rotation (W7 lesson). "
                    "Last good record kept; restart from a fresh shell.")
                return 2
            time.sleep(0.25)
    log("done: %d results" % len(results))
    return 0


if __name__ == "__main__":
    sys.exit(main())
