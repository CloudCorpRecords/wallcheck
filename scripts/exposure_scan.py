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
  exposure_scan.py deep <urls.txt> <outdir> [--max-assets N] [--max-paths N]
                        [--offset N] [--limit M]
      # deep mode (roadmap Waves 2+3): per site, the root page plus its
      # same-origin JS assets (document order, capped), each asset's
      # publicly served .map source map, and the standard app-shell
      # paths /login, /signin, /app — every file fetched exactly once,
      # everything scanned with the same library. Worst case per site:
      # 1 + 2*max-assets + max-paths GETs (20 with the defaults 8/3).
      # --offset/--limit process only urls[offset:offset+limit], so a
      # long sweep can run as restart-survivable slices; an offset run
      # writes findings_slice_<offset>.json / run_slice_<offset>.log
      # instead of findings.json / run.log.
"""
import json
import pathlib
import re
import sys
import time
import urllib.error
import urllib.parse
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


# --- deep mode -----------------------------------------------------------
# Where keys actually hide: not in homepage HTML but in the JS bundles
# and app shells a site serves any anonymous visitor. Deep mode follows
# exactly three kinds of publicly served files — the page's own
# same-origin script assets, each asset's .map source map, and a tiny
# standard list of app-shell paths. It is deliberately NOT a path
# fuzzer: the path list below is fixed and published in
# campaign/EXPOSURE-LAYER.md.

APP_SHELL_PATHS = ["/login", "/signin", "/app"]
DEEP_PAUSE = 0.25  # seconds between requests, per site

_TAG_URL = re.compile(
    r"<(?:script|link)\b[^>]*?(?:src|href)\s*=\s*[\"']([^\"']+)[\"']",
    re.I,
)


def extract_asset_urls(html: str, page_url: str, max_assets: int):
    """Same-origin .js asset URLs referenced by <script src>/<link href>,
    resolved against page_url, deduped in document order, capped."""
    page = urllib.parse.urlsplit(page_url)
    out, seen = [], set()
    for raw in _TAG_URL.findall(html):
        resolved = urllib.parse.urljoin(page_url, raw.strip())
        parts = urllib.parse.urlsplit(resolved)
        if parts.scheme not in ("http", "https"):
            continue
        if parts.netloc.lower() != page.netloc.lower():
            continue  # first-party only: no CDN, no third-party hosts
        if not parts.path.lower().endswith((".js", ".mjs")):
            continue
        if resolved in seen:
            continue
        seen.add(resolved)
        out.append(resolved)
        if len(out) >= max_assets:
            break
    return out


def map_url_for(asset_url: str) -> str:
    """The conventional source-map URL for a JS asset: asset + '.map'."""
    return asset_url.split("#", 1)[0] + ".map"


def deep_scan_site(root_url: str, max_assets=8, max_paths=3, pause=DEEP_PAUSE):
    """Scan one site the deep way. Returns findings; every finding's
    'source' is the exact URL the material was served from. Uses the
    module-level fetch() so tests can stub the network out entirely."""
    site = site_of(root_url)
    parts = urllib.parse.urlsplit(root_url)
    origin = "%s://%s" % (parts.scheme, parts.netloc)
    findings = []
    first = [True]

    def get(url, limit=2_000_000):
        if first[0]:
            first[0] = False
        elif pause:
            time.sleep(pause)
        return fetch(url, limit=limit)

    # 1. The root page itself.
    _, body = get(root_url)
    if body:
        findings += scan_text(body, site, root_url)
        # 2. Its same-origin JS assets, and each asset's source map.
        for asset in extract_asset_urls(body, root_url, max_assets):
            _, js = get(asset)
            if js:
                findings += scan_text(js, site, asset)
            map_url = map_url_for(asset)
            m_status, m_body = get(map_url, limit=5_000_000)
            # Only a served (200) map is a map; a 404 body is the site's
            # error page, not source material. Absent maps stay silent.
            if m_status == 200 and m_body:
                findings += scan_text(m_body, site, map_url)
    # 3. App-shell paths: scan whatever is served, any status — the
    # Monster login page answered 404 while serving the full app shell.
    for path in APP_SHELL_PATHS[:max_paths]:
        url = origin + path
        _, shell = get(url)
        if shell:
            findings += scan_text(shell, site, url)
    return findings


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


def run_deep(urls_file, outdir, max_assets=8, max_paths=3, offset=0,
             limit=None):
    outdir = pathlib.Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    all_urls = [u.strip() for u in pathlib.Path(urls_file).read_text().splitlines()
                if u.strip().startswith("http")]
    urls = all_urls[offset:offset + limit if limit else None]
    if offset > 0:
        findings_name = f"findings_slice_{offset}.json"
        log_name = f"run_slice_{offset}.log"
    else:
        findings_name = "findings.json"
        log_name = "run.log"
    findings = []
    log = (outdir / log_name).open("a")
    for i, url in enumerate(urls, 1):
        findings += deep_scan_site(url, max_assets=max_assets,
                                   max_paths=max_paths)
        if i % 25 == 0 or i == len(urls):
            # Progress counts are global (offset + i of the full list),
            # so slice logs read as one continuous sweep: 125/500, ...
            msg = (f"{offset + i}/{len(all_urls)} sites, "
                   f"{len(findings)} findings so far")
            print(msg, flush=True)
            log.write(msg + "\n")
            log.flush()
            (outdir / findings_name).write_text(json.dumps(findings, indent=1))
    log.close()
    return findings


def _flag(args, name, default):
    if name in args:
        return int(args[args.index(name) + 1])
    return default


def main():
    mode = sys.argv[1]
    if mode == "captures":
        findings = run_captures(sys.argv[2:])
        print(json.dumps(findings, indent=1))
    elif mode == "deep":
        args = sys.argv[2:]
        limit = _flag(args, "--limit", 0)
        findings = run_deep(args[0], args[1],
                            max_assets=_flag(args, "--max-assets", 8),
                            max_paths=_flag(args, "--max-paths", 3),
                            offset=_flag(args, "--offset", 0),
                            limit=limit if limit > 0 else None)
        from collections import Counter
        c = Counter(f["class"] for f in findings)
        cand = [f for f in findings if f["class"] == "CANDIDATE_EXPOSURE"]
        print("DONE", dict(c))
        print("candidate sites:", sorted({f["site"] for f in cand}))
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
        raise SystemExit("mode must be captures|live|deep")


if __name__ == "__main__":
    main()
