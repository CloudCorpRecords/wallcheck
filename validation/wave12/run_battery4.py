"""Wave 12 Leg B: adversarial battery v4 probe.

Runs every HANDCLASS-4 shape through the CURRENT classifier/audit
before any fix, printing verdict vs hand expectation. A mismatch is
a defect candidate (fix generalized) or an honest limitation (ledger).
D8 shapes run against a real localhost server (gzip-compressed
sitemaps); all other shapes are offline classify/audit calls.
"""

import gzip
import os
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from wallcheck.classify import classify  # noqa: E402
from wallcheck.audit import evaluate_audit, audit_site  # noqa: E402

LOGIN = "https://site.example/login"
CF = {"cf-ray": "abc123", "server": "cloudflare"}
SITEMAP_XML = b'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://x.example/</loc></url></urlset>'


def C(status, headers=None, body="", url="https://site.example/", chain=None):
    r = classify(status, headers or {}, body, final_url=url,
                 redirect_chain=chain)
    return r["verdict"], r["vendor"]


def rec(status=200, headers=None, body="", final_url="https://x.example/"):
    return {"url": final_url, "final_url": final_url, "status": status,
            "headers": headers or {}, "body": body, "error": None,
            "redirect_chain": []}


def _check(records, name):
    out = evaluate_audit("https://x.example", records)
    return [c for c in out["checks"] if c["check"] == name][0]["status"]


def audit_robots(robots_body):
    records = {
        "robots": rec(200, {"Content-Type": "text/plain"}, robots_body),
        "llms": rec(404, {}, "not found"),
        "sitemap": rec(404, {}, "not found"),
        "homepage": rec(200, {"Content-Type": "text/html"},
                        "<html><head><title>x</title></head><body>x</body></html>"),
        "signed": rec(404, {}, "not found"),
    }
    return _check(records, "robots_txt")


def audit_llms(body, content_type):
    records = {
        "robots": rec(200, {"Content-Type": "text/plain"},
                      "User-agent: *\nAllow: /\n"),
        "llms": rec(200, {"Content-Type": content_type}, body),
        "sitemap": rec(404, {}, "not found"),
        "homepage": rec(200, {"Content-Type": "text/html"},
                        "<html><head><title>x</title></head><body>x</body></html>"),
        "signed": rec(404, {}, "not found"),
    }
    return _check(records, "llms_txt")


def make_server(mode):
    """mode 'a': /sitemap.xml gzipped. mode 'b': /sitemap.xml 404,
    robots declares /sitemap.xml.gz which serves gzipped XML."""

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
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    return srv


def audit_sitemap_live(mode):
    srv = make_server(mode)
    try:
        out = audit_site("http://127.0.0.1:%d" % srv.server_address[1])
    finally:
        srv.shutdown()
        srv.server_close()
    return [c for c in out["checks"] if c["check"] == "sitemap"][0]["status"]


ARTICLE = ("<html><body>" + "<p>An article about bot detection and "
           "browser check techniques in modern web security.</p>" * 200
           + "</body></html>")
assert len(ARTICLE) > 16384, "article must clear the served-page gate"

CASES = [
    # D1 — additional languages (all 403, small, no vendor tokens)
    ("D1a-PL", C(403, {}, "<html><body><p>Potwierdź, że nie jesteś robotem. Zaznacz pole «Nie jestem robotem».</p></body></html>"), ("CHALLENGED", "Generic")),
    ("D1b-TR", C(403, {}, "<html><body><p>Robot olmadığınızı doğrulayın. «Robot değilim» kutusunu işaretleyin.</p></body></html>"), ("CHALLENGED", "Generic")),
    ("D1c-AR", C(403, {}, "<html><body><p>أكد أنك لست روبوتًا. ضع علامة على «أنا لست روبوتًا».</p></body></html>"), ("CHALLENGED", "Generic")),
    ("D1d-ZH", C(403, {}, "<html><body><p>请确认您不是机器人。请勾选«我不是机器人»。</p></body></html>"), ("CHALLENGED", "Generic")),
    ("D1e-RU", C(403, {}, "<html><body><p>Подтвердите, что вы не робот. Отметьте «Я не робот».</p></body></html>"), ("CHALLENGED", "Generic")),
    # D2 — countdown interstitials
    ("D2a", C(200, {}, '<html><body><p>Please wait 5 seconds…</p><script>var t=5;setInterval(function(){t--;if(t<=0){}},1000)</script><meta http-equiv="refresh" content="5;url=/content/page"></body></html>'), ("OPEN", None)),
    ("D2b", C(200, {}, '<html><body><p>Please wait 10 seconds while we verify your connection</p><script>var t=10;</script><form action="/challenge/verify" method="post"><input type="hidden" name="t" value="1"></form><script>document.forms[0].submit()</script></body></html>'), ("CHALLENGED", "Generic")),
    ("D2c", C(200, {}, '<html><body><p>Please wait 5 seconds</p><script>var t=5;</script><meta http-equiv="refresh" content="5;url=/challenge/verify-human"></body></html>'), ("CHALLENGED", "Generic")),
    # D3 — browser-check wording
    ("D3a", C(200, {}, '<html><body><p>Browser check in progress…</p><div class="spinner"></div><script>setTimeout(function(){location.reload()},3000)</script></body></html>'), ("CHALLENGED", "Generic")),
    ("D3b", C(200, {}, ARTICLE), ("OPEN", None)),
    # D4 — consent hybrids
    ("D4a", C(200, {}, '<html><body><p>Accept cookies to continue.</p><p>This content is blocked until you accept cookies.</p><button>Accept all</button></body></html>'), ("OPEN", None)),
    ("D4b", C(200, {}, '<html><body><p>Accept cookies to continue.</p><p>This content is blocked until you accept cookies.</p><p>Please verify you are human.</p><button>Accept all</button></body></html>'), ("CHALLENGED", "Generic")),
    # D5 — login form actions
    ("D5a", C(200, {}, '<html><body><form action="/challenge/verify-human" method="post"><input type="password" name="pw"><div class="h-captcha"></div><button>Sign in</button></form></body></html>', url=LOGIN), ("LOGIN_GATED", None)),
    ("D5b", C(200, {}, '<html><body><form action="/challenge/verify" method="post"><button>Continue</button></form></body></html>'), ("CHALLENGED", "Generic")),
    # D6 — robots carve-outs
    ("D6a", audit_robots("User-agent: *\nDisallow: /\n\nUser-agent: GPTBot\nAllow: /\n\nUser-agent: ClaudeBot\nAllow: /\n"), "WARN"),
    ("D6b", audit_robots("User-agent: *\nDisallow: /\n\nUser-agent: GPTBot\nDisallow: /private\n\nUser-agent: ClaudeBot\nDisallow: /private\n\nUser-agent: CCBot\nDisallow: /private\n\nUser-agent: Google-Extended\nDisallow: /private\n"), "WARN"),
    ("D6c", audit_robots("User-agent: *\nDisallow: /\n\nUser-agent: GPTBot\nDisallow: /\n"), "FAIL"),
    # D7 — llms format variants
    ("D7a", audit_llms("# Example Site\n\n## Docs\n\n- [Guide](/docs/guide)\n- [API](/docs/api)\n", "text/markdown"), "PASS"),
    ("D7b", audit_llms("Example Site index\nDocs: /docs/guide\nAPI: /docs/api\n", "text/plain"), "PASS"),
    ("D7c", audit_llms('{"@context": "https://schema.org", "@type": "WebSite", "name": "Example", "url": "https://x.example/"}', "application/ld+json"), "WARN"),
    ("D7d", audit_llms("# Example Site\n\n## Docs\n\n- [Guide](/docs/guide)\n", "text/html"), "PASS"),
    # D8 — gzipped sitemaps (live localhost)
    ("D8a", audit_sitemap_live("a"), "PASS"),
    ("D8b", audit_sitemap_live("b"), "PASS"),
    # D9 — multi-redirect chains
    ("D9a", C(403, CF, "<html><body><h1>Just a moment</h1></body></html>", chain=["https://site.example/", "https://site.example/a", "https://site.example/b", "https://site.example/c/challenge"]), ("CHALLENGED", "Cloudflare")),
    ("D9b", C(200, {}, '<html><body><form><input type="password"><button>Sign in</button></form></body></html>', url=LOGIN, chain=["https://site.example/", "https://site.example/challenge", LOGIN]), ("LOGIN_GATED", None)),
    ("D9c", C(200, {}, "<html><body><article>" + "real content " * 2000 + "</article></body></html>", url="https://site.example/home", chain=["https://site.example/", "https://site.example/a", "https://site.example/b", "https://site.example/home"]), ("OPEN", None)),
    ("D9d", C(200, {}, "<html><body><article>" + "real content " * 2000 + "</article></body></html>", url="https://site.example/x", chain=["https://site.example/", "https://site.example/challenge", "https://site.example/x"]), ("OPEN", None)),
]

if __name__ == "__main__":
    bad = 0
    for cid, got, exp in CASES:
        ok = got == exp
        if not ok:
            bad += 1
        print("%s got=%r expected=%r %s" % (cid, got, exp, "OK" if ok else "MISMATCH"))
    print("battery v4: %d cases, %d mismatches" % (len(CASES), bad))
