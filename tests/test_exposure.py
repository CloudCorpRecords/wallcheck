"""Offline tests for the exposure scanner library.

Every fixture value is synthetic and obviously fake (FAKE... strings
that satisfy the regexes but cannot be real credentials). The scanner
is a pure function over text, so these fully exercise classification,
dedupe, placeholder filtering and the fingerprint-only output contract
with no network.
Run: python3 -m unittest discover -s tests -v
"""

import base64
import hashlib
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from wallcheck.exposure import fp, scan_text  # noqa: E402

SITE, SOURCE = "example.test", "test-fixture"

# Synthetic values: shaped like the real classes, plainly invented.
# They are built by concatenation on purpose: a literal shaped exactly
# like a real token trips GitHub push protection (it cannot tell a fake
# Twilio SID from a real one), which would block this test file itself.
GOOGLE_KEY = "AIza" + "FAKE" * 5 + "0123456"
STRIPE_SECRET = "sk_live_" + "FAKE" * 4 + "1234"
STRIPE_PUB = "pk_live_" + "FAKE" * 4 + "1234"
WEBHOOK_SECRET = "whsec_" + "FAKE" * 5 + "0123"
GITHUB_TOKEN = "ghp_" + "FAKE" * 8
SLACK_TOKEN = "xoxb-" + "FAKE-FAKE-" + "FAKE123456"
SENDGRID_KEY = "SG." + "FAKE" * 5 + "12." + "FAKE" * 5 + "123"
TWILIO_KEY = "SK" + "0123456789abcdef" * 2
WECHAT_ID = "wx" + "0123456789abcdef"
OAUTH_CLIENT = "123456789012-fakefakefakefake.apps.googleusercontent.com"
MAPBOX_TOKEN = "pk.eyJ" + "FAKE" * 5 + "0123456789"
ENV_SECRET_VALUE = "FAKEENCRYPTIONKEY0123456789ABCDEF"
DB_URL = "postgres://fakeuser:fakepass99@db.example.test:5432/app"
GENERIC_SECRET = "FAKESECRETVALUE0123456789"


def mint_jwt(payload):
    def b64(obj):
        raw = json.dumps(obj, separators=(",", ":")).encode()
        return base64.urlsafe_b64encode(raw).decode().rstrip("=")
    return "%s.%s.%s" % (b64({"alg": "none", "typ": "JWT"}), b64(payload),
                         "FAKESIGNATURE0123456789")


def by_pattern(findings):
    return {f["pattern"]: f for f in findings}


class TestCandidateClassification(unittest.TestCase):
    def scan(self, body):
        return by_pattern(scan_text(body, SITE, SOURCE))

    def test_public_env_sensitive_name_next(self):
        f = self.scan('NEXT_PUBLIC_APP_ENCRYPTION_KEY":"%s"'
                      % ENV_SECRET_VALUE)
        hit = f["public_env_sensitive_name"]
        self.assertEqual(hit["class"], "CANDIDATE_EXPOSURE")
        self.assertEqual(hit["var_name"], "NEXT_PUBLIC_APP_ENCRYPTION_KEY")

    def test_public_env_sensitive_name_vite(self):
        f = self.scan("VITE_APP_SECRET=%s" % ENV_SECRET_VALUE)
        self.assertEqual(f["public_env_sensitive_name"]["class"],
                         "CANDIDATE_EXPOSURE")

    def test_stripe_secret_key(self):
        f = self.scan("key: %s" % STRIPE_SECRET)
        self.assertEqual(f["stripe_secret_key"]["class"],
                         "CANDIDATE_EXPOSURE")

    def test_stripe_webhook_secret(self):
        f = self.scan(WEBHOOK_SECRET)
        self.assertEqual(f["stripe_webhook_secret"]["class"],
                         "CANDIDATE_EXPOSURE")

    def test_github_token(self):
        f = self.scan(GITHUB_TOKEN)
        self.assertEqual(f["github_token"]["class"], "CANDIDATE_EXPOSURE")

    def test_slack_token(self):
        f = self.scan(SLACK_TOKEN)
        self.assertEqual(f["slack_token"]["class"], "CANDIDATE_EXPOSURE")

    def test_sendgrid_key(self):
        f = self.scan(SENDGRID_KEY)
        self.assertEqual(f["sendgrid_key"]["class"], "CANDIDATE_EXPOSURE")

    def test_twilio_api_key(self):
        f = self.scan(TWILIO_KEY)
        self.assertEqual(f["twilio_api_key"]["class"],
                         "CANDIDATE_EXPOSURE")

    def test_private_key_block_header(self):
        f = self.scan("-----BEGIN PRIVATE KEY-----\nFAKEBODY\n"
                      "-----END PRIVATE KEY-----")
        hit = f["private_key_block"]
        self.assertEqual(hit["class"], "CANDIDATE_EXPOSURE")
        # The captured group is the header line only, by construction.
        self.assertEqual(hit["value_len"],
                         len("-----BEGIN PRIVATE KEY-----"))

    def test_db_url_with_password(self):
        f = self.scan("DATABASE_URL=%s" % DB_URL)
        self.assertEqual(f["db_url_with_password"]["class"],
                         "CANDIDATE_EXPOSURE")

    def test_generic_secret_field(self):
        f = self.scan('{"api_secret": "%s"}' % GENERIC_SECRET)
        self.assertEqual(f["generic_secret_field"]["class"],
                         "CANDIDATE_EXPOSURE")


class TestPublicClassification(unittest.TestCase):
    def scan(self, body):
        return by_pattern(scan_text(body, SITE, SOURCE))

    def test_google_api_key_is_public(self):
        f = self.scan(GOOGLE_KEY)
        self.assertEqual(f["google_api_key"]["class"], "PUBLIC_BY_DESIGN")

    def test_stripe_publishable_is_public(self):
        f = self.scan(STRIPE_PUB)
        self.assertEqual(f["stripe_publishable_key"]["class"],
                         "PUBLIC_BY_DESIGN")

    def test_wechat_app_id_is_public(self):
        f = self.scan(WECHAT_ID)
        self.assertEqual(f["wechat_app_id"]["class"], "PUBLIC_BY_DESIGN")

    def test_google_oauth_client_id_is_public(self):
        f = self.scan(OAUTH_CLIENT)
        self.assertEqual(f["google_oauth_client_id"]["class"],
                         "PUBLIC_BY_DESIGN")

    def test_mapbox_public_token_is_public(self):
        f = self.scan(MAPBOX_TOKEN)
        self.assertEqual(f["mapbox_public_token"]["class"],
                         "PUBLIC_BY_DESIGN")


class TestDedupe(unittest.TestCase):
    def test_candidate_beats_public_for_same_value(self):
        findings = scan_text('NEXT_PUBLIC_APP_ENCRYPTION_KEY":"%s"'
                             % ENV_SECRET_VALUE, SITE, SOURCE)
        rows = [f for f in findings if f["sha256_16"] == fp(ENV_SECRET_VALUE)]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["class"], "CANDIDATE_EXPOSURE")

    def test_same_value_twice_yields_one_finding(self):
        findings = scan_text("%s and again %s" % (STRIPE_SECRET,
                                                  STRIPE_SECRET),
                             SITE, SOURCE)
        rows = [f for f in findings if f["pattern"] == "stripe_secret_key"]
        self.assertEqual(len(rows), 1)


class TestPlaceholderFiltering(unittest.TestCase):
    def test_redacted_marker_produces_no_finding(self):
        body = 'NEXT_PUBLIC_API_KEY":"REDACTED-PUBLIC-ENV-API-KEY"'
        self.assertEqual(scan_text(body, SITE, SOURCE), [])

    def test_your_value_produces_no_finding(self):
        body = '{"api_secret": "your-secret-value-0000"}'
        self.assertEqual(scan_text(body, SITE, SOURCE), [])

    def test_example_value_produces_no_finding(self):
        body = '{"client_secret": "example-secret-0123456789"}'
        self.assertEqual(scan_text(body, SITE, SOURCE), [])

    def test_xxxx_value_produces_no_finding(self):
        body = 'NEXT_PUBLIC_SOME_KEY":"xxxxxxxxxxxxxxxx"'
        self.assertEqual(scan_text(body, SITE, SOURCE), [])

    def test_dummy_value_produces_no_finding(self):
        body = '{"app_secret": "dummyvalue0123456789"}'
        self.assertEqual(scan_text(body, SITE, SOURCE), [])


class TestJwtLifetime(unittest.TestCase):
    def test_short_lived_jwt_is_visitor_token(self):
        token = mint_jwt({"iat": 1000, "exp": 1300})
        findings = scan_text(token, SITE, SOURCE)
        hit = by_pattern(findings)["jwt_in_page"]
        self.assertEqual(hit["class"], "VISITOR_TOKEN")
        self.assertEqual(hit["jwt_lifetime_s"], 300)

    def test_long_lived_jwt_is_candidate(self):
        token = mint_jwt({"iat": 1000, "exp": 1000 + 200000})
        findings = scan_text(token, SITE, SOURCE)
        hit = by_pattern(findings)["jwt_in_page"]
        self.assertEqual(hit["class"], "CANDIDATE_EXPOSURE")
        self.assertEqual(hit["jwt_lifetime_s"], 200000)
        self.assertEqual(hit["note"], "long-lived JWT served in page")

    def test_jwt_without_iat_is_visitor_token_with_null_lifetime(self):
        token = mint_jwt({"exp": 9999999999})
        findings = scan_text(token, SITE, SOURCE)
        hit = by_pattern(findings)["jwt_in_page"]
        self.assertEqual(hit["class"], "VISITOR_TOKEN")
        self.assertIsNone(hit["jwt_lifetime_s"])


class TestFingerprintOnlyOutput(unittest.TestCase):
    ALLOWED_KEYS = {"site", "source", "class", "pattern", "value_len",
                    "sha256_16", "var_name", "jwt_lifetime_s", "note"}

    def test_findings_never_contain_raw_values(self):
        values = [GOOGLE_KEY, STRIPE_SECRET, WEBHOOK_SECRET, GITHUB_TOKEN,
                  GENERIC_SECRET, ENV_SECRET_VALUE]
        body = " ".join(values) + ' {"api_secret": "%s"}' % GENERIC_SECRET \
            + ' NEXT_PUBLIC_APP_ENCRYPTION_KEY":"%s"' % ENV_SECRET_VALUE
        findings = scan_text(body, SITE, SOURCE)
        blob = json.dumps(findings)
        for v in values:
            self.assertNotIn(v, blob)

    def test_finding_shape_and_fingerprint_math(self):
        findings = scan_text(STRIPE_SECRET, SITE, SOURCE)
        self.assertEqual(len(findings), 1)
        hit = findings[0]
        self.assertTrue(set(hit) <= self.ALLOWED_KEYS)
        self.assertEqual(hit["site"], SITE)
        self.assertEqual(hit["source"], SOURCE)
        self.assertEqual(hit["value_len"], len(STRIPE_SECRET))
        self.assertEqual(
            hit["sha256_16"],
            hashlib.sha256(STRIPE_SECRET.encode()).hexdigest()[:16])
        self.assertEqual(hit["sha256_16"], fp(STRIPE_SECRET))


if __name__ == "__main__":
    unittest.main()
