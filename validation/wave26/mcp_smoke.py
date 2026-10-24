"""Wave 26: MCP smoke — all three tools over stdio JSON-RPC.
classify (offline), probe_url (one honest fetch), audit (one
domain, the tool's documented <=10 GETs)."""

import json
import os
import subprocess
import sys

BASE = os.path.join(os.path.dirname(__file__), "..", "..")
ENV = dict(os.environ, PYTHONPATH=os.path.join(BASE, "src"))


def rpc(proc, req):
    proc.stdin.write(json.dumps(req) + "\n")
    proc.stdin.flush()
    return json.loads(proc.stdout.readline())


def main():
    proc = subprocess.Popen(
        [sys.executable, "-m", "wallcheck.server"],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        text=True, env=ENV, cwd=BASE)
    try:
        r = rpc(proc, {"jsonrpc": "2.0", "id": 1, "method": "initialize",
                       "params": {"protocolVersion": "2024-11-05",
                                  "capabilities": {},
                                  "clientInfo": {"name": "smoke",
                                                 "version": "0"}}})
        assert "result" in r, r
        proc.stdin.write(json.dumps(
            {"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n")
        proc.stdin.flush()
        r = rpc(proc, {"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        names = [t["name"] for t in r["result"]["tools"]]
        assert names == ["probe_url", "classify", "audit"], names
        print("tools/list:", names)

        r = rpc(proc, {"jsonrpc": "2.0", "id": 3,
                       "method": "tools/call",
                       "params": {"name": "classify",
                                  "arguments": {
                                      "status": 403, "headers": {},
                                      "body": "<html><body>Just a "
                                              "moment</body></html>"}}})
        out = json.loads(r["result"]["content"][0]["text"])
        print("classify:", out["verdict"], out["vendor"])
        assert out["verdict"] == "CHALLENGED"

        r = rpc(proc, {"jsonrpc": "2.0", "id": 4,
                       "method": "tools/call",
                       "params": {"name": "probe_url",
                                  "arguments": {
                                      "url": "https://example.com"}}})
        out = json.loads(r["result"]["content"][0]["text"])
        print("probe_url:", out["verdict"], out["status"])
        assert out["verdict"] == "OPEN"

        r = rpc(proc, {"jsonrpc": "2.0", "id": 5,
                       "method": "tools/call",
                       "params": {"name": "audit",
                                  "arguments": {"domain": "example.com"}}})
        out = json.loads(r["result"]["content"][0]["text"])
        print("audit: grade", out["grade"],
              "checks", len(out["checks"]))
        assert out["grade"] in "ABCDF"
        print("MCP SMOKE PASS")
    finally:
        proc.kill()


if __name__ == "__main__":
    main()
