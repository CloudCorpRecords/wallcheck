"""Wave 18 battery v10 regression pins (see validation/wave18/
HANDCLASS-10.md for the hand classifications). Shapes: CSS custom
properties, sticky-banner challenges, SMS/email code prompts in
digit-box inputs, robots Sitemap lines pointing to a 404, llms.txt
through trailing-slash redirects, sitemap.xml files with relative
or empty <loc> entries, PT-BR/ID/VI/TH challenge phrases, and
aria-label-only challenge phrases. Plus guards for each fix's
blast radius.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from wallcheck.classify import classify  # noqa: E402
from wallcheck.audit import evaluate_audit  # noqa: E402

LOGIN = "https://site.example/login"
ARTICLE = ("<p>" + "This is a real article paragraph about how web "
           "servers handle requests, written for human readers. " * 8
           + "</p>")
BIG_ARTICLE = "<article>" + ("<p>Real article text about web "
               "infrastructure and the history of the open web, "
               "written in full sentences for readers. </p>" * 170) \
    + "</article>"  # > 16 KB served-page gate, by construction


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


def robots_with(sitemap_lines):
    body = "User-agent: *\nAllow: /\n" + "".join(
        "Sitemap: %s\n" % s for s in sitemap_lines)
    return rec(200, body=body)


# ---------------------------------------------------------------- K1: CSS custom properties

def test_k1a_unconsumed_custom_property_on_article_is_open():
    body = ARTICLE + '<style>:root{--notice:"verify you are human";}</style>'
    assert verdict(200, body=body) == ("OPEN", None)


def test_k1b_css_content_only_page_is_challenged():
    body = ('<div class="gate"></div><style>.gate::before{content:'
            '"verify you are human";}</style>')
    assert verdict(200, body=body) == ("CHALLENGED", "Generic")


def test_k1c_split_custom_properties_via_var_is_challenged():
    body = ('<div class="gate"></div><style>:root{--a:"verify you are "; '
            '--b:"human";}.gate::before{content:var(--a) var(--b);}</style>')
    assert verdict(200, body=body) == ("CHALLENGED", "Generic")


def test_k1d_unconsumed_vendor_property_on_article_is_open():
    body = ARTICLE + '<style>:root{--vendor:"perimeterx";}</style>'
    assert verdict(200, body=body) == ("OPEN", None)


def test_k1e_captcha_token_only_in_custom_property_is_challenged():
    body = '<style>:root{--flag:"captcha";}</style>'
    assert verdict(200, body=body) == ("CHALLENGED", "Generic")


def test_k1f_decorative_custom_property_on_big_article_is_open():
    body = (BIG_ARTICLE + '<style>:root{--note:"verify you are human";} '
            '.note::before{content:var(--note);}</style>')
    assert verdict(200, body=body) == ("OPEN", None)


# ---------------------------------------------------------------- K2: sticky banners

def _banner(cls, style, inner):
    return ('<div class="%s" style="%s">%s</div>' % (cls, style, inner))


def test_k2a_sticky_challenge_banner_over_big_article_is_challenged():
    body = BIG_ARTICLE + _banner(
        "announcement-banner", "position:fixed;top:0;",
        'Verify you are human <input type="checkbox">')
    assert verdict(200, body=body) == ("CHALLENGED", "Generic")


def test_k2b_sticky_cookie_banner_is_open():
    body = BIG_ARTICLE + _banner(
        "announcement-banner", "position:fixed;bottom:0;",
        "We use cookies to improve your experience.")
    assert verdict(200, body=body) == ("OPEN", None)


def test_k2c_sticky_newsletter_banner_is_open():
    body = BIG_ARTICLE + _banner(
        "announcement-banner", "position:fixed;bottom:0;",
        "Subscribe to our newsletter")
    assert verdict(200, body=body) == ("OPEN", None)


def test_k2d_small_page_sticky_banner_is_challenged():
    body = _banner("announcement-banner", "position:fixed;top:0;",
                   "Verify you are human")
    assert verdict(200, body=body) == ("CHALLENGED", "Generic")


def test_k2e_sticky_jsproof_banner_over_big_article_is_challenged():
    body = BIG_ARTICLE + _banner(
        "announcement-banner", "position:fixed;top:0;",
        "Checking your browser")
    assert verdict(200, body=body) == ("CHALLENGED", "Generic")


def test_k2f_inflow_banner_phrase_on_big_article_is_open():
    body = BIG_ARTICLE + _banner(
        "info-banner", "", "Verify you are human")
    assert verdict(200, body=body) == ("OPEN", None)


# ---------------------------------------------------------------- K3: SMS/email code prompts

def _digit_boxes(n=6):
    return "".join('<input name="digit-%d" maxlength="1">' % i
                   for i in range(1, n + 1))


def test_k3a_sms_code_digit_boxes_is_login_gated():
    body = ("<p>Enter the 6-digit code we texted to •••1234</p>"
            + _digit_boxes())
    assert verdict(200, body=body) == ("LOGIN_GATED", None)


def test_k3b_sms_code_named_input_is_login_gated():
    body = ('<p>Enter the verification code sent via SMS</p>'
            '<input name="code">')
    assert verdict(200, body=body) == ("LOGIN_GATED", None)


def test_k3c_sms_prompt_at_login_url_is_login_gated():
    body = ("<p>Enter the 6-digit code we texted to •••1234</p>"
            + _digit_boxes())
    assert verdict(200, body=body, url=LOGIN) == ("LOGIN_GATED", None)


def test_k3d_article_about_sms_codes_is_open():
    body = ("<p>SMS verification codes are sent to your phone when "
            "you sign in. This article explains how texted codes "
            "work and why sites use them.</p>")
    assert verdict(200, body=body) == ("OPEN", None)


def test_k3e_email_code_digit_boxes_is_login_gated():
    body = ("<p>Enter the code we emailed to you</p>" + _digit_boxes())
    assert verdict(200, body=body) == ("LOGIN_GATED", None)


def test_k3f_phone_request_form_is_open():
    body = ('<p>Enter your phone number to receive a code</p>'
            '<input name="phone" type="tel"><button>Send</button>')
    assert verdict(200, body=body) == ("OPEN", None)


# ---------------------------------------------------------------- K4: robots Sitemap -> 404

def test_k4a_declared_sitemap_dead_is_warn_and_named():
    records = base_records(
        robots=robots_with(["https://x.example/sitemap.xml"]),
        sitemap=rec(404, body=""))
    c = audit_check(records, "sitemap")
    assert c["status"] == "WARN"
    assert any("DECLARED_SITEMAP_DEAD" in e for e in c["evidence"])


def test_k4b_dead_declaration_with_serving_conventional_sitemap_passes():
    records = base_records(
        robots=robots_with(["https://x.example/dead.xml"]),
        sitemap=rec(200, body='<?xml version="1.0"?><urlset>'
                   '<url><loc>https://x.example/a</loc></url></urlset>'))
    assert audit_check(records, "sitemap")["status"] == "PASS"


def test_k4c_dead_first_declaration_with_serving_second_passes():
    records = base_records(
        robots=robots_with(["https://x.example/dead.xml",
                            "https://x.example/live.xml"]),
        sitemap=rec(200, body='<?xml version="1.0"?><urlset>'
                   '<url><loc>https://x.example/a</loc></url></urlset>'))
    c = audit_check(records, "sitemap")
    assert c["status"] == "PASS"
    assert "VIA_ROBOTS_DECLARATION" in c["evidence"]


def test_k4d_dead_declaration_with_html_conventional_path_is_warn():
    records = base_records(
        robots=robots_with(["https://x.example/dead.xml"]),
        sitemap=rec(200, body="<html><body>Not found</body></html>"))
    c = audit_check(records, "sitemap")
    assert c["status"] == "WARN"
    assert any("DECLARED_SITEMAP_DEAD" in e for e in c["evidence"])


def test_k4e_no_declaration_with_404_is_warn_without_dead_evidence():
    records = base_records(sitemap=rec(404, body=""))
    c = audit_check(records, "sitemap")
    assert c["status"] == "WARN"
    assert not any("DECLARED_SITEMAP_DEAD" in e for e in c["evidence"])


# ---------------------------------------------------------------- K5: llms via trailing-slash redirect
# (evaluate_audit grades the FINAL record; redirect-following itself
# is urllib's redirect handler, already covered. These pins lock the
# grading of each final-document species.)

LLMS_INDEX = "# Index\n\n[Docs](/docs)\n[Guide](/guide)\n"


def test_k5a_redirect_to_real_index_passes():
    records = base_records(llms=rec(200, body=LLMS_INDEX,
                                    final_url="https://x.example/llms.txt/"))
    assert audit_check(records, "llms_txt")["status"] == "PASS"


def test_k5b_redirect_to_html_shell_fails():
    records = base_records(llms=rec(
        200, body="<html><body><div id='app'></div></body></html>",
        final_url="https://x.example/llms.txt/"))
    assert audit_check(records, "llms_txt")["status"] == "FAIL"


def test_k5c_redirect_to_404_is_warn():
    records = base_records(llms=rec(404, body="",
                                    final_url="https://x.example/llms.txt/"))
    assert audit_check(records, "llms_txt")["status"] == "WARN"


def test_k5d_cross_host_redirect_to_real_index_passes():
    records = base_records(llms=rec(200, body=LLMS_INDEX,
                                    final_url="https://docs.x.example/llms"))
    assert audit_check(records, "llms_txt")["status"] == "PASS"


def test_k5e_redirect_loop_is_warn():
    bad = {"url": "https://x.example/llms.txt",
           "final_url": "https://x.example/llms.txt", "status": None,
           "headers": {}, "body": "",
           "error": "HTTPError: redirect loop", "redirect_chain": []}
    records = base_records(llms=bad)
    assert audit_check(records, "llms_txt")["status"] == "WARN"


# ---------------------------------------------------------------- K6: relative / empty <loc>

def test_k6a_root_relative_locs_pass():
    records = base_records(sitemap=rec(
        200, body='<urlset><url><loc>/docs/a</loc></url>'
        '<url><loc>/docs/b</loc></url></urlset>'))
    assert audit_check(records, "sitemap")["status"] == "PASS"


def test_k6b_document_relative_locs_pass():
    records = base_records(sitemap=rec(
        200, body='<urlset><url><loc>docs/a</loc></url></urlset>'))
    assert audit_check(records, "sitemap")["status"] == "PASS"


def test_k6c_empty_locs_only_is_warn():
    records = base_records(sitemap=rec(
        200, body='<urlset><url><loc></loc></url>'
        '<url><loc></loc></url></urlset>'))
    assert audit_check(records, "sitemap")["status"] == "WARN"


def test_k6d_whitespace_locs_only_is_warn():
    records = base_records(sitemap=rec(
        200, body='<urlset><url><loc>   </loc></url></urlset>'))
    assert audit_check(records, "sitemap")["status"] == "WARN"


def test_k6e_relative_sitemapindex_loc_passes():
    records = base_records(sitemap=rec(
        200, body='<sitemapindex><sitemap>'
        '<loc>/sitemap-posts.xml</loc></sitemap></sitemapindex>'))
    assert audit_check(records, "sitemap")["status"] == "PASS"


# ---------------------------------------------------------------- K7: PT-BR / ID / VI / TH phrases

def test_k7a_ptbr_confirm_phrase_is_challenged():
    body = "<p>Confirme que você não é um robô.</p>"
    assert verdict(403, body=body) == ("CHALLENGED", "Generic")


def test_k7b_ptbr_fuller_not_robot_is_challenged():
    body = "<p>Eu não sou um robô.</p>"
    assert verdict(403, body=body) == ("CHALLENGED", "Generic")


def test_k7c_indonesian_confirm_phrase_is_challenged():
    body = "<p>Konfirmasi bahwa Anda bukan robot.</p>"
    assert verdict(403, body=body) == ("CHALLENGED", "Generic")


def test_k7d_indonesian_not_robot_is_challenged():
    body = "<p>Saya bukan robot.</p>"
    assert verdict(403, body=body) == ("CHALLENGED", "Generic")


def test_k7e_vietnamese_confirm_phrase_is_challenged():
    body = "<p>Xác nhận bạn không phải là robot.</p>"
    assert verdict(403, body=body) == ("CHALLENGED", "Generic")


def test_k7f_vietnamese_not_robot_is_challenged():
    body = "<p>Tôi không phải là robot.</p>"
    assert verdict(403, body=body) == ("CHALLENGED", "Generic")


def test_k7g_thai_confirm_phrase_is_challenged():
    body = "<p>ยืนยันว่าคุณไม่ใช่หุ่นยนต์</p>"
    assert verdict(403, body=body) == ("CHALLENGED", "Generic")


def test_k7h_thai_not_robot_is_challenged():
    body = "<p>ฉันไม่ใช่หุ่นยนต์</p>"
    assert verdict(403, body=body) == ("CHALLENGED", "Generic")


def test_k7i_thai_phrase_quoted_in_big_article_is_open():
    body = BIG_ARTICLE + "<p>ยืนยันว่าคุณไม่ใช่หุ่นยนต์</p>"
    assert verdict(200, body=body) == ("OPEN", None)


def test_k7j_codeswitched_fragments_are_walled():
    body = "<p>Confirme / bukan robot</p>"
    assert verdict(403, body=body) == ("WALLED", None)


# ---------------------------------------------------------------- K8: aria-label phrases

def test_k8a_button_aria_label_only_page_is_challenged():
    body = '<button aria-label="Verify you are human">✓</button>'
    assert verdict(200, body=body) == ("CHALLENGED", "Generic")


def test_k8b_button_aria_label_on_small_article_is_challenged():
    body = ARTICLE + '<button aria-label="Verify you are human">✓</button>'
    assert verdict(200, body=body) == ("CHALLENGED", "Generic")


def test_k8c_button_aria_label_on_big_article_is_open():
    body = BIG_ARTICLE + '<button aria-label="Verify you are human">✓</button>'
    assert verdict(200, body=body) == ("OPEN", None)


def test_k8d_noninteractive_div_aria_label_vendor_is_open():
    body = ARTICLE + '<div aria-label="perimeterx"></div>'
    assert verdict(200, body=body) == ("OPEN", None)


def test_k8e_img_aria_label_only_page_is_challenged():
    body = '<img aria-label="Verify you are human" src="/check.png">'
    assert verdict(200, body=body) == ("CHALLENGED", "Generic")


# ---------------------------------------------------------------- W18-007: QR-prompt false positives on served homepages
# (live catch from round 14 — the rubygems.org failure mode, one
# rule later: the Wave 17 QR rule read wording from the raw body,
# so asset filenames, script identifiers, and stylesheet class
# names fired it. The fix requires QR wording + auth purpose in
# rendered visible text, and adds the served-page size gate the
# branch lacked.)

def test_w18_remoteok_qr_asset_filename_is_open():
    body = (ARTICLE + '<script src="/qrcode.js"></script>'
            '<a href="/login">Log in</a><img src="/logo.png">')
    assert verdict(200, body=body) == ("OPEN", None)


def test_w18_td_qr_script_identifier_is_open():
    body = (ARTICLE + '<script>var opts = "qrCode".split(" ");</script>'
            '<a href="/login">Log in</a><button>Continue</button>')
    assert verdict(200, body=body) == ("OPEN", None)


def test_w18_venmo_qr_css_class_is_open():
    body = (ARTICLE + '<style>.qr-code-image-container{overflow:hidden}'
            '.qr-code-appearance-default{background-color:#fff}</style>'
            '<img src="/app-qr.png">')
    assert verdict(200, body=body) == ("OPEN", None)


def test_w18_large_page_qr_prompt_is_open():
    body = (BIG_ARTICLE + '<p>Scan the QR code to sign in</p>'
            '<img src="/qr.png">')
    assert verdict(200, body=body) == ("OPEN", None)


def test_w18_real_qr_prompt_still_fires():
    body = ('<p>Scan the QR code with your phone to sign in</p>'
            '<img src="/qr.png">')
    assert verdict(200, body=body) == ("LOGIN_GATED", None)
