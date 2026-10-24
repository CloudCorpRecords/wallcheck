"""Wave 14 battery v6 regression pins (see validation/wave14/
HANDCLASS-6.md for the hand classifications). Shapes: script-JSON
markers, alt-attribute text, traffic-anomaly phrasing, Retry-After
throttles, login + session-challenge cookies, robots-declared
sitemap indexes, relative-link-only llms, redirect-hop walls.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from wallcheck.classify import classify  # noqa: E402
from wallcheck.audit import audit_site, evaluate_audit  # noqa: E402

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
    return [c for c in out["checks"] if c["check"] == name][0]["status"]


def llms_records(body):
    return {
        "robots": rec(200, {"Content-Type": "text/plain"},
                      "User-agent: *\nAllow: /\n"),
        "llms": rec(200, {"Content-Type": "text/plain"}, body),
        "sitemap": rec(404, {}, "not found"),
        "homepage": rec(200, {"Content-Type": "text/html"},
                        "<html><head><title>x</title></head><body>x</body></html>"),
        "signed": rec(404, {}, "not found"),
    }


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
    return [c for c in out["checks"] if c["check"] == "sitemap"][0]["status"]


PARA = ("<html><body><p>Our team ships every Friday and writes "
        "about the process in detail for our readers.</p></body></html>")
LOGIN_FORM = ('<html><body><form action="/session" method="post">'
              '<input type="password" name="pw">'
              '<button>Sign in</button></form></body></html>')
URLSET = ('<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
          '<url><loc>https://x.example/</loc></url></urlset>')
SITEMAPINDEX = ('<?xml version="1.0"?><sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                '<sitemap><loc>https://x.example/sitemap1.xml</loc></sitemap></sitemapindex>')


class TestScriptJsonBlobs:
    def test_f1a_challenge_only_blob(self):
        assert verdict(200, {}, '<html><body><script type="application/json">{"wall":{"type":"captcha","action":"verify"}}</script></body></html>') == ("CHALLENGED", "Generic")

    def test_f1b_form_config_blob_with_visible_text(self):
        # W14-001: script-only markers are configuration, not content.
        body = PARA.replace("</body>", '<script type="application/json">{"form":{"captcha":true,"sitekey":"abc"}}</script></body>')
        assert verdict(200, {}, body) == ("OPEN", None)

    def test_f1d_config_blob_without_visible_text(self):
        body = '<html><body><div class="spinner"></div><script type="application/json">{"form":{"captcha":true}}</script></body></html>'
        assert verdict(200, {}, body) == ("CHALLENGED", "Generic")

    def test_guard_loading_text_under_threshold_still_fires(self):
        # Visible text under _VISIBLE_TEXT_MIN is not content.
        body = '<html><body><p>Loading...</p><script>{"form":{"captcha":true}}</script></body></html>'
        assert verdict(200, {}, body) == ("CHALLENGED", "Generic")

    def test_guard_script_only_js_proof_suppressed_with_text(self):
        # The suppression generalizes to JS_PROOF phrases in scripts.
        body = PARA.replace("</body>", '<script>{"status":"verifying your browser"}</script></body>')
        assert verdict(200, {}, body) == ("OPEN", None)


class TestAltAttributes:
    def test_f2a_alt_human_check(self):
        assert verdict(403, {}, '<html><body><img src="/img/x.png" alt="Please verify you are human"></body></html>') == ("CHALLENGED", "Generic")

    def test_f2b_alt_refusal(self):
        assert verdict(403, {}, '<html><body><img src="/img/x.png" alt="Access denied"></body></html>') == ("WALLED", None)


class TestTrafficAnomaly:
    def test_f3a_phrase_alone_is_refusal(self):
        assert verdict(403, {}, '<html><body><p>Access denied: unusual traffic detected from your network.</p></body></html>') == ("WALLED", None)

    def test_f3b_phrase_plus_verification_is_challenge(self):
        # W14-002: TRAFFIC_CHECK.
        assert verdict(200, {}, '<html><body><p>Unusual traffic detected. Complete verification to continue.</p></body></html>') == ("CHALLENGED", "Generic")

    def test_guard_traffic_plus_captcha_cue(self):
        assert verdict(200, {}, '<html><body><p>Suspicious activity detected. Complete the captcha check.</p></body></html>') == ("CHALLENGED", "Generic")

    def test_f3d_suspension_without_cue_is_refusal(self):
        assert verdict(403, {}, '<html><body><p>Suspicious activity detected. Your account has been suspended.</p></body></html>') == ("WALLED", None)


class TestRetryAfterThrottles:
    def test_f4a_classic_429(self):
        assert verdict(429, {"retry-after": "60"}, '<html><body><p>Too many requests. Try again later.</p></body></html>') == ("RATE_LIMITED", None)

    def test_f4b_challenge_dominates_throttle(self):
        assert verdict(429, {"retry-after": "60"}, '<html><body><p>Too many requests. Please verify you are human to continue.</p></body></html>') == ("CHALLENGED", "Generic")

    def test_f4c_403_timed_throttle(self):
        # W14-003: Retry-After + throttle wording = throttle.
        assert verdict(403, {"retry-after": "120"}, '<html><body><p>Too many requests from your IP. Please retry after 120 seconds.</p></body></html>') == ("RATE_LIMITED", None)

    def test_f4d_503_timed_throttle(self):
        assert verdict(503, {"retry-after": "60"}, '<html><body><p>Too many requests, please retry in 60 seconds.</p></body></html>') == ("RATE_LIMITED", None)

    def test_f4e_overload_wording_stays_unreachable(self):
        assert verdict(503, {"retry-after": "60"}, '<html><body><p>Service temporarily unavailable.</p></body></html>') == ("UNREACHABLE", None)

    def test_f4f_header_alone_does_not_convert_refusal(self):
        assert verdict(403, {"retry-after": "120"}, '<html><body><p>Access denied.</p></body></html>') == ("WALLED", None)

    def test_guard_wall_signal_beats_throttle_rule(self):
        # A fired wall with a Retry-After header is still a wall.
        assert verdict(403, {"retry-after": "60", "cf-ray": "abc", "cf-mitigated": "challenge"},
                       '<html><body><h1>Just a moment</h1><p>Too many requests.</p></body></html>') == ("CHALLENGED", "Cloudflare")


class TestLoginChallengeCookies:
    def test_f5a_challenge_named_cookie(self):
        assert verdict(200, {"set-cookie": "challenge_token=abc; Path=/"}, LOGIN_FORM, url=LOGIN) == ("LOGIN_GATED", None)

    def test_f5b_px_sensor_cookie(self):
        assert verdict(200, {"set-cookie": "_pxvid=abc123; Path=/"}, LOGIN_FORM, url=LOGIN) == ("LOGIN_GATED", None)

    def test_f5c_datadome_cookie_keeps_vendor(self):
        assert verdict(200, {"set-cookie": "dd_cookie=abc; Path=/"}, LOGIN_FORM, url=LOGIN) == ("LOGIN_GATED", "DataDome")

    def test_f5d_imperva_cookie_keeps_vendor(self):
        assert verdict(200, {"set-cookie": "incap_ses=abc; Path=/"}, LOGIN_FORM, url=LOGIN) == ("LOGIN_GATED", "Imperva")


class TestDeclaredSitemaps:
    def test_f6a_html_sitemap_xml_hides_declared_index(self):
        # W14-004: fall through to declared sitemaps when the default
        # is not a usable sitemap document.
        assert sitemap_via_site(
            "User-agent: *\nAllow: /\nSitemap: https://x.example/sitemap-index.xml\n",
            rec(200, {"Content-Type": "text/html"}, "<html><body>Not found</body></html>"),
            {"https://x.example/sitemap-index.xml":
             rec(200, {"Content-Type": "application/xml"}, SITEMAPINDEX)}) == "PASS"

    def test_f6b_dead_first_declaration_falls_through(self):
        assert sitemap_via_site(
            "User-agent: *\nAllow: /\nSitemap: https://x.example/s1.xml\nSitemap: https://x.example/s2.xml\n",
            rec(404, {}, "not found"),
            {"https://x.example/s1.xml": rec(404, {}, "not found"),
             "https://x.example/s2.xml": rec(200, {"Content-Type": "application/xml"}, URLSET)}) == "PASS"

    def test_f6c_no_sitemap_anywhere(self):
        assert sitemap_via_site(
            "User-agent: *\nAllow: /\nSitemap: https://x.example/s1.xml\n",
            rec(404, {}, "not found"),
            {"https://x.example/s1.xml": rec(404, {}, "not found")}) == "WARN"

    def test_guard_declared_html_not_accepted(self):
        # A declared URL serving HTML is not a usable sitemap doc.
        assert sitemap_via_site(
            "User-agent: *\nAllow: /\nSitemap: https://x.example/s1.xml\n",
            rec(404, {}, "not found"),
            {"https://x.example/s1.xml": rec(200, {"Content-Type": "text/html"}, "<html><body>x</body></html>")}) == "WARN"


class TestLlmsRelativeLinks:
    def test_f7a_relative_links_only(self):
        assert audit_check(llms_records("- [A](/a)\n- [B](/b)\n- [C](/c)\n"), "llms_txt") == "PASS"

    def test_f7b_mixed_relative_and_absolute(self):
        assert audit_check(llms_records("- [A](/a)\n- [B](https://x.example/b)\n"), "llms_txt") == "PASS"

    def test_f7c_fragment_only_links_are_stub(self):
        # W14-005: fragment targets point at the file itself.
        assert audit_check(llms_records("- [Intro](#intro)\n- [Setup](#setup)\n"), "llms_txt") == "WARN"

    def test_f7d_bare_domain_is_stub(self):
        assert audit_check(llms_records("See example.com for details.\n"), "llms_txt") == "WARN"

    def test_guard_empty_link_target_does_not_count(self):
        assert audit_check(llms_records("- [A]()\n- [B]()\n"), "llms_txt") == "WARN"


class TestRedirectHopWalls:
    def test_f8a_challenge_hop_to_clean_final(self):
        assert verdict(200, {}, PARA, url="https://site.example/home",
                       chain=["https://site.example/", "https://site.example/challenge", "https://site.example/home"]) == ("OPEN", None)

    def test_f8b_captcha_hop_to_clean_final(self):
        assert verdict(200, {}, PARA, url="https://site.example/home",
                       chain=["https://site.example/", "https://site.example/verify-captcha", "https://site.example/home"]) == ("OPEN", None)

    def test_f8c_login_hop_to_login_final(self):
        assert verdict(200, {}, LOGIN_FORM, url=LOGIN,
                       chain=["https://site.example/", LOGIN]) == ("LOGIN_GATED", None)
