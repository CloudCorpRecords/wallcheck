"""Wave 17 battery v9 regression pins (see validation/wave17/
HANDCLASS-9.md for the hand classifications). Shapes: noscript-only
markers on served pages, title-only wall text on small content
pages, no-store/no-cache headers as the only header signal, QR-code
login prompts, robots Sitemap lines inside comments, llms.txt
bodies with HTML entities, Nordic multi-language challenge pages,
full-screen overlay challenges, and the script-boundary captcha
re-test. Plus guards for each fix's blast radius.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from wallcheck.classify import classify  # noqa: E402
from wallcheck.audit import evaluate_audit  # noqa: E402

LOGIN = "https://site.example/login"


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


def robots_records(robots_body):
    return {
        "robots": rec(200, {"Content-Type": "text/plain"}, robots_body),
        "llms": rec(404, {}, "not found"),
        "sitemap": rec(404, {}, "not found"),
        "homepage": rec(200, {"Content-Type": "text/html"},
                        "<html><head><title>x</title></head><body>x</body></html>"),
        "signed": rec(404, {}, "not found"),
    }


def llms_records(body, content_type="text/plain"):
    return {
        "robots": rec(200, {"Content-Type": "text/plain"},
                      "User-agent: *\nAllow: /\n"),
        "llms": rec(200, {"Content-Type": content_type}, body),
        "sitemap": rec(404, {}, "not found"),
        "homepage": rec(200, {"Content-Type": "text/html"},
                        "<html><head><title>x</title></head><body>x</body></html>"),
        "signed": rec(404, {}, "not found"),
    }


def sitemap_records(robots_body, sitemap_rec):
    records = robots_records(robots_body)
    records["sitemap"] = sitemap_rec
    return records


SENTENCE = ("The city council approved the new transit plan on Tuesday, "
            "expanding bus service to three additional neighborhoods "
            "over the next year. ")
ARTICLE = "<p>" + SENTENCE * 220 + "</p>"  # >16 KB served page
PARA = ("The city council approved the new transit plan on Tuesday, "
        "expanding bus service to three additional neighborhoods. "
        "Local riders welcomed the announcement at the town hall. ")


def page(body, title="News"):
    return ("<html><head><title>%s</title></head><body>%s</body></html>"
            % (title, body))


# --- J1: noscript-only markers on served pages ---

def test_j1a_article_plus_noscript_challenge_is_open():
    body = "<p>%s</p><noscript>Please enable JavaScript and verify " \
        "you are human to continue.</noscript>" % (SENTENCE * 5)
    assert verdict(200, {}, page(body)) == ("OPEN", None)


def test_j1b_noscript_only_challenge():
    body = "<noscript>Please enable JavaScript and verify you are " \
        "human to continue.</noscript>"
    assert verdict(200, {}, page(body)) == ("CHALLENGED", "Generic")


def test_j1c_small_para_plus_noscript_jsproof_is_open():
    body = "<p>%s</p><noscript>This site requires JavaScript. " \
        "Please enable JavaScript to continue.</noscript>" % PARA
    assert verdict(200, {}, page(body)) == ("OPEN", None)


def test_j1d_spinner_plus_noscript_challenge():
    body = "<div>Loading...</div><noscript>Please enable JavaScript " \
        "and verify you are human to continue.</noscript>"
    assert verdict(200, {}, page(body)) == ("CHALLENGED", "Generic")


def test_j1e_article_plus_noscript_vendor_is_open():
    body = "<p>%s</p><noscript>perimeterx</noscript>" % (SENTENCE * 5)
    assert verdict(200, {}, page(body)) == ("OPEN", None)


def test_j1f_403_noscript_only_challenge():
    body = "<noscript>verify you are human</noscript>"
    assert verdict(403, {}, page(body)) == ("CHALLENGED", "Generic")


def test_j1g_body_challenge_plus_neutral_noscript_still_fires():
    body = "<p>Verify you are human</p><noscript>JavaScript is " \
        "required for this site.</noscript>"
    assert verdict(200, {}, page(body)) == ("CHALLENGED", "Generic")


# --- J2: title-only wall text on small content pages ---

def test_j2a_small_content_page_title_phrase_is_open():
    assert verdict(200, {}, page("<p>%s</p>" % PARA,
                                  "Verify you are human")) == ("OPEN", None)


def test_j2b_title_only_plus_spinner_is_challenge():
    assert verdict(200, {},
                   page("<div>Loading...</div>",
                        "Verify you are human")) == ("CHALLENGED", "Generic")


def test_j2c_content_page_title_vendor_is_open():
    assert verdict(200, {}, page("<p>%s</p>" % PARA,
                                  "PerimeterX protection")) == ("OPEN", None)


def test_j2d_content_page_title_jsproof_is_open():
    assert verdict(200, {}, page("<p>%s</p>" % PARA,
                                  "Checking your browser")) == ("OPEN", None)


def test_j2e_refusal_body_title_traffic_is_walled():
    body = "Access denied. Your request was blocked by our security " \
        "policy."
    assert verdict(403, {}, page("<p>%s</p>" % body,
                                  "Unusual traffic from your network "
                                  "\u2014 please verify")) == ("WALLED", None)


def test_j2g_body_challenge_neutral_title_still_fires():
    assert verdict(200, {}, page("<p>Verify you are human</p>",
                                  "Welcome")) == ("CHALLENGED", "Generic")


# --- J3: no-store/no-cache headers as the only header signal ---

NOSTORE = {"Cache-Control": "no-store, no-cache"}


def test_j3a_loading_stub_plus_nostore_is_open():
    assert verdict(200, NOSTORE, page("<p>Please wait, loading your "
                                       "content...</p>")) == ("OPEN", None)


def test_j3b_empty_403_plus_nostore_is_walled():
    assert verdict(403, NOSTORE, "") == ("WALLED", None)


def test_j3c_challenge_plus_nostore_is_challenge():
    assert verdict(200, NOSTORE,
                   page("<p>Verify you are human</p>")) == ("CHALLENGED",
                                                             "Generic")


def test_j3d_jsproof_stub_plus_nostore_is_challenge():
    assert verdict(200, NOSTORE, page("<p>Please wait while we check "
                                       "your browser</p>")) == ("CHALLENGED",
                                                                "Generic")


# --- J4: QR-code login prompts ---

def test_j4a_qr_prompt_is_login_gated():
    body = "<p>Scan the QR code with your phone to sign in</p>" \
        "<img src=\"/qr.png\">"
    assert verdict(200, {}, page(body), "https://site.example/qr") == \
        ("LOGIN_GATED", None)


def test_j4b_article_about_qr_login_is_open():
    body = "<p>%s</p>" % ("How QR code sign-in works, and why sites "
        "offer it as an alternative to passwords. " * 4)
    assert verdict(200, {}, page(body), "https://site.example/qr") == \
        ("OPEN", None)


def test_j4c_app_download_qr_is_open():
    body = "<p>Scan the QR code to download our app</p>" \
        "<img src=\"/qr.png\">"
    assert verdict(200, {}, page(body), "https://site.example/qr") == \
        ("OPEN", None)


def test_j4d_qr_prompt_at_login_url():
    body = "<p>Scan the QR code with your phone to sign in</p>" \
        "<img src=\"/qr.png\">"
    assert verdict(200, {}, page(body), LOGIN) == ("LOGIN_GATED", None)


def test_j4e_qr_wording_bare_link_is_open():
    body = "<p>Scan the QR code to sign in</p>" \
        "<a href=\"/app\">Get the app</a>"
    assert verdict(200, {}, page(body), "https://site.example/qr") == \
        ("OPEN", None)


def test_j4f_canvas_qr_prompt_is_login_gated():
    body = "<p>Scan the QR code to sign in</p><canvas id=\"qr\"></canvas>"
    assert verdict(200, {}, page(body), "https://site.example/qr") == \
        ("LOGIN_GATED", None)


# --- J5: robots Sitemap lines inside comments ---

def test_j5a_commented_sitemap_only():
    records = robots_records("# Sitemap: https://x.example/sitemap.xml\n"
                             "User-agent: *\nAllow: /\n")
    assert audit_check(records, "robots_txt")["status"] == "PASS"
    sitemap = audit_check(records, "sitemap")
    assert sitemap["status"] == "WARN"
    assert not any("VIA_ROBOTS_DECLARATION" in e
                   for e in sitemap["evidence"])


def test_j5b_commented_plus_real_sitemap():
    sitemap_rec = rec(200, {"Content-Type": "application/xml"},
                      "<urlset><url><loc>https://x.example/a</loc>"
                      "</url></urlset>")
    records = sitemap_records("# Sitemap: https://x.example/trap.xml\n"
                              "Sitemap: https://x.example/s2.xml\n"
                              "User-agent: *\nAllow: /\n", sitemap_rec)
    sitemap = audit_check(records, "sitemap")
    assert sitemap["status"] == "PASS"
    assert any("VIA_ROBOTS_DECLARATION" in e
               for e in sitemap["evidence"])
    assert not any("trap" in e for e in sitemap["evidence"])


def test_j5c_inline_comment_sitemap_not_a_declaration():
    records = robots_records("User-agent: *\nDisallow: /private "
                             "# Sitemap: https://x.example/trap.xml\n")
    assert audit_check(records, "robots_txt")["status"] == "WARN"
    sitemap = audit_check(records, "sitemap")
    assert not any("VIA_ROBOTS_DECLARATION" in e
                   for e in sitemap["evidence"])


def test_j5d_commented_disallow_is_not_a_directive():
    records = robots_records("# Disallow: /\nUser-agent: *\nAllow: /\n")
    assert audit_check(records, "robots_txt")["status"] == "PASS"


# --- J6: llms.txt bodies with HTML entities ---

def test_j6a_amp_in_link_targets_passes():
    body = "# Index\n\n[Docs](/docs?a=1&amp;b=2)\n"
    assert audit_check(llms_records(body), "llms_txt")["status"] == "PASS"


def test_j6b_escaped_anchor_with_url_passes():
    body = "&lt;a href=\"https://example.com/docs\"&gt;Click " \
        "here&lt;/a&gt;"
    assert audit_check(llms_records(body), "llms_txt")["status"] == "PASS"


def test_j6c_entity_encoded_json_error_doc_fails():
    body = "{&quot;error&quot;: &quot;not found&quot;}"
    check = audit_check(llms_records(body), "llms_txt")
    assert check["status"] == "FAIL"
    assert "JSON_ERROR_DOC" in check["evidence"]


def test_j6d_entity_encoded_json_data_doc_warns():
    body = "{&quot;title&quot;: &quot;Docs&quot;}"
    check = audit_check(llms_records(body), "llms_txt")
    assert check["status"] == "WARN"
    assert "JSON_NOT_LLMS" in check["evidence"]


def test_j6e_entity_encoded_slash_is_not_a_path():
    body = "Visit &#47;docs for the index"
    check = audit_check(llms_records(body), "llms_txt")
    assert check["status"] == "WARN"
    assert "LLMS_STUB" in check["evidence"]


# --- J7: Nordic multi-language challenge pages ---

def test_j7a_swedish_challenge():
    assert verdict(403, {},
                   page("<p>Bekr\u00e4fta att du inte \u00e4r en "
                        "robot.</p>")) == ("CHALLENGED", "Generic")


def test_j7b_finnish_challenge():
    assert verdict(403, {},
                   page("<p>Vahvista, ettet ole robotti.</p>")) == \
        ("CHALLENGED", "Generic")


def test_j7c_danish_challenge():
    assert verdict(403, {},
                   page("<p>Bekr\u00e6ft, at du ikke er en "
                        "robot.</p>")) == ("CHALLENGED", "Generic")


def test_j7d_norwegian_challenge():
    assert verdict(403, {},
                   page("<p>Bekreft at du ikke er en robot.</p>")) == \
        ("CHALLENGED", "Generic")


def test_j7e_swedish_plus_finnish_mixed():
    body = "<p>Bekr\u00e4fta att du inte \u00e4r en robot. " \
        "Vahvista, ettet ole robotti.</p>"
    assert verdict(403, {}, page(body)) == ("CHALLENGED", "Generic")


def test_j7f_article_quoting_swedish_phrase_is_open():
    body = ARTICLE + "<p>As one Swedish site puts it: " \
        "Bekr\u00e4fta att du inte \u00e4r en robot.</p>"
    assert verdict(200, {}, page(body)) == ("OPEN", None)


def test_j7g_codeswitched_fragments_are_walled():
    assert verdict(403, {},
                   page("<p>Verify / eres humano</p>")) == ("WALLED", None)


# --- J8: full-screen overlay challenges ---

def test_j8a_article_plus_overlay_challenge():
    body = ARTICLE + "<div class=\"overlay-modal\" " \
        "style=\"position:fixed;inset:0\"><p>Verify you are human</p>" \
        "<input type=\"checkbox\"></div>"
    assert verdict(200, {}, page(body)) == ("CHALLENGED", "Generic")


def test_j8b_article_plus_cookie_overlay_is_open():
    body = ARTICLE + "<div class=\"overlay-modal\" " \
        "style=\"position:fixed;inset:0\"><p>We use cookies to improve " \
        "your experience</p></div>"
    assert verdict(200, {}, page(body)) == ("OPEN", None)


def test_j8c_article_plus_prose_mention_is_open():
    body = ARTICLE + "<p>This site uses verification to prevent " \
        "bots.</p>"
    assert verdict(200, {}, page(body)) == ("OPEN", None)


def test_j8d_small_page_overlay_challenge():
    body = "<div class=\"overlay\"><p>Verify you are human</p></div>"
    assert verdict(200, {}, page(body)) == ("CHALLENGED", "Generic")


def test_j8e_article_plus_overlay_jsproof():
    body = ARTICLE + "<div class=\"overlay\"><p>Checking your " \
        "browser</p></div>"
    assert verdict(200, {}, page(body)) == ("CHALLENGED", "Generic")


def test_j8f_stylesheet_positioned_modal_challenge():
    body = ARTICLE + "<div class=\"modal-content\"><p>Verify you are " \
        "human</p></div>"
    assert verdict(200, {}, page(body)) == ("CHALLENGED", "Generic")


def test_j8g_newsletter_modal_is_open():
    body = ARTICLE + "<div class=\"modal\"><p>Subscribe to our " \
        "newsletter</p></div>"
    assert verdict(200, {}, page(body)) == ("OPEN", None)


def test_j8h_commented_overlay_does_not_fire():
    body = ARTICLE + "<!-- <div class=\"overlay\">Verify you are " \
        "human</div> -->"
    assert verdict(200, {}, page(body)) == ("OPEN", None)


# --- J9: script-boundary captcha re-test ---

def test_j9a_token_split_across_script_boundary_is_open():
    body = "<p>Please complete the cap</p>" \
        "<script>var suffix=\"tcha\";</script>"
    assert verdict(200, {}, page(body)) == ("OPEN", None)


# --- W17-007: rubygems.org live catch (round-13 LOGIN_GATED overturned) ---

def test_w17_rubygems_shape_served_homepage_is_open():
    # The live rubygems.org homepage: real served content whose only
    # "webauthn" signals are asset filenames in the import map,
    # plus ordinary forms. Both the visible-text wording rule and
    # the served-page size gate must keep this OPEN.
    body = ARTICLE + "<script type=\"importmap\">{\"imports\": " \
        "{\"webauthn-json\": \"/assets/webauthn-json-74adc0e8.js\"}}" \
        "</script><form action=\"/search\"><input name=\"query\"></form>"
    assert verdict(200, {}, page(body)) == ("OPEN", None)


def test_w17_real_passkey_prompt_with_webauthn_assets_still_fires():
    # A real prompt that also loads webauthn assets: the wording is
    # in visible text, so the visible-text rule must not break it.
    body = "<p>Sign in with your passkey</p><button>Continue with " \
        "passkey</button><script src=\"/assets/webauthn-json.js\">" \
        "</script>"
    assert verdict(200, {}, page(body),
                   "https://site.example/passkey") == ("LOGIN_GATED", None)


def test_w17_large_page_passkey_form_is_open():
    # Size-gate boundary, documented: a full served page carrying a
    # passkey form is not "only" a form. Large login pages at login
    # URLs are still caught by the login heuristic.
    body = ARTICLE + "<p>Sign in with your passkey</p><button>" \
        "Continue</button>"
    assert verdict(200, {}, page(body)) == ("OPEN", None)


def test_w17_newsletter_form_script_only_magic_link_wording_is_open():
    # The magic-link wording lives only in script text: the
    # presented form is just an email input (a newsletter form),
    # not a link form — the wording key must be visible.
    body = "<p>Subscribe for updates</p><form><input type=\"email\" " \
        "name=\"email\"></form><script>var x = \"magic link\";</script>"
    assert verdict(200, {}, page(body)) == ("OPEN", None)


def test_w17_code_input_script_only_wording_still_fires():
    # Deliberate asymmetry, documented: the code INPUT is itself
    # presented barrier machinery, so a code input plus auth wording
    # is a form even when the wording rides in script text. The
    # served-page size gate (not the wording rule) is what keeps
    # large served pages from misfiring here.
    body = "<p>Enter the code below</p><form><input name=\"otp\">" \
        "</form><script>var x = \"verification code\";</script>"
    assert verdict(200, {}, page(body),
                   "https://site.example/verify") == ("LOGIN_GATED", None)
