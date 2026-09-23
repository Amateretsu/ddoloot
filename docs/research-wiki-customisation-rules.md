# Research: does ddowiki.com expose Customisation rules and data cleanly? (#7)

Status: PARTIAL. Direct primary-source verification was blocked (see Blocker). Claims below are marked
[snippet] (secondary: search-engine summary of ddowiki pages) or [unverified].
A follow-up must re-check them from a browser or an allowed client before the rules engine is specified.

## Blocker

Every scripted request to ddowiki.com (`/page/...`, `index.php?...&action=raw`, `api.php`) returns
HTTP 202, empty body, header `x-amzn-waf-action: challenge` (AWS WAF JS challenge), tested 2026-09-23
with curl and with a generic fetch tool. So the MediaWiki raw/API endpoints could not be read, and I did
not attempt to bypass the challenge. Implication for the project: the existing `ddowiki_scraper` may
also hit this challenge; this is a risk to the catalog-build pipeline itself, independent of #7.

## What appears to exist (pages found via search; content not fetched)

- Mythic Boost / Mythic Weapon Boost / Category:Mythic Armor Boost items: https://ddowiki.com/page/Mythic_Boost
- Reaper bonus: https://ddowiki.com/page/Reaper_bonus ; Reaper Forge: https://ddowiki.com/page/Reaper_Forge
- Category:Bonus types: https://ddowiki.com/page/Category:Bonus_types
- Item pages (e.g. https://ddowiki.com/page/Item:The_Reaper_of_Lives) list augment slots by colour.

## Claims (secondary, unverified against wikitext)

- Mythic bonus values by type: weapons, armor, shields +2 or +4 (+4 rarer); clothing and jewelry +1 or +3
  (+3 rarer). This matches the rule already stated in map #6. [snippet]
- Mythic bonus kind by slot: weapons, belts, gloves, goggles, rings, trinkets give Melee/Ranged/Universal
  Spell Power; armor, boots, bracers, cloaks, headwear, necklaces, shields give Physical/Magical Resistance
  Rating; orbs, rune arms, collars may be shield and/or weapon boost. [snippet]
- Augment slot colours appear on individual item pages (e.g. orange and purple on The Reaper of Lives), so
  per-item slot colours are likely already in the item page wikitext the scraper reads. [unverified]

## Answers to the question (provisional)

| Data | Likely source | Structured? | Confidence |
|---|---|---|---|
| Mythic bonus values by item type | Mythic Boost page | Probably prose + tables; small, stable | low-medium |
| Reaper bonus options | Reaper bonus / Reaper Forge pages | Unknown | low |
| Augment slot colours per item | Item pages | Likely per-item, scrapeable | medium |
| Augments that fit each colour | Augment/colour category pages | Unknown | low |

Working recommendation: treat the Mythic rules (tiny, stable) as hand-curated data in the repo, cited to the
wiki page; scrape slot colours per item with the existing pipeline; decide on Reaper options and
colour-to-augment lists only after a browser-based or allowed-client read of the pages above. Gaps:
completeness, format (wikitext tables vs templates vs prose), and whether MediaWiki `action=raw`/`api.php`
are usable at all.

## Follow-up needed

1. A human (or allowed client) opens the pages above, saves wikitext, and records table/template structure.
2. Confirm whether ddowiki permits scripted access for the project's scraper (contact admins, check robots.txt).
