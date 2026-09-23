# Catalog field audit (issue #8, map #6)

Source: read-only queries against `data/loot.db` (snapshot scraped 2026-05-02) plus `src/item_normalizer/models.py` and the schema in `src/item_db/schema.py`. All counts below are from that DB.

## Headline

- The catalog holds **80 Named Items**, all scraped in one 3-minute run. `data/queue.db` `scrape_queue` shows 80 `complete` and **4,993 `pending`**, so the full catalog is roughly 5,000+ pages and the current DB is about 1.6% of it. Every completeness figure below is a sample and may not hold at scale.
- Reliable: name, wiki_url, minimum_level, binding, material, enchantments (as text), weapon/armor stats.
- Unreliable or missing: item_type and slot for weapons, quest, named sets (empty), and enchantment values.

## Per dimension

| Dimension | Present? | Completeness (of 80) | Problems |
|---|---|---|---|
| Quest | `source_quests` (149 rows, 63 distinct strings) | 79 items have at least one row; 1 has none | Free-text wiki prose, not a quest reference. 41 items have a junk-only value ("End Chest" 14, "End chest" 13, "End reward" 8, "end chest" 4, ...). Chest notes live in the quest field, e.g. "Tahmael 's chest", "Stellite 's Chest (Rare encounter)". Case and spacing variants ("Bulat 's" vs "Dackle's"). No quest level, adventure pack or difficulty. |
| Level | `minimum_level` | 78 have it (range 5 to 23, 9 distinct values); 2 null | Minimum level only. There is no ML (item/crafting level) field. |
| Slot | `slot` | 17 have it (Eye 4, Neck 3, Head 3, Trinket 2, Hand 2, Wrist 1, Feet 1, Back 1); **63 null** | All 49 weapons and 13 armor items plus 1 other have null slot. Slot is only populated for the jewelry and clothing pages. Weapon and armor slot must be derived from the type. |
| Set | `named_sets`, `item_named_set`, `set_bonuses` | **0 sets, 0 rows in all three tables** | Schema and model exist but the sample yielded nothing. Set membership is unproven against real data. Needs checking against the parser and a wiki page known to have a set. |
| Enchantments | `enchantments` (561 rows, 77 items, 216 distinct names) | 77 of 80 items have at least one; 3 have none | See below. |
| Item type | `item_type` and `weapon_stats.weapon_type` / `armor_stats.armor_type` | `item_type` set on 17 items only; weapon_type on 49 of 49; armor_type on 13 of 13 (2 blank) | Two parallel type fields. `item_type` is a compound string ("Jewelry / Goggles", "Clothing / Helm"), weapon_type is "Scimitar / Slashing weapons" (type and damage class fused). No single clean facet. |

### Enchantments

- **382 of 561 rows have a null value; 179 have a value.** Values are parsed only when the wiki text has a leading `+N`-style number; numbers embedded in the name are not extracted. 44 null-value rows end in a digit ("Holy Burst 4", "Undead Bane 4", "Coruscating 4", "Heightened Awareness 4"), and "Tendon Slice 10%" and "Exceptional Fortification (+10%)" also carry their value in the name.
- Value distribution is dominated by 10 (47), 4 (34), 5 (26), 3, 6, and 120 (8, likely a charge or duration figure, not a bonus).
- Names are not normalised: "+5 Enhancement Bonus" is stored as a name with a null value (25 rows for +6, 19 for +5), and "+7 Enhancement Bonus → +8 Enhancement Bonus" (10 rows with an arrow) encodes a tiered upgrade in one string.
- Scrape noise is stored as enchantments: "One of the following" (12), "Mythic Weapon Boost +2 or" (29, truncated), "Attuned by Heroism" (28), "Attuned to Heroism Attuned by Heroism" (7), "Adds Red Augment Slot" and "Red Augment Slot" (both present), "Silver , Alchemical" (a material split with a stray space). 47 rows match the "or" / "One of the following" choice pattern.
- 34 items carry a Mythic enchantment string. That is a wiki-side option list, not a Customisation, so it must not be confused with Mythic values a User records on an Item Instance.
- Implication for "enchantment with value" search: filtering by name plus numeric value will fail for most rows without a re-parse that splits name from value and drops the noise rows.

### Other fields

- `required_race`: 9 blank, 66 "None", 5 "Warforged". `required_class`: **null for all 80** (column is dead in this sample).
- `binding`: 6 distinct values, with a variant "Bound to Account on Acquire , Exclusive" (5) that fuses binding and exclusivity, and 1 null.
- `material` 1 null (14 distinct); `hardness` 2 null; `durability` 2 null; `base_value` 1 null; `weight` 5 null; `flavor_text` 0 null.
- `item_source.chest` and `crafted_by`: **0 populated** out of 79 rows. `source_dropped_by`: **0 rows**. Only quests are populated.

## Count, duplicates, renames, identity

- **Count:** 80 items; 80 distinct `wiki_url`; 0 case-insensitive duplicate names; 0 names with a parenthetical disambiguator.
- **Duplicates and renames:** none in this sample, but the schema cannot detect a rename. `items.name` is `UNIQUE` and is the upsert key (`ItemRepository.upsert` matches by name). If the wiki renames a page, a re-scrape inserts a new row and orphans the old one, and any Inventory referencing it would be orphaned too.
- **Stable identifier:** none. Candidates:
  - `items.id` is an AUTOINCREMENT integer local to one database file. It is not stable across a rebuild or between the bundled catalog and a fresh scrape.
  - `name` is unique but mutable.
  - `wiki_url` is `https://ddowiki.com/page/Item:<Name>`, derived from the name (percent-encoded), so it changes on a rename as well.
  - The wiki's numeric page ID or revision ID is **not captured** anywhere in the schema. Nothing in the `wiki_api` scraping path stores it.
  - Recommendation for the spec: add an immutable catalog key (wiki page ID, or a generated slug that is assigned once and kept through renames) and store the current name as an attribute, before any Inventory row references an item.
- Other gaps for sync: no `deleted` or `superseded_by` marker, and `scraped_at` is the only version signal.

## What to plan around

1. Treat the 80-item sample as a schema and parser check, not a completeness check. Re-audit after the full ~5,000-page scrape.
2. Weapon and armor slot, and a single item-type facet, need a derivation or normalisation step.
3. Quest needs a cleanup pass (strip chest and reward prose, split quest from note, canonicalise case and spacing), or a separate quest reference table.
4. Enchantments need re-parsing (name and value split, noise removal, tier and option-list handling) before structured enchantment filters are possible.
5. Sets are entirely unverified.
6. Add a stable item key.
7. ML and Quest level are absent from the model, so the "level" filter is minimum level only unless the parser is extended.
