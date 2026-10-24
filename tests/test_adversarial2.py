"""Wave 10 adversarial battery v2 — hand-classified fixtures.

Each case pins the hand verdict from validation/wave10/HANDCLASS-2.md
BEFORE the classifier result is consulted. A failing case is a defect
candidate, fixed generalized or ledgered as an honest limitation.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from wallcheck.classify import classify  # noqa: E402
from wallcheck.audit import evaluate_audit  # noqa: E402


def C(status, headers=None, body="", url="https://site.example/"):
    return classify(status, headers or {}, body, final_url=url)


def verdict(status, headers=None, body="", url="https://site.example/"):
    r = C(status, headers, body, url)
    return r["verdict"], r["vendor"]


# B1 — mixed / contradictory vendor signals
def test_b1a_cf_presence_datadome_wall():
    assert verdict(403, {"cf-ray": "abc", "server": "cloudflare",
                         "x-datadome": "yes"},
                  "DataDome verification datadome") == ("CHALLENGED", "DataDome")


def test_b1c_edgesuite_plus_kasada():
    assert verdict(403, {}, "Access Denied errors.edgesuite.net "
                  "<script src=kpsdk></script>") == ("WALLED", "Akamai")


def test_b1d_imperva_marker_datadome_header():
    assert verdict(403, {"x-datadome": "yes"},
                  "incapsula protection") == ("CHALLENGED", "DataDome")


def test_b1e_served_page_vendor_mentions():
    big = "<html><body>" + "article about perimeterx " * 800 + "</body></html>"
    assert verdict(200, {"cf-ray": "abc"}, big) == ("OPEN", None)


# B2 — 401 / 403 login hybrids
def test_b2a_401_at_login():
    assert verdict(401, {}, "Unauthorized - please sign in",
                  "https://site.example/login") == ("LOGIN_GATED", None)


def test_b2b_403_at_login_plain_form():
    form = '<form action="/login"><input name="user"><input name="pw"></form>'
    assert verdict(403, {}, form,
                  "https://site.example/login") == ("WALLED", None)


def test_b2c_401_json_api():
    assert verdict(401, {}, '{"error": "invalid_token"}',
                  "https://api.example/data") == ("LOGIN_GATED", None)


def test_b2d_403_json_api():
    assert verdict(403, {}, '{"error": "forbidden"}',
                  "https://api.example/data") == ("WALLED", None)


# B3 — geo-blocks and legal refusals
def test_b3a_403_region_text():
    assert verdict(403, {}, "This content is not available in your region") \
        == ("WALLED", None)


def test_b3b_200_geo_block_page():
    body = ("<html><body><h1>Not available</h1><p>This service is not "
            "available in your country.</p><a href=/support>Support</a>"
            "</body></html>")
    assert verdict(200, {}, body) == ("WALLED", None)


def test_b3c_451_legal():
    assert verdict(451, {}, "Unavailable for legal reasons") == ("WALLED", None)


# B4 — meta-refresh and JS-redirect walls
def test_b4a_refresh_to_challenge():
    body = '<html><head><meta http-equiv="refresh" content="0; url=/challenge/">' \
        "</head><body></body></html>"
    assert verdict(200, {}, body) == ("CHALLENGED", "Generic")


def test_b4b_refresh_to_login():
    body = '<html><head><meta http-equiv="refresh" content="0; url=/login">' \
        "</head><body></body></html>"
    assert verdict(200, {}, body) == ("LOGIN_GATED", None)


def test_b4c_js_redirect_to_verify():
    body = '<html><body><script>window.location.href = '
    body += '"/challenge/verify-human";</script></body></html>'
    assert verdict(200, {}, body) == ("CHALLENGED", "Generic")


def test_b4d_refresh_to_content():
    body = '<html><head><meta http-equiv="refresh" content="0; url=/home">' \
        "</head><body></body></html>"
    assert verdict(200, {}, body) == ("OPEN", None)


# B5 — cookie-consent walls vs real walls
def test_b5a_consent_on_served_page():
    big = "<html><body>" + "real article text " * 1200 + \
        '<div class="consent">We use cookies. Accept all</div></body></html>'
    assert verdict(200, {}, big) == ("OPEN", None)


def test_b5b_consent_only_page():
    body = ('<html><body><div class="consent">Please accept cookies to '
            'continue</div><button>Accept</button></body></html>')
    assert verdict(200, {}, body) == ("OPEN", None)


def test_b5c_consent_plus_human_check():
    body = ('<html><body><div class="consent">We use cookies</div>'
            "<p>Verify you are human to continue</p></body></html>")
    assert verdict(200, {}, body) == ("CHALLENGED", "Generic")


# B6 — Cloudflare error-page variants
def test_b6a_attention_required():
    assert verdict(403, {"cf-ray": "abc"},
                  "Attention Required! | Cloudflare") == ("WALLED", "Cloudflare")


def test_b6b_error_1000():
    assert verdict(403, {"cf-ray": "abc"},
                  "Error 1000: DNS points to a prohibited IP") == \
        ("WALLED", "Cloudflare")


def test_b6c_error_522():
    assert verdict(503, {"cf-ray": "abc"},
                  "Error 522: Connection timed out") == ("UNREACHABLE", None)


# B7 — PerimeterX app interstitials
def test_b7a_px_app_interstitial():
    assert verdict(403, {}, '<div class="px-captcha"></div>'
                  "Please open this page in the app") == \
        ("CHALLENGED", "PerimeterX")


def test_b7b_app_only_gate_no_markers():
    assert verdict(403, {}, "Download our app to continue") == ("WALLED", None)


# B8 — DataDome variants
def test_b8a_datadome_delivery_no_widget():
    assert verdict(403, {}, '<script src="https://captcha-delivery.com/'
                  'x.js"></script>') == ("CHALLENGED", "DataDome")


def test_b8b_datadome_header_only():
    assert verdict(403, {"x-datadome": "yes"}, "Forbidden") == \
        ("CHALLENGED", "DataDome")


def test_b8c_served_page_dd_cookie():
    big = "<html><body>" + "real article text " * 1200 + "</body></html>"
    assert verdict(200, {"set-cookie": "dd_cookie=abc"}, big) == ("OPEN", None)


# B10 — three-vendor contradiction
def test_b10a_cf_mitigated_beats_all():
    assert verdict(403, {"cf-mitigated": "challenge"},
                  "datadome <div class=px-captcha></div>") == \
        ("CHALLENGED", "Cloudflare")


# B9 — audit soft-404 variants
def _rec(status, body, headers=None, url="https://site.example/x"):
    return {"url": url, "final_url": url, "status": status,
            "headers": headers or {}, "body": body, "error": None,
            "redirect_chain": []}


def _audit_with(llms=None, robots=None):
    home = _rec(200, "<html><body>home</body></html>", url="https://site.example/")
    recs = {"homepage": home,
            "robots": robots if robots is not None else _rec(404, ""),
            "llms": llms if llms is not None else _rec(404, ""),
            "sitemap": None, "openapi": _rec(404, ""),
            "openapi_wellknown": _rec(404, ""), "api_root": _rec(404, ""),
            "api_docs": _rec(404, ""), "signed": _rec(404, "")}
    out = evaluate_audit("https://site.example", recs)
    return {c["check"]: c["status"] for c in out["checks"]}


def test_b9a_llms_json_error():
    llms = _rec(200, '{"error": "not found"}',
                {"content-type": "text/plain"})
    assert _audit_with(llms=llms)["llms_txt"] == "FAIL"


def test_b9b_llms_redirect_to_homepage_html():
    llms = _rec(200, "<html><body>home</body></html>",
                {"content-type": "text/html"})
    assert _audit_with(llms=llms)["llms_txt"] == "FAIL"


def test_b9c_empty_robots():
    robots = _rec(200, "", {"content-type": "text/plain"})
    assert _audit_with(robots=robots)["robots_txt"] == "PASS"


def test_b9d_robots_html_soft404():
    robots = _rec(200, "<html><body>Not found</body></html>",
                 {"content-type": "text/plain"})
    assert _audit_with(robots=robots)["robots_txt"] == "FAIL"


def test_b9e_sitemap_html_200():
    home = _rec(200, "<html><body>home</body></html>", url="https://site.example/")
    sitemap = _rec(200, "<html><body>error</body></html>")
    recs = {"homepage": home, "robots": _rec(404, ""), "llms": _rec(404, ""),
            "sitemap": sitemap, "openapi": _rec(404, ""),
            "openapi_wellknown": _rec(404, ""), "api_root": _rec(404, ""),
            "api_docs": _rec(404, ""), "signed": _rec(404, "")}
    out = evaluate_audit("https://site.example", recs)
    assert {c["check"]: c["status"] for c in out["checks"]}["sitemap"] == "WARN"
