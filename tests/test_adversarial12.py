"""Wave 20 battery v12 regression pins (see validation/wave20/
HANDCLASS-12.md for the hand classifications). Shapes: iframe-src
routing targets, localized JS-proof phrases, new localized
human-check languages, identity-verification interstitials
(hand-corrected: auth-ambiguous, see PROBLEMS.md), iframe title
attributes, overlay/dialog challenges on error statuses,
precedence pins, inline <details> and accessible-name pins, JSON
captcha-error bodies, and audit edges (robots order, sitemapindex
declarations, empty-target llms links, BOM+CR+frontmatter llms).
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


SITEMAPINDEX = ('<?xml version="1.0"?><sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                '<sitemap><loc>https://x.example/sitemap-a.xml</loc></sitemap>'
                '<sitemap><loc>https://x.example/sitemap-b.xml</loc></sitemap></sitemapindex>')


# --- M1: iframe-src routing targets ---
def test_m1a_iframe_captcha_src_is_challenge():
    assert verdict(200, body='<html><body><iframe src="https://challenge.example/captcha/verify"></iframe></body></html>') == ("CHALLENGED", "Generic")


def test_m1b_iframe_content_src_is_open():
    assert verdict(200, body='<html><body><iframe src="https://content.example/article"></iframe></body></html>') == ("OPEN", None)


def test_m1c_iframe_captcha_src_on_article_is_open():
    assert verdict(200, body=BIG_ARTICLE + '<iframe src="https://challenge.example/captcha/verify"></iframe>') == ("OPEN", None)


def test_m1d_iframe_login_src_is_login_gated():
    assert verdict(200, body='<html><body><iframe src="/login"></iframe></body></html>') == ("LOGIN_GATED", None)


# --- M2: localized JS-proof phrases ---
def test_m2a_de_js_proof():
    assert verdict(200, body="<html><body><p>Wir überprüfen Ihren Browser, bitte warten.</p></body></html>") == ("CHALLENGED", "Generic")


def test_m2b_fr_js_proof():
    assert verdict(200, body="<html><body><p>Nous vérifions votre navigateur, veuillez patienter.</p></body></html>") == ("CHALLENGED", "Generic")


def test_m2c_es_js_proof():
    assert verdict(200, body="<html><body><p>Estamos verificando su navegador, por favor espere.</p></body></html>") == ("CHALLENGED", "Generic")


def test_m2d_pt_js_proof():
    assert verdict(200, body="<html><body><p>Estamos verificando o seu navegador, aguarde.</p></body></html>") == ("CHALLENGED", "Generic")


def test_m2e_ja_js_proof():
    assert verdict(200, body="<html><body><p>ブラウザを確認しています。お待ちください。</p></body></html>") == ("CHALLENGED", "Generic")


def test_m2f_de_js_proof_on_article_is_open():
    assert verdict(200, body=BIG_ARTICLE + "<p>Wir überprüfen Ihren Browser, bitte warten.</p>") == ("OPEN", None)


# --- M3: new localized human-check languages ---
def test_m3a_uk_human_check():
    assert verdict(200, body="<html><body><p>Підтвердіть, що ви не робот</p></body></html>") == ("CHALLENGED", "Generic")


def test_m3b_hi_human_check():
    assert verdict(200, body="<html><body><p>कृपया पुष्टि करें कि आप रोबोट नहीं हैं</p></body></html>") == ("CHALLENGED", "Generic")


def test_m3c_ms_human_check():
    assert verdict(200, body="<html><body><p>sahkan bahawa anda bukan robot</p></body></html>") == ("CHALLENGED", "Generic")


def test_m3d_tl_human_check():
    assert verdict(200, body="<html><body><p>kumpirmahin na hindi ka robot</p></body></html>") == ("CHALLENGED", "Generic")


def test_m3e_sw_human_check():
    assert verdict(200, body="<html><body><p>thibitisha kuwa wewe si roboti</p></body></html>") == ("CHALLENGED", "Generic")


def test_m3f_uk_on_article_is_open():
    assert verdict(200, body=BIG_ARTICLE + "<p>Підтвердіть, що ви не робот</p>") == ("OPEN", None)


def test_m3g_fragment_alone_is_open():
    assert verdict(200, body="<html><body><p>не робот</p></body></html>") == ("OPEN", None)


# --- M4: identity-verification interstitials (hand-corrected) ---
def test_m4a_identity_phrase_alone_is_open():
    # Auth-ambiguous (account recovery vs bot gate): the classifier
    # conservatively claims no wall without a challenge/vendor signal.
    assert verdict(200, body="<html><body><p>Please verify your identity to continue.</p></body></html>") == ("OPEN", None)


def test_m4b_identity_phrase_on_login_url_is_login_gated():
    assert verdict(200, body="<html><body><p>Please verify your identity to continue.</p></body></html>", url=LOGIN) == ("LOGIN_GATED", None)


def test_m4c_identity_phrase_on_article_is_open():
    assert verdict(200, body=BIG_ARTICLE + "<p>Please verify your identity to continue.</p>") == ("OPEN", None)


def test_m4d_identity_phrase_with_button_no_form_is_open():
    assert verdict(200, body='<html><body><p>Please verify your identity to continue.</p><button>Continue</button></body></html>') == ("OPEN", None)


# --- M5: iframe title attributes ---
def test_m5a_iframe_title_phrase_is_challenge():
    assert verdict(200, body='<html><body><iframe title="Verify you are human" src="https://x.example/vid"></iframe></body></html>') == ("CHALLENGED", "Generic")


def test_m5b_iframe_title_phrase_on_article_is_open():
    assert verdict(200, body=BIG_ARTICLE + '<iframe title="Verify you are human" src="https://x.example/vid"></iframe>') == ("OPEN", None)


# --- M6: overlay/dialog on error statuses ---
def test_m6a_overlay_challenge_on_403():
    assert verdict(403, body='<html><body><div class="modal-overlay">Verify you are human</div></body></html>') == ("CHALLENGED", "Generic")


def test_m6b_dialog_challenge_on_403():
    assert verdict(403, body='<html><body><dialog open>Verify you are human</dialog></body></html>') == ("CHALLENGED", "Generic")


# --- M8: precedence pins ---
def test_m8a_401_with_human_check_is_challenge():
    assert verdict(401, body="<html><body><p>Verify you are human</p></body></html>") == ("CHALLENGED", "Generic")


def test_m8b_429_with_human_check_is_challenge():
    assert verdict(429, body="<html><body><p>Verify you are human</p></body></html>") == ("CHALLENGED", "Generic")


def test_m8c_503_with_js_proof_is_challenge():
    assert verdict(503, body="<html><body><p>Verifying your browser, please wait.</p></body></html>") == ("CHALLENGED", "Generic")


def test_m8d_human_check_on_login_url_is_login_gated():
    assert verdict(200, body="<html><body><p>Verify you are human</p></body></html>", url=LOGIN) == ("LOGIN_GATED", None)


def test_m8e_meta_refresh_to_challenge_on_login_url_is_challenge():
    assert verdict(200, body='<html><head><meta http-equiv="refresh" content="0; url=/challenge/captcha"></head><body></body></html>', url=LOGIN) == ("CHALLENGED", "Generic")


# --- M9: inline-content and accessible-name pins ---
def test_m9a_details_challenge_on_article_is_open():
    assert verdict(200, body=BIG_ARTICLE + "<details open><summary>Check</summary><p>Verify you are human</p></details>") == ("OPEN", None)


def test_m9b_button_aria_label_challenge_is_challenge():
    assert verdict(200, body='<html><body><button aria-label="Verify you are human">Go</button></body></html>') == ("CHALLENGED", "Generic")


def test_m9c_button_aria_label_on_article_is_open():
    assert verdict(200, body=BIG_ARTICLE + '<button aria-label="Verify you are human">Go</button>') == ("OPEN", None)


# --- M10: JSON captcha-error body ---
def test_m10a_json_captcha_error_is_challenge():
    assert verdict(200, body='{"error": "captcha required", "code": "challenge"}') == ("CHALLENGED", "Generic")


# --- M7: audit edges ---
def test_m7a_named_carveout_after_wildcard_is_warn():
    r = base_records(robots=rec(200, body="User-agent: *\nDisallow: /\n\nUser-agent: GPTBot\nAllow: /\n"))
    assert audit_check(r, "robots_txt")["status"] == "WARN"


def test_m7b_sitemapindex_declaration_is_pass():
    r = base_records(robots=rec(200, body="User-agent: *\nAllow: /\nSitemap: https://x.example/sitemap.xml\n"),
                     sitemap=rec(200, body=SITEMAPINDEX))
    assert audit_check(r, "sitemap")["status"] == "PASS"


def test_m7c_empty_target_llms_link_is_warn():
    r = base_records(llms=rec(200, body="# Docs\n\n[Guide]()\n"))
    assert audit_check(r, "llms_txt")["status"] == "WARN"


def test_m7d_bom_cr_frontmatter_llms_is_pass():
    r = base_records(llms=rec(200, body="\ufeff---\rkey: https://meta.example\r---\r# Title\r[Guide](https://x.example/guide)\r"))
    assert audit_check(r, "llms_txt")["status"] == "PASS"


def test_m7e_wildcard_allow_with_private_disallow_is_warn():
    r = base_records(robots=rec(200, body="User-agent: *\nAllow: /\nDisallow: /private\n"))
    assert audit_check(r, "robots_txt")["status"] == "WARN"
