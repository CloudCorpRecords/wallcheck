"""Wave 13 Leg B: adversarial battery v5 runner.

Runs the CURRENT classifier/audit against the hand-classified
shapes in HANDCLASS-5.md and reports every mismatch. No fixes
are applied by this script; it is the measurement step.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from wallcheck.classify import classify  # noqa: E402
from wallcheck.audit import evaluate_audit  # noqa: E402

LOGIN = "https://site.example/login"


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


def llms_records(body, content_type="text/plain"):
    return {
        "robots": rec(200, {"Content-Type": "text/plain"},
                      "User-agent: *\nAllow: /\n"),
        "llms": rec(200, {"Content-Type": content_type}, body),
        "sitemap": rec(404, {}, "not found"),
        "homepage": rec(200, {"Content-Type": "text/html"},
                        "<html><head><title>x</title></head><body>x</body></html>"),
        "signed": rec(404, {}, "not found"),
    }


def sitemap_records(body):
    return {
        "robots": rec(200, {"Content-Type": "text/plain"},
                      "User-agent: *\nAllow: /\n"),
        "llms": rec(404, {}, "not found"),
        "sitemap": rec(200, {"Content-Type": "application/xml"}, body),
        "homepage": rec(200, {"Content-Type": "text/html"},
                        "<html><head><title>x</title></head><body>x</body></html>"),
        "signed": rec(404, {}, "not found"),
    }


ARTICLE = ("<html><body>" + "<p>An article about verification and "
           "bot detection in modern web security.</p>" * 300
           + "</body></html>")
assert len(ARTICLE) > 16384, "E3b article must clear the served-page gate"
SHORT_ARTICLE = ("<html><body><p>A short post about how the team "
                 "ships software on Fridays.</p></body></html>")
LOGIN_FORM = ('<html><body><form action="/session" method="post">'
              '<input type="password" name="pw">'
              '<div class="cf-turnstile"></div>'
              '<script src="https://challenges.cloudflare.com/turnstile/v0/api.js"></script>'
              '<button>Sign in</button></form></body></html>')

CASES = [
    # (id, expected, actual)
    ("E1a", ("CHALLENGED", "Generic"),
     verdict(403, {}, '<html><body><img src="/captcha/image.png" alt=""></body></html>')),
    ("E1b", ("WALLED", None),
     verdict(403, {}, '<html><body><img src="/img/a7f3.png" alt=""></body></html>')),
    ("E1c", ("CHALLENGED", "Generic"),
     verdict(403, {}, '<html><body><img src="/img/a7f3.png" title="Please verify you are human"></body></html>')),
    ("E2a", ("CHALLENGED", "Generic"),
     verdict(200, {}, '<html><body><noscript><p>This site requires JavaScript. Please enable JavaScript to continue.</p></noscript></body></html>')),
    ("E2b", ("OPEN", None),
     verdict(200, {}, '<html><body><noscript><p>This site requires JavaScript to run. Please enable JavaScript to run this app.</p></noscript></body></html>')),
    ("E2c", ("CHALLENGED", "Generic"),
     verdict(200, {}, '<html><body><noscript><p>Please enable JavaScript and verify you are human to continue.</p></noscript></body></html>')),
    ("E3a", ("CHALLENGED", "Generic"),
     verdict(200, {}, '<html><head><title>Verify you are human</title></head><body><div class="spinner"></div></body></html>')),
    ("E3b", ("OPEN", None),
     verdict(200, {}, "<html><head><title>Verify you are human: how sites check visitors</title></head><body>" + ARTICLE + "</body></html>")),
    ("E4a", ("OPEN", None),
     verdict(200, {"set-cookie": "_pxvid=abc123; Path=/"}, ARTICLE)),
    ("E4b", ("CHALLENGED", "Generic"),
     verdict(200, {"set-cookie": "_pxvid=abc123; Path=/"}, '<html><body><p>Please wait while we check your browser</p></body></html>')),
    ("E5a", "FAIL",
     audit_check(robots_records("User-agent: *\nDisallow: /\n"), "robots_txt")),
    ("E5b", "WARN",
     audit_check(robots_records("User-agent: GPTBot\nDisallow: /\n"), "robots_txt")),
    ("E5c", "FAIL",
     audit_check(robots_records("User-agent: GPTBot\nDisallow: /\n\nUser-agent: ClaudeBot\nDisallow: /\n\nUser-agent: CCBot\nDisallow: /\n\nUser-agent: Google-Extended\nDisallow: /\n"), "robots_txt")),
    ("E6a", "WARN",
     audit_check(llms_records("# Welcome to Example Corporation\n"), "llms_txt")),
    ("E6b", "PASS",
     audit_check(llms_records("# My Site\n\n- [Docs](/docs)\n"), "llms_txt")),
    ("E7a", "PASS",
     audit_check(sitemap_records('<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://x.example/</loc></url></urlset>'), "sitemap")),
    ("E7b", "PASS",
     audit_check(sitemap_records('<?xml version="1.0"?><sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><sitemap><loc>https://x.example/sitemap1.xml</loc></sitemap></sitemapindex>'), "sitemap")),
    ("E8a", ("LOGIN_GATED", None),
     verdict(200, {}, '<html><body><form><input type="password"><button>Sign in</button></form></body></html>', url=LOGIN, chain=["https://site.example/", "https://site.example/a", "https://site.example/b", "https://site.example/c", LOGIN])),
    ("E8b", ("LOGIN_GATED", "Cloudflare"),
     verdict(200, {}, LOGIN_FORM, url=LOGIN, chain=["https://site.example/", "https://site.example/challenge", LOGIN])),
    ("E8c", ("CHALLENGED", "Cloudflare"),
     verdict(403, {"cf-ray": "abc123", "cf-mitigated": "challenge"}, "<html><body><h1>Just a moment</h1></body></html>", url=LOGIN, chain=["https://site.example/", "https://site.example/a", LOGIN])),
    ("E9a", ("OPEN", None),
     verdict(200, {}, '<html><body>' + SHORT_ARTICLE + '<!-- Cloudflare Ray ID: abc123 — Just a moment --></body></html>')),
    ("E9b", ("WALLED", None),
     verdict(403, {}, '<html><body><p>Access denied</p><!-- PerimeterX px-captcha reference --></body></html>')),
    ("E10a", ("CHALLENGED", "Cloudflare"),
     verdict(403, {"cf-ray": "abc123"}, "<html><body><h1>JUST A MOMENT</h1></body></html>")),
    ("E10b", ("WALLED", "PerimeterX"),
     verdict(403, {}, "<html><body><p>PERIMETERX</p><p>Please verify you are NOT A ROBOT</p></body></html>")),
    ("E10c", ("CHALLENGED", "DataDome"),
     verdict(403, {}, "<html><body><p>DaTaDoMe</p><p>Access denied</p></body></html>")),
]


def main():
    mismatches = 0
    for cid, expected, actual in CASES:
        ok = expected == actual
        if not ok:
            mismatches += 1
        print("%s expected=%s actual=%s %s" % (cid, expected, actual, "OK" if ok else "MISMATCH"))
    print("total=%d mismatches=%d" % (len(CASES), mismatches))


if __name__ == "__main__":
    main()
