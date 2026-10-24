"""Wave 16 battery v8 regression pins (see validation/wave16/
HANDCLASS-8.md for the hand classifications). Shapes: TRAFFIC_CHECK
split across elements (incl. within-word splits), data-* attribute
markers, CSS-content challenges, 307/308 Location redirects,
passkey/WebAuthn prompts, robots files with no User-agent groups,
llms charset/BOM variants, circular sitemaps, application/json
script blocks, magic-link email forms. Plus guards for each fix's
blast radius.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
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


# H1 — TRAFFIC_CHECK splits
def test_h1a():
    assert verdict(403, {}, '<html><body><p>We noticed unusual</p><p>traffic from your device.</p><p>Please verify to continue.</p></body></html>') == ("CHALLENGED", "Generic")


def test_h1b():
    assert verdict(403, {}, '<html><body><p>Unusual traffic from your network.</p><p>Please ver<span>ify</span> your connection.</p></body></html>') == ("CHALLENGED", "Generic")


def test_h1c():
    assert verdict(200, {}, ARTICLE + '<p>We noticed unusual</p><p>traffic patterns</p><p>Please verify to continue.</p></body></html>') == ("OPEN", None)


def test_h1d():
    assert verdict(403, {}, '<html><body><p>Unusual traffic from your network. Please verify to continue.</p></body></html>') == ("CHALLENGED", "Generic")


def test_h1e():
    assert verdict(403, {}, '<html><body><p>We noticed unusual</p><p>traffic from your device.</p></body></html>') == ("WALLED", None)


def test_h1f():
    assert verdict(403, {}, '<html><body><p>Ver<span>ify</span> you are human</p></body></html>') == ("CHALLENGED", "Generic")


def test_h1g():
    assert verdict(403, {}, '<html><body><p>Brow<span>ser</span> check in progress</p></body></html>') == ("CHALLENGED", "Generic")


def test_h1h():
    assert verdict(403, {}, '<html><body><p>Please complete the cap<span>tcha</span> to continue.</p></body></html>') == ("CHALLENGED", "Generic")


# H2 — data-* attributes
def test_h2a():
    assert verdict(200, {}, SHORT_ARTICLE + '<div data-message="verify you are human"></div></body></html>') == ("OPEN", None)


def test_h2b():
    assert verdict(403, {}, '<html><body><div data-challenge="verify you are human"></div></body></html>') == ("CHALLENGED", "Generic")


def test_h2c():
    assert verdict(200, {}, SHORT_ARTICLE + '<div data-vendor="perimeterx"></div></body></html>') == ("OPEN", None)


def test_h2d():
    assert verdict(200, {}, '<html><body><div data-vendor="perimeterx"></div></body></html>') == ("CHALLENGED", "PerimeterX")


def test_h2e():
    assert verdict(200, {}, SHORT_ARTICLE + '<div data-captcha="true"></div></body></html>') == ("OPEN", None)


# H3 — CSS content
def test_h3a():
    assert verdict(403, {}, '<html><head><style>.gate::before{content:"Verify you are human"}</style></head><body><div class="gate"></div></body></html>') == ("CHALLENGED", "Generic")


def test_h3b():
    assert verdict(200, {}, SHORT_ARTICLE + '<style>.note::before{content:"Verify you are human"}</style></body></html>') == ("OPEN", None)


def test_h3c():
    assert verdict(200, {}, ARTICLE + '<style>.note::before{content:"Verify you are human"}</style></body></html>') == ("OPEN", None)


def test_h3d():
    assert verdict(200, {}, SHORT_ARTICLE + '<style>.captcha-box{border:1px solid red}</style></body></html>') == ("OPEN", None)


def test_h3e():
    assert verdict(200, {}, SHORT_ARTICLE + '<style>.px-note{content:"perimeterx"}</style></body></html>') == ("OPEN", None)


def test_h3f():
    assert verdict(200, {}, '<html><head><style>.px-note{content:"perimeterx"}</style></head><body></body></html>') == ("CHALLENGED", "PerimeterX")


# H4 — Location-header redirects
def test_h4a():
    assert verdict(307, {"Location": "/challenge/verify"}, "") == ("CHALLENGED", "Generic")


def test_h4b():
    assert verdict(308, {"Location": "/login"}, "") == ("LOGIN_GATED", None)


def test_h4c():
    assert verdict(307, {"Location": "/home"}, "") == ("OPEN", None)


def test_h4d():
    assert verdict(302, {"Location": "/challenge/verify"}, "") == ("CHALLENGED", "Generic")


def test_h4e():
    assert verdict(307, {"Location": "/challenge/verify"}, "", url=LOGIN) == ("CHALLENGED", "Generic")


# H5 — passkey prompts
def test_h5a():
    assert verdict(200, {}, PASSKEY_PROMPT, url="https://site.example/passkey") == ("LOGIN_GATED", None)


def test_h5b():
    assert verdict(200, {}, SHORT_ARTICLE + '<nav><a href="/passkey">Sign in with a passkey</a></nav></body></html>') == ("OPEN", None)


def test_h5c():
    assert verdict(200, {}, PASSKEY_PROMPT, url=LOGIN) == ("LOGIN_GATED", None)


def test_h5d():
    assert verdict(200, {}, '<html><body><p>Verify your identity to continue with your passkey.</p><button>Continue</button></body></html>', url="https://site.example/passkey") == ("LOGIN_GATED", None)


def test_h5e():
    assert verdict(200, {}, '<html><body><p>How passkeys work: a WebAuthn explainer covering public-key cryptography, authenticators, and the ceremony that replaces passwords.</p></body></html>') == ("OPEN", None)


# H6 — robots with no User-agent groups
def test_h6a():
    assert audit_check(robots_records("Sitemap: https://x.example/sitemap.xml\n"), "robots_txt") == "PASS"


def test_h6b():
    assert audit_check(robots_records(""), "robots_txt") == "PASS"


def test_h6c():
    assert audit_check(robots_records("# nothing here\n# just comments\n"), "robots_txt") == "PASS"


def test_h6d():
    assert audit_check(robots_records("User-agent: *\nCrawl-delay: 10\n"), "robots_txt") == "PASS"


def test_h6e():
    assert audit_check(robots_records("User-agent: *\nDisallow:\n"), "robots_txt") == "PASS"


# H7 — llms charset/BOM
def test_h7a():
    assert audit_check(llms_records("# Docs\n\n- [Guide](/guide)\n- [API](/api)\n", "text/plain; charset=utf-8"), "llms_txt") == "PASS"


def test_h7b():
    assert audit_check(llms_records("# Docs\n\n- [Guide](/guide)\n- [API](/api)\n", "text/markdown; charset=utf-8"), "llms_txt") == "PASS"


def test_h7c():
    assert audit_check(llms_records("# Docs\n\n- [Guide](/guide)\n- [API](/api)\n", "application/octet-stream"), "llms_txt") == "PASS"


def test_h7d():
    assert audit_check(llms_records("\ufeff---\ntitle: Example Site\nurl: https://x.example\n---\n"), "llms_txt") == "WARN"


def test_h7e():
    assert audit_check(llms_records("\ufeff# Docs\n\n- [Guide](/guide)\n- [API](/api)\n"), "llms_txt") == "PASS"


# H8 — circular sitemaps
def test_h8a():
    assert audit_check(sitemap_records('<?xml version="1.0"?><sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><sitemap><loc>https://x.example/sitemap-b.xml</loc></sitemap><sitemap><loc>https://x.example/sitemap-a.xml</loc></sitemap></sitemapindex>'), "sitemap") == "PASS"


def test_h8b():
    assert audit_check(sitemap_records('<?xml version="1.0"?><sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><sitemap><loc>https://x.example/sitemap.xml</loc></sitemap></sitemapindex>'), "sitemap") == "PASS"


def test_h8c():
    assert audit_check(sitemap_records('<?xml version="1.0"?><sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><sitemap><lastmod>2026-01-01</lastmod></sitemap></sitemapindex>'), "sitemap") == "WARN"


def test_h8d():
    assert audit_check(sitemap_records('<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://x.example/sitemap-a.xml</loc></url><url><loc>https://x.example/sitemap-b.xml</loc></url></urlset>'), "sitemap") == "PASS"


# H9 — application/json script blocks
def test_h9a():
    assert verdict(200, {}, SHORT_ARTICLE + '<script type="application/json">{"description": "perimeterx protects this site"}</script></body></html>') == ("OPEN", None)


def test_h9b():
    assert verdict(200, {}, '<html><body><script type="application/json">{"description": "perimeterx"}</script></body></html>') == ("CHALLENGED", "PerimeterX")


# H10 — magic-link forms
def test_h10a():
    assert verdict(200, {}, MAGIC_FORM, url="https://site.example/magic-link") == ("LOGIN_GATED", None)


def test_h10b():
    assert verdict(200, {}, '<html><body><form action="/subscribe" method="post"><label>Subscribe to our newsletter</label><input type="email" name="email"><button>Subscribe</button></form></body></html>') == ("OPEN", None)


def test_h10c():
    assert verdict(200, {}, RESET_FORM, url="https://site.example/forgot-password") == ("LOGIN_GATED", None)


def test_h10d():
    assert verdict(200, {}, '<html><body><p>Welcome to the site.</p><a href="/login">Sign in</a></body></html>') == ("OPEN", None)


# Guards — fix blast radius
def test_guard_loader_script_still_fires():
    # W16-007 guard: a vendor marker in a REGULAR (non-JSON) script
    # on a page with visible text still fires — only JSON data
    # blocks are stripped.
    assert verdict(200, {}, SHORT_ARTICLE + '<script>var vendor = "perimeterx";</script></body></html>') == ("CHALLENGED", "PerimeterX")


def test_guard_visible_widget_still_fires():
    # W16-002 guard: a visible captcha widget's class token
    # survives data-attribute stripping — the widget is body
    # markup, not a data attribute.
    assert verdict(403, {}, '<html><body><div class="h-captcha" data-sitekey="abc" data-vendor="x"></div></body></html>') == ("CHALLENGED", "Generic")


def test_guard_body_challenge_with_style_still_fires():
    # W16-003 guard: a real challenge sentence in body text still
    # fires even when a style block is also present.
    assert verdict(403, {}, '<html><body><p>Verify you are human</p><style>.note{color:red}</style></body></html>') == ("CHALLENGED", "Generic")


def test_guard_email_form_without_link_wording():
    # W16-008 guard, SUPERSEDED by Wave 19 (W19-L3) — read the note:
    # an email input plus generic "sign in" prose (no link wording)
    # is still NOT a magic-link form (the magic-link rule needs link
    # wording, and nothing here has it). But the shape IS an
    # email-only Continue sign-in step — the page's only content is
    # a "Sign in to your account" form with an email input and a
    # Continue button — so the newer, narrower Continue rule owns
    # the verdict now: LOGIN_GATED via EMAIL_CONTINUE_PROMPT, not
    # OPEN. The magic-link rule's narrowness is preserved (see the
    # Wave 19 L3d/L3e guards: Subscribe buttons and script-only
    # auth wording still read OPEN); what changed is that a new
    # sibling rule, hand-classified in HANDCLASS-11 (L3a), claims
    # this shape on its own grounds. Flipping a guard is allowed
    # only with this independent justification — the shape meets
    # SPEC's LOGIN_GATED definition on its own, not because the
    # magic-link rule moved.
    assert verdict(200, {}, '<html><body><form action="/account" method="post"><label>Sign in to your account</label><input type="email" name="email"><button>Continue</button></form></body></html>') == ("LOGIN_GATED", None)


def test_guard_script_split_phrase_suppressed():
    # W16-001b guard: a split phrase living ONLY in a script block
    # on a page with visible text stays suppressed — the nospace
    # variant is derived from the script-stripped body.
    assert verdict(200, {}, SHORT_ARTICLE + '<script>var s = "Ver<span>ify</span> you are human";</script></body></html>') == ("OPEN", None)
