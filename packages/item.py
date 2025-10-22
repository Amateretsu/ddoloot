from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from enum import Enum

class DDOItemType(Enum):

    # === ARMOR (5) ===
    ARMOR_CLOTH = "armor_cloth"
    ARMOR_LIGHT = "armor_light"
    ARMOR_MEDIUM = "armor_medium"
    ARMOR_HEAVY = "armor_heavy"
    ARMOR_DOCENTS = "armor_docents"

    # === SHIELDS (5) ===
    SHIELDS_BUCKLERS = "shields_bucklers"
    SHIELDS_SMALL = "shields_small"
    SHIELDS_LARGE = "shields_large"
    SHIELDS_TOWER = "shields_tower"
    SHIELDS_ORBS = "shields_orbs"

    # === CLOTHING (1) ===
    CLOTHING = "clothing"

    # === JEWELRY (10) ===
    JEWELRY_HELMS = "jewelry_helms"
    JEWELRY_GLOVES = "jewelry_gloves"
    JEWELRY_CLOAKS = "jewelry_cloaks"
    JEWELRY_BELTS = "jewelry_belts"
    JEWELRY_BOOTS = "jewelry_boots"
    JEWELRY_BRACERS = "jewelry_bracers"
    JEWELRY_GOGGLES = "jewelry_goggles"
    JEWELRY_NECKLACES = "jewelry_necklaces"
    JEWELRY_RINGS = "jewelry_rings"
    JEWELRY_TRINKETS = "jewelry_trinkets"

    # === WEAPONS (50+ FLATTENED) ===
    WEAPON_CLUB = "weapon_club"
    WEAPON_QUARTERSTAFF = "weapon_quarterstaff"
    WEAPON_DAGGER = "weapon_dagger"
    WEAPON_SICKLE = "weapon_sickle"
    WEAPON_LIGHT_MACE = "weapon_light_mace"
    WEAPON_HEAVY_MACE = "weapon_heavy_mace"
    WEAPON_MORNINGSTAR = "weapon_morningstar"
    WEAPON_HEAVY_CROSSBOW = "weapon_heavy_crossbow"
    WEAPON_LIGHT_CROSSBOW = "weapon_light_crossbow"

    WEAPON_HANDAXE = "weapon_handaxe"
    WEAPON_BATTLE_AXE = "weapon_battle_axe"
    WEAPON_GREAT_AXE = "weapon_great_axe"
    WEAPON_KUKRI = "weapon_kukri"
    WEAPON_LONG_SWORD = "weapon_long_sword"  # ← YOUR EXAMPLE!
    WEAPON_GREAT_SWORD = "weapon_great_sword"
    WEAPON_SCIMITAR = "weapon_scimitar"
    WEAPON_FALCHION = "weapon_falchion"
    WEAPON_LONG_BOW = "weapon_long_bow"
    WEAPON_SHORT_SWORD = "weapon_short_sword"
    WEAPON_RAPIER = "weapon_rapier"
    WEAPON_HEAVY_PICK = "weapon_heavy_pick"
    WEAPON_LIGHT_PICK = "weapon_light_pick"
    WEAPON_LIGHT_HAMMER = "weapon_light_hammer"
    WEAPON_WAR_HAMMER = "weapon_war_hammer"
    WEAPON_MAUL = "weapon_maul"
    WEAPON_GREAT_CLUB = "weapon_great_club"
    WEAPON_SHORT_BOW = "weapon_short_bow"

    WEAPON_BASTARD_SWORD = "weapon_bastard_sword"
    WEAPON_DWARVEN_WAR_AXE = "weapon_dwarven_war_axe"
    WEAPON_KAMA = "weapon_kama"
    WEAPON_KHOPESH = "weapon_khopesh"
    WEAPON_HANDWRAPS = "weapon_handwraps"
    WEAPON_RUNE_ARM = "weapon_rune_arm"
    WEAPON_GREAT_CROSSBOW = "weapon_great_crossbow"
    WEAPON_REPEATING_HEAVY_CROSSBOW = "weapon_repeating_heavy_crossbow"
    WEAPON_REPEATING_LIGHT_CROSSBOW = "weapon_repeating_light_crossbow"

    WEAPON_THROWING_AXE = "weapon_throwing_axe"
    WEAPON_THROWING_DAGGER = "weapon_throwing_dagger"
    WEAPON_THROWING_HAMMER = "weapon_throwing_hammer"
    WEAPON_DART = "weapon_dart"
    WEAPON_SHURIKEN = "weapon_shuriken"

    # === COLLARS (1) ===
    COLLAR_PET = "collar_pet"

    # === COSMETICS (15) ===
    COSMETIC_ARMOR = "cosmetic_armor"
    COSMETIC_SHIELDS = "cosmetic_shields"
    COSMETIC_HELMS = "cosmetic_helms"
    COSMETIC_GOGGLES = "cosmetic_goggles"
    COSMETIC_CLOAKS = "cosmetic_cloaks"
    COSMETIC_ONE_HANDED_STYLE = "cosmetic_one_handed_style"
    COSMETIC_ONE_HANDED_STYLE_THROWING = "cosmetic_one_handed_style_throwing"
    COSMETIC_TWO_HANDED_STYLE = "cosmetic_two_handed_style"
    COSMETIC_GREAT_AXE_STYLE = "cosmetic_great_axe_style"
    COSMETIC_QUARTERSTAFF_STYLE = "cosmetic_quarterstaff_style"
    COSMETIC_CROSSBOW_STYLE = "cosmetic_crossbow_style"
    COSMETIC_REPEATING_CROSSBOW_STYLE = "cosmetic_repeating_crossbow_style"
    COSMETIC_BOW_STYLE = "cosmetic_bow_style"
    COSMETIC_WEAPON_AURA = "cosmetic_weapon_aura"
    COSMETIC_WEAPONS = "cosmetic_weapons"

    @property
    def category(self) -> str:
        """Extract main category (weapon, armor, etc.)."""
        return self.value.split('_')[0]

    @property
    def display_name(self) -> str:
        """Human-readable name."""
        parts = self.value.replace('_', ' ').title()
        return f"{self.category.title()} {parts.split(' ', 1)[1]}"


@dataclass
class DDOItem:
    """SIMPLE DDO item - ONE ENUM, ZERO NESTING."""

    name: str = ""
    item_type: DDOItemType = field(default_factory=lambda: DDOItemType.ARMOR_CLOTH)

    @property
    def full_type(self) -> str:
        """Display: 'Weapon Long Sword'."""
        return self.item_type.display_name

    @classmethod
    def create(cls, name: str, item_type: DDOItemType) -> 'DDOItem':
        """Simple factory."""
        return cls(name=name, item_type=item_type)

    def to_dict(self) -> Dict[str, Any]:
        """JSON/DB serialization."""
        return {
            "name": self.name,
            "item_type": self.item_type.value,
            "full_type": self.full_type,
            "category": self.item_type.category
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DDOItem':
        """Deserialization."""
        return cls(name=data["name"], item_type=DDOItemType(data["item_type"]))