"""Wave 21 battery v13 regression pins (see validation/wave21/
HANDCLASS-13.md for the hand classifications). Shapes: object/embed
routing species, 503 throttle/traffic wording, authenticator-app
passcode prompts, robots.txt empty named groups, llms.txt
Windows-1252 artifacts, sitemap.xml non-HTTP-scheme locs,
challenge phrases in Tamil/Telugu/Marathi/Punjabi, and meta-
description-only challenge phrases.
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


# --- N1: object/embed routing species ---
def test_n1a_object_challenge_data_is_challenge():
    assert verdict(200, body='<html><body><object data="https://challenge.example/captcha/verify"></object></body></html>') == ("CHALLENGED", "Generic")


def test_n1b_embed_login_src_is_login_gated():
    assert verdict(200, body='<html><body><embed src="/login"></body></html>') == ("LOGIN_GATED", None)


def test_n1c_object_content_data_is_open():
    assert verdict(200, body='<html><body><object data="https://content.example/article"></object></body></html>') == ("OPEN", None)


def test_n1d_object_captcha_data_on_article_is_open():
    assert verdict(200, body=BIG_ARTICLE + '<object data="https://challenge.example/captcha/verify"></object>') == ("OPEN", None)


def test_n1e_object_fallback_phrase_is_challenge():
    assert verdict(200, body='<html><body><object data="https://x.example/vid">Verify you are human</object></body></html>') == ("CHALLENGED", "Generic")


def test_n1f_object_fallback_phrase_on_article_is_open():
    assert verdict(200, body=BIG_ARTICLE + '<object data="https://x.example/vid">Verify you are human</object>') == ("OPEN", None)


def test_n1g_embed_login_src_on_article_is_open():
    assert verdict(200, body=BIG_ARTICLE + '<embed src="/login">') == ("OPEN", None)


def test_n1h_object_bare_filename_is_open():
    assert verdict(200, body='<html><body><object data="player.swf"></object></body></html>') == ("OPEN", None)


# --- N2: 503 throttle / traffic wording ---
def test_n2a_503_retry_after_traffic_cause_is_rate_limited():
    assert verdict(503, {"retry-after": "60"}, body="<html><body><p>We are experiencing unusually high traffic. Please try again later.</p></body></html>") == ("RATE_LIMITED", None)


def test_n2b_503_retry_after_empty_body_is_unreachable():
    assert verdict(503, {"retry-after": "60"}, body="") == ("UNREACHABLE", None)


def test_n2c_503_retry_after_unavailable_is_unreachable():
    assert verdict(503, {"retry-after": "60"}, body="<html><body><p>Service temporarily unavailable.</p></body></html>") == ("UNREACHABLE", None)


def test_n2d_503_retry_after_too_many_is_rate_limited():
    assert verdict(503, {"retry-after": "60"}, body="<html><body><p>Too many requests, please retry in 60 seconds.</p></body></html>") == ("RATE_LIMITED", None)


# --- N3: authenticator-app passcode prompts ---
def test_n3a_authenticator_prompt_is_login_gated():
    assert verdict(200, body='<html><body><p>Enter the code from your authenticator app.</p><form><input name="totp"></form></body></html>') == ("LOGIN_GATED", None)


def test_n3b_authenticator_prompt_on_article_is_open():
    assert verdict(200, body=BIG_ARTICLE + '<p>Enter the code from your authenticator app.</p><form><input name="totp"></form>') == ("OPEN", None)


def test_n3c_authenticator_script_filename_is_open():
    assert verdict(200, body=BIG_ARTICLE + '<script src="/static/authenticator.js"></script>') == ("OPEN", None)


def test_n3d_authenticator_stylesheet_class_is_open():
    assert verdict(200, body=BIG_ARTICLE + '<style>.authenticator-prompt { color: blue; }</style>') == ("OPEN", None)


def test_n3e_authenticator_prompt_with_instructions_is_login_gated():
    assert verdict(200, body='<html><body><p>Enter the code from your authenticator app.</p><p>Open your app and type the six digits shown.</p><form><input name="totp"></form></body></html>') == ("LOGIN_GATED", None)


def test_n3f_authenticator_wording_no_input_is_open():
    assert verdict(200, body='<html><body><p>Enter the code from your authenticator app.</p></body></html>') == ("OPEN", None)


def test_n3g_authenticator_prompt_on_login_url_is_login_gated():
    assert verdict(200, body='<html><body><p>Enter the code from your authenticator app.</p><form><input name="totp"></form></body></html>', url=LOGIN) == ("LOGIN_GATED", None)


# --- N4: robots.txt empty named groups ---
def test_n4a_midfile_empty_named_group_is_fail():
    # HAND-CORRECTED (see PROBLEMS.md): RFC 9309 groups are one or
    # more user-agent lines followed by rules, so consecutive
    # user-agent lines with no rules between them are ONE group —
    # GPTBot and * share the Disallow: /, and all four agents read
    # blocked. The "empty group" imagined here cannot exist
    # mid-file; only a trailing user-agent line (N4b) is a group
    # with no rules. The parser's merge behavior is correct.
    r = base_records(robots=rec(200, body="User-agent: GPTBot\n\nUser-agent: *\nDisallow: /\n"))
    assert audit_check(r, "robots_txt")["status"] == "FAIL"


def test_n4b_trailing_empty_named_group_is_warn():
    r = base_records(robots=rec(200, body="User-agent: *\nDisallow: /\n\nUser-agent: GPTBot\n"))
    assert audit_check(r, "robots_txt")["status"] == "WARN"


def test_n4c_named_allow_only_group_is_warn():
    r = base_records(robots=rec(200, body="User-agent: GPTBot\nAllow: /\n\nUser-agent: *\nDisallow: /\n"))
    assert audit_check(r, "robots_txt")["status"] == "WARN"


# --- N5: llms.txt Windows-1252 artifacts ---
def test_n5a_curly_quote_index_is_pass():
    r = base_records(llms=rec(200, body="# Index\n\n- [“Docs”](/docs)\n- [Guide](/guide)\n"))
    assert audit_check(r, "llms_txt")["status"] == "PASS"


def test_n5b_curly_quote_frontmatter_only_is_warn():
    r = base_records(llms=rec(200, body="---\ntitle: Site\nurl: “https://x.example/”\n---\n"))
    assert audit_check(r, "llms_txt")["status"] == "WARN"


def test_n5c_bom_curly_quote_index_is_pass():
    r = base_records(llms=rec(200, body="\ufeff# Index\n\n- [“Docs”](/docs)\n"))
    assert audit_check(r, "llms_txt")["status"] == "PASS"


# --- N6: sitemap.xml non-HTTP-scheme locs ---
def test_n6a_mailto_only_locs_is_warn():
    r = base_records(sitemap=rec(200, body='<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>mailto:team@x.example</loc></url><url><loc>mailto:info@x.example</loc></url></urlset>'))
    assert audit_check(r, "sitemap")["status"] == "WARN"


def test_n6b_one_https_loc_among_mailto_is_pass():
    r = base_records(sitemap=rec(200, body='<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://x.example/</loc></url><url><loc>mailto:team@x.example</loc></url></urlset>'))
    assert audit_check(r, "sitemap")["status"] == "PASS"


def test_n6c_javascript_only_locs_is_warn():
    r = base_records(sitemap=rec(200, body='<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>javascript:openPage(1)</loc></url></urlset>'))
    assert audit_check(r, "sitemap")["status"] == "WARN"


# --- N7: Tamil, Telugu, Marathi, Punjabi challenge phrases ---
def test_n7a_ta_human_check():
    assert verdict(200, body="<html><body><p>நீங்கள் ரோபோ இல்லை என்பதை உறுதிப்படுத்தவும்</p></body></html>") == ("CHALLENGED", "Generic")


def test_n7b_te_human_check():
    assert verdict(200, body="<html><body><p>మీరు రోబో కాదని నిర్ధారించండి</p></body></html>") == ("CHALLENGED", "Generic")


def test_n7c_mr_human_check():
    assert verdict(200, body="<html><body><p>तुम्ही रोबोट नाही याची पुष्टी करा</p></body></html>") == ("CHALLENGED", "Generic")


def test_n7d_pa_human_check():
    assert verdict(200, body="<html><body><p>ਤੁਸੀਂ ਰੋਬੋਟ ਨਹੀਂ ਹੋ ਇਸ ਦੀ ਪੁਸ਼ਟੀ ਕਰੋ</p></body></html>") == ("CHALLENGED", "Generic")


def test_n7e_ta_on_article_is_open():
    assert verdict(200, body=BIG_ARTICLE + "<p>நீங்கள் ரோபோ இல்லை என்பதை உறுதிப்படுத்தவும்</p>") == ("OPEN", None)


def test_n7f_ta_fragment_alone_is_open():
    assert verdict(200, body="<html><body><p>ரோபோ</p></body></html>") == ("OPEN", None)


# --- N8: meta-description-only challenge phrases ---
def test_n8a_meta_description_phrase_content_free_is_challenge():
    assert verdict(200, body='<html><head><meta name="description" content="Verify you are human"></head><body></body></html>') == ("CHALLENGED", "Generic")


def test_n8b_meta_description_phrase_on_article_is_open():
    assert verdict(200, body='<html><head><meta name="description" content="Verify you are human"></head><body>' + BIG_ARTICLE + '</body></html>') == ("OPEN", None)


def test_n8c_meta_description_phrase_small_content_is_open():
    assert verdict(200, body='<html><head><meta name="description" content="Verify you are human"></head><body><p>A short real paragraph about the site and what it offers visitors today.</p></body></html>') == ("OPEN", None)
