"""RFC 9421 (hmac-sha256) signing: round-trip, tamper, expiry, and
the verify-server end to end. Fully offline except one localhost
round-trip against our own test server."""

import base64
import os
import sys
import tempfile
import threading
import time
import unittest
import urllib.error
import urllib.request

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from wallcheck.sign import (generate_key, load_key, make_verify_handler,
                            save_key, sign_request, verify_request)
from http.server import ThreadingHTTPServer

URL = "https://www.example.com/some/path?q=1"


def _ready(key):
    """generate_key returns the persistable dict; attach the raw secret
    the way load_key does."""
    key["_secret"] = base64.b64decode(key["secret_b64"])
    return key


class KeyTests(unittest.TestCase):
    def test_keygen_roundtrip_through_file(self):
        key = generate_key()
        self.assertEqual(key["alg"], "hmac-sha256")
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "k.json")
            save_key(key, path)
            self.assertEqual(oct(os.stat(path).st_mode & 0o777), "0o600")
            loaded = load_key(path)
        self.assertEqual(loaded["keyid"], key["keyid"])
        self.assertEqual(len(loaded["_secret"]), 32)


class SignVerifyTests(unittest.TestCase):
    def setUp(self):
        self.key = _ready(generate_key(keyid="test-key-1"))

    def _headers(self, url=URL, **kw):
        return sign_request(url, self.key, **kw)

    def test_roundtrip_ok(self):
        headers = self._headers()
        ok, reason = verify_request(headers, "www.example.com", self.key)
        self.assertTrue(ok, reason)
        self.assertIn("web-bot-auth", reason)

    def test_signature_input_shape(self):
        headers = self._headers()
        si = headers["Signature-Input"]
        self.assertIn('("@authority")', si)
        self.assertIn('alg="hmac-sha256"', si)
        self.assertIn('tag="web-bot-auth"', si)
        self.assertIn("created=", si)
        self.assertIn("expires=", si)
        self.assertIn("nonce=", si)
        self.assertTrue(headers["Signature"].startswith("sig1=:"))
        self.assertTrue(headers["Signature"].endswith(":"))

    def test_content_type_covered_when_present(self):
        headers = sign_request(URL, self.key,
                               content_type="application/json")
        self.assertIn('"content-type"', headers["Signature-Input"])
        ok, reason = verify_request(
            dict(headers, **{"Content-Type": "application/json"}),
            "www.example.com", self.key)
        self.assertTrue(ok, reason)

    def test_tampered_authority_fails(self):
        headers = self._headers()
        ok, reason = verify_request(headers, "evil.example.com", self.key)
        self.assertFalse(ok)
        self.assertIn("mismatch", reason)

    def test_tampered_signature_fails(self):
        headers = self._headers()
        sig = headers["Signature"]
        flipped = sig[:8] + ("A" if sig[8] != "A" else "B") + sig[9:]
        ok, _ = verify_request(dict(headers, Signature=flipped),
                               "www.example.com", self.key)
        self.assertFalse(ok)

    def test_tampered_params_fail(self):
        headers = self._headers()
        si = headers["Signature-Input"]
        # flip one char inside the signed params: base changes -> mismatch
        si2 = si[:-3] + ("x" if si[-3] != "x" else "y") + si[-2:]
        ok, _ = verify_request(dict(headers, **{"Signature-Input": si2}),
                               "www.example.com", self.key)
        self.assertFalse(ok)

    def test_expired_fails(self):
        old = int(time.time()) - 1000
        headers = sign_request(URL, self.key, created=old, lifetime=60)
        ok, reason = verify_request(headers, "www.example.com", self.key)
        self.assertFalse(ok)
        self.assertIn("expired", reason)

    def test_wrong_secret_fails(self):
        headers = self._headers()
        other = _ready(generate_key(keyid="test-key-1"))  # same keyid, new secret
        ok, _ = verify_request(headers, "www.example.com", other)
        self.assertFalse(ok)

    def test_unknown_keyid_fails(self):
        headers = self._headers()
        other = dict(self.key, keyid="someone-else")
        ok, reason = verify_request(headers, "www.example.com", other)
        self.assertFalse(ok)
        self.assertIn("keyid", reason)

    def test_missing_headers_fail(self):
        ok, reason = verify_request({}, "www.example.com", self.key)
        self.assertFalse(ok)
        self.assertIn("missing", reason)


class VerifyServerTests(unittest.TestCase):
    """End to end: our server accepts our signatures, rejects the rest."""

    @classmethod
    def setUpClass(cls):
        cls.key = _ready(generate_key(keyid="server-test"))
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0),
                                         make_verify_handler(cls.key))
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever,
                                      daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def _get(self, headers=None):
        req = urllib.request.Request(
            "http://127.0.0.1:%d/" % self.port, headers=headers or {})
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                return resp.status, resp.read().decode()
        except urllib.error.HTTPError as e:
            return e.code, e.read().decode()

    def test_unsigned_rejected(self):
        code, body = self._get()
        self.assertEqual(code, 401)
        self.assertIn("rejected", body)

    def test_signed_accepted(self):
        url = "http://127.0.0.1:%d/" % self.port
        headers = sign_request(url, self.key)
        code, body = self._get(headers)
        self.assertEqual(code, 200, body)
        self.assertIn("signature OK", body)

    def test_wrong_key_rejected(self):
        url = "http://127.0.0.1:%d/" % self.port
        other = _ready(generate_key(keyid="server-test"))
        code, _ = self._get(sign_request(url, other))
        self.assertEqual(code, 401)


if __name__ == "__main__":
    unittest.main()
