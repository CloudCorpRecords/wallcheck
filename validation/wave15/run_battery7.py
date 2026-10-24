"""Wave 15 Leg B: adversarial battery v7 runner.

Runs the CURRENT classifier/audit against the hand-classified shapes in
HANDCLASS-7.md and reports every mismatch. No fixes are applied by this
script; it is the measurement step. (Audit shapes use evaluate_audit
directly, like Waves 11-14; audit_site-level fetch shapes are not in
this battery.)
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
assert len(ARTICLE) > 16384, "article must clear the served-page gate"
SHORT_ARTICLE = ("<html><body><p>Our team ships every Friday and "
                 "writes about the process in detail here.</p></body></html>")
LOGIN_2FA = ('<html><body><form action="/verify" method="post">'
             '<label>Enter your 6-digit verification code</label>'
             '<input type="text" name="otp" maxlength="6">'
             '<button>Verify</button></form></body></html>')

CASES = [
    # G1 — JSON-LD blocks
    ("G1a", ("OPEN", None),
     verdict(200, {}, '<html><body><p>Our team ships every Friday and writes about the process in detail here.</p><script type="application/ld+json">{"@type": "Article", "description": "Verify you are human to access this article"}</script></body></html>')),
    ("G1b", ("CHALLENGED", "Generic"),
     verdict(200, {}, '<html><body><script type="application/ld+json">{"@type": "WebPage", "text": "Verify you are human to continue"}</script></body></html>')),
    ("G1c", ("OPEN", None),
     verdict(200, {}, '<html><body><p>Our team ships every Friday and writes about the process in detail here.</p><script type="application/ld+json">{"@type": "Article", "description": "An analysis of perimeterx and modern bot detection"}</script></body></html>')),
    ("G1d", ("CHALLENGED", "PerimeterX"),
     verdict(200, {}, '<html><body><script type="application/ld+json">{"@type": "WebPage", "description": "perimeterx"}</script></body></html>')),
    # G2 — access-denied variants
    ("G2a", ("WALLED", None),
     verdict(200, {}, "<html><body><p>Access denied.</p></body></html>")),
    ("G2b", ("WALLED", None),
     verdict(403, {}, "<html><body><p>Access denied.</p></body></html>")),
    ("G2c", ("LOGIN_GATED", None),
     verdict(401, {}, "<html><body><p>Access denied.</p></body></html>")),
    ("G2d", ("OPEN", None),
     verdict(200, {}, "<html><head><title>On permission errors</title></head><body>" + ARTICLE.replace("verification and bot detection", "access denied errors and permission models") + "</body></html>")),
    ("G2e", ("UNREACHABLE", None),
     verdict(503, {}, "<html><body><p>Access denied.</p></body></html>")),
    # G3 — SVG text
    ("G3a", ("CHALLENGED", "Generic"),
     verdict(403, {}, '<html><body><svg><text>Verify you are human</text></svg></body></html>')),
    ("G3b", ("CHALLENGED", "Generic"),
     verdict(403, {}, '<html><body><svg><text><tspan>Verify you</tspan><tspan> are human</tspan></text></svg></body></html>')),
    ("G3c", ("OPEN", None),
     verdict(200, {}, "<html><body>" + ARTICLE + '<svg><text>verify you are human</text></svg></body></html>')),
    # G4 — hCaptcha enterprise
    ("G4a", ("CHALLENGED", "Generic"),
     verdict(403, {}, '<html><body><div class="h-captcha" data-sitekey="abc"></div><script src="https://js.hcaptcha.com/1/api.js?render=explicit"></script></body></html>')),
    ("G4b", ("LOGIN_GATED", None),
     verdict(200, {}, '<html><body><form action="/session" method="post"><input type="password" name="pw"><div class="h-captcha" data-sitekey="abc"></div><button>Sign in</button></form></body></html>', url=LOGIN)),
    ("G4c", ("OPEN", None),
     verdict(200, {}, '<html><body><p>Our team ships every Friday and writes about the process in detail here.</p><div class="h-captcha" data-sitekey="abc" data-size="invisible"></div></body></html>')),
    ("G4d", ("CHALLENGED", "Generic"),
     verdict(403, {}, '<html><body><div class="h-captcha" data-sitekey="abc" data-size="invisible"></div></body></html>')),
    # G5 — Refresh header
    ("G5a", ("CHALLENGED", "Generic"),
     verdict(200, {"Refresh": "0; url=/challenge/verify"}, "<html><body></body></html>")),
    ("G5b", ("LOGIN_GATED", None),
     verdict(200, {"Refresh": "0; url=/login"}, "<html><body></body></html>")),
    ("G5c", ("OPEN", None),
     verdict(200, {"Refresh": "0; url=/home"}, "<html><body></body></html>")),
    ("G5d", ("OPEN", None),
     verdict(200, {"Refresh": "0; url=/challenge/verify"}, ARTICLE)),
    # G6 — 2FA first screens
    ("G6a", ("LOGIN_GATED", None),
     verdict(200, {}, LOGIN_2FA, url=LOGIN)),
    ("G6b", ("LOGIN_GATED", None),
     verdict(200, {}, '<html><body><p>Please verify you are human, then enter your code.</p>' + LOGIN_2FA + '</body></html>', url=LOGIN)),
    ("G6c", ("LOGIN_GATED", None),
     verdict(200, {}, LOGIN_2FA, url="https://site.example/verify-2fa")),
    ("G6d", ("CHALLENGED", "Cloudflare"),
     verdict(403, {"cf-ray": "abc123", "cf-mitigated": "challenge"}, "<html><body><h1>Just a moment</h1>" + LOGIN_2FA + "</body></html>", url=LOGIN)),
    # G7 — article + footer badge
    ("G7a", ("OPEN", None),
     verdict(200, {}, ARTICLE + "<footer>This site is protected by PerimeterX</footer></html>")),
    ("G7b", ("OPEN", None),
     verdict(200, {}, SHORT_ARTICLE + "<footer>This site is protected by PerimeterX</footer></html>")),
    ("G7c", ("OPEN", None),
     verdict(200, {}, "<html><body><footer>Protected by DataDome</footer></body></html>")),
    # G8 — robots Allow-all carve-outs
    ("G8a", "WARN",
     audit_check(robots_records("User-agent: *\nAllow: /\nDisallow: /private\n"), "robots_txt")),
    ("G8b", "PASS",
     audit_check(robots_records("User-agent: *\nAllow: /\n"), "robots_txt")),
    ("G8c", "WARN",
     audit_check(robots_records("User-agent: *\nDisallow: /private\n\nUser-agent: GPTBot\nAllow: /\n"), "robots_txt")),
    ("G8d", "PASS",
     audit_check(robots_records("User-agent: *\nDisallow: /\nAllow: /\n"), "robots_txt")),
    # G9 — llms frontmatter
    ("G9a", "PASS",
     audit_check(llms_records("---\ntitle: Example Site\ndate: 2026-01-01\n---\n\n# Docs\n\n- [Guide](/guide)\n- [API](/api)\n"), "llms_txt")),
    ("G9b", "WARN",
     audit_check(llms_records("---\ntitle: Example Site\nurl: https://x.example\n---\n"), "llms_txt")),
    ("G9c", "PASS",
     audit_check(llms_records("---\ntitle: Example Site\n---\n\n- [Docs](/docs)\n"), "llms_txt")),
    ("G9d", "WARN",
     audit_check(llms_records("---\ntitle: Example Site\ndescription: See [the guide](/guide) for details.\n---\n"), "llms_txt")),
    # G10 — lastmod-only sitemaps
    ("G10a", "WARN",
     audit_check(sitemap_records('<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><lastmod>2026-01-01</lastmod></url><url><lastmod>2026-01-02</lastmod></url></urlset>'), "sitemap")),
    ("G10b", "PASS",
     audit_check(sitemap_records('<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://x.example/</loc><lastmod>2026-01-01</lastmod></url></urlset>'), "sitemap")),
    ("G10c", "WARN",
     audit_check(sitemap_records('<?xml version="1.0"?><sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><sitemap><lastmod>2026-01-01</lastmod></sitemap></sitemapindex>'), "sitemap")),
    ("G10d", "PASS",
     audit_check(sitemap_records('<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://x.example/</loc></url><url><lastmod>2026-01-01</lastmod></url></urlset>'), "sitemap")),
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
