"""Owner-side audit: grade a site's agent-access posture.

`wallcheck probe` measures what an agent hits. The audit asks the
owner's question: *if I want legitimate agents to reach my public
content, is my site set up for that — and what exactly should I fix?*

Checks (each PASS / WARN / FAIL with evidence, deterministic):

- robots_txt      robots.txt present, and what it says to named AI
                  agents (GPTBot, ClaudeBot, CCBot, Google-Extended)
- llms_txt        /llms.txt present and genuine (a soft-404 HTML page
                  served with status 200 is a FAIL, not a pass —
                  Wave 2's verification lesson)
- sitemap         /sitemap.xml (or a robots-declared sitemap) served
- feed            RSS/Atom discovery via homepage <link> tags
- api             machine-readable API surface: OpenAPI document,
                  a serving /api root, or at least a developer portal
- signed_agents   a Web Bot Auth key directory published at
                  /.well-known/http-message-signatures-directory

Every fetched resource is also run through the classifier: a machine
file behind a wall is a FAIL with the wall named (Wave 2 measured
platforms that challenge even robots.txt).

Fetching is injectable so the evaluation core is a pure function of
captured responses — fixtures exercise it fully offline, same as the
classifier. Live runs make one honest fetch per resource, identified
wallcheck UA, no retries.
"""

from __future__ import annotations

import gzip
import json
import re
import urllib.error
import urllib.request
from urllib.parse import urljoin, urlsplit

from .classify import classify
from .probe import BODY_CAP, USER_AGENT, _RecordingRedirectHandler

PASS, WARN, FAIL = "PASS", "WARN", "FAIL"
_POINTS = {PASS: 2, WARN: 1, FAIL: 0}

AI_AGENTS = ("GPTBot", "ClaudeBot", "CCBot", "Google-Extended")
SIG_DIRECTORY_PATH = "/.well-known/http-message-signatures-directory"


# ---------------------------------------------------------------- fetch

def _decode_body(raw, headers):
    """Decode a fetched body sample, decompressing gzip when the
    server sent Content-Encoding: gzip (Wave 12, W12-D8): urllib does
    not decompress on its own, so without this a gzipped sitemap
    reads as binary garbage and misgrades. Decompressed output is
    capped at BODY_CAP like any other sample; on decompression
    failure the raw bytes are kept (a corrupt body is evidence, not
    a crash)."""
    if raw and "gzip" in _hget(headers, "content-encoding").lower():
        try:
            raw = gzip.decompress(raw)
        except Exception:
            pass
    return raw[:BODY_CAP].decode("utf-8", errors="replace")


def fetch_raw(url, timeout=15):
    """One honest fetch returning the raw response record the audit
    evaluates (status, headers, body sample, final_url, error)."""
    handler = _RecordingRedirectHandler()
    opener = urllib.request.build_opener(handler)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    status, headers, body, final_url, error = None, {}, "", url, None
    try:
        with opener.open(req, timeout=timeout) as resp:
            status = resp.status
            headers = dict(resp.headers.items())
            final_url = resp.geturl()
            body = _decode_body(resp.read(BODY_CAP), headers)
    except urllib.error.HTTPError as e:
        status = e.code
        headers = dict(e.headers.items()) if e.headers else {}
        final_url = e.geturl() or url
        try:
            body = _decode_body(e.read(BODY_CAP), headers)
        except Exception:
            body = ""
    except Exception as e:  # URLError, timeout, TLS, DNS...
        error = "%s: %s" % (type(e).__name__, e)
    return {"url": url, "final_url": final_url, "status": status,
            "headers": headers, "body": body, "error": error,
            "redirect_chain": handler.chain}


def _hget(headers, name):
    for k, v in (headers or {}).items():
        if str(k).lower() == name.lower():
            return str(v)
    return ""


def _wall(rec):
    """Classify a fetched resource; return (verdict, vendor) if the
    resource itself is behind a wall, else None."""
    r = classify(rec.get("status"), rec.get("headers") or {},
                 rec.get("body") or "", final_url=rec.get("final_url", ""),
                 redirect_chain=rec.get("redirect_chain") or [],
                 error=rec.get("error"))
    if r["verdict"] in ("CHALLENGED", "WALLED"):
        return r["verdict"], r["vendor"]
    return None


# ---------------------------------------------------------------- robots

def parse_robots(text):
    """Minimal robots.txt parser: groups of user-agents -> rules,
    plus Sitemap: lines. Returns (groups, sitemaps) where groups is a
    list of (agents_lower_set, [(directive, value), ...])."""
    groups, sitemaps = [], []
    agents, rules, in_group = set(), [], False
    for raw in (text or "").splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        field, _, value = line.partition(":")
        field, value = field.strip().lower(), value.strip()
        if field == "sitemap":
            sitemaps.append(value)
        elif field == "user-agent":
            if in_group and rules:
                groups.append((agents, rules))
                agents, rules = set(), []
            agents.add(value.lower())
            in_group = True
        elif field in ("disallow", "allow") and in_group:
            rules.append((field, value))
    if in_group:
        groups.append((agents, rules))
    return groups, sitemaps


def _agent_state(groups, agent):
    """blocked / restricted / open for one named agent, following
    robots semantics: the agent's own group wins, else the * group."""
    mine = [rules for agents, rules in groups if agent.lower() in agents]
    applicable = mine if mine else [r for a, r in groups if "*" in a]
    disallows = [v for rules in applicable for (f, v) in rules
                 if f == "disallow" and v]
    if any(v == "/" for v in disallows):
        return "blocked"
    if disallows:
        return "restricted"
    return "open"


def _check_robots(rec):
    ev = []
    if rec.get("error"):
        return FAIL, ["FETCH_ERROR: %s" % rec["error"]], \
            "robots.txt could not be fetched at all."
    wall = _wall(rec)
    if wall:
        return FAIL, ["WALLED: %s (%s)" % wall], \
            "robots.txt itself is behind a %s wall (%s) — the file " \
            "written for machines is not machine-reachable." % wall
    if rec.get("status") != 200:
        return FAIL, ["STATUS_%s" % rec.get("status")], \
            "No robots.txt served (status %s): crawlers and agents " \
            "get no directives at all." % rec.get("status")
    if _looks_like_html(rec.get("body"), rec.get("headers")):
        # Wave 10, W10-B9d: the robots check lacked the HTML gate
        # the llms check has — an HTML error page at /robots.txt is
        # a soft-404, not a (permissive, empty) robots file.
        return FAIL, ["SOFT_404_HTML"], \
            "robots.txt returns 200 but serves HTML (a soft-404 " \
            "error page) — agents parsing it as directives get " \
            "nothing, and the file's absence is hidden."
    ev.append("ROBOTS_200")
    groups, sitemaps = parse_robots(rec.get("body") or "")
    if sitemaps:
        ev.append("SITEMAP_DECLARED: %s" % sitemaps[0])
    states = {a: _agent_state(groups, a) for a in AI_AGENTS}
    blocked = [a for a, s in states.items() if s == "blocked"]
    restricted = [a for a, s in states.items() if s == "restricted"]
    for a in blocked:
        ev.append("AI_BLOCKED: %s" % a)
    for a in restricted:
        ev.append("AI_RESTRICTED: %s" % a)
    wildcard_all = any("*" in agents and
                       any(f == "disallow" and v == "/" for f, v in rules)
                       for agents, rules in groups)
    if wildcard_all:
        ev.append("WILDCARD_BLOCK_ALL")
    if len(blocked) == len(AI_AGENTS):
        # Wave 11, W11-C8b: FAIL means every tracked agent is
        # blocked — not merely that a wildcard Disallow: / exists.
        # A wildcard rule with a named-agent carve-out (GPTBot
        # Allow: /, ClaudeBot restricted to /private) leaves that
        # agent reachable, so the posture is WARN, not FAIL. When
        # no carve-out exists, all four agents are blocked and this
        # branch still fires exactly as before.
        return FAIL, ev, "robots.txt blocks every tracked AI agent " \
            "outright."
    if blocked or restricted:
        return WARN, ev, "robots.txt is served, but named AI agents " \
            "are refused: %s." % ", ".join(
                ["%s blocked" % a for a in blocked] +
                ["%s restricted" % a for a in restricted])
    return PASS, ev, "robots.txt served; no tracked AI agent is " \
        "blocked or restricted."


# ---------------------------------------------------------------- llms

def _looks_like_html(body, headers):
    ct = _hget(headers, "content-type").lower()
    head = (body or "").lstrip()[:200].lower()
    return "text/html" in ct or head.startswith("<!doctype") \
        or head.startswith("<html")


_MARKDOWN_HEADING_RE = re.compile(r"^#{1,6}\s+\S", re.MULTILINE)
_MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\([^)]+\)")
_MARKDOWN_LINK_TARGET_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def _has_usable_link(body):
    """True when the body carries a markdown link pointing somewhere
    other than a fragment of the same document (Wave 14, W14-F7c):
    `[Intro](#intro)` links to the llms.txt file itself, not to site
    content — a table of contents for a file that indexes nothing.
    Empty targets do not count either."""
    for m in _MARKDOWN_LINK_TARGET_RE.finditer(body or ""):
        target = m.group(1).strip()
        if target and not target.startswith("#"):
            return True
    return False
_HTML_TAG_RE = re.compile(
    r"<(html|head|body|div|p|a|span|script|link|meta|title|!doctype)\b",
    re.IGNORECASE)


def _looks_like_markdown(body):
    """True when the body is markdown text with no HTML tags in it
    (Wave 12, W12-D7d): a markdown heading or link, and no real HTML
    tag in the first kilobyte. Markdown autolinks (<https://…>) do
    not match the tag pattern, and a file mixing markdown with raw
    HTML tags does not qualify — the conservative side stays FAIL."""
    b = body or ""
    if not (_MARKDOWN_HEADING_RE.search(b) or _MARKDOWN_LINK_RE.search(b)):
        return False
    return _HTML_TAG_RE.search(b[:1024]) is None


def _check_llms(rec):
    if rec.get("error"):
        return WARN, ["FETCH_ERROR: %s" % rec["error"]], \
            "/llms.txt could not be fetched (network error)."
    wall = _wall(rec)
    if wall:
        return FAIL, ["WALLED: %s (%s)" % wall], \
            "/llms.txt is behind a %s wall (%s)." % wall
    status = rec.get("status")
    if status in (404, 410):
        return WARN, ["STATUS_%s" % status], \
            "No /llms.txt (honest %s). Agents get no curated map of " \
            "the site's content." % status
    if status != 200:
        return WARN, ["STATUS_%s" % status], \
            "/llms.txt answered status %s — not a usable file." % status
    if _looks_like_html(rec.get("body"), rec.get("headers")):
        # Wave 12, W12-D7d: a server can mislabel its content-type —
        # a genuine markdown body served as text/html IS the index
        # (agents ingest the body, not the header), so a markdown body
        # with no HTML tags anywhere is not a soft-404. The carve-out
        # is scoped to this check only: the shared HTML gate still
        # catches real HTML bodies everywhere else.
        if _looks_like_markdown(rec.get("body") or ""):
            pass
        else:
            return FAIL, ["SOFT_404_HTML"], \
                "/llms.txt returns 200 but serves HTML (a soft-404 error " \
                "page or the homepage) — worse than absent: agents ingest " \
                "it as if it were the real index."
    body = rec.get("body") or ""
    try:
        doc = json.loads(body)
    except Exception:
        doc = None
    if isinstance(doc, dict) and ("error" in doc or "errors" in doc):
        # Wave 10, W10-B9a: the file's content is an error document,
        # not an index — the JSON species of the HTML soft-404. The
        # gate is error-key presence only, not format policing: a
        # JSON index without an error key is not failed here.
        return FAIL, ["JSON_ERROR_DOC"], \
            "/llms.txt returns 200 but serves a JSON error document " \
            "— worse than absent, like the HTML soft-404."
    if isinstance(doc, (dict, list)):
        # Wave 12, W12-D7c: a JSON document without an error key is
        # machine-readable data, but it is not an llms.txt (which is
        # defined as markdown text) — so PASS ("served as genuine
        # text") overstates it, while FAIL would overstate the other
        # way. WARN is the honest middle grade: usable data in the
        # wrong format at the llms.txt location.
        return WARN, ["JSON_NOT_LLMS"], \
            "/llms.txt returns 200 but serves JSON, not llms.txt " \
            "markdown — machine-readable data in the wrong format."
    if len(body.strip()) < 20:
        return WARN, ["EMPTY_BODY"], "/llms.txt is served but " \
            "effectively empty."
    if not (_has_usable_link(body)
            or re.search(r"https?://", body)
            or re.search(r"/[A-Za-z0-9_.-]+", body)):
        # Wave 13, W13-E6a: a title-only file (or any body that
        # points nowhere — no markdown link, no URL, no path) is
        # not an index, whatever its length. The length gate above
        # passes any long title line; content, not length, decides.
        # A body with even one link or path (D7b's plain-text
        # index lines) still passes.
        return WARN, ["LLMS_STUB"], "/llms.txt is served but " \
            "contains no links, URLs, or paths — a title line, " \
            "not an index agents can use."
    return PASS, ["LLMS_TEXT %d bytes" % len(body.encode("utf-8"))], \
        "/llms.txt served as genuine text (%d bytes captured)." \
        % len(body.encode("utf-8"))


# ---------------------------------------------------------------- sitemap

def _check_sitemap(rec, declared):
    if rec is None:
        return WARN, ["NOT_FETCHED"], "No sitemap candidate to check."
    if rec.get("error"):
        return WARN, ["FETCH_ERROR: %s" % rec["error"]], \
            "Sitemap could not be fetched (network error)."
    wall = _wall(rec)
    if wall:
        return FAIL, ["WALLED: %s (%s)" % wall], \
            "The sitemap is behind a %s wall (%s)." % wall
    status = rec.get("status")
    body = rec.get("body") or ""
    if status == 200 and ("<urlset" in body or "<sitemapindex" in body
                           or body.lstrip().startswith("<?xml")):
        ev = ["SITEMAP_XML"]
        if declared:
            ev.append("VIA_ROBOTS_DECLARATION")
        return PASS, ev, "Sitemap served as XML — agents can " \
            "enumerate public content without scraping."
    if status == 200:
        return WARN, ["STATUS_200_NOT_XML"], "Sitemap URL answers " \
            "200 but the body is not sitemap XML."
    return WARN, ["STATUS_%s" % status], "No sitemap at %s " \
        "(status %s)." % (rec.get("final_url"), status)


# ---------------------------------------------------------------- feed

_FEED_LINK_RE = re.compile(
    r"<link[^>]+type=[\"']application/(?:rss|atom)\+xml[\"'][^>]*>",
    re.IGNORECASE)
_HREF_RE = re.compile(r"href=[\"']([^\"']+)[\"']", re.IGNORECASE)


def _check_feed(rec):
    if rec.get("error"):
        return FAIL, ["FETCH_ERROR: %s" % rec["error"]], \
            "Homepage unreachable — feed discovery impossible."
    wall = _wall(rec)
    if wall:
        return FAIL, ["WALLED: %s (%s)" % wall], \
            "Homepage is behind a %s wall (%s); feed discovery " \
            "never gets to run." % wall
    if rec.get("status") != 200:
        return WARN, ["STATUS_%s" % rec.get("status")], \
            "Homepage answered status %s; no feed discovery " \
            "performed." % rec.get("status")
    m = _FEED_LINK_RE.search(rec.get("body") or "")
    if m:
        href = _HREF_RE.search(m.group(0))
        return PASS, ["FEED_LINK: %s" % (href.group(1) if href else "?")], \
            "Homepage advertises an RSS/Atom feed — the classic " \
            "agent escape route is signposted."
    return WARN, ["NO_FEED_LINK"], "Homepage carries no RSS/Atom " \
        "<link rel=\"alternate\"> discovery tag."


# ---------------------------------------------------------------- api

def _check_api(records, homepage_rec):
    ev = []
    link_hdr = _hget(homepage_rec.get("headers") or {}, "link").lower()
    if "rel=" in link_hdr and ("api" in link_hdr or "service-desc" in link_hdr
                               or "describedby" in link_hdr):
        ev.append("API_LINK_HEADER")
    for key in ("openapi", "openapi_wellknown"):
        rec = records.get(key)
        if rec and rec.get("status") == 200 and not rec.get("error"):
            if _is_openapi_doc(rec):
                ev.append("OPENAPI_DOC: %s" % rec["final_url"])
                return PASS, ev, "A machine-readable OpenAPI document " \
                    "is published — agents can integrate without " \
                    "touching the web surface."
            ev.append("OPENAPI_NOT_SPEC: %s status 200, not an "
                      "OpenAPI document" % rec["final_url"])
    # SPA fallback trap: single-page apps serve the same HTML shell
    # at *every* unknown path, so a 200 at /api or /developers may be
    # the app shell, not a surface. A candidate whose body is the
    # homepage's body is the shell — it proves nothing exists there.
    home_body = (homepage_rec.get("body") or "").strip()

    def _is_shell(rec):
        return bool(home_body) and _looks_like_html(
            rec.get("body"), rec.get("headers")) \
            and (rec.get("body") or "").strip() == home_body

    rec = records.get("api_root")
    if rec and not rec.get("error") and rec.get("status") is not None:
        wall = _wall(rec)
        if wall is None and rec["status"] == 200 and not _is_shell(rec) \
                and not _looks_like_html(rec.get("body"),
                                         rec.get("headers")):
            ev.append("API_ROOT_200")
            return PASS, ev, "An /api root serves — a programmatic " \
                "surface exists alongside the web surface."
        if wall is None and rec["status"] == 200 and _is_shell(rec):
            ev.append("API_ROOT_IS_APP_SHELL")
        if wall is None and rec["status"] == 401:
            ev.append("API_ROOT_401")
            return PASS, ev, "An /api root answers 401 — an API " \
                "exists and requires auth, which is a front door, " \
                "not a wall."
    rec = records.get("api_docs")
    if rec and rec.get("status") == 200 and not rec.get("error") \
            and _wall(rec) is None and not _is_shell(rec):
        ev.append("DEV_PORTAL_200")
        return WARN, ev, "A developer portal page serves, but no " \
            "machine-readable API spec was discovered."
    if rec and rec.get("status") == 200 and _is_shell(rec):
        ev.append("DEV_PORTAL_IS_APP_SHELL")
    return FAIL, ev or ["NO_API_SURFACE"], "No OpenAPI document, " \
        "serving /api root, or developer portal discovered."


# ---------------------------------------------------------------- signed

def _check_signed(rec):
    if rec is None or rec.get("error"):
        return FAIL, ["FETCH_ERROR"], "The Web Bot Auth directory " \
            "could not be fetched."
    wall = _wall(rec)
    if wall:
        return FAIL, ["WALLED: %s (%s)" % wall], \
            "The signatures directory path is behind a wall."
    status = rec.get("status")
    if status == 200:
        try:
            doc = json.loads(rec.get("body") or "")
        except Exception:
            doc = None
        if isinstance(doc, dict) and "keys" in doc:
            return PASS, ["DIRECTORY_PUBLISHED"], \
                "A Web Bot Auth key directory is published at " \
                "/.well-known/http-message-signatures-directory — " \
                "signed agents can be verified against it."
        return WARN, ["DIRECTORY_UNPARSEABLE"], "The directory URL " \
            "answers 200 but the body is not a JWKS-style key set."
    return FAIL, ["STATUS_%s" % status], \
        "No Web Bot Auth key directory published (status %s) — the " \
        "site gives signed agents no way to be recognized. Expected " \
        "almost everywhere today; recorded as data." % status


# ---------------------------------------------------------------- assembly

_FIXES = {
    "robots_txt": "Publish/maintain /robots.txt and scope any "
                  "Disallow rules to the paths that need them; a "
                  "blanket block of named AI agents also blocks the "
                  "agents your own users send.",
    "llms_txt": "Publish a genuine /llms.txt (plain text/markdown "
                "index of your key pages) — and never let the route "
                "fall through to an HTML error page.",
    "sitemap": "Serve /sitemap.xml (or declare Sitemap: in "
               "robots.txt) and keep bot walls off it: it is the "
               "file you publish *for* machines.",
    "feed": "Add <link rel=\"alternate\" type=\"application/rss+xml\"> "
            "(or Atom) discovery tags to the homepage, or publish a "
            "feed — feeds are the lowest-cost agent channel there is.",
    "api": "Publish a machine-readable API surface: an OpenAPI "
           "document (conventionally /openapi.json) or a documented "
           "/api — agents integrate against specs, not markup.",
    "signed_agents": "Publish your Web Bot Auth key directory at "
                     "/.well-known/http-message-signatures-directory "
                     "and, on the receiving side, exempt verified "
                     "signed agents from managed challenges on public "
                     "paths (authenticated paths keep full protection).",
}


def evaluate_audit(base_url, records):
    """Pure evaluation: base_url + {resource_key: fetch record} ->
    the audit object. Records keys: robots, llms, sitemap (or None),
    homepage, openapi, openapi_wellknown, api_root, api_docs, signed.
    """
    declared = []
    robots_rec = records.get("robots") or {}
    if robots_rec.get("status") == 200 and not robots_rec.get("error"):
        _, declared = parse_robots(robots_rec.get("body") or "")

    checks = []
    for name, (status, evidence, detail) in (
            ("robots_txt", _check_robots(robots_rec)),
            ("llms_txt", _check_llms(records.get("llms") or {})),
            ("sitemap", _check_sitemap(records.get("sitemap"), declared)),
            ("feed", _check_feed(records.get("homepage") or {})),
            ("api", _check_api(records, records.get("homepage") or {})),
            ("signed_agents", _check_signed(records.get("signed")))):
        checks.append({"check": name, "status": status,
                       "evidence": evidence, "detail": detail})

    score = sum(_POINTS[c["status"]] for c in checks)
    max_score = 2 * len(checks)
    home = records.get("homepage") or {}
    if home.get("error") and robots_rec.get("error"):
        grade = "UNREACHABLE"
    elif score >= 11:
        grade = "A"
    elif score >= 9:
        grade = "B"
    elif score >= 7:
        grade = "C"
    elif score >= 5:
        grade = "D"
    else:
        grade = "F"
    fixes = [_FIXES[c["check"]] for c in checks if c["status"] != PASS]
    return {"target": base_url, "grade": grade, "score": score,
            "max_score": max_score, "checks": checks, "fixes": fixes}


def _is_openapi_doc(rec):
    """A record is a real spec only if it is a 200 whose body parses
    as an OpenAPI/Swagger document — a soft-404 SPA shell served at
    /openapi.json (200, HTML) must not suppress the /api fallbacks."""
    if not rec or rec.get("error") or rec.get("status") != 200:
        return False
    try:
        doc = json.loads(rec.get("body") or "")
    except Exception:
        return False
    return isinstance(doc, dict) and ("openapi" in doc or "swagger" in doc)


def _base_of(target):
    t = target if "://" in target else "https://" + target
    parts = urlsplit(t)
    return "%s://%s" % (parts.scheme, parts.netloc)


def _is_sitemap_doc(rec):
    """A record is a usable sitemap only if it is a 200 whose body
    is sitemap XML (urlset, sitemapindex, or an XML prolog) — the
    same test _check_sitemap grades on. A 200 HTML error page is
    not a sitemap, and a dead declared URL is not a fallback."""
    if not rec or rec.get("error") or rec.get("status") != 200:
        return False
    body = rec.get("body") or ""
    return ("<urlset" in body or "<sitemapindex" in body
            or body.lstrip().startswith("<?xml"))


def audit_site(target, timeout=15, fetch=None):
    """Live audit: one honest fetch per resource, then evaluate."""
    fetch = fetch or fetch_raw
    base = _base_of(target)
    records = {}
    records["homepage"] = fetch(base + "/", timeout=timeout)
    records["robots"] = fetch(base + "/robots.txt", timeout=timeout)
    records["llms"] = fetch(base + "/llms.txt", timeout=timeout)
    records["sitemap"] = fetch(base + "/sitemap.xml", timeout=timeout)
    if not _is_sitemap_doc(records["sitemap"]):
        # Wave 14, W14-F6a/F6b: the old code consulted the
        # robots-declared Sitemap: URL only when /sitemap.xml was
        # not 200, and only the first declared line — so a
        # 200-but-HTML /sitemap.xml hid a valid declared index,
        # and a dead first declaration hid a valid second one.
        # Fall through the declared lines in order until a usable
        # sitemap document serves; the grade reflects the sitemap
        # the site actually publishes.
        _, declared = parse_robots(records["robots"].get("body") or "")
        for d in declared:
            alt = fetch(urljoin(base + "/", d), timeout=timeout)
            if _is_sitemap_doc(alt):
                records["sitemap"] = alt
                break
    records["openapi"] = fetch(base + "/openapi.json", timeout=timeout)
    records["openapi_wellknown"] = fetch(
        base + "/.well-known/openapi.json", timeout=timeout)
    spec_found = any(
        _is_openapi_doc(records[k])
        for k in ("openapi", "openapi_wellknown"))
    if not spec_found:
        records["api_root"] = fetch(base + "/api", timeout=timeout)
        records["api_docs"] = fetch(base + "/developers", timeout=timeout)
    records["signed"] = fetch(base + SIG_DIRECTORY_PATH, timeout=timeout)
    result = evaluate_audit(base, records)
    result["target"] = target
    return result
