"""Wave 11 Leg B: adversarial battery v3 probe.

Runs every HANDCLASS-3 shape through the CURRENT classifier/audit
before any fix, printing verdict vs hand expectation. A mismatch is
a defect candidate (fix generalized) or an honest limitation (ledger).
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from wallcheck.classify import classify  # noqa: E402
from wallcheck.audit import evaluate_audit  # noqa: E402

LOGIN = "https://site.example/login"


def C(status, headers=None, body="", url="https://site.example/"):
    r = classify(status, headers or {}, body, final_url=url)
    return r["verdict"], r["vendor"]


def rec(status=200, headers=None, body="", final_url="https://x.example/"):
    return {"url": final_url, "final_url": final_url, "status": status,
            "headers": headers or {}, "body": body, "error": None,
            "redirect_chain": []}


def audit_robots(robots_body):
    records = {
        "robots": rec(200, {"Content-Type": "text/plain"}, robots_body),
        "llms": rec(404, {}, "not found"),
        "sitemap": rec(404, {}, "not found"),
        "homepage": rec(200, {"Content-Type": "text/html"},
                        "<html><head><title>x</title></head><body>x</body></html>"),
        "signed": rec(404, {}, "not found"),
    }
    out = evaluate_audit("https://x.example", records)
    return [c for c in out["checks"] if c["check"] == "robots_txt"][0]["status"]


def audit_sitemap(sitemap_body):
    records = {
        "robots": rec(200, {"Content-Type": "text/plain"}, "User-agent: *\nAllow: /\n"),
        "llms": rec(404, {}, "not found"),
        "sitemap": rec(200, {"Content-Type": "application/xml"}, sitemap_body),
        "homepage": rec(200, {"Content-Type": "text/html"},
                        "<html><head><title>x</title></head><body>x</body></html>"),
        "signed": rec(404, {}, "not found"),
    }
    out = evaluate_audit("https://x.example", records)
    return [c for c in out["checks"] if c["check"] == "sitemap"][0]["status"]


CASES = [
    # (id, got, expected)
    ("C1a", C(200, {}, "<html><head><script>setTimeout(function(){location.reload()},3000)</script></head><body></body></html>"), ("OPEN", None)),
    ("C1b", C(200, {}, '<html><body><form action="/challenge/verify-human" method="post"><input type="hidden" name="t" value="1"></form><script>document.forms[0].submit()</script></body></html>'), ("CHALLENGED", "Generic")),
    ("C1c", C(200, {}, "<html><body><p>Please wait while we verify your request</p><script src=\"/verify.js\"></script></body></html>"), ("CHALLENGED", "Generic")),
    ("C1d", C(200, {}, "<html><body><div id=\"app\">Loading...</div><script src=\"/bundle.js\"></script></body></html>"), ("OPEN", None)),
    ("C2a", C(403, {}, '<html><body><div class="h-captcha" data-sitekey="abc"></div><script src="https://js.hcaptcha.com/1/api.js"></script></body></html>'), ("CHALLENGED", "Generic")),
    ("C2b", C(403, {}, '<html><body><div class="cf-turnstile" data-sitekey="abc"></div><script src="https://challenges.cloudflare.com/turnstile/v0/api.js"></script></body></html>'), ("CHALLENGED", "Cloudflare")),
    ("C2c", C(200, {}, '<html><body><form action="/login"><input name="user"><input name="pass" type="password"><div class="cf-turnstile" data-sitekey="abc"></div><script src="https://challenges.cloudflare.com/turnstile/v0/api.js"></script></form></body></html>', LOGIN), ("LOGIN_GATED", "Cloudflare")),
    ("C2d", C(403, {}, '<html><body><form action="/login"><input name="user"></form><div class="px-captcha"></div></body></html>', LOGIN), ("CHALLENGED", "PerimeterX")),
    ("C3a", C(403, {}, '<html><body><img src="/captcha.png" alt="captcha image"></body></html>'), ("CHALLENGED", "Generic")),
    ("C3b", C(403, {}, '<html><body><svg xmlns="http://www.w3.org/2000/svg" width="300" height="100"><rect width="300" height="100" fill="#eee"/><circle cx="50" cy="50" r="30" fill="#333"/></svg></body></html>'), ("WALLED", None)),
    ("C3c", C(200, {}, '<html><body><svg xmlns="http://www.w3.org/2000/svg"><text x="10" y="20">Verify you are human</text></svg></body></html>'), ("CHALLENGED", "Generic")),
    ("C4a", C(403, {}, "<html><body><p>Verify you are human / Verifica que eres humano</p></body></html>"), ("CHALLENGED", "Generic")),
    ("C4b", C(403, {}, "<html><body><p>Verifica di essere umano. Non sono un robot.</p></body></html>"), ("CHALLENGED", "Generic")),
    ("C4c", C(403, {}, "<html><body><p>Bevestig dat u geen robot bent. Ik ben geen robot.</p></body></html>"), ("CHALLENGED", "Generic")),
    ("C4d", C(403, {}, "<html><body><p>로봇이 아님을 확인하세요.</p></body></html>"), ("CHALLENGED", "Generic")),
    ("C5a", C(403, {"cf-ray": "abc", "server": "cloudflare"}, ""), ("WALLED", "Cloudflare")),
    ("C5b", C(403, {"x-sucuri-id": "123"}, ""), ("WALLED", None)),
    ("C5c", C(429, {"retry-after": "60"}, ""), ("RATE_LIMITED", None)),
    ("C5d", C(503, {"cf-ray": "abc"}, ""), ("UNREACHABLE", None)),
    ("C6a", C(200, {}, '<html><body><form action="/login"><input name="user"><input name="pass" type="password"><script src="https://www.google.com/recaptcha/api.js"></script></form></body></html>', LOGIN), ("LOGIN_GATED", None)),
    ("C6b", C(200, {}, '<html><body><form action="/login"><input name="user"><input name="pass" type="password"><div class="h-captcha"></div><p>verify you are human to sign in</p></form></body></html>', LOGIN), ("LOGIN_GATED", None)),
    ("C7a", audit_sitemap('<?xml version="1.0"?><sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><sitemap><loc>https://x.example/s1.xml</loc></sitemap></sitemapindex>'), "PASS"),
    ("C7b", audit_sitemap('<?xml version="1.0"?><sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><sitemap><loc>https://x.example/dead.xml</loc></sitemap></sitemapindex>'), "PASS"),
    ("C7c", audit_sitemap('<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://x.example/</loc></url></urlset>'), "PASS"),
    ("C8a", audit_robots("User-agent: *\nCrawl-delay: 10\n"), "PASS"),
    ("C8b", audit_robots("User-agent: *\nDisallow: /\n\nUser-agent: GPTBot\nAllow: /\n"), "WARN"),
    ("C8c", audit_robots("User-agent: *\nDisallow: /\n\nUser-agent: ClaudeBot\nDisallow: /private\n"), "WARN"),
    ("C8d", audit_robots("User-agent: *\nCrawl-delay: 10\nSitemap: https://x.example/sitemap.xml\n"), "PASS"),
    ("C8e", audit_robots("user-agent: gptbot\nDisallow: /private\n"), "WARN"),
    ("C8f", audit_robots("User-agent: *\nDisallow:\n"), "PASS"),
    ("C8g", audit_robots("User-agent: GPTBot\nDisallow: /private\n\nUser-agent: *\nDisallow: /\n"), "WARN"),
]

if __name__ == "__main__":
    bad = 0
    for cid, got, exp in CASES:
        ok = got == exp
        if not ok:
            bad += 1
        print("%s got=%s expected=%s %s" % (cid, got, exp, "OK" if ok else "MISMATCH"))
    print("mismatches: %d / %d" % (bad, len(CASES)))
