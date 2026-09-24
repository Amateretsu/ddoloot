"""Dark DDO-inspired color palette and Qt stylesheet."""

COLORS = {
    "bg_dark": "#0e0e0e",
    "bg_medium": "#181818",
    "bg_light": "#242424",
    "bg_input": "#1c1c1c",
    "bg_selected": "#2e2510",
    "bg_hover": "#1e1a0e",
    "border": "#333333",
    "border_focus": "#c9a84c",
    "accent_gold": "#c9a84c",
    "accent_gold_dim": "#7a6028",
    "accent_gold_bright": "#e8c46a",
    "text_primary": "#e8e8e8",
    "text_secondary": "#a0a0a0",
    "text_muted": "#555555",
    "text_gold": "#c9a84c",
    "text_link": "#6aabe8",
    "success": "#4caf50",
    "success_dim": "#1a3a1a",
    "warning": "#ff9800",
    "error": "#e05c5c",
    "error_dim": "#3a1a1a",
    "in_progress": "#4a8fd4",
}

C = COLORS

STYLESHEET = f"""
/* ── Base ─────────────────────────────────────────────────────────────── */

QMainWindow, QDialog {{
    background-color: {C['bg_dark']};
}}

QWidget {{
    background-color: {C['bg_dark']};
    color: {C['text_primary']};
    font-family: "Segoe UI", "SF Pro Text", Arial, sans-serif;
    font-size: 13px;
}}

/* ── Panels / Frames ─────────────────────────────────────────────────── */

QFrame#FilterPanel {{
    background-color: {C['bg_medium']};
    border-right: 1px solid {C['border']};
}}

QFrame#DetailPanel {{
    background-color: {C['bg_medium']};
    border-left: 1px solid {C['border']};
}}

QFrame#SyncBar {{
    background-color: {C['bg_medium']};
    border-bottom: 1px solid {C['border']};
}}

QFrame#Divider {{
    background-color: {C['border']};
    max-height: 1px;
    min-height: 1px;
}}

/* ── Labels ──────────────────────────────────────────────────────────── */

QLabel {{
    background-color: transparent;
    color: {C['text_primary']};
}}

QLabel#SectionHeader {{
    color: {C['accent_gold']};
    font-size: 10px;
    font-weight: bold;
    letter-spacing: 2px;
    background-color: transparent;
}}

QLabel#ItemName {{
    color: {C['text_primary']};
    font-size: 17px;
    font-weight: bold;
    background-color: transparent;
}}

QLabel#ItemSubtitle {{
    color: {C['text_secondary']};
    font-size: 12px;
    background-color: transparent;
}}

QLabel#StatKey {{
    color: {C['text_secondary']};
    font-size: 12px;
    background-color: transparent;
}}

QLabel#StatValue {{
    color: {C['text_primary']};
    font-size: 12px;
    background-color: transparent;
}}

QLabel#EnchantName {{
    color: {C['accent_gold_bright']};
    font-size: 12px;
    background-color: transparent;
}}

QLabel#EnchantValue {{
    color: {C['text_secondary']};
    font-size: 12px;
    background-color: transparent;
}}

QLabel#FlavorText {{
    color: {C['text_secondary']};
    font-style: italic;
    font-size: 12px;
    background-color: transparent;
}}

QLabel#CountLabel {{
    color: {C['text_muted']};
    font-size: 11px;
    background-color: transparent;
}}

QLabel#StatBadge {{
    color: {C['text_muted']};
    font-size: 11px;
    padding: 0 6px;
    background-color: transparent;
}}

QLabel#StatBadge[role="pending"] {{ color: {C['warning']}; }}
QLabel#StatBadge[role="complete"] {{ color: {C['success']}; }}
QLabel#StatBadge[role="failed"] {{ color: {C['error']}; }}
QLabel#StatBadge[role="in_progress"] {{ color: {C['in_progress']}; }}

/* ── Inputs ──────────────────────────────────────────────────────────── */

QLineEdit {{
    background-color: {C['bg_input']};
    border: 1px solid {C['border']};
    border-radius: 4px;
    color: {C['text_primary']};
    padding: 5px 8px;
    selection-background-color: {C['accent_gold_dim']};
}}

QLineEdit:focus {{
    border-color: {C['border_focus']};
}}

QLineEdit::placeholder {{
    color: {C['text_muted']};
}}

QSpinBox {{
    background-color: {C['bg_input']};
    border: 1px solid {C['border']};
    border-radius: 4px;
    color: {C['text_primary']};
    padding: 4px 6px;
    selection-background-color: {C['accent_gold_dim']};
}}

QSpinBox:focus {{
    border-color: {C['border_focus']};
}}

QSpinBox::up-button, QSpinBox::down-button {{
    background-color: {C['bg_light']};
    border: none;
    width: 18px;
}}

QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
    background-color: {C['accent_gold_dim']};
}}

QComboBox {{
    background-color: {C['bg_input']};
    border: 1px solid {C['border']};
    border-radius: 4px;
    color: {C['text_primary']};
    padding: 5px 8px;
    selection-background-color: {C['accent_gold_dim']};
}}

QComboBox:focus {{
    border-color: {C['border_focus']};
}}

QComboBox::drop-down {{
    border: none;
    width: 22px;
    border-left: 1px solid {C['border']};
}}

QComboBox::down-arrow {{
    width: 10px;
    height: 10px;
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid {C['text_secondary']};
    margin-right: 4px;
}}

QComboBox QAbstractItemView {{
    background-color: {C['bg_light']};
    border: 1px solid {C['border_focus']};
    color: {C['text_primary']};
    selection-background-color: {C['accent_gold_dim']};
    outline: none;
}}

/* ── Buttons ─────────────────────────────────────────────────────────── */

QPushButton {{
    background-color: {C['bg_light']};
    border: 1px solid {C['border']};
    border-radius: 4px;
    color: {C['text_primary']};
    padding: 6px 16px;
    font-size: 12px;
}}

QPushButton:hover {{
    background-color: {C['bg_hover']};
    border-color: {C['accent_gold_dim']};
    color: {C['accent_gold']};
}}

QPushButton:pressed {{
    background-color: {C['accent_gold_dim']};
    border-color: {C['accent_gold']};
    color: {C['accent_gold_bright']};
}}

QPushButton:disabled {{
    background-color: {C['bg_medium']};
    border-color: {C['text_muted']};
    color: {C['text_muted']};
}}

QPushButton#SyncButton {{
    background-color: {C['success_dim']};
    border: 1px solid {C['success']};
    color: {C['success']};
    font-weight: bold;
    padding: 6px 20px;
    font-size: 12px;
}}

QPushButton#SyncButton:hover {{
    background-color: #254025;
    color: #6fcf73;
}}

QPushButton#SyncButton:disabled {{
    background-color: {C['bg_medium']};
    border-color: {C['text_muted']};
    color: {C['text_muted']};
}}

QPushButton#StopButton {{
    background-color: {C['error_dim']};
    border: 1px solid {C['error']};
    color: {C['error']};
    font-size: 12px;
    padding: 6px 16px;
}}

QPushButton#StopButton:hover {{
    background-color: #4a2020;
}}

QPushButton#ClearButton {{
    background-color: transparent;
    border: 1px solid {C['border']};
    color: {C['text_secondary']};
    font-size: 11px;
    padding: 4px 10px;
}}

QPushButton#ClearButton:hover {{
    border-color: {C['text_secondary']};
    color: {C['text_primary']};
}}

QPushButton#ApplyButton {{
    background-color: {C['accent_gold_dim']};
    border: 1px solid {C['accent_gold']};
    color: {C['accent_gold_bright']};
    font-size: 12px;
    padding: 5px 14px;
}}

QPushButton#ApplyButton:hover {{
    background-color: #9a7535;
}}

QPushButton#WikiLink {{
    background-color: transparent;
    border: none;
    color: {C['text_link']};
    text-decoration: underline;
    font-size: 11px;
    padding: 0;
    text-align: left;
}}

QPushButton#WikiLink:hover {{
    color: #8ac9ff;
    background-color: transparent;
}}

/* ── Table ────────────────────────────────────────────────────────────── */

QTableWidget {{
    background-color: {C['bg_medium']};
    border: none;
    gridline-color: {C['border']};
    color: {C['text_primary']};
    selection-background-color: {C['bg_selected']};
    selection-color: {C['text_primary']};
    outline: none;
    alternate-background-color: #161616;
}}

QTableWidget::item {{
    padding: 4px 10px;
    border-bottom: 1px solid #202020;
}}

QTableWidget::item:selected {{
    background-color: {C['bg_selected']};
    color: {C['text_primary']};
}}

QTableWidget::item:hover {{
    background-color: {C['bg_hover']};
}}

QHeaderView {{
    background-color: {C['bg_light']};
}}

QHeaderView::section {{
    background-color: {C['bg_light']};
    color: {C['accent_gold']};
    border: none;
    border-bottom: 2px solid {C['accent_gold_dim']};
    border-right: 1px solid {C['border']};
    padding: 6px 10px;
    font-weight: bold;
    font-size: 11px;
    letter-spacing: 1px;
}}

QHeaderView::section:last {{
    border-right: none;
}}

QHeaderView::section:hover {{
    background-color: {C['bg_hover']};
    color: {C['accent_gold_bright']};
}}

/* ── Scrollbars ──────────────────────────────────────────────────────── */

QScrollBar:vertical {{
    background-color: {C['bg_dark']};
    width: 8px;
    border-radius: 4px;
    margin: 0;
}}

QScrollBar::handle:vertical {{
    background-color: #3a3a3a;
    border-radius: 4px;
    min-height: 24px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {C['accent_gold_dim']};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

QScrollBar:horizontal {{
    background-color: {C['bg_dark']};
    height: 8px;
    border-radius: 4px;
    margin: 0;
}}

QScrollBar::handle:horizontal {{
    background-color: #3a3a3a;
    border-radius: 4px;
    min-width: 24px;
}}

QScrollBar::handle:horizontal:hover {{
    background-color: {C['accent_gold_dim']};
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0;
}}

/* ── CheckBox ────────────────────────────────────────────────────────── */

QCheckBox {{
    background-color: transparent;
    color: {C['text_secondary']};
    spacing: 6px;
    font-size: 12px;
}}

QCheckBox::indicator {{
    width: 14px;
    height: 14px;
    border: 1px solid {C['border']};
    border-radius: 3px;
    background-color: {C['bg_input']};
}}

QCheckBox::indicator:checked {{
    background-color: {C['accent_gold_dim']};
    border-color: {C['accent_gold']};
}}

QCheckBox::indicator:hover {{
    border-color: {C['accent_gold_dim']};
}}

/* ── Progress Bar ────────────────────────────────────────────────────── */

QProgressBar {{
    background-color: {C['bg_light']};
    border: 1px solid {C['border']};
    border-radius: 3px;
    text-align: center;
    color: transparent;
    max-height: 4px;
    min-height: 4px;
}}

QProgressBar::chunk {{
    background-color: {C['accent_gold']};
    border-radius: 3px;
}}

/* ── Splitter ─────────────────────────────────────────────────────────── */

QSplitter::handle {{
    background-color: {C['border']};
}}

QSplitter::handle:horizontal {{
    width: 1px;
}}

/* ── ScrollArea ──────────────────────────────────────────────────────── */

QScrollArea {{
    border: none;
    background-color: transparent;
}}

QScrollArea > QWidget > QWidget {{
    background-color: transparent;
}}

/* ── Status Bar ──────────────────────────────────────────────────────── */

QStatusBar {{
    background-color: {C['bg_medium']};
    color: {C['text_muted']};
    border-top: 1px solid {C['border']};
    font-size: 11px;
}}

/* ── ToolTip ─────────────────────────────────────────────────────────── */

QToolTip {{
    background-color: {C['bg_light']};
    border: 1px solid {C['accent_gold_dim']};
    color: {C['text_primary']};
    padding: 4px 8px;
    font-size: 12px;
}}
"""
