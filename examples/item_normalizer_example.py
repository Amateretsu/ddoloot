"""Examples for the item_normalizer package.

Demonstrates how to use WikiPageParser and ItemNormalizer against inline HTML
strings. No network requests are made — all HTML is defined in this file.

Run from the project root with:
    python examples/item_normalizer_example.py
"""

import json
import sys

from loguru import logger

from item_normalizer import ItemNormalizer
from item_normalizer.exceptions import ParseError
from item_normalizer.parser import WikiPageParser


# Silence debug/info noise so example output is clean.
logger.remove()
logger.add(sys.stderr, level="WARNING")


# ---------------------------------------------------------------------------
# Sample HTML strings — representative DDO Wiki item pages
# ---------------------------------------------------------------------------

CLOAK_HTML = """
<!DOCTYPE html>
<html>
<head><title>Item:Mantle of the Worldshaper - DDO wiki</title></head>
<body>
<div id="mw-content-text">
  <h1 id="firstHeading">Item:Mantle of the Worldshaper</h1>
  <div class="mw-parser-output">
    <table class="wikitable">
      <tr><th colspan="2">Mantle of the Worldshaper</th></tr>
      <tr><th>Item Type</th><td>Cloak</td></tr>
      <tr><th>Equips To</th><td>Back</td></tr>
      <tr><th>Minimum Level</th><td>20</td></tr>
      <tr><th>Binding</th><td>Bound to Character on Acquire</td></tr>
      <tr><th>Material</th><td>Cloth</td></tr>
      <tr><th>Hardness</th><td>14</td></tr>
      <tr><th>Durability</th><td>100</td></tr>
      <tr><th>Base Value</th><td>12,650 gp</td></tr>
      <tr><th>Weight</th><td>0.1 lbs</td></tr>
      <tr><th>Named Set</th><td>Thelanis Fairy Tale</td></tr>
      <tr><th>Location</th><td>The Snitch, The Spinner of Shadows</td></tr>
    </table>
    <p><b>Enchantments:</b></p>
    <ul>
      <li>Superior Devotion VI</li>
      <li>Resistance +5</li>
      <li>Metalline</li>
      <li>Good Luck +2</li>
    </ul>
    <p><i>This cloak was woven from the fabric of the planes themselves.</i></p>
  </div>
</div>
</body>
</html>
"""

WEAPON_HTML = """
<!DOCTYPE html>
<html>
<head><title>Item:Sword of Shadow - DDO wiki</title></head>
<body>
<div id="mw-content-text">
  <h1 id="firstHeading">Item:Sword of Shadow</h1>
  <div class="mw-parser-output">
    <table class="wikitable">
      <tr><th colspan="2">Sword of Shadow</th></tr>
      <tr><th>Item Type</th><td>Weapon</td></tr>
      <tr><th>Weapon Type</th><td>Longsword</td></tr>
      <tr><th>Equips To</th><td>Main Hand</td></tr>
      <tr><th>Minimum Level</th><td>15</td></tr>
      <tr><th>Handedness</th><td>One-Handed</td></tr>
      <tr><th>Proficiency</th><td>Martial Weapon Proficiency</td></tr>
      <tr><th>Damage</th><td>1d8+5</td></tr>
      <tr><th>Damage Type</th><td>Slashing, Magic</td></tr>
      <tr><th>Critical Roll</th><td>19-20/x2</td></tr>
      <tr><th>Enhancement Bonus</th><td>5</td></tr>
      <tr><th>Binding</th><td>Bound to Character on Equip</td></tr>
      <tr><th>Hardness</th><td>18</td></tr>
      <tr><th>Durability</th><td>150</td></tr>
      <tr><th>Base Value</th><td>8,400 gp</td></tr>
      <tr><th>Weight</th><td>4 lbs</td></tr>
      <tr><th>Location</th><td>The Pit</td></tr>
    </table>
    <p><b>Enchantments:</b></p>
    <ul>
      <li>Vorpal</li>
      <li>Improved Critical: Slashing Weapons</li>
      <li>Shadowstrike +3</li>
    </ul>
  </div>
</div>
</body>
</html>
"""

ARMOR_HTML = """
<!DOCTYPE html>
<html>
<head><title>Item:Plate of the Fallen - DDO wiki</title></head>
<body>
<div id="mw-content-text">
  <h1 id="firstHeading">Item:Plate of the Fallen</h1>
  <div class="mw-parser-output">
    <table class="wikitable">
      <tr><th colspan="2">Plate of the Fallen</th></tr>
      <tr><th>Item Type</th><td>Armor</td></tr>
      <tr><th>Armor Type</th><td>Heavy</td></tr>
      <tr><th>Equips To</th><td>Body</td></tr>
      <tr><th>Minimum Level</th><td>18</td></tr>
      <tr><th>Binding</th><td>Bound to Character on Acquire</td></tr>
      <tr><th>Material</th><td>Mithral</td></tr>
      <tr><th>Armor Bonus</th><td>9</td></tr>
      <tr><th>Maximum Dex Bonus</th><td>3</td></tr>
      <tr><th>Armor Check Penalty</th><td>-3</td></tr>
      <tr><th>Arcane Spell Failure</th><td>25%</td></tr>
      <tr><th>Hardness</th><td>20</td></tr>
      <tr><th>Durability</th><td>200</td></tr>
      <tr><th>Base Value</th><td>24,000 gp</td></tr>
      <tr><th>Weight</th><td>50 lbs</td></tr>
    </table>
    <p><b>Enchantments:</b></p>
    <ul>
      <li>Greater Fortification</li>
      <li>Fortification +150%</li>
    </ul>
    <p><i>Forged from the armor of a fallen celestial, it pulses with divine energy.</i></p>
  </div>
</div>
</body>
</html>
"""

WIKI_URL_BASE = "https://ddowiki.com/page/Item:"


# ---------------------------------------------------------------------------
# Example 1: Raw field extraction with WikiPageParser
# ---------------------------------------------------------------------------

def example_raw_parser() -> None:
    """Show the raw dict returned by WikiPageParser before normalization."""
    print("=" * 60)
    print("Example 1: WikiPageParser — raw field extraction")
    print("=" * 60)

    parser = WikiPageParser()
    fields = parser.parse(CLOAK_HTML, wiki_url=f"{WIKI_URL_BASE}Mantle_of_the_Worldshaper")

    print(f"Item name  : {fields['name']}")
    print(f"Min level  : {fields['minimum_level']!r}  (still a string)")
    print(f"Slot       : {fields['slot']!r}")
    print(f"Named set  : {fields['named_set_raw']!r}")
    print(f"Enchants   : {fields['enchantments']}")
    print(f"Flavor text: {fields['flavor_text']!r}")


# ---------------------------------------------------------------------------
# Example 2: Full normalization of a cloak (accessory)
# ---------------------------------------------------------------------------

def example_normalize_cloak() -> None:
    """Normalize a cloak item and inspect typed fields."""
    print("\n" + "=" * 60)
    print("Example 2: ItemNormalizer — cloak / accessory")
    print("=" * 60)

    normalizer = ItemNormalizer()
    item = normalizer.normalize(CLOAK_HTML, wiki_url=f"{WIKI_URL_BASE}Mantle_of_the_Worldshaper")

    print(f"Name          : {item.name}")
    print(f"Slot          : {item.slot}")
    print(f"Minimum level : {item.minimum_level}  (int, not string)")
    print(f"Binding       : {item.binding}")
    print(f"Material      : {item.material}")
    print(f"Hardness      : {item.hardness}")
    print(f"Durability    : {item.durability}")
    print(f"Weight        : {item.weight} lbs")
    print(f"Flavor text   : {item.flavor_text!r}")

    print(f"\nEnchantments ({len(item.enchantments)}):")
    for enc in item.enchantments:
        value_str = f" ({enc.value})" if enc.value else ""
        print(f"  - {enc.name}{value_str}")

    if item.named_set:
        print(f"\nNamed set: {item.named_set.name}")

    if item.source:
        print(f"Source quests: {item.source.quests}")


# ---------------------------------------------------------------------------
# Example 3: Full normalization of a weapon
# ---------------------------------------------------------------------------

def example_normalize_weapon() -> None:
    """Normalize a weapon and inspect WeaponStats sub-model."""
    print("\n" + "=" * 60)
    print("Example 3: ItemNormalizer — weapon")
    print("=" * 60)

    normalizer = ItemNormalizer()
    item = normalizer.normalize(WEAPON_HTML, wiki_url=f"{WIKI_URL_BASE}Sword_of_Shadow")

    print(f"Name          : {item.name}")
    print(f"Minimum level : {item.minimum_level}")

    ws = item.weapon_stats
    if ws:
        print(f"\nWeapon stats:")
        print(f"  Type        : {ws.weapon_type}")
        print(f"  Handedness  : {ws.handedness}")
        print(f"  Damage dice : {ws.damage_dice}")
        print(f"  Damage bonus: +{ws.damage_bonus}")
        print(f"  Damage type : {ws.damage_type}")
        print(f"  Crit range  : {ws.critical_range}")
        print(f"  Crit mult   : x{ws.critical_multiplier}")
        print(f"  Enh bonus   : +{ws.enchantment_bonus}")

    print(f"\nEnchantments ({len(item.enchantments)}):")
    for enc in item.enchantments:
        value_str = f" → {enc.value}" if enc.value else ""
        print(f"  - {enc.name}{value_str}")


# ---------------------------------------------------------------------------
# Example 4: Full normalization of armor
# ---------------------------------------------------------------------------

def example_normalize_armor() -> None:
    """Normalize heavy armor and inspect ArmorStats sub-model."""
    print("\n" + "=" * 60)
    print("Example 4: ItemNormalizer — heavy armor")
    print("=" * 60)

    normalizer = ItemNormalizer()
    item = normalizer.normalize(ARMOR_HTML, wiki_url=f"{WIKI_URL_BASE}Plate_of_the_Fallen")

    print(f"Name          : {item.name}")
    print(f"Minimum level : {item.minimum_level}")

    a = item.armor_stats
    if a:
        print(f"\nArmor stats:")
        print(f"  Armor type         : {a.armor_type}")
        print(f"  Armor bonus        : +{a.armor_bonus}")
        print(f"  Max dex bonus      : {a.max_dex_bonus}")
        print(f"  Armor check penalty: {a.armor_check_penalty}")
        print(f"  Arcane spell fail  : {a.arcane_spell_failure}%")


# ---------------------------------------------------------------------------
# Example 5: JSON serialization round-trip
# ---------------------------------------------------------------------------

def example_json_round_trip() -> None:
    """Serialize a DDOItem to JSON and restore it."""
    print("\n" + "=" * 60)
    print("Example 5: JSON serialization round-trip")
    print("=" * 60)

    normalizer = ItemNormalizer()
    item = normalizer.normalize(CLOAK_HTML, wiki_url=f"{WIKI_URL_BASE}Mantle_of_the_Worldshaper")

    json_str = item.to_json()

    # Peek at the structure
    data = json.loads(json_str)
    print("Top-level keys:", list(data.keys()))
    print(f"name          : {data['name']}")
    print(f"minimum_level : {data['minimum_level']}  (serialized as int)")
    print(f"enchantments  : {data['enchantments']}")

    # Round-trip restore
    from item_normalizer.models import DDOItem
    restored = DDOItem.from_json(json_str)
    assert restored.name == item.name
    assert restored.minimum_level == item.minimum_level
    assert len(restored.enchantments) == len(item.enchantments)
    print("\nRound-trip restore: OK")


# ---------------------------------------------------------------------------
# Example 6: ParseError handling
# ---------------------------------------------------------------------------

def example_parse_error() -> None:
    """Show how ParseError is raised when HTML has no item structure."""
    print("\n" + "=" * 60)
    print("Example 6: ParseError — unrecognized HTML")
    print("=" * 60)

    bad_html = "<html><body><p>404 Not Found</p></body></html>"
    normalizer = ItemNormalizer()

    try:
        normalizer.normalize(bad_html, wiki_url="https://ddowiki.com/page/Item:Missing")
    except ParseError as exc:
        print(f"Caught ParseError: {exc}")
        print(f"  field    : {exc.field!r}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    example_raw_parser()
    example_normalize_cloak()
    example_normalize_weapon()
    example_normalize_armor()
    example_json_round_trip()
    example_parse_error()


if __name__ == "__main__":
    main()
