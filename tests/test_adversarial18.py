"""Wave 26 battery v18 regression pins (see validation/wave26/
HANDCLASS-18.md for the hand classifications). Shapes: challenge
markers only in <label> elements, HTTP 451 responses carrying a
Retry-After header, login walls asking the user to tap an ID
badge, robots.txt User-agent values carrying trailing spaces,
llms.txt mixing LF and CRLF line endings in the same file,
sitemap.xml <loc> entries with percent-encoded hosts, challenge
phrases in Catalan/Estonian/Armenian/Georgian, and challenge
phrases only as the text of a <button>.
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
PARA = ("<p>A short real paragraph about the history of the open "
        "web and how it grew from a research network into the "
        "public infrastructure it is today.</p>")

CA_PHRASE = "Confirma que no ets un robot"
ET_PHRASE = "Kinnitage, et te ei ole robot"
HY_PHRASE = "Հաստատեք, որ ռոբոտ չեք"
KA_PHRASE = "დაადასტურეთ, რომ რობოტი არ ხართ"

BADGE_PAGE = ("<html><body><h1>Sign in</h1>"
              "<p>Tap your badge on the reader to sign in.</p>"
              "<button>Try again</button></body></html>")


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


# ------------------------------------------------------------ U1 label

def test_u1a_label_only_phrase_challenged():
    body = ("<html><body><label for=\"cb\">Verify you are human"
            "</label><input type=\"checkbox\" id=\"cb\">"
            "</body></html>")
    assert verdict(200, body=body) == ("CHALLENGED", "Generic")


def test_u1b_paragraph_plus_label_phrase_challenged():
    body = "<html><body>" + PARA + \
        "<label>Verify you are human</label></body></html>"
    assert verdict(200, body=body) == ("CHALLENGED", "Generic")


def test_u1c_big_article_label_phrase_open():
    body = "<html><body>" + BIG_ARTICLE + \
        "<label>Verify you are human</label></body></html>"
    assert verdict(200, body=body) == ("OPEN", None)


def test_u1d_403_label_only_phrase_challenged():
    body = ("<html><body><label>Verify you are human</label>"
            "</body></html>")
    assert verdict(403, body=body) == ("CHALLENGED", "Generic")


def test_u1e_label_no_phrase_open():
    body = ("<html><body><label>Your email address</label>"
            "<input type=\"email\" name=\"email\"></body></html>")
    assert verdict(200, body=body) == ("OPEN", None)


# ------------------------------------------------------------ U2 451+Retry-After

def test_u2a_451_retry_after_legal_notice_walled():
    body = ("<html><body><p>This content is unavailable for legal "
            "reasons in your region.</p></body></html>")
    assert verdict(451, headers={"Retry-After": "3600"}, body=body) == \
        ("WALLED", None)


def test_u2b_451_retry_after_throttle_wording_walled():
    body = ("<html><body><p>This content is unavailable for legal "
            "reasons in your region, and a rate limit is in effect "
            "for this resource.</p></body></html>")
    assert verdict(451, headers={"Retry-After": "120"}, body=body) == \
        ("WALLED", None)


def test_u2c_451_retry_after_challenge_phrase_walled_generic():
    body = "<html><body><p>Verify you are human to continue.</p></body></html>"
    assert verdict(451, headers={"Retry-After": "3600"}, body=body) == \
        ("WALLED", "Generic")


def test_u2d_451_no_retry_after_walled():
    body = ("<html><body><p>This content is unavailable for legal "
            "reasons in your region.</p></body></html>")
    assert verdict(451, body=body) == ("WALLED", None)


# ------------------------------------------------------------ U3 badge tap

def test_u3a_badge_tap_prompt_login_gated():
    assert verdict(200, body=BADGE_PAGE) == ("LOGIN_GATED", None)


def test_u3b_badge_tap_in_big_article_open():
    body = "<html><body>" + BIG_ARTICLE + BADGE_PAGE + "</body></html>"
    assert verdict(200, body=body) == ("OPEN", None)


def test_u3c_badge_asset_filename_open():
    body = ("<html><body>" + PARA +
            "<script src=\"/js/badge-tap.js\"></script>"
            "</body></html>")
    assert verdict(200, body=body) == ("OPEN", None)


def test_u3d_badge_stylesheet_class_open():
    body = ("<html><body>" + PARA +
            "<style>.badge-tap-prompt{border:0}</style>"
            "</body></html>")
    assert verdict(200, body=body) == ("OPEN", None)


def test_u3e_badge_prose_no_machinery_open():
    body = ("<html><body><p>Building access: tap your badge on "
            "the reader by the door. If the light stays red, see "
            "the front desk.</p></body></html>")
    assert verdict(200, body=body) == ("OPEN", None)


def test_u3f_badge_tap_at_login_url_login_gated():
    assert verdict(200, body=BADGE_PAGE, url=LOGIN) == \
        ("LOGIN_GATED", None)


def test_u3g_badge_script_string_open():
    body = ("<html><body>" + PARA +
            "<form><button type=\"button\">Cancel</button></form>"
            "<script>var hint = \"tap your badge\";</script>"
            "</body></html>")
    assert verdict(200, body=body) == ("OPEN", None)


# ------------------------------------------------------------ U4 robots UA spaces

def robots_grade(text):
    records = base_records(robots=rec(200, body=text))
    return audit_check(records, "robots_txt")["status"]


def test_u4a_trailing_space_named_agent_warn():
    assert robots_grade("User-agent: GPTBot   \nDisallow: /\n") == "WARN"


def test_u4b_all_agents_trailing_spaces_fail():
    text = ("User-agent: GPTBot  \nDisallow: /\n"
            "User-agent: ClaudeBot \nDisallow: /\n"
            "User-agent: CCBot    \nDisallow: /\n"
            "User-agent: Google-Extended \nDisallow: /\n")
    assert robots_grade(text) == "FAIL"


def test_u4c_wildcard_trailing_space_fail():
    assert robots_grade("User-agent: *  \nDisallow: /\n") == "FAIL"


def test_u4d_trailing_space_agent_allowed_pass():
    assert robots_grade("User-agent: GPTBot  \nAllow: /\n") == "PASS"


def test_u4e_disallow_value_trailing_space_fail():
    assert robots_grade("User-agent: *\nDisallow: /  \n") == "FAIL"


# ------------------------------------------------------------ U5 llms mixed endings

def llms_grade(body):
    records = base_records(llms=rec(200, body=body))
    return audit_check(records, "llms_txt")["status"]


def test_u5a_crlf_frontmatter_lf_body_pass():
    body = ("---\r\ntitle: Site Guide\r\n---\r\n"
            "# Site Guide\n- [Docs](/docs)\n")
    assert llms_grade(body) == "PASS"


def test_u5b_lf_frontmatter_crlf_body_pass():
    body = ("---\ntitle: Site Guide\n---\n"
            "# Site Guide\r\n- [Docs](/docs)\r\n")
    assert llms_grade(body) == "PASS"


def test_u5c_mixed_endings_frontmatter_only_warn():
    body = ("---\r\ntitle: Site Guide\n"
            "sitemap: https://example.com/sitemap.xml\r\n---\n")
    assert llms_grade(body) == "WARN"


def test_u5d_mixed_endings_no_links_warn():
    body = "# Site Guide\r\nAll about this site and its history.\n"
    assert llms_grade(body) == "WARN"


# ------------------------------------------------------------ U6 sitemap pct hosts

def sitemap_grade(body):
    records = base_records(sitemap=rec(200, body=body))
    return audit_check(records, "sitemap")["status"]


def test_u6a_pct_encoded_path_pass():
    body = ("<?xml version=\"1.0\"?><urlset>"
            "<url><loc>https://example.com/%70age</loc></url>"
            "</urlset>")
    assert sitemap_grade(body) == "PASS"


def test_u6b_pct_host_plus_good_loc_pass():
    body = ("<?xml version=\"1.0\"?><urlset>"
            "<url><loc>https://%65xample.com/a</loc></url>"
            "<url><loc>https://example.com/b</loc></url>"
            "</urlset>")
    assert sitemap_grade(body) == "PASS"


def test_u6c_pct_encoded_host_only_warn():
    body = ("<?xml version=\"1.0\"?><urlset>"
            "<url><loc>https://%65xample.com/a</loc></url>"
            "</urlset>")
    assert sitemap_grade(body) == "WARN"


def test_u6d_all_pct_encoded_hosts_warn():
    body = ("<?xml version=\"1.0\"?><urlset>"
            "<url><loc>https://example%2Ecom/a</loc></url>"
            "<url><loc>https://%65xample.com/b</loc></url>"
            "</urlset>")
    assert sitemap_grade(body) == "WARN"


# ------------------------------------------------------------ U7 languages

def test_u7a_catalan_phrase_challenged():
    body = "<html><body><p>" + CA_PHRASE + "</p></body></html>"
    assert verdict(403, body=body) == ("CHALLENGED", "Generic")


def test_u7b_estonian_phrase_challenged():
    body = "<html><body><p>" + ET_PHRASE + "</p></body></html>"
    assert verdict(403, body=body) == ("CHALLENGED", "Generic")


def test_u7c_armenian_phrase_challenged():
    body = "<html><body><p>" + HY_PHRASE + "</p></body></html>"
    assert verdict(403, body=body) == ("CHALLENGED", "Generic")


def test_u7d_georgian_phrase_challenged():
    body = "<html><body><p>" + KA_PHRASE + "</p></body></html>"
    assert verdict(403, body=body) == ("CHALLENGED", "Generic")


def test_u7e_estonian_phrase_big_article_open():
    body = "<html><body>" + BIG_ARTICLE + "<p>" + ET_PHRASE + \
        "</p></body></html>"
    assert verdict(200, body=body) == ("OPEN", None)


def test_u7f_fragment_open():
    body = "<html><body><p>robot</p></body></html>"
    assert verdict(200, body=body) == ("OPEN", None)


def test_u7g_armenian_phrase_in_style_open():
    body = ("<html><body>" + PARA + "<style>.x{content:\"" +
            HY_PHRASE + "\"}</style></body></html>")
    assert verdict(200, body=body) == ("OPEN", None)


# ------------------------------------------------------------ U8 button text

def test_u8a_button_only_phrase_challenged():
    body = ("<html><body><button>Verify you are human</button>"
            "</body></html>")
    assert verdict(200, body=body) == ("CHALLENGED", "Generic")


def test_u8b_paragraph_plus_button_phrase_challenged():
    body = "<html><body>" + PARA + \
        "<button>Verify you are human</button></body></html>"
    assert verdict(200, body=body) == ("CHALLENGED", "Generic")


def test_u8c_big_article_button_phrase_open():
    body = "<html><body>" + BIG_ARTICLE + \
        "<button>Verify you are human</button></body></html>"
    assert verdict(200, body=body) == ("OPEN", None)


def test_u8d_403_button_phrase_challenged():
    body = "<html><body>" + PARA + \
        "<button>Verify you are human</button></body></html>"
    assert verdict(403, body=body) == ("CHALLENGED", "Generic")


def test_u8e_button_no_phrase_open():
    body = ("<html><body><button>Continue</button></body></html>")
    assert verdict(200, body=body) == ("OPEN", None)
