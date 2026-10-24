"""Wave 12 adversarial battery v4 — hand-classified fixtures.

Each case pins the hand verdict from validation/wave12/HANDCLASS-4.md
BEFORE the classifier result is consulted. A failing case is a defect
candidate, fixed generalized or ledgered as an honest limitation.
"""

import gzip
import os
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from wallcheck.classify import classify  # noqa: E402
from wallcheck.audit import evaluate_audit, audit_site  # noqa: E402

LOGIN = "https://site.example/login"
CF = {"cf-ray": "abc123", "server": "cloudflare"}
SITEMAP_XML = b'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://x.example/</loc></url></urlset>'


def verdict(status, headers=None, body="", url="https://site.example/",
            chain=None):
    r = classify(status, headers or {}, body, final_url=url,
                 redirect_chain=chain)
    return r["verdict"], r["vendor"]


def rec(status=200, headers=None, body="", final_url="https://x.example/"):
    return {"url": final_url, "final_url": final_url, "status": status,
            "headers": headers or {}, "body": body, "error": None,
            "redirect_chain": []}


def audit_check(records, name):
    out = evaluate_audit("https://x.example", records)
    return [c for c in out["checks"] if c["check"] == name][0]["status"]


def robots_records(robots_body):
    return {
        "robots": rec(200, {"Content-Type": "text/plain"}, robots_body),
        "llms": rec(404, {}, "not found"),
        "sitemap": rec(404, {}, "not found"),
        "homepage": rec(200, {"Content-Type": "text/html"},
                        "<html><head><title>x</title></head><body>x</body></html>"),
        "signed": rec(404, {}, "not found"),
    }


def llms_records(body, content_type):
    return {
        "robots": rec(200, {"Content-Type": "text/plain"},
                      "User-agent: *\nAllow: /\n"),
        "llms": rec(200, {"Content-Type": content_type}, body),
        "sitemap": rec(404, {}, "not found"),
        "homepage": rec(200, {"Content-Type": "text/html"},
                        "<html><head><title>x</title></head><body>x</body></html>"),
        "signed": rec(404, {}, "not found"),
    }


def _make_server(mode):
    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def do_GET(self):
            gz = gzip.compress(SITEMAP_XML)
            if self.path == "/sitemap.xml" and mode == "a":
                self._send(200, gz, {"Content-Type": "application/xml",
                                     "Content-Encoding": "gzip"})
            elif self.path == "/robots.txt":
                body = "User-agent: *\nAllow: /\n"
                if mode == "b":
                    body += "Sitemap: /sitemap.xml.gz\n"
                self._send(200, body.encode(), {"Content-Type": "text/plain"})
            elif self.path == "/sitemap.xml.gz" and mode == "b":
                self._send(200, gz, {"Content-Type": "application/xml",
                                     "Content-Encoding": "gzip"})
            elif self.path == "/":
                self._send(200, b"<html><body>home</body></html>",
                           {"Content-Type": "text/html"})
            else:
                self._send(404, b"not found", {"Content-Type": "text/plain"})

        def _send(self, status, body, headers):
            self.send_response(status)
            for k, v in headers.items():
                self.send_header(k, v)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    srv = HTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def sitemap_live(mode):
    srv = _make_server(mode)
    try:
        out = audit_site("http://127.0.0.1:%d" % srv.server_address[1])
    finally:
        srv.shutdown()
        srv.server_close()
    return [c for c in out["checks"] if c["check"] == "sitemap"][0]["status"]


ARTICLE = ("<html><body>" + "<p>An article about bot detection and "
           "browser check techniques in modern web security.</p>" * 200
           + "</body></html>")


class TestBattery4Languages:
    def test_d1a_polish(self):
        assert verdict(403, {}, "<html><body><p>Potwierdź, że nie jesteś robotem. Zaznacz pole «Nie jestem robotem».</p></body></html>") == ("CHALLENGED", "Generic")

    def test_d1b_turkish(self):
        assert verdict(403, {}, "<html><body><p>Robot olmadığınızı doğrulayın. «Robot değilim» kutusunu işaretleyin.</p></body></html>") == ("CHALLENGED", "Generic")

    def test_d1c_arabic(self):
        assert verdict(403, {}, "<html><body><p>أكد أنك لست روبوتًا. ضع علامة على «أنا لست روبوتًا».</p></body></html>") == ("CHALLENGED", "Generic")

    def test_d1d_chinese(self):
        assert verdict(403, {}, "<html><body><p>请确认您不是机器人。请勾选«我不是机器人»。</p></body></html>") == ("CHALLENGED", "Generic")

    def test_d1e_russian(self):
        assert verdict(403, {}, "<html><body><p>Подтвердите, что вы не робот. Отметьте «Я не робот».</p></body></html>") == ("CHALLENGED", "Generic")


class TestBattery4CountdownAndCheck:
    def test_d2a_timer_to_content(self):
        assert verdict(200, {}, '<html><body><p>Please wait 5 seconds…</p><script>var t=5;</script><meta http-equiv="refresh" content="5;url=/content/page"></body></html>') == ("OPEN", None)

    def test_d2b_timer_form_to_challenge(self):
        assert verdict(200, {}, '<html><body><p>Please wait 10 seconds while we verify your connection</p><form action="/challenge/verify" method="post"></form></body></html>') == ("CHALLENGED", "Generic")

    def test_d2c_timer_refresh_to_challenge(self):
        assert verdict(200, {}, '<html><body><p>Please wait 5 seconds</p><meta http-equiv="refresh" content="5;url=/challenge/verify-human"></body></html>') == ("CHALLENGED", "Generic")

    def test_d3a_browser_check_in_progress(self):
        assert verdict(200, {}, '<html><body><p>Browser check in progress…</p><div class="spinner"></div><script>setTimeout(function(){location.reload()},3000)</script></body></html>') == ("CHALLENGED", "Generic")

    def test_d3b_article_mentioning_browser_check(self):
        assert len(ARTICLE) > 16384
        assert verdict(200, {}, ARTICLE) == ("OPEN", None)


class TestBattery4ConsentAndLogin:
    def test_d4a_consent_blocking_content(self):
        assert verdict(200, {}, '<html><body><p>Accept cookies to continue.</p><p>This content is blocked until you accept cookies.</p><button>Accept all</button></body></html>') == ("OPEN", None)

    def test_d4b_consent_plus_human_check(self):
        assert verdict(200, {}, '<html><body><p>Accept cookies to continue.</p><p>This content is blocked until you accept cookies.</p><p>Please verify you are human.</p><button>Accept all</button></body></html>') == ("CHALLENGED", "Generic")

    def test_d5a_login_form_action_to_challenge(self):
        assert verdict(200, {}, '<html><body><form action="/challenge/verify-human" method="post"><input type="password" name="pw"><div class="h-captcha"></div><button>Sign in</button></form></body></html>', url=LOGIN) == ("LOGIN_GATED", None)

    def test_d5b_stub_form_action_to_challenge(self):
        assert verdict(200, {}, '<html><body><form action="/challenge/verify" method="post"><button>Continue</button></form></body></html>') == ("CHALLENGED", "Generic")


class TestBattery4Audit:
    def test_d6a_two_carveouts(self):
        assert audit_check(robots_records("User-agent: *\nDisallow: /\n\nUser-agent: GPTBot\nAllow: /\n\nUser-agent: ClaudeBot\nAllow: /\n"), "robots_txt") == "WARN"

    def test_d6b_all_restricted(self):
        assert audit_check(robots_records("User-agent: *\nDisallow: /\n\nUser-agent: GPTBot\nDisallow: /private\n\nUser-agent: ClaudeBot\nDisallow: /private\n\nUser-agent: CCBot\nDisallow: /private\n\nUser-agent: Google-Extended\nDisallow: /private\n"), "robots_txt") == "WARN"

    def test_d6c_all_blocked(self):
        assert audit_check(robots_records("User-agent: *\nDisallow: /\n\nUser-agent: GPTBot\nDisallow: /\n"), "robots_txt") == "FAIL"

    def test_d7a_markdown_llms(self):
        assert audit_check(llms_records("# Example Site\n\n## Docs\n\n- [Guide](/docs/guide)\n", "text/markdown"), "llms_txt") == "PASS"

    def test_d7b_plaintext_llms(self):
        assert audit_check(llms_records("Example Site index\nDocs: /docs/guide\n", "text/plain"), "llms_txt") == "PASS"

    def test_d7c_jsonld_llms(self):
        assert audit_check(llms_records('{"@context": "https://schema.org", "@type": "WebSite", "name": "Example"}', "application/ld+json"), "llms_txt") == "WARN"

    def test_d7d_markdown_mislabeled_html(self):
        assert audit_check(llms_records("# Example Site\n\n## Docs\n\n- [Guide](/docs/guide)\n", "text/html"), "llms_txt") == "PASS"

    def test_d8a_gzipped_sitemap(self):
        assert sitemap_live("a") == "PASS"

    def test_d8b_gzipped_declared_sitemap(self):
        assert sitemap_live("b") == "PASS"


class TestBattery4Chains:
    def test_d9a_chain_to_wall(self):
        assert verdict(403, CF, "<html><body><h1>Just a moment</h1></body></html>", chain=["https://site.example/", "https://site.example/a", "https://site.example/b", "https://site.example/c/challenge"]) == ("CHALLENGED", "Cloudflare")

    def test_d9b_chain_to_login(self):
        assert verdict(200, {}, '<html><body><form><input type="password"><button>Sign in</button></form></body></html>', url=LOGIN, chain=["https://site.example/", "https://site.example/challenge", LOGIN]) == ("LOGIN_GATED", None)

    def test_d9c_chain_to_home(self):
        assert verdict(200, {}, "<html><body><article>" + "real content " * 2000 + "</article></body></html>", url="https://site.example/home", chain=["https://site.example/", "https://site.example/a", "https://site.example/b", "https://site.example/home"]) == ("OPEN", None)

    def test_d9d_chain_challenge_to_article(self):
        assert verdict(200, {}, "<html><body><article>" + "real content " * 2000 + "</article></body></html>", url="https://site.example/x", chain=["https://site.example/", "https://site.example/challenge", "https://site.example/x"]) == ("OPEN", None)
