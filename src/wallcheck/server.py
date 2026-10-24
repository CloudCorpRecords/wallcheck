"""wallcheck MCP server: stdio JSON-RPC, Python standard library only.

Tools:
  probe_url(url, timeout?)  -> live classification object
  classify(status, headers, body) -> offline classification of a captured
      response; no network. For pipelines that fetch their own way.
  scan_exposure(url, timeout?) -> live classification object plus an
      exposure section: key-like material the page itself serves,
      classified CANDIDATE_EXPOSURE / PUBLIC_BY_DESIGN / VISITOR_TOKEN,
      fingerprint-only (never values). One honest GET, same as probe_url.
  audit(domain, timeout?)   -> owner-side agent-access audit: grade plus
      per-check PASS/WARN/FAIL. Makes up to 11 honest GETs (homepage,
      robots.txt, llms.txt, sitemap, declared sitemap if any, two OpenAPI
      paths, /api and /developers only when no spec is found, the
      Web Bot Auth directory path, and security.txt), each with the
      probe's discipline:
      honest wallcheck user agent, per-fetch timeout, bounded body
      sample, no retries. Read-only GETs; the fetch budget is stated
      in the tool description so clients can rate-limit.
"""

from __future__ import annotations

import json
import sys

from . import __version__
from .audit import audit_site
from .classify import classify
from .probe import probe_url

PROTOCOL_VERSION = "2025-06-18"

TOOLS = [
    {
        "name": "probe_url",
        "description": "Fetch a URL once with an honest wallcheck user agent "
                       "and classify what an agent actually hits: OPEN, "
                       "CHALLENGED, WALLED, LOGIN_GATED, RATE_LIMITED, or "
                       "UNREACHABLE, with the wall vendor and evidence codes.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {"type": "string"},
                "timeout": {"type": "integer", "default": 15},
            },
            "required": ["url"],
        },
    },
    {
        "name": "classify",
        "description": "Offline classification of a captured HTTP response "
                       "(status, headers, body sample). No network. Returns "
                       "verdict, vendor, and evidence codes.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "status": {"type": ["integer", "null"]},
                "headers": {"type": "object"},
                "body": {"type": "string"},
            },
            "required": ["status"],
        },
    },
    {
        "name": "scan_exposure",
        "description": "Fetch a URL once with an honest wallcheck user "
                       "agent — one honest GET, no retries — classify the "
                       "wall, and scan the served page for key-like "
                       "material: CANDIDATE_EXPOSURE (server-secret "
                       "classes that should never be public), "
                       "PUBLIC_BY_DESIGN (frontend keys and app IDs), and "
                       "VISITOR_TOKEN (short-lived JWTs). Findings carry "
                       "pattern, class, value length and a SHA-256 "
                       "fingerprint prefix — never the value itself. The "
                       "scan covers the probe's bounded body sample "
                       "(64 KB), so material served past the cap is out "
                       "of reach of this tool.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {"type": "string"},
                "timeout": {"type": "integer", "default": 15},
            },
            "required": ["url"],
        },
    },
    {
        "name": "audit",
        "description": "Owner-side agent-access audit of a domain: robots.txt "
                       "AI-agent directives, llms.txt sanity, sitemap, feed "
                       "discovery, API surface, Web Bot Auth directory, and "
                       "security contact (RFC 9116 security.txt), "
                       "each PASS/WARN/FAIL with evidence and fixes, rolled "
                       "into an A-F grade. Read-only. Makes up to 11 honest "
                       "GETs to the one domain (homepage, robots, llms, "
                       "sitemap, declared sitemap if any, two OpenAPI "
                       "paths, /api and /developers only when no spec is "
                       "found, the signed-agent directory path, "
                       "security.txt), each with "
                       "the probe's timeout and bounded body sample, no "
                       "retries. Budget the call accordingly.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "domain": {"type": "string"},
                "timeout": {"type": "integer", "default": 15},
            },
            "required": ["domain"],
        },
    },
]


def _call_tool(name, args):
    if name == "probe_url":
        url = args.get("url", "")
        if "://" not in url:
            url = "https://" + url
        return probe_url(url, timeout=int(args.get("timeout", 15)))
    if name == "classify":
        return classify(args.get("status"), args.get("headers") or {},
                        args.get("body") or "")
    if name == "scan_exposure":
        url = args.get("url", "")
        if "://" not in url:
            url = "https://" + url
        return probe_url(url, timeout=int(args.get("timeout", 15)),
                         include_exposure=True)
    if name == "audit":
        domain = args.get("domain", "")
        return audit_site(domain, timeout=int(args.get("timeout", 15)))
    raise ValueError("unknown tool: %s" % name)


def handle(msg):
    """Return the JSON-RPC response dict for one message, or None."""
    method = msg.get("method")
    mid = msg.get("id")
    if method == "initialize":
        return {"jsonrpc": "2.0", "id": mid, "result": {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "wallcheck", "version": __version__}}}
    if method in ("notifications/initialized", "notifications/cancelled"):
        return None
    if method == "ping":
        return {"jsonrpc": "2.0", "id": mid, "result": {}}
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": mid, "result": {"tools": TOOLS}}
    if method == "tools/call":
        params = msg.get("params") or {}
        try:
            result = _call_tool(params.get("name"), params.get("arguments") or {})
            payload = {"content": [{"type": "text",
                                    "text": json.dumps(result, sort_keys=True)}],
                       "structuredContent": result}
            return {"jsonrpc": "2.0", "id": mid, "result": payload}
        except Exception as e:
            return {"jsonrpc": "2.0", "id": mid, "result": {
                "content": [{"type": "text", "text": "error: %s" % e}],
                "isError": True}}
    if mid is not None:
        return {"jsonrpc": "2.0", "id": mid,
                "error": {"code": -32601, "message": "method not found: %s" % method}}
    return None


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        resp = handle(msg)
        if resp is not None:
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
