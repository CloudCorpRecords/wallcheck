"""Deterministic bot-wall classifier.

Pure function of (status, headers, body_sample, final_url, redirect_chain).
No network, no randomness, no LLM: same input, same verdict, forever.
That property is the product — it makes recorded fixtures a complete
test suite and makes Index scans comparable across time.
"""

from __future__ import annotations

import re

# Verdicts
OPEN = "OPEN"
CHALLENGED = "CHALLENGED"
WALLED = "WALLED"
LOGIN_GATED = "LOGIN_GATED"
RATE_LIMITED = "RATE_LIMITED"
UNREACHABLE = "UNREACHABLE"

LOGIN_PATH_MARKERS = ("/login", "/signin", "/sign-in", "/auth/login", "/account/login")
# Segment-level login markers (Wave 2): a path segment that is exactly
# "auth" (SSO endpoints like Indeed's /auth;jsessionid=...) or that
# contains a login word marks a login URL. Segment matching keeps
# /author, /authenticate, /authorship from matching.
LOGIN_SEGMENTS = ("login", "signin", "sign-in")
# Statuses where a generic human-check marker plausibly *is* the wall:
# wall-plausible error statuses plus small 2xx interstitials (the
# served-page gate already excludes full 2xx pages). A definitive
# 404/410 is an answer, not a challenge (Wave 2, W2-002).
GENERIC_OK_STATUSES = (401, 403, 429, 503)


def _norm_headers(headers):
    """Case-insensitive header lookup; accepts dict or list of (k, v) pairs."""
    out = {}
    if not headers:
        return out
    items = headers.items() if hasattr(headers, "items") else headers
    for k, v in items:
        out[str(k).lower()] = str(v)
    return out


CF_WALL_CODES = ("CF_MITIGATED_CHALLENGE", "CF_JUST_A_MOMENT",
                 "CF_CHALLENGE_PLATFORM", "CF_BLOCK_SORRY")
# A 2xx page larger than this is a full served page: wall *mentions* on it
# (an embedded captcha widget, a CSP allowlist entry, a dns-prefetch
# hint, a sensor cookie) are presence, not a wall that fired.
# Interstitials are small by construction, and walls served on error
# statuses are never "served pages". Wave 1 generalized this gate from
# generic markers to every body-derived wall marker (see
# validation/wave1/PROBLEMS.md, W1-001/W1-002).
GENERIC_GATE_BYTES = 16384

# Quoted strings (script srcs, JS loader URLs) that reference a
# third-party captcha *widget loader* — recaptcha.net,
# google.com/recaptcha, js.hcaptcha.com. A served page embedding
# the widget for its own forms is presence, not a challenge (the
# Wave 1 GitHub species; Wave 5, W5-001 found it under the size
# gate on an 11 KB homepage). The generic marker scan runs on the
# body with these loader references blanked; the word in prose is
# untouched and still verdict-drives. NOTE (Wave 6): the blanking
# is deliberately NARROW — quoted captcha *references* elsewhere
# (a form action like /errors_page/validateCaptcha, a refresh
# target like /px/captcha/) are load-bearing challenge signals on
# pages with no other served content (Amazon's interstitial proves
# it); blanking all quoted "captcha" spans falsely OPENs them.
_CAPTCHA_LOADER_RE = re.compile(r"[\"'][^\"']*(?:recaptcha|hcaptcha)[^\"']*[\"']")
# NOTE (Wave 7, W7-001, corrected): a Turnstile-loader blanking
# was tried here and REVERTED. The careerjet capture that
# motivated it looked like a homepage from its <head> but its
# visible text is only a verification interstitial ("Verification
# required ... not a robot") — the classifier was right and the
# hand-classification was wrong. A Turnstile loader on a
# check-only page IS the challenge mechanism, not presence; the
# loader principle applies to served pages, where the size gate
# already suppresses it. Do not re-add loader blanking for
# CF_CHALLENGE_PLATFORM without a served-page capture proving
# the false positive. (Unobserved hypothetical, not a defect: a
# small login page carrying Turnstile for its own form would read
# CHALLENGED via this code path — the generic branch yields to
# login pages per W6-002 but this vendor branch does not. If a
# live capture ever shows that shape, fix it then, generalized.)

# JS-proof interstitial phrasing (Wave 6, W6-S3a): the vendor-neutral
# species behind the AWS WAF (W3-001) and Azure WAF (W5-002) stubs —
# a page whose only content is a browser-verification proof the agent
# cannot perform, with the vendor tokens filed off. Matched only on
# non-served pages (the markers_count gate); the phrases are
# interstitial-voice, distinct from a real page *about* walls (gated
# by size) and from an SPA capability note (W6-S3c pins the boundary:
# "enable JavaScript to run this app" is not here).
_JS_PROOF_PHRASES = (
    "verifying your browser",
    "verifying you are human",
    "checking your browser",
    # Wave 13, W13-E4b: "Please wait while we check your browser"
    # is the same species in base form — a page whose only content
    # is a browser-verification proof. Gated to small pages like
    # every phrase here, so articles about browser checks stay OPEN.
    "check your browser",
    # Wave 12, W12-D3a: "Browser check in progress" is the same
    # species in new wording — a browser-verification proof, not a
    # capability note. Gated to small pages like every phrase here,
    # so articles *about* browser checks stay OPEN (D3b pin).
    "browser check",
    "checking if the site connection is secure",
    "performing security verification",
    "please enable javascript to continue",
    "enable javascript and cookies to continue",
    # Wave 11, W11-C1c: request-directed verification wording — the
    # page's only content is a proof of the agent's own request.
    # Interstitial-voice, like the rest of this list; "verification
    # in progress" is deliberately NOT here (it also describes
    # account-email verification flows, a different gate).
    "verify your request",
    "verifying your request",
)

# Geo-refusal phrasing (Wave 10, W10-B3b): a small page whose entire
# content refuses service by region/country. Negated forms only —
# "now available in your region" (good news) must never match. Gated
# to stub-sized pages (see _detect_vendor): a product page noting one
# item is region-restricted is content, not a refusal page.
_GEO_REFUSAL_PHRASES = (
    "not available in your region",
    "not available in your country",
    "not available in your location",
    "is unavailable in your region",
    "is unavailable in your country",
    "service not available in your region",
    "service not available in your country",
)

# Redirect-target wall signals (Wave 10, W10-B4): a small page whose
# whole content is a redirect — meta refresh or JS location assignment
# — to a challenge, captcha, or login target is a wall/login by
# reference (the Wave 6 S2c principle, generalized from captcha-only
# refresh targets). A redirect to a content target is routing, not a
# wall. Targets are matched on the path only.
_REDIRECT_CHALLENGE_TOKENS = (
    "captcha", "challenge", "verify-human", "bot-check", "human-check",
)
_META_REFRESH_RE = re.compile(
    r"<meta[^>]+http-equiv=[\"']?refresh[\"']?[^>]*>", re.IGNORECASE)
_META_REFRESH_URL_RE = re.compile(
    r"url\s*=\s*[\"']?([^\"'\s>]+)", re.IGNORECASE)
# Form actions (Wave 11, W11-C1b): the redirect-target principle's
# third species. A form is interactive content, not a routing
# directive, so unlike meta refresh / JS location its targets only
# count on a SERVED (2xx) small page — a 403 page carrying a login
# form is a refusal (the Wave 8 B2b rule), not a gate by reference.
_FORM_ACTION_RE = re.compile(
    r"<form[^>]+action\s*=\s*[\"']([^\"']+)[\"']", re.IGNORECASE)
_JS_LOCATION_RE = re.compile(
    r"(?:window\.)?location(?:\.href)?\s*=\s*[\"']([^\"']+)[\"']",
    re.IGNORECASE)

# Localized human-check phrasing (Wave 6, W6-S6): challenge pages are
# not English-only. Each phrase is an interactive human-verification
# demand in the page's own language; matched on the lowered body like
# the English markers. Kept tight to interstitial wording.
_LOCALIZED_HUMAN_CHECK = (
    # Spanish
    "verifica que eres humano",
    "demuestra que eres humano",
    "no soy un robot",
    # German
    "dass sie ein mensch sind",
    "ich bin kein roboter",
    "sicherheitsprüfung",
    # French
    "vérifiez que vous êtes humain",
    "je ne suis pas un robot",
    # Japanese
    "ロボットでないことを確認",
    "私はロボットではありません",
    # Portuguese
    "verifique se você é humano",
    "não sou um robô",
    # Italian (Wave 11, W11-C4b)
    "verifica di essere umano",
    "non sono un robot",
    # Dutch (Wave 11, W11-C4c)
    "bevestig dat u geen robot bent",
    "ik ben geen robot",
    # Korean (Wave 11, W11-C4d)
    "로봇이 아님을 확인",
    "나는 로봇이 아닙니다",
    # Polish (Wave 12, W12-D1a)
    "potwierdź, że nie jesteś robotem",
    "nie jestem robotem",
    # Turkish (Wave 12, W12-D1b)
    "robot olmadığınızı doğrulayın",
    "robot değilim",
    # Arabic (Wave 12, W12-D1c)
    "أكد أنك لست روبوتًا",
    "أنا لست روبوتًا",
    # Chinese (Wave 12, W12-D1d)
    "请确认您不是机器人",
    "我不是机器人",
    # Russian (Wave 12, W12-D1e)
    "подтвердите, что вы не робот",
    "я не робот",
)


def _served_full_page(status, body):
    return (status is not None and 200 <= status < 300
            and len(body or "") > GENERIC_GATE_BYTES)


_HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.S)


def _detect_vendor(h, body, evidence, status=None):
    """Append vendor evidence codes and return the vendor name (or None).

    Presence signals (CDN headers, sensor cookies) are always recorded.
    Body-derived wall markers are recorded only when the response is not
    a full served page (see _served_full_page): the same words on a big
    2xx page are an embedded widget or a policy list, not an
    interstitial. Header wall signals (cf-mitigated) stay authoritative
    at any size.
    """
    vendor = None
    # Wave 13, W13-E9: HTML comments are developer metadata, not
    # rendered content and not executed code — a vendor marker that
    # exists only inside a comment is neither a fired wall nor
    # attribution. Strip comments before every body scan below
    # (markers, redirect targets, generic phrases alike), so a
    # comment can never drive a verdict or a vendor.
    b = _HTML_COMMENT_RE.sub(" ", body or "")
    bl = b.lower()
    set_cookie = h.get("set-cookie", "")
    markers_count = not _served_full_page(status, b)

    # --- Cloudflare ---
    cf = False
    if "cf-ray" in h:
        evidence.append("CF_RAY_HEADER")
        cf = True
    if h.get("cf-mitigated", "").strip().lower() == "challenge":
        evidence.append("CF_MITIGATED_CHALLENGE")
        cf = True
    if h.get("server", "").strip().lower() == "cloudflare":
        evidence.append("SERVER_CLOUDFLARE")
        cf = True
    if markers_count and "just a moment" in bl:
        evidence.append("CF_JUST_A_MOMENT")
        cf = True
    if markers_count and "challenges.cloudflare.com" in b:
        evidence.append("CF_CHALLENGE_PLATFORM")
        cf = True
    if markers_count and "sorry, you have been blocked" in bl:
        evidence.append("CF_BLOCK_SORRY")
        cf = True
    if cf:
        vendor = "Cloudflare"

    # --- PerimeterX ---
    # The cookie is a sensor that rides along on served pages too:
    # presence-only. Only the captcha container / body marker on a
    # non-served-page response is a wall signal.
    px_wall = False
    if "_px" in set_cookie or "_pxhd" in set_cookie:
        evidence.append("PX_COOKIE")
    if markers_count and ("px-captcha" in b or "pxcaptcha" in bl):
        evidence.append("PX_CAPTCHA")
        px_wall = True
    if markers_count and "perimeterx" in bl:
        evidence.append("PX_BODY_MARKER")
        px_wall = True
    if px_wall and vendor is None:
        vendor = "PerimeterX"

    # --- DataDome ---
    dd = False
    if "x-datadome" in h:
        evidence.append("DD_XDATADOME_HEADER")
        dd = True
    if (markers_count and ("datadome" in bl or "captcha-delivery.com" in bl)
            or "dd_cookie" in set_cookie):
        evidence.append("DD_BODY_MARKER")
        dd = True
    if dd and vendor is None:
        vendor = "DataDome"

    # --- Akamai ---
    ak = False
    if "akamai" in h.get("server", "").lower():
        evidence.append("AKAMAI_SERVER_HEADER")
        ak = True
    if "ak_bmsc" in set_cookie:
        evidence.append("AKAMAI_BMSC_COOKIE")
        ak = True
    if "bm_so" in set_cookie or "bm_sv" in set_cookie:
        evidence.append("AKAMAI_BM_COOKIE")
        ak = True
    if markers_count and "bm-verify" in b:
        evidence.append("AKAMAI_BM_VERIFY")
        ak = True
    if markers_count and "edgesuite" in bl:
        # Akamai's classic error-page signature (Wave 3, W3-002):
        # the "Access Denied ... errors.edgesuite.net" page carries
        # no GHost header and no Bot Manager cookie, so the body
        # reference is the only attribution. Matched on the bare
        # token because the real page HTML-encodes the dots
        # (edgesuite&#46;net). Same treatment as DataDome's
        # captcha-delivery.com host (W1-008).
        evidence.append("AKAMAI_EDGESUITE")
        ak = True
    if markers_count and re.search(r"reference\s+#?\d+\.[0-9a-f]{4,}", bl):
        # Akamai's other deny-page signature (Wave 5, W5-005): the
        # "Access Denied ... Reference 0.<hex>.<digits>.<hex>" page
        # (delta.com serves it with status 444 and no edgesuite
        # URL). The dotted reference token is the attribution; no
        # other vendor's deny page carries one.
        evidence.append("AKAMAI_REFERENCE")
        ak = True
    if ak and vendor is None:
        vendor = "Akamai"

    # --- Imperva (Incapsula) ---
    imp = False
    if "incap_ses" in set_cookie or "visid_incap" in set_cookie:
        evidence.append("IMPERVA_COOKIE")
        imp = True
    if markers_count and "incapsula" in bl:
        evidence.append("IMPERVA_BODY_MARKER")
        imp = True
        if "incapsula incident" in bl:
            # The Incapsula block page carries an incident ID line;
            # it is served at any status (commonly 200), so the
            # verdict must not be pinned to 401/403 (Wave 6, W6-S5d).
            evidence.append("IMPERVA_BLOCK_PAGE")
    if imp and vendor is None:
        vendor = "Imperva"

    # --- AWS WAF (Bot Control) ---
    # The JS token challenge page embeds the AwsWafIntegration
    # object and/or loads its challenge script from *.awswaf.com
    # (Wave 3, W3-001). It is served small (famously with status
    # 202), so the served-page gate keeps real pages *about* AWS
    # WAF from tripping it.
    if markers_count and ("awswafintegration" in bl or "awswaf.com" in bl):
        evidence.append("AWS_WAF_MARKER")
        if vendor is None:
            vendor = "AWS WAF"

    # --- Microsoft Azure WAF ---
    # Azure WAF's JS/CAPTCHA challenge page (Wave 5, W5-002): the
    # `azwaf` token is its CSS namespace and its challenge-asset
    # path (/.azwaf/captcha/...); the page titles itself "Azure
    # WAF". Served small, like AWS WAF's stub, so the gate applies
    # the same way.
    if markers_count and ("azwaf" in bl or "azure waf" in bl):
        evidence.append("AZURE_WAF_MARKER")
        if vendor is None:
            vendor = "Microsoft Azure WAF"

    # --- Kasada ---
    # Kasada's bot-wall payload is its KPSDK stub script (Wave 5,
    # W5-003). The marker is recorded here; attribution precedence
    # over mere cookie presence is resolved in classify(), the way
    # the PerimeterX-over-CDN case is. A Kasada sensor on a full
    # served page is gated out by markers_count, like every other
    # body marker — presence, not a wall.
    if markers_count and ("kpsdk" in bl or "kasada" in bl):
        evidence.append("KASADA_MARKER")
        if vendor is None:
            vendor = "Kasada"

    # --- AWS CloudFront (generated block page) ---
    # CloudFront's own 403 page for a blocked request (Wave 5,
    # W5-004): "The request could not be satisfied" is also its
    # origin-error wording, so attribution requires the "Request
    # blocked" line as well. Attribution only — the bare-403 rule
    # already owns the verdict.
    if markers_count and ("request could not be satisfied" in bl
                          and "request blocked" in bl):
        evidence.append("AWS_CLOUDFRONT_BLOCK")
        if vendor is None:
            vendor = "AWS CloudFront"

    # --- Generic human-check markers (no vendor signature) ---
    if markers_count and vendor is None:
        bl_generic = _CAPTCHA_LOADER_RE.sub(" ", bl)
        if "captcha" in bl_generic:
            evidence.append("GENERIC_CAPTCHA")
    if (markers_count
            and ("verify you are human" in bl or "human verification" in bl
                 or "are you a robot" in bl or "not a robot" in bl
                 or any(p in bl for p in _LOCALIZED_HUMAN_CHECK))
            and vendor is None):
        evidence.append("GENERIC_HUMAN_CHECK")

    # --- Generic JS-proof interstitial (no vendor signature) ---
    # The vendor-neutral browser-verification stub (Wave 6, W6-S3a):
    # a small page whose only content is a JS proof the agent cannot
    # perform. Served-page gated like every body marker.
    if (markers_count and vendor is None
            and any(p in bl for p in _JS_PROOF_PHRASES)):
        evidence.append("JS_PROOF")

    # --- Geo-refusal stub (Wave 10, W10-B3b) ---
    # A refusal page is a stub by construction: bound to 4 KB so a
    # product or article page that merely mentions regional
    # availability stays content, not a wall. Verdict-only signal
    # (no vendor): a geo refusal is a refusal, not a bot-wall brand.
    if (markers_count and len(b) < 4096
            and any(p in bl for p in _GEO_REFUSAL_PHRASES)):
        evidence.append("GEO_REFUSAL")

    # --- Redirect-target signals (Wave 10, W10-B4) ---
    # Collect every redirect target the page itself declares (meta
    # refresh, JS location assignment). A target that IS a login path
    # names a login gate; a target carrying a challenge token names a
    # challenge. Content targets produce no evidence. Gated like every
    # body marker, so a served page that happens to refresh (a
    # session-timeout redirect on real content) is untouched.
    if markers_count:
        targets = []
        for tag in _META_REFRESH_RE.findall(b):
            m = _META_REFRESH_URL_RE.search(tag)
            if m:
                targets.append(m.group(1))
        targets += _JS_LOCATION_RE.findall(b)
        form_targets = []
        if status is not None and 200 <= status < 300:
            # Wave 11, W11-C1b: form actions count as redirect
            # targets only on served pages (see _FORM_ACTION_RE).
            form_targets += _FORM_ACTION_RE.findall(b)
        for t in targets:
            path = t.split("?", 1)[0].split("#", 1)[0].lower()
            if _is_login(t):
                evidence.append("REDIRECT_TO_LOGIN_PAGE")
            elif any(tok in path for tok in _REDIRECT_CHALLENGE_TOKENS):
                evidence.append("REDIRECT_TO_CHALLENGE")
        # Wave 12, W12-D5a: a form action to a challenge is its own
        # evidence code, not REDIRECT_TO_CHALLENGE — because on an
        # identified login page the form action is the sign-in
        # form's own submission endpoint (part of auth, Wave 6 S5c),
        # while a meta refresh / JS location to a challenge on any
        # page is a routing stub that must keep its precedence.
        # Splitting the code lets the verdict chain yield the
        # form-action species to the login heuristic without
        # weakening the redirect species (D5b guards the split).
        for t in form_targets:
            path = t.split("?", 1)[0].split("#", 1)[0].lower()
            if _is_login(t):
                evidence.append("REDIRECT_TO_LOGIN_PAGE")
            elif any(tok in path for tok in _REDIRECT_CHALLENGE_TOKENS):
                evidence.append("FORM_ACTION_TO_CHALLENGE")
        if ("REDIRECT_TO_CHALLENGE" in evidence
                or "FORM_ACTION_TO_CHALLENGE" in evidence) \
                and vendor is None:
            vendor = "Generic"

    if vendor is None and ("GENERIC_CAPTCHA" in evidence
                         or "GENERIC_HUMAN_CHECK" in evidence
                         or "JS_PROOF" in evidence):
        vendor = "Generic"

    # Wall-signal precedence (Wave 6, economist.com): when several
    # vendors are detected, the one whose wall actually fired outranks
    # one present only as CDN/sensor presence — the
    # PerimeterX-over-CDN principle, generalized. (economist.com
    # serves DataDome's captcha-delivery payload behind Cloudflare's
    # CDN: cf-ray + server headers are presence; the x-datadome
    # header + body marker are the wall that answered.) Detection
    # order below matches the blocks above: first wall-signal vendor
    # wins; with no wall signals, the first detected vendor stands
    # (bare-403-behind-CDN keeps Cloudflare, as before).
    _WALL_SIGNALS = (
        ("Cloudflare", ("CF_MITIGATED_CHALLENGE", "CF_JUST_A_MOMENT",
                        "CF_CHALLENGE_PLATFORM", "CF_BLOCK_SORRY")),
        ("PerimeterX", ("PX_CAPTCHA", "PX_BODY_MARKER")),
        ("DataDome", ("DD_XDATADOME_HEADER", "DD_BODY_MARKER")),
        ("Akamai", ("AKAMAI_BM_VERIFY", "AKAMAI_EDGESUITE",
                    "AKAMAI_REFERENCE")),
        ("Imperva", ("IMPERVA_BODY_MARKER",)),
        ("AWS WAF", ("AWS_WAF_MARKER",)),
        ("Microsoft Azure WAF", ("AZURE_WAF_MARKER",)),
        ("Kasada", ("KASADA_MARKER",)),
        ("AWS CloudFront", ("AWS_CLOUDFRONT_BLOCK",)),
        ("Generic", ("GENERIC_CAPTCHA", "GENERIC_HUMAN_CHECK",
                     "JS_PROOF", "FORM_ACTION_TO_CHALLENGE")),
    )
    detected = [v for v, codes in _WALL_SIGNALS
                if any(c in evidence for c in codes)
                or v == vendor]
    if vendor not in [v for v, _ in _WALL_SIGNALS]:
        detected.append(vendor)
    wall_first = [v for v, codes in _WALL_SIGNALS
                  if v in detected
                  and any(c in evidence for c in codes)]
    if wall_first:
        vendor = wall_first[0]
    elif detected:
        vendor = detected[0]

    return vendor


def _turnstile_loader_only(evidence, final_url):
    """True when the only Cloudflare signal on an identified login
    page is a challenge-platform loader reference (Wave 11, W11-C2c):
    a Turnstile widget on a sign-in form is the form's own check,
    not a wall that fired — the Wave 6 S5c principle in vendor
    form. Deliberately narrow: any fired-wall signal (cf-mitigated,
    Just a moment, block page) or any other vendor/generic wall
    signal keeps the challenge verdict (Wave 6 S5a, Wave 7
    careerjet: a loader on a check-only, non-login page IS the
    challenge). The caller checks _is_login separately; this
    helper only gates the signal set."""
    if not _is_login(final_url):
        return False
    if "CF_CHALLENGE_PLATFORM" not in evidence:
        return False
    fired_cf = [c for c in CF_WALL_CODES if c != "CF_CHALLENGE_PLATFORM"]
    if any(c in evidence for c in fired_cf):
        return False
    other_wall = ("PX_CAPTCHA", "PX_BODY_MARKER",
                  "DD_XDATADOME_HEADER", "DD_BODY_MARKER",
                  "AKAMAI_BM_VERIFY", "AKAMAI_EDGESUITE",
                  "AKAMAI_REFERENCE", "IMPERVA_BODY_MARKER",
                  "AWS_WAF_MARKER", "AZURE_WAF_MARKER", "KASADA_MARKER",
                  "AWS_CLOUDFRONT_BLOCK", "GENERIC_CAPTCHA",
                  "GENERIC_HUMAN_CHECK", "JS_PROOF", "GEO_REFUSAL")
    if any(c in evidence for c in other_wall):
        return False
    return True


def classify(status, headers=None, body="", final_url="", redirect_chain=None, error=None):
    """Classify a captured response. Returns the stable result object
    (without url/final_url/elapsed fields, which the caller adds)."""
    h = _norm_headers(headers)
    evidence = []
    chain = list(redirect_chain or [])
    b = body or ""

    if error is not None or status is None:
        if error:
            evidence.append("FETCH_ERROR: %s" % error)
        return {"status": status, "verdict": UNREACHABLE, "vendor": None,
                "evidence": evidence}

    vendor = _detect_vendor(h, b, evidence, status=status)
    loader_only_login = _turnstile_loader_only(evidence, final_url)

    # --- Strong wall/challenge signals first ---
    if "CF_BLOCK_SORRY" in evidence:
        verdict = WALLED
    elif (("CF_MITIGATED_CHALLENGE" in evidence or "CF_JUST_A_MOMENT" in evidence
           or "CF_CHALLENGE_PLATFORM" in evidence)
          and not loader_only_login):
        verdict = CHALLENGED
    elif "PX_CAPTCHA" in evidence:
        verdict = CHALLENGED
    elif "PX_BODY_MARKER" in evidence:
        # PerimeterX deny pages carry the marker without offering a captcha.
        # (PX_COOKIE alone is sensor presence on served pages too —
        # it is evidence, never a verdict.)
        verdict = WALLED if status in (401, 403) else CHALLENGED
    elif vendor == "DataDome" and status in (401, 403):
        verdict = CHALLENGED
    elif "AKAMAI_BM_VERIFY" in evidence and status in (401, 403):
        verdict = CHALLENGED
    elif "IMPERVA_BODY_MARKER" in evidence and (
            status in (401, 403) or "IMPERVA_BLOCK_PAGE" in evidence):
        # The Incapsula block page itself (Wave 2, W2-001): a deny page,
        # served even at login URLs — the wall fired before any login
        # form could be reached. The block page carries an incident-ID
        # line and is served at any status (commonly 200), so the
        # incident marker, not the status, owns the verdict (Wave 6,
        # W6-S5d). A bare "incapsula" mention on an error status keeps
        # the 401/403 pin.
        verdict = WALLED
    elif "JS_PROOF" in evidence:
        # The vendor-neutral browser-verification stub (Wave 6,
        # W6-S3a): a JS proof the agent cannot perform is a challenge,
        # whatever status the stub was served with — the same
        # reasoning as the AWS/Azure WAF stub rules.
        verdict = CHALLENGED
    elif "AWS_WAF_MARKER" in evidence:
        # AWS WAF's token challenge (Wave 3, W3-001): a JS proof the
        # agent cannot perform is a challenge, whatever status the
        # stub was served with (202 in the wild).
        verdict = CHALLENGED
    elif "AZURE_WAF_MARKER" in evidence:
        # Azure WAF's JS/CAPTCHA challenge page (Wave 5, W5-002):
        # same reasoning as AWS WAF — the page's only content is a
        # proof a non-JS agent cannot perform.
        verdict = CHALLENGED
    elif (status == 403 and "AKAMAI_SERVER_HEADER" in evidence
          and ("AKAMAI_BM_COOKIE" in evidence
               or "AKAMAI_BMSC_COOKIE" in evidence)):
        # Akamai Bot Manager deny shape (Wave 2, W2-001): GHost error
        # page + BM cookie on a 403. Both signals required and status
        # pinned to 403, so served pages and plain 401 auth responses
        # that merely carry BM cookies are untouched.
        verdict = WALLED
    elif "GEO_REFUSAL" in evidence:
        # Wave 10, W10-B3b: a stub page refusing service by region is
        # a refusal, not served content — the 200-status species of
        # the bare-403 geo refusal. No vendor is named: this is a
        # verdict signal, not a bot-wall brand.
        verdict = WALLED
    elif "REDIRECT_TO_CHALLENGE" in evidence:
        # Wave 10, W10-B4a/B4c: a page whose whole content routes the
        # client to a challenge is a challenge by reference (the Wave 6
        # S2c principle, generalized past captcha-only targets).
        verdict = CHALLENGED
    elif "FORM_ACTION_TO_CHALLENGE" in evidence \
            and not _is_login(final_url):
        # Wave 12, W12-D5a: a form action to a challenge on a page
        # that is NOT the login is a challenge by reference (Wave 11
        # W11-001). On an identified login page the branch is
        # skipped, so the page falls through to the login heuristic
        # below: the form is the sign-in form, and its action is the
        # form's own submission endpoint — part of the auth
        # experience (Wave 6 S5c), not a routing stub.
        verdict = CHALLENGED
    elif "REDIRECT_TO_LOGIN_PAGE" in evidence:
        # Wave 10, W10-B4b: a page whose whole content routes the
        # client to login is a login gate, not a wall.
        verdict = LOGIN_GATED
    elif (("GENERIC_CAPTCHA" in evidence or "GENERIC_HUMAN_CHECK" in evidence)
          and (status in GENERIC_OK_STATUSES
               or (status is not None and 200 <= status < 300))
          and not _is_login(final_url)):
        # The generic-marker branch yields to an identified login page
        # (Wave 6, W6-S5c): human-check prose on a sign-in form is part
        # of the auth experience, not a wall — the operative gate is
        # the login. Vendor wall codes keep their precedence above.
        verdict = CHALLENGED
    elif status == 429:
        evidence.append("STATUS_429")
        verdict = RATE_LIMITED
    elif status == 401:
        evidence.append("STATUS_401")
        verdict = LOGIN_GATED
    elif ((_is_login(final_url) or any(_is_login(u) for u in chain))
          and status is not None and 200 <= status < 400):
        # The login heuristic never pre-empts an error status (Wave 2,
        # W2-001; generalized Wave 8, W8-001): a gate must be a served
        # page (2xx/3xx), never a 4xx/5xx. The old exclusion set
        # (403/404/410) let 444 Akamai denies and 5xx failures at login
        # URLs read as LOGIN_GATED — delta's 444 deny was the catch.
        # Served login pages (2xx) and redirects landing on login URLs
        # still land here; 401 has its own branch above.
        evidence.append("REDIRECT_TO_LOGIN")
        verdict = LOGIN_GATED
    elif status == 403:
        evidence.append("STATUS_403")
        verdict = WALLED
    elif status == 444:
        # 444 (Wave 5, W5-005): the server closed the request
        # without serving content (nginx's no-response code, also
        # used by edge deny configurations). Nothing was served,
        # so OPEN is definitionally wrong; a deliberate drop is a
        # refusal.
        evidence.append("STATUS_444")
        verdict = WALLED
    elif status == 451:
        # 451 (Wave 10, W10-B3c): Unavailable For Legal Reasons
        # (RFC 7725) is a deliberate refusal, not a served page and
        # not a server failure — the 444 rule's sibling.
        evidence.append("STATUS_451")
        verdict = WALLED
    elif 200 <= status < 400:
        evidence.append("STATUS_%d" % status)
        verdict = OPEN
    elif status >= 500:
        evidence.append("STATUS_%d" % status)
        verdict = UNREACHABLE
    else:
        evidence.append("STATUS_%d" % status)
        verdict = WALLED if status in (401, 403) else OPEN

    # Vendor semantics: the wall vendor behind the verdict. Mere CDN
    # presence (cf-ray on a served page) is evidence, not a wall — an
    # OPEN page has no wall vendor. And when a PerimeterX challenge fires
    # behind a Cloudflare-fronted site (Fiverr's real setup), the wall is
    # PerimeterX unless Cloudflare's own wall signals fired too.
    if verdict == OPEN:
        vendor = None
    if verdict == LOGIN_GATED and vendor == "Generic":
        # Wave 11, W11-C6b: generic evidence on a login page was
        # judged to be auth copy, not a wall (the login yield) —
        # naming Generic as the wall vendor would contradict the
        # verdict, the Wave 10 W10-006 species. Named-vendor
        # presence (e.g. cf-ray on a served login page, the Wave 6
        # S5b pattern) is untouched: only the generic-only leak
        # is nulled.
        vendor = None
    if verdict == UNREACHABLE:
        # Wave 10, W10-B6c: an UNREACHABLE verdict claims no wall —
        # a 5xx error page wearing a vendor's branding (Cloudflare
        # 522) is an origin failure, not a wall, so no vendor is
        # named. This matches the fetch-error path, which already
        # returns vendor None.
        vendor = None
    elif (any(c in evidence for c in ("PX_CAPTCHA", "PX_BODY_MARKER"))
          and not any(c in evidence for c in CF_WALL_CODES)):
        vendor = "PerimeterX"
    elif ("KASADA_MARKER" in evidence and vendor == "Akamai"
          and "AKAMAI_EDGESUITE" not in evidence
          and "AKAMAI_BM_VERIFY" not in evidence):
        # Wave 5, W5-003: the response's own body is Kasada's wall
        # payload (its KPSDK stub) while Akamai is present only as
        # Bot Manager cookies — the wall that answered outranks the
        # sensor that rode along, the same principle as the
        # PerimeterX-over-CDN case above. A genuine Akamai deny
        # shape (edgesuite page, bm-verify) keeps Akamai.
        vendor = "Kasada"

    return {"status": status, "verdict": verdict, "vendor": vendor,
            "evidence": evidence}


def _is_login(url):
    if not url:
        return False
    path = url.split("?", 1)[0].split("#", 1)[0].lower()
    if any(m in path for m in LOGIN_PATH_MARKERS):
        return True
    for segment in path.split("/"):
        segment = segment.split(";", 1)[0]  # strip ;jsessionid=... params
        if segment == "auth" or any(m in segment for m in LOGIN_SEGMENTS):
            return True
    return False
