# Research: Customisation rules on ddowiki.com (#7)

Sources read directly on 2026-09-23 (page text extracted from the rendered pages; wiki content is CC BY-SA 2.5, so this file summarises rather than copies):

- <https://ddowiki.com/page/Mythic_Boost> (last modified 2026-08-31, Update 81.2)
- <https://ddowiki.com/page/Reaper_bonus>
- <https://ddowiki.com/page/Reaper_Forge>
- <https://ddowiki.com/page/Augment_Slot>

Retrieval note: the pages sit behind an AWS WAF JavaScript challenge that plain HTTP clients (including the repo's `ddowiki_scraper`) do not pass. These four were fetched once, by hand, with a real headless Chrome at a 4s spacing, at the user's explicit instruction. Nothing about that was added to the codebase.

## Answer

The rules are on the wiki as **prose and small tables, not structured data**. They are small and stable enough to **hand-curate**; only per-item facts (which slots and augment colours a given item has) need scraping.

## Mythic bonus

- Magnitude is +1 to +4, and only two values are valid per item type:
  - Weapons, armor, shields: **+2 or +4** (+4 rarer).
  - Clothing and jewelry: **+1 or +3** (+3 rarer).
- What the bonus applies to depends on slot:
  - Weapons, belts, gloves, goggles, rings, trinkets: Melee, Ranged and Universal Spell Power.
  - Armor, boots, bracers, cloaks, headwear, necklaces, shields: Physical and Magical Resistance Rating.
  - Orbs, rune arms, collars: Shield and/or Weapon boost.
- Some Tomb of the Eldritch Evil (ToEE) items can carry **two** Mythic bonuses (e.g. Weapon and Shield).
- Eligibility: named chest loot (Update 34 onward, all named chest loot). Crafted, reward-only and randomly generated items cannot be Mythic, with listed crafting exceptions (ToEE, Slave Lords, Schism Shard + Threads of Fate, Dust of Mythic Power, Heirloom loot).
- Mythic and Reaper can coexist on one item.
- Mythic bonuses from all sources stack.

The user's stated rule (+2/+4 on weapons, shields, armor; +1/+3 otherwise) matches the wiki.

## Reaper bonus

Two families:

1. **Generic** (any named item, including wands; found naturally only, cannot be made at the Reaper Forge): Power +3; Physical Resistance Rating +3; Magical Resistance Rating +3.
2. **Slot-specific** (added at the Reaper Forge, 75 Reaper Fragments, onto an item in the matching slot with no existing Reaper bonus): one fixed effect each for goggles, helmet, necklace, cloak, belt, gloves, boots, bracers, armor and shield; **rings have four alternatives** (Reaper Ring Boost 1 to 4).

Constraints worth encoding:
- An item with a Reaper bonus already can only be destroyed, not re-imprinted.
- Multi-slot items (e.g. Five Rings from Slave Lords) behave unpredictably and can waste fragments.
- Some upgrades (Epic Crafting, Essence Crafting) can remove the bonus; disjunction removes it entirely.
- Slot-specific bonuses date from Update 52 (helmet earlier).

The exact effect text per slot is on the Reaper bonus page; it is a short list (about 14 entries) and changes rarely.

## Augment slots

Seven colours: Red, Blue, Yellow, Purple, Orange, Green, Colorless. Compatibility (slot colour -> augment colours that fit), from the wiki's matrix:

| Slot | Accepts |
|---|---|
| Colorless | Colorless only |
| Red | Red, Colorless |
| Blue | Blue, Colorless |
| Yellow | Yellow, Colorless |
| Purple | Blue, Purple, Red, Colorless |
| Orange | Orange, Red, Yellow, Colorless |
| Green | Blue, Green, Yellow, Colorless |

Which item types carry which slot colours: Red on weapons/shields/hand-held; Blue on armor/robes/outfits/shields/off-hand; Yellow on accessories; Purple and Orange on named weapons/shields/hand-held; Green on accessories or named armor/robes/outfits.

Exceptions the model must allow for:
- Special named items can have slot colours not normal for their type (Thirteen has one of every colour; Minor Artifacts have Blue, Green and Yellow regardless of slot).
- "Unique" augment slots (Green Steel, Slave Lords, Dinosaur Bone crafting) accept only their own system's augments and cannot take normal ones.
- Named items often have 1 slot, raid or high-level items usually 2, Minor Artifacts 3.

The augment catalogue itself (standard, purchasable, named/uncommon, essence, set augments) is listed on the Augment Slot page and linked sub-pages; not audited item by item here.

## Recommendation

- **Hand-curate** as versioned data in the repo: Mythic magnitude by item type, Mythic stat by slot, the Reaper bonus list, and the slot-colour compatibility matrix. Small, changes only with game updates.
- **Scrape per item** (from the item page): which augment slot colours it has, and whether it is eligible for a Mythic bonus. The catalog audit (#8) shows these fields are not reliably populated today.
- **Augment catalogue**: treat as a separate scrape or curation job; needs its own audit.
- Unresolved for the model: how to represent the ToEE double-Mythic items, unique-augment systems, and multi-slot items.
