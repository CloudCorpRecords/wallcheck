"""Wave 25 battery v17 regression pins (see validation/wave25/
HANDCLASS-17.md for the hand classifications). Shapes: challenge
markers only in <blockquote> content, HTTP 410 responses, login
walls asking for an employee ID, robots.txt orphan rules and
blank-line-separated groups, llms.txt carrying a sitemap link only
inside frontmatter, sitemap.xml <loc> entries containing URL
fragments, challenge phrases in Serbian/Macedonian/Latvian/
Lithuanian, and challenge phrases only as a <textarea>'s default
text.
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

SR_PHRASE = "Потврдите да нисте робот"
MK_PHRASE = "Потврдете дека не сте робот"
LV_PHRASE = "Apstipriniet, ka neesat robots"
LT_PHRASE = "Patvirtinkite, kad nesate robotas"

EMPLOYEE_FORM = ("<html><body><form method=\"post\">"
                 "<label>Employee ID</label>"
                 "<input type=\"text\" name=\"employee_id\">"
                 "<input type=\"password\" name=\"password\">"
                 "<button type=\"submit\">Sign in</button>"
                 "</form></body></html>")


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


# ------------------------------------------------------------ T1 blockquote

def test_t1a_blockquote_only_phrase_challenged():
    body = ("<html><body><blockquote>Verify you are human"
            "</blockquote></body></html>")
    assert verdict(200, body=body) == ("CHALLENGED", "Generic")


def test_t1b_paragraph_plus_blockquote_phrase_challenged():
    body = "<html><body>" + PARA + \
        "<blockquote>Verify you are human</blockquote></body></html>"
    assert verdict(200, body=body) == ("CHALLENGED", "Generic")


def test_t1c_big_article_blockquote_phrase_open():
    body = "<html><body>" + BIG_ARTICLE + \
        "<blockquote>Verify you are human</blockquote></body></html>"
    assert verdict(200, body=body) == ("OPEN", None)


def test_t1d_blockquote_no_phrase_open():
    body = ("<html><body><blockquote>The city is a poem in stone."
            "</blockquote></body></html>")
    assert verdict(200, body=body) == ("OPEN", None)


# ------------------------------------------------------------ T2 HTTP 410

def test_t2a_410_removed_body_open():
    # Hand-corrected (see HANDCLASS-17 T2): 410 is a definitive
    # answer about the resource (the 404 species, W2-002 /
    # W6-S1c), not a requester-targeted refusal.
    body = "<html><body><p>This page has been permanently removed.</p></body></html>"
    assert verdict(410, body=body) == ("OPEN", None)


def test_t2b_410_challenge_phrase_body_open():
    # W6-S1b species at 410: a phrase in the body does not
    # convert a definitive answer into a wall (410 is outside
    # GENERIC_OK_STATUSES).
    body = "<html><body><p>Verify you are human to continue.</p></body></html>"
    assert verdict(410, body=body) == ("OPEN", None)


def test_t2c_410_cloudflare_challenge_outranks():
    body = "<html><body><p>Just a moment...</p></body></html>"
    assert verdict(410, headers={"cf-ray": "8f00-LHR"}, body=body) == \
        ("CHALLENGED", "Cloudflare")


def test_t2d_410_empty_body_open():
    assert verdict(410, body="") == ("OPEN", None)


# ------------------------------------------------------------ T3 employee ID

def test_t3a_employee_id_form_login_gated():
    assert verdict(200, body=EMPLOYEE_FORM) == ("LOGIN_GATED", None)


def test_t3b_employee_id_form_in_big_article_open():
    body = "<html><body>" + BIG_ARTICLE + EMPLOYEE_FORM + "</body></html>"
    assert verdict(200, body=body) == ("OPEN", None)


def test_t3c_employee_id_asset_filename_open():
    body = ("<html><body>" + PARA +
            "<script src=\"/js/employee-id.js\"></script>"
            "</body></html>")
    assert verdict(200, body=body) == ("OPEN", None)


def test_t3d_employee_id_stylesheet_class_open():
    body = ("<html><body>" + PARA +
            "<style>.employee-id-field{border:0}</style>"
            "</body></html>")
    assert verdict(200, body=body) == ("OPEN", None)


def test_t3e_employee_id_prose_no_machinery_open():
    body = ("<html><body><p>Your employee ID is printed on your "
            "badge. Use it together with your network password at "
            "the terminal in the lobby.</p></body></html>")
    assert verdict(200, body=body) == ("OPEN", None)


def test_t3f_employee_id_form_at_login_url_login_gated():
    assert verdict(200, body=EMPLOYEE_FORM, url=LOGIN) == \
        ("LOGIN_GATED", None)


def test_t3g_employee_id_script_string_open():
    body = ("<html><body>" + PARA +
            "<form><input type=\"password\" name=\"pw\"></form>"
            "<script>var label = \"employee id\";</script>"
            "</body></html>")
    assert verdict(200, body=body) == ("OPEN", None)


# ------------------------------------------------------------ T4 robots

def robots_grade(text):
    records = base_records(robots=rec(200, body=text))
    return audit_check(records, "robots_txt")["status"]


def test_t4a_orphan_rules_only_pass():
    assert robots_grade("Disallow: /\n") == "PASS"


def test_t4b_blank_line_inside_group_fail():
    assert robots_grade("User-agent: *\n\nDisallow: /\n") == "FAIL"


def test_t4c_orphan_then_wildcard_allow_pass():
    assert robots_grade(
        "Disallow: /private\nUser-agent: *\nAllow: /\n") == "PASS"


def test_t4d_orphan_then_empty_named_group_pass():
    assert robots_grade("Disallow: /\nUser-agent: GPTBot\n") == "PASS"


# ------------------------------------------------------------ T5 llms

def llms_grade(body):
    records = base_records(llms=rec(200, body=body))
    return audit_check(records, "llms_txt")["status"]


def test_t5a_sitemap_link_only_in_frontmatter_warn():
    body = ("---\ntitle: Site Guide\n"
            "sitemap: https://example.com/sitemap.xml\n---\n")
    assert llms_grade(body) == "WARN"


def test_t5b_bare_sitemap_url_body_pass():
    body = ("---\ntitle: Site Guide\n---\n"
            "Sitemap: https://example.com/sitemap.xml\n")
    assert llms_grade(body) == "PASS"


def test_t5c_frontmatter_sitemap_plus_real_index_pass():
    body = ("---\ntitle: Site Guide\n"
            "sitemap: https://example.com/sitemap.xml\n---\n"
            "# Site Guide\n- [Docs](/docs)\n")
    assert llms_grade(body) == "PASS"


# ------------------------------------------------------------ T6 sitemap

def sitemap_grade(body):
    records = base_records(sitemap=rec(200, body=body))
    return audit_check(records, "sitemap")["status"]


def test_t6a_full_urls_with_fragments_pass():
    body = ("<?xml version=\"1.0\"?><urlset>"
            "<url><loc>https://example.com/a#top</loc></url>"
            "<url><loc>https://example.com/b#s2</loc></url>"
            "</urlset>")
    assert sitemap_grade(body) == "PASS"


def test_t6b_fragment_only_plus_full_with_fragment_pass():
    body = ("<?xml version=\"1.0\"?><urlset>"
            "<url><loc>#section</loc></url>"
            "<url><loc>https://example.com/a#top</loc></url>"
            "</urlset>")
    assert sitemap_grade(body) == "PASS"


def test_t6c_relative_loc_with_fragment_pass():
    body = ("<?xml version=\"1.0\"?><urlset>"
            "<url><loc>/guide#install</loc></url>"
            "</urlset>")
    assert sitemap_grade(body) == "PASS"


# ------------------------------------------------------------ T7 languages

def test_t7a_serbian_phrase_challenged():
    body = "<html><body><p>" + SR_PHRASE + "</p></body></html>"
    assert verdict(403, body=body) == ("CHALLENGED", "Generic")


def test_t7b_macedonian_phrase_challenged():
    body = "<html><body><p>" + MK_PHRASE + "</p></body></html>"
    assert verdict(403, body=body) == ("CHALLENGED", "Generic")


def test_t7c_latvian_phrase_challenged():
    body = "<html><body><p>" + LV_PHRASE + "</p></body></html>"
    assert verdict(403, body=body) == ("CHALLENGED", "Generic")


def test_t7d_lithuanian_phrase_challenged():
    body = "<html><body><p>" + LT_PHRASE + "</p></body></html>"
    assert verdict(403, body=body) == ("CHALLENGED", "Generic")


def test_t7e_latvian_phrase_big_article_open():
    body = "<html><body>" + BIG_ARTICLE + "<p>" + LV_PHRASE + \
        "</p></body></html>"
    assert verdict(200, body=body) == ("OPEN", None)


def test_t7f_lithuanian_fragment_open():
    body = "<html><body><p>robotas</p></body></html>"
    assert verdict(200, body=body) == ("OPEN", None)


def test_t7g_macedonian_phrase_in_style_open():
    body = ("<html><body>" + PARA + "<style>.x{content:\"" +
            MK_PHRASE + "\"}</style></body></html>")
    assert verdict(200, body=body) == ("OPEN", None)


# ------------------------------------------------------------ T8 textarea

def test_t8a_textarea_only_phrase_challenged():
    body = ("<html><body><textarea>Verify you are human</textarea>"
            "</body></html>")
    assert verdict(200, body=body) == ("CHALLENGED", "Generic")


def test_t8b_paragraph_plus_textarea_phrase_challenged():
    body = "<html><body>" + PARA + \
        "<textarea>Verify you are human</textarea></body></html>"
    assert verdict(200, body=body) == ("CHALLENGED", "Generic")


def test_t8c_big_article_textarea_phrase_open():
    body = "<html><body>" + BIG_ARTICLE + \
        "<textarea>Verify you are human</textarea></body></html>"
    assert verdict(200, body=body) == ("OPEN", None)


def test_t8d_phrase_only_in_placeholder_open():
    body = ("<html><body>" + PARA +
            "<textarea placeholder=\"Verify you are human\"></textarea>"
            "</body></html>")
    assert verdict(200, body=body) == ("OPEN", None)


def test_t8e_textarea_innocuous_text_open():
    body = ("<html><body><textarea>Tell us about your project"
            "</textarea></body></html>")
    assert verdict(200, body=body) == ("OPEN", None)
