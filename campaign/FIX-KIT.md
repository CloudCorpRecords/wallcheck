# The Owner Fix Kit — opening your own front door, on purpose

*For site owners. The Bot Wall Index (`INDEX.md`) measures what an
identified agent actually gets from your site. This kit is the
other half of the campaign: the concrete, vendor-verified steps to
fix the walls that are accidents — and to keep the ones that are
policy, but make them legible. Every dashboard path and field name
below was checked against the vendor's current public
documentation; citations are inline. Nothing here weakens
protection on authenticated or abuse-prone surfaces — the whole
point is that a wall can tell the difference.*

**Diagnose first.** Run `wallcheck audit yourdomain.com`. It
grades the six things agents look for — robots.txt, llms.txt,
sitemap, feed, API surface, signed-agent directory — and names the
failure mode (a machine file that is *walled* fails differently
from one that is *missing*). Then work this kit top-down.

---

## 1. Cloudflare: exempt verified and signed agents from managed challenges

Cloudflare already knows how to tell a proven agent from an
anonymous one. A request carrying a valid Web Bot Auth signature
is classified as a **verified bot**: the Bot Management variable
`cf.bot_management.signed_agent` "indicates whether the request
originated from a known agent that self-identifies with Web Bot
Auth. Such agents are now classified as verified bots"
([Bot Management variables](https://developers.cloudflare.com/bots/reference/bot-management-variables/)).
The fix is to stop challenging the requests you can already
identify.

### Step 1 — Add a Skip rule for verified bots (works on any plan with WAF custom rules)

1. Cloudflare dashboard → your zone → **Security → WAF → Custom
   rules → Create rule**.
2. Name it e.g. `Exempt verified bots and signed agents`.
3. Expression (Edit expression):
   ```
   (cf.client.bot)
   ```
   `cf.client.bot` is the field Cloudflare's own use-case page
   uses to determine "if the request originated from a known good
   bot or crawler," in a rule that challenges everyone else
   ([Allow traffic from search engine bots and other verified bots](https://developers.cloudflare.com/waf/custom-rules/use-cases/allow-traffic-from-verified-bots/)).
4. Action: **Skip** — and in the Skip options, skip the rules and
   phases your challenge lives in (your remaining custom rules,
   the Managed Rulesets, and Super Bot Fight Mode as applicable).
   Custom rules support the *Skip* action and run in the
   `http_request_firewall_custom` phase, before managed rules
   ([Security features interoperability](https://developers.cloudflare.com/waf/feature-interoperability/)).
5. **Place this rule above every challenge/block rule.** Custom
   rules evaluate in list order; an exemption that runs after the
   challenge exempts nothing.

### Step 2 — If you have Bot Management, aim precisely

Bot Management fields require a Bot Management subscription
([Custom rules, bot solutions docs](https://developers.cloudflare.com/bots/additional-configurations/custom-rules/));
the signed-agent field is an Enterprise Bot Management add-on
field ([Fields reference](https://developers.cloudflare.com/ruleset-engine/rules-language/fields/reference/)).
With it, you can exempt *only* signature-proven agents, and *only*
on public paths — Cloudflare's own docs compose bot fields with
`http.request.uri.path` for exactly this path-specific pattern
(same custom-rules doc):

```
(cf.bot_management.signed_agent and http.request.method eq "GET"
 and not starts_with(http.request.uri.path, "/wp-admin")
 and not starts_with(http.request.uri.path, "/checkout"))
```
Action: **Skip**, as above. Authenticated and transactional paths
keep full protection; the identity does the sorting, not the
user-agent string.

Super Bot Fight Mode users (Pro/Business/Enterprise without the
Bot Management add-on) have a coarser switch: SBFM lets you set an
action for **Verified bots** traffic separately, and a custom-rule
Skip can bypass SBFM for chosen requests (interoperability doc,
above).

### Step 3 — Exempt the machine files by path

`robots.txt`, `llms.txt`, the sitemap, and the signature directory
are how an agent asks permission and proves identity. Challenging
them is pure loss — Wave 4 found 16 of 154 major domains wall even
the directory path (`validation/wave4/DIRECTORY.md`), which means
an agent cannot even *ask* who it should sign as. Add a path rule
above your bot rules:

```
(http.request.uri.path in {"/robots.txt" "/llms.txt"
  "/llms-full.txt" "/sitemap.xml"}
 or http.request.uri.path eq
  "/.well-known/http-message-signatures-directory")
```
Action: **Skip** (or Allow). These are small static documents; no
challenge product decision should ever have rested on them.

### Two Cloudflare caveats, from Cloudflare's docs

- **Bot Fight Mode cannot be skipped.** On Free plans, Bot Fight
  Mode "is a simple on/off toggle… You cannot customize its
  behavior or skip it with custom rules" (interoperability doc).
  If you need agent exemptions on a Free plan, the honest options
  are turning Bot Fight Mode off or moving to Super Bot Fight
  Mode / Bot Management — there is no rule that exempts anyone
  from it.
- **Check your AI-bot settings didn't decide for you.** The
  dashboard's bot settings (Security Settings, filtered by Bot
  traffic) offer one-click blocking of AI crawlers, and Cloudflare
  can *manage your robots.txt for you*, prepending its own
  directives (`is_robots_txt_managed` in the
  [Bot Management API](https://developers.cloudflare.com/api/resources/bot_management/);
  [Managed robots.txt docs](https://developers.cloudflare.com/bots/additional-configurations/managed-robots-txt/)).
  If your robots policy and your challenge behavior disagree with
  what you intended, one of these defaults is usually why.

The same pattern — identity exemption rule + machine-file path
allowlist, ordered first — ports to any WAF that can match on a
verified-bot signal and a URI path; the field names above are
Cloudflare's because Cloudflare's are the ones we verified.

---

## 2. Serve a real llms.txt

`llms.txt` is the curated map you hand an agent instead of making
it scrape: an H1 with the site's name (the only required element),
a blockquote summary, then H2 sections of link lists, with an
`## Optional` section for links an agent may skip when context is
tight ([The /llms.txt file, v2 — llmstxt.org](https://llmstxt.org/)).

Template:

```markdown
# Your Site Name

> One-paragraph summary: what this site is, who runs it, and the
> single most important thing an agent should understand about it.

## Product / Documentation / Policies

- [Pricing](https://example.com/pricing): What it costs, in one line.
- [API reference](https://example.com/docs/api): How an agent's
  user can connect programmatically.

## Optional

- [About](https://example.com/about): Background, safe to skip.
```

Two failure modes to avoid — both measured, both embarrassing:

- **The soft-404.** An SPA or a catch-all rewrite serves the app's
  HTML shell with status 200 at `/llms.txt`. There is no text file
  there; our own Clipwise did exactly this until Wave 5 caught it
  (`fix-kit/`). Test yours the way an agent receives it:
  `curl -s https://yoursite.com/llms.txt | head` must print the
  markdown as `text/plain`, not `<!DOCTYPE html`. Serve the file
  as a static asset *ahead of* your SPA fallback.
- **The stale map.** An llms.txt pointing at moved pages is worse
  than none — agents trust it. Regenerate it when your sitemap
  changes, or generate both from the same source.

Serve `/llms-full.txt` (the same map with full text inlined) only
if your content is small enough to stay useful in one fetch.

---

## 3. robots.txt: say the policy you actually mean

robots.txt (RFC 9309) decides *fetching*. Three honest postures,
with what each one costs you:

### Variant A — Open (agents welcome)

```
User-agent: *
Allow: /

Sitemap: https://example.com/sitemap.xml
```

*Trade-off:* maximum discoverability — your pages can be read,
quoted, and cited by assistants acting for users. You are relying
on rate limits and authentication, not obscurity, for protection —
which is where protection actually lives anyway.

### Variant B — Restricted (public yes, bulk/training no)

```
# User agents fetch on behalf of a person asking a question.
User-agent: GPTBot
User-agent: ClaudeBot
User-agent: CCBot
Disallow: /

User-agent: *
Allow: /
Disallow: /account/
Disallow: /checkout/

Sitemap: https://example.com/sitemap.xml
```

*Trade-off:* named training crawlers are told no (honored by the
operators who publish those agents — the audit parses GPTBot,
ClaudeBot, CCBot and Google-Extended groups individually), while
user-directed agents and search stay open, and private paths stay
private to everyone. You lose training-corpus presence; you keep
being *answerable*. Note the group rules are matched per agent —
a named group that disallows overrides the wildcard allow for that
agent, which is the mechanism this variant depends on.

### Variant C — Blocked (no agents)

```
User-agent: *
Disallow: /
```

*Trade-off:* the strongest statement robots can make, and a real
cost: assistants cannot read you even when *your own customer*
asks them to. Expect to disappear from agent-mediated answers,
comparisons, and bookings — and expect the decision to be visible:
the Bot Wall Index records it. Choose this for genuinely private
surfaces (staging, internal tools), not as a default you inherited
from a plugin or a CDN toggle (see §1's managed-robots warning).

**Add Content Signals if you have a use policy, not just a fetch
policy.** Cloudflare's Content Signals Policy adds a
`Content-Signal` line to robots.txt distinguishing `search`
(building an index), `ai-input` (grounding a real-time AI answer)
and `ai-train` (training/fine-tuning) — each yes or no, absent =
no preference stated
([robots.txt setting, Cloudflare bot docs](https://developers.cloudflare.com/bots/additional-configurations/managed-robots-txt/)).
That split is what Variant B cannot express on its own: "answer
questions with my content, don't train on it" is
`Content-Signal: search=yes, ai-input=yes, ai-train=no`.

---

## 4. Publish a Web Bot Auth directory (for agent operators)

If you *operate* an agent, the reciprocal fix is yours to make:
give sites a key to verify. The standard shape — measured live in
Wave 4, where 3 of 154 major domains publish one
(`validation/wave4/DIRECTORY.md`) — is a JWKS document at
`/.well-known/http-message-signatures-directory`:

```json
{"keys":[{"crv":"Ed25519","kid":"wallcheck-wave4","kty":"OKP",
"x":"UXAV1-ndyhzViaTME9Fs97bNa2DpZc9-C0VxjSG9-yg"}],
"purpose":"Web Bot Auth"}
```

(That is wallcheck's own Wave 4 sample,
`validation/wave4/sample-directory.json`. OpenAI's production
document adds `use: "sig"`, a validity window (`nbf`/`exp`), a
top-level `purpose` and `signature_agent` URL — the reference
profile, verified field-by-field in Wave 5.)

With wallcheck, the whole flow is three commands:

```
wallcheck keygen --alg ed25519 --keyid your-agent-name \
    --out agent-key.json        # keep this file secret; 0600
python3 -c "from wallcheck.sign import load_key, \
    directory_document; import json; \
    print(json.dumps(directory_document(load_key('agent-key.json'))))"
                                # serve this JSON at the well-known path
wallcheck probe https://anysite.example --sign agent-key.json
                                # every request now carries an
                                # RFC 9421 signature, tag="web-bot-auth"
```

Then register: Cloudflare's verified-bot program accepts Web Bot
Auth as a validation method, via the BotBase submission form in
the dashboard; approval lists the agent in Cloudflare's bots and
agents directory, and submissions are tracked under BotBase →
Submission history
([Verified bots](https://developers.cloudflare.com/bots/concepts/bot/verified-bots/)).
Registration is what turns "a key exists" into
`cf.bot_management.signed_agent` lighting up at the edge (§1) —
Wave 5 measured that an *unregistered* key changes no verdict
anywhere yet (`validation/wave5/SIGNED-EXPERIMENT.md`), which is
the gap this step closes.

Key hygiene, briefly: one key per agent identity, a `kid` that
names it, rotate on a schedule and publish the successor before
retiring the predecessor (a directory can list several keys), and
never let the private seed anywhere near a repository.

---

## 5. The appeal path — the campaign's ask

Every fix above is mechanical. This one is a promise, and it is
the campaign's central ask of every platform in the Index:

**When your wall stops a legitimate agent, give it somewhere to
appeal — and answer.**

Concretely:

1. **Publish a contact that reaches a human.** A
   `/.well-known/security.txt` (RFC 9116) with a working contact
   is the established shape; an "agent access" line in your
   llms.txt or a comment in robots.txt costs nothing:
   `# Agent access questions: agents@example.com`.
2. **Name the wall in the refusal.** A 403 page that states the
   vendor, a reference ID, and the appeal contact converts a dead
   end into a bug report. Cloudflare already includes a ray ID;
   most custom deny pages include nothing.
3. **Log and review false positives on a cadence.** The verified
   agent you challenged this week is next week's integration
   partner. If your vendor offers verified/signed-agent signals
   (§1), a weekly glance at "verified agents challenged" is a
   one-line report.
4. **Say what would have worked.** If the answer is "use our
   API," the wall page should link the API. The Index's
   front-doors research (`campaign/FRONT-DOORS.md`) found that on
   most walled platforms a sanctioned route exists — it is simply
   never mentioned at the wall.

---

## 6. Verify the fix

```
wallcheck audit yourdomain.com     # the six checks, graded
wallcheck probe https://yourdomain.com            # the front door
wallcheck probe https://yourdomain.com/llms.txt   # the map
```

Re-run after every CDN, WAF, or robots change — the Index re-runs
on a cadence too, and a fixed wall gets visibly credited in it
(`INDEX.md`, history in `validation/wave4/history.jsonl`). That is
the campaign's whole bargain: walls are measured, fixes are
measured, and both are on the record.

## 7. Wave 8: the two-step signed-agent fix, the API-surface fix, and a worked C → B

Wave 7's audit sweep (92 most-walled domains, `validation/wave7
/AUDITS-SWEEP.md`) found five systemic mistakes. Two of them need
kit sections of their own, because the obvious single fix does not
work.

### 7a. The signed-agent fix has two steps, and one without the other is nothing

The sweep graded signed_agents FAIL on **92 of 92** domains — but
read that number with its selection effect: the sweep covers
walled domains, and the census (`validation/wave7/DIRECTORY-2.md`)
is the adoption measure (4 adopters in 499). The sharper finding is
the census's: **71 domains wall the directory path itself.** An
agent operator who publishes a directory (§4) but whose *own* wall
blocks `/.well-known/http-message-signatures-directory` has built a
door and bricked over the keyhole — and, symmetrically, a site owner
who exempts the path (§1, Step 3) but never publishes a directory
has opened a keyhole with no key in it.

So the fix is two steps, in order:

1. **Publish the directory** (§4): a JWKS document at the
   well-known path, with `use: "sig"`, a validity window, and a
   `purpose` — the OpenAI reference profile, not bare keys.
2. **Let the path through your own wall ruleset** (§1, Step 3):
   add the well-known path to the same Skip/Allow rule as
   robots.txt and llms.txt, *above* your challenge rules, and
   verify with `wallcheck probe
   https://yourdomain.com/.well-known/http-message-signatures-directory`
   — a 200 with JSON, not a challenge page and not a 404.

Verify both halves separately. A directory that only your own
dashboard can fetch is not published; a path exemption with no
directory behind it is not a fix. Wave 7's sweep could not grade
either half PASS on any walled domain — that is the size of the
gap, and why this section exists.

### 7b. The API-surface fix: a portal page is not a spec

The sweep graded api PASS on **0 of 92** domains; 83 FAIL, 9 WARN —
and every WARN is the same shape: "a developer portal page serves,
but no machine-readable API spec was discovered" (etsy, huggingface,
sendgrid, census.gov, chicagotribune, energy.gov, reddit, typeform,
usps). Agents do not integrate against marketing pages. The fix:

1. **Publish an OpenAPI document at a conventional path:**
   `/openapi.json` (or `/api/openapi.json` — but then link it from
   the portal; the audit checks conventional paths first).
   OpenAPI 3.x, served as `application/json`, with real paths —
   not a 200 that returns your SPA shell (the audit records
   OPENAPI_NOT_SPEC for that shape, and our own Clipwise does
   exactly this today).
2. **Link it from the developer portal** with an anchor an agent
   can find (`rel="api"`, or a literal "OpenAPI" link in the page
   header). A spec nobody can discover scores the same as no spec.
3. **Keep it honest:** the spec must describe the endpoints that
   actually answer. A stale spec is worse than a portal page, for
   the same reason a stale llms.txt is (§2).

Note what this section does *not* ask for: it does not ask a site
with no API to invent one. If you have no programmatic surface,
the honest audit outcome is api FAIL with a front-doors entry that
says so (`campaign/FRONT-DOORS.md`) — a documented absence beats a
fake spec. The fix here is for the nine WARN domains that already
*have* an API and only lack the machine-readable description of it.

### 7c. Worked example: huggingface.co, C (7/12) → B (10/12) → A (12/12)

Wave 7's sweep graded huggingface.co **C, 7 of 12** — one of only
three C grades in the sweep, and the cleanest teaching example
because its failures are all fixable without touching its wall
policy:

| Check | Wave 7 result | Fix | New score |
| --- | --- | --- | --- |
| robots_txt | PASS — served, no tracked agent blocked; sitemap declared | Nothing | 2 |
| llms_txt | FAIL — behind a CHALLENGED wall (AWS WAF) | Serve a real llms.txt as static text; exempt the path from the WAF (§1 Step 3, §2) | 2 |
| sitemap | PASS — XML, via robots declaration | Nothing | 2 |
| feed | PASS — homepage advertises /blog/feed.xml | Nothing | 2 |
| api | WARN — developer portal serves, no machine-readable spec | Publish /openapi.json and link it from the portal (§7b) | 1 → 2 |
| signed_agents | FAIL — directory path behind a CHALLENGED wall (AWS WAF) | Publish the directory AND exempt the path (§7a) | 0 → 2 |

Arithmetic, with the kit's thresholds (A ≥ 11, B ≥ 9, C ≥ 7):

- **Today: 7/12 = C** (2 + 0 + 2 + 2 + 1 + 0).
- **Fix llms.txt alone: 9/12 = B.** One static file, exempted
  from the WAF, moves the grade a full letter — the cheapest B on
  the board, and the reason §2 leads with the soft-404 warning.
- **Fix llms.txt + the API spec: 10/12 = B**, with room to spare.
- **Fix llms.txt + the directory (both steps): 11/12 = A.**
- **Fix all three: 12/12 = A.**

The lesson generalizes: on a domain that already passes robots,
sitemap, and feed, the entire distance from C to A is three
mechanical moves — a text file, a JSON spec, and a key directory —
none of which requires weakening the wall on any authenticated or
abuse-prone surface. The wall on huggingface.co's homepage can stay
exactly as it is; the grade moves because the *machine* surfaces
stop being collateral damage.

**This kit, applied to its authors (Wave 8 re-audit, 2026-10-24).** **This kit, applied to its authors (Wave 8 re-audit, 2026-10-24).**
Wave 8 re-ran `wallcheck audit` on all three own properties, and
nothing has moved on its own:

| Property | Grade | robots | llms | sitemap | feed | api | signed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| clipwise.replit.app | D (5/12) | PASS | FAIL (soft-404) | WARN (200, not XML) | WARN | FAIL | WARN (200, not JWKS) |
| reneturcios.replit.app | F (3/12) | FAIL (404) | WARN (honest 404) | WARN (404) | WARN | FAIL | FAIL (404) |
| cloudcorprecords.github.io | F (3/12) | FAIL (404) | WARN (honest 404) | WARN (404) | WARN | FAIL | FAIL (404) |

Two Wave 8 findings correct the Wave 5 record:

1. **The staged three-file deploy no longer buys a B on the
   portfolio site.** Wave 5's `fix-kit/README.md` promised the
   portfolio site would rise "from F to at least B." Under the
   current scoring that is wrong: robots FAIL→PASS (+2), llms
   WARN→PASS (+1), sitemap WARN→PASS (+1) takes it from 3 to **7
   = C**, with feed WARN, api FAIL, and signed_agents FAIL still
   open. B (≥9) additionally requires the feed (+1 → 8, still C)
   *and* the signed-agent directory (+2 → 10). The README's claim
   is corrected to C in this wave; the directory step (§7a) is
   what stands between the staged fixes and a B. For Clipwise the
   same deploy takes it from 5 to **8 = C** (llms FAIL→PASS +2,
   sitemap WARN→PASS +1, robots already PASS).
2. **The third property was never staged.** Wave 5 staged fixes for
   the two Replit properties only; cloudcorprecords.github.io has
   no staged files in `fix-kit/`, and its problem is bigger than
   three files — the Pages root itself 404s, so the fix is a real
   site (index + machine files), not a file drop. That staging is
   still open, and is recorded here rather than papered over.

One new nuance, measured, not assumed: Clipwise's signed_agents
check now reads WARN (DIRECTORY_UNPARSEABLE) rather than FAIL —
the SPA catch-all answers the well-known path with 200 and the app
shell, so the audit distinguishes "answers but not JWKS" from
"absent." The staged llms.txt and sitemap.xml in `fix-kit/` are
still current (verified present this wave: both properties' three
files intact, content written from the sites' own text). They are
still staged, not deployed: neither app's source exists in the
campaign's workspace — both live only on Replit — so the deploy is
a short manual step inside each Repl, and the re-audit after it is
the receipt we will publish against our own names first.
