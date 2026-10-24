"""Offline tests for the capture scrubber.

The scrubber's redaction table is derived from the scanner's pattern
table (src/wallcheck/exposure.py), so every class the scanner can find
must be a class the scrubber removes. Fixture values are synthetic and
obviously fake (FAKE... strings), embedded in a JSON capture written to
a temp dir; the scrubbed result must still parse as JSON, contain none
of the raw values, and scan clean under the scanner itself.
Run: python3 -m unittest discover -s tests -v
"""

import importlib.util
import json
import pathlib
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from wallcheck.exposure import scan_text  # noqa: E402


def _load_scrubber():
    path = os.path.join(os.path.dirname(__file__), "..",
                        "scripts", "scrub_captures.py")
    spec = importlib.util.spec_from_file_location("scrub_captures", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


scrub = _load_scrubber()

# Synthetic values, one per scanner class (see test_exposure.py).
# Built by concatenation so no literal in this file is shaped exactly
# like a real token (GitHub push protection cannot tell fakes apart).
VALUES = {
    "google_api_key": "AIza" + "FAKE" * 5 + "0123456",
    "wechat_app_id": "wx" + "0123456789abcdef",
    "public_env_sensitive_name": "FAKEENCRYPTIONKEY0123456789ABCDEF",
    "stripe_secret_key": "sk_live_" + "FAKE" * 4 + "1234",
    "stripe_publishable_key": "pk_live_" + "FAKE" * 4 + "1234",
    "stripe_webhook_secret": "whsec_" + "FAKE" * 5 + "0123",
    "github_token": "ghp_" + "FAKE" * 8,
    "slack_token": "xoxb-" + "FAKE-FAKE-" + "FAKE123456",
    "sendgrid_key": "SG." + "FAKE" * 5 + "12." + "FAKE" * 5 + "123",
    "twilio_api_key": "SK" + "0123456789abcdef" * 2,
    "db_url_with_password": "postgres://fakeuser:fakepass99@db.example.test/app",
    "generic_secret_field": "FAKESECRETVALUE0123456789",
    "google_oauth_client_id":
        "123456789012-fakefakefakefake.apps.googleusercontent.com",
    "mapbox_public_token": "pk.eyJFAKEFAKEFAKEFAKEFAKE0123456789",
}
PEM_BLOCK = ("-----BEGIN PRIVATE KEY-----\n"
             "FAKEBASE64BODYLINE0123456789\n"
             "-----END PRIVATE KEY-----")
JWT = ("eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0."
       "eyJpYXQiOjEwMDAsImV4cCI6MTMwMH0.FAKESIGNATURE0123456789")


def build_body():
    parts = [
        "google %s" % VALUES["google_api_key"],
        "wechat %s" % VALUES["wechat_app_id"],
        'NEXT_PUBLIC_APP_ENCRYPTION_KEY":"%s"'
        % VALUES["public_env_sensitive_name"],
        "stripe %s" % VALUES["stripe_secret_key"],
        "pub %s" % VALUES["stripe_publishable_key"],
        "hook %s" % VALUES["stripe_webhook_secret"],
        "gh %s" % VALUES["github_token"],
        "slack %s" % VALUES["slack_token"],
        "sg %s" % VALUES["sendgrid_key"],
        "twilio %s" % VALUES["twilio_api_key"],
        "db %s" % VALUES["db_url_with_password"],
        '{"api_secret": "%s"}' % VALUES["generic_secret_field"],
        "oauth %s" % VALUES["google_oauth_client_id"],
        "mapbox %s" % VALUES["mapbox_public_token"],
        "jwt %s" % JWT,
        PEM_BLOCK,
    ]
    return " ".join(parts)


class TestScrubCaptures(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)
        self.path = os.path.join(self.dir.name, "capture.json")
        capture = {"url": "https://example.test/login",
                   "status": 200, "body": build_body()}
        with open(self.path, "w") as f:
            json.dump(capture, f)

    def scrubbed_body(self):
        scrub.scrub_file(pathlib.Path(self.path))
        with open(self.path) as f:
            return json.load(f)["body"]

    def test_every_scanner_class_is_scrubbed(self):
        body = self.scrubbed_body()
        for name, value in VALUES.items():
            self.assertNotIn(value, body,
                             "%s value survived scrubbing" % name)
        self.assertNotIn("FAKEBASE64BODYLINE0123456789", body)
        self.assertNotIn(JWT, body)

    def test_markers_name_the_pattern(self):
        body = self.scrubbed_body()
        for marker in ("REDACTED-GOOGLE-API-KEY", "REDACTED-WECHAT-APP-ID",
                       "REDACTED-PUBLIC-ENV-SENSITIVE-NAME",
                       "REDACTED-STRIPE-SECRET-KEY",
                       "REDACTED-STRIPE-WEBHOOK-SECRET",
                       "REDACTED-GITHUB-TOKEN", "REDACTED-SLACK-TOKEN",
                       "REDACTED-SENDGRID-KEY", "REDACTED-TWILIO-API-KEY",
                       "REDACTED-DB-URL-WITH-PASSWORD",
                       "REDACTED-GENERIC-SECRET-FIELD",
                       "REDACTED-PRIVATE-KEY-BLOCK"):
            self.assertIn(marker, body)

    def test_redaction_count_covers_all_classes(self):
        count = scrub.scrub_file(pathlib.Path(self.path))
        # 14 table values + the JWT + the PEM block sweep = 16 redactions.
        self.assertEqual(count, len(VALUES) + 2)

    def test_scrubbed_capture_scans_clean(self):
        body = self.scrubbed_body()
        self.assertEqual(scan_text(body, "example.test", "capture"), [])

    def test_output_still_valid_json_with_other_fields_intact(self):
        scrub.scrub_file(pathlib.Path(self.path))
        with open(self.path) as f:
            data = json.load(f)
        self.assertEqual(data["url"], "https://example.test/login")
        self.assertEqual(data["status"], 200)

    def test_no_match_file_is_byte_identical_and_leaves_no_tmp(self):
        clean = os.path.join(self.dir.name, "clean.json")
        raw = json.dumps({"url": "https://example.test", "body": "hello"})
        with open(clean, "w") as f:
            f.write(raw)
        self.assertEqual(scrub.scrub_file(pathlib.Path(clean)), 0)
        with open(clean) as f:
            self.assertEqual(f.read(), raw)
        leftovers = [n for n in os.listdir(self.dir.name)
                     if n.endswith(".scrub-tmp")]
        self.assertEqual(leftovers, [])


if __name__ == "__main__":
    unittest.main()
