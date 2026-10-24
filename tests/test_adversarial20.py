"""Wave 28 battery v20 regression pins (see validation/wave28/
HANDCLASS-20.md for the hand classifications). Shapes: challenge
markers only in <output> elements, HTTP 451 carrying a Link
header to a policy page, login walls asking for a Windows PIN,
robots.txt underscore vs hyphen product tokens, llms.txt tables
of contents with no links, sitemap.xml <loc> entries on a
different TLD, challenge phrases in Burmese/Sinhala/Amharic/
Azerbaijani, and challenges in role="alertdialog" modals.
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

MY_PHRASE = "သင်သည် စက်ရုပ်မဟုတ်ကြောင်း အတည်ပြုပါ"
MY_CHECKBOX = "ကျွန်ုပ်သည် စက်ရုပ်မဟုတ်ပါ"
SI_PHRASE = "ඔබ රොබෝවෙක් නොවන බව තහවුරු කරන්න"
SI_CHECKBOX = "මම රොබෝවෙක් නොවේ"
AM_PHRASE = "ሮቦት እንዳልሆኑ ያረጋግጡ"
AM_CHECKBOX = "እኔ ሮቦት አይደለሁም"
AZ_PHRASE = "Robot olmadığınızı təsdiqləyin"
AZ_CHECKBOX = "Mən robot deyiləm"

WINDOWS_PIN_PAGE = ("<html><body><h1>Sign in</h1>"
                    "<p>Enter your Windows PIN to continue.</p>"
                    "<button>Continue</button></body></html>")
BLOCKED_BY = {"Link": '<https://example.com/legal>; rel="blocked-by"'}


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


# ------------------------------------------------------------- W1

def test_w1a_output_only_phrase_challenged():
    body = "<html><body><output>Verify you are human</output></body></html>"
    assert verdict(200, body=body) == ("CHALLENGED", "Generic")


def test_w1b_output_phrase_small_page_challenged():
    body = "<html><body>" + PARA + \
        "<output>Verify you are human</output></body></html>"
    assert verdict(200, body=body) == ("CHALLENGED", "Generic")


def test_w1c_output_phrase_big_article_open():
    body = "<html><body>" + BIG_ARTICLE + \
        "<output>Verify you are human</output></body></html>"
    assert verdict(200, body=body) == ("OPEN", None)


def test_w1d_output_phrase_403_challenged():
    body = "<html><body><output>Verify you are human</output></body></html>"
    assert verdict(403, body=body) == ("CHALLENGED", "Generic")


def test_w1e_output_ordinary_text_open():
    body = "<html><body><output>42 results found</output></body></html>"
    assert verdict(200, body=body) == ("OPEN", None)


def test_w1f_output_in_form_big_article_open():
    body = "<html><body>" + BIG_ARTICLE + \
        '<form><output name="result">Verify you are human</output>' \
        "</form></body></html>"
    assert verdict(200, body=body) == ("OPEN", None)


# ------------------------------------------------------------- W2

def test_w2a_451_blocked_by_link_walled():
    body = ("<html><body><h1>Unavailable For Legal Reasons</h1>"
            "<p>This content is not available in your region.</p>"
            "</body></html>")
    v, _ = verdict(451, headers=BLOCKED_BY, body=body)
    assert v == "WALLED"


def test_w2b_451_link_and_phrase_walled_generic():
    body = ("<html><body><p>Verify you are human</p>"
            "</body></html>")
    assert verdict(451, headers=BLOCKED_BY, body=body) == \
        ("WALLED", "Generic")


def test_w2c_451_link_full_article_walled():
    body = "<html><body>" + BIG_ARTICLE + "</body></html>"
    v, _ = verdict(451, headers=BLOCKED_BY, body=body)
    assert v == "WALLED"


def test_w2d_200_blocked_by_link_open():
    body = "<html><body>" + BIG_ARTICLE + "</body></html>"
    assert verdict(200, headers=BLOCKED_BY, body=body) == ("OPEN", None)


def test_w2e_451_link_to_login_stays_walled():
    headers = {"Link": '<https://site.example/login>; rel="blocked-by"'}
    body = ("<html><body><h1>Unavailable For Legal Reasons</h1>"
            "</body></html>")
    v, _ = verdict(451, headers=headers, body=body)
    assert v == "WALLED"


def test_w2f_451_link_and_retry_after_walled():
    headers = dict(BLOCKED_BY)
    headers["Retry-After"] = "3600"
    body = ("<html><body><h1>Unavailable For Legal Reasons</h1>"
            "</body></html>")
    v, _ = verdict(451, headers=headers, body=body)
    assert v == "WALLED"


# ------------------------------------------------------------- W3

def test_w3a_windows_pin_prompt_login_gated():
    assert verdict(200, body=WINDOWS_PIN_PAGE) == ("LOGIN_GATED", None)


def test_w3b_windows_pin_big_article_open():
    body = "<html><body>" + BIG_ARTICLE + \
        "<p>Enter your Windows PIN to continue.</p>" \
        "<button>Continue</button></body></html>"
    assert verdict(200, body=body) == ("OPEN", None)


def test_w3c_windows_asset_filename_open():
    body = "<html><body>" + PARA + \
        '<script src="/js/windows-hello.js"></script></body></html>'
    assert verdict(200, body=body) == ("OPEN", None)


def test_w3d_windows_stylesheet_class_open():
    body = "<html><body>" + PARA + \
        "<style>.windows-pin-prompt{border:0}</style></body></html>"
    assert verdict(200, body=body) == ("OPEN", None)


def test_w3e_windows_prose_no_machinery_open():
    body = ("<html><body><p>On Windows, you can set a Windows PIN "
            "under Settings &gt; Accounts after you sign in with "
            "your password.</p></body></html>")
    assert verdict(200, body=body) == ("OPEN", None)


def test_w3f_windows_pin_at_login_url():
    body = ("<html><body><h1>Sign in</h1><form>"
            "<p>Enter your Windows PIN to continue.</p>"
            "<button>Continue</button></form></body></html>")
    assert verdict(200, body=body, url=LOGIN) == ("LOGIN_GATED", None)


def test_w3g_windows_script_string_open():
    body = "<html><body>" + PARA + \
        '<form><button>Cancel</button></form>' \
        '<script>var msg = "enter your windows pin";</script>' \
        "</body></html>"
    assert verdict(200, body=body) == ("OPEN", None)


def test_w3h_windows_hello_prompt_login_gated():
    body = ("<html><body><h1>Sign in with Windows Hello</h1>"
            "<button>Sign in</button></body></html>")
    assert verdict(200, body=body) == ("LOGIN_GATED", None)


# ------------------------------------------------------------- W4

def test_w4a_underscore_wallcheck_pass():
    assert robots_grade("User-agent: wall_check\nDisallow: /\n") == "PASS"


def test_w4b_hyphenated_gptbot_pass():
    assert robots_grade("User-agent: GPT-Bot\nDisallow: /\n") == "PASS"


def test_w4c_underscore_gptbot_pass():
    assert robots_grade("User-agent: gpt_bot\nDisallow: /\n") == "PASS"


def test_w4d_underscore_allow_does_not_cancel_warn():
    text = ("User-agent: GPTBot\nDisallow: /\n\n"
            "User-agent: GPT_Bot\nAllow: /\n")
    assert robots_grade(text) == "WARN"


def test_w4e_hyphenated_claudebot_restriction_pass():
    text = ("User-agent: Claude-Bot\nDisallow: /private\n\n"
            "User-agent: *\nAllow: /\n")
    assert robots_grade(text) == "PASS"


def test_w4f_versioned_and_underscore_not_merged_pass():
    text = ("User-agent: wallcheck/1.0\nDisallow: /\n\n"
            "User-agent: wall_check\nDisallow: /\n")
    assert robots_grade(text) == "PASS"


# ------------------------------------------------------------- W5

TOC = ("# Site Guide\n\n"
       "## Getting Started\n\n"
       "This section explains how new accounts are created and "
       "how the first project is configured for a small team.\n\n"
       "## Billing\n\n"
       "This section explains invoices, receipts, and how plan "
       "changes take effect during a cycle.\n\n"
       "## Support\n\n"
       "This section explains how to reach the support team and "
       "what information to include in a request.\n")


def test_w5a_toc_no_links_warn():
    assert llms_grade(TOC) == "WARN"


def test_w5b_toc_plus_real_link_pass():
    body = TOC + "\n[Full documentation](https://x.example/docs)\n"
    assert llms_grade(body) == "PASS"


def test_w5c_toc_fragment_links_only_warn():
    body = ("# Site Guide\n\n"
            "- [Install](#install)\n"
            "- [Config](#config)\n"
            "- [Billing](#billing)\n")
    assert llms_grade(body) == "WARN"


def test_w5d_toc_incidental_slashes_pass_by_doctrine():
    body = ("# Site Guide\n\n"
            "## Pipelines\n\n"
            "This section explains CI/CD pipelines and the "
            "pros/cons of each runner the platform offers.\n")
    assert llms_grade(body) == "PASS"


def test_w5e_toc_plain_text_paths_pass():
    body = "# Site Guide\n\n## /docs\n\n## /api\n\n## /pricing\n"
    assert llms_grade(body) == "PASS"


def test_w5f_tiny_toc_warn():
    assert llms_grade("# Guide\n\n## Soon\n") == "WARN"


# ------------------------------------------------------------- W6

def test_w6a_cross_tld_only_loc_pass():
    body = ('<?xml version="1.0"?><urlset>'
            "<url><loc>https://other.example.net/page</loc></url>"
            "</urlset>")
    assert sitemap_grade(body) == "PASS"


def test_w6b_mixed_same_and_cross_tld_pass():
    body = ('<?xml version="1.0"?><urlset>'
            "<url><loc>https://x.example/a</loc></url>"
            "<url><loc>https://other.example.net/b</loc></url>"
            "</urlset>")
    assert sitemap_grade(body) == "PASS"


def test_w6c_percent_encoded_foreign_host_warn():
    body = ('<?xml version="1.0"?><urlset>'
            "<url><loc>https://%65xample.net/a</loc></url>"
            "</urlset>")
    assert sitemap_grade(body) == "WARN"


def test_w6d_cross_tld_sitemapindex_child_pass():
    body = ('<?xml version="1.0"?><sitemapindex>'
            "<sitemap><loc>https://other.example.net/sitemap.xml"
            "</loc></sitemap></sitemapindex>")
    assert sitemap_grade(body) == "PASS"


def test_w6e_lookalike_host_loc_pass_by_doctrine():
    body = ('<?xml version="1.0"?><urlset>'
            "<url><loc>https://x.example.evil.net/a</loc></url>"
            "</urlset>")
    assert sitemap_grade(body) == "PASS"


# ------------------------------------------------------------- W7

def _stub(phrase):
    return "<html><body><p>%s</p></body></html>" % phrase


def test_w7a_burmese_demand_challenged():
    assert verdict(403, body=_stub(MY_PHRASE)) == ("CHALLENGED", "Generic")


def test_w7b_burmese_checkbox_challenged():
    assert verdict(403, body=_stub(MY_CHECKBOX)) == \
        ("CHALLENGED", "Generic")


def test_w7c_sinhala_demand_challenged():
    assert verdict(403, body=_stub(SI_PHRASE)) == ("CHALLENGED", "Generic")


def test_w7d_sinhala_checkbox_challenged():
    assert verdict(403, body=_stub(SI_CHECKBOX)) == \
        ("CHALLENGED", "Generic")


def test_w7e_amharic_demand_challenged():
    assert verdict(403, body=_stub(AM_PHRASE)) == ("CHALLENGED", "Generic")


def test_w7f_amharic_checkbox_challenged():
    assert verdict(403, body=_stub(AM_CHECKBOX)) == \
        ("CHALLENGED", "Generic")


def test_w7g_azerbaijani_demand_challenged():
    assert verdict(403, body=_stub(AZ_PHRASE)) == ("CHALLENGED", "Generic")


def test_w7h_azerbaijani_checkbox_challenged():
    assert verdict(403, body=_stub(AZ_CHECKBOX)) == \
        ("CHALLENGED", "Generic")


def test_w7i_burmese_big_article_open():
    body = "<html><body>" + BIG_ARTICLE + \
        "<p>%s</p></body></html>" % MY_PHRASE
    assert verdict(200, body=body) == ("OPEN", None)


def test_w7j_burmese_fragment_open():
    assert verdict(200, body=_stub("စက်ရုပ်")) == ("OPEN", None)


def test_w7k_azerbaijani_style_block_open():
    body = "<html><body>" + PARA + \
        "<style>.x::after{content:\"%s\"}</style></body></html>" \
        % AZ_PHRASE
    assert verdict(200, body=body) == ("OPEN", None)


# ------------------------------------------------------------- W8

def test_w8a_alertdialog_over_article_challenged():
    body = "<html><body>" + BIG_ARTICLE + \
        '<div role="alertdialog"><p>Verify you are human</p></div>' \
        "</body></html>"
    assert verdict(200, body=body) == ("CHALLENGED", "Generic")


def test_w8b_aria_modal_dialog_challenged():
    body = "<html><body>" + BIG_ARTICLE + \
        '<div role="dialog" aria-modal="true">' \
        "<p>Verify you are human</p></div></body></html>"
    assert verdict(200, body=body) == ("CHALLENGED", "Generic")


def test_w8c_alertdialog_no_phrase_open():
    body = "<html><body>" + BIG_ARTICLE + \
        '<div role="alertdialog"><p>We use cookies to improve ' \
        "your experience.</p></div></body></html>"
    assert verdict(200, body=body) == ("OPEN", None)


def test_w8d_alertdialog_only_content_challenged():
    body = ('<html><body><div role="alertdialog">Verify you are '
            "human</div></body></html>")
    assert verdict(200, body=body) == ("CHALLENGED", "Generic")


def test_w8e_alertdialog_data_attr_carrier_open():
    body = "<html><body>" + BIG_ARTICLE + \
        '<div role="alertdialog" data-text="Verify you are human">' \
        "<p>Session notice</p></div></body></html>"
    assert verdict(200, body=body) == ("OPEN", None)


def test_w8f_modeless_dialog_role_open():
    body = "<html><body>" + BIG_ARTICLE + \
        '<div role="dialog"><p>Verify you are human</p></div>' \
        "</body></html>"
    assert verdict(200, body=body) == ("OPEN", None)
