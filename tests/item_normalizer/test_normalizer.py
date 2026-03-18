"""Unit tests for item_normalizer.normalizer.ItemNormalizer."""

from datetime import timezone

import pytest

from item_normalizer.exceptions import ParseError
from item_normalizer.models import ArmorStats, DDOItem, WeaponStats
from item_normalizer.normalizer import ItemNormalizer

WIKI_URL = "https://ddowiki.com/page/Item:Test"


@pytest.fixture
def normalizer() -> ItemNormalizer:
    return ItemNormalizer()


# ---------------------------------------------------------------------------
# Full-item smoke tests
# ---------------------------------------------------------------------------


class TestNormalizeCloak:
    def test_returns_ddo_item(
        self, normalizer: ItemNormalizer, cloak_html: str
    ) -> None:
        item = normalizer.normalize(cloak_html, WIKI_URL)
        assert isinstance(item, DDOItem)

    def test_name(self, normalizer: ItemNormalizer, cloak_html: str) -> None:
        item = normalizer.normalize(cloak_html, WIKI_URL)
        assert item.name == "Mantle of the Worldshaper"

    def test_minimum_level(self, normalizer: ItemNormalizer, cloak_html: str) -> None:
        item = normalizer.normalize(cloak_html, WIKI_URL)
        assert item.minimum_level == 20

    def test_material(self, normalizer: ItemNormalizer, cloak_html: str) -> None:
        item = normalizer.normalize(cloak_html, WIKI_URL)
        assert item.material == "Cloth"

    def test_hardness_and_durability(
        self, normalizer: ItemNormalizer, cloak_html: str
    ) -> None:
        item = normalizer.normalize(cloak_html, WIKI_URL)
        assert item.hardness == 14
        assert item.durability == 100

    def test_weight(self, normalizer: ItemNormalizer, cloak_html: str) -> None:
        item = normalizer.normalize(cloak_html, WIKI_URL)
        assert item.weight == pytest.approx(0.1)

    def test_binding(self, normalizer: ItemNormalizer, cloak_html: str) -> None:
        item = normalizer.normalize(cloak_html, WIKI_URL)
        assert item.binding == "Bound to Character on Acquire"

    def test_enchantments(self, normalizer: ItemNormalizer, cloak_html: str) -> None:
        item = normalizer.normalize(cloak_html, WIKI_URL)
        names = [e.name for e in item.enchantments]
        assert "Metalline" in names
        assert "Resistance" in names
        assert "Superior Devotion" in names

    def test_resistance_value(
        self, normalizer: ItemNormalizer, cloak_html: str
    ) -> None:
        item = normalizer.normalize(cloak_html, WIKI_URL)
        resistance = next(e for e in item.enchantments if e.name == "Resistance")
        assert resistance.value == 5

    def test_devotion_roman_numeral_value(
        self, normalizer: ItemNormalizer, cloak_html: str
    ) -> None:
        item = normalizer.normalize(cloak_html, WIKI_URL)
        devotion = next(e for e in item.enchantments if e.name == "Superior Devotion")
        assert devotion.value == 6

    def test_named_set(self, normalizer: ItemNormalizer, cloak_html: str) -> None:
        item = normalizer.normalize(cloak_html, WIKI_URL)
        assert item.named_set is not None
        assert item.named_set.name == "Thelanis Fairy Tale"

    def test_source_quests(self, normalizer: ItemNormalizer, cloak_html: str) -> None:
        item = normalizer.normalize(cloak_html, WIKI_URL)
        assert item.source is not None
        assert "The Snitch" in item.source.quests

    def test_flavor_text(self, normalizer: ItemNormalizer, cloak_html: str) -> None:
        item = normalizer.normalize(cloak_html, WIKI_URL)
        assert item.flavor_text is not None
        assert "planes" in item.flavor_text

    def test_no_weapon_stats(self, normalizer: ItemNormalizer, cloak_html: str) -> None:
        item = normalizer.normalize(cloak_html, WIKI_URL)
        assert item.weapon_stats is None

    def test_no_armor_stats(self, normalizer: ItemNormalizer, cloak_html: str) -> None:
        item = normalizer.normalize(cloak_html, WIKI_URL)
        assert item.armor_stats is None

    def test_wiki_url(self, normalizer: ItemNormalizer, cloak_html: str) -> None:
        item = normalizer.normalize(cloak_html, WIKI_URL)
        assert item.wiki_url == WIKI_URL

    def test_scraped_at_is_utc(
        self, normalizer: ItemNormalizer, cloak_html: str
    ) -> None:
        item = normalizer.normalize(cloak_html, WIKI_URL)
        assert item.scraped_at.tzinfo == timezone.utc

    def test_json_round_trip(self, normalizer: ItemNormalizer, cloak_html: str) -> None:
        item = normalizer.normalize(cloak_html, WIKI_URL)
        restored = DDOItem.from_json(item.to_json())
        assert restored.name == item.name
        assert len(restored.enchantments) == len(item.enchantments)


class TestNormalizeWeapon:
    def test_weapon_stats_present(
        self, normalizer: ItemNormalizer, weapon_html: str
    ) -> None:
        item = normalizer.normalize(weapon_html, WIKI_URL)
        assert item.weapon_stats is not None
        assert isinstance(item.weapon_stats, WeaponStats)

    def test_damage_dice(self, normalizer: ItemNormalizer, weapon_html: str) -> None:
        item = normalizer.normalize(weapon_html, WIKI_URL)
        assert item.weapon_stats.damage_dice == "1d8"

    def test_damage_bonus(self, normalizer: ItemNormalizer, weapon_html: str) -> None:
        item = normalizer.normalize(weapon_html, WIKI_URL)
        assert item.weapon_stats.damage_bonus == 5

    def test_damage_type(self, normalizer: ItemNormalizer, weapon_html: str) -> None:
        item = normalizer.normalize(weapon_html, WIKI_URL)
        assert "Slashing" in item.weapon_stats.damage_type
        assert "Magic" in item.weapon_stats.damage_type

    def test_critical_range(self, normalizer: ItemNormalizer, weapon_html: str) -> None:
        item = normalizer.normalize(weapon_html, WIKI_URL)
        assert item.weapon_stats.critical_range == "19-20"

    def test_critical_multiplier(
        self, normalizer: ItemNormalizer, weapon_html: str
    ) -> None:
        item = normalizer.normalize(weapon_html, WIKI_URL)
        assert item.weapon_stats.critical_multiplier == 2

    def test_enchantment_bonus(
        self, normalizer: ItemNormalizer, weapon_html: str
    ) -> None:
        item = normalizer.normalize(weapon_html, WIKI_URL)
        assert item.weapon_stats.enchantment_bonus == 5

    def test_handedness(self, normalizer: ItemNormalizer, weapon_html: str) -> None:
        item = normalizer.normalize(weapon_html, WIKI_URL)
        assert item.weapon_stats.handedness == "One-Handed"

    def test_weapon_type(self, normalizer: ItemNormalizer, weapon_html: str) -> None:
        item = normalizer.normalize(weapon_html, WIKI_URL)
        assert item.weapon_stats.weapon_type == "Longsword"

    def test_no_armor_stats(self, normalizer: ItemNormalizer, weapon_html: str) -> None:
        item = normalizer.normalize(weapon_html, WIKI_URL)
        assert item.armor_stats is None

    def test_colon_split_enchantment(
        self, normalizer: ItemNormalizer, weapon_html: str
    ) -> None:
        item = normalizer.normalize(weapon_html, WIKI_URL)
        crit = next((e for e in item.enchantments if "Critical" in e.name), None)
        assert crit is not None
        assert crit.value is None


class TestNormalizeArmor:
    def test_armor_stats_present(
        self, normalizer: ItemNormalizer, armor_html: str
    ) -> None:
        item = normalizer.normalize(armor_html, WIKI_URL)
        assert item.armor_stats is not None
        assert isinstance(item.armor_stats, ArmorStats)

    def test_armor_type(self, normalizer: ItemNormalizer, armor_html: str) -> None:
        item = normalizer.normalize(armor_html, WIKI_URL)
        assert item.armor_stats.armor_type == "Heavy"

    def test_armor_bonus(self, normalizer: ItemNormalizer, armor_html: str) -> None:
        item = normalizer.normalize(armor_html, WIKI_URL)
        assert item.armor_stats.armor_bonus == 9

    def test_max_dex_bonus(self, normalizer: ItemNormalizer, armor_html: str) -> None:
        item = normalizer.normalize(armor_html, WIKI_URL)
        assert item.armor_stats.max_dex_bonus == 3

    def test_armor_check_penalty(
        self, normalizer: ItemNormalizer, armor_html: str
    ) -> None:
        item = normalizer.normalize(armor_html, WIKI_URL)
        assert item.armor_stats.armor_check_penalty == -3

    def test_arcane_spell_failure(
        self, normalizer: ItemNormalizer, armor_html: str
    ) -> None:
        item = normalizer.normalize(armor_html, WIKI_URL)
        assert item.armor_stats.arcane_spell_failure == 25

    def test_no_weapon_stats(self, normalizer: ItemNormalizer, armor_html: str) -> None:
        item = normalizer.normalize(armor_html, WIKI_URL)
        assert item.weapon_stats is None

    def test_flavor_text(self, normalizer: ItemNormalizer, armor_html: str) -> None:
        item = normalizer.normalize(armor_html, WIKI_URL)
        assert item.flavor_text is not None
        assert "celestial" in item.flavor_text


class TestNormalizeMinimal:
    def test_minimal_item_name(
        self, normalizer: ItemNormalizer, minimal_html: str
    ) -> None:
        item = normalizer.normalize(minimal_html, WIKI_URL)
        assert item.name == "Basic Ring"

    def test_minimal_item_no_enchantments(
        self, normalizer: ItemNormalizer, minimal_html: str
    ) -> None:
        item = normalizer.normalize(minimal_html, WIKI_URL)
        assert item.enchantments == []

    def test_minimal_item_optional_fields_none(
        self, normalizer: ItemNormalizer, minimal_html: str
    ) -> None:
        item = normalizer.normalize(minimal_html, WIKI_URL)
        assert item.minimum_level is None
        assert item.weapon_stats is None
        assert item.armor_stats is None
        assert item.named_set is None
        assert item.source is None


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------


class TestNormalizerErrors:
    def test_parse_error_propagates(self, normalizer: ItemNormalizer) -> None:
        html = "<html><body><p>No item here</p></body></html>"
        with pytest.raises(ParseError):
            normalizer.normalize(html, WIKI_URL)
