"""wallcheck CLI: probe a URL, name the wall, show the evidence."""

from __future__ import annotations

import argparse
import json
import sys

from . import __version__
from .classify import OPEN
from .probe import probe_url


def _print_human(r):
    print("%s -> %s" % (r["url"], r["verdict"]))
    if r["final_url"] != r["url"]:
        print("  final url: %s" % r["final_url"])
    print("  status: %s" % (r["status"] if r["status"] is not None else "none"))
    print("  vendor: %s" % (r["vendor"] or "none detected"))
    print("  elapsed: %dms" % r["elapsed_ms"])
    if r["redirect_chain"]:
        print("  redirects: %s" % " -> ".join(r["redirect_chain"]))
    print("  evidence:")
    for e in r["evidence"]:
        print("    - %s" % e)
    if "exposure" in r:
        exp = r["exposure"]
        print("  exposure: %d finding(s)" % len(exp["findings"]))
        for cls in sorted(exp["counts"]):
            print("    - %s: %d" % (cls, exp["counts"][cls]))
        for f in exp["findings"]:
            if f["class"] == "CANDIDATE_EXPOSURE":
                print("    ! candidate: %s (fingerprint %s)"
                      % (f["pattern"], f["sha256_16"]))


def _print_audit(r):
    print("audit %s -> grade %s (%d/%d)" % (
        r["target"], r["grade"], r["score"], r["max_score"]))
    for c in r["checks"]:
        print("  [%s] %s — %s" % (c["status"], c["check"], c["detail"]))
        for e in c["evidence"]:
            print("      - %s" % e)
    if r["fixes"]:
        print("  fixes:")
        for f in r["fixes"]:
            print("    - %s" % f)


def _cmd_audit(args):
    from .audit import audit_site
    result = audit_site(args.target, timeout=args.timeout)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        _print_audit(result)
    return 0 if result["grade"] in ("A", "B") else 1


def _cmd_keygen(args):
    from .sign import ALG, generate_key, key_fingerprint, save_key
    key = generate_key(keyid=args.keyid, alg=args.alg)
    save_key(key, args.out)
    print("wrote key file: %s" % args.out)
    print("  keyid: %s" % key["keyid"])
    if key["alg"] == ALG:
        print("  alg: %s (RFC 9421, shared secret — keep this file "
              "private)" % key["alg"])
    else:
        print("  alg: %s (RFC 9421 + RFC 8032; the seed in this file "
              "is private, the public key is directory-publishable)"
              % key["alg"])
        print("  public: %s" % key["public_b64"])
    print("  fingerprint: %s" % key_fingerprint(key))
    return 0


def _cmd_verify_server(args):
    from .sign import load_key, serve_verify_server
    key = load_key(args.key)
    serve_verify_server(key, args.host, args.port)
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="wallcheck",
        description="Deterministic bot-wall transparency: probe a URL, "
                    "name the wall, get the evidence.")
    parser.add_argument("--version", action="version",
                        version="wallcheck %s" % __version__)
    sub = parser.add_subparsers(dest="command")

    p = sub.add_parser("probe", help="probe one URL")
    p.add_argument("url")
    p.add_argument("--json", action="store_true", help="machine-readable output")
    p.add_argument("--timeout", type=int, default=15)
    p.add_argument("--sign", metavar="KEYFILE",
                   help="attach an RFC 9421 signature from this key "
                        "file (algorithm from the key: hmac-sha256 or "
                        "ed25519, Web Bot Auth style) — signed agent "
                        "identity, same single honest fetch")
    p.add_argument("--exposure", action="store_true",
                   help="also scan the served page for key-like "
                        "material (candidate exposures, public-by-design "
                        "keys, visitor tokens); findings are "
                        "fingerprint-only, never values")

    a = sub.add_parser("audit", help="audit a site's agent-access "
                                     "posture (owner-side: robots "
                                     "directives, llms.txt, sitemap, "
                                     "feeds, API, signed-agent readiness)")
    a.add_argument("target", help="domain or URL, e.g. example.com")
    a.add_argument("--json", action="store_true",
                   help="machine-readable output")
    a.add_argument("--timeout", type=int, default=15)

    k = sub.add_parser("keygen", help="generate a signing key file")
    k.add_argument("--out", default="wallcheck-key.json")
    k.add_argument("--keyid", default=None)
    k.add_argument("--alg", default="hmac-sha256",
                   choices=["hmac-sha256", "ed25519"],
                   help="hmac-sha256 (shared secret, bilateral) or "
                        "ed25519 (public key, directory-publishable; "
                        "default hmac-sha256)")

    v = sub.add_parser("verify-server", help="run a tiny local HTTP "
                                             "server that only accepts "
                                             "requests signed with a key")
    v.add_argument("--key", required=True)
    v.add_argument("--host", default="127.0.0.1")
    v.add_argument("--port", type=int, default=8799)

    args = parser.parse_args(argv)

    if args.command == "audit":
        return _cmd_audit(args)
    if args.command == "keygen":
        return _cmd_keygen(args)
    if args.command == "verify-server":
        return _cmd_verify_server(args)
    if args.command != "probe":
        parser.print_help()
        return 2

    url = args.url if "://" in args.url else "https://" + args.url
    extra_headers = None
    if args.sign:
        from .sign import load_key, sign_request
        key = load_key(args.sign)
        extra_headers = sign_request(url, key)
    result = probe_url(url, timeout=args.timeout, extra_headers=extra_headers,
                       include_exposure=args.exposure)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        _print_human(result)
    return 0 if result["verdict"] == OPEN else 1


if __name__ == "__main__":
    sys.exit(main())
