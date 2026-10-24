# wallcheck

**Point an agent at a URL. Find out what actually stops it — with receipts.**

**0.5.0** — stamped final at the ship-readiness pass (release
candidate at Wave 9). Not yet published; the launch hold stands. What is proven, what is not, and what the ship
decision still needs: [campaign/LAUNCH-READINESS.md](campaign/LAUNCH-READINESS.md).

Agents die silently on bot walls. A fetch returns 403, a browser session
churns through environment after environment, an upload never starts —
and nothing can say *what* stopped it, *whose* wall it was, or show the
evidence. wallcheck probes a URL once, honestly, and classifies what an
agent really hits: `OPEN`, `CHALLENGED`, `WALLED`, `LOGIN_GATED`,
`RATE_LIMITED`, or `UNREACHABLE` — naming the vendor (Cloudflare,
PerimeterX, DataDome, Akamai, Imperva, AWS WAF, Microsoft Azure WAF,
Kasada, AWS CloudFront) and the exact signals
that prove it.

No LLM anywhere in the verdict: the classifier is a deterministic pure
function of `(status, headers, body)`. Same response in, same verdict
out — which is what makes the results safe to put in CI, in an incident
report, or in the public [Bot Wall Index](SPEC.md#the-bot-wall-index-flywheel).

**New in v0.2:** signed agent identity. `wallcheck keygen` mints an
RFC 9421 signing key and `wallcheck probe <url> --sign key.json`
attaches a real HTTP Message Signature (`hmac-sha256`,
`tag="web-bot-auth"`) to the probe — an agent with a name, not an
anonymous bot. `wallcheck verify-server --key key.json` runs a tiny
server that honors only correctly signed requests, so site owners can
test their side. The `hmac-sha256` variant covers
bilateral agent↔owner setups; Ed25519 (v0.4) covers the public
directory case — see
[validation/wave2/SIGNING.md](validation/wave2/SIGNING.md).

**New in 0.5.0:** the owner-side audit joins the MCP server as
the `audit` tool (up to 10 honest GETs per call, same bounded-fetch
discipline as `probe_url`), the docs pass in Wave 9 corrected every
stale count against measured reality, and the suite stood at 120
tests at the Wave 9 stamp. Waves 10–17 took it to 428 tests (the
Wave 17 audit's 423 predates the W17-007 live fix's 5 fixtures —
see [validation/wave17/STABILITY-12.md](validation/wave17/STABILITY-12.md));
Wave 18's battery v10 plus the W18-007 live fix took it to 481.
Wave 19's battery v11 took it to 532; Wave 20's battery v12 took
it to 571; Wave 21's battery v13 took it to 608; Wave 22's
battery v14 took it to 638; Wave 23's battery v15 took it to
674; Wave 24's battery v16 took it to 710; Wave 25's battery
v17 took it to 747; Wave 26's battery v18 took it to 788;
Wave 27's battery v19 took it to 831.

**New in v0.5:** the classifier learned the territory the Wave 5
expansion measured — Microsoft Azure WAF, Kasada, and AWS
CloudFront detection; the Akamai reference-token deny page; a
verdict rule for status 444 (a dropped request is a refusal, never
an OPEN); and the end of the false-challenge species where a
served page merely embeds a reCAPTCHA/hCaptcha loader for its own
forms. All five Wave 5 defects are fixed test-first from live captures
([PROBLEMS.md](validation/wave5/PROBLEMS.md)). The index now
covers 500 sites (Waves 6–7 expansion, Wave 18 row 500), and Wave 5 ran the first signed-vs-unsigned
experiment with the shipped signer
([SIGNED-EXPERIMENT.md](validation/wave5/SIGNED-EXPERIMENT.md)):
an unregistered key changed no verdict anywhere — the measured
baseline the campaign's identity front has to move. For owners,
the [Fix Kit](campaign/FIX-KIT.md) turns audit findings into
vendor-verified remediation steps.

**New in v0.4:** Ed25519 signed identity. The signer now implements
Ed25519 per RFC 8032 in pure Python stdlib (verified against the
official RFC 8032 §7.1 test vectors), so `wallcheck keygen --alg
ed25519` mints a directory-compatible Web Bot Auth key — the public
half publishes in a `/.well-known/http-message-signatures-directory`
document, and `probe --sign` auto-detects the key's algorithm.
Wave 4 also took the index's third data point and ran the first
signed-agent-directory census of all 154 index domains
([DIRECTORY.md](validation/wave4/DIRECTORY.md)).

**New in v0.3:** the owner-side audit. `wallcheck audit <domain>`
grades a site's agent-access posture across six checks — robots.txt
AI-agent directives, llms.txt sanity (an HTML soft-404 *fails*),
sitemap, feed discovery, API discovery, and Web Bot Auth
signed-agent readiness — each PASS/WARN/FAIL with evidence and a
concrete fix, rolled into an A–F grade. First live audits
([validation/wave3/AUDITS.md](validation/wave3/AUDITS.md)): our own
properties grade D/F — the audit found real work on our own sites
before anyone else's. v0.3 also adds AWS WAF detection to the
classifier and merges the census into the
[Bot Wall Index](INDEX.md) working table (499 sites after the
Waves 6–7 expansion).

## Non-goals

wallcheck will **never** solve CAPTCHAs, spoof fingerprints or user
agents, or bypass/evade a wall, rate limit, or access control. The probe
identifies itself (`wallcheck/<version>` user agent). The combat is
detection + evidence + standards: a wall an agent can *name* is a bug
report; signed agent identity (Web Bot Auth, RFC 9421 — prototype
shipped in v0.2, see [SPEC.md](SPEC.md)) is how agents stop being
anonymous in the first place.

## Usage

### CLI

```bash
# No install needed beyond Python 3.11+ (standard library only):
PYTHONPATH=src python3 -m wallcheck probe https://www.upwork.com

# Or install the package:
pip install .   # then: wallcheck probe <url> [--json]
```

Example output (a real run — see [DOGFOOD.md](DOGFOOD.md) for the full set):

```
https://example.com -> OPEN
  status: 200
  vendor: none detected
  elapsed: 87ms
  evidence:
    - STATUS_200
```

Exit codes: `0` for OPEN, `1` for any other verdict, `2` for usage
errors — CI-ready. `--json` prints one stable object:
`{url, final_url, status, verdict, vendor, evidence[], elapsed_ms,
redirect_chain[]}`.

Signed probes and owner-side verification:

```bash
PYTHONPATH=src python3 -m wallcheck keygen --out wallcheck-key.json
PYTHONPATH=src python3 -m wallcheck probe https://example.com --sign wallcheck-key.json
PYTHONPATH=src python3 -m wallcheck verify-server --key wallcheck-key.json --port 8799
```

Owner-side audit of your own site's agent-access posture:

```bash
PYTHONPATH=src python3 -m wallcheck audit example.com [--json]
```

Six checks (robots.txt, llms.txt, sitemap, feed, API, signed-agent
readiness) → per-check PASS/WARN/FAIL + evidence + a fix list, and a
grade. Exit `0` for grade A/B, `1` otherwise.

### Verdicts

| verdict | meaning |
| --- | --- |
| `OPEN` | Served. An agent can read it. |
| `CHALLENGED` | An interactive human-verification challenge was presented (Cloudflare "Just a moment", a CAPTCHA page). Non-interactive agents stop here. |
| `WALLED` | A hard block page ("Sorry, you have been blocked", a deny page, a bare 403). No challenge is even offered. |
| `LOGIN_GATED` | Redirected to / served a login wall. Content exists, behind authentication. |
| `RATE_LIMITED` | HTTP 429 without a stronger wall signal. A throttle, not a wall. |
| `UNREACHABLE` | The fetch failed (DNS/TLS/timeout) or 5xx. No wall verdict is claimed. |

### MCP server

```bash
PYTHONPATH=src python3 -m wallcheck mcp
# or, installed: wallcheck-mcp
```

Tools:

- `probe_url(url, timeout?)` — live fetch → classification object.
- `classify(status, headers, body)` — offline classification of a
  response you captured yourself. No network.
- `audit(domain, timeout?)` — owner-side agent-access audit: grade
  plus per-check PASS/WARN/FAIL. Up to 10 honest GETs to the one
  domain, same bounded-fetch discipline as `probe_url`.

Add to an MCP client config as a stdio server running either command,
or via Docker (GHCR image planned at ship time; see `Dockerfile`).

## Tests

Fully offline — recorded fixtures exercise the pure classifier:

```bash
python3 -m unittest discover -s tests -v
```

## Family

By [Rene Turcios](https://github.com/CloudCorpRecords) — sibling of
[greenlight](https://github.com/CloudCorpRecords/greenlight) (know before
you claim an issue: GO/NO-GO with evidence) and
[mcpaudit](https://github.com/CloudCorpRecords/mcpaudit) (audit any MCP
server, scored). Same house rules: deterministic core, named issues,
evidence over vibes, dogfood on real targets before claiming anything.

Full product spec, roadmap (Web Bot Auth signing shipped as the
v0.2 prototype; the owner-side audit shipped in v0.3), and the Bot
Wall Index plan: [SPEC.md](SPEC.md). Validation waves live in
`validation/` — Wave 2 added depth probing of 77 platform paths
([PATHS.md](validation/wave2/PATHS.md)) and the signing prototype
([SIGNING.md](validation/wave2/SIGNING.md)); Wave 3 added the
stability re-probe, the 154-site index, and the audit's first live
runs ([AUDITS.md](validation/wave3/AUDITS.md)). Wave 4 added the
third stability data point ([STABILITY-2.md](validation/wave4/STABILITY-2.md)),
the signed-agent directory census
([DIRECTORY.md](validation/wave4/DIRECTORY.md)), and Ed25519. Wave 5
added the territory growth, the signed-vs-unsigned experiment, and
the owner fix kit; Wave 6 hardened the classifier against 25
adversarial shapes; Wave 7 took the index to 499 sites, ran the
second directory census (4 adopters) and an audit sweep; Wave 8
probed paths on 46 more platforms and took the front-doors file to
65 platforms. Wave 9 stamped 0.5.0-rc and added the audit MCP tool;
Waves 10–28 ran nineteen more stability rounds (rounds 6–24)
and adversarial batteries v2–v20, took the suite to 885 tests,
and kept the launch hold.

## License

MIT — see [LICENSE](LICENSE).
