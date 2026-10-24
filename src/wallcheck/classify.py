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
    # Wave 20, W20-M2: localized JS-proof phrases — a browser-
    # verification stub is a challenge whatever language it is
    # written in, the localized human-check principle applied to
    # the JS_PROOF family (previously English-only). Each phrase
    # is a full interstitial sentence, gated to small pages like
    # every phrase here.
    "wir überprüfen ihren browser",
    "nous vérifions votre navigateur",
    "estamos verificando su navegador",
    "estamos verificando o seu navegador",
    "ブラウザを確認しています",
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

# Throttle wording for the Retry-After rule (Wave 14, W14-F4c):
# the server's statement of cause. Deliberately narrow: "too many
# requests" / rate-limit phrasing / "slow down" — NOT "temporarily
# unavailable" / "service unavailable", which is overload wording
# and stays UNREACHABLE on 5xx (F4e pin). A bare "too many" is
# excluded: "too many items" is not a throttle.
_THROTTLE_PHRASES = (
    "too many requests",
    "rate limit",
    "rate-limit",
    "ratelimit",
    "slow down",
    "request limit exceeded",
    # Wave 21, W21-N2a: traffic-overload cause wording joins the
    # cause list — a server stating overload ("high traffic") with
    # a Retry-After header and a retry instruction is stating a
    # throttle, not an origin failure. "Temporarily unavailable"
    # stays excluded (F4e): overload wording without a cause
    # phrase is still not a throttle cause.
    "high traffic",
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
# Iframe sources (Wave 20, W20-M1): the redirect-target principle's
# fourth species. An <iframe> src is an embedded routing directive:
# a page whose only content is a frame to a challenge/login target
# routes the client there, exactly like a meta refresh or a JS
# location. Content targets are routing, and the served-page gate
# (markers_count) protects real pages embedding frames.
_IFRAME_SRC_RE = re.compile(
    r"<iframe[^>]+src\s*=\s*[\"']([^\"']+)[\"']", re.IGNORECASE)

# Object data URLs and embed sources (Wave 21, W21-N1): the same
# routing species as iframe sources. An <object> data URL or an
# <embed> src is an embedded routing directive: a page whose only
# content is an object/embed to a challenge/login target routes the
# client there. Object fallback text is body text (not routing) and
# is handled by the visible-text scans, not here.
_OBJECT_DATA_RE = re.compile(
    r"<object[^>]+data\s*=\s*[\"']([^\"']+)[\"']", re.IGNORECASE)
_EMBED_SRC_RE = re.compile(
    r"<embed[^>]+src\s*=\s*[\"']([^\"']+)[\"']", re.IGNORECASE)

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
    # Swedish (Wave 17, W17-J7a)
    "bekräfta att du inte är en robot",
    "jag är inte en robot",
    # Finnish (Wave 17, W17-J7b)
    "vahvista, ettet ole robotti",
    "en ole robotti",
    # Danish (Wave 17, W17-J7c)
    "bekræft, at du ikke er en robot",
    # Norwegian (Wave 17, W17-J7d) — "jeg er ikke en robot" is
    # shared with Danish, so it is listed once below.
    "bekreft at du ikke er en robot",
    "jeg er ikke en robot",
    # Portuguese, Brazilian (Wave 18, W18-K7a) — the fuller "eu não
    # sou um robô" already matches the European-PT "não sou um robô"
    # by substring, so only the distinct "Confirme…" demand is new.
    "confirme que você não é um robô",
    # Indonesian (Wave 18, W18-K7c/d)
    "konfirmasi bahwa anda bukan robot",
    "saya bukan robot",
    # Vietnamese (Wave 18, W18-K7e/f)
    "xác nhận bạn không phải là robot",
    "tôi không phải là robot",
    # Thai (Wave 18, W18-K7g/h)
    "ยืนยันว่าคุณไม่ใช่หุ่นยนต์",
    "ฉันไม่ใช่หุ่นยนต์",
    # Hebrew (Wave 19, W19-L7a/e)
    "אמת שאינך רובוט",
    "אני לא רובוט",
    # Persian (Wave 19, W19-L7b)
    "تأیید کنید که ربات نیستید",
    # Urdu (Wave 19, W19-L7c)
    "تصدیق کریں کہ آپ روبوٹ نہیں ہیں",
    # Bengali (Wave 19, W19-L7d)
    "আপনি রোবট নন তা নিশ্চিত করুন",
    # Ukrainian (Wave 20, W20-M3a)
    "підтвердіть, що ви не робот",
    # Hindi (Wave 20, W20-M3b)
    "कृपया पुष्टि करें कि आप रोबोट नहीं हैं",
    # Malay (Wave 20, W20-M3c)
    "sahkan bahawa anda bukan robot",
    # Tagalog (Wave 20, W20-M3d)
    "kumpirmahin na hindi ka robot",
    # Swahili (Wave 20, W20-M3e)
    "thibitisha kuwa wewe si roboti",
    # Tamil (Wave 21, W21-N7a)
    "நீங்கள் ரோபோ இல்லை என்பதை உறுதிப்படுத்தவும்",
    # Telugu (Wave 21, W21-N7b)
    "మీరు రోబో కాదని నిర్ధారించండి",
    # Marathi (Wave 21, W21-N7c)
    "तुम्ही रोबोट नाही याची पुष्टी करा",
    # Punjabi (Wave 21, W21-N7d)
    "ਤੁਸੀਂ ਰੋਬੋਟ ਨਹੀਂ ਹੋ ਇਸ ਦੀ ਪੁਸ਼ਟੀ ਕਰੋ",
    # Gujarati (Wave 22, W22-P7a)
    "તમે રોબોટ નથી તેની ખાતરી કરો",
    # Kannada (Wave 22, W22-P7b)
    "ನೀವು ರೋಬೋಟ್ ಅಲ್ಲ ಎಂದು ಖಚಿತಪಡಿಸಿ",
    # Nepali (Wave 22, W22-P7c)
    "तपाईं रोबोट होइन भनेर पुष्टि गर्नुहोस्",
    # Khmer (Wave 22, W22-P7d)
    "បញ្ជាក់ថាអ្នកមិនមែនជាមនុស្សយន្ត",
    # Greek (Wave 23, W23-Q7a)
    "επιβεβαιώστε ότι δεν είστε ρομπότ",
    # Czech (Wave 23, W23-Q7b)
    "potvrďte, že nejste robot",
    # Hungarian (Wave 23, W23-Q7c)
    "kérjük, erősítse meg, hogy ön nem robot",
    # Romanian (Wave 23, W23-Q7d)
    "confirmați că nu sunteți un robot",
    # Bulgarian (Wave 24, W24-R7a)
    "потвърдете, че не сте робот",
    "не съм робот",
    # Slovak (Wave 24, W24-R7b) — "nie ste" is not Czech
    # "nejste" (Wave 23, W23-Q7b); neither string contains
    # the other, so neither entry can fire for the other
    # language's pages.
    "potvrďte, že nie ste robot",
    "nie som robot",
    # Croatian (Wave 24, W24-R7c)
    "potvrdite da niste robot",
    "nisam robot",
    # Slovenian (Wave 24, W24-R7d)
    "potrdite, da niste robot",
    "nisem robot",
    # Serbian, Cyrillic (Wave 25, W25-T7a) — Croatian W24-R7c is
    # Latin script ("potvrdite da niste robot"); neither string
    # crosses scripts, so neither entry can fire for the other
    # language's pages.
    "потврдите да нисте робот",
    "нисам робот",
    # Macedonian (Wave 25, W25-T7b) — not Bulgarian W24-R7a:
    # "дека" for ", че", no ъ, and checkbox "сум" for "съм";
    # neither Macedonian string contains a Bulgarian one.
    "потврдете дека не сте робот",
    "не сум робот",
    # Latvian (Wave 25, W25-T7c)
    "apstipriniet, ka neesat robots",
    "es neesmu robots",
    # Lithuanian (Wave 25, W25-T7d)
    "patvirtinkite, kad nesate robotas",
    "aš nesu robotas",
    # Catalan (Wave 26, W26-U7a) — "no soc" is not Spanish
    # "no soy"; neither string contains a Spanish or Portuguese
    # entry, nor the reverse.
    "confirma que no ets un robot",
    "no soc un robot",
    # Estonian (Wave 26, W26-U7b) — "ma ei ole robot" is not
    # Finnish "en ole robotti" (ei != en, robot != robotti);
    # neither Estonian string contains a Finnish one.
    "kinnitage, et te ei ole robot",
    "ma ei ole robot",
    # Armenian (Wave 26, W26-U7c) — unique script, no collisions.
    "հաստատեք, որ ռոբոտ չեք",
    "ես ռոբոտ չեմ",
    # Georgian (Wave 26, W26-U7d) — unique script, no collisions.
    "დაადასტურეთ, რომ რობოტი არ ხართ",
    "მე რობოტი არ ვარ",
    # Albanian (Wave 27, W27-V7a) — "nuk jeni" is neither
    # Catalan "no ets" nor Spanish "no eres"; neither string
    # contains another entry.
    "konfirmoni që nuk jeni robot",
    "unë nuk jam një robot",
    # Icelandic (Wave 27, W27-V7b) — "vélmenni" and the ð/þ
    # letters; no Scandinavian entry contains either string
    # (the Nordic entries all say "robot").
    "staðfestu að þú sért ekki vélmenni",
    "ég er ekki vélmenni",
    # Kazakh (Wave 27, W27-V7c) — Cyrillic, but the "емес"
    # negation and Kazakh-specific letters keep both strings
    # clear of the Russian, Ukrainian, Bulgarian, Serbian, and
    # Macedonian entries; neither contains another entry.
    "робот емес екеніңізді растаңыз",
    "мен робот емеспін",
    # Malayalam (Wave 27, W27-V7d) — unique script, no
    # Tamil/Telugu collision (different scripts entirely).
    "നിങ്ങൾ ഒരു റോബോട്ട് അല്ലെന്ന് സ്ഥിരീകരിക്കുക",
    "ഞാൻ ഒരു റോബോട്ട് അല്ല",
    # Burmese (Wave 28, W28-W7a) — Myanmar script; no entry
    # anywhere in the list uses it, so neither string can
    # collide with another language's.
    "သင်သည် စက်ရုပ်မဟုတ်ကြောင်း အတည်ပြုပါ",
    "ကျွန်ုပ်သည် စက်ရုပ်မဟုတ်ပါ",
    # Sinhala (Wave 28, W28-W7b) — unique script, no
    # Tamil/Telugu/Malayalam collision (different scripts
    # entirely).
    "ඔබ රොබෝවෙක් නොවන බව තහවුරු කරන්න",
    "මම රොබෝවෙක් නොවේ",
    # Amharic (Wave 28, W28-W7c) — Ethiopic script; no entry
    # anywhere in the list uses it.
    "ሮቦት እንዳልሆኑ ያረጋግጡ",
    "እኔ ሮቦት አይደለሁም",
    # Azerbaijani (Wave 28, W28-W7d) — the demand verb
    # "təsdiqləyin" is not the Turkish entry's "doğrulayın";
    # neither string contains a Turkish one, nor the reverse.
    "robot olmadığınızı təsdiqləyin",
    "mən robot deyiləm",
)

# Body-presented wall phrases (Wave 17, W17-J2 refinement): the
# vendor-scan head/noscript strip applies only when the title or
# fallback note stands ALONE on served content. When the body
# itself already presents a wall phrase, a head/noscript marker is
# corroborating attribution (the real Cloudflare challenge page
# titles itself "Just a moment..." while its body performs the
# security verification) and must not be stripped. A bare "captcha"
# token counts here because vendor attribution, unlike the
# generic branches, names the wall behind a body-presented check.
_BODY_WALL_SIGNAL_PHRASES = (
    "verify you are human", "human verification",
    "are you a robot", "not a robot",
    "captcha", "unusual traffic", "suspicious activity",
) + tuple(_LOCALIZED_HUMAN_CHECK) + _JS_PROOF_PHRASES


def _served_full_page(status, body):
    return (status is not None and 200 <= status < 300
            and len(body or "") > GENERIC_GATE_BYTES)


_HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.S)
# JSON data blocks (Wave 15, W15-001; generalized Wave 16, W16-007):
# metadata about the page, not code the page runs and not a loader.
# Vendor names inside one are stripped from the vendor scan when the
# page has visible text (same visible-text condition as W14-001);
# content-free pages still fire. The strip covers every JSON script
# type (ld+json, plain application/json, text/json) — a data block is
# a data block whatever its MIME label. Regular <script> blocks are
# untouched — loader signals stay load-bearing.
_JSON_DATA_BLOCK_RE = re.compile(
    r"<script\b[^>]*type=[\"'](?:application/ld\+json|application/json|"
    r"text/json)[\"'][^>]*>.*?</script>",
    re.S | re.I)
# data-* attributes (Wave 16, W16-002): pure configuration, never
# rendered to any reader — unlike alt/title text (Wave 14, F2),
# which IS page text. A challenge/vendor token living only in a
# data-* attribute (name or value) is metadata about the page, not
# a presented challenge, when the page has visible text.
_DATA_ATTR_RE = re.compile(
    r"""\sdata-[a-z0-9-]+\s*=\s*("[^"]*"|'[^']*'|[^\s>]+)""", re.I)
# Placeholder attributes (Wave 25, W25-T8d): a placeholder is a
# hint shown as ghost text inside an EMPTY field — it is never
# presented content, exactly like a data-* attribute. A challenge
# phrase living only in a placeholder must not fire on a page
# with visible text; the survival variants strip it alongside
# data-* (the raw scan still fires on content-free pages, where
# the configuration IS the page).
_PLACEHOLDER_ATTR_RE = re.compile(
    r"""\splaceholder\s*=\s*("[^"]*"|'[^']*'|[^\s>]+)""", re.I)
# Invisible-captcha widget tags (Wave 15, W15-004): a widget with
# data-size="invisible" presents nothing to the reader — it gates
# form submission, not reading. Its "captcha" token is configuration,
# like script JSON (W14-001), when the page has visible text.
_INVISIBLE_WIDGET_TAG_RE = re.compile(
    r"<[^>]*\bdata-size\s*=\s*[\"']invisible[\"'][^>]*>", re.I)
# Footer-badge phrases (Wave 15, W15-007): "protected by X" /
# "powered by X" on a served (2xx) page is furniture, not a fired
# wall. Stripped from marker scans on 2xx only — error pages keep
# full attribution, so a deny page's badge still names its vendor.
# At most three words after "by" (vendor names run to three words);
# the strip never eats past the badge into following sentences.
_BADGE_RE = re.compile(
    r"(?:protected|powered) by [A-Za-z0-9][A-Za-z0-9\-]*"
    r"(?: [A-Za-z0-9][A-Za-z0-9\-]*){0,2}", re.I)
# HTTP Refresh-header target (Wave 15, W15-005): the header form of
# a meta refresh — same routing semantics, same target rules.
_REFRESH_URL_RE = re.compile(r"url\s*=\s*([^;,\s]+)", re.I)

# Script/style/head stripping for the visible-text test (Wave 14,
# W14-F1b): a challenge marker that exists ONLY inside a <script>
# block is configuration JSON (a form's captcha config, a loader
# string), not page content — unless the page has no visible text
# at all, in which case the blob IS the page (F1a/F1d). The test
# applies ONLY to the generic evidence branches below (captcha /
# human-check / JS-proof prose); vendor markers and redirect
# targets keep reading scripts, because loader scripts and JS
# location assignments are load-bearing signals (Wave 10 B4).
_SCRIPT_BLOCK_RE = re.compile(r"<script\b[^>]*>.*?</script>", re.S | re.I)
_STYLE_BLOCK_RE = re.compile(r"<style\b[^>]*>.*?</style>", re.S | re.I)
_HEAD_BLOCK_RE = re.compile(r"<head\b[^>]*>.*?</head>", re.S | re.I)
# Wave 22, W22-P1: SVG <title>/<desc> metadata. A <title> or <desc>
# inside an <svg> is accessibility metadata, not rendered body text
# — the same family as <head> metadata (Wave 17 J2, Wave 21 N8).
# The backreference keeps <title>...</title> and <desc>...</desc>
# distinct; <head> titles are already gone by the time this runs
# (head strip first), so what remains here is svg metadata or a
# stray body title — metadata either way, never body content.
_SVG_META_RE = re.compile(r"<(title|desc)\b[^>]*>.*?</\1>", re.S | re.I)
# Noscript blocks (Wave 17, W17-J1): a <noscript> fallback note is
# ancillary text for clients without JS — like a data attribute or
# a style block, it is not a presented challenge when the page
# also serves real body content. Stripped from the visible-text
# test and from the marker scans (conditioned on visible text,
# like every suppression in this family): a page whose ONLY text
# is a noscript block still fires on it (Wave 13, E2c).
_NOSCRIPT_BLOCK_RE = re.compile(r"<noscript\b[^>]*>.*?</noscript>",
                                re.S | re.I)
# Template blocks (Wave 19, W19-L1): a <template> element's contents
# are inert — parsed but never rendered until a script clones them
# into the document. Template text is configuration, not presented
# content (the script-JSON / data-attribute / style-block species,
# not the noscript species: noscript text IS rendered for clients
# without JS). Stripped from the visible-text test and from the
# marker scans, conditioned on visible text like every suppression
# in this family: a page whose ONLY text is a template block still
# fires on it (blob-is-the-page).
_TEMPLATE_BLOCK_RE = re.compile(r"<template\b[^>]*>.*?</template>",
                                re.S | re.I)
# Picture blocks (Wave 23, W23-Q1): a <picture> element renders
# only its <img>; stray text nodes inside it are not valid content
# and are never rendered by any browser. Picture text is therefore
# never-presented content, the template species — stripped from
# the visible-text test and from the marker scans, conditioned on
# visible text like every suppression in this family: a page whose
# ONLY text is a picture text node still fires on it. Deliberately
# NOT stripped from the alt-attribute scan: the picture's <img>
# renders, so its alt text IS presented (the Wave 19 L2 family).
_PICTURE_BLOCK_RE = re.compile(r"<picture\b[^>]*>.*?</picture>",
                               re.S | re.I)
# Overlay containers (Wave 17, W17-J8): a full-screen modal/overlay
# carrying a human check BLOCKS the content beneath it, so the
# size gate's "mentions on a served page are presence" rule must
# not apply to phrases inside one. The tag marker (class/id naming
# an overlay, modal, popup, lightbox, or dialog) is the first key;
# a challenge phrase in the following text is the second.
_OVERLAY_TAG_RE = re.compile(
    r"<[^>]*\b(?:class|id)\s*=\s*[\"'][^\"']*\b(?:overlay|modal|popup|"
    r"lightbox|dialog)\b[^\"']*[\"'][^>]*>", re.I)
# ARIA modal containers (Wave 28, W28-W8): a tag asserting
# modality in ARIA spelling — role="alertdialog", or
# aria-modal="true" — is the J8 overlay species with no class/id
# marker at all. role="alert" and a bare role="dialog" assert
# no modality and deliberately do not match.
_MODAL_ROLE_TAG_RE = re.compile(
    r"<[^>]*\b(?:role\s*=\s*[\"']alertdialog[\"']|"
    r"aria-modal\s*=\s*[\"']true[\"'])[^>]*>", re.I)
# Sticky banners (Wave 18, W18-K2): a banner is the J8 species at
# smaller scale — but ONLY when it signals stickiness. "Banner"
# alone does not imply blocking: in-flow banners (K2f) are layout,
# not overlays, and must not fire. So a banner tag counts only when
# the tag itself also carries fixed/sticky positioning (inline style
# or a sticky/fixed class marker) — the stickiness signal is the
# third key, alongside the banner marker and the phrase.
_BANNER_TAG_RE = re.compile(
    r"<[^>]*\b(?:class|id)\s*=\s*[\"'][^\"']*\b(?:banner|announcement)"
    r"\b[^\"']*[\"'][^>]*>", re.I)
_TAG_RE = re.compile(r"<[^>]+>")
# Visible text shorter than this is a spinner, a heading, or a
# loader note — not content a reader came for. The threshold is a
# judgment call, documented here so it can be challenged: a real
# paragraph clears it easily, "Loading..." does not.
_VISIBLE_TEXT_MIN = 20


def _visible_text(body):
    """Text a reader sees: head, script, style, noscript, and
    template blocks removed, tags stripped, whitespace collapsed.
    Noscript text is excluded (Wave 17, W17-J1): a fallback note is
    not body content, and a page whose only text is a noscript block
    must read as content-free so the fallback rules below still fire.
    Template text is excluded (Wave 19, W19-L1) for the same reason:
    inert markup is not body content either."""
    t = _HEAD_BLOCK_RE.sub(" ", body or "")
    t = _SVG_META_RE.sub(" ", t)
    t = _SCRIPT_BLOCK_RE.sub(" ", t)
    t = _STYLE_BLOCK_RE.sub(" ", t)
    t = _NOSCRIPT_BLOCK_RE.sub(" ", t)
    t = _TEMPLATE_BLOCK_RE.sub(" ", t)
    t = _PICTURE_BLOCK_RE.sub(" ", t)
    t = _TAG_RE.sub(" ", t)
    return re.sub(r"\s+", " ", t).strip()


# aria-label values (Wave 18, W18-K8d): an aria-label on an
# interactive element (a, area, button, input, select, textarea) IS
# the element's accessible name — presented text, like alt/title
# (Wave 14, F2). On a non-interactive element the label is ignored
# by assistive technology entirely: metadata, not presentation.
# Stripped (attribute only — the tag and its other attributes are
# kept, so overlay class markers survive) from every body scan when
# the page has visible text, exactly like data-* and style text.
_TAG_RE_FOR_ARIA = re.compile(r"<[a-z][a-z0-9]*\b[^>]*>", re.I)
_ARIA_ATTR_RE = re.compile(
    r"""\saria-label\s*=\s*("[^"]*"|'[^']*')""", re.I)
_INTERACTIVE_TAGS = ("a", "area", "button", "input", "select",
                     "textarea")


def _strip_noninteractive_aria_labels(body):
    """Remove aria-label attributes from non-interactive tags only.
    Interactive elements keep their accessible names (presented
    text); everything else loses a label nobody can hear."""

    def _fix(m):
        tag = m.group(0)
        name = re.match(r"<([a-z][a-z0-9]*)", tag, re.I).group(1).lower()
        if name in _INTERACTIVE_TAGS:
            return tag
        return _ARIA_ATTR_RE.sub(" ", tag)

    return _TAG_RE_FOR_ARIA.sub(_fix, body or "")


# CSS content: resolution (Wave 18, W18-K1c): a challenge sentence
# assembled from custom properties and presented via a ::before
# content: rule IS presented text — but only the content: slice of
# CSS rendering is claimed here. Custom-property values are
# substituted into content: declarations (bounded iterative
# resolution, string values only), and adjacent string tokens in a
# content: value concatenate with no added separator (CSS renders
# juxtaposed strings exactly so). Unconsumed properties are never
# reported (K1a/K1d): only what a content: rule presents counts.
_CUSTOM_PROP_RE = re.compile(
    r"""--([a-zA-Z0-9_-]+)\s*:\s*("[^"]*"|'[^']*')""", re.I)
_CONTENT_DECL_RE = re.compile(r"content\s*:\s*([^;}]+)", re.I)
_CSS_VAR_RE = re.compile(r"var\(\s*--([a-zA-Z0-9_-]+)\s*\)", re.I)


def _css_content_strings(body):
    """Resolved content: strings from a document's style blocks."""
    props = {}
    styles = [m.group(0) for m in _STYLE_BLOCK_RE.finditer(body or "")]
    for style in styles:
        for pm in _CUSTOM_PROP_RE.finditer(style):
            props[pm.group(1).lower()] = pm.group(2)
    out = []
    for style in styles:
        for cm in _CONTENT_DECL_RE.finditer(style):
            value = cm.group(1)
            for _ in range(5):
                new = _CSS_VAR_RE.sub(
                    lambda vm: props.get(vm.group(1).lower(), ""), value)
                if new == value:
                    break
                value = new
            parts = re.findall(r'"([^"]*)"', value)
            if parts:
                out.append("".join(parts))
    return out


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
    if status is not None and 200 <= status < 300:
        # Wave 15, W15-007: footer badges are furniture on served
        # pages, not fired walls — blank them before marker scans.
        b = _BADGE_RE.sub(" ", b)
    # Wave 18, W18-K8d: aria-labels on non-interactive elements are
    # metadata, not presentation — strip them before every body scan
    # below, conditioned on visible text like every suppression in
    # this family (interactive elements keep their accessible names,
    # and a page whose only text is such a label still fires on it —
    # the blob-is-the-page species). Visible text ignores attributes,
    # so the condition is identical before and after the strip.
    if len(_visible_text(b)) >= _VISIBLE_TEXT_MIN:
        b = _strip_noninteractive_aria_labels(b)
    bl = b.lower()
    set_cookie = h.get("set-cookie", "")
    markers_count = not _served_full_page(status, b)
    # Wave 15, W15-001: visible text for the metadata-suppression
    # rules below (computed here so the vendor blocks can use it;
    # the generic section reuses this value).
    has_visible = len(_visible_text(b)) >= _VISIBLE_TEXT_MIN
    # Vendor markers read this body: JSON data blocks, data-*
    # attributes, and <style> blocks are stripped from it when the
    # page has visible text (W15-001, W16-002, W16-003) — all three
    # are configuration/metadata, not presented content — while
    # regular scripts keep reading (loaders are load-bearing).
    # <head> and <noscript> blocks are stripped on the same
    # condition (W17-J1/J2) EXCEPT when the body itself already
    # presents a wall phrase: then the title/fallback marker is
    # corroborating attribution for a body-presented wall, not a
    # standalone signal, and stripping it would lose the vendor
    # (the Cloudflare challenge fixture: title "Just a moment..."
    # over a body performing security verification).
    # Content-free pages still fire: with no visible content, the
    # configuration IS the page.
    if has_visible:
        b_vendor = _JSON_DATA_BLOCK_RE.sub(" ", b)
        b_vendor = _DATA_ATTR_RE.sub(" ", b_vendor)
        b_vendor = _STYLE_BLOCK_RE.sub(" ", b_vendor)
        b_vendor = _TEMPLATE_BLOCK_RE.sub(" ", b_vendor)
        b_vendor = _PICTURE_BLOCK_RE.sub(" ", b_vendor)
        body_wall_signal = any(
            p in _visible_text(b).lower()
            for p in _BODY_WALL_SIGNAL_PHRASES)
        if not body_wall_signal:
            b_vendor = _HEAD_BLOCK_RE.sub(" ", b_vendor)
            b_vendor = _SVG_META_RE.sub(" ", b_vendor)
            b_vendor = _NOSCRIPT_BLOCK_RE.sub(" ", b_vendor)
    else:
        b_vendor = b
    bl_vendor = b_vendor.lower()

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
    if markers_count and "just a moment" in bl_vendor:
        evidence.append("CF_JUST_A_MOMENT")
        cf = True
    if markers_count and "challenges.cloudflare.com" in b_vendor:
        evidence.append("CF_CHALLENGE_PLATFORM")
        cf = True
    if markers_count and "sorry, you have been blocked" in bl_vendor:
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
    if markers_count and ("px-captcha" in b_vendor or "pxcaptcha" in bl_vendor):
        evidence.append("PX_CAPTCHA")
        px_wall = True
    if markers_count and "perimeterx" in bl_vendor:
        evidence.append("PX_BODY_MARKER")
        px_wall = True
    if px_wall and vendor is None:
        vendor = "PerimeterX"

    # --- DataDome ---
    dd = False
    if "x-datadome" in h:
        evidence.append("DD_XDATADOME_HEADER")
        dd = True
    if (markers_count and ("datadome" in bl_vendor or "captcha-delivery.com" in bl_vendor)
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
    if markers_count and "bm-verify" in b_vendor:
        evidence.append("AKAMAI_BM_VERIFY")
        ak = True
    if markers_count and "edgesuite" in bl_vendor:
        # Akamai's classic error-page signature (Wave 3, W3-002):
        # the "Access Denied ... errors.edgesuite.net" page carries
        # no GHost header and no Bot Manager cookie, so the body
        # reference is the only attribution. Matched on the bare
        # token because the real page HTML-encodes the dots
        # (edgesuite&#46;net). Same treatment as DataDome's
        # captcha-delivery.com host (W1-008).
        evidence.append("AKAMAI_EDGESUITE")
        ak = True
    if markers_count and re.search(r"reference\s+#?\d+\.[0-9a-f]{4,}", bl_vendor):
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
    if markers_count and "incapsula" in bl_vendor:
        evidence.append("IMPERVA_BODY_MARKER")
        imp = True
        if "incapsula incident" in bl_vendor:
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
    if markers_count and ("awswafintegration" in bl_vendor or "awswaf.com" in bl_vendor):
        evidence.append("AWS_WAF_MARKER")
        if vendor is None:
            vendor = "AWS WAF"

    # --- Microsoft Azure WAF ---
    # Azure WAF's JS/CAPTCHA challenge page (Wave 5, W5-002): the
    # `azwaf` token is its CSS namespace and its challenge-asset
    # path (/.azwaf/captcha/...); the page titles itself "Azure
    # WAF". Served small, like AWS WAF's stub, so the gate applies
    # the same way.
    if markers_count and ("azwaf" in bl_vendor or "azure waf" in bl_vendor):
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
    if markers_count and ("kpsdk" in bl_vendor or "kasada" in bl_vendor):
        evidence.append("KASADA_MARKER")
        if vendor is None:
            vendor = "Kasada"

    # --- AWS CloudFront (generated block page) ---
    # CloudFront's own 403 page for a blocked request (Wave 5,
    # W5-004): "The request could not be satisfied" is also its
    # origin-error wording, so attribution requires the "Request
    # blocked" line as well. Attribution only — the bare-403 rule
    # already owns the verdict.
    if markers_count and ("request could not be satisfied" in bl_vendor
                          and "request blocked" in bl_vendor):
        evidence.append("AWS_CLOUDFRONT_BLOCK")
        if vendor is None:
            vendor = "AWS CloudFront"

    # --- Generic human-check markers (no vendor signature) ---
    # Wave 14, W14-F1b: a marker that appears ONLY inside <script>
    # blocks is configuration, not content — but only when the page
    # HAS visible content for the blob to be configuration of. A
    # content-free page (spinner, empty body) with a script-only
    # marker is a challenge page whose only content is the blob.
    # Vendor markers and redirect targets are unaffected: they keep
    # reading scripts (see the note on _SCRIPT_BLOCK_RE).
    bl_noscript = _SCRIPT_BLOCK_RE.sub(" ", b).lower()
    # Wave 16, W16-002/W16-003: the "survives stripping" test below
    # also strips <style> blocks and data-* attributes — a phrase
    # living only in a stylesheet or a data attribute is
    # configuration, not presented content, exactly like a
    # script-only phrase (W14-001). Rendered text (body markup,
    # alt/title attributes) survives all three strips.
    bl_noscript_clean = _STYLE_BLOCK_RE.sub(" ", bl_noscript)
    bl_noscript_clean = _DATA_ATTR_RE.sub(" ", bl_noscript_clean)
    bl_noscript_clean = _PLACEHOLDER_ATTR_RE.sub(" ", bl_noscript_clean)
    # Wave 17, W17-J1/J2: the same survival test for <head> blocks
    # (a <title> phrase is document metadata, not page content)
    # and <noscript> blocks (a fallback note is not a presented
    # challenge) — but only when the page has visible text, so
    # title-only and noscript-only pages still fire (W13 E2/E3).
    if has_visible:
        bl_noscript_clean = _HEAD_BLOCK_RE.sub(" ", bl_noscript_clean)
        bl_noscript_clean = _SVG_META_RE.sub(" ", bl_noscript_clean)
        bl_noscript_clean = _NOSCRIPT_BLOCK_RE.sub(" ", bl_noscript_clean)
        bl_noscript_clean = _TEMPLATE_BLOCK_RE.sub(" ", bl_noscript_clean)
        bl_noscript_clean = _PICTURE_BLOCK_RE.sub(" ", bl_noscript_clean)
    # Wave 16, W16-001b: rendered text with tags removed entirely
    # (no space substitution) — inline elements add no space to
    # rendered text, so a word split WITHIN itself across spans
    # ("ver<span>ify</span>") reads whole only here. Third scan
    # variant alongside raw body and space-separated visible text.
    # Derived from the script/style/data-stripped body, so the
    # survival guards below still hold: script-only, style-only,
    # widget-tag, and data-attribute tokens never reach it (their
    # tags are removed, not their text kept).
    bl_noscript_clean_nospace = _TAG_RE.sub("", bl_noscript_clean)
    # has_visible was computed with the vendor blocks above; the
    # generic section reuses it (Wave 15: moved, not recomputed).
    # Visible text for the phrase scan (Wave 15, W15-003): rendered
    # text with tags stripped, so a human-check sentence split
    # across elements (SVG tspans) still reads as one sentence.
    vis_text = _visible_text(b).lower()
    # Wave 18, W18-K1c: CSS content: strings resolved from custom
    # properties are presented text — a ::before challenge sentence
    # assembled via var() is rendered whole to the reader. They join
    # the phrase scans below as a presented-text variant, checked
    # per string, never joined (joining separate content strings
    # could compose a phrase no single element presents — the J7g
    # guessing boundary). Conditioned on content-free pages, like
    # every suppression in this family: on a page with visible text
    # a content: string is decorative (the H3b pin — a note
    # element's ::before string on an article is not a challenge),
    # while on a content-free page it IS the page's text (H3a).
    css_strings = ([s.lower() for s in _css_content_strings(b)]
                   if not has_visible else [])
    # Wave 19, W19-L2: alt values in document order, joined with
    # spaces — the H1 concatenated-text principle in attribute form.
    # A phrase split across images' alts is presented whole to a
    # reader using fallback text, exactly as a word split across
    # spans is. Derived from the script-stripped body (script text
    # is configuration, never an attribute), with template and
    # noscript blocks stripped when the page has visible text (the
    # L1 family conditioning: inert/fallback markup is not
    # presented text). Checked as a phrase-scan variant, never
    # joined across languages by construction — fragments in
    # different languages compose no listed phrase (J7g).
    _ALT_ATTR_RE = re.compile(
        r"""\salt\s*=\s*("[^"]*"|'[^']*')""", re.I)
    _alt_src = bl_noscript
    if has_visible:
        _alt_src = _TEMPLATE_BLOCK_RE.sub(" ", _alt_src)
        _alt_src = _NOSCRIPT_BLOCK_RE.sub(" ", _alt_src)
    alt_joined = " ".join(
        m.group(1)[1:-1] for m in _ALT_ATTR_RE.finditer(_alt_src)).lower()
    _HUMAN_CHECK_PHRASES = ("verify you are human", "human verification",
                            "are you a robot", "not a robot") \
        + tuple(_LOCALIZED_HUMAN_CHECK)

    if markers_count and vendor is None:
        bl_generic = _CAPTCHA_LOADER_RE.sub(" ", bl)
        bl_generic_noscript = _CAPTCHA_LOADER_RE.sub(" ", bl_noscript)
        # Wave 15, W15-004: a "captcha" token appearing ONLY in an
        # invisible-widget tag is form-submission machinery, not a
        # presented challenge — it must also survive invisible-tag
        # stripping to fire when the page has visible text.
        bl_generic_nowidget = _INVISIBLE_WIDGET_TAG_RE.sub(
            " ", bl_generic)
        # Wave 16, W16-002/W16-003: same survival test for <style>
        # blocks and data-* attributes — a token living only there
        # is configuration, not a presented challenge.
        bl_generic_clean = _STYLE_BLOCK_RE.sub(" ", bl_generic)
        bl_generic_clean = _DATA_ATTR_RE.sub(" ", bl_generic_clean)
        bl_generic_clean = _PLACEHOLDER_ATTR_RE.sub(
            " ", bl_generic_clean)
        # Wave 17, W17-J1/J2: same survival test for <head> and
        # <noscript> blocks — a token living only in a title or a
        # fallback note is metadata, not a presented challenge,
        # when the page has visible text.
        if has_visible:
            bl_generic_noscript = _HEAD_BLOCK_RE.sub(
                " ", bl_generic_noscript)
            bl_generic_noscript = _SVG_META_RE.sub(
                " ", bl_generic_noscript)
            bl_generic_noscript = _NOSCRIPT_BLOCK_RE.sub(
                " ", bl_generic_noscript)
            bl_generic_noscript = _TEMPLATE_BLOCK_RE.sub(
                " ", bl_generic_noscript)
            bl_generic_noscript = _PICTURE_BLOCK_RE.sub(
                " ", bl_generic_noscript)
            bl_generic_nowidget = _HEAD_BLOCK_RE.sub(
                " ", bl_generic_nowidget)
            bl_generic_nowidget = _SVG_META_RE.sub(
                " ", bl_generic_nowidget)
            bl_generic_nowidget = _NOSCRIPT_BLOCK_RE.sub(
                " ", bl_generic_nowidget)
            bl_generic_nowidget = _TEMPLATE_BLOCK_RE.sub(
                " ", bl_generic_nowidget)
            bl_generic_nowidget = _PICTURE_BLOCK_RE.sub(
                " ", bl_generic_nowidget)
            bl_generic_clean = _HEAD_BLOCK_RE.sub(" ", bl_generic_clean)
            bl_generic_clean = _SVG_META_RE.sub(" ", bl_generic_clean)
            bl_generic_clean = _NOSCRIPT_BLOCK_RE.sub(
                " ", bl_generic_clean)
            bl_generic_clean = _TEMPLATE_BLOCK_RE.sub(
                " ", bl_generic_clean)
            bl_generic_clean = _PICTURE_BLOCK_RE.sub(
                " ", bl_generic_clean)
        if ("captcha" in bl_generic
                or "captcha" in bl_noscript_clean_nospace
                or any("captcha" in s for s in css_strings)) and (
                ("captcha" in bl_generic_noscript
                 and "captcha" in bl_generic_nowidget
                 and "captcha" in bl_generic_clean)
                or "captcha" in bl_noscript_clean_nospace
                or any("captcha" in s for s in css_strings)
                or not has_visible):
            evidence.append("GENERIC_CAPTCHA")
    if (markers_count
            and vendor is None
            and (any(p in bl for p in _HUMAN_CHECK_PHRASES)
                 or any(p in vis_text for p in _HUMAN_CHECK_PHRASES)
                 or any(p in bl_noscript_clean_nospace
                        for p in _HUMAN_CHECK_PHRASES)
                 or any(p in alt_joined for p in _HUMAN_CHECK_PHRASES)
                 or any(p in s for s in css_strings
                        for p in _HUMAN_CHECK_PHRASES))
            and (any(p in bl_noscript_clean for p in _HUMAN_CHECK_PHRASES)
                 or any(p in vis_text for p in _HUMAN_CHECK_PHRASES)
                 or any(p in bl_noscript_clean_nospace
                        for p in _HUMAN_CHECK_PHRASES)
                 or any(p in alt_joined for p in _HUMAN_CHECK_PHRASES)
                 or any(p in s for s in css_strings
                        for p in _HUMAN_CHECK_PHRASES)
                 or not has_visible)):
        evidence.append("GENERIC_HUMAN_CHECK")

    # --- Generic JS-proof interstitial (no vendor signature) ---
    # The vendor-neutral browser-verification stub (Wave 6, W6-S3a):
    # a small page whose only content is a JS proof the agent cannot
    # perform. Served-page gated like every body marker.
    if (markers_count and vendor is None
            and (any(p in bl for p in _JS_PROOF_PHRASES)
                 or any(p in vis_text for p in _JS_PROOF_PHRASES)
                 or any(p in bl_noscript_clean_nospace
                        for p in _JS_PROOF_PHRASES)
                 or any(p in s for s in css_strings
                        for p in _JS_PROOF_PHRASES))
            and (any(p in bl_noscript_clean for p in _JS_PROOF_PHRASES)
                 or any(p in vis_text for p in _JS_PROOF_PHRASES)
                 or any(p in bl_noscript_clean_nospace
                        for p in _JS_PROOF_PHRASES)
                 or any(p in s for s in css_strings
                        for p in _JS_PROOF_PHRASES)
                 or not has_visible)):
        evidence.append("JS_PROOF")

    # --- Traffic-anomaly challenge (Wave 14, W14-F3b) ---
    # "Unusual traffic" / "suspicious activity" wording ALONE is a
    # refusal statement (F3a/F3d: bare 403 stays WALLED). Paired
    # with a verification demand it is a presented challenge: the
    # server names the anomaly AND asks the agent to prove itself.
    # Gated like every generic marker (small pages only), and the
    # verification cue is a substring ("verif" covers verify /
    # verification) — documented so the boundary can be challenged.
    _TRAFFIC_WORDS = ("unusual traffic", "suspicious activity")
    _VERIF_CUES = ("verif", "captcha", "prove you", "confirm you")
    # Wave 16, W16-001: the anomaly phrase AND the verification cue
    # are also matched against rendered visible text (W15-003's
    # treatment, extended to this branch) — a sentence split across
    # elements is one sentence to the reader, and the raw-body scan
    # alone misses it. W16-001b adds the concatenated variant for
    # within-word splits ("ver<span>ify</span>"): inline elements
    # add no space to rendered text. The served-page gate above
    # still protects large articles.
    # Wave 17, W17-J2e: the raw-body side of this branch must not
    # read <head> or <noscript> text on a page with visible text —
    # a title's anomaly wording must not upgrade a body refusal
    # into a challenge. (vis_text and the nospace variant already
    # exclude both; only the raw side needs the strip.)
    bl_traffic = bl
    if has_visible:
        bl_traffic = _HEAD_BLOCK_RE.sub(" ", bl_traffic)
        bl_traffic = _SVG_META_RE.sub(" ", bl_traffic)
        bl_traffic = _NOSCRIPT_BLOCK_RE.sub(" ", bl_traffic)
        bl_traffic = _TEMPLATE_BLOCK_RE.sub(" ", bl_traffic)
        bl_traffic = _PICTURE_BLOCK_RE.sub(" ", bl_traffic)
    if (markers_count and vendor is None
            and (any(w in bl_traffic for w in _TRAFFIC_WORDS)
                 or any(w in vis_text for w in _TRAFFIC_WORDS)
                 or any(w in bl_noscript_clean_nospace
                        for w in _TRAFFIC_WORDS))
            and (any(c in bl_traffic for c in _VERIF_CUES)
                 or any(c in vis_text for c in _VERIF_CUES)
                 or any(c in bl_noscript_clean_nospace
                        for c in _VERIF_CUES))):
        evidence.append("TRAFFIC_CHECK")

    # --- Geo-refusal stub (Wave 10, W10-B3b) ---
    # A refusal page is a stub by construction: bound to 4 KB so a
    # product or article page that merely mentions regional
    # availability stays content, not a wall. Verdict-only signal
    # (no vendor): a geo refusal is a refusal, not a bot-wall brand.
    if (markers_count and len(b) < 4096
            and any(p in bl for p in _GEO_REFUSAL_PHRASES)):
        evidence.append("GEO_REFUSAL")

    # --- Refusal-phrase stub (Wave 15, W15-002) ---
    # Same stub logic as GEO_REFUSAL for the general refusal: a
    # small page whose content is "Access denied" is a refusal, not
    # served content — the 200-status species of the bare-403
    # refusal. Verdict-only (no vendor); the verdict branch below
    # sits after the 401 branch (a 401 keeps auth precedence) and
    # is guarded to sub-500 statuses (a 5xx keeps UNREACHABLE).
    _REFUSAL_PHRASES = ("access denied",)
    if (markers_count and len(b) < 4096
            and any(p in bl for p in _REFUSAL_PHRASES)):
        evidence.append("REFUSAL_PHRASE")

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
        # Wave 20, W20-M1: iframe sources join the redirect-target
        # species (see _IFRAME_SRC_RE) — an embedded frame to a
        # challenge/login target names the same gate by reference.
        targets += _IFRAME_SRC_RE.findall(b)
        # Wave 21, W21-N1: object data URLs and embed sources join
        # the same species (see _OBJECT_DATA_RE / _EMBED_SRC_RE) —
        # an embedded object to a challenge/login target routes the
        # client there exactly like a frame does. Object fallback
        # text is body text, not routing, and is not collected here.
        targets += _OBJECT_DATA_RE.findall(b)
        targets += _EMBED_SRC_RE.findall(b)
        # Wave 15, W15-005: the HTTP Refresh header declares the
        # same routing as a meta refresh — a challenge/login target
        # there names the same gate, a content target is routing.
        refresh = h.get("refresh", "")
        if refresh:
            m = _REFRESH_URL_RE.search(refresh)
            if m:
                targets.append(m.group(1))
        # Wave 16, W16-004: the HTTP Location header on a 3xx
        # response declares the same routing — a challenge/login
        # target there names the same gate. Only 3xx responses
        # carry a Location worth collecting (a Location on a 200
        # is not a redirect). This matters to offline classify
        # users, whose pipelines may not follow redirects; live
        # probes follow them and classify the landing page.
        if status is not None and 300 <= status < 400:
            loc = h.get("location", "")
            if loc:
                targets.append(loc)
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

    # --- Overlay challenge (Wave 17, W17-J8) ---
    # NOT gated by markers_count: a full-screen overlay carrying a
    # human check blocks the content beneath it, whatever the page
    # size — the size gate's "mentions on a served page are
    # presence" rule does not apply to a modal that must be passed.
    # Two keys: an overlay-marked container tag, plus a human-check
    # or JS-proof phrase in the following text (800 chars,
    # script/style stripped so loader text cannot fire it). A bare
    # "captcha" token is deliberately NOT enough here — widget
    # loaders ride in overlay markup too, and a loader is presence.
    for m in _OVERLAY_TAG_RE.finditer(b):
        window = b[m.end():m.end() + 800]
        window = _SCRIPT_BLOCK_RE.sub(" ", window)
        window = _STYLE_BLOCK_RE.sub(" ", window)
        window = _TEMPLATE_BLOCK_RE.sub(" ", window)
        window = _PICTURE_BLOCK_RE.sub(" ", window)
        wl = window.lower()
        if (any(p in wl for p in _HUMAN_CHECK_PHRASES)
                or any(p in wl for p in _JS_PROOF_PHRASES)):
            evidence.append("OVERLAY_CHALLENGE")
            break

    # --- Sticky-banner challenge (Wave 18, W18-K2) ---
    # Same verdict logic as the overlay rule, with the stickiness
    # third key: the banner tag must itself signal fixed/sticky
    # positioning (inline style or a sticky/fixed class marker).
    # In-flow banners are layout, not overlays, and must not fire.
    if "OVERLAY_CHALLENGE" not in evidence:
        for m in _BANNER_TAG_RE.finditer(b):
            tag_text = m.group(0).lower()
            if "fixed" not in tag_text and "sticky" not in tag_text:
                continue
            window = b[m.end():m.end() + 800]
            window = _SCRIPT_BLOCK_RE.sub(" ", window)
            window = _STYLE_BLOCK_RE.sub(" ", window)
            window = _TEMPLATE_BLOCK_RE.sub(" ", window)
            window = _PICTURE_BLOCK_RE.sub(" ", window)
            wl = window.lower()
            if (any(p in wl for p in _HUMAN_CHECK_PHRASES)
                    or any(p in wl for p in _JS_PROOF_PHRASES)):
                evidence.append("OVERLAY_CHALLENGE")
                break

    # --- Native <dialog> challenge (Wave 19, W19-L8) ---
    # The J8 overlay species with no class/id marker at all: a
    # <dialog open> renders as a modal over the page, so a challenge
    # inside it blocks the content beneath — same two keys (blocking
    # container + challenge phrase in the following 800 chars).
    # The open attribute is load-bearing: a <dialog> without open
    # renders nothing and blocks nothing. The attribute check is
    # strict (whitespace before "open", then whitespace, =, or tag
    # end) so data-open or open-ended names cannot fake it.
    if "OVERLAY_CHALLENGE" not in evidence:
        for m in re.finditer(r"<dialog\b[^>]*>", b, re.I):
            tag = m.group(0)
            if not re.search(r"\sopen(\s|=|/?>)", tag, re.I):
                continue
            window = b[m.end():m.end() + 800]
            window = _SCRIPT_BLOCK_RE.sub(" ", window)
            window = _STYLE_BLOCK_RE.sub(" ", window)
            window = _TEMPLATE_BLOCK_RE.sub(" ", window)
            window = _PICTURE_BLOCK_RE.sub(" ", window)
            wl = window.lower()
            if (any(p in wl for p in _HUMAN_CHECK_PHRASES)
                    or any(p in wl for p in _JS_PROOF_PHRASES)):
                evidence.append("OVERLAY_CHALLENGE")
                break

    # --- ARIA modal challenge (Wave 28, W28-W8) ---
    # The J8 species in ARIA spelling: a plain <div> carrying
    # role="alertdialog" (or aria-modal="true") asserts modality
    # in the markup itself — the content beneath it is blocked
    # until the dialog is answered — with no overlay class/id
    # and no <dialog> tag for the earlier blocks to key on.
    # Same two keys (modal container + a human-check or JS-proof
    # phrase in the following 800 chars, same strips). NOT
    # size-gated, like every overlay member: a modal that must
    # be passed blocks the page beneath it, whatever its size.
    # role="alert" (Wave 27's toast) and a bare role="dialog"
    # assert no modality and do not fire — the boundary is
    # deliberate (battery v20 W8f).
    if "OVERLAY_CHALLENGE" not in evidence:
        for m in _MODAL_ROLE_TAG_RE.finditer(b):
            window = b[m.end():m.end() + 800]
            window = _SCRIPT_BLOCK_RE.sub(" ", window)
            window = _STYLE_BLOCK_RE.sub(" ", window)
            window = _TEMPLATE_BLOCK_RE.sub(" ", window)
            window = _PICTURE_BLOCK_RE.sub(" ", window)
            wl = window.lower()
            if (any(p in wl for p in _HUMAN_CHECK_PHRASES)
                    or any(p in wl for p in _JS_PROOF_PHRASES)):
                evidence.append("OVERLAY_CHALLENGE")
                break

    if vendor is None and ("GENERIC_CAPTCHA" in evidence
                         or "GENERIC_HUMAN_CHECK" in evidence
                         or "JS_PROOF" in evidence
                         or "TRAFFIC_CHECK" in evidence
                         or "OVERLAY_CHALLENGE" in evidence):
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
                     "JS_PROOF", "TRAFFIC_CHECK", "OVERLAY_CHALLENGE",
                     "FORM_ACTION_TO_CHALLENGE")),
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
                  "GENERIC_HUMAN_CHECK", "JS_PROOF", "TRAFFIC_CHECK",
                  "GEO_REFUSAL")
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
    elif ("OVERLAY_CHALLENGE" in evidence
          and status is not None and 200 <= status < 300
          and not _is_login(final_url)):
        # Wave 17, W17-J8: a full-screen overlay carrying a human
        # check blocks the served content beneath it — the check is
        # presented, not mentioned, whatever the page size. The
        # login exclusion mirrors the generic branch: an overlay on
        # an identified login page is auth furniture, and the login
        # heuristic below owns it.
        verdict = CHALLENGED
    elif (("GENERIC_CAPTCHA" in evidence or "GENERIC_HUMAN_CHECK" in evidence
           or "TRAFFIC_CHECK" in evidence)
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
    elif ("REFUSAL_PHRASE" in evidence
          and status is not None and status < 500):
        # Wave 15, W15-002: a small page whose content is a refusal
        # ("Access denied") is a wall, not served content. Placed
        # after the 401 branch (auth keeps precedence) and guarded
        # to sub-500 statuses (a 5xx keeps UNREACHABLE); vendor
        # branches above keep precedence, so a refused page wearing
        # a vendor marker keeps its attribution.
        verdict = WALLED
    elif (_is_code_entry_form(b)
          and status is not None and 200 <= status < 400
          and not _served_full_page(status, b)):
        # Wave 15, W15-006: a served page whose only content is a
        # one-time-code entry form is an authentication barrier,
        # not served content — the gate is auth. Narrower than
        # general form-text detection (Wave 14, F5 limitation): it
        # requires BOTH a code input and auth wording, so a "sign
        # in" link or a discount-code form cannot fire it. Wall
        # branches above keep precedence; the login heuristic below
        # covers login URLs, this covers the rest. Wave 17,
        # W17-007: the served-page size gate applies here too —
        # the design says "only content", and a full served page
        # (rubygems.org at 36 KB, caught by the passkey sibling)
        # is not only a form. Large login pages at login URLs are
        # still caught by the heuristic below; a large non-login
        # page with an auth form reads OPEN, the documented
        # boundary.
        evidence.append("CODE_ENTRY_FORM")
        verdict = LOGIN_GATED
    elif (_is_passkey_prompt(b)
          and status is not None and 200 <= status < 400
          and not _served_full_page(status, b)):
        # Wave 16, W16-005: a served page whose content is a
        # passkey/WebAuthn prompt is an authentication barrier,
        # not served content — the gate is auth. Same placement
        # and precedence as CODE_ENTRY_FORM: wall branches above
        # keep precedence; the login heuristic below covers login
        # URLs, this covers the rest. Wave 17, W17-007: same
        # served-page gate as CODE_ENTRY_FORM (see above).
        evidence.append("PASSKEY_PROMPT")
        verdict = LOGIN_GATED
    elif (_is_magic_link_form(b)
          and status is not None and 200 <= status < 400
          and not _served_full_page(status, b)):
        # Wave 16, W16-008: a served page whose content is an
        # email-entry form delivering an authentication link is
        # an authentication barrier, not served content. Same
        # placement, precedence, and two-key discipline as the
        # code-entry and passkey rules. Wave 17, W17-007: same
        # served-page gate (see CODE_ENTRY_FORM above).
        evidence.append("MAGIC_LINK_FORM")
        verdict = LOGIN_GATED
    elif (_is_delivery_code_prompt(b)
          and status is not None and 200 <= status < 400
          and not _served_full_page(status, b)):
        # Wave 18, W18-K3: a served page whose only content is a
        # delivery-channel code prompt is an authentication barrier,
        # not served content. Same placement, precedence, and size
        # gate as the code-entry, passkey, and magic-link rules.
        evidence.append("DELIVERY_CODE_PROMPT")
        verdict = LOGIN_GATED
    elif (_is_email_continue_prompt(b)
          and status is not None and 200 <= status < 400
          and not _served_full_page(status, b)):
        # Wave 19, W19-L3: a served page whose only content is an
        # email-only Continue sign-in step is an authentication
        # barrier, not served content. Same placement, precedence,
        # visible-text discipline, and size gate as the code-entry,
        # passkey, magic-link, delivery-code, and QR siblings.
        evidence.append("EMAIL_CONTINUE_PROMPT")
        verdict = LOGIN_GATED
    elif (_is_authenticator_prompt(b)
          and status is not None and 200 <= status < 400
          and not _served_full_page(status, b)):
        # Wave 21, W21-N3: a served page whose only content is an
        # authenticator-app passcode prompt is an authentication
        # barrier, not served content. Same placement, precedence,
        # visible-text discipline, and size gate as the code-entry,
        # passkey, magic-link, delivery-code, email-Continue, and
        # QR siblings.
        evidence.append("AUTHENTICATOR_PROMPT")
        verdict = LOGIN_GATED
    elif (_is_sso_prompt(b)
          and status is not None and 200 <= status < 400
          and not _served_full_page(status, b)):
        # Wave 22, W22-P3: a served page whose only content is an
        # SSO-continue sign-in step is an authentication barrier,
        # not served content. Same placement, precedence,
        # visible-text discipline, and size gate as the
        # authenticator sibling.
        evidence.append("SSO_PROMPT")
        verdict = LOGIN_GATED
    elif (_is_push_approval_prompt(b)
          and status is not None and 200 <= status < 400
          and not _served_full_page(status, b)):
        # Wave 24, W24-R3: a served page whose only content is
        # a push-approval sign-in prompt (approve this sign-in
        # on your device) is an authentication barrier, not
        # served content. Same placement, precedence, visible-
        # text discipline, and size gate as the SSO sibling.
        evidence.append("PUSH_APPROVAL_PROMPT")
        verdict = LOGIN_GATED
    elif (_is_employee_id_prompt(b)
          and status is not None and 200 <= status < 400
          and not _served_full_page(status, b)):
        # Wave 25, W25-T3: a served page whose only content is
        # an employee-ID sign-in form (a workforce identifier
        # instead of an email address) is an authentication
        # barrier, not served content. Same placement,
        # precedence, visible-text discipline, and size gate
        # as the push-approval sibling.
        evidence.append("EMPLOYEE_ID_PROMPT")
        verdict = LOGIN_GATED
    elif (_is_badge_tap_prompt(b)
          and status is not None and 200 <= status < 400
          and not _served_full_page(status, b)):
        # Wave 26, W26-U3: a served page whose only content is a
        # badge-tap sign-in prompt (tap your workplace ID badge
        # on the reader) is an authentication barrier, not
        # served content. Same placement, precedence, visible-
        # text discipline, and size gate as the employee-ID
        # sibling.
        evidence.append("BADGE_TAP_PROMPT")
        verdict = LOGIN_GATED
    elif (_is_biometric_prompt(b)
          and status is not None and 200 <= status < 400
          and not _served_full_page(status, b)):
        # Wave 27, W27-V3: a served page whose only content is a
        # biometric sign-in prompt (use your fingerprint / face
        # to sign in) is an authentication barrier, not served
        # content. Same placement, precedence, visible-text
        # discipline, and size gate as the badge-tap sibling.
        evidence.append("BIOMETRIC_PROMPT")
        verdict = LOGIN_GATED
    elif (_is_windows_pin_prompt(b)
          and status is not None and 200 <= status < 400
          and not _served_full_page(status, b)):
        # Wave 28, W28-W3: a served page whose only content is a
        # Windows PIN / Windows Hello sign-in prompt is an
        # authentication barrier, not served content. Same
        # placement, precedence, visible-text discipline, and
        # size gate as the biometric sibling.
        evidence.append("WINDOWS_PIN_PROMPT")
        verdict = LOGIN_GATED
    elif (_is_qr_prompt(b)
          and status is not None and 200 <= status < 400
          and not _served_full_page(status, b)):
        # Wave 17, W17-J4: a served page whose content is a QR-code
        # sign-in prompt is an authentication barrier, not served
        # content. Same placement, precedence, key discipline, and
        # served-page size gate as the code-entry, passkey, and
        # magic-link rules — the gate is Wave 18, W18-007: the
        # Wave 17 branch lacked it, so a full served homepage
        # carrying any QR wording anywhere read as a prompt.
        evidence.append("QR_PROMPT")
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
    elif (status in (403, 503) and "retry-after" in h
          and any(p in _HTML_COMMENT_RE.sub(" ", b).lower()
                  for p in _THROTTLE_PHRASES)):
        # Wave 14, W14-F4c/F4d: a timed, explicitly retryable refusal
        # is a throttle, not a wall — but ONLY when the server states
        # both the expiry (Retry-After header) and the cause (throttle
        # wording). Either alone is not enough (F4e/F4f pins). Wall
        # branches above keep precedence: a fired wall with a
        # Retry-After header is still a wall, and a challenged 429
        # is still a challenge (the generic branch above fires
        # first). 429 needs no rule (already RATE_LIMITED); 401
        # keeps auth precedence above.
        evidence.append("RETRY_AFTER_THROTTLE")
        verdict = RATE_LIMITED
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
    elif status == 418:
        # 418 (Wave 23, W23-Q2): the RFC 2324 joke code, reserved
        # by RFC 9110 (§15.5.19) and used in the wild as a
        # deliberate refusal — including specifically to refuse
        # non-browser clients. A server answering 418 has
        # declined to serve the resource: not a served page, not
        # a challenge, not an origin failure — the 444/451
        # refusal family's third member. Before this branch, 418
        # fell through to the final else and read OPEN whenever
        # no wall signal had fired.
        evidence.append("STATUS_418")
        verdict = WALLED
    elif status == 402:
        # 402 (Wave 24, W24-R2): Payment Required is a deliberate
        # refusal to serve without payment — not served content,
        # not an interactive challenge, not an authentication
        # demand (no credentials are entered), and not an origin
        # failure. The 444/451/418 refusal family's fourth
        # member. Before this branch, 402 fell through to the
        # final else and read OPEN whenever no wall signal had
        # fired — the W23-Q2 fallthrough species, one code over.
        evidence.append("STATUS_402")
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


# One-time-code entry form (Wave 15, W15-006): input names that name
# a code, plus auth wording in the body. Both keys are required: a
# code input without auth wording could be a discount/promo code,
# and auth wording without a code input is just prose.
_CODE_INPUT_VALUE_RE = re.compile(
    r"(?:^|[^a-z0-9])(otp|2fa|auth[-_]?code|verification[-_]?code|"
    r"security[-_]?code|one[-_ ]?time[-_ ]?code)(?:$|[^a-z0-9])")
_CODE_INPUT_ATTR_RE = re.compile(
    r"""(?:name|id)\s*=\s*["']([^"']+)["']""", re.I)
_CODE_WORDS = ("verification code", "one-time code", "one time code",
               "authentication code", "security code", "6-digit")


def _is_code_entry_form(body):
    """True when the body carries a one-time-code entry form: an
    input named for a code (otp/2fa/auth-code/...) or exactly "code",
    plus auth wording. Comments are stripped first (a commented-out
    form is not a form). Wave 17, W17-007 note: unlike its passkey
    and magic-link siblings, this rule keeps its wording check on
    the raw body — the code INPUT is itself presented barrier
    machinery, not a mere mention, so a code input plus auth
    wording is a form even when the wording rides in script text;
    the served-page size gate on the branch (below) is what keeps
    large served pages from misfiring here."""
    bl = _HTML_COMMENT_RE.sub(" ", body or "").lower()
    values = _CODE_INPUT_ATTR_RE.findall(bl)
    has_code_input = any(v.strip() == "code" for v in values) or any(
        _CODE_INPUT_VALUE_RE.search(v) for v in values)
    if not has_code_input:
        return False
    return any(w in bl for w in _CODE_WORDS)


# Passkey/WebAuthn prompt (Wave 16, W16-005): the code-entry rule's
# sibling. Two keys, same discipline: passkey/WebAuthn wording PLUS
# a prompt marker (a button, form, or input element, or a
# credentials-API reference). Prose ABOUT passkeys has no prompt
# marker; a bare sign-in link has no button/form/input — both stay
# content, exactly like the F5 species.
_PASSKEY_WORDS = ("passkey", "webauthn")
_PASSKEY_PROMPT_MARKERS = ("<button", "<form", "<input", "credentials.")


def _is_passkey_prompt(body):
    """True when the body carries a passkey/WebAuthn prompt: the
    wording plus a prompt marker. Comments stripped first. Wave 17,
    W17-007: the wording must appear in RENDERED visible text —
    rubygems.org's served homepage misfired this rule because its
    import map mentions "webauthn" asset files while the page
    carries ordinary forms; an asset filename is configuration,
    not a prompt."""
    bl = _HTML_COMMENT_RE.sub(" ", body or "").lower()
    vis = _visible_text(_HTML_COMMENT_RE.sub(" ", body or "")).lower()
    if not any(w in vis for w in _PASSKEY_WORDS):
        return False
    return any(m in bl for m in _PASSKEY_PROMPT_MARKERS)


# Magic-link / email sign-in form (Wave 16, W16-008): the
# code-entry rule's second sibling. Two keys: an email input PLUS
# auth-link wording ("sign-in link", "magic link", "password
# reset"). A newsletter form has the input but not the wording; a
# bare "sign in" link has neither — both stay content.
_MAGIC_LINK_WORDS = ("sign-in link", "sign in link", "magic link",
                     "password reset")
_EMAIL_INPUT_RE = re.compile(
    r"""<input[^>]*\b(?:type\s*=\s*["']email["']|(?:name|id)\s*=\s*["']email["'])""",
    re.I)


# QR-code sign-in prompt (Wave 17, W17-J4): the code-entry rule's
# third sibling. Three keys: QR wording, an auth purpose ("sign
# in" / "log in" / "authenticate"), and a prompt marker (an image,
# canvas, or button presenting the code). Prose ABOUT QR sign-in
# has no marker; an app-download QR code has no auth purpose; a
# bare link has no marker — all three stay content.
_QR_WORDS = ("qr code", "qr-code", "qrcode")
_QR_AUTH_WORDS = ("sign in", "log in", "authenticate")
_QR_PROMPT_MARKERS = ("<img", "<canvas", "<button")


def _is_qr_prompt(body):
    """True when the body carries a QR-code sign-in prompt: the QR
    wording, an auth purpose, and a prompt marker. Comments stripped
    first. Wave 18, W18-007: the wording AND the auth purpose must
    appear in RENDERED visible text — the Wave 17 rule read them
    from the raw body, so it misfired on served homepages whose
    only QR signals were a script filename (remoteok.com's
    qrcode.js), a script identifier (td.com's Branch qrCode
    token), and stylesheet class names (venmo.com's
    .qr-code-image-container rules): configuration, not a prompt,
    exactly the rubygems.org failure mode W17-007 fixed for the
    passkey and magic-link siblings. The prompt marker stays a raw
    element check (an image, canvas, or button IS presented
    machinery)."""
    bl = _HTML_COMMENT_RE.sub(" ", body or "").lower()
    vis = _visible_text(_HTML_COMMENT_RE.sub(" ", body or "")).lower()
    if not any(w in vis for w in _QR_WORDS):
        return False
    if not any(w in vis for w in _QR_AUTH_WORDS):
        return False
    return any(m in bl for m in _QR_PROMPT_MARKERS)


# Delivery-channel code prompt (Wave 18, W18-K3): the code-entry
# rule's third sibling. Real SMS/email code prompts do not use G6's
# input names — they use a row of digit boxes (digit-1 … digit-6)
# and delivery wording ("the code we texted/emailed to you"). Two
# keys: a digit-box input PLUS delivery wording in rendered visible
# text (the W17-007 visible-text discipline: a script-only mention
# is not a prompt). A phone-number request form has no digit input
# and stays content; prose about codes has no input and stays
# content.
_DELIVERY_WORDS = ("sms", "texted", "text message", "sent to your phone",
                   "sent to your mobile", "emailed to you",
                   "sent to your email")
_DIGIT_INPUT_RE = re.compile(
    r"""<input[^>]*\b(?:name|id)\s*=\s*["'][^"']*digit[^"']*["']""", re.I)


def _is_delivery_code_prompt(body):
    """True when the body carries a delivery-channel code prompt: a
    digit-box input plus delivery wording in visible text. Comments
    stripped first."""
    bl = _HTML_COMMENT_RE.sub(" ", body or "").lower()
    if not _DIGIT_INPUT_RE.search(bl):
        return False
    vis = _visible_text(_HTML_COMMENT_RE.sub(" ", body or "")).lower()
    return any(w in vis for w in _DELIVERY_WORDS)


def _is_magic_link_form(body):
    """True when the body carries an email-entry form whose purpose
    is to deliver an authentication link. Comments stripped first.
    Wave 17, W17-007: the wording must appear in RENDERED visible
    text, like its code-entry and passkey siblings — an asset or
    script mention of a link word is not a link form."""
    bl = _HTML_COMMENT_RE.sub(" ", body or "").lower()
    if not _EMAIL_INPUT_RE.search(bl):
        return False
    vis = _visible_text(_HTML_COMMENT_RE.sub(" ", body or "")).lower()
    return any(w in vis for w in _MAGIC_LINK_WORDS)


# Authenticator-app passcode prompt (Wave 21, W21-N3): the
# code-entry rule's next sibling. A sign-in step asking for the
# code from an authenticator app is an authentication barrier, but
# no existing rule names it: code-entry needs a code-named input
# (otp/2fa/auth-code/...), delivery needs digit boxes plus a
# delivery channel (texted/emailed), email-Continue needs an email
# input plus a Continue button. An authenticator prompt uses a
# TOTP field and authenticator wording — neither existing key
# fires. Two keys, from birth: authenticator wording in rendered
# visible text PLUS a TOTP-style code input (name/id containing
# "totp" or "authenticator"). The visible-text discipline and
# served-page size gate apply from birth (the Waves 17–20 lesson:
# a script filename like authenticator.js or a stylesheet class
# like .authenticator-prompt is configuration, not a prompt).
_AUTHENTICATOR_WORDS = ("authenticator app", "authenticator")
_TOTP_INPUT_RE = re.compile(
    r"""<input[^>]*\b(?:name|id)\s*=\s*["'][^"']*(totp|authenticator)[^"']*["']""",
    re.I)


def _is_authenticator_prompt(body):
    """True when the body carries an authenticator-app passcode
    prompt: authenticator wording in visible text plus a TOTP-style
    code input. Comments stripped first."""
    bl = _HTML_COMMENT_RE.sub(" ", body or "")
    if not _TOTP_INPUT_RE.search(bl):
        return False
    vis = _visible_text(_HTML_COMMENT_RE.sub(" ", body or "")).lower()
    return any(w in vis for w in _AUTHENTICATOR_WORDS)


# SSO-continue prompt (Wave 22, W22-P3): the authenticator rule's
# next sibling. A sign-in step offering single sign-on is an
# authentication barrier, but no existing rule names it: code-entry
# needs a code-named input, delivery needs digit boxes plus a
# channel, email-Continue needs an email input plus a Continue
# button, authenticator needs TOTP wording plus a TOTP input. An
# SSO step uses SSO wording plus an SSO button or link that starts
# the flow. Two keys, from birth: SSO wording in rendered visible
# text PLUS an SSO button/link. The visible-text discipline and
# served-page size gate apply from birth (the Waves 17–21 lesson:
# a script filename like sso.js or a stylesheet class like
# .sso-button is configuration, not a prompt).
_SSO_WORDS = ("continue with sso", "sign in with sso",
              "log in with sso", "single sign-on")
_SSO_BUTTON_RE = re.compile(
    r"<(?:button|a)\b[^>]*>[^<]*sso[^<]*</(?:button|a)>",
    re.I | re.S)
_SSO_LINK_RE = re.compile(
    r"""<a\b[^>]*href\s*=\s*["'][^"']*sso[^"']*["'][^>]*>""", re.I)


def _is_sso_prompt(body):
    """True when the body carries an SSO-continue sign-in step:
    SSO wording in visible text plus an SSO button or link.
    Comments stripped first."""
    bl = _HTML_COMMENT_RE.sub(" ", body or "")
    if not (_SSO_BUTTON_RE.search(bl) or _SSO_LINK_RE.search(bl)):
        return False
    vis = _visible_text(_HTML_COMMENT_RE.sub(" ", body or "")).lower()
    return any(w in vis for w in _SSO_WORDS)


# Push-approval sign-in prompt (Wave 24, W24-R3): the SSO rule's
# next sibling. A sign-in step whose only content asks the user
# to approve the sign-in on another device (push approval) is an
# authentication barrier, but no existing rule names it: code-
# entry needs a code input, passkey needs WebAuthn wording,
# delivery needs digit boxes plus a channel, email-Continue
# needs an email input, authenticator needs a TOTP input, SSO
# needs SSO wording, QR needs a code image. A push step has
# none of those — only the approval demand and its machinery.
# Two keys, from birth: a full sign-in-approval phrase in
# rendered visible text (never the bare word "approve") PLUS a
# prompt marker (a <button> or <form> — the page's actionable
# machinery: resend, cancel, continue). The visible-text
# discipline and served-page size gate apply from birth (the
# Waves 17–23 lesson: an asset filename like push-approve.js or
# a stylesheet class like .push-approval-prompt is
# configuration, not a prompt). Accepted narrow boundary,
# ledgered at birth: a push waiting page carrying neither a
# button nor a form is prose to this rule and stays OPEN.
_PUSH_APPROVAL_WORDS = ("approve this sign-in",
                        "approve the sign-in",
                        "approve your sign-in",
                        "approve this sign in",
                        "approve the sign in",
                        "approve this login",
                        "approve the login",
                        "approve your login",
                        "approve this sign-in request",
                        "approve the sign-in request",
                        "approve this login request",
                        "approve the login request")
_PUSH_PROMPT_MARKERS = ("<button", "<form")

# Employee-ID sign-in prompt (Wave 25, W25-T3): the auth family's
# workforce sibling. Two keys, same discipline as push approval:
# employee-ID wording in RENDERED visible text (a workforce
# identifier — "employee id", "employee number", "staff id",
# "associate id") PLUS credential machinery (a password input or
# a form element). Prose ABOUT employee IDs has no machinery; a
# badge-help page stays content. Configuration carriers (asset
# filenames, script identifiers, stylesheet classes) are not
# rendered wording and cannot fire the first key.
_EMPLOYEE_ID_WORDS = ("employee id", "employee number", "staff id",
                      "associate id")
_PASSWORD_INPUT_RE = re.compile(
    r"<input[^>]*\btype\s*=\s*[\"']?password\b", re.I)
_EMPLOYEE_ID_MARKERS = ("<form",)


def _is_employee_id_prompt(body):
    """True when the body carries an employee-ID sign-in prompt:
    workforce-identifier wording in visible text plus credential
    machinery (a password input or a form). Comments stripped
    first."""
    bl = _HTML_COMMENT_RE.sub(" ", body or "").lower()
    vis = _visible_text(_HTML_COMMENT_RE.sub(" ", body or "")).lower()
    if not any(w in vis for w in _EMPLOYEE_ID_WORDS):
        return False
    return bool(_PASSWORD_INPUT_RE.search(bl)) or any(
        m in bl for m in _EMPLOYEE_ID_MARKERS)


def _is_push_approval_prompt(body):
    """True when the body carries a push-approval sign-in prompt:
    a sign-in-approval phrase in visible text plus a button or
    form marker. Comments stripped first."""
    bl = _HTML_COMMENT_RE.sub(" ", body or "").lower()
    vis = _visible_text(_HTML_COMMENT_RE.sub(" ", body or "")).lower()
    if not any(w in vis for w in _PUSH_APPROVAL_WORDS):
        return False
    return any(m in bl for m in _PUSH_PROMPT_MARKERS)


# Badge-tap sign-in prompt (Wave 26, W26-U3): the auth family's
# physical-credential sibling. A sign-in step whose only content
# instructs the user to tap (or hold) a workplace ID badge on a
# reader is an authentication barrier, but no existing rule names
# it: code-entry needs a code input, passkey needs WebAuthn
# wording, employee-ID needs a typed workforce identifier,
# push-approval needs a device approval demand. A badge step has
# none of those — only the tap demand and its machinery. Two
# keys, from birth: a full badge-tap phrase in rendered visible
# text (never the bare word "badge" — badge-help pages, badge
# product pages, and footer-badge furniture all say "badge")
# PLUS prompt machinery (a <button> or <form> — the page's
# actionable apparatus: retry, cancel, continue). The
# visible-text discipline and served-page size gate apply from
# birth (the Waves 17–25 lesson: an asset filename like
# badge-tap.js or a stylesheet class like .badge-tap-prompt is
# configuration, not a prompt). Accepted narrow boundary,
# ledgered at birth (the R3 species): badge wording in prose
# with no button or form — a building-access note — is prose to
# this rule and stays OPEN; the machinery key is load-bearing.
_BADGE_TAP_WORDS = ("tap your badge", "tap your id badge",
                    "tap your employee badge",
                    "tap your security badge", "hold your badge")
_BADGE_TAP_MARKERS = ("<button", "<form")


def _is_badge_tap_prompt(body):
    """True when the body carries a badge-tap sign-in prompt: a
    badge-tap phrase in visible text plus a button or form
    marker. Comments stripped first."""
    bl = _HTML_COMMENT_RE.sub(" ", body or "").lower()
    vis = _visible_text(_HTML_COMMENT_RE.sub(" ", body or "")).lower()
    if not any(w in vis for w in _BADGE_TAP_WORDS):
        return False
    return any(m in bl for m in _BADGE_TAP_MARKERS)


# Biometric sign-in prompt (Wave 27, W27-V3): the auth family's
# device-biometric sibling. A sign-in step whose only content
# instructs the user to authenticate with a fingerprint (or
# face) is an authentication barrier, but no existing rule names
# it: passkey needs WebAuthn vocabulary ("passkey"/"webauthn"),
# which consumer biometric prompts deliberately avoid, and the
# other siblings all need something typed or tapped on another
# device. Two keys, from birth (the family discipline): a full
# biometric demand in rendered visible text (never the bare
# word "fingerprint" — fingerprinting articles, privacy
# policies, and phone reviews all say "fingerprint") PLUS
# prompt machinery (a <button> or <form>). The visible-text
# discipline and served-page size gate apply from birth.
# Accepted narrow boundary, ledgered at birth (the R3/U3
# species): biometric wording in prose with no button or form —
# a help article about unlocking a phone — is prose to this
# rule and stays OPEN; the machinery key is load-bearing.
_BIOMETRIC_WORDS = ("use your fingerprint", "scan your fingerprint",
                    "fingerprint to sign in", "use your face",
                    "biometric authentication", "biometric sign-in")
_BIOMETRIC_MARKERS = ("<button", "<form")


def _is_biometric_prompt(body):
    """True when the body carries a biometric sign-in prompt: a
    biometric demand phrase in visible text plus a button or
    form marker. Comments stripped first."""
    bl = _HTML_COMMENT_RE.sub(" ", body or "").lower()
    vis = _visible_text(_HTML_COMMENT_RE.sub(" ", body or "")).lower()
    if not any(w in vis for w in _BIOMETRIC_WORDS):
        return False
    return any(m in bl for m in _BIOMETRIC_MARKERS)


# Windows PIN / Windows Hello sign-in prompts (Wave 28, W28-W3):
# the device-credential ceremony none of the siblings name — the
# page's only step is entering a Windows PIN or pressing a
# Windows Hello button, a credential bound to one physical
# device the agent does not hold. Two keys, from birth (the
# family discipline): a Windows demand in rendered visible text
# ("windows pin" or "windows hello" — never the bare word
# "windows", which every OS article and settings page says)
# PLUS prompt machinery (a <button> or <form>). The visible-text
# discipline and served-page size gate apply from birth.
# Accepted narrow boundary, ledgered at birth (the R3/U3/V3
# species): Windows sign-in wording in prose with no button or
# form — a help article about setting a PIN — is prose to this
# rule and stays OPEN; the machinery key is load-bearing.
_WINDOWS_PIN_WORDS = ("windows pin", "windows hello")
_WINDOWS_PIN_MARKERS = ("<button", "<form")


def _is_windows_pin_prompt(body):
    """True when the body carries a Windows PIN / Windows Hello
    sign-in prompt: a Windows credential demand in visible text
    plus a button or form marker. Comments stripped first."""
    bl = _HTML_COMMENT_RE.sub(" ", body or "").lower()
    vis = _visible_text(_HTML_COMMENT_RE.sub(" ", body or "")).lower()
    if not any(w in vis for w in _WINDOWS_PIN_WORDS):
        return False
    return any(m in bl for m in _WINDOWS_PIN_MARKERS)


# Email-only Continue step (Wave 19, W19-L3): the magic-link rule's
# next sibling. A modern sign-in flow's first step is an email
# input plus a Continue button, with the auth purpose in the page's
# sign-in context rather than in any delivery promise. Three keys,
# all required: an email input, a Continue button (a <button> whose
# text is Continue, or a submit input valued Continue), and
# auth-purpose wording ("sign in" / "log in" / "authenticate") in
# rendered visible text. Signup wording is deliberately NOT an auth
# purpose: a newsletter's "sign up" step with an email input and a
# Continue button must not fire, and the signup-form boundary is
# ledgered separately (L3g).
_CONTINUE_BUTTON_RE = re.compile(
    r"<button\b[^>]*>\s*continue\s*</button>", re.I)
_CONTINUE_INPUT_RE = re.compile(r"<input\b[^>]*>", re.I)


def _is_email_continue_prompt(body):
    """True when the body carries an email-only Continue sign-in
    step. Comments stripped first; auth purpose must appear in
    rendered visible text (the rubygems/QR lesson, applied from
    birth — a script identifier like continueSignIn is not a
    prompt)."""
    bl = _HTML_COMMENT_RE.sub(" ", body or "")
    if not _EMAIL_INPUT_RE.search(bl):
        return False
    has_button = _CONTINUE_BUTTON_RE.search(bl) is not None
    has_submit = False
    for tag in _CONTINUE_INPUT_RE.findall(bl):
        tl = tag.lower()
        if "submit" in tl and "continue" in tl:
            has_submit = True
            break
    if not has_button and not has_submit:
        return False
    vis = _visible_text(_HTML_COMMENT_RE.sub(" ", body or "")).lower()
    return any(w in vis for w in _QR_AUTH_WORDS)
