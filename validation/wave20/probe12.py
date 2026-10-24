"""Scratch probe for battery v12: prints actual classifier/audit
verdicts for every HANDCLASS-12 shape, for comparison against the
hand classifications. Not a test file; the test file is written
from these results plus the hand classifications.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from wallcheck.classify import classify  # noqa: E402
from wallcheck.audit import evaluate_audit  # noqa: E402

BIG = "<article>" + ("<p>Real article text about web infrastructure and the history of the open web, written in full sentences for readers. </p>" * 170) + "</article>"


def v(status, body, url="https://site.example/", headers=None):
    r = classify(status, headers or {}, body, final_url=url)
    return "%s/%s" % (r["verdict"], r["vendor"])


def rec(status=200, headers=None, body="", final_url="https://x.example/"):
    return {"url": final_url, "final_url": final_url, "status": status,
            "headers": headers or {}, "body": body, "error": None,
            "redirect_chain": []}


def base_records(**over):
    records = {
        "homepage": rec(200, body="<html><body>Home</body></html>"),
        "robots": rec(200, body="User-agent: *\nAllow: /\n"),
        "llms": rec(404, body=""),
        "sitemap": rec(404, body=""),
        "openapi": rec(404, body=""),
        "openapi_wellknown": rec(404, body=""),
        "api_root": rec(404, body=""),
        "api_docs": rec(404, body=""),
        "signed": rec(404, body=""),
    }
    records.update(over)
    return records


def audit_check(records, name):
    out = evaluate_audit("https://x.example", records)
    return [c for c in out["checks"] if c["check"] == name][0]


URLSET = ('<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
          '<url><loc>https://x.example/</loc></url></urlset>')
SITEMAPINDEX = ('<?xml version="1.0"?><sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                '<sitemap><loc>https://x.example/sitemap-a.xml</loc></sitemap>'
                '<sitemap><loc>https://x.example/sitemap-b.xml</loc></sitemap></sitemapindex>')

shapes = [
    ("M1a", v(200, '<html><body><iframe src="https://challenge.example/captcha/verify"></iframe></body></html>')),
    ("M1b", v(200, '<html><body><iframe src="https://content.example/article"></iframe></body></html>')),
    ("M1c", v(200, BIG + '<iframe src="https://challenge.example/captcha/verify"></iframe>')),
    ("M1d", v(200, '<html><body><iframe src="/login"></iframe></body></html>')),
    ("M2a", v(200, "<html><body><p>Wir überprüfen Ihren Browser, bitte warten.</p></body></html>")),
    ("M2b", v(200, "<html><body><p>Nous vérifions votre navigateur, veuillez patienter.</p></body></html>")),
    ("M2c", v(200, "<html><body><p>Estamos verificando su navegador, por favor espere.</p></body></html>")),
    ("M2d", v(200, "<html><body><p>Estamos verificando o seu navegador, aguarde.</p></body></html>")),
    ("M2e", v(200, "<html><body><p>ブラウザを確認しています。お待ちください。</p></body></html>")),
    ("M2f", v(200, BIG + "<p>Wir überprüfen Ihren Browser, bitte warten.</p>")),
    ("M3a", v(200, "<html><body><p>Підтвердіть, що ви не робот</p></body></html>")),
    ("M3b", v(200, "<html><body><p>कृपया पुष्टि करें कि आप रोबोट नहीं हैं</p></body></html>")),
    ("M3c", v(200, "<html><body><p>sahkan bahawa anda bukan robot</p></body></html>")),
    ("M3d", v(200, "<html><body><p>kumpirmahin na hindi ka robot</p></body></html>")),
    ("M3e", v(200, "<html><body><p>thibitisha kuwa wewe si roboti</p></body></html>")),
    ("M3f", v(200, BIG + "<p>Підтвердіть, що ви не робот</p>")),
    ("M3g", v(200, "<html><body><p>не робот</p></body></html>")),
    ("M4a", v(200, "<html><body><p>Please verify your identity to continue.</p></body></html>")),
    ("M4b", v(200, "<html><body><p>Please verify your identity to continue.</p></body></html>", url="https://site.example/login")),
    ("M4c", v(200, BIG + "<p>Please verify your identity to continue.</p>")),
    ("M4d", v(200, '<html><body><p>Please verify your identity to continue.</p><button>Continue</button></body></html>')),
    ("M5a", v(200, '<html><body><iframe title="Verify you are human" src="https://x.example/vid"></iframe></body></html>')),
    ("M5b", v(200, BIG + '<iframe title="Verify you are human" src="https://x.example/vid"></iframe>')),
    ("M6a", v(403, '<html><body><div class="modal-overlay">Verify you are human</div></body></html>')),
    ("M6b", v(403, '<html><body><dialog open>Verify you are human</dialog></body></html>')),
    ("M8a", v(401, "<html><body><p>Verify you are human</p></body></html>")),
    ("M8b", v(429, "<html><body><p>Verify you are human</p></body></html>")),
    ("M8c", v(503, "<html><body><p>Verifying your browser, please wait.</p></body></html>")),
    ("M8d", v(200, "<html><body><p>Verify you are human</p></body></html>", url="https://site.example/login")),
    ("M8e", v(200, '<html><head><meta http-equiv="refresh" content="0; url=/challenge/captcha"></head><body></body></html>', url="https://site.example/login")),
    ("M9a", v(200, BIG + "<details open><summary>Check</summary><p>Verify you are human</p></details>")),
    ("M9b", v(200, '<html><body><button aria-label="Verify you are human">Go</button></body></html>')),
    ("M9c", v(200, BIG + '<button aria-label="Verify you are human">Go</button>')),
    ("M10a", v(200, '{"error": "captcha required", "code": "challenge"}')),
]

for name, actual in shapes:
    print("%s -> %s" % (name, actual))

# M7 audit shapes
r = base_records(robots=rec(200, body="User-agent: *\nDisallow: /\n\nUser-agent: GPTBot\nAllow: /\n"))
c = audit_check(r, "robots_txt")
print("M7a robots -> %s %s" % (c["status"], c["evidence"][:2]))
r = base_records(robots=rec(200, body="User-agent: *\nAllow: /\nSitemap: https://x.example/sitemap.xml\n"),
                 sitemap=rec(200, body=SITEMAPINDEX))
c = audit_check(r, "sitemap")
print("M7b sitemap -> %s %s" % (c["status"], c["evidence"][:2]))
r = base_records(llms=rec(200, body="# Docs\n\n[Guide]()\n"))
c = audit_check(r, "llms_txt")
print("M7c llms -> %s %s" % (c["status"], c["evidence"][:2]))
r = base_records(llms=rec(200, body="\ufeff---\rkey: https://meta.example\r---\r# Title\r[Guide](https://x.example/guide)\r"))
c = audit_check(r, "llms_txt")
print("M7d llms -> %s %s" % (c["status"], c["evidence"][:2]))
r = base_records(robots=rec(200, body="User-agent: *\nAllow: /\nDisallow: /private\n"))
c = audit_check(r, "robots_txt")
print("M7e robots -> %s %s" % (c["status"], c["evidence"][:2]))
