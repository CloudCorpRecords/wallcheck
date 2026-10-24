"""Signed agent identity (Web Bot Auth style), RFC 9421 HTTP Message
Signatures — two algorithms, both Python-standard-library-only:

- `hmac-sha256` (RFC 9421 §3.3.3): shared-secret signatures. Real RFC
  9421, but a shared secret cannot be published in a key directory,
  so this covers the bilateral case (agent operator ↔ site owner who
  agreed on a secret out of band) and owner-side testing.
- `ed25519` (RFC 9421 §3.3.2 over RFC 8032 Ed25519): public-key
  signatures, implemented in pure Python below (SHA-512 from
  `hashlib`, curve arithmetic on big integers, extended twisted
  Edwards coordinates). This is the algorithm the public Web Bot
  Auth ecosystem (Cloudflare's directory, the IETF draft) is built
  on: the public key can be published in a
  `/.well-known/http-message-signatures-directory` document (see
  `directory_document`), and anyone can verify without holding a
  secret. The implementation is verified against the official
  RFC 8032 §7.1 test vectors in tests/test_ed25519.py — that gate,
  not enthusiasm, is why it ships. Pure-Python big-int math is not
  constant-time; performance and side-channel hardening are
  explicit non-goals here (one signature per probe fetch).

The signature identifies the request. It grants nothing, bypasses
nothing, and is attached only to the same single honest fetch the
unsigned probe would have made.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import re
import secrets
import time
import urllib.parse

ALG = "hmac-sha256"
ALG_ED25519 = "ed25519"
ALGS = (ALG, ALG_ED25519)
TAG = "web-bot-auth"
DEFAULT_LIFETIME = 300  # seconds; signature validity window


# ---------------------------------------------------------------- keys

def generate_key(keyid=None, alg=ALG):
    """Return a fresh key dict (not yet persisted)."""
    key = {
        "version": 1,
        "keyid": keyid or ("wallcheck-" + secrets.token_hex(4)),
        "alg": alg,
        "created": int(time.time()),
    }
    if alg == ALG:
        key["secret_b64"] = base64.b64encode(
            secrets.token_bytes(32)).decode("ascii")
    elif alg == ALG_ED25519:
        seed = secrets.token_bytes(32)
        key["seed_b64"] = base64.b64encode(seed).decode("ascii")
        key["public_b64"] = base64.b64encode(
            ed25519_public_key(seed)).decode("ascii")
    else:
        raise ValueError("unsupported alg: %r (expected one of %r)"
                         % (alg, ALGS))
    return key


def save_key(key, path):
    """Write the key file with owner-only permissions."""
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        json.dump(key, f, indent=2, sort_keys=True)
        f.write("\n")
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass
    return path


def load_key(path):
    """Load a key file written by save_key; returns the dict with the
    raw key material attached (`_secret` for HMAC, `_seed`/`_public`
    for Ed25519)."""
    with open(path) as f:
        key = json.load(f)
    if key.get("alg") not in ALGS:
        raise ValueError("unsupported key alg: %r (expected one of %r)"
                         % (key.get("alg"), ALGS))
    if key["alg"] == ALG:
        key["_secret"] = base64.b64decode(key["secret_b64"])
    else:
        if key.get("seed_b64"):
            key["_seed"] = base64.b64decode(key["seed_b64"])
        key["_public"] = base64.b64decode(key["public_b64"])
    return key


def key_fingerprint(key):
    """Non-secret identifier for display. HMAC: sha256 over the
    secret (identifies without revealing). Ed25519: sha256 over the
    public key (public anyway; stable across seed handling)."""
    if key.get("alg") == ALG_ED25519:
        public = key.get("_public") or base64.b64decode(key["public_b64"])
        return hashlib.sha256(public).hexdigest()[:16]
    secret = key.get("_secret") or base64.b64decode(key["secret_b64"])
    return hashlib.sha256(secret).hexdigest()[:16]


def _b64url_nopad(raw):
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def directory_document(key):
    """The Web Bot Auth directory document (JWKS-style) for an
    Ed25519 key — what a signer publishes at
    /.well-known/http-message-signatures-directory so any site can
    discover and verify its public key. HMAC keys cannot be
    published (the 'key' is the secret); asking raises ValueError."""
    if key.get("alg") != ALG_ED25519:
        raise ValueError("only ed25519 keys can be published in a "
                         "directory (an hmac-sha256 secret must stay "
                         "secret)")
    public = key.get("_public") or base64.b64decode(key["public_b64"])
    return {
        "purpose": "Web Bot Auth",
        "keys": [{
            "kty": "OKP",
            "crv": "Ed25519",
            "kid": key["keyid"],
            "x": _b64url_nopad(public),
        }],
    }


# ------------------------------------------------------- sf primitives

def _sf_string(value):
    return '"%s"' % str(value).replace("\\", "\\\\").replace('"', '\\"')


def _parse_sf_string(text, i):
    """Parse an sf-string starting at text[i] == '"'. Returns (value, next_i)."""
    assert text[i] == '"'
    out, i = [], i + 1
    while i < len(text):
        c = text[i]
        if c == "\\":
            out.append(text[i + 1])
            i += 2
        elif c == '"':
            return "".join(out), i + 1
        else:
            out.append(c)
            i += 1
    raise ValueError("unterminated sf-string")


# ---------------------------------------------------------------- sign

def authority_of(url):
    """The @authority component value for a URL: lowercase host, with
    port only when explicitly present (userinfo stripped)."""
    parts = urllib.parse.urlsplit(url)
    host = (parts.hostname or "").lower()
    if parts.port:
        return "%s:%d" % (host, parts.port)
    return host


def _signature_params(components, keyid, created, expires, nonce, alg=ALG):
    inner = "(" + " ".join(_sf_string(c) for c in components) + ")"
    return (inner
            + ";keyid=" + _sf_string(keyid)
            + ";alg=" + _sf_string(alg)
            + ";created=%d" % created
            + ";expires=%d" % expires
            + ";nonce=" + _sf_string(nonce)
            + ";tag=" + _sf_string(TAG))


def signature_base(components, params_str, authority, content_type=None):
    """RFC 9421 section 3.1 signature base for our component set."""
    lines = []
    for comp in components:
        if comp == "@authority":
            value = authority
        elif comp == "content-type":
            if content_type is None:
                raise ValueError("content-type covered but not provided")
            value = " ".join(str(content_type).split())  # OWS-normalized
        else:
            raise ValueError("unsupported component: %r" % comp)
        lines.append("%s: %s" % (_sf_string(comp), value))
    lines.append("%s: %s" % (_sf_string("@signature-params"), params_str))
    return "\n".join(lines)


def _sign_bytes(key, base_bytes):
    """Raw signature over the RFC 9421 signature base, dispatched on
    the key's algorithm."""
    if key.get("alg") == ALG_ED25519:
        seed = key.get("_seed") or base64.b64decode(key["seed_b64"])
        return ed25519_sign(seed, base_bytes)
    secret = key.get("_secret") or base64.b64decode(key["secret_b64"])
    return hmac.new(secret, base_bytes, hashlib.sha256).digest()


def sign_request(url, key, content_type=None, created=None,
                 lifetime=DEFAULT_LIFETIME, nonce=None, label="sig1"):
    """Build (Signature-Input, Signature) header values for a request
    to `url`, signed with `key` (a dict from generate_key/load_key).
    The algorithm comes from the key — hmac-sha256 or ed25519."""
    created = int(time.time()) if created is None else int(created)
    expires = created + int(lifetime)
    nonce = nonce or secrets.token_hex(8)
    components = ["@authority"]
    if content_type is not None:
        components.append("content-type")
    params = _signature_params(components, key["keyid"], created, expires,
                               nonce, alg=key.get("alg", ALG))
    base = signature_base(components, params, authority_of(url), content_type)
    sig_b64 = base64.b64encode(
        _sign_bytes(key, base.encode("utf-8"))).decode("ascii")
    return {
        "Signature-Input": "%s=%s" % (label, params),
        "Signature": "%s=:%s:" % (label, sig_b64),
    }


# -------------------------------------------------------------- verify

_INPUT_RE = re.compile(r"^([A-Za-z0-9_-]+)=\(")


def _parse_signature_input(value):
    """Parse one label's entry from a Signature-Input header value.
    Returns (label, components list, params dict, raw_params_str).
    Deliberately small: handles the sf shapes RFC 9421 signers emit
    for inner lists of strings + string/int params."""
    value = value.strip()
    m = _INPUT_RE.match(value)
    if not m:
        raise ValueError("malformed Signature-Input")
    label = m.group(1)
    i = m.end()  # just past '('
    components = []
    while True:
        while i < len(value) and value[i] == " ":
            i += 1
        if i < len(value) and value[i] == ")":
            i += 1
            break
        comp, i = _parse_sf_string(value, i)
        components.append(comp)
    raw_params = value[i:]  # ';keyid=...;alg=...' exactly as signed
    params = {}
    for part in raw_params.split(";"):
        part = part.strip()
        if not part:
            continue
        if "=" in part:
            k, v = part.split("=", 1)
            v = v.strip()
            if v.startswith('"'):
                v, _ = _parse_sf_string(v, 0)
            else:
                try:
                    v = int(v)
                except ValueError:
                    pass
            params[k.strip()] = v
        else:
            params[part] = True
    return label, components, params, raw_params


def _extract_signature(sig_header, label):
    m = re.search(r"(?:^|,)\s*%s=:([^:]+):" % re.escape(label), sig_header)
    if not m:
        raise ValueError("no signature for label %r" % label)
    return m.group(1)


def verify_request(headers, authority, key, now=None):
    """Verify an RFC 9421 signature over @authority (+ content-type
    when covered). `headers` is a case-insensitive-ish dict of the
    request's headers; `key` as from load_key/generate_key.
    Returns (ok: bool, reason: str). Offline; no network."""
    h = {str(k).lower(): str(v) for k, v in (headers or {}).items()}
    sig_input = h.get("signature-input")
    sig_header = h.get("signature")
    if not sig_input or not sig_header:
        return False, "missing Signature/Signature-Input headers"
    try:
        label, components, params, raw_params = _parse_signature_input(sig_input)
        sig_b64 = _extract_signature(sig_header, label)
        presented = base64.b64decode(sig_b64)
    except Exception as e:
        return False, "malformed: %s" % e
    if params.get("alg") not in ALGS:
        return False, "unsupported alg: %r" % params.get("alg")
    if params.get("alg") != key.get("alg"):
        return False, "alg mismatch: signature says %r, key is %r" % (
            params.get("alg"), key.get("alg"))
    if params.get("keyid") != key.get("keyid"):
        return False, "unknown keyid: %r" % params.get("keyid")
    now = int(time.time()) if now is None else int(now)
    created, expires = params.get("created"), params.get("expires")
    if not isinstance(created, int) or not isinstance(expires, int):
        return False, "missing created/expires"
    if now < created:
        return False, "signature not yet valid (created in the future)"
    if now > expires:
        return False, "signature expired"
    params_str = ("(" + " ".join(_sf_string(c) for c in components) + ")"
                  + raw_params)
    try:
        base = signature_base(components, params_str, authority,
                              h.get("content-type"))
    except ValueError as e:
        return False, str(e)
    if key.get("alg") == ALG_ED25519:
        public = key.get("_public") or base64.b64decode(key["public_b64"])
        if not ed25519_verify(public, base.encode("utf-8"), presented):
            return False, "signature mismatch"
    else:
        secret = key.get("_secret") or base64.b64decode(key["secret_b64"])
        expected = hmac.new(secret, base.encode("utf-8"),
                            hashlib.sha256).digest()
        if not hmac.compare_digest(expected, presented):
            return False, "signature mismatch"
    return True, "ok (keyid %s, tag %s)" % (params.get("keyid"),
                                            params.get("tag"))


# -------------------------------------------------------- test server

def make_verify_handler(key):
    """An http.server handler class that answers 200 only to requests
    carrying a signature that verifies against `key`."""
    from http.server import BaseHTTPRequestHandler

    class VerifyHandler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def _handle(self):
            authority = self.headers.get("Host", "")
            ok, reason = verify_request(dict(self.headers.items()),
                                        authority, key)
            code = 200 if ok else 401
            body = ("wallcheck verify-server: %s\n"
                    % ("signature OK — " + reason if ok
                       else "rejected — " + reason)).encode()
            self.send_response(code)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        do_GET = _handle
        do_POST = _handle

        def log_message(self, *args):  # keep the terminal clean
            pass

    return VerifyHandler


def serve_verify_server(key, host, port):
    from http.server import ThreadingHTTPServer
    server = ThreadingHTTPServer((host, port), make_verify_handler(key))
    print("wallcheck verify-server on http://%s:%d (keyid %s, alg %s)"
          % (host, port, key["keyid"], key.get("alg", ALG)))
    print("unsigned requests get 401; requests signed with the key get 200.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


# ------------------------------------------------- Ed25519 (RFC 8032)
# Pure-Python Ed25519 over hashlib's SHA-512 and big-integer field
# arithmetic, points in extended twisted Edwards coordinates
# (add-2008-hwcd / dbl-2008-hwcd formulas; no inversions per op).
# Correctness is gated on the official RFC 8032 section 7.1 test
# vectors — see tests/test_ed25519.py. Not constant-time; one
# signature per probe fetch is the whole workload.

_ED_Q = 2 ** 255 - 19
_ED_L = 2 ** 252 + 27742317777372353535851937790883648493
_ED_D = (-121665 * pow(121666, _ED_Q - 2, _ED_Q)) % _ED_Q
_ED_D2 = (2 * _ED_D) % _ED_Q
_ED_I = pow(2, (_ED_Q - 1) // 4, _ED_Q)  # sqrt(-1) mod q
_ED_IDENTITY = (0, 1, 1, 0)


def _ed_recover_x(y, sign):
    """x for a y coordinate with the given sign bit, or None when no
    such point exists (RFC 8032 section 5.1.3 decoding rules)."""
    if y >= _ED_Q:
        return None
    xx = ((y * y - 1) * pow(_ED_D * y * y + 1, _ED_Q - 2, _ED_Q)) % _ED_Q
    x = pow(xx, (_ED_Q + 3) // 8, _ED_Q)
    if (x * x - xx) % _ED_Q != 0:
        x = (x * _ED_I) % _ED_Q
    if (x * x - xx) % _ED_Q != 0:
        return None
    if x == 0 and sign:
        return None  # RFC: x = 0 with the sign bit set is invalid
    if (x & 1) != sign:
        x = _ED_Q - x
    return x


def _ed_base_point():
    by = (4 * pow(5, _ED_Q - 2, _ED_Q)) % _ED_Q
    bx = _ed_recover_x(by, 0)  # base point x is even
    return (bx, by, 1, (bx * by) % _ED_Q)


_ED_B = _ed_base_point()


def _ed_add(P, Q):
    X1, Y1, Z1, T1 = P
    X2, Y2, Z2, T2 = Q
    A = ((Y1 - X1) * (Y2 - X2)) % _ED_Q
    B = ((Y1 + X1) * (Y2 + X2)) % _ED_Q
    C = (_ED_D2 * T1 * T2) % _ED_Q
    D = (2 * Z1 * Z2) % _ED_Q
    E, F, G, H = B - A, D - C, D + C, B + A
    return ((E * F) % _ED_Q, (G * H) % _ED_Q, (F * G) % _ED_Q,
            (E * H) % _ED_Q)


def _ed_double(P):
    X1, Y1, Z1, _ = P
    A = (X1 * X1) % _ED_Q
    B = (Y1 * Y1) % _ED_Q
    C = (2 * Z1 * Z1) % _ED_Q
    D = (-A) % _ED_Q
    E = ((X1 + Y1) * (X1 + Y1) - A - B) % _ED_Q
    G, F, H = D + B, D + B - C, D - B
    return ((E * F) % _ED_Q, (G * H) % _ED_Q, (F * G) % _ED_Q,
            (E * H) % _ED_Q)


def _ed_scalarmult(P, e):
    Q = _ED_IDENTITY
    for i in range(e.bit_length() - 1, -1, -1):
        Q = _ed_double(Q)
        if (e >> i) & 1:
            Q = _ed_add(Q, P)
    return Q


def _ed_encode(P):
    X, Y, Z, _ = P
    zinv = pow(Z, _ED_Q - 2, _ED_Q)
    x, y = (X * zinv) % _ED_Q, (Y * zinv) % _ED_Q
    return (y | ((x & 1) << 255)).to_bytes(32, "little")


def _ed_decode(data):
    if len(data) != 32:
        return None
    v = int.from_bytes(data, "little")
    y, sign = v & (2 ** 255 - 1), v >> 255
    x = _ed_recover_x(y, sign)
    if x is None:
        return None
    return (x, y, 1, (x * y) % _ED_Q)


def _ed_clamp(h32):
    a = int.from_bytes(h32, "little")
    a &= (1 << 254) - 8
    a |= 1 << 254
    return a


def _ed_hash_int(*parts):
    h = hashlib.sha512()
    for p in parts:
        h.update(p)
    return int.from_bytes(h.digest(), "little") % _ED_L


def ed25519_public_key(seed):
    """32-byte seed -> 32-byte encoded public key (RFC 8032 5.1.5)."""
    if len(seed) != 32:
        raise ValueError("ed25519 seed must be 32 bytes")
    h = hashlib.sha512(seed).digest()
    a = _ed_clamp(h[:32])
    return _ed_encode(_ed_scalarmult(_ED_B, a))


def ed25519_sign(seed, message):
    """32-byte seed + message -> 64-byte RFC 8032 signature."""
    if len(seed) != 32:
        raise ValueError("ed25519 seed must be 32 bytes")
    h = hashlib.sha512(seed).digest()
    a = _ed_clamp(h[:32])
    prefix = h[32:]
    public = _ed_encode(_ed_scalarmult(_ED_B, a))
    r = _ed_hash_int(prefix, message)
    r_enc = _ed_encode(_ed_scalarmult(_ED_B, r))
    k = _ed_hash_int(r_enc, public, message)
    s = (r + k * a) % _ED_L
    return r_enc + s.to_bytes(32, "little")


def ed25519_verify(public, message, signature):
    """Encoded public key + message + 64-byte signature -> bool.
    Cofactorless group equation [S]B = R + [k]A, with S required in
    [0, L) and both encoded points required to decode (RFC 8032
    5.1.7)."""
    if len(public) != 32 or len(signature) != 64:
        return False
    r_enc, s = signature[:32], int.from_bytes(signature[32:], "little")
    if s >= _ED_L:
        return False
    A = _ed_decode(public)
    R = _ed_decode(r_enc)
    if A is None or R is None:
        return False
    k = _ed_hash_int(r_enc, public, message)
    return _ed_encode(_ed_scalarmult(_ED_B, s)) == \
        _ed_encode(_ed_add(R, _ed_scalarmult(A, k)))
