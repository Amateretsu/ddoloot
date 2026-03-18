"""ItemFilter dataclass and WHERE clause builder for item_db searches.

Internal module — not part of the public API. Import ItemFilter from item_db
directly.

Example:
    >>> from item_db import ItemFilter
    >>> f = ItemFilter(slot="Back", minimum_level_max=20)
    >>> sql, params = build_where_clause(f)
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Tuple


@dataclass
class ItemFilter:
    """Criteria for filtering items in ItemRepository.search().

    All fields are optional. Set fields are ANDed together.
    An empty ItemFilter (all None / False) returns all items.

    Example:
        >>> # Find all cloaks usable at level 20 or below
        >>> f = ItemFilter(slot="Back", minimum_level_max=20)

        >>> # Find weapons with Vorpal enchantment
        >>> f = ItemFilter(has_enchantment="Vorpal")

        >>> # Find non-restricted heavy armor for arcane casters
        >>> f = ItemFilter(
        ...     armor_type="Heavy",
        ...     arcane_spell_failure_max=15,
        ...     exclude_class_restricted=True,
        ... )
    """

    # Core identity
    name_contains: Optional[str] = None          # case-insensitive LIKE '%x%'
    item_type: Optional[str] = None              # exact: 'Cloak', 'Weapon'
    slot: Optional[str] = None                   # exact: 'Back', 'Finger'

    # Level gating
    minimum_level_min: Optional[int] = None      # minimum_level >= x
    minimum_level_max: Optional[int] = None      # minimum_level <= x (equippable at level x)

    # Character restrictions
    required_race: Optional[str] = None
    required_class: Optional[str] = None
    exclude_race_restricted: bool = False        # WHERE required_race IS NULL
    exclude_class_restricted: bool = False       # WHERE required_class IS NULL

    # Binding / material
    binding: Optional[str] = None
    material: Optional[str] = None

    # Weapon filters (joins weapon_stats)
    weapon_type: Optional[str] = None
    handedness: Optional[str] = None
    damage_type_includes: Optional[str] = None  # item has at least this damage type

    # Armor filters (joins armor_stats)
    armor_type: Optional[str] = None
    arcane_spell_failure_max: Optional[int] = None

    # Enchantment filter (joins enchantments)
    has_enchantment: Optional[str] = None       # case-insensitive LIKE match on name

    # Set membership (joins item_named_set → named_sets)
    named_set: Optional[str] = None             # exact set name

    # Source filters
    drops_in_quest: Optional[str] = None        # LIKE substring match on quest_name
    dropped_by: Optional[str] = None            # LIKE substring match on monster

    # Data freshness
    scraped_before: Optional[datetime] = None
    scraped_after: Optional[datetime] = None


def build_where_clause(f: ItemFilter) -> Tuple[str, List]:
    """Build a parameterized SQL query that returns matching item IDs.

    All JOINs reference the integer item_id FK. Only joins required by the
    active filters are emitted. DISTINCT prevents fan-out from one-to-many
    joins (enchantments, quests, etc.).

    Args:
        f: Populated ItemFilter instance

    Returns:
        Tuple of (sql, params) where sql is a complete SELECT that returns
        a list of (id, name) rows for matching items, ordered by name.
    """
    joins: List[str] = []
    clauses: List[str] = []
    params: List = []

    # ── Items table filters ─────────────────────────────────────────────────

    if f.name_contains is not None:
        clauses.append("i.name LIKE ?")
        params.append(f"%{f.name_contains}%")

    if f.item_type is not None:
        clauses.append("i.item_type = ?")
        params.append(f.item_type)

    if f.slot is not None:
        clauses.append("i.slot = ?")
        params.append(f.slot)

    if f.minimum_level_min is not None:
        clauses.append("i.minimum_level >= ?")
        params.append(f.minimum_level_min)

    if f.minimum_level_max is not None:
        clauses.append("(i.minimum_level IS NULL OR i.minimum_level <= ?)")
        params.append(f.minimum_level_max)

    if f.required_race is not None:
        clauses.append("i.required_race = ?")
        params.append(f.required_race)

    if f.required_class is not None:
        clauses.append("i.required_class = ?")
        params.append(f.required_class)

    if f.exclude_race_restricted:
        clauses.append("i.required_race IS NULL")

    if f.exclude_class_restricted:
        clauses.append("i.required_class IS NULL")

    if f.binding is not None:
        clauses.append("i.binding = ?")
        params.append(f.binding)

    if f.material is not None:
        clauses.append("i.material = ?")
        params.append(f.material)

    if f.scraped_before is not None:
        clauses.append("i.scraped_at < ?")
        params.append(f.scraped_before.isoformat())

    if f.scraped_after is not None:
        clauses.append("i.scraped_at > ?")
        params.append(f.scraped_after.isoformat())

    # ── Weapon filters ──────────────────────────────────────────────────────

    if f.weapon_type is not None or f.handedness is not None:
        joins.append("JOIN weapon_stats ws ON ws.item_id = i.id")
        if f.weapon_type is not None:
            clauses.append("ws.weapon_type = ?")
            params.append(f.weapon_type)
        if f.handedness is not None:
            clauses.append("ws.handedness = ?")
            params.append(f.handedness)

    if f.damage_type_includes is not None:
        joins.append("JOIN weapon_damage_types wdt ON wdt.item_id = i.id")
        clauses.append("wdt.damage_type = ?")
        params.append(f.damage_type_includes)

    # ── Armor filters ───────────────────────────────────────────────────────

    if f.armor_type is not None or f.arcane_spell_failure_max is not None:
        joins.append("JOIN armor_stats ast ON ast.item_id = i.id")
        if f.armor_type is not None:
            clauses.append("ast.armor_type = ?")
            params.append(f.armor_type)
        if f.arcane_spell_failure_max is not None:
            clauses.append(
                "(ast.arcane_spell_failure IS NULL OR ast.arcane_spell_failure <= ?)"
            )
            params.append(f.arcane_spell_failure_max)

    # ── Enchantment filter ──────────────────────────────────────────────────

    if f.has_enchantment is not None:
        joins.append("JOIN enchantments enc ON enc.item_id = i.id")
        clauses.append("enc.name LIKE ?")
        params.append(f"%{f.has_enchantment}%")

    # ── Named set filter ────────────────────────────────────────────────────

    if f.named_set is not None:
        joins.append("JOIN item_named_set ins ON ins.item_id = i.id")
        joins.append("JOIN named_sets ns ON ns.id = ins.named_set_id")
        clauses.append("ns.name = ?")
        params.append(f.named_set)

    # ── Source filters ──────────────────────────────────────────────────────

    if f.drops_in_quest is not None:
        joins.append("JOIN source_quests sq ON sq.item_id = i.id")
        clauses.append("sq.quest_name LIKE ?")
        params.append(f"%{f.drops_in_quest}%")

    if f.dropped_by is not None:
        joins.append("JOIN source_dropped_by sdb ON sdb.item_id = i.id")
        clauses.append("sdb.monster LIKE ?")
        params.append(f"%{f.dropped_by}%")

    # ── Assemble ────────────────────────────────────────────────────────────

    join_sql = (" " + " ".join(joins)) if joins else ""
    where_sql = (" WHERE " + " AND ".join(clauses)) if clauses else ""

    sql = f"SELECT DISTINCT i.id FROM items i{join_sql}{where_sql} ORDER BY i.name"
    return sql, params
