"""Left-sidebar filter panel for the DDOLoot item browser."""

from __future__ import annotations

from PySide6.QtCore import QTimer, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from item_db import ItemFilter

# ── Slot / type / binding value lists ────────────────────────────────────────

_SLOTS = [
    "", "Back", "Belt", "Body", "Bracers", "Eyes", "Feet",
    "Finger", "Hand", "Head", "Legs", "Neck", "Off-Hand",
    "Primary", "Quiver", "Trinket",
]

_ITEM_TYPES = [
    "", "Armor", "Belt", "Boots", "Bracers", "Cloak", "Docent",
    "Gloves", "Goggles", "Helmet", "Necklace", "Ring", "Shield", "Trinket",
]

_BINDINGS = [
    "",
    "Bound to Character on Acquire",
    "Bound to Account on Acquire",
    "Bound to Character on Equip",
    "Unbound",
]

_ARMOR_TYPES = ["", "Light", "Medium", "Heavy", "Docent", "Shield", "Tower Shield"]

_HANDEDNESS = ["", "One-Handed", "Two-Handed"]

_SEARCH_DEBOUNCE_MS = 320


def _section_label(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setObjectName("SectionHeader")
    return lbl


def _divider() -> QFrame:
    line = QFrame()
    line.setObjectName("Divider")
    line.setFrameShape(QFrame.Shape.HLine)
    return line


class FilterPanel(QWidget):
    """Emits ``filter_changed`` whenever the user modifies any control.

    Signals
    -------
    filter_changed(ItemFilter)
        The newly constructed filter ready to pass to ItemRepository.search().
    """

    filter_changed: Signal = Signal(object)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("FilterPanel")
        self.setFixedWidth(260)
        self._debounce = QTimer(self)
        self._debounce.setSingleShot(True)
        self._debounce.setInterval(_SEARCH_DEBOUNCE_MS)
        self._debounce.timeout.connect(self._emit_filter)
        self._build_ui()

    # ── Build ──────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(
            scroll.horizontalScrollBarPolicy().ScrollBarAlwaysOff
        )
        outer.addWidget(scroll)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        scroll.setWidget(container)

        # ── Title ──────────────────────────────────────────────────────
        title = QLabel("FILTERS")
        title.setObjectName("SectionHeader")
        layout.addWidget(title)
        layout.addWidget(_divider())

        # ── Name search ────────────────────────────────────────────────
        layout.addWidget(_section_label("NAME"))
        self._name_edit = QLineEdit()
        self._name_edit.setPlaceholderText("Search by name…")
        self._name_edit.setClearButtonEnabled(True)
        self._name_edit.textChanged.connect(self._debounce.start)
        layout.addWidget(self._name_edit)

        # ── Slot ───────────────────────────────────────────────────────
        layout.addSpacing(4)
        layout.addWidget(_section_label("SLOT"))
        self._slot_combo = QComboBox()
        self._slot_combo.addItems([s if s else "All Slots" for s in _SLOTS])
        self._slot_combo.currentIndexChanged.connect(self._emit_filter)
        layout.addWidget(self._slot_combo)

        # ── Item type ──────────────────────────────────────────────────
        layout.addSpacing(4)
        layout.addWidget(_section_label("ITEM TYPE"))
        self._type_combo = QComboBox()
        self._type_combo.addItems([t if t else "All Types" for t in _ITEM_TYPES])
        self._type_combo.currentIndexChanged.connect(self._emit_filter)
        layout.addWidget(self._type_combo)

        # ── Level range ────────────────────────────────────────────────
        layout.addSpacing(4)
        layout.addWidget(_section_label("MINIMUM LEVEL"))
        level_row = QHBoxLayout()
        level_row.setSpacing(6)
        self._level_min = QSpinBox()
        self._level_min.setRange(0, 32)
        self._level_min.setSpecialValueText("Any")
        self._level_min.valueChanged.connect(self._emit_filter)
        self._level_max = QSpinBox()
        self._level_max.setRange(0, 32)
        self._level_max.setSpecialValueText("Any")
        self._level_max.setValue(0)
        self._level_max.valueChanged.connect(self._emit_filter)
        lbl_to = QLabel("to")
        lbl_to.setObjectName("StatKey")
        lbl_to.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        level_row.addWidget(self._level_min)
        level_row.addWidget(lbl_to)
        level_row.addWidget(self._level_max)
        layout.addLayout(level_row)

        # ── Binding ────────────────────────────────────────────────────
        layout.addSpacing(4)
        layout.addWidget(_section_label("BINDING"))
        self._binding_combo = QComboBox()
        self._binding_combo.addItems([b if b else "Any Binding" for b in _BINDINGS])
        self._binding_combo.currentIndexChanged.connect(self._emit_filter)
        layout.addWidget(self._binding_combo)

        layout.addWidget(_divider())

        # ── Enchantment ────────────────────────────────────────────────
        layout.addWidget(_section_label("HAS ENCHANTMENT"))
        self._enchant_edit = QLineEdit()
        self._enchant_edit.setPlaceholderText("e.g. Resistance")
        self._enchant_edit.setClearButtonEnabled(True)
        self._enchant_edit.textChanged.connect(self._debounce.start)
        layout.addWidget(self._enchant_edit)

        # ── Named set ──────────────────────────────────────────────────
        layout.addSpacing(4)
        layout.addWidget(_section_label("NAMED SET"))
        self._set_edit = QLineEdit()
        self._set_edit.setPlaceholderText("e.g. Slavelord's")
        self._set_edit.setClearButtonEnabled(True)
        self._set_edit.textChanged.connect(self._debounce.start)
        layout.addWidget(self._set_edit)

        # ── Quest drop ─────────────────────────────────────────────────
        layout.addSpacing(4)
        layout.addWidget(_section_label("DROPS IN QUEST"))
        self._quest_edit = QLineEdit()
        self._quest_edit.setPlaceholderText("e.g. Chronoscope")
        self._quest_edit.setClearButtonEnabled(True)
        self._quest_edit.textChanged.connect(self._debounce.start)
        layout.addWidget(self._quest_edit)

        layout.addWidget(_divider())

        # ── Armor type ─────────────────────────────────────────────────
        layout.addWidget(_section_label("ARMOR TYPE"))
        self._armor_combo = QComboBox()
        self._armor_combo.addItems([a if a else "Any Armor" for a in _ARMOR_TYPES])
        self._armor_combo.currentIndexChanged.connect(self._emit_filter)
        layout.addWidget(self._armor_combo)

        # ── Handedness ─────────────────────────────────────────────────
        layout.addSpacing(4)
        layout.addWidget(_section_label("HANDEDNESS"))
        self._hand_combo = QComboBox()
        self._hand_combo.addItems([h if h else "Any" for h in _HANDEDNESS])
        self._hand_combo.currentIndexChanged.connect(self._emit_filter)
        layout.addWidget(self._hand_combo)

        layout.addWidget(_divider())

        # ── Restriction checkboxes ─────────────────────────────────────
        self._excl_race = QCheckBox("Exclude race-restricted")
        self._excl_race.stateChanged.connect(self._emit_filter)
        self._excl_class = QCheckBox("Exclude class-restricted")
        self._excl_class.stateChanged.connect(self._emit_filter)
        layout.addWidget(self._excl_race)
        layout.addWidget(self._excl_class)

        layout.addWidget(_divider())

        # ── Clear button ───────────────────────────────────────────────
        btn_clear = QPushButton("Clear All Filters")
        btn_clear.setObjectName("ClearButton")
        btn_clear.clicked.connect(self.clear)
        layout.addWidget(btn_clear)

        layout.addStretch()

    # ── Public ────────────────────────────────────────────────────────

    def get_filter(self) -> ItemFilter:
        f: dict = {}

        name = self._name_edit.text().strip()
        if name:
            f["name_contains"] = name

        slot_idx = self._slot_combo.currentIndex()
        if slot_idx > 0:
            f["slot"] = _SLOTS[slot_idx]

        type_idx = self._type_combo.currentIndex()
        if type_idx > 0:
            f["item_type"] = _ITEM_TYPES[type_idx]

        lmin = self._level_min.value()
        lmax = self._level_max.value()
        if lmin > 0:
            f["minimum_level_min"] = lmin
        if lmax > 0:
            f["minimum_level_max"] = lmax

        bind_idx = self._binding_combo.currentIndex()
        if bind_idx > 0:
            f["binding"] = _BINDINGS[bind_idx]

        enchant = self._enchant_edit.text().strip()
        if enchant:
            f["has_enchantment"] = enchant

        named_set = self._set_edit.text().strip()
        if named_set:
            f["named_set"] = named_set

        quest = self._quest_edit.text().strip()
        if quest:
            f["drops_in_quest"] = quest

        armor_idx = self._armor_combo.currentIndex()
        if armor_idx > 0:
            f["armor_type"] = _ARMOR_TYPES[armor_idx]

        hand_idx = self._hand_combo.currentIndex()
        if hand_idx > 0:
            f["handedness"] = _HANDEDNESS[hand_idx]

        if self._excl_race.isChecked():
            f["exclude_race_restricted"] = True
        if self._excl_class.isChecked():
            f["exclude_class_restricted"] = True

        return ItemFilter(**f)

    def clear(self) -> None:
        for widget in [self._name_edit, self._enchant_edit, self._set_edit, self._quest_edit]:
            widget.blockSignals(True)
            widget.clear()
            widget.blockSignals(False)
        for combo in [self._slot_combo, self._type_combo, self._binding_combo,
                      self._armor_combo, self._hand_combo]:
            combo.blockSignals(True)
            combo.setCurrentIndex(0)
            combo.blockSignals(False)
        for spin in [self._level_min, self._level_max]:
            spin.blockSignals(True)
            spin.setValue(0)
            spin.blockSignals(False)
        for cb in [self._excl_race, self._excl_class]:
            cb.blockSignals(True)
            cb.setChecked(False)
            cb.blockSignals(False)
        self._emit_filter()

    # ── Private ───────────────────────────────────────────────────────

    def _emit_filter(self) -> None:
        self.filter_changed.emit(self.get_filter())
