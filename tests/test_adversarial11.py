"""Wave 19 battery v11 regression pins (see validation/wave19/
HANDCLASS-11.md for the hand classifications). Shapes: challenge
markers only inside <template> elements, phrases split across images'
alt attributes, email-only Continue sign-in steps, robots-declared
sitemaps that are stubs by the grade's own test, CRLF/CR-only llms.txt
files, fragment-only and query-only sitemap <loc> entries, Hebrew /
Persian / Urdu / Bengali challenge phrases, and native <dialog>
elements. Plus guards for each fix's blast radius.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from wallcheck.classify import classify  # noqa: E402
from wallcheck.audit import audit_site, evaluate_audit  # noqa: E402

LOGIN = "https://site.example/login"
ARTICLE = ("<p>" + "This is a real article paragraph about how web "
           "servers handle requests, written for human readers. " * 8
           + "</p>")
BIG_ARTICLE = "<article>" + ("<p>Real article text about web "
               "infrastructure and the history of the open web, "
               "written in full sentences for readers. </p>" * 170) \
    + "</article>"  # > 16 KB served-page gate, by construction
PARA = ("<html><body><p>Our team ships every Friday and writes "
        "about the process in detail for our readers.</p></body></html>")
URLSET = ('<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
          '<url><loc>https://x.example/</loc></url></urlset>')
PROLOG_ONLY = '<?xml version="1.0" encoding="UTF-8"?>'
EMPTY_LOCS = ('<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
              '<url><loc></loc></url><url><loc>   </loc></url></urlset>')


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


def sitemap_via_site(robots_body, sitemap_rec, extra):
    url_map = {
        "https://x.example/": rec(200, {"Content-Type": "text/html"},
                                  "<html><head><title>x</title></head><body>x</body></html>"),
        "https://x.example/robots.txt": rec(200, {"Content-Type": "text/plain"}, robots_body),
        "https://x.example/llms.txt": rec(404, {}, "not found"),
        "https://x.example/sitemap.xml": sitemap_rec,
        "https://x.example/.well-known/http-message-signatures-directory": rec(404, {}, "not found"),
    }
    url_map.update(extra)

    def fake_fetch(url, timeout=15):
        return url_map.get(url, rec(404, {}, "not found", final_url=url))

    out = audit_site("https://x.example", fetch=fake_fetch)
    return [c for c in out["checks"] if c["check"] == "sitemap"][0]


def robots_with(sitemap_lines):
    body = "User-agent: *\nAllow: /\n" + "".join(
        "Sitemap: %s\n" % s for s in sitemap_lines)
    return body


# ---------------------------------------------------------------- L1: <template> elements

def test_l1a_template_challenge_on_paragraph_is_open():
    body = ARTICLE + '<template><div>Verify you are human</div></template>'
    assert verdict(200, body=body) == ("OPEN", None)


def test_l1b_template_only_page_is_challenged():
    body = '<template><div>Verify you are human</div></template>'
    assert verdict(200, body=body) == ("CHALLENGED", "Generic")


def test_l1c_template_vendor_on_big_article_is_open():
    body = BIG_ARTICLE + '<template><div>perimeterx</div></template>'
    assert verdict(200, body=body) == ("OPEN", None)


def test_l1d_template_vendor_on_paragraph_is_open():
    body = ARTICLE + '<template><div>perimeterx</div></template>'
    assert verdict(200, body=body) == ("OPEN", None)


def test_l1e_script_asset_filename_carrier_is_open():
    body = ARTICLE + '<script src="/templates/verify-human.js"></script>'
    assert verdict(200, body=body) == ("OPEN", None)


def test_l1f_template_jsproof_on_paragraph_is_open():
    body = ARTICLE + '<template><div>Checking your browser</div></template>'
    assert verdict(200, body=body) == ("OPEN", None)


# ---------------------------------------------------------------- L2: split alt attributes

def test_l2a_split_alt_phrase_is_challenged():
    body = ('<img src="/a.png" alt="verify you are">'
            '<img src="/b.png" alt="human">')
    assert verdict(403, body=body) == ("CHALLENGED", "Generic")


def test_l2b_image_input_alt_is_challenged():
    body = '<input type="image" src="/go.png" alt="verify you are human">'
    assert verdict(403, body=body) == ("CHALLENGED", "Generic")


def test_l2c_area_alt_is_challenged():
    body = ('<map><area shape="rect" coords="0,0,10,10" href="/x" '
            'alt="verify you are human"></map>')
    assert verdict(403, body=body) == ("CHALLENGED", "Generic")


def test_l2d_alt_phrase_on_big_article_is_open():
    body = BIG_ARTICLE + '<img src="/x.png" alt="verify you are human">'
    assert verdict(200, body=body) == ("OPEN", None)


def test_l2e_cross_language_alt_fragments_are_walled():
    # Corrected during the run: the first draft used alt="ich bin
    # kein roboter" as the second half, but that IS a complete DE
    # phrase (Wave 6) on its own — the classifier rightly read
    # CHALLENGED. True fragments (neither half a listed phrase):
    body = ('<img src="/a.png" alt="verify you are">'
            '<img src="/b.png" alt="kein roboter">')
    assert verdict(403, body=body) == ("WALLED", None)


def test_l2f_script_preload_list_carrier_is_open():
    body = (ARTICLE + '<script>var imgs=["verify you are", "human"];'
            '</script>')
    assert verdict(200, body=body) == ("OPEN", None)


# ---------------------------------------------------------------- L3: email-only Continue

def _continue_form(heading, button="Continue"):
    return ('<h1>%s</h1><form><input type="email" name="email">'
            '<button>%s</button></form>' % (heading, button))


def test_l3a_signin_continue_step_is_login_gated():
    assert verdict(200, body=_continue_form("Sign in")) == ("LOGIN_GATED", None)


def test_l3b_email_capture_continue_is_open():
    assert verdict(200, body=_continue_form("")) == ("OPEN", None)


def test_l3c_continue_at_login_url_is_login_gated():
    assert verdict(200, body=_continue_form("Welcome"), url=LOGIN) == ("LOGIN_GATED", None)


def test_l3d_newsletter_subscribe_with_signin_link_is_open():
    body = ('<nav><a href="/login">Sign in</a></nav><form>'
            '<input type="email" name="email"><button>Subscribe</button>'
            '</form>')
    assert verdict(200, body=body) == ("OPEN", None)


def test_l3e_script_identifier_carrier_is_open():
    body = (ARTICLE + '<script>var continueSignIn = true;</script>'
            '<form><input type="email" name="email">'
            '<button>Subscribe</button></form>')
    assert verdict(200, body=body) == ("OPEN", None)


def test_l3f_signin_section_on_big_article_is_open():
    body = BIG_ARTICLE + _continue_form("Sign in")
    assert verdict(200, body=body) == ("OPEN", None)


def test_l3g_create_account_continue_is_open_boundary():
    assert verdict(200, body=_continue_form("Create account")) == ("OPEN", None)


# ---------------------------------------------------------------- L4: fallthrough usability

def test_l4a_prolog_only_then_real_is_pass():
    robots = robots_with(["https://x.example/sitemap-a.xml",
                          "https://x.example/sitemap-b.xml"])
    extra = {
        "https://x.example/sitemap-a.xml": rec(200, {"Content-Type": "application/xml"}, PROLOG_ONLY, "https://x.example/sitemap-a.xml"),
        "https://x.example/sitemap-b.xml": rec(200, {"Content-Type": "application/xml"}, URLSET, "https://x.example/sitemap-b.xml"),
    }
    check = sitemap_via_site(robots, rec(404, {}, "not found"), extra)
    assert check["status"] == "PASS"


def test_l4b_empty_locs_then_real_is_pass():
    robots = robots_with(["https://x.example/sitemap-a.xml",
                          "https://x.example/sitemap-b.xml"])
    extra = {
        "https://x.example/sitemap-a.xml": rec(200, {"Content-Type": "application/xml"}, EMPTY_LOCS, "https://x.example/sitemap-a.xml"),
        "https://x.example/sitemap-b.xml": rec(200, {"Content-Type": "application/xml"}, URLSET, "https://x.example/sitemap-b.xml"),
    }
    check = sitemap_via_site(robots, rec(404, {}, "not found"), extra)
    assert check["status"] == "PASS"


def test_l4c_dead_then_real_is_pass():
    robots = robots_with(["https://x.example/sitemap-a.xml",
                          "https://x.example/sitemap-b.xml"])
    extra = {
        "https://x.example/sitemap-a.xml": rec(404, {}, "not found", "https://x.example/sitemap-a.xml"),
        "https://x.example/sitemap-b.xml": rec(200, {"Content-Type": "application/xml"}, URLSET, "https://x.example/sitemap-b.xml"),
    }
    check = sitemap_via_site(robots, rec(404, {}, "not found"), extra)
    assert check["status"] == "PASS"


def test_l4d_two_dead_then_real_is_pass():
    robots = robots_with(["https://x.example/sitemap-a.xml",
                          "https://x.example/sitemap-b.xml",
                          "https://x.example/sitemap-c.xml"])
    extra = {
        "https://x.example/sitemap-a.xml": rec(404, {}, "not found", "https://x.example/sitemap-a.xml"),
        "https://x.example/sitemap-b.xml": rec(404, {}, "not found", "https://x.example/sitemap-b.xml"),
        "https://x.example/sitemap-c.xml": rec(200, {"Content-Type": "application/xml"}, URLSET, "https://x.example/sitemap-c.xml"),
    }
    check = sitemap_via_site(robots, rec(404, {}, "not found"), extra)
    assert check["status"] == "PASS"


def test_l4e_prolog_only_alone_is_warn_with_dead_evidence():
    robots = robots_with(["https://x.example/sitemap-a.xml"])
    extra = {
        "https://x.example/sitemap-a.xml": rec(200, {"Content-Type": "application/xml"}, PROLOG_ONLY, "https://x.example/sitemap-a.xml"),
    }
    check = sitemap_via_site(robots, rec(404, {}, "not found"), extra)
    assert check["status"] == "WARN"
    assert any("DECLARED_SITEMAP_DEAD" in e for e in check["evidence"])


def test_l4f_conventional_path_serves_is_pass():
    robots = robots_with(["https://x.example/sitemap-a.xml"])
    extra = {
        "https://x.example/sitemap-a.xml": rec(404, {}, "not found", "https://x.example/sitemap-a.xml"),
    }
    check = sitemap_via_site(robots, rec(200, {"Content-Type": "application/xml"}, URLSET), extra)
    assert check["status"] == "PASS"


def test_l4g_commented_declaration_is_not_a_declaration():
    robots = "# Sitemap: https://x.example/sitemap-a.xml\nUser-agent: *\nAllow: /\n"
    check = sitemap_via_site(robots, rec(200, {"Content-Type": "application/xml"}, URLSET), {})
    assert check["status"] == "PASS"


# ---------------------------------------------------------------- L5: CRLF / CR-only llms

def _llms_records(body):
    return base_records(llms=rec(200, {"Content-Type": "text/plain"}, body))


def test_l5a_crlf_real_index_is_pass():
    body = "# Site map\r\n\r\n[Docs](https://x.example/docs)\r\n[Blog](https://x.example/blog)\r\n"
    assert audit_check(_llms_records(body), "llms_txt")["status"] == "PASS"


def test_l5b_crlf_frontmatter_stub_is_warn():
    body = "---\r\ntitle: Site\r\nurl: https://x.example/\r\n---\r\n"
    assert audit_check(_llms_records(body), "llms_txt")["status"] == "WARN"


def test_l5c_crlf_html_shell_is_fail():
    body = "<html>\r\n<head><title>x</title></head>\r\n<body>hi</body>\r\n</html>\r\n"
    assert audit_check(_llms_records(body), "llms_txt")["status"] == "FAIL"


def test_l5d_cr_only_frontmatter_stub_is_warn():
    body = "---\rtitle: Site\rurl: https://x.example/\r---\r"
    assert audit_check(_llms_records(body), "llms_txt")["status"] == "WARN"


def test_l5e_cr_only_real_index_is_pass():
    body = "# Site map\r\r[Docs](https://x.example/docs)\r[Blog](https://x.example/blog)\r"
    assert audit_check(_llms_records(body), "llms_txt")["status"] == "PASS"


def test_l5f_crlf_bom_frontmatter_stub_is_warn():
    body = "\ufeff---\r\ntitle: Site\r\nurl: https://x.example/\r\n---\r\n"
    assert audit_check(_llms_records(body), "llms_txt")["status"] == "WARN"


# ---------------------------------------------------------------- L6: fragment / query locs

def _sitemap_records(body):
    return base_records(sitemap=rec(200, {"Content-Type": "application/xml"}, body))


def _urlset(locs):
    inner = "".join("<url><loc>%s</loc></url>" % l for l in locs)
    return ('<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            + inner + '</urlset>')


def test_l6a_query_string_locs_are_pass():
    body = _urlset(["/page?id=1", "/page?id=2"])
    assert audit_check(_sitemap_records(body), "sitemap")["status"] == "PASS"


def test_l6b_fragment_only_locs_are_warn():
    body = _urlset(["#section", "#other"])
    assert audit_check(_sitemap_records(body), "sitemap")["status"] == "WARN"


def test_l6c_bare_query_loc_is_pass():
    body = _urlset(["?id=1"])
    assert audit_check(_sitemap_records(body), "sitemap")["status"] == "PASS"


def test_l6d_mixed_fragment_and_query_is_pass():
    body = _urlset(["#section", "/page?id=1"])
    assert audit_check(_sitemap_records(body), "sitemap")["status"] == "PASS"


def test_l6e_whitespace_only_locs_are_warn():
    body = _urlset(["   "])
    assert audit_check(_sitemap_records(body), "sitemap")["status"] == "WARN"


# ---------------------------------------------------------------- L7: HE / FA / UR / BN phrases

def test_l7a_hebrew_challenge_is_challenged():
    assert verdict(403, body="אמת שאינך רובוט") == ("CHALLENGED", "Generic")


def test_l7b_persian_challenge_is_challenged():
    assert verdict(403, body="تأیید کنید که ربات نیستید") == ("CHALLENGED", "Generic")


def test_l7c_urdu_challenge_is_challenged():
    assert verdict(403, body="تصدیق کریں کہ آپ روبوٹ نہیں ہیں") == ("CHALLENGED", "Generic")


def test_l7d_bengali_challenge_is_challenged():
    assert verdict(403, body="আপনি রোবট নন তা নিশ্চিত করুন") == ("CHALLENGED", "Generic")


def test_l7e_hebrew_not_a_robot_is_challenged():
    assert verdict(403, body="אני לא רובוט") == ("CHALLENGED", "Generic")


def test_l7f_quoted_hebrew_on_big_article_is_open():
    body = BIG_ARTICLE + "<p>As the saying goes, אמת שאינך רובוט.</p>"
    assert verdict(200, body=body) == ("OPEN", None)


def test_l7g_cross_language_fragments_are_walled():
    assert verdict(403, body="אמת / ربات نیستید") == ("WALLED", None)


# ---------------------------------------------------------------- L8: native <dialog>

def test_l8a_open_dialog_challenge_over_article_is_challenged():
    body = BIG_ARTICLE + '<dialog open>Verify you are human <input type="checkbox"></dialog>'
    assert verdict(200, body=body) == ("CHALLENGED", "Generic")


def test_l8b_closed_dialog_challenge_is_open():
    body = BIG_ARTICLE + '<dialog>Verify you are human <input type="checkbox"></dialog>'
    assert verdict(200, body=body) == ("OPEN", None)


def test_l8c_open_dialog_cookie_text_is_open():
    body = BIG_ARTICLE + '<dialog open>We use cookies to improve your experience.</dialog>'
    assert verdict(200, body=body) == ("OPEN", None)


def test_l8d_open_dialog_on_small_page_is_challenged():
    body = '<dialog open>Verify you are human <input type="checkbox"></dialog>'
    assert verdict(200, body=body) == ("CHALLENGED", "Generic")


def test_l8e_open_dialog_jsproof_is_challenged():
    body = BIG_ARTICLE + '<dialog open>Checking your browser, please wait.</dialog>'
    assert verdict(200, body=body) == ("CHALLENGED", "Generic")


def test_l8f_open_dialog_on_login_url_is_login_gated():
    body = BIG_ARTICLE + '<dialog open>Verify you are human <input type="checkbox"></dialog>'
    assert verdict(200, body=body, url=LOGIN) == ("LOGIN_GATED", None)


def test_l8g_stylesheet_dialog_class_carrier_is_open():
    body = BIG_ARTICLE + '<style>.dialog-challenge { display: none; }</style>'
    assert verdict(200, body=body) == ("OPEN", None)
