"""Wave 23 battery v15 regression pins (see validation/wave23/
HANDCLASS-15.md for the hand classifications). Shapes: stray
text nodes inside <picture>, HTTP 418 responses, robots.txt
wildcard-group placement, llms.txt frontmatter containing
markdown, sitemap <loc> uppercase schemes, challenge text
inside <slot> elements, challenge phrases in Greek/Czech/
Hungarian/Romanian, and HTTP-date Retry-After values.
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
DATE_RA = "Wed, 21 Oct 2015 07:28:00 GMT"

EL_PHRASE = "Επιβεβαιώστε ότι δεν είστε ρομπότ"
CS_PHRASE = "Potvrďte, že nejste robot"
HU_PHRASE = "Kérjük, erősítse meg, hogy Ön nem robot"
RO_PHRASE = "Confirmați că nu sunteți un robot"


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


# --- Q1: stray text nodes inside <picture> ---
def test_q1a_picture_text_with_paragraph_is_open():
    body = ("<html><body>" + PARA +
            '<picture><source srcset="gate.jpg">Verify you are human'
            '<img src="gate.jpg" alt="A scenic photo"></picture>'
            "</body></html>")
    assert verdict(200, body=body) == ("OPEN", None)


def test_q1b_picture_text_only_is_challenge():
    body = ('<html><body><picture><source srcset="gate.jpg">'
            'Verify you are human'
            '<img src="gate.jpg" alt="A scenic photo"></picture>'
            "</body></html>")
    assert verdict(200, body=body) == ("CHALLENGED", "Generic")


def test_q1c_picture_text_on_article_is_open():
    body = (BIG_ARTICLE + '<picture>Verify you are human'
            '<img src="gate.jpg" alt="A scenic photo"></picture>')
    assert verdict(200, body=body) == ("OPEN", None)


def test_q1d_picture_without_phrase_is_open():
    body = ('<html><body><picture><source srcset="a.jpg">'
            '<img src="a.jpg" alt="A scenic photo"></picture>'
            "</body></html>")
    assert verdict(200, body=body) == ("OPEN", None)


def test_q1e_picture_asset_filename_on_article_is_open():
    body = (BIG_ARTICLE + '<picture><source '
            'srcset="verify-you-are-human.png">'
            '<img src="verify-you-are-human.png" '
            'alt="A scenic photo"></picture>')
    assert verdict(200, body=body) == ("OPEN", None)


# --- Q2: HTTP 418 ---
def test_q2a_418_teapot_body_is_walled():
    body = ("<html><body><p>I'm a teapot. This server is a "
            "teapot; it declines to brew your request.</p>"
            "</body></html>")
    assert verdict(418, body=body) == ("WALLED", None)


def test_q2b_418_with_challenge_phrase_is_walled_generic():
    body = ("<html><body><p>Verify you are human to "
            "continue.</p></body></html>")
    assert verdict(418, body=body) == ("WALLED", "Generic")


def test_q2c_418_with_cloudflare_challenge_is_challenged():
    body = ("<html><head><title>Just a moment...</title></head>"
            "<body>Checking your browser before accessing the "
            "site.</body></html>")
    assert verdict(418, headers={"cf-ray": "8f00-example",
                                 "server": "cloudflare"},
                   body=body) == ("CHALLENGED", "Cloudflare")


def test_q2d_418_empty_body_is_walled():
    assert verdict(418, body="") == ("WALLED", None)


# --- Q3: robots.txt wildcard-group placement ---
def test_q3a_named_block_then_wildcard_allow_is_warn():
    body = ("User-agent: GPTBot\nDisallow: /\n\n"
            "User-agent: *\nAllow: /\n")
    r = base_records(robots=rec(200, body=body))
    assert audit_check(r, "robots_txt")["status"] == "WARN"


def test_q3b_wildcard_block_then_named_allow_is_warn():
    body = ("User-agent: *\nDisallow: /\n\n"
            "User-agent: ClaudeBot\nAllow: /\n")
    r = base_records(robots=rec(200, body=body))
    assert audit_check(r, "robots_txt")["status"] == "WARN"


def test_q3c_wildcard_allow_mid_file_is_warn():
    body = ("User-agent: GPTBot\nDisallow: /\n\n"
            "User-agent: *\nAllow: /\n\n"
            "User-agent: CCBot\nDisallow: /\n")
    r = base_records(robots=rec(200, body=body))
    assert audit_check(r, "robots_txt")["status"] == "WARN"


def test_q3d_two_wildcard_groups_allow_cancels_is_pass():
    body = ("User-agent: *\nDisallow: /\n\n"
            "User-agent: *\nAllow: /\n")
    r = base_records(robots=rec(200, body=body))
    assert audit_check(r, "robots_txt")["status"] == "PASS"


# --- Q4: llms.txt frontmatter containing markdown ---
FM_LINKS = ("---\ntitle: Site\n"
            "description: See [Docs](https://x.example/docs) and "
            "[Guide](https://x.example/guide) for details.\n---\n")


def test_q4a_frontmatter_links_title_only_body_is_warn():
    r = base_records(llms=rec(200, body=FM_LINKS + "# Site\n"))
    assert audit_check(r, "llms_txt")["status"] == "WARN"


def test_q4b_frontmatter_links_real_index_is_pass():
    body = (FM_LINKS + "# Index\n\n"
            "- [Docs](https://x.example/docs)\n"
            "- [API](https://x.example/api)\n")
    r = base_records(llms=rec(200, body=body))
    assert audit_check(r, "llms_txt")["status"] == "PASS"


def test_q4c_frontmatter_only_with_links_is_warn():
    r = base_records(llms=rec(200, body=FM_LINKS))
    assert audit_check(r, "llms_txt")["status"] == "WARN"


def test_q4d_frontmatter_links_one_body_link_is_pass():
    body = FM_LINKS + "# Index\n\n- [Docs](https://x.example/docs)\n"
    r = base_records(llms=rec(200, body=body))
    assert audit_check(r, "llms_txt")["status"] == "PASS"


# --- Q5: sitemap <loc> uppercase schemes ---
def test_q5a_uppercase_https_loc_is_pass():
    body = ('<?xml version="1.0" encoding="UTF-8"?>'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            "<url><loc>HTTPS://EXAMPLE.COM/PAGE</loc></url></urlset>")
    r = base_records(sitemap=rec(200, body=body))
    assert audit_check(r, "sitemap")["status"] == "PASS"


def test_q5b_uppercase_https_index_loc_is_pass():
    body = ('<?xml version="1.0" encoding="UTF-8"?>'
            '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            "<sitemap><loc>HTTPS://EXAMPLE.COM/SITEMAP-1.XML</loc>"
            "</sitemap></sitemapindex>")
    r = base_records(sitemap=rec(200, body=body))
    assert audit_check(r, "sitemap")["status"] == "PASS"


def test_q5c_mixed_case_scheme_loc_is_pass():
    body = ('<?xml version="1.0"?>'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            "<url><loc>HtTpS://example.com/x</loc></url></urlset>")
    r = base_records(sitemap=rec(200, body=body))
    assert audit_check(r, "sitemap")["status"] == "PASS"


def test_q5d_uppercase_ftp_loc_is_warn():
    body = ('<?xml version="1.0"?>'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            "<url><loc>FTP://EXAMPLE.COM/FILE</loc></url></urlset>")
    r = base_records(sitemap=rec(200, body=body))
    assert audit_check(r, "sitemap")["status"] == "WARN"


# --- Q6: challenge text inside <slot> ---
def test_q6a_slot_only_is_challenge():
    body = ("<html><body><slot>Verify you are human</slot>"
            "</body></html>")
    assert verdict(200, body=body) == ("CHALLENGED", "Generic")


def test_q6b_slot_on_article_is_open():
    body = BIG_ARTICLE + "<slot>Verify you are human</slot>"
    assert verdict(200, body=body) == ("OPEN", None)


def test_q6c_slot_with_paragraph_is_challenge():
    body = ("<html><body>" + PARA +
            '<slot name="gate">Verify you are human</slot>'
            "</body></html>")
    assert verdict(200, body=body) == ("CHALLENGED", "Generic")


def test_q6d_slot_inside_template_with_paragraph_is_open():
    body = ("<html><body>" + PARA +
            "<template><slot>Verify you are human</slot>"
            "</template></body></html>")
    assert verdict(200, body=body) == ("OPEN", None)


# --- Q7: Greek / Czech / Hungarian / Romanian phrases ---
def test_q7a_greek_phrase_is_challenge():
    body = "<html><body><p>%s</p></body></html>" % EL_PHRASE
    assert verdict(403, body=body) == ("CHALLENGED", "Generic")


def test_q7b_czech_phrase_is_challenge():
    body = "<html><body><p>%s</p></body></html>" % CS_PHRASE
    assert verdict(403, body=body) == ("CHALLENGED", "Generic")


def test_q7c_hungarian_phrase_is_challenge():
    body = "<html><body><p>%s</p></body></html>" % HU_PHRASE
    assert verdict(403, body=body) == ("CHALLENGED", "Generic")


def test_q7d_romanian_phrase_is_challenge():
    body = "<html><body><p>%s</p></body></html>" % RO_PHRASE
    assert verdict(403, body=body) == ("CHALLENGED", "Generic")


def test_q7e_greek_phrase_on_article_is_open():
    body = BIG_ARTICLE + "<p>%s</p>" % EL_PHRASE
    assert verdict(200, body=body) == ("OPEN", None)


def test_q7f_greek_fragment_is_open():
    body = "<html><body><p>ρομπότ</p></body></html>"
    assert verdict(200, body=body) == ("OPEN", None)


def test_q7g_greek_phrase_in_style_only_is_open():
    body = ("<html><head><style>.gate::after { content: '%s'; }"
            "</style></head><body>%s</body></html>"
            % (EL_PHRASE, PARA))
    assert verdict(200, body=body) == ("OPEN", None)


# --- Q8: HTTP-date Retry-After ---
def test_q8a_429_date_retry_after_is_rate_limited():
    body = "<html><body><p>Too many requests.</p></body></html>"
    assert verdict(429, headers={"retry-after": DATE_RA},
                   body=body) == ("RATE_LIMITED", None)


def test_q8b_403_date_retry_after_throttle_is_rate_limited():
    body = ("<html><body><p>Too many requests. Please slow "
            "down.</p></body></html>")
    assert verdict(403, headers={"retry-after": DATE_RA},
                   body=body) == ("RATE_LIMITED", None)


def test_q8c_503_date_retry_after_throttle_is_rate_limited():
    body = "<html><body><p>Too many requests.</p></body></html>"
    assert verdict(503, headers={"retry-after": DATE_RA},
                   body=body) == ("RATE_LIMITED", None)


def test_q8d_403_date_retry_after_no_throttle_is_walled():
    body = "<html><body><p>Access denied.</p></body></html>"
    assert verdict(403, headers={"retry-after": DATE_RA},
                   body=body) == ("WALLED", None)
