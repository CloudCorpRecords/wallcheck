"""Exposure scan library: find key-like material in what a site serves
to an anonymous, plainly-identified visitor.

Pure functions, standard library only, no network — the pattern table
here is the single source of truth shared by the probe (opt-in), the
scripts/exposure_scan.py sweep tool and the scripts/scrub_captures.py
redactor, so the three can never drift apart.

Findings are classified:

  CANDIDATE_EXPOSURE  server-secret classes that should never be public
                      (encryption/private keys, live secret keys, tokens,
                      credentialed DB URLs, secret JSON fields)
  PUBLIC_BY_DESIGN    the public half of the web's key pairs (Google
                      frontend keys, Stripe publishable keys, app IDs,
                      OAuth client IDs) — normal, not a finding
  VISITOR_TOKEN       short-lived JWTs a site issues to any visitor
                      (WAF/session tokens) — wall machinery, not a leak

Found values are NEVER stored in a finding. A finding carries only:
pattern name, class, value length and a SHA-256 fingerprint prefix —
enough for the owner to recognise their key, useless to anyone else.
"""

from __future__ import annotations

import base64
import hashlib
import json
import re

PLACEHOLDER = re.compile(
    r"REDACTED|xxxx|your[-_ ]|example|placeholder|changeme|dummy|test[-_]?key",
    re.I,
)


def fp(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()[:16]


# --- pattern table -------------------------------------------------------
# Each entry: (name, class, regex). The regex must capture the secret-ish
# value in group "v" when it has one; name-only matches use group "n".

ENV_SENSITIVE = (
    r"(?:NEXT_PUBLIC_|NUXT_PUBLIC_|VITE_|REACT_APP_|GATSBY_)"
    r"[A-Z0-9_]*(?:SECRET|PRIVATE|ENCRYPTION|PASSWORD|AUTH_TOKEN)[A-Z0-9_]*"
)
ENV_ANY_KEY = (
    r"(?:NEXT_PUBLIC_|NUXT_PUBLIC_|VITE_|REACT_APP_|GATSBY_)[A-Z0-9_]*KEY[A-Z0-9_]*"
)
ENV_ASSIGN = r"\\*\"?\s*[:=]\s*\\*\"?(?P<v>[^\"\\,\s}{]{8,})"

PATTERNS = [
    ("public_env_sensitive_name", "CANDIDATE_EXPOSURE",
     re.compile(r"(?P<n>" + ENV_SENSITIVE + r")" + ENV_ASSIGN)),
    ("stripe_secret_key", "CANDIDATE_EXPOSURE",
     re.compile(r"\b(?P<v>(?:sk|rk)_live_[0-9A-Za-z]{10,})")),
    ("stripe_webhook_secret", "CANDIDATE_EXPOSURE",
     re.compile(r"\b(?P<v>whsec_[0-9A-Za-z]{20,})")),
    ("github_token", "CANDIDATE_EXPOSURE",
     re.compile(r"\b(?P<v>(?:gh[pousr]_[0-9A-Za-z]{30,}|github_pat_[0-9A-Za-z_]{50,}))")),
    ("slack_token", "CANDIDATE_EXPOSURE",
     re.compile(r"\b(?P<v>xox[bpas]-[0-9A-Za-z-]{10,})")),
    ("sendgrid_key", "CANDIDATE_EXPOSURE",
     re.compile(r"\b(?P<v>SG\.[0-9A-Za-z_-]{20,}\.[0-9A-Za-z_-]{20,})")),
    ("twilio_api_key", "CANDIDATE_EXPOSURE",
     re.compile(r"\b(?P<v>SK[0-9a-f]{32})\b")),
    ("private_key_block", "CANDIDATE_EXPOSURE",
     re.compile(r"(?P<v>-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)")),
    ("db_url_with_password", "CANDIDATE_EXPOSURE",
     re.compile(r"(?P<v>(?:postgres(?:ql)?|mysql|mongodb(?:\+srv)?|redis|amqp)://[^\s\"'/:]+:[^\s\"'@]{4,}@)")),
    ("generic_secret_field", "CANDIDATE_EXPOSURE",
     re.compile(r"[\"']?(?:api_secret|client_secret|app_secret|auth_token|access_token|private_key|aws_secret_access_key)[\"']?\s*[:=]\s*[\"'](?P<v>[^\"']{16,})[\"']", re.I)),
    ("google_api_key", "PUBLIC_BY_DESIGN",
     re.compile(r"\b(?P<v>AIza[0-9A-Za-z\-_]{20,})")),
    ("stripe_publishable_key", "PUBLIC_BY_DESIGN",
     re.compile(r"\b(?P<v>pk_(?:live|test)_[0-9A-Za-z]{10,})")),
    ("wechat_app_id", "PUBLIC_BY_DESIGN",
     re.compile(r"\b(?P<v>wx[0-9a-f]{16})\b")),
    ("google_oauth_client_id", "PUBLIC_BY_DESIGN",
     re.compile(r"\b(?P<v>[0-9]{6,}-[0-9a-z]+\.apps\.googleusercontent\.com)")),
    ("mapbox_public_token", "PUBLIC_BY_DESIGN",
     re.compile(r"\b(?P<v>pk\.eyJ[0-9A-Za-z\-_.]{20,})")),
    ("public_env_api_key", "PUBLIC_BY_DESIGN",
     re.compile(r"(?P<n>" + ENV_ANY_KEY + r")" + ENV_ASSIGN)),
    ("jwt_in_page", "VISITOR_TOKEN",
     re.compile(r"\b(?P<v>eyJ[0-9A-Za-z_-]{10,}\.eyJ[0-9A-Za-z_-]{10,}\.[0-9A-Za-z_-]{10,})")),
]


def jwt_lifetime(token: str):
    try:
        payload = token.split(".")[1]
        payload += "=" * (-len(payload) % 4)
        data = json.loads(base64.urlsafe_b64decode(payload))
        if "exp" in data and "iat" in data:
            return int(data["exp"]) - int(data["iat"])
    except Exception:
        pass
    return None


def scan_text(text: str, site: str, source: str):
    findings, seen = [], set()
    for name, cls, pat in PATTERNS:
        for m in pat.finditer(text):
            value = m.groupdict().get("v") or ""
            if PLACEHOLDER.search(value):
                continue
            key = (name, fp(value) if value else (m.groupdict().get("n") or ""))
            if key in seen:
                continue
            seen.add(key)
            f = {
                "site": site, "source": source, "class": cls, "pattern": name,
                "value_len": len(value),
                "sha256_16": fp(value) if value else None,
            }
            if m.groupdict().get("n"):
                f["var_name"] = m.group("n")
            if name == "jwt_in_page":
                life = jwt_lifetime(value)
                f["jwt_lifetime_s"] = life
                if life is not None and life > 86400:
                    f["class"] = "CANDIDATE_EXPOSURE"
                    f["note"] = "long-lived JWT served in page"
            findings.append(f)
    # A value flagged as a candidate is not also "public by design".
    cand_fps = {f["sha256_16"] for f in findings
                if f["class"] == "CANDIDATE_EXPOSURE" and f["sha256_16"]}
    return [f for f in findings
            if not (f["class"] == "PUBLIC_BY_DESIGN"
                    and f["sha256_16"] in cand_fps)]
