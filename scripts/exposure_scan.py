#!/usr/bin/env python3
"""Wallcheck exposure scan: find key-like material in what a site serves
to an anonymous, plainly-identified visitor.

The Monster catch (Oct 2026) proved the point: our probe stored a public
page as evidence and the page contained a server-side encryption key
shipped as a NEXT_PUBLIC_ variable. This scanner turns that accident
into a method. The pattern table and classifier live in
src/wallcheck/exposure.py — the single source of truth shared with the
probe and the capture scrubber; this script is only fetch/IO glue.
It classifies what it finds:

  CANDIDATE_EXPOSURE  server-secret classes that should never be public
                      (encryption/private keys, live secret keys, tokens,
                      credentialed DB URLs, secret JSON fields)
  PUBLIC_BY_DESIGN    the public half of the web's key pairs (Google
                      frontend keys, Stripe publishable keys, app IDs,
                      OAuth client IDs) — normal, not a finding
  VISITOR_TOKEN       short-lived JWTs a site issues to any visitor
                      (WAF/session tokens) — wall machinery, not a leak

RULES (the wallcheck hard line, in code):
- Anonymous GETs only, with wallcheck's own identifying user agent.
- One fetch per URL, no retries against a wall, no JS, no interaction.
- Found values are NEVER stored, printed or transmitted. Output carries
  only: pattern name, class, value length and a SHA-256 fingerprint
  prefix — enough for the owner to recognise their key, useless to
  anyone else.
- Candidate findings are private by default: validate live, disclose
  through the owner's published channel, publish nothing before the
  owner resolves (see campaign/EXPOSURE-LAYER.md).

Usage:
  exposure_scan.py captures <file-or-dir...>   # scan stored captures
  exposure_scan.py live <urls.txt> <outdir>   # one honest fetch per URL
"""
import json
import pathlib
import re
import sys
import time
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from wallcheck.exposure import scan_text  # noqa: E402
from wallcheck.probe import USER_AGENT  # noqa: E402


def fetch(url: str, timeout=20, limit=2_000_000):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT,
                                               "Accept": "text/html,*/*"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read(limit).decode(errors="ignore")
    except urllib.error.HTTPError as e:
        try:
            return e.code, e.read(limit).decode(errors="ignore")
        except Exception:
            return e.code, ""
    except Exception:
        return None, ""


def site_of(url: str) -> str:
    return re.sub(r"^https?://", "", url).split("/")[0]


def run_captures(paths):
    out = []
    for raw in paths:
        p = pathlib.Path(raw)
        files = sorted(p.rglob("*.json")) if p.is_dir() else [p]
        for f in files:
            text = f.read_text(errors="ignore")
            body = text
            try:
                body = json.loads(text).get("body", text)
            except Exception:
                pass
            out += scan_text(body, f.stem, str(f))
    return out


def run_live(urls_file, outdir):
    outdir = pathlib.Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    urls = [u.strip() for u in pathlib.Path(urls_file).read_text().splitlines()
            if u.strip().startswith("http")]
    findings, doors = [], {}
    log = (outdir / "run.log").open("a")
    for i, url in enumerate(urls, 1):
        site = site_of(url)
        status, body = fetch(url)
        if body:
            findings += scan_text(body, site, url)
        # front-door check: is there a published security contact route?
        origin = "https://" + site
        s_status, _ = fetch(origin + "/.well-known/security.txt", timeout=10,
                            limit=2000)
        doors[site] = {"security_txt": s_status == 200, "home_status": status}
        if i % 25 == 0 or i == len(urls):
            msg = f"{i}/{len(urls)} sites, {len(findings)} findings so far"
            print(msg, flush=True)
            log.write(msg + "\n")
            log.flush()
            (outdir / "findings.json").write_text(json.dumps(findings, indent=1))
            (outdir / "front_doors.json").write_text(json.dumps(doors, indent=1))
        time.sleep(0.3)
    log.close()
    return findings, doors


def main():
    mode = sys.argv[1]
    if mode == "captures":
        findings = run_captures(sys.argv[2:])
        print(json.dumps(findings, indent=1))
    elif mode == "live":
        findings, doors = run_live(sys.argv[2], sys.argv[3])
        from collections import Counter
        c = Counter(f["class"] for f in findings)
        cand = [f for f in findings if f["class"] == "CANDIDATE_EXPOSURE"]
        print("DONE", dict(c))
        print("candidate sites:", sorted({f["site"] for f in cand}))
        print("sites with security.txt:", sum(1 for d in doors.values()
                                               if d["security_txt"]), "/", len(doors))
    else:
        raise SystemExit("mode must be captures|live")


if __name__ == "__main__":
    main()
