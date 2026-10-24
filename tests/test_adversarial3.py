"""Wave 11 adversarial battery v3 — hand-classified fixtures.

Each case pins the hand verdict from validation/wave11/HANDCLASS-3.md
BEFORE the classifier result is consulted. A failing case is a defect
candidate, fixed generalized or ledgered as an honest limitation.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from wallcheck.classify import classify  # noqa: E402
from wallcheck.audit import evaluate_audit  # noqa: E402

LOGIN = "https://site.example/login"


def C(status, headers=None, body="", url="https://site.example/"):
    return classify(status, headers or {}, body, final_url=url)


def verdict(status, headers=None, body="", url="https://site.example/"):
    r = C(status, headers, body, url)
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


def sitemap_records(sitemap_body):
    return {
        "robots": rec(200, {"Content-Type": "text/plain"},
                      "User-agent: *\nAllow: /\n"),
        "llms": rec(404, {}, "not found"),
        "sitemap": rec(200, {"Content-Type": "application/xml"},
                       sitemap_body),
        "homepage": rec(200, {"Content-Type": "text/html"},
                        "<html><head><title>x</title></head><body>x</body></html>"),
        "signed": rec(404, {}, "not found"),
    }


# C1 — silent JS-proof stubs (200, no vendor tokens)
def test_c1a_reload_only_empty_page():
    assert verdict(200, {}, "<html><head><script>setTimeout(function(){location.reload()},3000)</script></head><body></body></html>") == ("OPEN", None)


def test_c1b_form_action_to_challenge():
    assert verdict(200, {}, '<html><body><form action="/challenge/verify-human" method="post"><input type="hidden" name="t" value="1"></form><script>document.forms[0].submit()</script></body></html>') == ("CHALLENGED", "Generic")


def test_c1c_verify_your_request_stub():
    assert verdict(200, {}, "<html><body><p>Please wait while we verify your request</p><script src=\"/verify.js\"></script></body></html>") == ("CHALLENGED", "Generic")


def test_c1d_spa_shell_loading():
    assert verdict(200, {}, "<html><body><div id=\"app\">Loading...</div><script src=\"/bundle.js\"></script></body></html>") == ("OPEN", None)


# C2 — widget variants (hCaptcha vs Turnstile)
def test_c2a_hcaptcha_widget_only():
    assert verdict(403, {}, '<html><body><div class="h-captcha" data-sitekey="abc"></div><script src="https://js.hcaptcha.com/1/api.js"></script></body></html>') == ("CHALLENGED", "Generic")


def test_c2b_turnstile_widget_only():
    assert verdict(403, {}, '<html><body><div class="cf-turnstile" data-sitekey="abc"></div><script src="https://challenges.cloudflare.com/turnstile/v0/api.js"></script></body></html>') == ("CHALLENGED", "Cloudflare")


def test_c2c_turnstile_on_login_form_yields():
    assert verdict(200, {}, '<html><body><form action="/login"><input name="user"><input name="pass" type="password"><div class="cf-turnstile" data-sitekey="abc"></div><script src="https://challenges.cloudflare.com/turnstile/v0/api.js"></script></form></body></html>', LOGIN) == ("LOGIN_GATED", "Cloudflare")


def test_c2d_px_captcha_at_login_url():
    assert verdict(403, {}, '<html><body><form action="/login"><input name="user"></form><div class="px-captcha"></div></body></html>', LOGIN) == ("CHALLENGED", "PerimeterX")


# C3 — SVG / image-only challenge pages
def test_c3a_img_captcha_alt():
    assert verdict(403, {}, '<html><body><img src="/captcha.png" alt="captcha image"></body></html>') == ("CHALLENGED", "Generic")


def test_c3b_textless_svg_graphic():
    assert verdict(403, {}, '<html><body><svg xmlns="http://www.w3.org/2000/svg" width="300" height="100"><rect width="300" height="100" fill="#eee"/><circle cx="50" cy="50" r="30" fill="#333"/></svg></body></html>') == ("WALLED", None)


def test_c3c_svg_text_human_check():
    assert verdict(200, {}, '<html><body><svg xmlns="http://www.w3.org/2000/svg"><text x="10" y="20">Verify you are human</text></svg></body></html>') == ("CHALLENGED", "Generic")


# C4 — multi-language mixed pages
def test_c4a_en_es_mixed():
    assert verdict(403, {}, "<html><body><p>Verify you are human / Verifica que eres humano</p></body></html>") == ("CHALLENGED", "Generic")


def test_c4b_italian_only():
    assert verdict(403, {}, "<html><body><p>Verifica di essere umano. Non sono un robot.</p></body></html>") == ("CHALLENGED", "Generic")


def test_c4c_dutch_only():
    assert verdict(403, {}, "<html><body><p>Bevestig dat u geen robot bent. Ik ben geen robot.</p></body></html>") == ("CHALLENGED", "Generic")


def test_c4d_korean_only():
    assert verdict(403, {}, "<html><body><p>로봇이 아님을 확인하세요.</p></body></html>") == ("CHALLENGED", "Generic")


# C5 — status code + one header only
def test_c5a_403_cf_headers_only():
    assert verdict(403, {"cf-ray": "abc", "server": "cloudflare"}, "") == ("WALLED", "Cloudflare")


def test_c5b_403_unknown_vendor_header():
    assert verdict(403, {"x-sucuri-id": "123"}, "") == ("WALLED", None)


def test_c5c_429_retry_after_only():
    assert verdict(429, {"retry-after": "60"}, "") == ("RATE_LIMITED", None)


def test_c5d_503_cf_ray_only():
    assert verdict(503, {"cf-ray": "abc"}, "") == ("UNREACHABLE", None)


# C6 — login pages with an embedded captcha widget
def test_c6a_recaptcha_loader_on_login():
    assert verdict(200, {}, '<html><body><form action="/login"><input name="user"><input name="pass" type="password"><script src="https://www.google.com/recaptcha/api.js"></script></form></body></html>', LOGIN) == ("LOGIN_GATED", None)


def test_c6b_hcaptcha_widget_plus_prose_on_login():
    assert verdict(200, {}, '<html><body><form action="/login"><input name="user"><input name="pass" type="password"><div class="h-captcha"></div><p>verify you are human to sign in</p></form></body></html>', LOGIN) == ("LOGIN_GATED", None)


# C7 — sitemap INDEX files (audit tool)
def test_c7a_sitemapindex_passes():
    assert audit_check(sitemap_records('<?xml version="1.0"?><sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><sitemap><loc>https://x.example/s1.xml</loc></sitemap></sitemapindex>'), "sitemap") == "PASS"


def test_c7b_sitemapindex_dead_children_still_pass():
    assert audit_check(sitemap_records('<?xml version="1.0"?><sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><sitemap><loc>https://x.example/dead.xml</loc></sitemap></sitemapindex>'), "sitemap") == "PASS"


def test_c7c_redirected_sitemap_urlset_passes():
    assert audit_check(sitemap_records('<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://x.example/</loc></url></urlset>'), "sitemap") == "PASS"


# C8 — robots.txt subtleties (audit tool)
def test_c8a_crawl_delay_only_passes():
    assert audit_check(robots_records("User-agent: *\nCrawl-delay: 10\n"), "robots_txt") == "PASS"


def test_c8b_wildcard_block_with_gptbot_carveout_warns():
    assert audit_check(robots_records("User-agent: *\nDisallow: /\n\nUser-agent: GPTBot\nAllow: /\n"), "robots_txt") == "WARN"


def test_c8c_wildcard_block_with_restricted_agent_warns():
    assert audit_check(robots_records("User-agent: *\nDisallow: /\n\nUser-agent: ClaudeBot\nDisallow: /private\n"), "robots_txt") == "WARN"


def test_c8d_crawl_delay_plus_sitemap_declared_passes():
    assert audit_check(robots_records("User-agent: *\nCrawl-delay: 10\nSitemap: https://x.example/sitemap.xml\n"), "robots_txt") == "PASS"


def test_c8e_lowercase_agent_restricted_warns():
    assert audit_check(robots_records("user-agent: gptbot\nDisallow: /private\n"), "robots_txt") == "WARN"


def test_c8f_empty_disallow_passes():
    assert audit_check(robots_records("User-agent: *\nDisallow:\n"), "robots_txt") == "PASS"


def test_c8g_named_group_first_still_warns():
    assert audit_check(robots_records("User-agent: GPTBot\nDisallow: /private\n\nUser-agent: *\nDisallow: /\n"), "robots_txt") == "WARN"
