# Launch post — wallcheck

*Draft for Rene's channels. Numbers refreshed at the
ship-readiness pass (2026-10-24) against the 500-site Index,
rounds 1–24. Post as-is or cut from the top.*

---

## Main post (~340 words)

I built wallcheck because Cloudflare ate my afternoon.

The task was nothing. Publish two portfolio drafts on my own Upwork
account. I was sitting right there, directing my agent, approving
every step. Cloudflare's wall cycled the browser through ten
environments, killed every file upload bound to them, and burned
hours — without ever saying, in any form a machine could read, what
it was or why it was stopping me. A human with my password walks in.
My agent, doing exactly what I asked, gets treated like an attack.

So I stopped trying to work around it and built the tool that names
it.

**wallcheck** probes a URL once — honestly, with its own user agent,
no spoofing, no CAPTCHA tricks — and tells you what actually stops an
agent: OPEN, CHALLENGED, WALLED, LOGIN_GATED, RATE_LIMITED. It names
the vendor and shows the evidence. Deterministic, no LLM in the
verdict. Same response in, same verdict out — 885 tests pin the
verdicts.

Then I pointed it at the web and published the results as the
**Bot Wall Index** — 500 sites now. 415 open. 62 walled or
challenged, and Akamai alone operates 22 of the 37 hard walls.
And the category that hit me wasn't banking or health — it was
**freelance**: 4 of the 13 platforms that exist to connect
workers with clients stop a worker's agent at the door. Upwork
hard-blocks (Cloudflare). Fiverr challenges (PerimeterX). Guru
hard-blocks (Imperva). Gun.io hard-blocks (Cloudflare). Contra,
serving the same market, just works. (The only harder beat in
the index is travel — 9 of 19 airlines, hotels, and rail sites
wall or throttle agents.) The wall is a choice, and now it's a
measured one.

This is not a bypass tool, and it never will be. No CAPTCHA solving,
no fingerprint games. The fight is lawful and it's three moves:
**measure** the walls in public, **sign** our agents so they have an
identity worth trusting (Web Bot Auth, RFC 9421 — the standard
Cloudflare itself co-wrote; today only 4 of 500 sites publish a
key directory, and ChatGPT's is the maintained reference — its
expiry has renewed forward every time we've re-checked), and
**document the front doors** —
the official APIs and feeds — so legitimate work has a sanctioned
route on every platform. We've logged 66 platforms so far: 40
with a verified sanctioned route, 20 where we found none.

Two asks.

**Site owners:** check your wall. `wallcheck probe yoursite.com`.
Half of these walls are defaults nobody chose, sitting in front of
pages you want read.

**Agent builders:** sign your requests. Anonymous traffic is
unjudgeable traffic. Give the walls an identity they can hold
accountable — and then hold them accountable when they block it
anyway.

The Index re-scans weekly. Walls that come down get credited in it.
Walls that stay up get famous.

— Rene Turcios, SF. Builder of Clipwise and Greenlight. Currently
at war, lawfully.

---

## Threads version (3 posts)

**1/3**
Cloudflare ate my afternoon. Ten browser environments, dead file
uploads, hours gone — to publish two portfolio drafts on my OWN
Upwork account, with me sitting there directing it. So I built the
tool that names the wall: **wallcheck**. One honest probe. It tells
you exactly what stops your agent, whose wall it is, and shows the
evidence.

**2/3**
Then I measured 500 sites and published the Bot Wall Index. 415
open, 62 walled/challenged — and freelance, my own beat, puts 4
of its 13 platforms behind a wall or a challenge: Upwork
(Cloudflare), Fiverr (PerimeterX), Guru (Imperva), Gun.io
(Cloudflare). Contra just serves. The wall is a choice. Now
it's data.

**3/3**
This is not a bypass tool. No CAPTCHA solving, no spoofing, ever.
The fight is lawful: measure in public, sign our agents (Web Bot
Auth, RFC 9421), document every official front door. Site owners —
probe your own site. Agent builders — sign your requests. The Index
re-scans weekly. Walls that come down get credited. Walls that stay
up get famous.
