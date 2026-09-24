"""Background QThread that drives a full DDOLoot sync cycle."""

from __future__ import annotations

import asyncio

from PySide6.QtCore import QThread, Signal

from ddoloot_ui._paths import DATA_DIR, LOOT_DB, QUEUE_DB
from ddo_sync import DDOSyncer, QueueRepository
from ddo_sync.exceptions import UpdatePageError
from ddo_sync.models import QueueStats
from ddo_sync.page_discovery import UpdatePageDiscoverer
from ddowiki_scraper import WikiFetcher, WikiFetcherConfig
from item_db import ItemRepository
from item_normalizer import ItemNormalizer


class SyncWorker(QThread):
    """Runs discover → register → refresh → process in a background thread.

    Signals
    -------
    message(str)
        Human-readable status line to display in the toolbar.
    stats_updated(QueueStats)
        Emitted after each item is processed so the UI can update counts.
    finished(bool, str)
        Emitted when the sync ends; bool is True on clean success, str is a
        summary message.
    """

    message: Signal = Signal(str)
    stats_updated: Signal = Signal(object)
    finished: Signal = Signal(bool, str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._stop_requested = False

    def request_stop(self) -> None:
        self._stop_requested = True

    # ------------------------------------------------------------------

    def run(self) -> None:
        self._stop_requested = False
        # aiohttp (used by WikiApiClient) requires an event loop in every thread.
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            self._sync()
        except Exception as exc:  # noqa: BLE001
            self.finished.emit(False, f"Fatal error: {exc}")
        finally:
            loop.close()

    def _sync(self) -> None:
        DATA_DIR.mkdir(parents=True, exist_ok=True)

        cfg = WikiFetcherConfig(rate_limit_delay=2.5, max_retries=3, timeout=30)

        with (
            WikiFetcher(cfg) as fetcher,
            ItemRepository(str(LOOT_DB)) as item_repo,
            QueueRepository(str(QUEUE_DB)) as queue_repo,
        ):
            syncer = DDOSyncer(
                fetcher=fetcher,
                normalizer=ItemNormalizer(),
                item_repo=item_repo,
                queue_repo=queue_repo,
                max_retries=3,
            )

            # ── Discovery ──────────────────────────────────────────────
            self.message.emit("Discovering update pages…")
            try:
                pages = UpdatePageDiscoverer().discover()
                for page in pages:
                    syncer.register_update_page(page)
                self.message.emit(f"Found {len(pages)} update pages")
            except Exception as exc:  # noqa: BLE001
                self.message.emit(f"Discovery error: {exc}")

            if self._stop_requested:
                self.finished.emit(False, "Stopped by user")
                return

            # ── Reset previously failed items ──────────────────────────
            reset_count = queue_repo.reset_failed_to_pending(syncer._max_retries)
            if reset_count:
                self.message.emit(f"Reset {reset_count} failed item(s) to pending")

            # ── Refresh wiki timestamps & re-sync stale pages ──────────
            for page_status in queue_repo.list_update_pages():
                if self._stop_requested:
                    break
                try:
                    syncer._refresh_wiki_timestamp(page_status.page_name)
                    updated = queue_repo.get_update_page_status(page_status.page_name)
                    if updated and updated.needs_resync:
                        self.message.emit(f"Syncing page: {page_status.page_name}")
                        syncer.sync_update_page(page_status.page_name)
                except UpdatePageError as exc:
                    self.message.emit(f"Page error: {exc}")
                except Exception as exc:  # noqa: BLE001
                    self.message.emit(f"Unexpected error: {exc}")

            self.stats_updated.emit(queue_repo.get_queue_stats())

            if self._stop_requested:
                self.finished.emit(False, "Stopped by user")
                return

            # ── Process queue one item at a time for live progress ─────
            self.message.emit("Processing item queue…")
            while not self._stop_requested:
                stats: QueueStats = queue_repo.get_queue_stats()
                if stats.pending == 0:
                    break
                try:
                    syncer.process_queue(limit=1)
                except Exception as exc:  # noqa: BLE001
                    self.message.emit(f"Item error: {exc}")
                self.stats_updated.emit(queue_repo.get_queue_stats())

            # ── Wrap up ────────────────────────────────────────────────
            final: QueueStats = queue_repo.get_queue_stats()
            self.stats_updated.emit(final)

            if self._stop_requested:
                self.finished.emit(False, "Stopped by user")
            else:
                ok = final.failed == 0
                msg = (
                    f"Sync complete — {final.complete} items"
                    + (f", {final.failed} failed" if final.failed else "")
                )
                self.finished.emit(ok, msg)


class ResetFailedWorker(QThread):
    """Resets all failed queue items back to pending."""

    finished: Signal = Signal(int)

    def run(self) -> None:
        try:
            with QueueRepository(str(QUEUE_DB)) as qr:
                count = qr.reset_failed_to_pending(max_retries=9999)
            self.finished.emit(count)
        except Exception:  # noqa: BLE001
            self.finished.emit(0)
