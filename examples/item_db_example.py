"""Examples for the item_db package.

Demonstrates how to use ItemRepository to persist, query, and manage DDOItem
objects in a SQLite database.

Most examples use ":memory:" — an in-memory SQLite database that exists only
for the duration of the script and produces no file on disk. Example 9 uses a
real file (examples/loot.db) to demonstrate cross-connection persistence.

Run from the project root with:
    python examples/item_db_example.py
"""

import sys
from datetime import datetime, timezone
from pathlib import Path

from loguru import logger

from item_db import ItemFilter, ItemRepository
from item_db.exceptions import DuplicateItemError, ItemNotFoundError
from item_normalizer.models import (
    ArmorStats,
    DDOItem,
    Enchantment,
    ItemSource,
    NamedSet,
    SetBonus,
    WeaponStats,
)


# Silence debug/info noise so example output is clean.
logger.remove()
logger.add(sys.stderr, level="WARNING")


# ---------------------------------------------------------------------------
# Sample DDOItem objects
# ---------------------------------------------------------------------------

_TS = datetime(2026, 1, 1, tzinfo=timezone.utc)

CLOAK = DDOItem(
    name="Mantle of the Worldshaper",
    item_type="Cloak",
    slot="Back",
    minimum_level=20,
    binding="Bound to Character on Acquire",
    material="Cloth",
    hardness=14,
    durability=100,
    base_value="12,650 gp",
    weight=0.1,
    flavor_text="This cloak was woven from the fabric of the planes themselves.",
    wiki_url="https://ddowiki.com/page/Item:Mantle_of_the_Worldshaper",
    scraped_at=_TS,
    enchantments=[
        Enchantment(name="Superior Devotion", value="VI"),
        Enchantment(name="Resistance", value="+5"),
        Enchantment(name="Metalline"),
        Enchantment(name="Good Luck", value="+2"),
    ],
    named_set=NamedSet(
        name="Thelanis Fairy Tale",
        bonuses=[SetBonus(pieces_required=2, description="+1 artifact bonus to all saves")],
    ),
    source=ItemSource(quests=["The Snitch", "The Spinner of Shadows"]),
)

SWORD = DDOItem(
    name="Sword of Shadow",
    item_type="Weapon",
    slot="Main Hand",
    minimum_level=15,
    binding="Bound to Character on Equip",
    hardness=18,
    durability=150,
    base_value="8,400 gp",
    weight=4.0,
    wiki_url="https://ddowiki.com/page/Item:Sword_of_Shadow",
    scraped_at=_TS,
    enchantments=[
        Enchantment(name="Vorpal"),
        Enchantment(name="Improved Critical", value="Slashing Weapons"),
        Enchantment(name="Shadowstrike", value="+3"),
    ],
    weapon_stats=WeaponStats(
        damage_dice="1d8",
        damage_bonus=5,
        damage_type=["Slashing", "Magic"],
        critical_range="19-20",
        critical_multiplier=2,
        enchantment_bonus=5,
        handedness="One-Handed",
        proficiency="Martial Weapon Proficiency",
        weapon_type="Longsword",
    ),
    source=ItemSource(quests=["The Pit"]),
)

PLATE = DDOItem(
    name="Plate of the Fallen",
    item_type="Armor",
    slot="Body",
    minimum_level=18,
    binding="Bound to Character on Acquire",
    material="Mithral",
    hardness=20,
    durability=200,
    base_value="24,000 gp",
    weight=50.0,
    flavor_text="Forged from the armor of a fallen celestial, it pulses with divine energy.",
    wiki_url="https://ddowiki.com/page/Item:Plate_of_the_Fallen",
    scraped_at=_TS,
    enchantments=[
        Enchantment(name="Greater Fortification"),
        Enchantment(name="Fortification", value="+150%"),
    ],
    armor_stats=ArmorStats(
        armor_type="Heavy",
        armor_bonus=9,
        max_dex_bonus=3,
        armor_check_penalty=-3,
        arcane_spell_failure=25,
    ),
)

RING = DDOItem(
    name="Ring of the Stalker",
    item_type="Ring",
    slot="Finger",
    minimum_level=12,
    binding="Bound to Character on Acquire",
    wiki_url="https://ddowiki.com/page/Item:Ring_of_the_Stalker",
    scraped_at=_TS,
    enchantments=[
        Enchantment(name="Resistance", value="+3"),
        Enchantment(name="Hide", value="+10"),
        Enchantment(name="Move Silently", value="+10"),
    ],
    named_set=NamedSet(name="Thelanis Fairy Tale"),
    source=ItemSource(quests=["The Spinner of Shadows"]),
)

ALL_ITEMS = [CLOAK, SWORD, PLATE, RING]


# ---------------------------------------------------------------------------
# Example 1: Open a database and save items
# ---------------------------------------------------------------------------

def example_save_and_count() -> None:
    print("=" * 60)
    print("Example 1: save() and count()")
    print("=" * 60)

    with ItemRepository(":memory:") as repo:
        for item in ALL_ITEMS:
            repo.save(item)

        print(f"Total items saved : {repo.count()}")
        print(f"All names         : {repo.list_names()}")


# ---------------------------------------------------------------------------
# Example 2: Retrieve a single item and inspect its fields
# ---------------------------------------------------------------------------

def example_get_item() -> None:
    print("\n" + "=" * 60)
    print("Example 2: get() — full item retrieval")
    print("=" * 60)

    with ItemRepository(":memory:") as repo:
        repo.save(SWORD)
        item = repo.get("Sword of Shadow")

        print(f"Name         : {item.name}")
        print(f"Slot         : {item.slot}")
        print(f"Min level    : {item.minimum_level}")

        ws = item.weapon_stats
        print(f"\nWeapon stats :")
        print(f"  Damage     : {ws.damage_dice}+{ws.damage_bonus}")
        print(f"  Types      : {ws.damage_type}")
        print(f"  Crit       : {ws.critical_range} / x{ws.critical_multiplier}")
        print(f"  Enh bonus  : +{ws.enchantment_bonus}")
        print(f"  Handedness : {ws.handedness}")

        print(f"\nEnchantments ({len(item.enchantments)}):")
        for enc in item.enchantments:
            value_str = f" → {enc.value}" if enc.value else ""
            print(f"  - {enc.name}{value_str}")

        print(f"\nDrops in    : {item.source.quests}")


# ---------------------------------------------------------------------------
# Example 3: Upsert — safely overwrite an existing item
# ---------------------------------------------------------------------------

def example_upsert() -> None:
    print("\n" + "=" * 60)
    print("Example 3: upsert() — insert or replace")
    print("=" * 60)

    with ItemRepository(":memory:") as repo:
        repo.save(CLOAK)
        print(f"Before upsert — minimum_level: {repo.get(CLOAK.name).minimum_level}")

        # save() would raise DuplicateItemError here; upsert() replaces cleanly
        updated = DDOItem(**{**CLOAK.model_dump(), "minimum_level": 25})
        repo.upsert(updated)

        print(f"After upsert  — minimum_level: {repo.get(CLOAK.name).minimum_level}")
        print(f"Item count still: {repo.count()}  (no duplicate created)")


# ---------------------------------------------------------------------------
# Example 4: DuplicateItemError and ItemNotFoundError
# ---------------------------------------------------------------------------

def example_error_handling() -> None:
    print("\n" + "=" * 60)
    print("Example 4: error handling")
    print("=" * 60)

    with ItemRepository(":memory:") as repo:
        repo.save(CLOAK)

        # Attempt to save again with save() — raises DuplicateItemError
        try:
            repo.save(CLOAK)
        except DuplicateItemError as exc:
            print(f"DuplicateItemError : {exc}")

        # Attempt to fetch something that does not exist
        try:
            repo.get("The Ring of Sauron")
        except ItemNotFoundError as exc:
            print(f"ItemNotFoundError  : {exc}")

        # get_or_none is the safe alternative
        result = repo.get_or_none("The Ring of Sauron")
        print(f"get_or_none        : {result}")


# ---------------------------------------------------------------------------
# Example 5: Bulk save and delete
# ---------------------------------------------------------------------------

def example_bulk_and_delete() -> None:
    print("\n" + "=" * 60)
    print("Example 5: save_many() and delete()")
    print("=" * 60)

    with ItemRepository(":memory:") as repo:
        saved, errors = repo.save_many(ALL_ITEMS)
        print(f"Bulk save: {saved} saved, {errors} errors")
        print(f"Count after bulk : {repo.count()}")

        repo.delete(RING.name)
        print(f"Count after delete: {repo.count()}")
        print(f"exists(RING)      : {repo.exists(RING.name)}")


# ---------------------------------------------------------------------------
# Example 6: search() with ItemFilter
# ---------------------------------------------------------------------------

def example_search() -> None:
    print("\n" + "=" * 60)
    print("Example 6: search() with ItemFilter")
    print("=" * 60)

    with ItemRepository(":memory:") as repo:
        repo.save_many(ALL_ITEMS)

        # Items equippable at level 15 or below
        results = repo.search(ItemFilter(minimum_level_max=15))
        print(f"Items usable at level 15 or below ({len(results)}):")
        for item in results:
            print(f"  - {item.name}  (ml={item.minimum_level})")

        # Cloaks only
        results = repo.search(ItemFilter(slot="Back"))
        print(f"\nBack slot items ({len(results)}):")
        for item in results:
            print(f"  - {item.name}")

        # Heavy armor with low arcane spell failure
        results = repo.search(ItemFilter(armor_type="Heavy", arcane_spell_failure_max=30))
        print(f"\nHeavy armor with ≤30% ASF ({len(results)}):")
        for item in results:
            print(f"  - {item.name}  (asf={item.armor_stats.arcane_spell_failure}%)")

        # One-handed longswords
        results = repo.search(ItemFilter(weapon_type="Longsword", handedness="One-Handed"))
        print(f"\nOne-handed longswords ({len(results)}):")
        for item in results:
            print(f"  - {item.name}")

        # Combined: Back slot, level ≤ 20, not class-restricted
        results = repo.search(ItemFilter(slot="Back", minimum_level_max=20, exclude_class_restricted=True))
        print(f"\nBack slot, ml≤20, no class restriction ({len(results)}):")
        for item in results:
            print(f"  - {item.name}")


# ---------------------------------------------------------------------------
# Example 7: Convenience finders
# ---------------------------------------------------------------------------

def example_finders() -> None:
    print("\n" + "=" * 60)
    print("Example 7: find_by_enchantment(), find_by_set(), find_by_quest()")
    print("=" * 60)

    with ItemRepository(":memory:") as repo:
        repo.save_many(ALL_ITEMS)

        # Items with a Resistance enchantment (partial match)
        names = repo.find_by_enchantment("Resistance")
        print(f"Items with 'Resistance' enchantment : {names}")

        # Items with Vorpal
        names = repo.find_by_enchantment("Vorpal")
        print(f"Items with 'Vorpal'                 : {names}")

        # All items in the Thelanis Fairy Tale set
        items = repo.find_by_set("Thelanis Fairy Tale")
        print(f"\nThelanis Fairy Tale set members ({len(items)}):")
        for item in items:
            print(f"  - {item.name}")

        # Items that drop in a quest matching "Spinner"
        names = repo.find_by_quest("Spinner")
        print(f"\nItems dropping in quests matching 'Spinner' : {names}")


# ---------------------------------------------------------------------------
# Example 8: Staleness check via get_scraped_at()
# ---------------------------------------------------------------------------

def example_staleness_check() -> None:
    print("\n" + "=" * 60)
    print("Example 8: get_scraped_at() — staleness check")
    print("=" * 60)

    with ItemRepository(":memory:") as repo:
        repo.save_many(ALL_ITEMS)

        now = datetime.now(timezone.utc)
        stale_threshold_days = 30

        print(f"Checking items scraped more than {stale_threshold_days} days ago:")
        for name in repo.list_names():
            ts = repo.get_scraped_at(name)
            age_days = (now - ts).days
            status = "STALE — re-scrape" if age_days > stale_threshold_days else "fresh"
            print(f"  {name:<40} age={age_days}d  [{status}]")


# ---------------------------------------------------------------------------
# Example 9: File-based database — persistent across connections
# ---------------------------------------------------------------------------

def example_file_database() -> None:
    print("\n" + "=" * 60)
    print("Example 9: file-based database — persistent across connections")
    print("=" * 60)

    db_path = Path(__file__).parent / "loot.db"

    # First connection — write items
    with ItemRepository(str(db_path)) as repo:
        repo.save_many(ALL_ITEMS)
        print(f"Database written to : {db_path}")
        print(f"File size           : {db_path.stat().st_size} bytes")
        print(f"Items saved         : {repo.count()}")

    # Second connection — prove data survived
    with ItemRepository(str(db_path)) as repo:
        print(f"\nReopened same file  : {repo.count()} items still present")
        item = repo.get(CLOAK.name)
        print(f"Retrieved           : {item.name!r}  (ml={item.minimum_level})")

    print(f"\nDB file location    : {db_path.resolve()}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    example_save_and_count()
    example_get_item()
    example_upsert()
    example_error_handling()
    example_bulk_and_delete()
    example_search()
    example_finders()
    example_staleness_check()
    example_file_database()


if __name__ == "__main__":
    main()
