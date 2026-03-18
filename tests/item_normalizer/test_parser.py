"""Unit tests for item_normalizer.parser.WikiPageParser."""

import pytest

from item_normalizer.exceptions import ParseError
from item_normalizer.parser import WikiPageParser


WIKI_URL = "https://ddowiki.com/page/Item:Test"


@pytest.fixture
def parser() -> WikiPageParser:
    return WikiPageParser()


# ---------------------------------------------------------------------------
# Name extraction
# ---------------------------------------------------------------------------

class TestExtractName:
    def test_from_h1_firstheading(self, parser: WikiPageParser) -> None:
        html = '<h1 id="firstHeading">Item:Mantle of the Worldshaper</h1>'
        fields = parser.parse(html, WIKI_URL)
        assert fields["name"] == "Mantle of the Worldshaper"

    def test_strips_item_prefix(self, parser: WikiPageParser) -> None:
        html = '<h1 id="firstHeading">Item:Sword of Shadow</h1>'
        fields = parser.parse(html, WIKI_URL)
        assert fields["name"] == "Sword of Shadow"

    def test_fallback_to_wikitable_th(self, parser: WikiPageParser) -> None:
        html = """
        <table class="wikitable">
          <tr><th colspan="2">Mantle of the Worldshaper</th></tr>
          <tr><th>Minimum Level</th><td>15</td></tr>
        </table>
        """
        fields = parser.parse(html, WIKI_URL)
        assert fields["name"] == "Mantle of the Worldshaper"

    def test_raises_parse_error_when_no_name(self, parser: WikiPageParser) -> None:
        html = "<html><body><p>No item here</p></body></html>"
        with pytest.raises(ParseError, match="Could not extract item name"):
            parser.parse(html, WIKI_URL)


# ---------------------------------------------------------------------------
# Infobox field extraction
# ---------------------------------------------------------------------------

class TestExtractInfoboxFields:
    def test_minimum_level(self, parser: WikiPageParser, cloak_html: str) -> None:
        fields = parser.parse(cloak_html, WIKI_URL)
        assert fields["minimum_level"] == "20"

    def test_binding(self, parser: WikiPageParser, cloak_html: str) -> None:
        fields = parser.parse(cloak_html, WIKI_URL)
        assert fields["binding"] == "Bound to Character on Acquire"

    def test_material(self, parser: WikiPageParser, cloak_html: str) -> None:
        fields = parser.parse(cloak_html, WIKI_URL)
        assert fields["material"] == "Cloth"

    def test_hardness_and_durability(self, parser: WikiPageParser, cloak_html: str) -> None:
        fields = parser.parse(cloak_html, WIKI_URL)
        assert fields["hardness"] == "14"
        assert fields["durability"] == "100"

    def test_weight(self, parser: WikiPageParser, cloak_html: str) -> None:
        fields = parser.parse(cloak_html, WIKI_URL)
        assert fields["weight"] == "0.1 lbs"

    def test_slot_alias_equips_to(self, parser: WikiPageParser, cloak_html: str) -> None:
        fields = parser.parse(cloak_html, WIKI_URL)
        assert fields["slot"] == "Back"

    def test_damage_type_is_list(self, parser: WikiPageParser, weapon_html: str) -> None:
        fields = parser.parse(weapon_html, WIKI_URL)
        assert isinstance(fields["damage_type"], list)
        assert "Slashing" in fields["damage_type"]
        assert "Magic" in fields["damage_type"]

    def test_critical_roll_alias(self, parser: WikiPageParser, weapon_html: str) -> None:
        fields = parser.parse(weapon_html, WIKI_URL)
        assert "critical_roll" in fields
        assert "19-20" in fields["critical_roll"]

    def test_enhancement_bonus_alias(self, parser: WikiPageParser, weapon_html: str) -> None:
        fields = parser.parse(weapon_html, WIKI_URL)
        assert fields["enchantment_bonus"] == "5"

    def test_armor_type(self, parser: WikiPageParser, armor_html: str) -> None:
        fields = parser.parse(armor_html, WIKI_URL)
        assert fields["armor_type"] == "Heavy"

    def test_armor_check_penalty(self, parser: WikiPageParser, armor_html: str) -> None:
        fields = parser.parse(armor_html, WIKI_URL)
        assert fields["armor_check_penalty"] == "-3"

    def test_arcane_spell_failure(self, parser: WikiPageParser, armor_html: str) -> None:
        fields = parser.parse(armor_html, WIKI_URL)
        assert fields["arcane_spell_failure"] == "25%"

    def test_named_set_raw(self, parser: WikiPageParser, cloak_html: str) -> None:
        fields = parser.parse(cloak_html, WIKI_URL)
        assert fields["named_set_raw"] == "Thelanis Fairy Tale"

    def test_unknown_field_ignored(self, parser: WikiPageParser) -> None:
        html = """
        <h1 id="firstHeading">Item:Test</h1>
        <table class="wikitable">
          <tr><th>Unknown Field XYZ</th><td>some value</td></tr>
          <tr><th>Minimum Level</th><td>5</td></tr>
        </table>
        """
        fields = parser.parse(html, WIKI_URL)
        assert "unknown_field_xyz" not in fields
        assert fields["minimum_level"] == "5"

    def test_no_infobox_yields_warning_not_error(
        self, parser: WikiPageParser, minimal_html: str
    ) -> None:
        fields = parser.parse(minimal_html, WIKI_URL)
        assert fields["name"] == "Basic Ring"
        assert fields["enchantments"] == []


# ---------------------------------------------------------------------------
# Enchantment extraction
# ---------------------------------------------------------------------------

class TestExtractEnchantments:
    def test_cloak_enchantments(self, parser: WikiPageParser, cloak_html: str) -> None:
        fields = parser.parse(cloak_html, WIKI_URL)
        enchants = fields["enchantments"]
        assert "Superior Devotion VI" in enchants
        assert "Resistance +5" in enchants
        assert "Metalline" in enchants

    def test_no_enchantments_returns_empty_list(
        self, parser: WikiPageParser, minimal_html: str
    ) -> None:
        fields = parser.parse(minimal_html, WIKI_URL)
        assert fields["enchantments"] == []

    def test_weapon_enchantments(self, parser: WikiPageParser, weapon_html: str) -> None:
        fields = parser.parse(weapon_html, WIKI_URL)
        assert "Vorpal" in fields["enchantments"]


# ---------------------------------------------------------------------------
# Flavor text extraction
# ---------------------------------------------------------------------------

class TestExtractFlavorText:
    def test_cloak_flavor_text(self, parser: WikiPageParser, cloak_html: str) -> None:
        fields = parser.parse(cloak_html, WIKI_URL)
        expected = "This cloak was woven from the fabric of the planes themselves."
        assert fields["flavor_text"] == expected

    def test_no_flavor_text_returns_none(
        self, parser: WikiPageParser, weapon_html: str
    ) -> None:
        fields = parser.parse(weapon_html, WIKI_URL)
        assert fields.get("flavor_text") is None

    def test_armor_flavor_text(self, parser: WikiPageParser, armor_html: str) -> None:
        fields = parser.parse(armor_html, WIKI_URL)
        assert "celestial" in fields["flavor_text"]


# ---------------------------------------------------------------------------
# wiki_url injection
# ---------------------------------------------------------------------------

class TestWikiUrl:
    def test_wiki_url_is_injected(self, parser: WikiPageParser, cloak_html: str) -> None:
        url = "https://ddowiki.com/page/Item:Mantle_of_the_Worldshaper"
        fields = parser.parse(cloak_html, url)
        assert fields["wiki_url"] == url
