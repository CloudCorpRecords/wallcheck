"""Offline tests for the MCP server surface (Wave 9: audit tool added).

No network: tools/list and classify go through handle() directly, and
the audit dispatch is tested with a stubbed audit_site so the wiring
— not the network — is what's pinned. The live audit call is covered
by scripts/smoke_mcp.py against example.com.
Run: python3 -m unittest discover -s tests -v
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import wallcheck.server as server  # noqa: E402


class TestServerSurface(unittest.TestCase):
    def test_tools_list_has_four_tools(self):
        resp = server.handle({"jsonrpc": "2.0", "id": 1,
                              "method": "tools/list"})
        names = [t["name"] for t in resp["result"]["tools"]]
        self.assertEqual(names, ["probe_url", "classify", "scan_exposure",
                                 "audit"])

    def test_audit_tool_schema_requires_domain(self):
        resp = server.handle({"jsonrpc": "2.0", "id": 1,
                              "method": "tools/list"})
        audit = [t for t in resp["result"]["tools"]
                 if t["name"] == "audit"][0]
        self.assertEqual(audit["inputSchema"]["required"], ["domain"])
        self.assertIn("11", audit["description"])

    def test_classify_via_handle(self):
        resp = server.handle({"jsonrpc": "2.0", "id": 2,
                              "method": "tools/call",
                              "params": {"name": "classify",
                                         "arguments": {
                                             "status": 403,
                                             "headers": {"Server": "cloudflare"},
                                             "body": "Sorry, you have been blocked"}}})
        sc = resp["result"]["structuredContent"]
        self.assertEqual(sc["verdict"], "WALLED")
        self.assertEqual(sc["vendor"], "Cloudflare")

    def test_audit_dispatch_calls_audit_site(self):
        seen = {}

        def stub_audit_site(domain, timeout=15):
            seen["domain"] = domain
            seen["timeout"] = timeout
            return {"target": domain, "grade": "C", "score": 7,
                    "max_score": 12, "checks": [], "fixes": []}

        orig = server.audit_site
        server.audit_site = stub_audit_site
        try:
            resp = server.handle({"jsonrpc": "2.0", "id": 3,
                                  "method": "tools/call",
                                  "params": {"name": "audit",
                                             "arguments": {
                                                 "domain": "example.com"}}})
        finally:
            server.audit_site = orig
        sc = resp["result"]["structuredContent"]
        self.assertEqual(seen["domain"], "example.com")
        self.assertEqual(sc["grade"], "C")

    def test_unknown_tool_is_error(self):
        resp = server.handle({"jsonrpc": "2.0", "id": 4,
                              "method": "tools/call",
                              "params": {"name": "nope", "arguments": {}}})
        self.assertTrue(resp["result"]["isError"])


if __name__ == "__main__":
    unittest.main()
