"""Main application window — three-panel layout with sync toolbar."""

from __future__ import annotations

from typing import List

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow,
    QMessageBox,
    QSplitter,
    QStatusBar,
    QWidget,
)

from ddoloot_ui._paths import LOOT_DB, QUEUE_DB
from ddoloot_ui.widgets.filter_panel import FilterPanel
from ddoloot_ui.widgets.item_detail import ItemDetail
from ddoloot_ui.widgets.item_table import ItemTable
from ddoloot_ui.widgets.sync_toolbar import SyncToolbar
from ddoloot_ui.workers.sync_worker import ResetFailedWorker, SyncWorker
from ddo_sync import QueueRepository
from ddo_sync.models import QueueStats
from item_db import ItemFilter, ItemRepository
from item_normalizer.models import DDOItem


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("DDOLoot")
        self.resize(1280, 800)
        self.setMinimumSize(800, 500)

        self._sync_worker: SyncWorker | None = None
        self._reset_worker: ResetFailedWorker | None = None

        self._build_ui()
        self._refresh_items(ItemFilter())
        self._refresh_stats()

    # ── Build ──────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        # Central widget holds the toolbar + splitter
        central = QWidget()
        self.setCentralWidget(central)

        from PySide6.QtWidgets import QVBoxLayout
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ── Sync toolbar ───────────────────────────────────────────────
        self._toolbar = SyncToolbar()
        self._toolbar.sync_requested.connect(self._on_sync_requested)
        self._toolbar.reset_failed_requested.connect(self._on_reset_failed)
        self._toolbar.stop_requested.connect(self._on_stop_requested)
        root_layout.addWidget(self._toolbar)

        # ── Three-panel splitter ───────────────────────────────────────
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)

        self._filter_panel = FilterPanel()
        self._filter_panel.filter_changed.connect(self._on_filter_changed)
        splitter.addWidget(self._filter_panel)

        self._item_table = ItemTable()
        self._item_table.item_selected.connect(self._detail_panel.show_item
                                               if hasattr(self, "_detail_panel")
                                               else lambda _: None)
        splitter.addWidget(self._item_table)

        self._detail_panel = ItemDetail()
        splitter.addWidget(self._detail_panel)

        # Wire table → detail (replaces the placeholder lambda above)
        self._item_table.item_selected.connect(self._detail_panel.show_item)
        self._item_table.item_deselected.connect(self._detail_panel.clear)

        splitter.setSizes([260, 620, 400])
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setStretchFactor(2, 0)

        root_layout.addWidget(splitter)

        # ── Status bar ─────────────────────────────────────────────────
        sb = QStatusBar()
        self.setStatusBar(sb)
        self._status_bar = sb
        self._update_status_bar()

    # ── Slots ──────────────────────────────────────────────────────────

    def _on_filter_changed(self, f: ItemFilter) -> None:
        self._refresh_items(f)

    def _on_sync_requested(self) -> None:
        if self._sync_worker and self._sync_worker.isRunning():
            return
        self._toolbar.set_syncing(True)
        self._sync_worker = SyncWorker(parent=self)
        self._sync_worker.message.connect(self._toolbar.set_message)
        self._sync_worker.stats_updated.connect(self._on_stats_updated)
        self._sync_worker.finished.connect(self._on_sync_finished)
        self._sync_worker.start()

    def _on_stop_requested(self) -> None:
        if self._sync_worker:
            self._sync_worker.request_stop()
            self._toolbar.set_message("Stopping after current item…")

    def _on_reset_failed(self) -> None:
        if self._reset_worker and self._reset_worker.isRunning():
            return
        self._reset_worker = ResetFailedWorker(parent=self)
        self._reset_worker.finished.connect(self._on_reset_done)
        self._reset_worker.start()

    def _on_stats_updated(self, stats: QueueStats) -> None:
        self._toolbar.update_stats(stats)

    def _on_sync_finished(self, success: bool, message: str) -> None:
        self._toolbar.set_syncing(False)
        self._toolbar.set_message("")
        self._refresh_items(self._filter_panel.get_filter())
        self._refresh_stats()
        self._update_status_bar()
        if not success and "Stopped" not in message:
            QMessageBox.warning(self, "Sync Error", message)

    def _on_reset_done(self, count: int) -> None:
        self._refresh_stats()
        msg = f"Reset {count} failed item(s) to pending." if count else "No failed items to reset."
        self._status_bar.showMessage(msg, 4000)

    # ── Helpers ────────────────────────────────────────────────────────

    def _refresh_items(self, f: ItemFilter) -> None:
        if not LOOT_DB.exists():
            self._item_table.load_items([])
            self._update_status_bar()
            return
        try:
            with ItemRepository(str(LOOT_DB)) as repo:
                items: List[DDOItem] = repo.search(f)
            self._item_table.load_items(items)
            self._detail_panel.clear()
        except Exception as exc:  # noqa: BLE001
            self._status_bar.showMessage(f"DB error: {exc}", 5000)

    def _refresh_stats(self) -> None:
        if not QUEUE_DB.exists():
            return
        try:
            with QueueRepository(str(QUEUE_DB)) as qr:
                stats = qr.get_queue_stats()
            self._toolbar.update_stats(stats)
        except Exception:  # noqa: BLE001
            pass

    def _update_status_bar(self) -> None:
        if not LOOT_DB.exists():
            self._status_bar.showMessage(
                f"No database found at {LOOT_DB} — run a sync to populate it."
            )
        else:
            self._status_bar.clearMessage()

    # ── Lifecycle ──────────────────────────────────────────────────────

    def closeEvent(self, event) -> None:
        if self._sync_worker and self._sync_worker.isRunning():
            self._sync_worker.request_stop()
            self._sync_worker.wait(3000)
        super().closeEvent(event)
