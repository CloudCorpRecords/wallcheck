# Wave 10 — Signing regression on the 0.5.0-rc code path (Leg C)

Question: did the 0.5.0-rc stamp or the Wave 9 audit-tool addition
regress the Wave 4 signing machinery? Answer: **no regression.**

## Self-verification (offline, no network)

A fresh Ed25519 key was generated on the rc code path
(`validation/wave10/wave10-rc-key.json`, 0600, secret never printed
or quoted anywhere). The rc's `sign_request` output verifies
against the rc's own `verify_request` (ok, keyid + web-bot-auth
tag), a tampered signature is rejected, and `directory_document()`
renders a one-key JWKS document for the fresh key. The full suite
(152/152, including the Wave 4 RFC 8032 vector tests and the
public-only verification tests) also passes, so the Wave 4
fixtures still pin the same behavior.

Note on the code path, stated honestly: Leg C ran on the
0.5.0-rc-stamped tree including Wave 10's classifier/audit fixes
(W10-001…W10-008). The signing module itself is unchanged since
Wave 4; the regression question is whether the rc surface around it
broke it, and it did not. No version bump was made for the Wave 10
fixes (they are unreleased fixes on the rc tree, not a new rc).

## Signed vs unsigned (7 targets, one honest fetch each)

| target | group | unsigned | signed | changed |
| --- | --- | --- | --- | --- |
| chatgpt.com | adopter | OPEN | OPEN | no |
| www.indeed.com | adopter | OPEN | OPEN | no |
| substack.com | adopter | OPEN | OPEN | no |
| www.ahrefs.com | adopter | OPEN | OPEN | no |
| upwork.com | walled control | WALLED / Cloudflare | WALLED / Cloudflare | no |
| fiverr.com | walled control | CHALLENGED / PerimeterX | CHALLENGED / PerimeterX | no |
| guru.com | walled control | WALLED / Imperva | WALLED / Imperva | no |

**7/7 unchanged** — the same finding as Wave 5's 12/12 and Wave 2's
own-property probes. An unregistered signature is not consulted by
any wall or any adopter: the adopters publish directories for
verifying *their* agents' keys, not for exempting an unknown
wallcheck key, and the walls trust no key they were not given.
The passport remains proven machinery, not proven acceptance — the
campaign's identity front still has to move adoption (4 of 499)
before any site honors a wallcheck signature in practice.

Raw results: `validation/wave10/results-signed-rc.json` (7 rows).
