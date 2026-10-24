"""Wave 24 battery v16 regression pins (see validation/wave24/
HANDCLASS-16.md for the hand classifications). Shapes: challenge
markers only in <figcaption> content, HTTP 402 responses, login
walls with an "approve this sign-in on your device" push prompt,
robots.txt mixed-case group names, llms.txt duplicate H1
headings, sitemap.xml mixing www and non-www <loc> hosts,
challenge phrases in Bulgarian/Slovak/Croatian/Slovenian, and
challenge phrases only inside a <summary> element.
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

BG_PHRASE = "Потвърдете, че не сте робот"
SK_PHRASE = "Potvrďte, že nie ste robot"
HR_PHRASE = "Potvrdite da niste robot"
SL_PHRASE = "Potrdite, da niste robot"

PUSH_PAGE = ("<html><body><p>Approve this sign-in on your device "
             "to continue.</p><button>Resend notification</button>"
             "</body></html>")


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


# --- R1: challenge markers only in <figcaption> ---
def test_r1a_figcaption_only_phrase_is_challenged():
    body = ('<html><body><figure><img src="/img/x.png">'
            "<figcaption>Verify you are human</figcaption>"
            "</figure></body></html>")
    assert verdict(200, body=body) == ("CHALLENGED", "Generic")


def test_r1b_figcaption_phrase_with_paragraph_is_challenged():
    body = ("<html><body>" + PARA +
            '<figure><img src="/img/x.png">'
            "<figcaption>Verify you are human</figcaption>"
            "</figure></body></html>")
    assert verdict(200, body=body) == ("CHALLENGED", "Generic")


def test_r1c_figcaption_phrase_on_article_is_open():
    body = (BIG_ARTICLE + '<figure><img src="/img/x.png">'
            "<figcaption>Verify you are human</figcaption></figure>")
    assert verdict(200, body=body) == ("OPEN", None)


def test_r1d_figure_with_scenic_caption_is_open():
    body = ('<html><body><figure><img src="/img/bay.png">'
            "<figcaption>The bay at dawn, from Pier 9.</figcaption>"
            "</figure></body></html>")
    assert verdict(200, body=body) == ("OPEN", None)


# --- R2: HTTP 402 ---
def test_r2a_402_paywall_body_is_walled():
    body = ("<html><body><p>Payment required. Subscribe to "
            "access this content.</p></body></html>")
    assert verdict(402, body=body) == ("WALLED", None)


def test_r2b_402_with_challenge_phrase_is_walled_generic():
    body = ("<html><body><p>Verify you are human to "
            "continue.</p></body></html>")
    assert verdict(402, body=body) == ("WALLED", "Generic")


def test_r2c_402_with_cloudflare_challenge_is_challenged():
    body = ("<html><head><title>Just a moment...</title></head>"
            "<body>Checking your browser before accessing the "
            "site.</body></html>")
    assert verdict(402, headers={"cf-ray": "8f00-example",
                                 "server": "cloudflare"},
                   body=body) == ("CHALLENGED", "Cloudflare")


def test_r2d_402_empty_body_is_walled():
    assert verdict(402, body="") == ("WALLED", None)


# --- R3: push-approval sign-in prompts ---
def test_r3a_push_approval_prompt_is_login_gated():
    assert verdict(200, body=PUSH_PAGE) == ("LOGIN_GATED", None)


def test_r3b_push_approval_on_article_is_open():
    body = BIG_ARTICLE + PUSH_PAGE
    assert verdict(200, body=body) == ("OPEN", None)


def test_r3c_push_asset_filename_is_open():
    body = ("<html><body>" + PARA +
            '<script src="/js/push-approve.js"></script>'
            "</body></html>")
    assert verdict(200, body=body) == ("OPEN", None)


def test_r3d_push_stylesheet_class_is_open():
    body = ("<html><head><style>.push-approval-prompt{border:0}"
            "</style></head><body>" + PARA + "</body></html>")
    assert verdict(200, body=body) == ("OPEN", None)


def test_r3e_push_wording_without_machinery_is_open():
    body = ("<html><body><p>To sign in, approve this sign-in on "
            "your device when prompted. This page explains how "
            "the process works.</p></body></html>")
    assert verdict(200, body=body) == ("OPEN", None)


def test_r3f_push_approval_at_login_url_is_login_gated():
    assert verdict(200, body=PUSH_PAGE, url=LOGIN) == \
        ("LOGIN_GATED", None)


def test_r3g_push_wording_in_script_is_open():
    body = ("<html><body>" + PARA +
            "<nav><button>Menu</button></nav>"
            '<script>var msg = "approve this sign-in";</script>'
            "</body></html>")
    assert verdict(200, body=body) == ("OPEN", None)


# --- R4: robots.txt mixed-case group names ---
def test_r4a_wallcheck_group_only_is_pass():
    body = "User-Agent: WALLCHECK\nDisallow: /\n"
    r = base_records(robots=rec(200, body=body))
    assert audit_check(r, "robots_txt")["status"] == "PASS"


def test_r4b_uppercase_agent_value_group_is_warn():
    body = "User-Agent: GPTBOT\nDisallow: /\n"
    r = base_records(robots=rec(200, body=body))
    assert audit_check(r, "robots_txt")["status"] == "WARN"


def test_r4c_uppercase_directive_name_wildcard_is_fail():
    body = "USER-AGENT: *\nDisallow: /\n"
    r = base_records(robots=rec(200, body=body))
    assert audit_check(r, "robots_txt")["status"] == "FAIL"


def test_r4d_wallcheck_block_plus_wildcard_allow_is_pass():
    body = ("User-Agent: Wallcheck\nDisallow: /\n\n"
            "User-agent: *\nAllow: /\n")
    r = base_records(robots=rec(200, body=body))
    assert audit_check(r, "robots_txt")["status"] == "PASS"


# --- R5: llms.txt duplicate H1 headings ---
def test_r5a_duplicate_h1_with_link_is_pass():
    body = "# Site Guide\n# Site Guide\n- [Docs](/docs)\n"
    r = base_records(llms=rec(200, body=body))
    assert audit_check(r, "llms_txt")["status"] == "PASS"


def test_r5b_duplicate_h1_only_is_warn():
    body = "# Site Guide\n# Site Guide\n"
    r = base_records(llms=rec(200, body=body))
    assert audit_check(r, "llms_txt")["status"] == "WARN"


def test_r5c_duplicate_h1_with_paths_is_pass():
    body = ("# Guide\n# Guide\n\nFull docs at /docs and the "
            "API map at /api.\n")
    r = base_records(llms=rec(200, body=body))
    assert audit_check(r, "llms_txt")["status"] == "PASS"


# --- R6: sitemap.xml mixing www and non-www <loc> hosts ---
def test_r6a_mixed_host_urlset_is_pass():
    body = ('<?xml version="1.0" encoding="UTF-8"?>'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            "<url><loc>https://example.com/a</loc></url>"
            "<url><loc>https://www.example.com/b</loc></url>"
            "</urlset>")
    r = base_records(sitemap=rec(200, body=body))
    assert audit_check(r, "sitemap")["status"] == "PASS"


def test_r6b_mixed_host_index_is_pass():
    body = ('<?xml version="1.0" encoding="UTF-8"?>'
            '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            "<sitemap><loc>https://example.com/s1.xml</loc></sitemap>"
            "<sitemap><loc>https://www.example.com/s2.xml</loc></sitemap>"
            "</sitemapindex>")
    r = base_records(sitemap=rec(200, body=body))
    assert audit_check(r, "sitemap")["status"] == "PASS"


def test_r6c_all_locs_on_other_host_is_pass():
    body = ('<?xml version="1.0" encoding="UTF-8"?>'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            "<url><loc>https://www.example.com/a</loc></url>"
            "<url><loc>https://www.example.com/b</loc></url>"
            "</urlset>")
    r = base_records(sitemap=rec(
        200, body=body, final_url="https://example.com/sitemap.xml"))
    assert audit_check(r, "sitemap")["status"] == "PASS"


# --- R7: Bulgarian / Slovak / Croatian / Slovenian phrases ---
def test_r7a_bulgarian_phrase_is_challenged():
    body = "<html><body><p>%s</p></body></html>" % BG_PHRASE
    assert verdict(403, body=body) == ("CHALLENGED", "Generic")


def test_r7b_slovak_phrase_is_challenged():
    body = "<html><body><p>%s</p></body></html>" % SK_PHRASE
    assert verdict(403, body=body) == ("CHALLENGED", "Generic")


def test_r7c_croatian_phrase_is_challenged():
    body = "<html><body><p>%s</p></body></html>" % HR_PHRASE
    assert verdict(403, body=body) == ("CHALLENGED", "Generic")


def test_r7d_slovenian_phrase_is_challenged():
    body = "<html><body><p>%s</p></body></html>" % SL_PHRASE
    assert verdict(403, body=body) == ("CHALLENGED", "Generic")


def test_r7e_bulgarian_phrase_on_article_is_open():
    body = BIG_ARTICLE + "<p>%s</p>" % BG_PHRASE
    assert verdict(200, body=body) == ("OPEN", None)


def test_r7f_bulgarian_fragment_is_open():
    body = "<html><body><p>робот</p></body></html>"
    assert verdict(200, body=body) == ("OPEN", None)


def test_r7g_bulgarian_phrase_in_style_block_is_open():
    body = ("<html><head><style>.gate::before{content:\""
            + BG_PHRASE + "\"}</style></head><body>" + PARA +
            "</body></html>")
    assert verdict(200, body=body) == ("OPEN", None)


# --- R8: challenge phrase only inside a <summary> element ---
def test_r8a_summary_only_phrase_is_challenged():
    body = ("<html><body><details open><summary>Verify you are "
            "human</summary></details></body></html>")
    assert verdict(200, body=body) == ("CHALLENGED", "Generic")


def test_r8b_summary_phrase_closed_details_is_challenged():
    body = ("<html><body>" + PARA +
            "<details><summary>Verify you are human</summary>"
            "<p>Extra text.</p></details></body></html>")
    assert verdict(200, body=body) == ("CHALLENGED", "Generic")


def test_r8c_summary_phrase_on_article_is_open():
    body = (BIG_ARTICLE + "<details><summary>Verify you are "
            "human</summary></details>")
    assert verdict(200, body=body) == ("OPEN", None)


def test_r8d_summary_without_phrase_is_open():
    body = ("<html><body><details><summary>Site navigation"
            "</summary></details></body></html>")
    assert verdict(200, body=body) == ("OPEN", None)
