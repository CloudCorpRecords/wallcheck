# Wave 14 — Adversarial Battery v6: Results

**32 shapes, 8 mismatches before fixes, 0 after.** Five genuine
defects, all fixed test-first and generalized; one fixture
correction (the classifier was right); 24 pins that held. Full
suite after fixes: **270/270** (236 prior + 34 new: 33 battery
pins/guards + 1 F7b pin). Real-capture corpus: replayed after the
fixes (see PROBLEMS.md) — no verdict/vendor change on any real
wall capture.

## Mismatches → fixes (5 defects)

| shape | pre-fix | hand | fix |
| --- | --- | --- | --- |
| F1b (form-config script JSON + visible text) | CHALLENGED / Generic | OPEN | W14-001: generic markers appearing ONLY inside `<script>` blocks are configuration, not content — suppressed when the page has visible text (≥20 chars). Content-free pages still fire (F1a/F1d pins). Applies to captcha, human-check, and JS-proof prose only; vendor markers and redirect targets keep reading scripts. |
| F3b ("Unusual traffic… Complete verification") | OPEN | CHALLENGED / Generic | W14-002: TRAFFIC_CHECK — anomaly wording (unusual traffic / suspicious activity) PLUS a verification cue (verif/captcha/prove/confirm) reads CHALLENGED. Either half alone does not fire (F3a/F3d pins). |
| F4c (403 + Retry-After + throttle wording) | WALLED | RATE_LIMITED | W14-003: Retry-After header + throttle wording + no wall signal reads RATE_LIMITED on 403/503. Header alone (F4f) and overload wording alone (F4e) do not convert; wall signals and challenges keep precedence (F4b, throttle-guard pin). |
| F4d (503 + Retry-After + throttle wording) | UNREACHABLE | RATE_LIMITED | W14-003, same rule in 503 form. |
| F6a (/sitemap.xml 200-HTML hides declared index) | WARN | PASS | W14-004: audit_site falls through the robots-declared Sitemap: lines in order until a usable sitemap document serves — not only when /sitemap.xml is non-200, and not only the first line (F6b same fix). A declared URL serving HTML is not accepted (guard pin). |
| F6b (dead first declaration hides valid second) | WARN | PASS | W14-004, same fix. |
| F7c (fragment-only llms links) | PASS | WARN | W14-005: markdown links count as index entries only when the target is non-empty and not a pure fragment (`#section` points at the file itself). Empty targets do not count (guard pin). |

## Correction, not a defect (1)

- **F5c fixture corrected** (LOGIN_GATED, None → LOGIN_GATED,
  DataDome): the first draft used `Set-Cookie: datadome=abc`,
  which no rule recognizes — the codebase's pinned DataDome
  cookie signal is literally `dd_cookie` (test_b8c). With the
  correct cookie name the classifier answers LOGIN_GATED /
  DataDome exactly as hand-classified. The hand classification
  was right; the fixture named the wrong cookie. Lesson
  restated: fixture signals must be the signals the code
  actually recognizes, not the names a vendor's marketing uses.
  No new cookie signal was invented on a guess.

## Pins that held (24 shapes)

F1a/F1d (challenge-only and spinner-only script blobs fire),
F1c (large article + script config stays OPEN via the size gate),
F2a/F2b (alt human-check fires, alt refusal stays WALLED),
F2c (article-image alt stays OPEN via the gate), F3a/F3d
(anomaly wording without a cue stays a refusal), F3c (article
about traffic checks stays OPEN via the gate), F4a (classic
429), F4b (challenge dominates throttle), F4e/F4f (Retry-After
boundaries), F5a/F5b/F5d (login + challenge-named / sensor /
Imperva cookies all stay LOGIN_GATED with established vendors),
F6c (no sitemap anywhere is WARN), F6d (sitemapindex at the
default location passes), F7a/F7b/F7d (relative-only and mixed
links pass; bare-domain-only warns), F8a/F8b/F8c (hop walls
resolve to the final resource; login hops gate).

## Notable interactions

- **W14-001 is a scope fix, not a phrase fix.** It draws the line
  the Wave 1 widget principle always implied but never stated for
  scripts: code is not content. The visible-text threshold (20
  chars) is the judgment call, documented in the code so it can
  be challenged — a spinner or "Loading..." does not count as
  content, a paragraph does. The guard pins on both sides of
  the threshold exist so the next wave can tighten it with
  evidence instead of taste.
- **W14-003 reframes RATE_LIMITED honestly.** SPEC's "HTTP 429"
  definition was narrower than the throttle concept: a server
  that says "too many" AND "retry after" on 403/503 is throttling
  you, and calling it WALLED or UNREACHABLE hides the retryable
  fact. The rule is deliberately two-keyed (header + wording)
  so neither key alone reclassifies anything — F4e/F4f prove
  both halves of that.
- **W14-004 fixes the audit's own fetch logic, not a grade
  rule.** The sitemap check was always right; the fetcher never
  gave it the declared document. Waves that only test
  `evaluate_audit` cannot catch fetch-logic gaps — F6a/F6b are
  the first battery shapes run through `audit_site` itself, and
  that level is where future audit-battery shapes should live.
- **F5/F8 are documentation batteries.** Every shape pinned, no
  defect — but the pins now record two boundaries future waves
  must not re-litigate: session cookies never change a login
  verdict, and hop bodies are not classifier inputs by
  construction (a hop wall that blocked would BE the final
  response).

## What this wave says about saturation

Battery v6 found 5 genuine defects on shapes no earlier battery
exercised — the adversarial surface is still not exhausted, and
Wave 14 is NOT a clean wave on the battery prong regardless of
Leg A's outcome. The saturation clock, reset by Wave 13, stays
reset: a clean wave needs zero defects in BOTH the battery and
the measurement round.
