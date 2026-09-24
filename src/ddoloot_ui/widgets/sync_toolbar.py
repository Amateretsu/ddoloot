"""Top toolbar: sync controls + live queue statistics."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from ddo_sync.models import QueueStats
from ddoloot_ui.theme import COLORS

C = COLORS


def _stat_badge(role: str, label: str, value: int) -> QLabel:
    lbl = QLabel(f"{label}: {value}")
    lbl.setObjectName("StatBadge")
    lbl.setProperty("role", role)
    lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    lbl.setMinimumWidth(80)
    return lbl


class SyncToolbar(QWidget):
    """Horizontal bar with sync controls and queue-stats badges.

    Signals
    -------
    sync_requested()
    reset_failed_requested()
    stop_requested()
    """

    sync_requested: Signal = Signal()
    reset_failed_requested: Signal = Signal()
    stop_requested: Signal = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("SyncBar")
        self.setFixedHeight(72)
        self._build_ui()

    # ── Build ──────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(12, 8, 12, 4)
        outer.setSpacing(4)

        # Top row: controls + stats
        top_row = QHBoxLayout()
        top_row.setSpacing(8)

        # ── Controls ───────────────────────────────────────────────────
        self._sync_btn = QPushButton("▶  Run Sync")
        self._sync_btn.setObjectName("SyncButton")
        self._sync_btn.setToolTip("Discover all update pages and process the item queue")
        self._sync_btn.clicked.connect(self.sync_requested)
        top_row.addWidget(self._sync_btn)

        self._stop_btn = QPushButton("■  Stop")
        self._stop_btn.setObjectName("StopButton")
        self._stop_btn.setToolTip("Request a graceful stop after the current item")
        self._stop_btn.setVisible(False)
        self._stop_btn.clicked.connect(self.stop_requested)
        top_row.addWidget(self._stop_btn)

        self._reset_btn = QPushButton("↺  Reset Failed")
        self._reset_btn.setToolTip("Move all failed items back to pending")
        self._reset_btn.clicked.connect(self.reset_failed_requested)
        top_row.addWidget(self._reset_btn)

        top_row.addSpacing(16)

        # Vertical separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setStyleSheet(f"color: {C['border']};")
        top_row.addWidget(sep)

        top_row.addSpacing(8)

        # ── Stats badges ───────────────────────────────────────────────
        self._lbl_complete = _stat_badge("complete", "Complete", 0)
        self._lbl_pending = _stat_badge("pending", "Pending", 0)
        self._lbl_in_progress = _stat_badge("in_progress", "In Progress", 0)
        self._lbl_failed = _stat_badge("failed", "Failed", 0)

        for badge in [self._lbl_complete, self._lbl_pending,
                      self._lbl_in_progress, self._lbl_failed]:
            top_row.addWidget(badge)

        top_row.addStretch()

        # Message label
        self._msg_label = QLabel("")
        self._msg_label.setObjectName("StatKey")
        self._msg_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self._msg_label.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        top_row.addWidget(self._msg_label)

        outer.addLayout(top_row)

        # ── Progress bar (hidden until sync starts) ────────────────────
        self._progress = QProgressBar()
        self._progress.setRange(0, 0)  # indeterminate by default
        self._progress.setVisible(False)
        outer.addWidget(self._progress)

    # ── Public ─────────────────────────────────────────────────────────

    def update_stats(self, stats: QueueStats) -> None:
        self._lbl_complete.setText(f"Complete: {stats.complete}")
        self._lbl_pending.setText(f"Pending: {stats.pending}")
        self._lbl_in_progress.setText(f"In Progress: {stats.in_progress}")
        self._lbl_failed.setText(f"Failed: {stats.failed}")

        # Switch progress bar to determinate once we know the total
        total = stats.pending + stats.in_progress + stats.complete
        if total > 0 and stats.complete > 0:
            self._progress.setRange(0, total)
            self._progress.setValue(stats.complete)

        # Re-apply stylesheet so dynamic property colours update
        for lbl in [self._lbl_complete, self._lbl_pending,
                    self._lbl_in_progress, self._lbl_failed]:
            lbl.style().unpolish(lbl)
            lbl.style().polish(lbl)

    def set_message(self, text: str) -> None:
        self._msg_label.setText(text)

    def set_syncing(self, syncing: bool) -> None:
        self._sync_btn.setVisible(not syncing)
        self._stop_btn.setVisible(syncing)
        self._reset_btn.setEnabled(not syncing)
        self._progress.setVisible(syncing)
        if not syncing:
            self._msg_label.clear()
            self._progress.setRange(0, 1)
            self._progress.setValue(0)
