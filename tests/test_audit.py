"""Offline fixture tests for the owner-side audit (v0.3).

The evaluation core is a pure function of captured fetch records, so
fixture sites exercise it completely with no network. One test drives
audit_site itself through a fake fetcher to pin the URL routing.
Run: python3 -m unittest discover -s tests -v
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from wallcheck.audit import audit_site, evaluate_audit  # noqa: E402

CF_BLOCK_BODY = """<!DOCTYPE html><html><head><title>Attention Required! | Cloudflare</title></head>
<body><h1>Sorry, you have been blocked</h1>
<p>You are unable to access walled.example</p></body></html>"""

CF_HEADERS = {"Server": "cloudflare", "CF-Ray": "8abc124-IAD"}

ROBOTS_OPEN = """User-agent: *
Allow: /

Sitemap: https://open.example/sitemap.xml
"""

ROBOTS_BLOCKING = """User-agent: GPTBot
Disallow: /

User-agent: *
Allow: /
"""

LLMS_REAL = "# Open Example\n\n> A site that wants agents to read it.\n\n" \
            "## Docs\n\n- [Guide](https://open.example/guide)\n"

SITEMAP_XML = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
<url><loc>https://open.example/</loc></url>
</urlset>"""

HOMEPAGE_WITH_FEED = """<!DOCTYPE html><html><head><title>Open Example</title>
<link rel="alternate" type="application/rss+xml" title="RSS" href="/feed.xml">
</head><body><h1>Open Example</h1></body></html>"""

HOMEPAGE_NO_FEED = """<!DOCTYPE html><html><head><title>Plain</title></head>
<body><h1>Plain site</h1></body></html>"""

OPENAPI_DOC = '{"openapi": "3.1.0", "info": {"title": "Open API", ' \
              '"version": "1"}, "paths": {}}'

JWKS_DIRECTORY = '{"keys": [{"kty": "OKP", "crv": "Ed25519", ' \
                 '"kid": "agent-1", "x": "abc"}]}'

SECURITY_TXT = "Contact: mailto:security@open.example\n" \
               "Expires: 2027-01-01T00:00:00.000Z\n" \
               "Preferred-Languages: en\n"

SOFT_404_LLMS = """<!DOCTYPE html><html><head><title>Page not found</title></head>
<body><h1>404 — this page does not exist</h1>
<p>Return to the homepage.</p></body></html>"""


def rec(status=200, headers=None, body="", error=None,
        final_url="https://x.example/"):
    return {"url": final_url, "final_url": final_url, "status": status,
            "headers": headers or {}, "body": body, "error": error,
            "redirect_chain": []}


def open_records():
    return {
        "robots": rec(200, {"Content-Type": "text/plain"}, ROBOTS_OPEN),
        "llms": rec(200, {"Content-Type": "text/plain"}, LLMS_REAL),
        "sitemap": rec(200, {"Content-Type": "application/xml"}, SITEMAP_XML),
        "homepage": rec(200, {"Content-Type": "text/html"},
                        HOMEPAGE_WITH_FEED),
        "openapi": rec(200, {"Content-Type": "application/json"}, OPENAPI_DOC),
        "openapi_wellknown": rec(404, {}, "not found"),
        "signed": rec(200, {"Content-Type": "application/json"},
                      JWKS_DIRECTORY),
        "security": rec(200, {"Content-Type": "text/plain"}, SECURITY_TXT),
    }


def walled_records():
    w = lambda: rec(403, CF_HEADERS, CF_BLOCK_BODY)  # noqa: E731
    return {"robots": w(), "llms": w(), "sitemap": w(), "homepage": w(),
            "openapi": w(), "openapi_wellknown": w(), "api_root": w(),
            "api_docs": w(), "signed": w(), "security": w()}


def by_check(result):
    return {c["check"]: c for c in result["checks"]}


class TestAuditFixtures(unittest.TestCase):
    def test_fully_open_site(self):
        r = evaluate_audit("https://open.example", open_records())
        checks = by_check(r)
        for name, c in checks.items():
            self.assertEqual(c["status"], "PASS", "%s: %s" % (name, c))
        self.assertEqual(r["grade"], "A")
        self.assertEqual(r["score"], r["max_score"])
        self.assertEqual(r["fixes"], [])

    def test_fully_walled_site(self):
        r = evaluate_audit("https://walled.example", walled_records())
        checks = by_check(r)
        for name, c in checks.items():
            self.assertEqual(c["status"], "FAIL", "%s: %s" % (name, c))
        self.assertEqual(r["grade"], "F")
        self.assertEqual(len(r["fixes"]), 7)
        self.assertIn("WALLED", checks["robots_txt"]["evidence"][0])

    def test_soft_404_llms_trap(self):
        records = open_records()
        records["llms"] = rec(200, {"Content-Type": "text/html"},
                              SOFT_404_LLMS)
        r = evaluate_audit("https://open.example", records)
        checks = by_check(r)
        self.assertEqual(checks["llms_txt"]["status"], "FAIL")
        self.assertIn("SOFT_404_HTML", checks["llms_txt"]["evidence"])
        # Everything else still passes; one fake file costs the grade.
        self.assertEqual(checks["robots_txt"]["status"], "PASS")
        self.assertEqual(r["grade"], "B")

    def test_robots_blocks_one_named_agent(self):
        records = open_records()
        records["robots"] = rec(200, {"Content-Type": "text/plain"},
                                ROBOTS_BLOCKING)
        r = evaluate_audit("https://open.example", records)
        c = by_check(r)["robots_txt"]
        self.assertEqual(c["status"], "WARN")
        self.assertIn("AI_BLOCKED: GPTBot", c["evidence"])
        self.assertNotIn("AI_BLOCKED: ClaudeBot", c["evidence"])

    def test_absent_llms_is_warn_not_fail(self):
        records = open_records()
        records["llms"] = rec(404, {"Content-Type": "text/html"},
                              "<html><body>not found</body></html>")
        r = evaluate_audit("https://open.example", records)
        self.assertEqual(by_check(r)["llms_txt"]["status"], "WARN")

    def test_no_feed_link_is_warn(self):
        records = open_records()
        records["homepage"] = rec(200, {"Content-Type": "text/html"},
                                   HOMEPAGE_NO_FEED)
        r = evaluate_audit("https://open.example", records)
        self.assertEqual(by_check(r)["feed"]["status"], "WARN")

    def test_signed_directory_absent_is_fail_with_data_note(self):
        records = open_records()
        records["signed"] = rec(404, {}, "not found")
        r = evaluate_audit("https://open.example", records)
        c = by_check(r)["signed_agents"]
        self.assertEqual(c["status"], "FAIL")
        self.assertIn("STATUS_404", c["evidence"])


class TestSecurityContact(unittest.TestCase):
    def check(self, record):
        records = open_records()
        if record is None:
            records.pop("security")
        else:
            records["security"] = record
        r = evaluate_audit("https://open.example", records)
        return by_check(r)["security_contact"], r

    def test_security_txt_with_contact_passes(self):
        c, r = self.check(rec(200, {"Content-Type": "text/plain"},
                              SECURITY_TXT))
        self.assertEqual(c["status"], "PASS")
        self.assertIn("CONTACT_PRESENT", c["evidence"])
        self.assertEqual(r["max_score"], 14)

    def test_security_txt_absent_is_warn_not_fail(self):
        c, _ = self.check(rec(404, {}, "not found"))
        self.assertEqual(c["status"], "WARN")
        self.assertIn("STATUS_404", c["evidence"])

    def test_security_txt_without_contact_is_warn(self):
        c, _ = self.check(rec(200, {"Content-Type": "text/plain"},
                              "Expires: 2027-01-01T00:00:00.000Z\n"))
        self.assertEqual(c["status"], "WARN")
        self.assertIn("NO_CONTACT_FIELD", c["evidence"])

    def test_security_txt_soft_404_html_fails(self):
        c, _ = self.check(rec(200, {"Content-Type": "text/html"},
                              SOFT_404_LLMS))
        self.assertEqual(c["status"], "FAIL")
        self.assertIn("SOFT_404_HTML", c["evidence"])

    def test_security_txt_walled_fails(self):
        c, _ = self.check(rec(403, CF_HEADERS, CF_BLOCK_BODY))
        self.assertEqual(c["status"], "FAIL")
        self.assertIn("WALLED", c["evidence"][0])

    def test_security_txt_missing_record_is_warn(self):
        c, _ = self.check(None)
        self.assertEqual(c["status"], "WARN")


class TestAuditSiteRouting(unittest.TestCase):
    def test_audit_site_with_fake_fetcher(self):
        pages = {
            "/": rec(200, {"Content-Type": "text/html"},
                     HOMEPAGE_WITH_FEED),
            "/robots.txt": rec(200, {"Content-Type": "text/plain"},
                               ROBOTS_OPEN),
            "/llms.txt": rec(200, {"Content-Type": "text/plain"}, LLMS_REAL),
            "/sitemap.xml": rec(200, {"Content-Type": "application/xml"},
                                SITEMAP_XML),
            "/openapi.json": rec(200, {"Content-Type": "application/json"},
                                 OPENAPI_DOC),
            "/.well-known/http-message-signatures-directory":
                rec(200, {"Content-Type": "application/json"},
                    JWKS_DIRECTORY),
        }

        def fake_fetch(url, timeout=15):
            for path, record in pages.items():
                if url.endswith(path):
                    return dict(record, url=url, final_url=url)
            return rec(404, {}, "not found", final_url=url)

        r = audit_site("https://open.example", fetch=fake_fetch)
        self.assertEqual(r["grade"], "A")
        self.assertEqual(by_check(r)["api"]["status"], "PASS")

    def test_soft404_openapi_does_not_suppress_api_fallback(self):
        # An SPA shell served at /openapi.json (200, HTML) is not a
        # spec — audit_site must still probe /api before failing
        # the api check. (Found live on clipwise.replit.app.)
        spa = "<!DOCTYPE html><html><head><title>App</title></head>" \
              "<body><div id=\"root\"></div></body></html>"
        pages = {
            "/": rec(200, {"Content-Type": "text/html"}, HOMEPAGE_WITH_FEED),
            "/robots.txt": rec(200, {"Content-Type": "text/plain"},
                               ROBOTS_OPEN),
            "/llms.txt": rec(200, {"Content-Type": "text/plain"}, LLMS_REAL),
            "/sitemap.xml": rec(200, {"Content-Type": "application/xml"},
                                SITEMAP_XML),
            "/openapi.json": rec(200, {"Content-Type": "text/html"}, spa),
            "/.well-known/openapi.json":
                rec(200, {"Content-Type": "text/html"}, spa),
            "/api": rec(200, {"Content-Type": "application/json"},
                        '{"name": "app-api", "version": "1"}'),
            "/.well-known/http-message-signatures-directory":
                rec(200, {"Content-Type": "application/json"},
                    JWKS_DIRECTORY),
        }

        def fake_fetch(url, timeout=15):
            for path, record in pages.items():
                if url.endswith(path):
                    return dict(record, url=url, final_url=url)
            return rec(404, {}, "not found", final_url=url)

        r = audit_site("https://spa.example", fetch=fake_fetch)
        c = by_check(r)["api"]
        self.assertEqual(c["status"], "PASS")
        self.assertIn("API_ROOT_200", c["evidence"])

    def test_audit_site_fetch_budget(self):
        # Wave 9 (MCP audit tool): an audit call must stay bounded.
        # All-404 site: homepage, robots, llms, sitemap, two OpenAPI
        # paths, /api + /developers fallbacks, signed directory,
        # security.txt = 10 fetches. The hard cap is 11
        # (declared-sitemap alt fetch).
        calls = []

        def counting_fetch(url, timeout=15):
            calls.append(url)
            return {"url": url, "final_url": url, "status": 404,
                    "headers": {}, "body": "not found", "error": None,
                    "redirect_chain": []}

        r = audit_site("https://all404.example", fetch=counting_fetch)
        self.assertLessEqual(len(calls), 11)
        self.assertEqual(len(calls), 10)
        self.assertEqual(len(r["checks"]), 7)
        self.assertIn(r["grade"], ("A", "B", "C", "D", "F", "UNREACHABLE"))


if __name__ == "__main__":
    unittest.main()
