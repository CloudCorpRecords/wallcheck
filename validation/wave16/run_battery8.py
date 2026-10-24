"""Wave 16 Leg B: adversarial battery v8 runner.

Runs the CURRENT classifier/audit against the hand-classified shapes in
HANDCLASS-8.md and reports every mismatch. No fixes are applied by this
script; it is the measurement step. (Audit shapes use evaluate_audit
directly, like Waves 11-15.)
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
PASSKEY_PROMPT = ('<html><body><p>Sign in with your passkey</p>'
                  '<button>Continue with passkey</button>'
                  '<script>navigator.credentials.get({publicKey: {}});'
                  '</script></body></html>')
MAGIC_FORM = ('<html><body><form action="/magic" method="post">'
              '<label>We\'ll send you a sign-in link</label>'
              '<input type="email" name="email">'
              '<button>Send link</button></form></body></html>')
RESET_FORM = ('<html><body><form action="/reset" method="post">'
              '<label>Send me a password reset link</label>'
              '<input type="email" name="email">'
              '<button>Send link</button></form></body></html>')

CASES = [
    # H1 — TRAFFIC_CHECK split across elements
    ("H1a", ("CHALLENGED", "Generic"),
     verdict(403, {}, '<html><body><p>We noticed unusual</p><p>traffic from your device.</p><p>Please verify to continue.</p></body></html>')),
    ("H1b", ("CHALLENGED", "Generic"),
     verdict(403, {}, '<html><body><p>Unusual traffic from your network.</p><p>Please ver<span>ify</span> your connection.</p></body></html>')),
    ("H1c", ("OPEN", None),
     verdict(200, {}, ARTICLE + '<p>We noticed unusual</p><p>traffic patterns</p><p>Please verify to continue.</p></body></html>')),
    ("H1d", ("CHALLENGED", "Generic"),
     verdict(403, {}, '<html><body><p>Unusual traffic from your network. Please verify to continue.</p></body></html>')),
    ("H1e", ("WALLED", None),
     verdict(403, {}, '<html><body><p>We noticed unusual</p><p>traffic from your device.</p></body></html>')),
    ("H1f", ("CHALLENGED", "Generic"),
     verdict(403, {}, '<html><body><p>Ver<span>ify</span> you are human</p></body></html>')),
    ("H1g", ("CHALLENGED", "Generic"),
     verdict(403, {}, '<html><body><p>Brow<span>ser</span> check in progress</p></body></html>')),
    ("H1h", ("CHALLENGED", "Generic"),
     verdict(403, {}, '<html><body><p>Please complete the cap<span>tcha</span> to continue.</p></body></html>')),
    # H2 — data-* attributes
    ("H2a", ("OPEN", None),
     verdict(200, {}, SHORT_ARTICLE + '<div data-message="verify you are human"></div></body></html>')),
    ("H2b", ("CHALLENGED", "Generic"),
     verdict(403, {}, '<html><body><div data-challenge="verify you are human"></div></body></html>')),
    ("H2c", ("OPEN", None),
     verdict(200, {}, SHORT_ARTICLE + '<div data-vendor="perimeterx"></div></body></html>')),
    ("H2d", ("CHALLENGED", "PerimeterX"),
     verdict(200, {}, '<html><body><div data-vendor="perimeterx"></div></body></html>')),
    ("H2e", ("OPEN", None),
     verdict(200, {}, SHORT_ARTICLE + '<div data-captcha="true"></div></body></html>')),
    # H3 — CSS content
    ("H3a", ("CHALLENGED", "Generic"),
     verdict(403, {}, '<html><head><style>.gate::before{content:"Verify you are human"}</style></head><body><div class="gate"></div></body></html>')),
    ("H3b", ("OPEN", None),
     verdict(200, {}, SHORT_ARTICLE + '<style>.note::before{content:"Verify you are human"}</style></body></html>')),
    ("H3c", ("OPEN", None),
     verdict(200, {}, ARTICLE + '<style>.note::before{content:"Verify you are human"}</style></body></html>')),
    ("H3d", ("OPEN", None),
     verdict(200, {}, SHORT_ARTICLE + '<style>.captcha-box{border:1px solid red}</style></body></html>')),
    ("H3e", ("OPEN", None),
     verdict(200, {}, SHORT_ARTICLE + '<style>.px-note{content:"perimeterx"}</style></body></html>')),
    ("H3f", ("CHALLENGED", "PerimeterX"),
     verdict(200, {}, '<html><head><style>.px-note{content:"perimeterx"}</style></head><body></body></html>')),
    # H4 — 307/308 Location redirects
    ("H4a", ("CHALLENGED", "Generic"),
     verdict(307, {"Location": "/challenge/verify"}, "")),
    ("H4b", ("LOGIN_GATED", None),
     verdict(308, {"Location": "/login"}, "")),
    ("H4c", ("OPEN", None),
     verdict(307, {"Location": "/home"}, "")),
    ("H4d", ("CHALLENGED", "Generic"),
     verdict(302, {"Location": "/challenge/verify"}, "")),
    ("H4e", ("CHALLENGED", "Generic"),
     verdict(307, {"Location": "/challenge/verify"}, "", url=LOGIN)),
    # H5 — passkey/WebAuthn prompts
    ("H5a", ("LOGIN_GATED", None),
     verdict(200, {}, PASSKEY_PROMPT, url="https://site.example/passkey")),
    ("H5b", ("OPEN", None),
     verdict(200, {}, SHORT_ARTICLE + '<nav><a href="/passkey">Sign in with a passkey</a></nav></body></html>')),
    ("H5c", ("LOGIN_GATED", None),
     verdict(200, {}, PASSKEY_PROMPT, url=LOGIN)),
    ("H5d", ("LOGIN_GATED", None),
     verdict(200, {}, '<html><body><p>Verify your identity to continue with your passkey.</p><button>Continue</button></body></html>', url="https://site.example/passkey")),
    ("H5e", ("OPEN", None),
     verdict(200, {}, '<html><body><p>How passkeys work: a WebAuthn explainer covering public-key cryptography, authenticators, and the ceremony that replaces passwords.</p></body></html>')),
    # H6 — robots with no User-agent groups
    ("H6a", "PASS",
     audit_check(robots_records("Sitemap: https://x.example/sitemap.xml\n"), "robots_txt")),
    ("H6b", "PASS",
     audit_check(robots_records(""), "robots_txt")),
    ("H6c", "PASS",
     audit_check(robots_records("# nothing here\n# just comments\n"), "robots_txt")),
    ("H6d", "PASS",
     audit_check(robots_records("User-agent: *\nCrawl-delay: 10\n"), "robots_txt")),
    ("H6e", "PASS",
     audit_check(robots_records("User-agent: *\nDisallow:\n"), "robots_txt")),
    # H7 — llms charset/BOM
    ("H7a", "PASS",
     audit_check(llms_records("# Docs\n\n- [Guide](/guide)\n- [API](/api)\n", "text/plain; charset=utf-8"), "llms_txt")),
    ("H7b", "PASS",
     audit_check(llms_records("# Docs\n\n- [Guide](/guide)\n- [API](/api)\n", "text/markdown; charset=utf-8"), "llms_txt")),
    ("H7c", "PASS",
     audit_check(llms_records("# Docs\n\n- [Guide](/guide)\n- [API](/api)\n", "application/octet-stream"), "llms_txt")),
    ("H7d", "WARN",
     audit_check(llms_records("\ufeff---\ntitle: Example Site\nurl: https://x.example\n---\n"), "llms_txt")),
    ("H7e", "PASS",
     audit_check(llms_records("\ufeff# Docs\n\n- [Guide](/guide)\n- [API](/api)\n"), "llms_txt")),
    # H8 — circular sitemaps
    ("H8a", "PASS",
     audit_check(sitemap_records('<?xml version="1.0"?><sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><sitemap><loc>https://x.example/sitemap-b.xml</loc></sitemap><sitemap><loc>https://x.example/sitemap-a.xml</loc></sitemap></sitemapindex>'), "sitemap")),
    ("H8b", "PASS",
     audit_check(sitemap_records('<?xml version="1.0"?><sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><sitemap><loc>https://x.example/sitemap.xml</loc></sitemap></sitemapindex>'), "sitemap")),
    ("H8c", "WARN",
     audit_check(sitemap_records('<?xml version="1.0"?><sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><sitemap><lastmod>2026-01-01</lastmod></sitemap></sitemapindex>'), "sitemap")),
    ("H8d", "PASS",
     audit_check(sitemap_records('<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://x.example/sitemap-a.xml</loc></url><url><loc>https://x.example/sitemap-b.xml</loc></url></urlset>'), "sitemap")),
    # H9 — application/json script blocks
    ("H9a", ("OPEN", None),
     verdict(200, {}, SHORT_ARTICLE + '<script type="application/json">{"description": "perimeterx protects this site"}</script></body></html>')),
    ("H9b", ("CHALLENGED", "PerimeterX"),
     verdict(200, {}, '<html><body><script type="application/json">{"description": "perimeterx"}</script></body></html>')),
    # H10 — magic-link / email sign-in forms
    ("H10a", ("LOGIN_GATED", None),
     verdict(200, {}, MAGIC_FORM, url="https://site.example/magic-link")),
    ("H10b", ("OPEN", None),
     verdict(200, {}, '<html><body><form action="/subscribe" method="post"><label>Subscribe to our newsletter</label><input type="email" name="email"><button>Subscribe</button></form></body></html>')),
    ("H10c", ("LOGIN_GATED", None),
     verdict(200, {}, RESET_FORM, url="https://site.example/forgot-password")),
    ("H10d", ("OPEN", None),
     verdict(200, {}, '<html><body><p>Welcome to the site.</p><a href="/login">Sign in</a></body></html>')),
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
