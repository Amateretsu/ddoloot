# Wiki acquisition policy: polite fetch first, browser fallback, committed source

The maintainer builds the catalog from ddowiki.com, which sits behind an AWS WAF challenge (HTTP 202, `x-amzn-waf-action: challenge`). We fetch politely and identified, fall back to a real browser only for challenged pages, and commit normalized per-item JSON so CI never touches the wiki.

## Why

- Alternatives were researched (`docs/research/19-*.md`): the wiki has no known official dump or API allowance, DDO Compendium is a one-maintainer site with unclear terms and provenance, and Wayback is partial. Sourcing stays ddowiki; Compendium is parked, to be revisited if its maintainer or the wiki admins make contact.
- Solving a challenge carries legal and ethical risk (DMCA §1201, unsettled whether a WAF challenge is an access gate). It is accepted only as a bounded fallback.

## Policy

- **Plain fetch first**: identified user agent with a contact, `Crawl-delay` of at least 4s, one page at a time, `/page/...` reads only (never `/api.php` or `Special:`), stop on challenge rather than treating an empty 202 as success.
- **Browser fallback**: a challenged page is retried in a real browser. If more than 20% of a batch, or 5 consecutive fetches, are challenged, the rest of that run uses the browser. Each new run starts with plain fetching.
- **Limits on the fallback**: same identity and pace as plain fetching; no proxy or IP rotation; no CAPTCHA-solving services.
- **Admin override**: if the wiki admins say no, bulk fetching stops and the catalog grows by hand. Any agreed route (bot account, read allowance) replaces this policy.
- **Where it runs**: the maintainer runs a manual refresh command locally; CI only builds and releases from committed source (ADR 0004).
- **Committed source**: normalized JSON per Named Item at `catalog-src/items/<update>/<category>/<uuid>-<slug>.json`. `<update>` is the introduced-in update (`unknown` if absent); `<category>` is weapon, armor, shield, jewelry, clothing or other; the filename leads with the ADR 0003 UUID. Each file records page title, revision id and source URL (CC BY-SA attribution). Raw pages live in a gitignored local cache. Finer groupings (slot, level, quest, set) go in generated indexes, never directories. A corrected update or category moves the file by git rename.

## Consequences

- Wiki changes are reviewable as diffs; CI needs no wiki access.
- The catalog is only as fresh as the last manual refresh.
- Scraper build work follows: WAF-challenge detection, robots.txt parser fix, crawl-delay, browser fallback, layout writer.
