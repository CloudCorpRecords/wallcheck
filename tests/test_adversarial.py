"""Wave 6 adversarial battery: obfuscated/edge wall shapes.

Every fixture was classified BY HAND first (see
validation/wave6/HANDCLASS.md); the hand verdict is pinned here and the
classifier must match it. Mismatches are classifier defects, fixed by
generalized rules only.

Run: python3 -m unittest discover -s tests -v
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from wallcheck.classify import classify  # noqa: E402


def _big(content, target_bytes=30000):
    """Pad a small page up past the 16 KB served-page gate with real text."""
    filler = ("<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
              "Sed do eiusmod tempor incididunt ut labore et dolore magna "
              "aliqua. Ut enim ad minim veniam, quis nostrud exercitation "
              "ullamco laboris nisi ut aliquip ex ea commodo consequat.</p>")
    body = content
    while len(body) < target_bytes:
        body += filler
    return body


# ---------------- S1: soft-404 variants ----------------

S1A = ("<!DOCTYPE html><html><head><title>Page Not Found</title></head>"
       "<body><h1>404 - Page not found</h1>"
       "<p>The page you requested could not be found.</p></body></html>")

S1B = ("<!DOCTYPE html><html><head><title>Not found</title></head>"
       "<body><h1>404</h1><p>Verify you are human to continue.</p></body></html>")

S1C = "<!DOCTYPE html><html><head><title>Gone</title></head><body><h1>Gone</h1></body></html>"


# ---------------- S2: redirect-chain walls ----------------

S2A_BODY = ("<!DOCTYPE html><html><head><title>Just a moment...</title></head>"
            "<body><p>Just a moment...</p>"
            "<script src=\"https://challenges.cloudflare.com/turnstile/v0/api.js\">"
            "</script></body></html>")

S2B_HOMEPAGE = _big("<!DOCTYPE html><html><head><title>Passed Example</title></head>"
                    "<body><h1>Welcome to Passed Example</h1>"
                    "<p>Real homepage content lives here.</p>")

S2C_BODY = ("<html><head><meta http-equiv=\"refresh\" content=\"0;url=/px/captcha/\">"
            "</head><body></body></html>")


# ---------------- S3: JS-proof pages without vendor tokens ----------------

S3A_BODY = ("<!DOCTYPE html><html><head><title>Verifying your browser</title></head>"
            "<body><h1>Verifying your browser...</h1>"
            "<p>This process is automatic. Your browser will redirect to the "
            "requested content shortly.</p>"
            "<script>setTimeout(function(){location.reload();},3000);</script>"
            "</body></html>")

S3B_BODY = _big("<!DOCTYPE html><html><head><title>Inside the bot-wall economy</title></head>"
                "<body><h1>Inside the bot-wall economy</h1>"
                "<p>One vendor's interstitial reads, in full: \"verifying your "
                "browser\" — a phrase every agent builder learns to dread.</p>")

S3C_BODY = ("<!DOCTYPE html><html><head><title>App</title></head>"
            "<body><noscript>You need to enable JavaScript to run this app.</noscript>"
            "<div id=\"root\"></div><script src=\"/static/bundle.js\"></script></body></html>")


# ---------------- S4: multi-vendor stacks ----------------

S4A_BODY = ("<!DOCTYPE html><html><head><title>Access Denied</title></head>"
            "<body><div id=\"px-captcha\"></div>"
            "<script src=\"https://client.perimeterx.net/abc/main.min.js\"></script>"
            "</body></html>")

S4C_BODY = ("<!DOCTYPE html><html><head><title>Device Check</title></head>"
            "<body><p>datadome device check</p>"
            "<script src=\"https://captcha-delivery.com/captcha.js\"></script></body></html>")

S4D_BODY = ("<html><head></head><body><script>window.KPSDK={};</script>"
            "<script src=\"https://cdn.kasada.com/sensor.js\"></script></body></html>")


# ---------------- S5: login walls behind challenges ----------------

S5A_BODY = S2A_BODY

S5B_BODY = ("<!DOCTYPE html><html><head><title>Sign in</title></head>"
            "<body><h1>Sign in to App</h1>"
            "<form><input type=\"email\"><input type=\"password\">"
            "<button>Sign in</button></form></body></html>")

S5C_BODY = ("<!DOCTYPE html><html><head><title>Sign in</title></head>"
            "<body><h1>Sign in</h1>"
            "<p>To protect your account, verify you are human.</p>"
            "<form><input type=\"email\"><input type=\"password\">"
            "<button>Sign in</button></form></body></html>")

S5D_BODY = ("<!DOCTYPE html><html><head><title>Request unsuccessful</title></head>"
            "<body><h1>Request unsuccessful</h1>"
            "<p>Incapsula incident ID: 12345</p></body></html>")


# ---------------- S6: localized challenge pages ----------------

S6A_BODY = ("<!DOCTYPE html><html lang=\"es\"><head><title>Verificación</title></head>"
            "<body><h1>Verifica que eres un humano para continuar.</h1>"
            "<p>Marca la casilla «No soy un robot».</p></body></html>")

S6B_BODY = ("<!DOCTYPE html><html lang=\"de\"><head><title>Überprüfung</title></head>"
            "<body><h1>Bitte bestätigen Sie, dass Sie ein Mensch sind.</h1>"
            "<p>Klicken Sie auf „Ich bin kein Roboter“.</p></body></html>")

S6C_BODY = ("<!DOCTYPE html><html lang=\"fr\"><head><title>Vérification</title></head>"
            "<body><h1>Veuillez vérifier que vous êtes un humain.</h1>"
            "<p>Cochez la case « Je ne suis pas un robot ».</p></body></html>")

S6D_BODY = ("<!DOCTYPE html><html lang=\"ja\"><head><title>確認</title></head>"
            "<body><h1>あなたがロボットでないことを確認してください。</h1>"
            "<p>「私はロボットではありません」にチェックを入れてください。</p></body></html>")

S6E_BODY = ("<!DOCTYPE html><html><head><title>Verification</title></head>"
            "<body><h1>Verify you are human.</h1>"
            "<p>Check the box: I am not a robot.</p></body></html>")

S6F_BODY = ("<!DOCTYPE html><html lang=\"pt\"><head><title>Verificação</title></head>"
            "<body><h1>Verifique se você é humano.</h1>"
            "<p>Marque a caixa «Não sou um robô».</p></body></html>")


class TestAdversarialBattery(unittest.TestCase):
    # S1 — soft-404 variants: all OPEN, the status is the answer.
    def test_s1a_soft404_200(self):
        r = classify(200, {}, S1A, final_url="https://example-shop.com/no-such-page")
        self.assertEqual(r["verdict"], "OPEN")
        self.assertIsNone(r["vendor"])

    def test_s1b_404_with_challenge_prose(self):
        r = classify(404, {}, S1B)
        self.assertEqual(r["verdict"], "OPEN")
        self.assertIsNone(r["vendor"])

    def test_s1c_410_gone(self):
        r = classify(410, {}, S1C)
        self.assertEqual(r["verdict"], "OPEN")
        self.assertIsNone(r["vendor"])

    def test_s1d_empty_200(self):
        r = classify(200, {}, "")
        self.assertEqual(r["verdict"], "OPEN")
        self.assertIsNone(r["vendor"])

    # S2 — redirect-chain walls.
    def test_s2a_challenge_at_chain_end(self):
        r = classify(403, {"CF-Ray": "x-IAD"}, S2A_BODY,
                     final_url="https://walls.example/",
                     redirect_chain=["https://walls.example/",
                                     "https://walls.example/cdn-cgi/challenge"])
        self.assertEqual(r["verdict"], "CHALLENGED")
        self.assertEqual(r["vendor"], "Cloudflare")

    def test_s2b_challenge_in_chain_but_real_page_served(self):
        r = classify(200, {"CF-Ray": "x-IAD"}, S2B_HOMEPAGE,
                     final_url="https://passed.example/",
                     redirect_chain=["https://passed.example/",
                                     "https://passed.example/cdn-cgi/challenge-platform/h/b/abc"])
        self.assertEqual(r["verdict"], "OPEN")
        self.assertIsNone(r["vendor"])

    def test_s2c_meta_refresh_to_captcha(self):
        # The page's whole content routes the client to a captcha:
        # a CAPTCHA page by reference. The probe does not follow the
        # refresh, but the unblanked reference is the challenge signal
        # (Amazon's /errors_page/validateCaptcha interstitial is the
        # real-world specimen that pins this).
        r = classify(200, {}, S2C_BODY)
        self.assertEqual(r["verdict"], "CHALLENGED")
        self.assertEqual(r["vendor"], "Generic")

    # S3 — JS-proof pages with no vendor tokens.
    def test_s3a_202_js_proof_stub(self):
        r = classify(202, {}, S3A_BODY)
        self.assertEqual(r["verdict"], "CHALLENGED")
        self.assertEqual(r["vendor"], "Generic")
        self.assertIn("JS_PROOF", r["evidence"])

    def test_s3b_full_page_about_walls(self):
        r = classify(200, {}, S3B_BODY)
        self.assertEqual(r["verdict"], "OPEN")
        self.assertIsNone(r["vendor"])

    def test_s3c_spa_shell(self):
        r = classify(200, {}, S3C_BODY)
        self.assertEqual(r["verdict"], "OPEN")
        self.assertIsNone(r["vendor"])

    # S4 — multi-vendor stacks.
    def test_s4a_cf_front_px_wall(self):
        r = classify(403, {"Server": "cloudflare", "CF-Ray": "x-IAD"}, S4A_BODY)
        self.assertEqual(r["verdict"], "CHALLENGED")
        self.assertEqual(r["vendor"], "PerimeterX")

    def test_s4b_cf_wall_and_px(self):
        r = classify(403, {"cf-mitigated": "challenge"}, S4A_BODY)
        self.assertEqual(r["verdict"], "CHALLENGED")
        self.assertEqual(r["vendor"], "Cloudflare")

    def test_s4c_datadome_over_akamai_cookie(self):
        r = classify(403, {"x-datadome": "protected", "Set-Cookie": "ak_bmsc=x"},
                     S4C_BODY)
        self.assertEqual(r["verdict"], "CHALLENGED")
        self.assertEqual(r["vendor"], "DataDome")

    def test_s4d_kasada_over_akamai_cookie(self):
        r = classify(429, {"Set-Cookie": "ak_bmsc=x"}, S4D_BODY)
        self.assertEqual(r["verdict"], "RATE_LIMITED")
        self.assertEqual(r["vendor"], "Kasada")

    def test_s4e_datadome_wall_behind_cloudflare_cdn(self):
        # Wave 6 expansion specimen (economist.com): DataDome's
        # captcha-delivery payload served behind Cloudflare's CDN.
        # The wall that fired outranks the CDN that fronted — the
        # PerimeterX-over-CDN principle, generalized to every vendor.
        body = ("<html><head></head><body><script>var dd={"
                "'host':'geo.captcha-delivery.com'};</script>"
                "<script src=\"https://ct.captcha-delivery.com/c.js\">"
                "</script></body></html>")
        r = classify(403, {"Server": "cloudflare", "CF-Ray": "x-IAD",
                           "x-datadome": "protected"}, body)
        self.assertEqual(r["verdict"], "CHALLENGED")
        self.assertEqual(r["vendor"], "DataDome")

    # S5 — login walls behind challenges.
    def test_s5a_vendor_wall_at_login_url(self):
        r = classify(403, {"CF-Ray": "x-IAD"}, S5A_BODY,
                     final_url="https://members.example/login")
        self.assertEqual(r["verdict"], "CHALLENGED")
        self.assertEqual(r["vendor"], "Cloudflare")

    def test_s5b_plain_login_page(self):
        r = classify(200, {"CF-Ray": "x-IAD"}, S5B_BODY,
                     final_url="https://app.example/login",
                     redirect_chain=["https://app.example/",
                                     "https://app.example/login"])
        self.assertEqual(r["verdict"], "LOGIN_GATED")

    def test_s5c_login_page_with_human_check_prose(self):
        r = classify(200, {}, S5C_BODY, final_url="https://accounts.example/login")
        self.assertEqual(r["verdict"], "LOGIN_GATED")

    def test_s5d_vendor_block_at_login_url(self):
        r = classify(200, {}, S5D_BODY, final_url="https://site.example/login")
        self.assertEqual(r["verdict"], "WALLED")
        self.assertEqual(r["vendor"], "Imperva")

    # S6 — localized challenge pages: all CHALLENGED / Generic.
    def test_s6a_spanish(self):
        r = classify(403, {}, S6A_BODY)
        self.assertEqual(r["verdict"], "CHALLENGED")
        self.assertEqual(r["vendor"], "Generic")

    def test_s6b_german(self):
        r = classify(403, {}, S6B_BODY)
        self.assertEqual(r["verdict"], "CHALLENGED")
        self.assertEqual(r["vendor"], "Generic")

    def test_s6c_french(self):
        r = classify(403, {}, S6C_BODY)
        self.assertEqual(r["verdict"], "CHALLENGED")
        self.assertEqual(r["vendor"], "Generic")

    def test_s6d_japanese(self):
        r = classify(403, {}, S6D_BODY)
        self.assertEqual(r["verdict"], "CHALLENGED")
        self.assertEqual(r["vendor"], "Generic")

    def test_s6e_english_control(self):
        r = classify(403, {}, S6E_BODY)
        self.assertEqual(r["verdict"], "CHALLENGED")
        self.assertEqual(r["vendor"], "Generic")

    def test_s6f_portuguese(self):
        r = classify(403, {}, S6F_BODY)
        self.assertEqual(r["verdict"], "CHALLENGED")
        self.assertEqual(r["vendor"], "Generic")


if __name__ == "__main__":
    unittest.main()
