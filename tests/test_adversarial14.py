"""Wave 22 battery v14 regression pins (see validation/wave22/
HANDCLASS-14.md for the hand classifications). Shapes: SVG
<title>/<desc> metadata, HTTP 451 variants, "Continue with SSO"
prompts, robots.txt stray rules and Crawl-delay, llms.txt BOM+CRLF
composition, sitemap index composition, challenge phrases in
Gujarati/Kannada/Nepali/Khmer, and og:description-only challenge
phrases.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from wallcheck.classify import classify  # noqa: E402
from wallcheck.audit import evaluate_audit  # noqa: E402

LOGIN = "https://site.example/login"
BIG_ARTICLE = "<article>" + ("<p>Real article text about web "
               "infrastructure and the history of the open web, "
               "written in full sentences for readers. </p>" * 170) \
    + "</article>"  # > 16 KB served-page gate, by construction
LEGAL_NOTICE = "<p>Access to this resource is restricted in your " \
    "jurisdiction under applicable law. This notice explains the " \
    "legal basis for the restriction, the categories of content " \
    "affected, and the process by which you may request review " \
    "of this determination from the site operator. </p>"
LONG_LEGAL = "<html><body>" + LEGAL_NOTICE * 12 + "</body></html>"


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
    return [c for c in out["checks"] if c["check"] == name][0]


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


# --- P1: SVG title/desc metadata ---
def test_p1a_svg_title_only_is_challenge():
    assert verdict(200, body='<html><body><svg><title>Verify you are human</title><rect width="10" height="10"/></svg></body></html>') == ("CHALLENGED", "Generic")


def test_p1b_svg_title_on_article_is_open():
    assert verdict(200, body=BIG_ARTICLE + '<svg><title>Verify you are human</title></svg>') == ("OPEN", None)


def test_p1c_svg_title_with_real_paragraph_is_open():
    assert verdict(200, body='<html><body><p>A short real paragraph about the history of the open web and how it grew.</p><svg><title>Verify you are human</title></svg></body></html>') == ("OPEN", None)


def test_p1d_svg_desc_only_is_challenge():
    assert verdict(200, body='<html><body><svg><desc>Verify you are human</desc><rect width="10" height="10"/></svg></body></html>') == ("CHALLENGED", "Generic")


# --- P2: HTTP 451 variants ---
def test_p2a_451_long_legal_notice_is_walled():
    assert verdict(451, body=LONG_LEGAL) == ("WALLED", None)


def test_p2b_451_empty_body_is_walled():
    assert verdict(451, body="") == ("WALLED", None)


def test_p2c_451_challenge_phrase_body_is_walled():
    # Verdict governs (451 refusal beats presented challenge text);
    # the Generic vendor cell records that the refusal body also
    # carries a generic human-check phrase — body evidence, not a
    # re-attribution of the refusal itself.
    assert verdict(451, body="<html><body><p>Verify you are human</p></body></html>") == ("WALLED", "Generic")


# --- P3: SSO-continue prompts ---
def test_p3a_sso_button_is_login_gated():
    assert verdict(200, body='<html><body><p>Sign in to continue.</p><button>Continue with SSO</button></body></html>') == ("LOGIN_GATED", None)


def test_p3b_sso_button_on_article_is_open():
    assert verdict(200, body=BIG_ARTICLE + '<button>Continue with SSO</button>') == ("OPEN", None)


def test_p3c_sso_script_filename_is_open():
    assert verdict(200, body=BIG_ARTICLE + '<script src="/static/sso.js"></script>') == ("OPEN", None)


def test_p3d_sso_stylesheet_class_is_open():
    assert verdict(200, body=BIG_ARTICLE + '<style>.sso-button { color: blue; }</style>') == ("OPEN", None)


def test_p3e_sso_wording_without_button_is_open():
    assert verdict(200, body='<html><body><p>Our platform supports SSO for enterprise customers.</p></body></html>') == ("OPEN", None)


def test_p3f_sso_button_with_short_paragraph_is_login_gated():
    assert verdict(200, body='<html><body><p>Sign in with your company account to continue.</p><button>Continue with SSO</button></body></html>') == ("LOGIN_GATED", None)


# --- P4: robots.txt stray rules and Crawl-delay ---
def test_p4a_stray_rule_before_first_group_is_pass():
    r = base_records(robots=rec(200, body="Disallow: /private\nUser-agent: *\nAllow: /\n"))
    assert audit_check(r, "robots_txt")["status"] == "PASS"


def test_p4b_crawl_delay_with_disallow_is_fail():
    r = base_records(robots=rec(200, body="User-agent: *\nDisallow: /\nCrawl-delay: 10\n"))
    assert audit_check(r, "robots_txt")["status"] == "FAIL"


# --- P5: llms.txt BOM + CRLF composition ---
def test_p5a_bom_crlf_index_is_pass():
    body = "\ufeff# Index\r\n\r\n- [Docs](https://x.example/docs)\r\n- [Guide](https://x.example/guide)\r\n"
    r = base_records(llms=rec(200, body=body))
    assert audit_check(r, "llms_txt")["status"] == "PASS"


def test_p5b_bom_crlf_frontmatter_only_is_warn():
    body = "\ufeff---\r\ntitle: Site\r\nurl: https://x.example/\r\n---\r\n"
    r = base_records(llms=rec(200, body=body))
    assert audit_check(r, "llms_txt")["status"] == "WARN"


def test_p5c_crlf_index_is_pass():
    body = "# Index\r\n\r\n- [Docs](https://x.example/docs)\r\n"
    r = base_records(llms=rec(200, body=body))
    assert audit_check(r, "llms_txt")["status"] == "PASS"


# --- P6: sitemap index composition ---
def test_p6a_empty_sitemapindex_is_warn():
    body = '<?xml version="1.0" encoding="UTF-8"?><sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"></sitemapindex>'
    r = base_records(sitemap=rec(200, body=body))
    assert audit_check(r, "sitemap")["status"] == "WARN"


def test_p6b_lastmod_only_urlset_is_warn():
    body = '<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><lastmod>2026-01-01</lastmod></url></urlset>'
    r = base_records(sitemap=rec(200, body=body))
    assert audit_check(r, "sitemap")["status"] == "WARN"


def test_p6c_nested_sitemapindex_is_pass():
    body = '<?xml version="1.0"?><sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><sitemap><loc>https://x.example/sitemap-1.xml</loc></sitemap></sitemapindex>'
    r = base_records(sitemap=rec(200, body=body))
    assert audit_check(r, "sitemap")["status"] == "PASS"


# --- P7: GU/KN/NE/KM challenge phrases ---
def test_p7a_gujarati_phrase_is_challenge():
    assert verdict(200, body='<html><body><p>તમે રોબોટ નથી તેની ખાતરી કરો</p></body></html>') == ("CHALLENGED", "Generic")


def test_p7b_kannada_phrase_is_challenge():
    assert verdict(200, body='<html><body><p>ನೀವು ರೋಬೋಟ್ ಅಲ್ಲ ಎಂದು ಖಚಿತಪಡಿಸಿ</p></body></html>') == ("CHALLENGED", "Generic")


def test_p7c_nepali_phrase_is_challenge():
    assert verdict(200, body='<html><body><p>तपाईं रोबोट होइन भनेर पुष्टि गर्नुहोस्</p></body></html>') == ("CHALLENGED", "Generic")


def test_p7d_khmer_phrase_is_challenge():
    assert verdict(200, body='<html><body><p>បញ្ជាក់ថាអ្នកមិនមែនជាមនុស្សយន្ត</p></body></html>') == ("CHALLENGED", "Generic")


def test_p7e_gujarati_phrase_on_article_is_open():
    assert verdict(200, body=BIG_ARTICLE + "<p>તમે રોબોટ નથી તેની ખાતરી કરો</p>") == ("OPEN", None)


def test_p7f_gujarati_fragment_is_open():
    assert verdict(200, body='<html><body><p>રોબોટ</p></body></html>') == ("OPEN", None)


# --- P8: og:description-only challenge phrases ---
def test_p8a_og_description_only_is_challenge():
    assert verdict(200, body='<html><head><meta property="og:description" content="Verify you are human"></head><body></body></html>') == ("CHALLENGED", "Generic")


def test_p8b_og_description_on_article_is_open():
    assert verdict(200, body='<html><head><meta property="og:description" content="Verify you are human"></head><body>' + BIG_ARTICLE + '</body></html>') == ("OPEN", None)


def test_p8c_og_description_with_real_paragraph_is_open():
    assert verdict(200, body='<html><head><meta property="og:description" content="Verify you are human"></head><body><p>A short real paragraph about the history of the open web.</p></body></html>') == ("OPEN", None)
