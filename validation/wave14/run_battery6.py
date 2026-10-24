"""Wave 14 Leg B: adversarial battery v6 runner.

Runs the CURRENT classifier/audit against the hand-classified
shapes in HANDCLASS-6.md and reports every mismatch. No fixes
are applied by this script; it is the measurement step.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from wallcheck.classify import classify  # noqa: E402
from wallcheck.audit import audit_site, evaluate_audit  # noqa: E402

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


def sitemap_site_records(robots_body, url_map):
    """Run audit_site with a fake fetch: url_map maps URL -> record.
    Unmapped URLs answer 404. Returns the sitemap check status."""
    def fake_fetch(url, timeout=15):
        if url in url_map:
            return url_map[url]
        return rec(404, {}, "not found", final_url=url)

    out = audit_site("https://x.example", fetch=fake_fetch)
    # audit_site also fetches homepage/robots/llms/openapi/api/signed;
    # the fake fetch must cover robots + sitemap candidates. Homepage
    # and llms records come from url_map too.
    return [c for c in out["checks"] if c["check"] == "sitemap"][0]["status"]


def sitemap_case(robots_body, sitemap_rec, extra):
    url_map = {
        "https://x.example/": rec(200, {"Content-Type": "text/html"},
                                  "<html><head><title>x</title></head><body>x</body></html>"),
        "https://x.example/robots.txt": rec(200, {"Content-Type": "text/plain"}, robots_body),
        "https://x.example/llms.txt": rec(404, {}, "not found"),
        "https://x.example/sitemap.xml": sitemap_rec,
        "https://x.example/.well-known/http-message-signatures-directory": rec(404, {}, "not found"),
    }
    url_map.update(extra)
    return sitemap_site_records(robots_body, url_map)


ARTICLE = ("<html><body>" + "<p>An article about verification and "
           "bot detection in modern web security.</p>" * 300
           + "</body></html>")
assert len(ARTICLE) > 16384, "article must clear the served-page gate"
PARA = ("<html><body><p>Our team ships every Friday and writes "
        "about the process in detail for our readers.</p></body></html>")
LOGIN_FORM = ('<html><body><form action="/session" method="post">'
              '<input type="password" name="pw">'
              '<button>Sign in</button></form></body></html>')

URLSET = ('<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
          '<url><loc>https://x.example/</loc></url></urlset>')
SITEMAPINDEX = ('<?xml version="1.0"?><sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                '<sitemap><loc>https://x.example/sitemap1.xml</loc></sitemap></sitemapindex>')

CASES = [
    # F1 — script JSON blobs
    ("F1a", ("CHALLENGED", "Generic"),
     verdict(200, {}, '<html><body><script type="application/json">{"wall":{"type":"captcha","action":"verify"}}</script></body></html>')),
    ("F1b", ("OPEN", None),
     verdict(200, {}, PARA.replace("</body>",
        '<script type="application/json">{"form":{"captcha":true,"sitekey":"abc"}}</script></body>'))),
    ("F1c", ("OPEN", None),
     verdict(200, {}, "<html><body>" + ARTICLE +
        '<script type="application/json">{"form":{"captcha":true}}</script></body></html>')),
    ("F1d", ("CHALLENGED", "Generic"),
     verdict(200, {}, '<html><body><div class="spinner"></div><script type="application/json">{"form":{"captcha":true}}</script></body></html>')),
    # F2 — alt attributes
    ("F2a", ("CHALLENGED", "Generic"),
     verdict(403, {}, '<html><body><img src="/img/x.png" alt="Please verify you are human"></body></html>')),
    ("F2b", ("WALLED", None),
     verdict(403, {}, '<html><body><img src="/img/x.png" alt="Access denied"></body></html>')),
    ("F2c", ("OPEN", None),
     verdict(200, {}, "<html><body>" + ARTICLE +
        '<img src="/img/x.png" alt="verify you are human"></body></html>')),
    # F3 — unusual traffic / suspicious activity
    ("F3a", ("WALLED", None),
     verdict(403, {}, '<html><body><p>Access denied: unusual traffic detected from your network.</p></body></html>')),
    ("F3b", ("CHALLENGED", "Generic"),
     verdict(200, {}, '<html><body><p>Unusual traffic detected. Complete verification to continue.</p></body></html>')),
    ("F3c", ("OPEN", None),
     verdict(200, {}, "<html><body>" + ARTICLE +
        "<p>Unusual traffic detection and verification systems.</p></body></html>")),
    ("F3d", ("WALLED", None),
     verdict(403, {}, '<html><body><p>Suspicious activity detected. Your account has been suspended.</p></body></html>')),
    # F4 — Retry-After throttles
    ("F4a", ("RATE_LIMITED", None),
     verdict(429, {"retry-after": "60"}, '<html><body><p>Too many requests. Try again later.</p></body></html>')),
    ("F4b", ("CHALLENGED", "Generic"),
     verdict(429, {"retry-after": "60"}, '<html><body><p>Too many requests. Please verify you are human to continue.</p></body></html>')),
    ("F4c", ("RATE_LIMITED", None),
     verdict(403, {"retry-after": "120"}, '<html><body><p>Too many requests from your IP. Please retry after 120 seconds.</p></body></html>')),
    ("F4d", ("RATE_LIMITED", None),
     verdict(503, {"retry-after": "60"}, '<html><body><p>Too many requests, please retry in 60 seconds.</p></body></html>')),
    ("F4e", ("UNREACHABLE", None),
     verdict(503, {"retry-after": "60"}, '<html><body><p>Service temporarily unavailable.</p></body></html>')),
    ("F4f", ("WALLED", None),
     verdict(403, {"retry-after": "120"}, '<html><body><p>Access denied.</p></body></html>')),
    # F5 — login + session-challenge cookies
    ("F5a", ("LOGIN_GATED", None),
     verdict(200, {"set-cookie": "challenge_token=abc; Path=/"}, LOGIN_FORM, url=LOGIN)),
    ("F5b", ("LOGIN_GATED", None),
     verdict(200, {"set-cookie": "_pxvid=abc123; Path=/"}, LOGIN_FORM, url=LOGIN)),
    ("F5c", ("LOGIN_GATED", "DataDome"),
     verdict(200, {"set-cookie": "dd_cookie=abc; Path=/"}, LOGIN_FORM, url=LOGIN)),
    ("F5d", ("LOGIN_GATED", "Imperva"),
     verdict(200, {"set-cookie": "incap_ses=abc; Path=/"}, LOGIN_FORM, url=LOGIN)),
    # F6 — robots-declared sitemap indexes (audit_site level)
    ("F6a", "PASS",
     sitemap_case("User-agent: *\nAllow: /\nSitemap: https://x.example/sitemap-index.xml\n",
                  rec(200, {"Content-Type": "text/html"}, "<html><body>Not found</body></html>"),
                  {"https://x.example/sitemap-index.xml":
                   rec(200, {"Content-Type": "application/xml"}, SITEMAPINDEX)})),
    ("F6b", "PASS",
     sitemap_case("User-agent: *\nAllow: /\nSitemap: https://x.example/s1.xml\nSitemap: https://x.example/s2.xml\n",
                  rec(404, {}, "not found"),
                  {"https://x.example/s1.xml": rec(404, {}, "not found"),
                   "https://x.example/s2.xml": rec(200, {"Content-Type": "application/xml"}, URLSET)})),
    ("F6c", "WARN",
     sitemap_case("User-agent: *\nAllow: /\nSitemap: https://x.example/s1.xml\n",
                  rec(404, {}, "not found"),
                  {"https://x.example/s1.xml": rec(404, {}, "not found")})),
    ("F6d", "PASS",
     sitemap_case("User-agent: *\nAllow: /\n",
                  rec(200, {"Content-Type": "application/xml"}, SITEMAPINDEX),
                  {})),
    # F7 — llms relative links
    ("F7a", "PASS",
     audit_check(llms_records("- [A](/a)\n- [B](/b)\n- [C](/c)\n"), "llms_txt")),
    ("F7b", "PASS",
     audit_check(llms_records("- [A](/a)\n- [B](https://x.example/b)\n"), "llms_txt")),
    ("F7c", "WARN",
     audit_check(llms_records("- [Intro](#intro)\n- [Setup](#setup)\n"), "llms_txt")),
    ("F7d", "WARN",
     audit_check(llms_records("See example.com for details.\n"), "llms_txt")),
    # F8 — redirect-hop walls
    ("F8a", ("OPEN", None),
     verdict(200, {}, PARA, url="https://site.example/home",
             chain=["https://site.example/", "https://site.example/challenge", "https://site.example/home"])),
    ("F8b", ("OPEN", None),
     verdict(200, {}, PARA, url="https://site.example/home",
             chain=["https://site.example/", "https://site.example/verify-captcha", "https://site.example/home"])),
    ("F8c", ("LOGIN_GATED", None),
     verdict(200, {}, LOGIN_FORM, url=LOGIN,
             chain=["https://site.example/", LOGIN])),
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
