"""MCP smoke driver: initialize + tools/list (pinning all four tool
names, scan_exposure included) + classify + probe_url + audit calls
against the stdio server, over real pipes.
Usage: python3 scripts/smoke_mcp.py
"""
import json
import os
import subprocess
import sys

ROOT = os.path.join(os.path.dirname(__file__), "..")
ENV = dict(os.environ, PYTHONPATH=os.path.join(ROOT, "src"))

proc = subprocess.Popen(
    [sys.executable, "-m", "wallcheck", "mcp"],
    stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, env=ENV)


def rpc(msg):
    proc.stdin.write(json.dumps(msg) + "\n")
    proc.stdin.flush()
    if msg.get("id") is None:
        return None
    return json.loads(proc.stdout.readline())


init = rpc({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
    "protocolVersion": "2025-06-18", "capabilities": {},
    "clientInfo": {"name": "smoke", "version": "0"}}})
assert init["result"]["serverInfo"]["name"] == "wallcheck", init
rpc({"jsonrpc": "2.0", "method": "notifications/initialized"})

tools = rpc({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
names = [t["name"] for t in tools["result"]["tools"]]
assert names == ["probe_url", "classify", "scan_exposure", "audit"], names

cls = rpc({"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {
    "name": "classify", "arguments": {
        "status": 403, "headers": {"Server": "cloudflare", "CF-Ray": "x-IAD"},
        "body": "<title>Just a moment...</title> challenges.cloudflare.com"}}})
sc = cls["result"]["structuredContent"]
assert sc["verdict"] == "CHALLENGED" and sc["vendor"] == "Cloudflare", sc

live = rpc({"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {
    "name": "probe_url", "arguments": {"url": "https://example.com", "timeout": 15}}})
sc = live["result"]["structuredContent"]
assert sc["verdict"] == "OPEN" and sc["status"] == 200, sc

aud = rpc({"jsonrpc": "2.0", "id": 5, "method": "tools/call", "params": {
    "name": "audit", "arguments": {"domain": "example.com", "timeout": 15}}})
asc = aud["result"]["structuredContent"]
assert "grade" in asc and asc["grade"] in ("A", "B", "C", "D", "F", "UNREACHABLE"), asc
assert [c["check"] for c in asc["checks"]] == [
    "robots_txt", "llms_txt", "sitemap", "feed", "api", "signed_agents"], asc

proc.stdin.close()
proc.wait(timeout=10)
print("MCP SMOKE OK: initialize, tools/list", names)
print("  classify ->", cls["result"]["structuredContent"]["verdict"],
      cls["result"]["structuredContent"]["vendor"])
print("  probe_url(example.com) ->", sc["verdict"], sc["status"],
      "%dms" % sc["elapsed_ms"])
print("  audit(example.com) -> grade", asc["grade"],
      "%d/%d" % (asc["score"], asc["max_score"]))
