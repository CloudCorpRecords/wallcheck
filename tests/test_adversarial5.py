"""Wave 13 adversarial battery v5 — hand-classified fixtures.

Each case pins the hand verdict from validation/wave13/HANDCLASS-5.md
BEFORE the classifier result is consulted. A failing case is a defect
candidate, fixed generalized or ledgered as an honest limitation.
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
SHORT_ARTICLE = ("<html><body><p>A short post about how the team "
                 "ships software on Fridays.</p></body></html>")
LOGIN_FORM = ('<html><body><form action="/session" method="post">'
              '<input type="password" name="pw">'
              '<div class="cf-turnstile"></div>'
              '<script src="https://challenges.cloudflare.com/turnstile/v0/api.js"></script>'
              '<button>Sign in</button></form></body></html>')
ARTICLE_CHECK_BROWSER = ("<html><body>" + "<p>An article about how "
                         "to check your browser settings before a video call.</p>" * 300
                         + "</body></html>")


class TestBattery5Images:
    def test_e1a_captcha_filename(self):
        assert verdict(403, {}, '<html><body><img src="/captcha/image.png" alt=""></body></html>') == ("CHALLENGED", "Generic")

    def test_e1b_opaque_image_no_signal(self):
        assert verdict(403, {}, '<html><body><img src="/img/a7f3.png" alt=""></body></html>') == ("WALLED", None)

    def test_e1c_image_title_attribute(self):
        assert verdict(403, {}, '<html><body><img src="/img/a7f3.png" title="Please verify you are human"></body></html>') == ("CHALLENGED", "Generic")


class TestBattery5NoscriptAndTitle:
    def test_e2a_noscript_js_proof_phrase(self):
        assert verdict(200, {}, '<html><body><noscript><p>This site requires JavaScript. Please enable JavaScript to continue.</p></noscript></body></html>') == ("CHALLENGED", "Generic")

    def test_e2b_noscript_capability_note(self):
        assert verdict(200, {}, '<html><body><noscript><p>This site requires JavaScript to run. Please enable JavaScript to run this app.</p></noscript></body></html>') == ("OPEN", None)

    def test_e2c_noscript_human_check(self):
        assert verdict(200, {}, '<html><body><noscript><p>Please enable JavaScript and verify you are human to continue.</p></noscript></body></html>') == ("CHALLENGED", "Generic")

    def test_e3a_title_only_human_check(self):
        assert verdict(200, {}, '<html><head><title>Verify you are human</title></head><body><div class="spinner"></div></body></html>') == ("CHALLENGED", "Generic")

    def test_e3b_article_with_check_title(self):
        assert len(ARTICLE) > 16384
        assert verdict(200, {}, "<html><head><title>Verify you are human: how sites check visitors</title></head><body>" + ARTICLE + "</body></html>") == ("OPEN", None)


class TestBattery5CookieAndPhrases:
    def test_e4a_px_cookie_on_served_article(self):
        assert verdict(200, {"set-cookie": "_pxvid=abc123; Path=/"}, ARTICLE) == ("OPEN", None)

    def test_e4b_js_proof_stub_with_px_cookie(self):
        assert verdict(200, {"set-cookie": "_pxvid=abc123; Path=/"}, '<html><body><p>Please wait while we check your browser</p></body></html>') == ("CHALLENGED", "Generic")

    def test_e4b_guard_article_mentioning_check_browser(self):
        assert len(ARTICLE_CHECK_BROWSER) > 16384
        assert verdict(200, {}, ARTICLE_CHECK_BROWSER) == ("OPEN", None)


class TestBattery5Audit:
    def test_e5a_wildcard_only_block(self):
        assert audit_check(robots_records("User-agent: *\nDisallow: /\n"), "robots_txt") == "FAIL"

    def test_e5b_single_named_block(self):
        assert audit_check(robots_records("User-agent: GPTBot\nDisallow: /\n"), "robots_txt") == "WARN"

    def test_e5c_all_named_blocks_no_wildcard(self):
        assert audit_check(robots_records("User-agent: GPTBot\nDisallow: /\n\nUser-agent: ClaudeBot\nDisallow: /\n\nUser-agent: CCBot\nDisallow: /\n\nUser-agent: Google-Extended\nDisallow: /\n"), "robots_txt") == "FAIL"

    def test_e6a_title_only_llms(self):
        assert audit_check(llms_records("# Welcome to Example Corporation\n"), "llms_txt") == "WARN"

    def test_e6b_minimal_linked_llms(self):
        assert audit_check(llms_records("# My Site\n\n- [Docs](/docs)\n"), "llms_txt") == "PASS"

    def test_e7a_one_url_sitemap(self):
        assert audit_check(sitemap_records('<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://x.example/</loc></url></urlset>'), "sitemap") == "PASS"

    def test_e7b_one_child_sitemapindex(self):
        assert audit_check(sitemap_records('<?xml version="1.0"?><sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><sitemap><loc>https://x.example/sitemap1.xml</loc></sitemap></sitemapindex>'), "sitemap") == "PASS"


class TestBattery5ChainsAndCommentsAndCase:
    def test_e8a_four_hop_chain_to_login(self):
        assert verdict(200, {}, '<html><body><form><input type="password"><button>Sign in</button></form></body></html>', url=LOGIN, chain=["https://site.example/", "https://site.example/a", "https://site.example/b", "https://site.example/c", LOGIN]) == ("LOGIN_GATED", None)

    def test_e8b_chain_to_turnstile_login(self):
        assert verdict(200, {}, LOGIN_FORM, url=LOGIN, chain=["https://site.example/", "https://site.example/challenge", LOGIN]) == ("LOGIN_GATED", "Cloudflare")

    def test_e8c_fired_wall_at_login_url(self):
        assert verdict(403, {"cf-ray": "abc123", "cf-mitigated": "challenge"}, "<html><body><h1>Just a moment</h1></body></html>", url=LOGIN, chain=["https://site.example/", "https://site.example/a", LOGIN]) == ("CHALLENGED", "Cloudflare")

    def test_e9a_comment_only_markers_on_article(self):
        assert verdict(200, {}, '<html><body>' + SHORT_ARTICLE + '<!-- Cloudflare Ray ID: abc123 — Just a moment --></body></html>') == ("OPEN", None)

    def test_e9b_comment_only_vendor_on_refusal(self):
        assert verdict(403, {}, '<html><body><p>Access denied</p><!-- PerimeterX px-captcha reference --></body></html>') == ("WALLED", None)

    def test_e10a_mixed_case_just_a_moment(self):
        assert verdict(403, {"cf-ray": "abc123"}, "<html><body><h1>JUST A MOMENT</h1></body></html>") == ("CHALLENGED", "Cloudflare")

    def test_e10b_mixed_case_perimeterx(self):
        assert verdict(403, {}, "<html><body><p>PERIMETERX</p><p>Please verify you are NOT A ROBOT</p></body></html>") == ("WALLED", "PerimeterX")

    def test_e10c_mixed_case_datadome(self):
        assert verdict(403, {}, "<html><body><p>DaTaDoMe</p><p>Access denied</p></body></html>") == ("CHALLENGED", "DataDome")
