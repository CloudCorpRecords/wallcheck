"""Offline tests for exposure_scan.py deep mode (roadmap Waves 2+3).

The helpers under test — asset extraction, same-origin filtering, cap
enforcement, source-map URL derivation — are pure functions over HTML.
The per-site orchestration is exercised against a stubbed fetch, so no
test touches the network.

Fixture values are synthetic and built by concatenation on purpose:
a literal shaped exactly like a real token trips GitHub push
protection (see tests/test_exposure.py).
Run: python3 -m unittest discover -s tests -v
"""

import importlib.util
import json
import os
import sys
import unittest
from unittest import mock

_HERE = os.path.dirname(__file__)
_SCRIPT = os.path.join(_HERE, "..", "scripts", "exposure_scan.py")


def _load_scanner():
    spec = importlib.util.spec_from_file_location("exposure_scan", _SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


scan = _load_scanner()

ROOT = "https://example.test/"
ORIGIN = "https://example.test"

# Synthetic values: shaped like the real classes, plainly invented.
STRIPE_SECRET = "sk_live_" + "FAKE" * 4 + "1234"
ENV_SECRET_VALUE = "FAKEENCRYPTIONKEY0123456789ABCDEF"
DB_URL = "postgres://fakeuser:fakepass99@db.example.test:5432/app"


class FakeFetch:
    """fetch(url, ...) stand-in: serves routed (status, body) pairs,
    defaults to a bare 404, and records every URL it was asked for."""

    def __init__(self, routes=None):
        self.routes = routes or {}
        self.calls = []

    def __call__(self, url, timeout=20, limit=2_000_000):
        self.calls.append(url)
        return self.routes.get(url, (404, ""))


def run_site(routes, **kw):
    fake = FakeFetch(routes)
    kw.setdefault("pause", 0)
    with mock.patch.object(scan, "fetch", fake):
        findings = scan.deep_scan_site(ROOT, **kw)
    return findings, fake.calls


class ExtractAssetsTest(unittest.TestCase):
    def test_extracts_script_and_link_js(self):
        html = """
        <script src="/static/app.js"></script>
        <script src="https://example.test/_next/static/chunks/main-abc.js"></script>
        <link rel="preload" as="script" href="/static/vendor.mjs">
        <script src="js/relative.js"></script>
        <script src="//example.test/proto-relative.js"></script>
        """
        got = scan.extract_asset_urls(html, ROOT, 8)
        self.assertEqual(got, [
            "https://example.test/static/app.js",
            "https://example.test/_next/static/chunks/main-abc.js",
            "https://example.test/static/vendor.mjs",
            "https://example.test/js/relative.js",
            "https://example.test/proto-relative.js",
        ])

    def test_rejects_cross_origin_and_non_js(self):
        html = """
        <script src="https://cdn.other.test/lib.js"></script>
        <script src="//other.test/x.js"></script>
        <link rel="stylesheet" href="/style.css">
        <link rel="icon" href="/logo.png">
        <script src="/data.json"></script>
        <script src="data:text/javascript,alert(1)"></script>
        """
        self.assertEqual(scan.extract_asset_urls(html, ROOT, 8), [])

    def test_dedupes_and_respects_cap(self):
        html = "".join(
            '<script src="/a.js"></script>' * 2
            + "".join('<script src="/%d.js"></script>' % i for i in range(5))
        )
        got = scan.extract_asset_urls(html, ROOT, 2)
        self.assertEqual(got, ["https://example.test/a.js",
                               "https://example.test/0.js"])


class MapUrlTest(unittest.TestCase):
    def test_map_derivation(self):
        self.assertEqual(scan.map_url_for("https://x.test/a/b.js"),
                         "https://x.test/a/b.js.map")
        self.assertEqual(scan.map_url_for("https://x.test/a/b.js#frag"),
                         "https://x.test/a/b.js.map")


class DeepScanSiteTest(unittest.TestCase):
    def test_bundle_candidate_reported_with_bundle_source(self):
        bundle = "https://example.test/static/app.js"
        routes = {
            ROOT: (200, '<script src="/static/app.js"></script>'),
            bundle: (200, 'var k = "%s";' % STRIPE_SECRET),
        }
        findings, _ = run_site(routes)
        cand = [f for f in findings if f["pattern"] == "stripe_secret_key"]
        self.assertEqual(len(cand), 1)
        self.assertEqual(cand[0]["class"], "CANDIDATE_EXPOSURE")
        self.assertEqual(cand[0]["source"], bundle)
        # Fingerprint-only contract holds for deep findings too.
        self.assertNotIn(STRIPE_SECRET, json.dumps(findings))

    def test_404_shell_still_scanned(self):
        login = ORIGIN + "/login"
        shell = ('{"NEXT_PUBLIC_APP_ENCRYPTION_KEY":"%s"}'
                 % ENV_SECRET_VALUE)
        routes = {ROOT: (200, "<html>ok</html>"), login: (404, shell)}
        findings, _ = run_site(routes)
        cand = [f for f in findings
                if f["pattern"] == "public_env_sensitive_name"]
        self.assertEqual(len(cand), 1)
        self.assertEqual(cand[0]["source"], login)

    def test_map_scanned_with_map_source(self):
        bundle = "https://example.test/static/app.js"
        map_url = bundle + ".map"
        map_body = json.dumps({
            "version": 3,
            "sources": ["../src/config.ts"],
            "sourcesContent": ["const db = '%s';" % DB_URL],
        })
        routes = {
            ROOT: (200, '<script src="/static/app.js"></script>'),
            bundle: (200, "console.log('clean');"),
            map_url: (200, map_body),
        }
        findings, calls = run_site(routes)
        cand = [f for f in findings if f["pattern"] == "db_url_with_password"]
        self.assertEqual(len(cand), 1)
        self.assertEqual(cand[0]["source"], map_url)
        self.assertIn(map_url, calls)

    def test_absent_map_is_silent(self):
        bundle = "https://example.test/static/app.js"
        routes = {
            ROOT: (200, '<script src="/static/app.js"></script>'),
            bundle: (200, "console.log('clean');"),
            # .map deliberately unrouted -> FakeFetch's bare 404.
        }
        findings, calls = run_site(routes)
        self.assertEqual(findings, [])
        self.assertIn(bundle + ".map", calls)

    def test_cross_origin_asset_never_fetched(self):
        html = ('<script src="https://cdn.other.test/lib.js"></script>'
                '<script src="/local.js"></script>')
        routes = {ROOT: (200, html)}
        _, calls = run_site(routes)
        self.assertFalse(any("other.test" in u for u in calls))
        self.assertIn("https://example.test/local.js", calls)

    def test_fetch_budget_worst_case(self):
        html = "".join('<script src="/%d.js"></script>' % i
                       for i in range(10))
        routes = {ROOT: (200, html)}
        _, calls = run_site(routes, max_assets=3, max_paths=2)
        # 1 root + 3 assets + 3 maps + 2 app-shell paths, each once.
        self.assertEqual(len(calls), 9)
        self.assertEqual(len(calls), len(set(calls)))


if __name__ == "__main__":
    unittest.main()
