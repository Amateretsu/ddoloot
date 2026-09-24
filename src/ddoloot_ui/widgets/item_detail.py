"""Right-panel item detail view rendered as styled HTML in a QTextBrowser."""

from __future__ import annotations

import webbrowser
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QScrollArea,
    QSizePolicy,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from item_normalizer.models import DDOItem
from ddoloot_ui.theme import COLORS

C = COLORS

_DETAIL_CSS = f"""
body {{
    background-color: {C['bg_medium']};
    color: {C['text_primary']};
    font-family: "Segoe UI", "SF Pro Text", Arial, sans-serif;
    font-size: 13px;
    margin: 0;
    padding: 0;
}}

h1.item-name {{
    font-size: 17px;
    font-weight: bold;
    color: {C['text_primary']};
    margin: 0 0 2px 0;
    padding: 0;
}}

p.subtitle {{
    font-size: 12px;
    color: {C['text_secondary']};
    margin: 0 0 12px 0;
}}

h3.section {{
    font-size: 10px;
    font-weight: bold;
    letter-spacing: 2px;
    color: {C['accent_gold']};
    margin: 14px 0 6px 0;
    padding: 0;
    text-transform: uppercase;
    border-bottom: 1px solid {C['accent_gold_dim']};
    padding-bottom: 4px;
}}

table.stats {{
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 4px;
}}

td.key {{
    color: {C['text_secondary']};
    font-size: 12px;
    padding: 2px 12px 2px 0;
    width: 40%;
    vertical-align: top;
}}

td.val {{
    color: {C['text_primary']};
    font-size: 12px;
    padding: 2px 0;
    vertical-align: top;
}}

ul.enchants {{
    margin: 4px 0;
    padding-left: 16px;
}}

li.enchant {{
    font-size: 12px;
    color: {C['accent_gold_bright']};
    padding: 1px 0;
}}

li.enchant span.val {{
    color: {C['text_secondary']};
}}

ul.plain {{
    margin: 4px 0;
    padding-left: 16px;
}}

li.plain {{
    font-size: 12px;
    color: {C['text_primary']};
    padding: 1px 0;
}}

p.flavor {{
    font-size: 12px;
    font-style: italic;
    color: {C['text_secondary']};
    margin: 6px 0;
    padding: 8px;
    border-left: 2px solid {C['accent_gold_dim']};
    background-color: {C['bg_dark']};
}}

p.empty {{
    font-size: 13px;
    color: {C['text_muted']};
    margin-top: 48px;
    text-align: center;
}}

a {{ color: {C['text_link']}; }}
a:hover {{ color: #8ac9ff; }}
"""


def _html_escape(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _row(key: str, value: str) -> str:
    return (
        f"<tr><td class='key'>{_html_escape(key)}</td>"
        f"<td class='val'>{_html_escape(value)}</td></tr>"
    )


def _copper_to_display(cp: int) -> str:
    pp, rem = divmod(cp, 1000)
    gp, rem = divmod(rem, 100)
    sp, cp_left = divmod(rem, 10)
    parts = []
    if pp:
        parts.append(f"{pp} pp")
    if gp:
        parts.append(f"{gp} gp")
    if sp:
        parts.append(f"{sp} sp")
    if cp_left:
        parts.append(f"{cp_left} cp")
    return " ".join(parts) if parts else "0 cp"


def _build_html(item: DDOItem) -> str:
    h = ["<html><head><style>", _DETAIL_CSS, "</style></head><body>"]

    # ── Header ────────────────────────────────────────────────────────
    h.append(f"<h1 class='item-name'>{_html_escape(item.name)}</h1>")
    subtitle_parts = [p for p in [item.slot, item.item_type] if p]
    if item.minimum_level:
        subtitle_parts.append(f"Level {item.minimum_level}")
    h.append(f"<p class='subtitle'>{_html_escape(' · '.join(subtitle_parts))}</p>")

    # ── Core properties ───────────────────────────────────────────────
    h.append("<h3 class='section'>Properties</h3>")
    h.append("<table class='stats'>")
    if item.binding:
        h.append(_row("Binding", item.binding))
    if item.material:
        h.append(_row("Material", item.material))
    if item.hardness is not None:
        h.append(_row("Hardness", str(item.hardness)))
    if item.durability is not None:
        h.append(_row("Durability", str(item.durability)))
    if item.weight is not None:
        h.append(_row("Weight", f"{item.weight} lbs"))
    if item.base_value is not None:
        h.append(_row("Value", _copper_to_display(item.base_value)))
    if item.required_race:
        h.append(_row("Required Race", item.required_race))
    if item.required_class:
        h.append(_row("Required Class", item.required_class))
    h.append("</table>")

    # ── Weapon stats ──────────────────────────────────────────────────
    if item.weapon_stats:
        ws = item.weapon_stats
        h.append("<h3 class='section'>Weapon</h3>")
        h.append("<table class='stats'>")
        if ws.weapon_type:
            h.append(_row("Type", ws.weapon_type))
        if ws.handedness:
            h.append(_row("Handedness", ws.handedness))
        if ws.proficiency:
            h.append(_row("Proficiency", ws.proficiency))
        if ws.enchantment_bonus is not None:
            h.append(_row("Enchantment Bonus", f"+{ws.enchantment_bonus}"))

        dmg_parts = []
        if ws.damage_dice:
            dmg_parts.append(ws.damage_dice)
        if ws.damage_bonus:
            dmg_parts.append(f"+{ws.damage_bonus}")
        if ws.damage_type:
            dmg_parts.append(" / ".join(ws.damage_type))
        if dmg_parts:
            h.append(_row("Damage", " ".join(dmg_parts)))

        if ws.critical_range or ws.critical_multiplier:
            crit = []
            if ws.critical_range:
                crit.append(ws.critical_range)
            if ws.critical_multiplier:
                crit.append(f"×{ws.critical_multiplier}")
            h.append(_row("Critical", " / ".join(crit)))
        h.append("</table>")

    # ── Armor stats ───────────────────────────────────────────────────
    if item.armor_stats:
        ar = item.armor_stats
        h.append("<h3 class='section'>Armor</h3>")
        h.append("<table class='stats'>")
        if ar.armor_type:
            h.append(_row("Armor Type", ar.armor_type))
        if ar.armor_bonus is not None:
            h.append(_row("Armor Bonus", f"+{ar.armor_bonus}"))
        if ar.max_dex_bonus is not None:
            h.append(_row("Max Dex Bonus", str(ar.max_dex_bonus)))
        if ar.armor_check_penalty is not None:
            h.append(_row("Check Penalty", str(ar.armor_check_penalty)))
        if ar.arcane_spell_failure is not None:
            h.append(_row("Arcane Spell Failure", f"{ar.arcane_spell_failure}%"))
        h.append("</table>")

    # ── Enchantments ──────────────────────────────────────────────────
    if item.enchantments:
        h.append("<h3 class='section'>Enchantments</h3>")
        h.append("<ul class='enchants'>")
        for ench in item.enchantments:
            name_esc = _html_escape(ench.name)
            if ench.value is not None:
                h.append(
                    f"<li class='enchant'>{name_esc} "
                    f"<span class='val'>+{ench.value}</span></li>"
                )
            else:
                h.append(f"<li class='enchant'>{name_esc}</li>")
        h.append("</ul>")

    # ── Named set ─────────────────────────────────────────────────────
    if item.named_set:
        ns = item.named_set
        h.append("<h3 class='section'>Named Set</h3>")
        h.append("<table class='stats'>")
        h.append(_row("Set", ns.name))
        h.append("</table>")
        if ns.bonuses:
            h.append("<ul class='plain'>")
            for bonus in ns.bonuses:
                h.append(
                    f"<li class='plain'>"
                    f"{bonus.pieces_required} pieces: "
                    f"{_html_escape(bonus.description)}"
                    f"</li>"
                )
            h.append("</ul>")

    # ── Source ────────────────────────────────────────────────────────
    if item.source:
        src = item.source
        has_source = src.quests or src.chest or src.dropped_by or src.crafted_by
        if has_source:
            h.append("<h3 class='section'>Source</h3>")
            h.append("<table class='stats'>")
            if src.chest:
                h.append(_row("Chest", src.chest))
            if src.crafted_by:
                h.append(_row("Crafted by", src.crafted_by))
            h.append("</table>")
            if src.quests:
                h.append("<ul class='plain'>")
                for q in src.quests:
                    h.append(f"<li class='plain'>{_html_escape(q)}</li>")
                h.append("</ul>")
            if src.dropped_by:
                h.append("<ul class='plain'>")
                for mob in src.dropped_by:
                    h.append(f"<li class='plain'>Dropped by: {_html_escape(mob)}</li>")
                h.append("</ul>")

    # ── Flavor text ───────────────────────────────────────────────────
    if item.flavor_text:
        h.append(f"<p class='flavor'>{_html_escape(item.flavor_text)}</p>")

    # ── Wiki link ─────────────────────────────────────────────────────
    if item.wiki_url:
        esc_url = _html_escape(item.wiki_url)
        h.append(f"<p style='margin-top:16px; font-size:11px;'>"
                 f"<a href='{esc_url}'>Open wiki page ↗</a></p>")

    # ── Scraped date ──────────────────────────────────────────────────
    h.append(
        f"<p style='font-size:10px; color:{C['text_muted']}; margin-top:6px;'>"
        f"Scraped: {item.scraped_at.strftime('%Y-%m-%d %H:%M UTC')}</p>"
    )

    h.append("</body></html>")
    return "".join(h)


_EMPTY_HTML = f"""<html><head><style>{_DETAIL_CSS}</style></head>
<body><p class='empty'>Select an item to see details</p></body></html>"""


class ItemDetail(QWidget):
    """Scrollable right panel that displays a single DDOItem."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("DetailPanel")
        self.setMinimumWidth(300)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._browser = QTextBrowser()
        self._browser.setOpenLinks(False)
        self._browser.anchorClicked.connect(self._open_link)
        self._browser.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._browser)

        self.clear()

    def show_item(self, item: DDOItem) -> None:
        self._browser.setHtml(_build_html(item))
        self._browser.verticalScrollBar().setValue(0)

    def clear(self) -> None:
        self._browser.setHtml(_EMPTY_HTML)

    def _open_link(self, url) -> None:
        QDesktopServices.openUrl(url)
