"""Center results table showing the currently filtered DDO items."""

from __future__ import annotations

from typing import List, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from item_normalizer.models import DDOItem
from ddoloot_ui.theme import COLORS

_COLUMNS = ["Name", "Level", "Slot", "Type", "Binding", "Enchantments"]
_COL_NAME = 0
_COL_LEVEL = 1
_COL_SLOT = 2
_COL_TYPE = 3
_COL_BIND = 4
_COL_ENCH = 5

_BINDING_SHORT = {
    "Bound to Character on Acquire": "BtCoA",
    "Bound to Account on Acquire": "BtAoA",
    "Bound to Character on Equip": "BtCoE",
    "Unbound": "Unbound",
}


def _shorten_binding(binding: Optional[str]) -> str:
    if binding is None:
        return ""
    return _BINDING_SHORT.get(binding, binding)


def _enchant_summary(item: DDOItem) -> str:
    if not item.enchantments:
        return ""
    names = [
        (f"{e.name} +{e.value}" if e.value is not None else e.name)
        for e in item.enchantments[:3]
    ]
    suffix = f" +{len(item.enchantments) - 3} more" if len(item.enchantments) > 3 else ""
    return ", ".join(names) + suffix


class ItemTable(QWidget):
    """Sortable item table with item-selected signal.

    Signals
    -------
    item_selected(DDOItem)
        Emitted when the user clicks a row.  Carries the full DDOItem.
    item_deselected()
        Emitted when selection is cleared.
    """

    item_selected: Signal = Signal(object)
    item_deselected: Signal = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._items: List[DDOItem] = []
        self._build_ui()

    # ── Build ──────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._count_label = QLabel("0 items")
        self._count_label.setObjectName("CountLabel")
        self._count_label.setContentsMargins(10, 6, 10, 4)
        layout.addWidget(self._count_label)

        self._table = QTableWidget(0, len(_COLUMNS))
        self._table.setHorizontalHeaderLabels(_COLUMNS)
        self._table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self._table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.setAlternatingRowColors(True)
        self._table.setSortingEnabled(True)
        self._table.verticalHeader().setVisible(False)
        self._table.setShowGrid(False)
        self._table.setWordWrap(False)
        self._table.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        hdr = self._table.horizontalHeader()
        hdr.setSectionResizeMode(
            _COL_NAME, QHeaderView.ResizeMode.Stretch
        )
        hdr.setSectionResizeMode(
            _COL_LEVEL, QHeaderView.ResizeMode.Fixed
        )
        hdr.setSectionResizeMode(
            _COL_SLOT, QHeaderView.ResizeMode.ResizeToContents
        )
        hdr.setSectionResizeMode(
            _COL_TYPE, QHeaderView.ResizeMode.ResizeToContents
        )
        hdr.setSectionResizeMode(
            _COL_BIND, QHeaderView.ResizeMode.ResizeToContents
        )
        hdr.setSectionResizeMode(
            _COL_ENCH, QHeaderView.ResizeMode.Stretch
        )
        self._table.setColumnWidth(_COL_LEVEL, 52)

        self._table.verticalHeader().setDefaultSectionSize(28)
        self._table.itemSelectionChanged.connect(self._on_selection_changed)

        layout.addWidget(self._table)

    # ── Public ─────────────────────────────────────────────────────────

    def load_items(self, items: List[DDOItem]) -> None:
        self._items = items
        self._table.setSortingEnabled(False)
        self._table.setRowCount(0)
        self._table.setRowCount(len(items))

        gold = QColor(COLORS["accent_gold"])
        muted = QColor(COLORS["text_muted"])

        for row, item in enumerate(items):
            # Name
            name_cell = QTableWidgetItem(item.name)
            name_cell.setData(Qt.ItemDataRole.UserRole, item)
            self._table.setItem(row, _COL_NAME, name_cell)

            # Level  (numeric sort via QTableWidgetItem with int role)
            lvl = item.minimum_level
            lvl_cell = QTableWidgetItem()
            lvl_cell.setData(Qt.ItemDataRole.DisplayRole, lvl if lvl is not None else "")
            lvl_cell.setData(Qt.ItemDataRole.UserRole + 1, lvl if lvl is not None else -1)
            lvl_cell.setTextAlignment(
                Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter
            )
            if lvl is None:
                lvl_cell.setForeground(muted)
            self._table.setItem(row, _COL_LEVEL, lvl_cell)

            # Slot
            slot_cell = QTableWidgetItem(item.slot or "")
            self._table.setItem(row, _COL_SLOT, slot_cell)

            # Type
            type_cell = QTableWidgetItem(item.item_type or "")
            self._table.setItem(row, _COL_TYPE, type_cell)

            # Binding
            bind_cell = QTableWidgetItem(_shorten_binding(item.binding))
            if item.binding and "Character" in item.binding:
                bind_cell.setForeground(gold)
            self._table.setItem(row, _COL_BIND, bind_cell)

            # Enchantments
            ench_cell = QTableWidgetItem(_enchant_summary(item))
            ench_cell.setForeground(QColor(COLORS["text_secondary"]))
            self._table.setItem(row, _COL_ENCH, ench_cell)

        self._table.setSortingEnabled(True)
        self._update_count_label()

    def clear_selection(self) -> None:
        self._table.clearSelection()

    def selected_item(self) -> Optional[DDOItem]:
        rows = self._table.selectedItems()
        if not rows:
            return None
        return self._table.item(rows[0].row(), _COL_NAME).data(Qt.ItemDataRole.UserRole)

    # ── Private ────────────────────────────────────────────────────────

    def _on_selection_changed(self) -> None:
        item = self.selected_item()
        if item is not None:
            self.item_selected.emit(item)
        else:
            self.item_deselected.emit()

    def _update_count_label(self) -> None:
        n = self._table.rowCount()
        self._count_label.setText(f"{n} item{'s' if n != 1 else ''}")
