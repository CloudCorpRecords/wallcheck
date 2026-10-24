"""Wave 15 battery v7 regression pins (see validation/wave15/
HANDCLASS-7.md for the hand classifications). Shapes: JSON-LD
markers, access-denied variants, SVG tspan-split phrases, hCaptcha
enterprise/invisible widgets, Refresh-header routing, 2FA-first
login walls, article + footer badges, robots Allow tiebreaks,
llms YAML frontmatter, lastmod-only sitemaps. Plus guards for each
fix's blast radius.
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


def llms_records(body):
    return {
        "robots": rec(200, {"Content-Type": "text/plain"},
                      "User-agent: *\nAllow: /\n"),
        "llms": rec(200, {"Content-Type": "text/plain"}, body),
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
assert len(ARTICLE) > 16384
SHORT_ARTICLE = ("<html><body><p>Our team ships every Friday and "
                 "writes about the process in detail here.</p></body></html>")
LOGIN_2FA = ('<html><body><form action="/verify" method="post">'
             '<label>Enter your 6-digit verification code</label>'
             '<input type="text" name="otp" maxlength="6">'
             '<button>Verify</button></form></body></html>')


# G1 — JSON-LD blocks
def test_g1a_jsonld_generic_with_visible_text():
    assert verdict(200, {}, '<html><body><p>Our team ships every Friday and writes about the process in detail here.</p><script type="application/ld+json">{"@type": "Article", "description": "Verify you are human to access this article"}</script></body></html>') == ("OPEN", None)


def test_g1b_jsonld_only_challenge():
    assert verdict(200, {}, '<html><body><script type="application/ld+json">{"@type": "WebPage", "text": "Verify you are human to continue"}</script></body></html>') == ("CHALLENGED", "Generic")


def test_g1c_jsonld_vendor_with_visible_text():
    # W15-001: vendor names in JSON-LD metadata are not fired walls.
    assert verdict(200, {}, '<html><body><p>Our team ships every Friday and writes about the process in detail here.</p><script type="application/ld+json">{"@type": "Article", "description": "An analysis of perimeterx and modern bot detection"}</script></body></html>') == ("OPEN", None)


def test_g1d_jsonld_only_vendor():
    assert verdict(200, {}, '<html><body><script type="application/ld+json">{"@type": "WebPage", "description": "perimeterx"}</script></body></html>') == ("CHALLENGED", "PerimeterX")


def test_guard_regular_script_vendor_still_fires():
    # Loader scripts are load-bearing: only ld+json is stripped.
    assert verdict(200, {}, '<html><body><p>Our team ships every Friday and writes about the process in detail here.</p><script src="https://example.com/px.js"></script><p>perimeterx</p></body></html>') == ("CHALLENGED", "PerimeterX")


# G2 — access-denied variants
def test_g2a_200_access_denied_stub():
    # W15-002: a small refusal page is a wall, not served content.
    assert verdict(200, {}, "<html><body><p>Access denied.</p></body></html>") == ("WALLED", None)


def test_g2b_403_access_denied():
    assert verdict(403, {}, "<html><body><p>Access denied.</p></body></html>") == ("WALLED", None)


def test_g2c_401_access_denied_keeps_auth():
    assert verdict(401, {}, "<html><body><p>Access denied.</p></body></html>") == ("LOGIN_GATED", None)


def test_g2d_article_mentioning_access_denied():
    assert verdict(200, {}, "<html><head><title>On permission errors</title></head><body>" + ARTICLE.replace("verification and bot detection", "access denied errors and permission models") + "</body></html>") == ("OPEN", None)


def test_g2e_503_access_denied_keeps_unreachable():
    assert verdict(503, {}, "<html><body><p>Access denied.</p></body></html>") == ("UNREACHABLE", None)


def test_guard_login_url_access_denied_is_refusal():
    # The refusal branch precedes the login heuristic: a login page
    # saying only "Access denied" refuses, it does not gate.
    assert verdict(200, {}, "<html><body><p>Access denied.</p></body></html>", url=LOGIN) == ("WALLED", None)


# G3 — SVG text
def test_g3a_svg_contiguous_challenge():
    assert verdict(403, {}, '<html><body><svg><text>Verify you are human</text></svg></body></html>') == ("CHALLENGED", "Generic")


def test_g3b_svg_tspan_split_challenge():
    # W15-003: rendered text is what matters; tags must not split it.
    assert verdict(403, {}, '<html><body><svg><text><tspan>Verify you</tspan><tspan> are human</tspan></text></svg></body></html>') == ("CHALLENGED", "Generic")


def test_g3c_article_svg_text():
    assert verdict(200, {}, "<html><body>" + ARTICLE + '<svg><text>verify you are human</text></svg></body></html>') == ("OPEN", None)


def test_guard_split_non_challenge_text():
    assert verdict(403, {}, '<html><body><svg><text><tspan>Verify your</tspan><tspan> email address</tspan></text></svg></body></html>') == ("WALLED", None)


def test_guard_js_proof_split_across_tspans():
    # W15-003 extends to JS_PROOF phrases by the same principle.
    assert verdict(200, {}, '<html><body><svg><text><tspan>Verifying your</tspan><tspan> browser</tspan></text></svg></body></html>') == ("CHALLENGED", "Generic")


# G4 — hCaptcha enterprise / invisible widgets
def test_g4a_enterprise_widget_only():
    assert verdict(403, {}, '<html><body><div class="h-captcha" data-sitekey="abc"></div><script src="https://js.hcaptcha.com/1/api.js?render=explicit"></script></body></html>') == ("CHALLENGED", "Generic")


def test_g4b_widget_on_login_form():
    assert verdict(200, {}, '<html><body><form action="/session" method="post"><input type="password" name="pw"><div class="h-captcha" data-sitekey="abc"></div><button>Sign in</button></form></body></html>', url=LOGIN) == ("LOGIN_GATED", None)


def test_g4c_invisible_widget_with_visible_text():
    # W15-004: an invisible widget presents nothing to the reader.
    assert verdict(200, {}, '<html><body><p>Our team ships every Friday and writes about the process in detail here.</p><div class="h-captcha" data-sitekey="abc" data-size="invisible"></div></body></html>') == ("OPEN", None)


def test_g4d_invisible_widget_only():
    assert verdict(403, {}, '<html><body><div class="h-captcha" data-sitekey="abc" data-size="invisible"></div></body></html>') == ("CHALLENGED", "Generic")


def test_guard_visible_widget_with_visible_text_still_fires():
    assert verdict(200, {}, '<html><body><p>Our team ships every Friday and writes about the process in detail here.</p><div class="h-captcha" data-sitekey="abc"></div></body></html>') == ("CHALLENGED", "Generic")


# G5 — Refresh header
def test_g5a_refresh_to_challenge():
    # W15-005: the header form of a meta refresh.
    assert verdict(200, {"Refresh": "0; url=/challenge/verify"}, "<html><body></body></html>") == ("CHALLENGED", "Generic")


def test_g5b_refresh_to_login():
    assert verdict(200, {"Refresh": "0; url=/login"}, "<html><body></body></html>") == ("LOGIN_GATED", None)


def test_g5c_refresh_to_content():
    assert verdict(200, {"Refresh": "0; url=/home"}, "<html><body></body></html>") == ("OPEN", None)


def test_g5d_refresh_on_served_article():
    assert verdict(200, {"Refresh": "0; url=/challenge/verify"}, ARTICLE) == ("OPEN", None)


def test_guard_refresh_delay_only():
    assert verdict(200, {"Refresh": "5"}, "<html><body><p>Content.</p></body></html>") == ("OPEN", None)


# G6 — 2FA first screens
def test_g6a_2fa_on_login_url():
    assert verdict(200, {}, LOGIN_2FA, url=LOGIN) == ("LOGIN_GATED", None)


def test_g6b_2fa_plus_human_check_prose_on_login():
    assert verdict(200, {}, '<html><body><p>Please verify you are human, then enter your code.</p>' + LOGIN_2FA + '</body></html>', url=LOGIN) == ("LOGIN_GATED", None)


def test_g6c_2fa_form_off_login_url():
    # W15-006: a code-entry form is an auth barrier wherever it sits.
    assert verdict(200, {}, LOGIN_2FA, url="https://site.example/verify-2fa") == ("LOGIN_GATED", None)


def test_g6d_fired_wall_at_login_with_2fa():
    assert verdict(403, {"cf-ray": "abc123", "cf-mitigated": "challenge"}, "<html><body><h1>Just a moment</h1>" + LOGIN_2FA + "</body></html>", url=LOGIN) == ("CHALLENGED", "Cloudflare")


def test_guard_discount_code_form_is_not_login():
    # Neither key alone fires: a promo code is not an auth barrier.
    assert verdict(200, {}, '<html><body><form action="/apply" method="post"><label>Enter your discount code</label><input type="text" name="promo_code"><button>Apply</button></form></body></html>') == ("OPEN", None)


def test_guard_code_input_without_auth_wording():
    assert verdict(200, {}, '<html><body><form action="/go" method="post"><label>Enter the code below</label><input type="text" name="otp"><button>Go</button></form></body></html>') == ("OPEN", None)


# G7 — article + footer badge
def test_g7a_large_article_footer_badge():
    assert verdict(200, {}, ARTICLE + "<footer>This site is protected by PerimeterX</footer></html>") == ("OPEN", None)


def test_g7b_small_article_footer_badge():
    # W15-007: a badge on served content is furniture, not a wall.
    assert verdict(200, {}, SHORT_ARTICLE + "<footer>This site is protected by PerimeterX</footer></html>") == ("OPEN", None)


def test_g7c_badge_only_page():
    assert verdict(200, {}, "<html><body><footer>Protected by DataDome</footer></body></html>") == ("OPEN", None)


def test_guard_error_page_badge_keeps_vendor():
    # Badge stripping is 2xx-only: a deny page keeps attribution.
    assert verdict(403, {}, "<html><body><p>Access denied.</p><footer>This site is protected by PerimeterX</footer></body></html>") == ("WALLED", "PerimeterX")


# G8 — robots Allow tiebreaks
def test_g8a_allow_all_plus_private_disallow():
    assert audit_check(robots_records("User-agent: *\nAllow: /\nDisallow: /private\n"), "robots_txt") == "WARN"


def test_g8b_allow_only():
    assert audit_check(robots_records("User-agent: *\nAllow: /\n"), "robots_txt") == "PASS"


def test_g8c_named_allow_vs_wildcard_disallow():
    assert audit_check(robots_records("User-agent: *\nDisallow: /private\n\nUser-agent: GPTBot\nAllow: /\n"), "robots_txt") == "WARN"


def test_g8d_allow_disallow_root_tie():
    # W15-008: RFC 9309 — an equally specific Allow wins the tie.
    assert audit_check(robots_records("User-agent: *\nDisallow: /\nAllow: /\n"), "robots_txt") == "PASS"


def test_guard_partial_allow_softens_block_to_restricted():
    # Disallow: / + Allow: /images = partial access, not a block.
    assert audit_check(robots_records("User-agent: *\nDisallow: /\nAllow: /images\n"), "robots_txt") == "WARN"


# G9 — llms frontmatter
def test_g9a_frontmatter_plus_index():
    assert audit_check(llms_records("---\ntitle: Example Site\ndate: 2026-01-01\n---\n\n# Docs\n\n- [Guide](/guide)\n- [API](/api)\n"), "llms_txt") == "PASS"


def test_g9b_frontmatter_only_with_url_field():
    # W15-009: metadata URLs are not index entries.
    assert audit_check(llms_records("---\ntitle: Example Site\nurl: https://x.example\n---\n"), "llms_txt") == "WARN"


def test_g9c_frontmatter_plus_one_link():
    # W15-009 refinement: a link is usable content however short.
    assert audit_check(llms_records("---\ntitle: Example Site\n---\n\n- [Docs](/docs)\n"), "llms_txt") == "PASS"


def test_g9d_frontmatter_link_only():
    assert audit_check(llms_records("---\ntitle: Example Site\ndescription: See [the guide](/guide) for details.\n---\n"), "llms_txt") == "WARN"


def test_guard_unclosed_frontmatter_not_stripped():
    # No closing --- means no frontmatter: the link still counts.
    assert audit_check(llms_records("---\ntitle: Example Site\n- [Docs](/docs)\n"), "llms_txt") == "PASS"


# G10 — lastmod-only sitemaps
def test_g10a_urlset_lastmod_only():
    # W15-010: a sitemap naming no URLs is not a usable sitemap.
    assert audit_check(sitemap_records('<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><lastmod>2026-01-01</lastmod></url><url><lastmod>2026-01-02</lastmod></url></urlset>'), "sitemap") == "WARN"


def test_g10b_urlset_loc_plus_lastmod():
    assert audit_check(sitemap_records('<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://x.example/</loc><lastmod>2026-01-01</lastmod></url></urlset>'), "sitemap") == "PASS"


def test_g10c_sitemapindex_lastmod_only():
    assert audit_check(sitemap_records('<?xml version="1.0"?><sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><sitemap><lastmod>2026-01-01</lastmod></sitemap></sitemapindex>'), "sitemap") == "WARN"


def test_g10d_one_loc_among_lastmod_only():
    assert audit_check(sitemap_records('<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://x.example/</loc></url><url><lastmod>2026-01-01</lastmod></url></urlset>'), "sitemap") == "PASS"


def test_guard_bare_xml_prolog_is_not_a_sitemap():
    # Blast radius of W15-010: a prolog alone names no URLs.
    assert audit_check(sitemap_records('<?xml version="1.0"?>'), "sitemap") == "WARN"
