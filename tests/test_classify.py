"""Offline fixture tests for the deterministic classifier.

Every fixture is a recorded-style (status, headers, body) triple; the
classifier is a pure function, so these fully exercise it with no network.
Run: python3 -m unittest discover -s tests -v
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from wallcheck.classify import classify  # noqa: E402

CF_CHALLENGE_BODY = """<!DOCTYPE html><html><head><title>Just a moment...</title></head>
<body><div class="main-wrapper"><p>Performing security verification</p>
<script src="https://challenges.cloudflare.com/turnstile/v0/api.js"></script>
</div></body></html>"""

CF_BLOCK_BODY = """<!DOCTYPE html><html><head><title>Attention Required! | Cloudflare</title></head>
<body><h1>Sorry, you have been blocked</h1>
<p>You are unable to access example-walled.com</p></body></html>"""

PX_BODY = """<!DOCTYPE html><html><head><title>Access Denied</title></head>
<body><div id="px-captcha"></div>
<script src="https://client.perimeterx.net/abc/main.min.js"></script>
<p>PerimeterX protects this site.</p></body></html>"""

OPEN_BODY = "<!DOCTYPE html><html><head><title>Example Domain</title></head>" \
            "<body><h1>Example Domain</h1><p>Hello.</p></body></html>"


class TestClassify(unittest.TestCase):
    def test_cloudflare_challenge_page(self):
        r = classify(403, {"Server": "cloudflare", "CF-Ray": "8abc123-IAD",
                           "Cf-Mitigated": "challenge"}, CF_CHALLENGE_BODY)
        self.assertEqual(r["verdict"], "CHALLENGED")
        self.assertEqual(r["vendor"], "Cloudflare")
        for code in ("CF_RAY_HEADER", "CF_MITIGATED_CHALLENGE", "CF_JUST_A_MOMENT"):
            self.assertIn(code, r["evidence"])

    def test_cloudflare_block_page(self):
        r = classify(403, {"Server": "cloudflare", "CF-Ray": "8abc124-IAD"}, CF_BLOCK_BODY)
        self.assertEqual(r["verdict"], "WALLED")
        self.assertEqual(r["vendor"], "Cloudflare")
        self.assertIn("CF_BLOCK_SORRY", r["evidence"])

    def test_perimeterx(self):
        r = classify(403, {"Set-Cookie": "_pxhd=xyz; Path=/"}, PX_BODY)
        self.assertEqual(r["vendor"], "PerimeterX")
        self.assertEqual(r["verdict"], "CHALLENGED")
        self.assertIn("PX_CAPTCHA", r["evidence"])
        self.assertIn("PX_COOKIE", r["evidence"])

    def test_datadome_header_case(self):
        r = classify(403, {"X-DataDome": "protected"}, "<html><body>blocked</body></html>")
        self.assertEqual(r["vendor"], "DataDome")
        self.assertEqual(r["verdict"], "CHALLENGED")
        self.assertIn("DD_XDATADOME_HEADER", r["evidence"])

    def test_akamai_cookie_marker_still_open_on_200(self):
        # Presence markers are evidence, not a wall: an OPEN page has no
        # wall vendor.
        r = classify(200, {"Set-Cookie": "ak_bmsc=abc; Path=/"}, OPEN_BODY)
        self.assertIsNone(r["vendor"])
        self.assertEqual(r["verdict"], "OPEN")
        self.assertIn("AKAMAI_BMSC_COOKIE", r["evidence"])

    def test_large_200_page_mentioning_captcha_is_open(self):
        # Regression (found in live dogfood, github.com): a big content
        # page embedding a captcha form widget is not a challenge.
        big = "<html><body>" + ("real content " * 2000) + \
              "<script>var k='recaptcha-site-key';</script></body></html>"
        self.assertGreater(len(big), 16384)
        r = classify(200, {"Server": "github.com"}, big)
        self.assertEqual(r["verdict"], "OPEN")
        self.assertNotIn("GENERIC_CAPTCHA", r["evidence"])

    def test_perimeterx_challenge_behind_cloudflare_cdn(self):
        # Fiverr's real setup: Cloudflare fronts the site (cf-ray, server
        # headers) but the challenge that fires is PerimeterX's.
        r = classify(403, {"Server": "cloudflare", "CF-Ray": "8abc-IAD"}, PX_BODY)
        self.assertEqual(r["verdict"], "CHALLENGED")
        self.assertEqual(r["vendor"], "PerimeterX")
        self.assertIn("CF_RAY_HEADER", r["evidence"])
        self.assertIn("PX_CAPTCHA", r["evidence"])

    def test_plain_open(self):
        r = classify(200, {"Server": "nginx", "Content-Type": "text/html"}, OPEN_BODY)
        self.assertEqual(r["verdict"], "OPEN")
        self.assertIsNone(r["vendor"])
        self.assertIn("STATUS_200", r["evidence"])

    def test_rate_limited(self):
        r = classify(429, {"Retry-After": "60"}, "<html><body>Too Many Requests</body></html>")
        self.assertEqual(r["verdict"], "RATE_LIMITED")
        self.assertIn("STATUS_429", r["evidence"])

    def test_login_redirect(self):
        r = classify(200, {"Content-Type": "text/html"},
                     "<html><body>Sign in to continue</body></html>",
                     final_url="https://app.example.com/login?next=/dashboard",
                     redirect_chain=["https://app.example.com/login?next=/dashboard"])
        self.assertEqual(r["verdict"], "LOGIN_GATED")
        self.assertIn("REDIRECT_TO_LOGIN", r["evidence"])

    def test_401_is_login_gated(self):
        r = classify(401, {"WWW-Authenticate": "Bearer"}, "")
        self.assertEqual(r["verdict"], "LOGIN_GATED")

    def test_bare_403_is_walled(self):
        r = classify(403, {"Server": "Apache"}, "<html><body>Forbidden</body></html>")
        self.assertEqual(r["verdict"], "WALLED")
        self.assertIsNone(r["vendor"])

    def test_generic_captcha(self):
        r = classify(200, {}, "<html><body>Please complete the captcha "
                              "to verify you are human.</body></html>")
        self.assertEqual(r["verdict"], "CHALLENGED")
        self.assertEqual(r["vendor"], "Generic")

    def test_unreachable(self):
        r = classify(None, {}, "", error="URLError: <urlopen error [Errno -2] Name or service not known>")
        self.assertEqual(r["verdict"], "UNREACHABLE")
        self.assertIsNone(r["status"])
        self.assertTrue(any(e.startswith("FETCH_ERROR") for e in r["evidence"]))

    def test_server_error_is_unreachable(self):
        r = classify(503, {}, "<html><body>Service Unavailable</body></html>")
        self.assertEqual(r["verdict"], "UNREACHABLE")

    def test_determinism(self):
        args = (403, {"Server": "cloudflare", "CF-Ray": "x"}, CF_CHALLENGE_BODY)
        self.assertEqual(classify(*args), classify(*args))


class TestWave1Regressions(unittest.TestCase):
    """Fixtures from Wave 1 live captures (validation/wave1/PROBLEMS.md).
    Each is the generalized captured shape, not a per-site special case."""

    def test_large_200_cloudflare_prefetch_is_open(self):
        # W1-001 (techcrunch shape): a served homepage that merely
        # dns-prefetches challenges.cloudflare.com is not a challenge.
        body = ("<html><head><title>News</title>"
                "<link rel='dns-prefetch' href='//challenges.cloudflare.com' />"
                "</head><body>" + ("article text " * 2000) +
                "<p>Readers said just a moment ago...</p></body></html>")
        self.assertGreater(len(body), 16384)
        r = classify(200, {"Server": "cloudflare", "CF-Ray": "8abc-IAD"}, body)
        self.assertEqual(r["verdict"], "OPEN")
        self.assertIsNone(r["vendor"])
        self.assertNotIn("CF_CHALLENGE_PLATFORM", r["evidence"])
        self.assertNotIn("CF_JUST_A_MOMENT", r["evidence"])
        self.assertIn("CF_RAY_HEADER", r["evidence"])

    def test_large_200_px_csp_mention_is_open(self):
        # W1-002 (walmart shape): "perimeterx" inside a CSP allowlist on
        # a full served homepage is presence, not a wall.
        body = ("<html><head><title>Store</title><meta http-equiv="
                "\"Content-Security-Policy\" content=\"*.perimeterx.net "
                "*.px-cdn.net\"></head><body>" + ("product " * 2500) +
                "</body></html>")
        self.assertGreater(len(body), 16384)
        r = classify(200, {"Content-Type": "text/html"}, body)
        self.assertEqual(r["verdict"], "OPEN")
        self.assertNotIn("PX_BODY_MARKER", r["evidence"])

    def test_200_px_cookie_only_is_open(self):
        # W1-002 (target shape): an _pxhd sensor cookie on a served page
        # is presence-only, like ak_bmsc — never a verdict by itself.
        r = classify(200, {"Set-Cookie": "_pxhd=abc123; Path=/"},
                     "<html><body><h1>Store home</h1></body></html>")
        self.assertEqual(r["verdict"], "OPEN")
        self.assertIsNone(r["vendor"])
        self.assertIn("PX_COOKIE", r["evidence"])

    def test_small_200_px_captcha_is_challenged(self):
        # W1-002 pin: a real PerimeterX interstitial can arrive as a
        # small 200 page; the gate must not swallow it.
        r = classify(200, {}, PX_BODY)
        self.assertEqual(r["verdict"], "CHALLENGED")
        self.assertEqual(r["vendor"], "PerimeterX")

    def test_akamai_ghost_403_is_walled_akamai(self):
        # W1-003 (ebay shape): AkamaiGHost server header + Bot Manager
        # bm_so cookie on a 403 error page names the vendor.
        r = classify(403, {"Server": "AkamaiGHost",
                           "Set-Cookie": "bm_so=ABCDEF0123; Path=/"},
                     "<html><head><title>Error Page</title></head>"
                     "<body>There was a problem.</body></html>")
        self.assertEqual(r["verdict"], "WALLED")
        self.assertEqual(r["vendor"], "Akamai")
        self.assertIn("AKAMAI_SERVER_HEADER", r["evidence"])
        self.assertIn("AKAMAI_BM_COOKIE", r["evidence"])

    def test_imperva_403_is_walled_imperva(self):
        # W1-004 (guru shape): Incapsula block page + incap_ses cookie.
        body = ('<html><head><META NAME="ROBOTS" CONTENT="NOINDEX, '
                'NOFOLLOW"><script src="/_Incapsula_Resource?'
                'SWJIYLWA=719d34d3"></script></head><body>'
                '<iframe id="main-iframe" src="/_Incapsula_Resource?'
                'CWUDNSAI=23&incident_id=1322_1227176"></iframe>'
                '</body></html>')
        r = classify(403, {"Set-Cookie": "incap_ses_1322_1227176=xyz; Path=/"}, body)
        self.assertEqual(r["verdict"], "WALLED")
        self.assertEqual(r["vendor"], "Imperva")
        self.assertIn("IMPERVA_COOKIE", r["evidence"])
        self.assertIn("IMPERVA_BODY_MARKER", r["evidence"])

    def test_datadome_captcha_delivery_body_marker(self):
        # W1-008 (nytimes shape): DataDome's captcha host in the body
        # attributes the vendor even without the x-datadome header.
        body = ("<html><head><title>nytimes.com</title></head><body>"
                "<script>var dd={'host':'geo.captcha-delivery.com',"
                "'cookie':'abc'};</script></body></html>")
        r = classify(403, {"Content-Type": "text/html;charset=UTF-8"}, body)
        self.assertEqual(r["verdict"], "CHALLENGED")
        self.assertEqual(r["vendor"], "DataDome")
        self.assertIn("DD_BODY_MARKER", r["evidence"])


class TestWave2Regressions(unittest.TestCase):
    """Fixtures from Wave 2 depth-probing captures
    (validation/wave2/PROBLEMS.md). Generalized shapes, no per-site
    special cases."""

    def test_imperva_block_at_login_url_is_walled(self):
        # W2-001 (guru shape): the Incapsula deny page served at /login
        # itself — the wall fired before any login form. The login-URL
        # heuristic must not relabel a wall as a gate.
        body = ('<html><head><META NAME="ROBOTS" CONTENT="NOINDEX, '
                'NOFOLLOW"><script src="/_Incapsula_Resource?'
                'SWJIYLWA=719d34d3"></script></head><body>'
                '<iframe src="/_Incapsula_Resource?incident_id=9">'
                '</iframe></body></html>')
        r = classify(403, {"Set-Cookie": "incap_ses_9=xyz; Path=/"}, body,
                     final_url="https://www.guru.com/login")
        self.assertEqual(r["verdict"], "WALLED")
        self.assertEqual(r["vendor"], "Imperva")

    def test_akamai_deny_at_signin_url_is_walled(self):
        # W2-001 (ebay shape): AkamaiGHost "Error Page" + bm_so cookie
        # on a 403 at the sign-in host — a Bot Manager deny, not a
        # served login form.
        r = classify(403, {"Server": "AkamaiGHost",
                           "Set-Cookie": "bm_so=ABCDEF0123; Path=/"},
                     "<html><head><title>Error Page</title></head>"
                     "<body>There was a problem.</body></html>",
                     final_url="https://signin.ebay.com/signin/",
                     redirect_chain=["https://signin.ebay.com/signin/"])
        self.assertEqual(r["verdict"], "WALLED")
        self.assertEqual(r["vendor"], "Akamai")

    def test_404_at_login_url_is_open_not_gated(self):
        # W2-001 (monster shape): a real "Page Not Found" 404 served at
        # a login-marked URL, DataDome JS riding along as presence.
        # A definitive 404 is a served answer, not a gate.
        body = ("<html><head><title>Page Not Found</title></head><body>"
                "<script src='https://js.datadome.co/tags.js'></script>"
                "<h1>Page Not Found</h1></body></html>")
        r = classify(404, {"Content-Type": "text/html"}, body,
                     final_url="https://www.monster.com/profile/login")
        self.assertEqual(r["verdict"], "OPEN")
        self.assertIsNone(r["vendor"])
        self.assertIn("STATUS_404", r["evidence"])
        self.assertIn("DD_BODY_MARKER", r["evidence"])

    def test_404_with_captcha_word_is_open_not_challenged(self):
        # W2-002 (nytimes shape): a large 404 page whose scripts merely
        # mention "captcha" is not a challenge — 404 is definitive.
        body = ("<html><head><title>Not Found</title></head><body>"
                + ("page chrome " * 3000)
                + "<script>var cfg={'captchaSiteKey':'abc'};</script>"
                "</body></html>")
        self.assertGreater(len(body), 16384)
        r = classify(404, {"Content-Type": "text/html"}, body,
                     final_url="https://www.nytimes.com/llms.txt")
        self.assertEqual(r["verdict"], "OPEN")
        self.assertIsNone(r["vendor"])
        self.assertIn("STATUS_404", r["evidence"])

    def test_generic_captcha_on_403_still_challenged(self):
        # W2-002 pin: the status gate must not swallow real generic
        # challenges on wall-plausible statuses.
        r = classify(403, {}, "<html><body>Please complete the captcha "
                              "to verify you are human.</body></html>")
        self.assertEqual(r["verdict"], "CHALLENGED")
        self.assertEqual(r["vendor"], "Generic")

    def test_bare_403_at_login_url_is_walled(self):
        # W2-001 pin: a 403 at a login URL with zero wall evidence is
        # indistinguishable from any bare deny — SPEC's bare-403 rule
        # owns it. (Served 2xx login pages still classify LOGIN_GATED,
        # see test_login_redirect.)
        r = classify(403, {"Server": "Apache"},
                     "<html><body>Forbidden</body></html>",
                     final_url="https://app.example.com/login")
        self.assertEqual(r["verdict"], "WALLED")
        self.assertIsNone(r["vendor"])

    def test_444_at_login_url_is_walled_not_gated(self):
        # W8-001 (delta shape, Wave 8 path wave): a 444 Akamai deny
        # at a login URL must not read as a login gate. The login
        # heuristic fired because 444 was not in its exclusion set,
        # even though no redirect happened (empty chain) and the
        # body carries Akamai deny evidence. A gate must be a
        # served page, not an error status.
        r = classify(444, {"Server": "AkamaiGHost"},
                     "<html><body>Access Denied. Reference "
                     "#18.12345678abcdef</body></html>",
                     final_url="https://www.delta.com/login")
        self.assertEqual(r["verdict"], "WALLED")
        self.assertEqual(r["vendor"], "Akamai")

    def test_500_at_login_url_is_unreachable_not_gated(self):
        # W8-001 generalization: a 5xx at a login URL is a server
        # failure (SPEC: UNREACHABLE), not a gate — the old
        # exclusion set (403/404/410) let 5xx through to LOGIN_GATED
        # as well.
        r = classify(500, {"Server": "Apache"},
                     "<html><body>Internal Server Error</body></html>",
                     final_url="https://app.example.com/login")
        self.assertEqual(r["verdict"], "UNREACHABLE")

    def test_auth_segment_url_is_login(self):
        # W2-003 (indeed shape): the SSO auth endpoint with a
        # ;jsessionid path param is a login wall when served.
        r = classify(200, {"Content-Type": "text/html"},
                     "<html><head><title>Sign In</title></head>"
                     "<body>Sign in to continue</body></html>",
                     final_url="https://secure.indeed.com/auth;"
                               "jsessionid=node0abc.node0?hl=en_US",
                     redirect_chain=["https://secure.indeed.com/auth;"
                                     "jsessionid=node0abc.node0?hl=en_US"])
        self.assertEqual(r["verdict"], "LOGIN_GATED")
        self.assertIn("REDIRECT_TO_LOGIN", r["evidence"])

    def test_author_path_is_not_login(self):
        # W2-003 pin: segment matching must not match /author or
        # /authenticate.
        for u in ("https://blog.example.com/author/jane",
                  "https://api.example.com/authenticate/token"):
            r = classify(200, {"Content-Type": "text/html"},
                         "<html><body>Content</body></html>", final_url=u)
            self.assertEqual(r["verdict"], "OPEN", u)


AWS_WAF_BODY = """<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<title></title>
<script type="text/javascript">
AwsWafIntegration.saveReferrer();
AwsWafIntegration.getToken().then(() => { window.location.href = newHref; });
</script></head>
<body><noscript>
<h1>JavaScript is disabled</h1>
In order to continue, we need to verify that you're not a robot.
This requires JavaScript. Enable JavaScript and then reload the page.
</noscript></body></html>"""

EDGESUITE_BODY = """<HTML><HEAD>
<TITLE>Access Denied</TITLE>
</HEAD><BODY>
<H1>Access Denied</H1>

You don't have permission to access "http&#58;&#47;&#47;www&#46;example&#46;com&#47;" on this server.<P>
Reference&#32;#18&#46;92620317&#46;1792812173&#46;96605d52
<P>https&#58;&#47;&#47;errors&#46;edgesuite&#46;net&#47;18&#46;92620317&#46;1792812173&#46;96605d52</P>
</BODY>
</HTML>"""


class TestWave3Fixtures(unittest.TestCase):
    def test_aws_waf_challenge_on_202(self):
        # W3-001 (booking.com shape): AWS WAF's JS token challenge is
        # served as a small 202 page — AwsWafIntegration in the body,
        # a "not a robot" noscript note, zero content. A non-JS agent
        # stops here: CHALLENGED, and the vendor is AWS WAF.
        r = classify(202, {"Server": "nginx"}, AWS_WAF_BODY)
        self.assertEqual(r["verdict"], "CHALLENGED")
        self.assertEqual(r["vendor"], "AWS WAF")
        self.assertIn("AWS_WAF_MARKER", r["evidence"])

    def test_not_a_robot_generic_marker(self):
        # W3-001 (companion): the same human-check wording with no
        # vendor signature still challenges — "not a robot" joins the
        # generic marker family ("are you a robot" was already there).
        r = classify(202, {}, "<html><body><h1>JavaScript is disabled</h1>"
                              "In order to continue, we need to verify "
                              "that you're not a robot.</body></html>")
        self.assertEqual(r["verdict"], "CHALLENGED")
        self.assertEqual(r["vendor"], "Generic")
        self.assertIn("GENERIC_HUMAN_CHECK", r["evidence"])

    def test_large_200_mentioning_awswaf_is_open(self):
        # The served-page gate covers the new vendor too: a big real
        # page *about* AWS WAF is content, not a challenge.
        big = "<html><body>" + ("how aws waf integration works " * 1200) + \
              "</body></html>"
        self.assertGreater(len(big), 16384)
        r = classify(200, {"Server": "nginx"}, big)
        self.assertEqual(r["verdict"], "OPEN")
        self.assertIsNone(r["vendor"])

    def test_akamai_edgesuite_error_page(self):
        # W3-002 (w3schools shape): Akamai's classic error page has no
        # GHost server header and no Bot Manager cookie — the only
        # signature is errors.edgesuite.net in the body.
        r = classify(403, {"Content-Type": "text/html"}, EDGESUITE_BODY)
        self.assertEqual(r["verdict"], "WALLED")
        self.assertEqual(r["vendor"], "Akamai")
        self.assertIn("AKAMAI_EDGESUITE", r["evidence"])


DUOLINGO_SHAPE_BODY = """<!doctype html><html dir="ltr"><head><meta charset="utf-8">
<title>Duolingo - Learn a language for free</title></head>
<body><div id="root"><nav>Learn Spanish, French, German and more</nav>
<main><h1>Learn a new language with the world's most-downloaded
education app</h1><p>Get started — create a free account, or log in
to continue your streak.</p></main></div>
<script>var e=document.createElement("script");
e.src="https://www.recaptcha.net/recaptcha/enterprise.js?render=6LcLOdsjAAAAAFfwGusLLnnn";
document.head.appendChild(e);</script>
</body></html>"""

AZURE_WAF_BODY = """<!DOCTYPE html><html><head><meta charset="utf-8"/>
<meta name="description" content="Azure WAF"/><title>Azure WAF</title>
<style>:root{--azwaf-brand-color-primary:#0f6cbd;
--azwaf-background-color-primary:#f4f3f5}</style></head>
<body><div id="azwaf-container">Azure WAF
<p>Please enable JavaScript to run this application.</p>
<span>20261024T043047Z-15d69cf9fcdh5zj5hC1FTY6hu800000009e0000000000b9r</span>
</div><script>
var cfg={"capiScriptUrl":"/.azwaf/captcha/proxied/v2/8A1EAD4C-ABA1-4A1D-87DD-87521C761AF4/api.js"};
</script><img id="index-gif-tracking-pixel"
src="/.azwaf/captcha/telemetry/tp/index.gif?azureRef=20261024T043047Z"/>
</body></html>"""

KASADA_429_BODY = """<!DOCTYPE html><html><head></head><body>
<script>window.KPSDK={};KPSDK.now=typeof performance!=='undefined'?
performance.now.bind(performance):Date.now.bind(Date);KPSDK.start=KPSDK.now();</script>
<script src="/ips.js?timestamp=1"></script>
</body></html>"""

CLOUDFRONT_BLOCK_BODY = """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
"http://www.w3.org/TR/html4/loose.dtd">
<HTML><HEAD><TITLE>ERROR: The request could not be satisfied</TITLE></HEAD>
<BODY><H1>403 ERROR</H1>
<H2>The request could not be satisfied.</H2>
Request blocked. We can't connect to the server for this app or website
at this time.
<HR noshade size="1px">
Generated by cloudfront (CloudFront)
</BODY></HTML>"""


class TestWave5Fixtures(unittest.TestCase):
    """Fixtures from Wave 5 live captures (validation/wave5/PROBLEMS.md).
    Each is the generalized captured shape, not a per-site special case."""

    def test_small_200_recaptcha_loader_include_is_open(self):
        # W5-001 (duolingo.com shape): a small but fully served 200
        # homepage whose only "captcha" occurrence is the reCAPTCHA
        # Enterprise *loader include* for its own forms. A widget
        # include is presence, not a challenge (the W1 GitHub species,
        # under the 16 KB gate). Verdict must be OPEN.
        self.assertLess(len(DUOLINGO_SHAPE_BODY), 16384)
        r = classify(200, {"Server": "duo-api"}, DUOLINGO_SHAPE_BODY)
        self.assertEqual(r["verdict"], "OPEN")
        self.assertIsNone(r["vendor"])
        self.assertNotIn("GENERIC_CAPTCHA", r["evidence"])

    def test_small_200_hcaptcha_loader_include_is_open(self):
        # W5-001 (companion): the hCaptcha loader script tag on a
        # served page is likewise a widget include, not a wall.
        body = ("<html><head><title>Community Forum</title></head>"
                "<body><h1>Welcome to the forum</h1>"
                "<p>Log in to post. New here? Create an account.</p>"
                "<script src=\"https://js.hcaptcha.com/1/api.js\" "
                "async defer></script></body></html>")
        r = classify(200, {"Server": "nginx"}, body)
        self.assertEqual(r["verdict"], "OPEN")
        self.assertNotIn("GENERIC_CAPTCHA", r["evidence"])

    def test_generic_captcha_prose_on_small_200_still_challenged(self):
        # W5-001 pin: stripping loader URLs must not swallow prose
        # challenges — the word in visible text still verdict-drives.
        r = classify(200, {}, "<html><body><p>To continue, complete "
                              "the captcha below.</p>"
                              "<div class=\"captcha-box\"></div>"
                              "</body></html>")
        self.assertEqual(r["verdict"], "CHALLENGED")
        self.assertEqual(r["vendor"], "Generic")

    def test_azure_waf_captcha_challenge_on_403(self):
        # W5-002 (ed.gov shape): Azure WAF's JS/CAPTCHA challenge
        # page — azwaf CSS namespace, /.azwaf/captcha/ assets, a
        # reference id, and no content. CHALLENGED, and the vendor
        # is Microsoft Azure WAF, not Generic.
        r = classify(403, {"Content-Type": "text/html"}, AZURE_WAF_BODY)
        self.assertEqual(r["verdict"], "CHALLENGED")
        self.assertEqual(r["vendor"], "Microsoft Azure WAF")
        self.assertIn("AZURE_WAF_MARKER", r["evidence"])

    def test_large_200_mentioning_azwaf_is_open(self):
        # The served-page gate covers the new vendor too.
        big = "<html><body>" + ("how the azwaf namespace works " * 1200) + \
              "</body></html>"
        self.assertGreater(len(big), 16384)
        r = classify(200, {"Server": "nginx"}, big)
        self.assertEqual(r["verdict"], "OPEN")
        self.assertIsNone(r["vendor"])

    def test_kasada_429_attributes_kasada(self):
        # W5-003 (chewy.com shape): a 429 whose body is Kasada's
        # KPSDK stub, behind an Akamai Bot Manager cookie. The
        # verdict stays RATE_LIMITED (a sensor is presence, never a
        # verdict — the PX_COOKIE precedent), but the vendor named
        # is the wall whose payload answered: Kasada.
        r = classify(429, {"Set-Cookie": "ak_bmsc=abc; Path=/"}, KASADA_429_BODY)
        self.assertEqual(r["verdict"], "RATE_LIMITED")
        self.assertEqual(r["vendor"], "Kasada")
        self.assertIn("KASADA_MARKER", r["evidence"])
        self.assertIn("AKAMAI_BMSC_COOKIE", r["evidence"])

    def test_cloudfront_request_blocked_403(self):
        # W5-004 (redfin.com shape): CloudFront's own "Request
        # blocked" error page. WALLED stands (bare 403), and the
        # vendor is AWS CloudFront, not nobody.
        r = classify(403, {"Server": "CloudFront"}, CLOUDFRONT_BLOCK_BODY)
        self.assertEqual(r["verdict"], "WALLED")
        self.assertEqual(r["vendor"], "AWS CloudFront")
        self.assertIn("AWS_CLOUDFRONT_BLOCK", r["evidence"])

    def test_akamai_reference_deny_on_444_is_walled(self):
        # W5-005 (delta.com shape): an Akamai "Access Denied"
        # reference page served with status 444 — the deny shape
        # is not 403-only, and 444 is never a served page.
        body = ("<HTML><HEAD>\n<TITLE>Access Denied</TITLE>\n</HEAD><BODY>\n"
                "<H1>Access Denied</H1>\n \nYou don't have permission "
                "to access this server.<P>\nReference "
                "0.116bdc17.1792816805.402e199e\n</BODY>\n</HTML>")
        r = classify(444, {"Server": "AkamaiGHost"}, body)
        self.assertEqual(r["verdict"], "WALLED")
        self.assertEqual(r["vendor"], "Akamai")
        self.assertIn("AKAMAI_REFERENCE", r["evidence"])

    def test_bare_444_is_walled(self):
        # W5-005 (companion): a 444 with no attribution at all is
        # still a refusal — the status means the server closed the
        # request without serving content, so OPEN is definitionally
        # wrong for it.
        r = classify(444, {"Server": "nginx"}, "")
        self.assertEqual(r["verdict"], "WALLED")
        self.assertIsNone(r["vendor"])
        self.assertIn("STATUS_444", r["evidence"])

    def test_cloudfront_text_without_request_blocked_is_unattributed(self):
        # W5-004 pin: CloudFront also generates "could not be
        # satisfied" pages for origin errors; without the "Request
        # blocked" line there is no block attribution.
        body = CLOUDFRONT_BLOCK_BODY.replace("Request blocked. ", "")
        r = classify(403, {"Server": "CloudFront"}, body)
        self.assertEqual(r["verdict"], "WALLED")
        self.assertIsNone(r["vendor"])
        self.assertNotIn("AWS_CLOUDFRONT_BLOCK", r["evidence"])


class TestWave7Fixtures(unittest.TestCase):
    """Wave 7 regressions (validation/wave7/PROBLEMS.md)."""

    def test_turnstile_verification_interstitial_is_challenged(self):
        # W7-001 (careerjet shape, live capture — CORRECTED): the
        # capture looked like a homepage from its <head> (styles,
        # spinner) but stripping scripts/styles leaves ONLY
        # "Careerjet / Verification required / Our systems have
        # detected unusual traffic ... not a robot" — a genuine
        # verification interstitial, not a served page. The
        # Turnstile loader on a check-only page IS the challenge
        # mechanism, so CF_CHALLENGE_PLATFORM correctly fires.
        # Lesson pinned here: hand-classification must read the
        # visible text (scripts/styles stripped), never the head.
        body = ("<!DOCTYPE html><html lang=\"en\"><head>"
                "<meta charset=\"utf-8\"><title>Careerjet</title>"
                "<style>@keyframes svg_wait_rotation{}</style></head>"
                "<body><h1>Verification required</h1>"
                "<p>Our systems have detected unusual traffic from "
                "your computer network. This page checks to see if "
                "it's really you sending the requests, and not a "
                "robot.</p>"
                "<div class=\"cf-turnstile\" "
                "data-sitekey=\"0x4AAAAAACFype7J48Z2j8-U\"></div>"
                "<script src=\"https://challenges.cloudflare.com/turnstile/v0/api.js\">"
                "</script></body></html>")
        r = classify(200, {"Server": "nginx",
                           "Content-Type": "text/html;charset=UTF-8"}, body)
        self.assertEqual(r["verdict"], "CHALLENGED")
        self.assertEqual(r["vendor"], "Cloudflare")
        self.assertIn("CF_CHALLENGE_PLATFORM", r["evidence"])

    def test_just_a_moment_with_turnstile_still_challenged(self):
        # W7-001 control: a classic Cloudflare challenge page with
        # the Turnstile loader still classifies CHALLENGED via the
        # independent "Just a moment" marker.
        body = ("<!DOCTYPE html><html><head><title>Just a moment...</title>"
                "</head><body><p>Just a moment...</p>"
                "<script src=\"https://challenges.cloudflare.com/turnstile/v0/api.js\">"
                "</script></body></html>")
        r = classify(403, {}, body)
        self.assertEqual(r["verdict"], "CHALLENGED")
        self.assertEqual(r["vendor"], "Cloudflare")
        self.assertIn("CF_JUST_A_MOMENT", r["evidence"])


class TestMcpClassifierToolShape(unittest.TestCase):
    def test_classify_tool_via_server_handle(self):
        from wallcheck.server import handle
        resp = handle({"jsonrpc": "2.0", "id": 7, "method": "tools/call",
                       "params": {"name": "classify",
                                  "arguments": {"status": 429, "headers": {}, "body": ""}}})
        self.assertEqual(resp["id"], 7)
        sc = resp["result"]["structuredContent"]
        self.assertEqual(sc["verdict"], "RATE_LIMITED")


if __name__ == "__main__":
    unittest.main()
