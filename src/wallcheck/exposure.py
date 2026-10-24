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
    # AI-provider API keys: billed, account-scoped credentials. The
    # prefixed forms (sk-proj-/sk-svcacct-/sk-admin-, sk-ant-) are
    # unambiguous; the legacy OpenAI form is bare "sk-" + 48 chars,
    # and the 48-char floor is what keeps it from eating prose —
    # shorter sk- strings are not OpenAI keys.
    ("openai_api_key", "CANDIDATE_EXPOSURE",
     re.compile(r"\b(?P<v>sk-(?:proj|svcacct|admin)-[0-9A-Za-z_-]{20,}|sk-[0-9A-Za-z]{48,})")),
    ("anthropic_api_key", "CANDIDATE_EXPOSURE",
     re.compile(r"\b(?P<v>sk-ant-[0-9A-Za-z_-]{20,})")),
    # Source-hosting and package-registry tokens: each grants write
    # access to code or published packages, so a served copy is a
    # supply-chain exposure, not a client identifier.
    ("gitlab_pat", "CANDIDATE_EXPOSURE",
     re.compile(r"\b(?P<v>glpat-[0-9A-Za-z_-]{20,})")),
    ("npm_token", "CANDIDATE_EXPOSURE",
     re.compile(r"\b(?P<v>npm_[0-9A-Za-z]{36})\b")),
    ("pypi_token", "CANDIDATE_EXPOSURE",
     re.compile(r"\b(?P<v>pypi-[0-9A-Za-z_-]{50,})")),
    ("digitalocean_token", "CANDIDATE_EXPOSURE",
     re.compile(r"\b(?P<v>dop_v1_[0-9a-f]{64})\b")),
    # An AWS access key ID is the identifier half of a credential
    # pair (the secret half is what generic_secret_field catches as
    # aws_secret_access_key). Scanner-standard to flag on its own:
    # it names the account and is half of everything needed.
    ("aws_access_key_id", "CANDIDATE_EXPOSURE",
     re.compile(r"\b(?P<v>(?:AKIA|ASIA)[0-9A-Z]{16})\b")),
    # Webhook URLs that are themselves credentials: anyone holding
    # the URL can post into the channel / trigger the hook — there
    # is no separate secret to leak.
    ("slack_webhook_url", "CANDIDATE_EXPOSURE",
     re.compile(r"\b(?P<v>https://hooks\.slack\.com/services/T[0-9A-Z]{8,}/B[0-9A-Z]{8,}/[0-9A-Za-z]{24})")),
    ("discord_webhook_url", "CANDIDATE_EXPOSURE",
     re.compile(r"\b(?P<v>https://(?:canary\.|ptb\.)?discord(?:app)?\.com/api/webhooks/[0-9]{17,20}/[0-9A-Za-z_-]{60,})")),
    ("telegram_bot_token", "CANDIDATE_EXPOSURE",
     re.compile(r"\b(?P<v>[0-9]{8,10}:[0-9A-Za-z_-]{35})\b")),
    ("private_key_block", "CANDIDATE_EXPOSURE",
     re.compile(r"(?P<v>-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)")),
    ("db_url_with_password", "CANDIDATE_EXPOSURE",
     re.compile(r"(?P<v>(?:postgres(?:ql)?|mariadb|mysql|mongodb(?:\+srv)?|mssql|sqlserver|cassandra|redis|rediss|amqp|amqps)://[^\s\"'/:]+:[^\s\"'@]{4,}@)")),
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
    # Sentry DSNs are designed to ship in client code: the embedded
    # key is a public project identifier that can only submit events
    # to that one project — it is not an auth secret. Public, counted
    # for the census, never a disclosure.
    ("sentry_dsn", "PUBLIC_BY_DESIGN",
     re.compile(r"\b(?P<v>https://[0-9a-f]{32}@[0-9A-Za-z.-]*sentry\.io/[0-9]+)")),
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
