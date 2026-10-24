"""Ed25519 (RFC 8032) in pure Python: the correctness gate is the
official RFC 8032 section 7.1 test vectors — public-key derivation,
signing, and verification must reproduce them exactly. Plus the
RFC 9421 layer round-trips with an Ed25519 key (tamper / wrong key /
expiry), a public-key-only verify (the directory scenario), the
verify-server end to end, and the directory document shape.

Fully offline except one localhost round-trip against our own test
server."""

import base64
import os
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from wallcheck.sign import (directory_document, ed25519_public_key,
                            ed25519_sign, ed25519_verify, generate_key,
                            load_key, make_verify_handler, save_key,
                            sign_request, verify_request)
from http.server import ThreadingHTTPServer

URL = "https://www.example.com/some/path?q=1"

# RFC 8032 section 7.1 test vectors for Ed25519, transcribed from
# the RFC text (rfc-editor.org/rfc/rfc8032.txt): (secret seed,
# public key, message, signature), all hex.
RFC8032_VECTORS = [
    (  # TEST 1 — empty message
        "9d61b19deffd5a60ba844af492ec2cc4"
        "4449c5697b326919703bac031cae7f60",
        "d75a980182b10ab7d54bfed3c964073a"
        "0ee172f3daa62325af021a68f707511a",
        "",
        "e5564300c360ac729086e2cc806e828a"
        "84877f1eb8e5d974d873e06522490155"
        "5fb8821590a33bacc61e39701cf9b46b"
        "d25bf5f0595bbe24655141438e7a100b",
    ),
    (  # TEST 2 — 1-byte message
        "4ccd089b28ff96da9db6c346ec114e0f"
        "5b8a319f35aba624da8cf6ed4fb8a6fb",
        "3d4017c3e843895a92b70aa74d1b7ebc"
        "9c982ccf2ec4968cc0cd55f12af4660c",
        "72",
        "92a009a9f0d4cab8720e820b5f642540"
        "a2b27b5416503f8fb3762223ebdb69da"
        "085ac1e43e15996e458f3613d0f11d8c"
        "387b2eaeb4302aeeb00d291612bb0c00",
    ),
    (  # TEST 3 — 2-byte message
        "c5aa8df43f9f837bedb7442f31dcb7b1"
        "66d38535076f094b85ce3a2e0b4458f7",
        "fc51cd8e6218a1a38da47ed00230f058"
        "0816ed13ba3303ac5deb911548908025",
        "af82",
        "6291d657deec24024827e69c3abe01a3"
        "0ce548a284743a445e3680d7db5ac3ac"
        "18ff9b538d16f290ae67f760984dc659"
        "4a7c15e9716ed28dc027beceea1ec40a",
    ),
    (  # TEST SHA(abc) — 64-byte message (the SHA-512 digest of "abc")
        "833fe62409237b9d62ec77587520911e"
        "9a759cec1d19755b7da901b96dca3d42",
        "ec172b93ad5e563bf4932c70e1245034"
        "c35467ef2efd4d64ebf819683467e2bf",
        "ddaf35a193617abacc417349ae204131"
        "12e6fa4e89a97ea20a9eeee64b55d39a"
        "2192992a274fc1a836ba3c23a3feebbd"
        "454d4423643ce80e2a9ac94fa54ca49f",
        "dc2a4459e7369633a52b1bf277839a00"
        "201009a3efbf3ecb69bea2186c26b589"
        "09351fc9ac90b3ecfdfbc7c66431e030"
        "3dca179c138ac17ad9bef1177331a704",
    ),
]


class RFC8032VectorTests(unittest.TestCase):
    def test_public_keys_match(self):
        for sk, pk, _msg, _sig in RFC8032_VECTORS:
            derived = ed25519_public_key(bytes.fromhex(sk))
            self.assertEqual(derived.hex(), pk)

    def test_signatures_match(self):
        for sk, _pk, msg, sig in RFC8032_VECTORS:
            produced = ed25519_sign(bytes.fromhex(sk), bytes.fromhex(msg))
            self.assertEqual(produced.hex(), sig)

    def test_vectors_verify_and_tampering_fails(self):
        for _sk, pk, msg, sig in RFC8032_VECTORS:
            pub, m, s = (bytes.fromhex(pk), bytes.fromhex(msg),
                         bytes.fromhex(sig))
            self.assertTrue(ed25519_verify(pub, m, s))
            self.assertFalse(ed25519_verify(pub, m + b"x", s))
            bad = bytearray(s)
            bad[10] ^= 1
            self.assertFalse(ed25519_verify(pub, m, bytes(bad)))
            bad_s = bytearray(s)
            bad_s[63] ^= 1  # perturb S
            self.assertFalse(ed25519_verify(pub, m, bytes(bad_s)))

    def test_cross_check_with_pynacl_when_available(self):
        """Bonus interop evidence (not the gate): if PyNaCl happens
        to be installed, our signatures verify under it and vice
        versa. Skipped silently where it is absent — the core never
        depends on it."""
        try:
            import nacl.signing
        except ImportError:
            self.skipTest("PyNaCl not installed")
        seed = bytes(range(32))
        ours = ed25519_sign(seed, b"interop check")
        ref = nacl.signing.SigningKey(seed)
        self.assertEqual(ed25519_public_key(seed),
                         bytes(ref.verify_key))
        ref.verify_key.verify(b"interop check", ours)  # raises on mismatch
        ref_sig = ref.sign(b"interop check").signature
        self.assertTrue(
            ed25519_verify(bytes(ref.verify_key), b"interop check",
                           ref_sig))


class Ed25519KeyTests(unittest.TestCase):
    def test_keygen_roundtrip_through_file(self):
        key = generate_key(alg="ed25519")
        self.assertEqual(key["alg"], "ed25519")
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "k.json")
            save_key(key, path)
            self.assertEqual(oct(os.stat(path).st_mode & 0o777), "0o600")
            loaded = load_key(path)
        self.assertEqual(loaded["keyid"], key["keyid"])
        self.assertEqual(len(loaded["_seed"]), 32)
        self.assertEqual(len(loaded["_public"]), 32)
        self.assertEqual(
            loaded["_public"],
            ed25519_public_key(loaded["_seed"]))

    def test_directory_document_shape(self):
        key = generate_key(keyid="dir-test", alg="ed25519")
        doc = directory_document(key)
        self.assertEqual(doc["purpose"], "Web Bot Auth")
        (jwk,) = doc["keys"]
        self.assertEqual(jwk["kty"], "OKP")
        self.assertEqual(jwk["crv"], "Ed25519")
        self.assertEqual(jwk["kid"], "dir-test")
        x = base64.urlsafe_b64decode(jwk["x"] + "=" * (-len(jwk["x"]) % 4))
        self.assertEqual(x, base64.b64decode(key["public_b64"]))

    def test_hmac_key_cannot_be_published(self):
        with self.assertRaises(ValueError):
            directory_document(generate_key())


class Ed25519SignVerifyTests(unittest.TestCase):
    def setUp(self):
        self.key = generate_key(keyid="ed-test-1", alg="ed25519")

    def test_roundtrip_ok_and_alg_labelled(self):
        headers = sign_request(URL, self.key)
        self.assertIn('alg="ed25519"', headers["Signature-Input"])
        self.assertIn('tag="web-bot-auth"', headers["Signature-Input"])
        ok, reason = verify_request(headers, "www.example.com", self.key)
        self.assertTrue(ok, reason)

    def test_tampered_authority_fails(self):
        headers = sign_request(URL, self.key)
        ok, _ = verify_request(headers, "evil.example.com", self.key)
        self.assertFalse(ok)

    def test_tampered_signature_fails(self):
        headers = sign_request(URL, self.key)
        raw = bytearray(base64.b64decode(
            headers["Signature"].split(":", 2)[1]))
        raw[0] ^= 1
        headers = dict(headers)
        headers["Signature"] = "sig1=:%s:" % base64.b64encode(
            bytes(raw)).decode()
        ok, _ = verify_request(headers, "www.example.com", self.key)
        self.assertFalse(ok)

    def test_wrong_key_fails(self):
        headers = sign_request(URL, self.key)
        other = generate_key(keyid="ed-test-1", alg="ed25519")
        ok, _ = verify_request(headers, "www.example.com", other)
        self.assertFalse(ok)

    def test_expired_fails(self):
        import time
        old = int(time.time()) - 1000
        headers = sign_request(URL, self.key, created=old, lifetime=60)
        ok, reason = verify_request(headers, "www.example.com", self.key)
        self.assertFalse(ok)
        self.assertIn("expired", reason)

    def test_content_type_covered_when_present(self):
        headers = sign_request(URL, self.key,
                               content_type="application/json")
        ok, reason = verify_request(
            dict(headers, **{"Content-Type": "application/json"}),
            "www.example.com", self.key)
        self.assertTrue(ok, reason)

    def test_public_only_key_verifies(self):
        """The directory scenario: a verifier holding only the
        published public key (no seed) can verify."""
        headers = sign_request(URL, self.key)
        public_only = {"version": 1, "keyid": self.key["keyid"],
                       "alg": "ed25519",
                       "public_b64": self.key["public_b64"],
                       "_public": base64.b64decode(self.key["public_b64"])}
        ok, reason = verify_request(headers, "www.example.com",
                                    public_only)
        self.assertTrue(ok, reason)

    def test_hmac_signature_rejected_under_ed_key(self):
        hmac_key = generate_key(keyid="ed-test-1")
        headers = sign_request(URL, hmac_key)
        ok, _ = verify_request(headers, "www.example.com", self.key)
        self.assertFalse(ok)


class Ed25519VerifyServerTests(unittest.TestCase):
    def test_verify_server_end_to_end(self):
        key = generate_key(keyid="srv-ed", alg="ed25519")
        server = ThreadingHTTPServer(("127.0.0.1", 0),
                                     make_verify_handler(key))
        port = server.server_address[1]
        t = threading.Thread(target=server.serve_forever, daemon=True)
        t.start()
        base = "http://127.0.0.1:%d/" % port
        try:
            with self.assertRaises(urllib.error.HTTPError) as cm:
                urllib.request.urlopen(base, timeout=10)
            self.assertEqual(cm.exception.code, 401)

            headers = sign_request(base, key)
            req = urllib.request.Request(base, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                self.assertEqual(resp.status, 200)

            wrong = generate_key(keyid="srv-ed", alg="ed25519")
            req = urllib.request.Request(base,
                                         headers=sign_request(base, wrong))
            with self.assertRaises(urllib.error.HTTPError) as cm:
                urllib.request.urlopen(req, timeout=10)
            self.assertEqual(cm.exception.code, 401)
        finally:
            server.shutdown()


if __name__ == "__main__":
    unittest.main()
