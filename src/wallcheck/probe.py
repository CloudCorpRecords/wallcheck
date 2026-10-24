"""One honest fetch. No spoofing, no retries against a wall, no JS."""

from __future__ import annotations

import time
import urllib.error
import urllib.parse
import urllib.request

from . import __version__
from .classify import classify
from .exposure import scan_text

USER_AGENT = (
    "wallcheck/%s (+https://github.com/CloudCorpRecords/wallcheck) "
    "bot-wall-transparency-probe" % __version__
)
MAX_REDIRECTS = 5
BODY_CAP = 64 * 1024


class _RecordingRedirectHandler(urllib.request.HTTPRedirectHandler):
    def __init__(self):
        self.chain = []

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if len(self.chain) >= MAX_REDIRECTS:
            return None
        self.chain.append(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def probe_url(url, timeout=15, extra_headers=None, include_exposure=False):
    """Fetch `url` once and return the stable classification object.

    `extra_headers` (e.g. RFC 9421 Signature/Signature-Input from
    wallcheck.sign) are attached to the same single honest fetch —
    identification, never camouflage.

    `include_exposure` (opt-in, default off) additionally scans the
    already-fetched body for key-like material and adds an
    "exposure" key: {"findings": [...], "counts": {class: n}}.
    Findings carry pattern, class, length and a hash fingerprint —
    never a value."""
    handler = _RecordingRedirectHandler()
    opener = urllib.request.build_opener(handler)
    headers = {"User-Agent": USER_AGENT}
    if extra_headers:
        headers.update(extra_headers)
    req = urllib.request.Request(url, headers=headers)
    start = time.monotonic()
    status, headers, body, final_url, error = None, {}, "", url, None
    try:
        with opener.open(req, timeout=timeout) as resp:
            status = resp.status
            headers = dict(resp.headers.items())
            final_url = resp.geturl()
            body = resp.read(BODY_CAP).decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        status = e.code
        headers = dict(e.headers.items()) if e.headers else {}
        final_url = e.geturl() or url
        try:
            body = e.read(BODY_CAP).decode("utf-8", errors="replace")
        except Exception:
            body = ""
    except Exception as e:  # URLError, timeout, TLS, DNS...
        error = "%s: %s" % (type(e).__name__, e)
    elapsed_ms = int((time.monotonic() - start) * 1000)

    result = classify(status, headers, body, final_url=final_url,
                      redirect_chain=handler.chain, error=error)
    out = {
        "url": url,
        "final_url": final_url,
        "status": result["status"],
        "verdict": result["verdict"],
        "vendor": result["vendor"],
        "evidence": result["evidence"],
        "elapsed_ms": elapsed_ms,
        "redirect_chain": handler.chain,
    }
    if include_exposure:
        # The scan runs over the body this fetch already captured,
        # which is capped at BODY_CAP (64 KB) — key material served
        # past the cap is out of reach of this path (the standalone
        # sweep script samples up to 2 MB). No extra fetch is made.
        site = urllib.parse.urlsplit(final_url).hostname or url
        findings = scan_text(body, site, url)
        counts = {}
        for f in findings:
            counts[f["class"]] = counts.get(f["class"], 0) + 1
        out["exposure"] = {"findings": findings, "counts": counts}
    return out
