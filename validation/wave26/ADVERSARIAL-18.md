# Wave 26 — Adversarial Battery v18 (41 shapes)

Hand-first discipline as in Waves 6, 10–25: HANDCLASS-18.md was
written BEFORE the battery ran. First run: **7 failures, 34
passes — exactly the predicted gaps in 3 families, zero
surprises.** After the three generalized fixes: **41/41 green**,
corpus regression clean (44 captures, diff empty vs
`validation/wave15/corpus-after.txt`), full suite **788/788**
via pytest (747 at wave start + 41).

| Family | Shapes | First run | After fix |
|--------|--------|-----------|-----------|
| U1 label-element markers | 5 | 5 pins held | — |
| U2 HTTP 451 + Retry-After | 4 | 4 pins held | — |
| U3 badge-tap login walls | 7 | **1 defect** (U3a) + 6 pins held | fixed (W26-U3) |
| U4 robots UA trailing spaces | 5 | 5 pins held | — |
| U5 llms mixed LF/CRLF | 4 | 4 pins held | — |
| U6 sitemap pct-encoded hosts | 4 | **2 defects** (U6c, U6d) + 2 pins held | fixed (W26-U6) |
| U7 CA/ET/HY/KA phrases | 7 | **4 defects** (U7a–d) + 3 pins held | fixed (W26-U7) |
| U8 button-text phrases | 5 | 5 pins held | — |

## The three defect families

**W26-U3 — badge-tap sign-in prompts had no signal.** The auth
family named every credential ceremony except the physical one:
a page whose only content instructs the user to tap a workplace
ID badge on a reader read OPEN. The fix adds
`_is_badge_tap_prompt` to the auth elif chain with
`BADGE_TAP_PROMPT` evidence, two-keyed from birth: (1) a full
badge-tap phrase ("tap your badge", "tap your id badge", "tap
your employee badge", "tap your security badge", "hold your
badge") in RENDERED visible text — never the bare word "badge";
(2) prompt machinery (a <button> or <form>). All six guards
held from the first run and remain as pins: the prompt inside
BIG_ARTICLE stays OPEN (the chain's served-page gate),
asset-filename (badge-tap.js) and stylesheet-class
(.badge-tap-prompt) carriers stay OPEN, prose with the wording
but no machinery stays OPEN (U3e — the machinery key is
load-bearing), the same prompt at a login URL agrees with the
heuristic (U3f), and wording carried only by a script string
stays OPEN even beside a real button and form (U3g — the
visible-text key is load-bearing).

**W26-U6 — percent-encoded sitemap hosts counted as
destinations.** The loc test asked whether an entry names a
crawlable URL, but accepted any non-empty http(s) loc — so a
urlset whose only loc was `https://%65xample.com/a` passed,
although the WHATWG host parser rejects "%" in hosts of
special schemes and the loc does not parse as a URL at all
under standard URL parsing. The fix tests only the authority
component: for absolute locs, a "%" in the host (after any
userinfo) skips the entry. Path percent-encoding is untouched
(U6a pin: `https://example.com/%70age` passes), and one good
loc still suffices (U6b pin). Checked against the older pins
before fixing, per the Wave 25 lesson: K6 (relative/query),
L6 (fragments), N6 (non-HTTP schemes), Q6 (uppercase scheme)
— none carries a percent-encoded authority, and the full
suite confirms none broke.

**W26-U7 — Catalan, Estonian, Armenian, Georgian challenge
phrases missing.** `_LOCALIZED_HUMAN_CHECK` covered 47
languages but none of these four. All eight strings were
grep-verified absent before the battery was written, with the
distinctions that keep them collision-free: Catalan "no soc"
is not Spanish "no soy"; Estonian "ma ei ole robot" is not
Finnish "en ole robotti"; Armenian and Georgian are unique
scripts. The fix adds all eight with per-language comments.
Guards held: ET phrase on BIG_ARTICLE stays OPEN (served-page
gate), the bare fragment "robot" stays OPEN (the fragment
rule), the HY phrase inside a <style> block stays OPEN
(style suppression).

## The pins that mattered

- **U1/U8 (presented text, last unnamed carriers):** <label>
  element text and <button> text complete the presented-
  element survey — figcaption (R1), summary (R8), blockquote
  (T1), textarea values (T8), label text, and button text all
  fire on non-served pages and gate on served ones; the
  never-presented family (head, noscript, template, picture
  stray text, SVG metadata, style, data/placeholder/aria
  attributes) is closed on both poles.
- **U2 (451 + Retry-After):** the deliberate-refusal family
  does not yield to a duration header — the throttle rule's
  403/503 scope held against a 451 carrying both Retry-After
  and throttle wording, and the P2c composition (verdict
  governs, vendor cell records body evidence) held with the
  header present.
- **U4 (robots whitespace):** trailing spaces inside the
  User-agent value and the Disallow value bind exactly as
  their trimmed forms do — whitespace is not an exemption,
  for named agents or the wildcard.
- **U5 (mixed line endings):** an llms.txt mixing LF and CRLF
  behaves exactly like either uniform twin, frontmatter strip
  included — the W19-L5 normalization composes per-line, not
  per-file.
