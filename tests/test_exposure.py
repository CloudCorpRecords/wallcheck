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
OPENAI_KEY = "sk-proj-" + "FAKE" * 6 + "0123456789"
OPENAI_LEGACY_KEY = "sk-" + "FAKE" * 12
ANTHROPIC_KEY = "sk-ant-" + "FAKE" * 6 + "0123456789"
GITLAB_PAT = "glpat-" + "FAKE" * 5
NPM_TOKEN = "npm_" + "FAKE" * 9
PYPI_TOKEN = "pypi-" + "FAKE" * 13 + "12"
DIGITALOCEAN_TOKEN = "dop_v1_" + "0123456789abcdef" * 4
AWS_ACCESS_KEY_ID = "AKIA" + "FAKE" * 4
SLACK_WEBHOOK = ("https://hooks.slack.com/services/"
                 + "T" + "FAKEFAKE1" + "/" + "B" + "FAKEFAKE1" + "/"
                 + "FAKE" * 6)
DISCORD_WEBHOOK = ("https://discord.com/api/webhooks/"
                   + "1" * 18 + "/" + "FAKE" * 16)
TELEGRAM_TOKEN = "123456789:" + "FAKE" * 8 + "FAK"
SENTRY_DSN = ("https://" + "0123456789abcdef" * 2
              + "@o123.ingest.us.sentry.io/4567890")
ENV_SECRET_VALUE = "FAKEENCRYPTIONKEY0123456789ABCDEF"
DB_URL = "postgres://fakeuser:fakepass99@db.example.test:5432/app"
GENERIC_SECRET = "FAKESECRETVALUE0123456789"
# A PEM-shaped base64 body: plain base64 alphabet, 64 chars, no key.
PEM_BODY = "FAKEBODY" * 8


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

    def test_private_key_block_with_pem_body(self):
        f = self.scan("-----BEGIN PRIVATE KEY-----\n" + PEM_BODY + "\n"
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

    def test_openai_api_key(self):
        f = self.scan(OPENAI_KEY)
        self.assertEqual(f["openai_api_key"]["class"],
                         "CANDIDATE_EXPOSURE")

    def test_openai_legacy_api_key(self):
        f = self.scan(OPENAI_LEGACY_KEY)
        self.assertEqual(f["openai_api_key"]["class"],
                         "CANDIDATE_EXPOSURE")

    def test_short_sk_string_is_not_an_openai_key(self):
        # Bare "sk-" + a short tail is prose-shaped, not a key: the
        # legacy branch demands the full 48-char body.
        self.assertNotIn("openai_api_key", self.scan("sk-" + "FAKE" * 4))

    def test_anthropic_api_key(self):
        f = self.scan(ANTHROPIC_KEY)
        self.assertEqual(f["anthropic_api_key"]["class"],
                         "CANDIDATE_EXPOSURE")

    def test_gitlab_pat(self):
        f = self.scan(GITLAB_PAT)
        self.assertEqual(f["gitlab_pat"]["class"], "CANDIDATE_EXPOSURE")

    def test_npm_token(self):
        f = self.scan(NPM_TOKEN)
        self.assertEqual(f["npm_token"]["class"], "CANDIDATE_EXPOSURE")

    def test_pypi_token(self):
        f = self.scan(PYPI_TOKEN)
        self.assertEqual(f["pypi_token"]["class"], "CANDIDATE_EXPOSURE")

    def test_digitalocean_token(self):
        f = self.scan(DIGITALOCEAN_TOKEN)
        self.assertEqual(f["digitalocean_token"]["class"],
                         "CANDIDATE_EXPOSURE")

    def test_aws_access_key_id(self):
        f = self.scan(AWS_ACCESS_KEY_ID)
        self.assertEqual(f["aws_access_key_id"]["class"],
                         "CANDIDATE_EXPOSURE")

    def test_slack_webhook_url(self):
        f = self.scan(SLACK_WEBHOOK)
        self.assertEqual(f["slack_webhook_url"]["class"],
                         "CANDIDATE_EXPOSURE")

    def test_discord_webhook_url(self):
        f = self.scan(DISCORD_WEBHOOK)
        self.assertEqual(f["discord_webhook_url"]["class"],
                         "CANDIDATE_EXPOSURE")

    def test_telegram_bot_token(self):
        f = self.scan(TELEGRAM_TOKEN)
        self.assertEqual(f["telegram_bot_token"]["class"],
                         "CANDIDATE_EXPOSURE")

    def test_db_url_extended_schemes(self):
        for scheme in ("mariadb", "mssql", "sqlserver", "cassandra",
                       "amqps", "rediss"):
            body = "%s://fakeuser:fakepass99@db.example.test/app" % scheme
            f = self.scan(body)
            self.assertEqual(f["db_url_with_password"]["class"],
                             "CANDIDATE_EXPOSURE", scheme)


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

    def test_sentry_dsn_is_public(self):
        # DSNs ship in client code by design; the embedded key only
        # submits events to one project.
        f = self.scan(SENTRY_DSN)
        self.assertEqual(f["sentry_dsn"]["class"], "PUBLIC_BY_DESIGN")


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


class TestPrivateKeyBodyEvidence(unittest.TestCase):
    """L2: a bare BEGIN header is a string constant, not a key."""

    def scan(self, body):
        return by_pattern(scan_text(body, SITE, SOURCE))

    def test_bare_begin_header_in_js_is_benign(self):
        body = 'var PEM_HEADER = "-----BEGIN PRIVATE KEY-----";'
        self.assertNotIn("private_key_block", self.scan(body))

    def test_bare_rsa_begin_header_is_benign(self):
        body = "-----BEGIN RSA PRIVATE KEY-----"
        self.assertNotIn("private_key_block", self.scan(body))

    def test_begin_and_end_with_no_body_is_benign(self):
        body = ("-----BEGIN PRIVATE KEY-----\n"
                "-----END PRIVATE KEY-----")
        self.assertNotIn("private_key_block", self.scan(body))

    def test_begin_and_end_with_prose_between_is_benign(self):
        body = ("-----BEGIN PRIVATE KEY-----\n"
                "this is a help string, not key material at all!!\n"
                "-----END PRIVATE KEY-----")
        self.assertNotIn("private_key_block", self.scan(body))

    def test_truncated_block_with_base64_body_is_candidate(self):
        # No END marker in the fetched text, but a base64 body starts
        # right after the header: body evidence is present.
        body = "-----BEGIN EC PRIVATE KEY-----\n" + PEM_BODY
        hit = self.scan(body)["private_key_block"]
        self.assertEqual(hit["class"], "CANDIDATE_EXPOSURE")

    def test_wrapped_base64_body_with_end_is_candidate(self):
        body = ("-----BEGIN OPENSSH PRIVATE KEY-----\n"
                + PEM_BODY[:32] + "\n" + PEM_BODY[32:] + "\n"
                "-----END OPENSSH PRIVATE KEY-----")
        hit = self.scan(body)["private_key_block"]
        self.assertEqual(hit["class"], "CANDIDATE_EXPOSURE")

    def test_base64_body_counts_even_without_matching_end(self):
        body = ("-----BEGIN PRIVATE KEY-----\n" + PEM_BODY + "\n"
                "-----END CERTIFICATE-----")
        hit = self.scan(body)["private_key_block"]
        self.assertEqual(hit["class"], "CANDIDATE_EXPOSURE")


class TestAnalyticsJwt(unittest.TestCase):
    """L1: analytics/experiment JWTs are annotated, not candidates."""

    def scan(self, payload):
        token = mint_jwt(payload)
        return by_pattern(scan_text(token, SITE, SOURCE))["jwt_in_page"]

    def test_long_lived_segment_jwt_stays_visitor_token(self):
        hit = self.scan({"iat": 1000, "exp": 1000 + 200000,
                         "iss": "https://api.segment.io/v1"})
        self.assertEqual(hit["class"], "VISITOR_TOKEN")
        self.assertEqual(hit["note"], "analytics/experiment JWT")
        self.assertEqual(hit["jwt_lifetime_s"], 200000)

    def test_experiment_claims_annotate(self):
        hit = self.scan({"iat": 1000, "exp": 1000 + 200000,
                         "experiments": ["checkout_v2"]})
        self.assertEqual(hit["class"], "VISITOR_TOKEN")
        self.assertEqual(hit["note"], "analytics/experiment JWT")

    def test_provider_audience_annotates_even_short_lived(self):
        hit = self.scan({"iat": 1000, "exp": 1300, "aud": "posthog"})
        self.assertEqual(hit["class"], "VISITOR_TOKEN")
        self.assertEqual(hit["note"], "analytics/experiment JWT")
        self.assertEqual(hit["jwt_lifetime_s"], 300)

    def test_feature_flag_claim_key_annotates(self):
        hit = self.scan({"iat": 1000, "exp": 1000 + 200000,
                         "feature_flags": {"new_nav": True}})
        self.assertEqual(hit["class"], "VISITOR_TOKEN")
        self.assertEqual(hit["note"], "analytics/experiment JWT")

    def test_plain_long_lived_session_jwt_still_candidate(self):
        hit = self.scan({"iat": 1000, "exp": 1000 + 200000,
                         "sub": "user-123", "role": "admin"})
        self.assertEqual(hit["class"], "CANDIDATE_EXPOSURE")
        self.assertEqual(hit["note"], "long-lived JWT served in page")


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
