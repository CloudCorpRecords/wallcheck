"""Wave 27 battery v19 regression pins (see validation/wave27/
HANDCLASS-19.md for the hand classifications). Shapes: challenge
markers only in table cells, HTTP 307 redirects to a maintenance
page, login walls asking for a fingerprint, robots.txt
product-token groups carrying a version, llms.txt whose only
links live inside an HTML comment, sitemap.xml <loc> entries
that are IP literals, challenge phrases in Albanian/Icelandic/
Kazakh/Malayalam, and challenges presented as toast
notifications.
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

SQ_PHRASE = "Konfirmoni që nuk jeni robot"
SQ_CHECKBOX = "Unë nuk jam një robot"
IS_PHRASE = "Staðfestu að þú sért ekki vélmenni"
IS_CHECKBOX = "Ég er ekki vélmenni"
KK_PHRASE = "Робот емес екеніңізді растаңыз"
KK_CHECKBOX = "Мен робот емеспін"
ML_PHRASE = "നിങ്ങൾ ഒരു റോബോട്ട് അല്ലെന്ന് സ്ഥിരീകരിക്കുക"
ML_CHECKBOX = "ഞാൻ ഒരു റോബോട്ട് അല്ല"

MAINTENANCE = ("<html><body><h1>Scheduled maintenance</h1>"
               "<p>We will be back soon.</p></body></html>")
BIOMETRIC_PAGE = ("<html><body><h1>Sign in</h1>"
                  "<p>Use your fingerprint to sign in.</p>"
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


def robots_grade(text):
    records = base_records(robots=rec(200, body=text))
    return audit_check(records, "robots_txt")["status"]


def llms_grade(body):
    records = base_records(llms=rec(200, body=body))
    return audit_check(records, "llms_txt")["status"]


def sitemap_grade(body):
    records = base_records(sitemap=rec(200, body=body))
    return audit_check(records, "sitemap")["status"]


# ------------------------------------------------------------ V1 table cells

def test_v1a_td_only_phrase_challenged():
    body = ("<html><body><table><tr><td>Verify you are human</td>"
            "</tr></table></body></html>")
    assert verdict(200, body=body) == ("CHALLENGED", "Generic")


def test_v1b_paragraph_plus_th_phrase_challenged():
    body = "<html><body>" + PARA + \
        "<table><tr><th>Verify you are human</th></tr></table>" \
        "</body></html>"
    assert verdict(200, body=body) == ("CHALLENGED", "Generic")


def test_v1c_big_article_td_phrase_open():
    body = "<html><body>" + BIG_ARTICLE + \
        "<table><tr><td>Verify you are human</td></tr></table>" \
        "</body></html>"
    assert verdict(200, body=body) == ("OPEN", None)


def test_v1d_403_td_only_phrase_challenged():
    body = ("<html><body><table><tr><td>Verify you are human</td>"
            "</tr></table></body></html>")
    assert verdict(403, body=body) == ("CHALLENGED", "Generic")


def test_v1e_table_no_phrase_open():
    body = ("<html><body><table><tr><td>Quarterly revenue "
            "results</td></tr></table></body></html>")
    assert verdict(200, body=body) == ("OPEN", None)


# ------------------------------------------------------------ V2 307 maintenance

def test_v2a_307_to_maintenance_open():
    assert verdict(307, {"Location": "/maintenance"}, "") == \
        ("OPEN", None)


def test_v2b_maintenance_landing_open():
    assert verdict(200, body=MAINTENANCE,
                   url="https://site.example/maintenance") == \
        ("OPEN", None)


def test_v2c_503_maintenance_unreachable():
    assert verdict(503, body=MAINTENANCE) == ("UNREACHABLE", None)


def test_v2d_maintenance_at_root_open():
    assert verdict(200, body=MAINTENANCE) == ("OPEN", None)


# ------------------------------------------------------------ V3 biometric

def test_v3a_fingerprint_prompt_login_gated():
    assert verdict(200, body=BIOMETRIC_PAGE) == ("LOGIN_GATED", None)


def test_v3b_fingerprint_prompt_big_article_open():
    body = "<html><body>" + BIG_ARTICLE + \
        "<p>Use your fingerprint to sign in.</p>" \
        "<button>Try again</button></body></html>"
    assert verdict(200, body=body) == ("OPEN", None)


def test_v3c_fingerprint_asset_filename_open():
    body = "<html><body>" + PARA + \
        "<script src=\"/js/fingerprint-signin.js\"></script>" \
        "</body></html>"
    assert verdict(200, body=body) == ("OPEN", None)


def test_v3d_fingerprint_stylesheet_class_open():
    body = "<html><body>" + PARA + \
        "<style>.fingerprint-prompt{border:0}</style>" \
        "</body></html>"
    assert verdict(200, body=body) == ("OPEN", None)


def test_v3e_fingerprint_prose_no_machinery_open():
    body = ("<html><body><p>On your phone, use your fingerprint "
            "to unlock the app after you sign in with your "
            "password.</p></body></html>")
    assert verdict(200, body=body) == ("OPEN", None)


def test_v3f_fingerprint_prompt_at_login_url():
    assert verdict(200, body=BIOMETRIC_PAGE, url=LOGIN) == \
        ("LOGIN_GATED", None)


def test_v3g_fingerprint_script_string_open():
    body = "<html><body>" + PARA + \
        "<form><button>Cancel</button></form>" \
        "<script>var msg = \"use your fingerprint\";</script>" \
        "</body></html>"
    assert verdict(200, body=body) == ("OPEN", None)


# ------------------------------------------------------------ V4 robots versions

def test_v4a_versioned_untracked_agent_pass():
    assert robots_grade("User-agent: wallcheck/1.0\n"
                        "Disallow: /\n") == "PASS"


def test_v4b_versioned_gptbot_blocked_warn():
    assert robots_grade("User-agent: GPTBot/2.0\n"
                        "Disallow: /\n") == "WARN"


def test_v4c_all_versioned_agents_fail():
    text = ("User-agent: GPTBot/1.0\nDisallow: /\n"
            "User-agent: ClaudeBot/2.0\nDisallow: /\n"
            "User-agent: CCBot/1.1\nDisallow: /\n"
            "User-agent: Google-Extended/1.0\nDisallow: /\n")
    assert robots_grade(text) == "FAIL"


def test_v4d_versioned_allow_cancels_block_pass():
    text = ("User-agent: GPTBot\nDisallow: /\n\n"
            "User-agent: GPTBot/2.0\nAllow: /\n")
    assert robots_grade(text) == "PASS"


def test_v4e_versioned_claudebot_restricted_warn():
    text = ("User-agent: ClaudeBot/3.1\nDisallow: /private\n\n"
            "User-agent: *\nAllow: /\n")
    assert robots_grade(text) == "WARN"


# ------------------------------------------------------------ V5 llms comments

def test_v5a_llms_comment_only_link_warn():
    body = ("# Site Index\n\n"
            "<!-- [Docs](https://example.com/docs) -->\n")
    assert llms_grade(body) == "WARN"


def test_v5b_llms_comment_plus_real_link_pass():
    body = ("# Site Index\n\n"
            "<!-- [Docs](https://example.com/docs) -->\n"
            "- [Guide](/guide)\n")
    assert llms_grade(body) == "PASS"


def test_v5c_llms_comment_only_warn():
    body = "<!-- see https://example.com/map -->\n"
    assert llms_grade(body) == "WARN"


# ------------------------------------------------------------ V6 sitemap IP locs

def test_v6a_ipv4_literal_loc_pass():
    body = ("<?xml version=\"1.0\"?><urlset>"
            "<url><loc>http://192.0.2.10/sitemap.xml</loc></url>"
            "</urlset>")
    assert sitemap_grade(body) == "PASS"


def test_v6b_ipv6_literal_loc_pass():
    body = ("<?xml version=\"1.0\"?><urlset>"
            "<url><loc>http://[2001:db8::10]/page</loc></url>"
            "</urlset>")
    assert sitemap_grade(body) == "PASS"


def test_v6c_loopback_loc_pass():
    body = ("<?xml version=\"1.0\"?><urlset>"
            "<url><loc>https://127.0.0.1/admin</loc></url>"
            "</urlset>")
    assert sitemap_grade(body) == "PASS"


def test_v6d_pct_host_plus_ip_loc_pass():
    body = ("<?xml version=\"1.0\"?><urlset>"
            "<url><loc>https://%65xample.com/a</loc></url>"
            "<url><loc>http://192.0.2.10/b</loc></url>"
            "</urlset>")
    assert sitemap_grade(body) == "PASS"


# ------------------------------------------------------------ V7 SQ/IS/KK/ML

def test_v7a_sq_demand_challenged():
    body = "<html><body><p>%s</p></body></html>" % SQ_PHRASE
    assert verdict(403, body=body) == ("CHALLENGED", "Generic")


def test_v7b_sq_checkbox_challenged():
    body = "<html><body><p>%s</p></body></html>" % SQ_CHECKBOX
    assert verdict(403, body=body) == ("CHALLENGED", "Generic")


def test_v7c_is_demand_challenged():
    body = "<html><body><p>%s</p></body></html>" % IS_PHRASE
    assert verdict(403, body=body) == ("CHALLENGED", "Generic")


def test_v7d_is_checkbox_challenged():
    body = "<html><body><p>%s</p></body></html>" % IS_CHECKBOX
    assert verdict(403, body=body) == ("CHALLENGED", "Generic")


def test_v7e_kk_demand_challenged():
    body = "<html><body><p>%s</p></body></html>" % KK_PHRASE
    assert verdict(403, body=body) == ("CHALLENGED", "Generic")


def test_v7f_kk_checkbox_challenged():
    body = "<html><body><p>%s</p></body></html>" % KK_CHECKBOX
    assert verdict(403, body=body) == ("CHALLENGED", "Generic")


def test_v7g_ml_demand_challenged():
    body = "<html><body><p>%s</p></body></html>" % ML_PHRASE
    assert verdict(403, body=body) == ("CHALLENGED", "Generic")


def test_v7h_ml_checkbox_challenged():
    body = "<html><body><p>%s</p></body></html>" % ML_CHECKBOX
    assert verdict(403, body=body) == ("CHALLENGED", "Generic")


def test_v7i_sq_phrase_big_article_open():
    body = "<html><body>" + BIG_ARTICLE + \
        "<p>%s</p></body></html>" % SQ_PHRASE
    assert verdict(200, body=body) == ("OPEN", None)


def test_v7j_is_fragment_open():
    body = "<html><body><p>vélmenni</p></body></html>"
    assert verdict(200, body=body) == ("OPEN", None)


def test_v7k_ml_phrase_style_block_open():
    body = "<html><body>" + PARA + \
        "<style>.x{content:\"%s\"}</style></body></html>" % ML_PHRASE
    assert verdict(200, body=body) == ("OPEN", None)


# ------------------------------------------------------------ V8 toast

def test_v8a_big_article_toast_phrase_open():
    body = "<html><body>" + BIG_ARTICLE + \
        "<div class=\"toast\" role=\"alert\">Verify you are " \
        "human to continue</div></body></html>"
    assert verdict(200, body=body) == ("OPEN", None)


def test_v8b_toast_only_phrase_challenged():
    body = ("<html><body><div class=\"toast\">Verify you are "
            "human</div></body></html>")
    assert verdict(200, body=body) == ("CHALLENGED", "Generic")


def test_v8c_big_article_toast_data_attr_open():
    body = "<html><body>" + BIG_ARTICLE + \
        "<div class=\"toast\" data-toast-text=\"Verify you are " \
        "human\">Welcome back</div></body></html>"
    assert verdict(200, body=body) == ("OPEN", None)


def test_v8d_toast_no_phrase_open():
    body = ("<html><body><div class=\"toast\">Item added to "
            "your cart</div></body></html>")
    assert verdict(200, body=body) == ("OPEN", None)
