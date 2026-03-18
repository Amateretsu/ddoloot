"""ddo_sync usage examples.

Demonstrates the full DDOSyncer pipeline using mocked external dependencies
(no real HTTP requests, no real item_db writes). All queue state is persisted
to an in-memory SQLite database so you can run this script without any setup.

Run:
    python examples/ddo_sync_example.py

Examples covered:
    1.  Register and inspect update page state
    2.  Parse item links from a local HTML snippet
    3.  Enqueue items and inspect queue stats
    4.  Process the queue with a mock scraper
    5.  Retry logic — reset failed items
    6.  Full sync_all cycle
    7.  Status snapshot (SyncStatus)
    8.  File-based queue database (persistent across runs)
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock

# ── Ensure src/ is on the path when running without editable install ──────────
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from ddo_sync import (
    DDOSyncer,
    ItemLink,
    QueueRepository,
    UpdatePageParser,
    WikiApiClient,
)

UTC = timezone.utc
DIVIDER = "-" * 60

# ── Minimal HTML that mimics a DDO Wiki update page ───────────────────────────
SAMPLE_HTML = """
<html>
<body>
  <div id="mw-content-text">
    <p>Named items added in Update 5:</p>
    <ul>
      <li><a href="/page/Item:Cloak_of_Shadows">Cloak of Shadows</a></li>
      <li><a href="/page/Item:Sword_of_Light">Sword of Light</a></li>
      <li><a href="/page/Item:Ring_of_Fire">Ring of Fire</a></li>
    </ul>
    <!-- duplicate should be deduplicated -->
    <a href="/page/Item:Cloak_of_Shadows">Cloak of Shadows</a>
  </div>
</body>
</html>
"""

PAGE_NAME = "Update_5_named_items"


# ── Example 1: Register update pages and inspect initial state ────────────────
print(DIVIDER)
print("Example 1: Register update pages")
print(DIVIDER)

with QueueRepository(":memory:") as qr:
    qr.register_update_page(PAGE_NAME, f"https://ddowiki.com/page/{PAGE_NAME}")
    qr.register_update_page("Update_6_named_items", "https://ddowiki.com/page/Update_6_named_items")

    pages = qr.list_update_pages()
    for p in pages:
        print(f"  {p.page_name}")
        print(f"    url:              {p.page_url}")
        print(f"    last_synced_at:   {p.last_synced_at}")
        print(f"    wiki_modified_at: {p.wiki_modified_at}")
        print(f"    needs_resync:     {p.needs_resync}")

print()


# ── Example 2: Parse item links from HTML ─────────────────────────────────────
print(DIVIDER)
print("Example 2: Parse item links with UpdatePageParser")
print(DIVIDER)

parser = UpdatePageParser(base_url="https://ddowiki.com")
links = parser.parse(SAMPLE_HTML, PAGE_NAME)

print(f"  Found {len(links)} unique item links:")
for lnk in links:
    print(f"    {lnk.item_name:30s}  {lnk.wiki_url}")

print()


# ── Example 3: Enqueue items and inspect stats ────────────────────────────────
print(DIVIDER)
print("Example 3: Enqueue items and queue stats")
print(DIVIDER)

with QueueRepository(":memory:") as qr:
    qr.register_update_page(PAGE_NAME, f"https://ddowiki.com/page/{PAGE_NAME}")
    inserted = qr.enqueue_items(links)
    print(f"  Inserted: {inserted}")

    # Re-enqueue — duplicates are silently skipped
    skipped = qr.enqueue_items(links)
    print(f"  Re-inserted (should be 0): {skipped}")

    stats = qr.get_queue_stats()
    print(f"  Queue stats:")
    print(f"    pending:     {stats.pending}")
    print(f"    in_progress: {stats.in_progress}")
    print(f"    complete:    {stats.complete}")
    print(f"    failed:      {stats.failed}")
    print(f"    skipped:     {stats.skipped}")
    print(f"    total:       {stats.total}")

print()


# ── Example 4: Process the queue with a mock scraper ─────────────────────────
print(DIVIDER)
print("Example 4: Process queue (mocked scraper + normalizer)")
print(DIVIDER)

# Build mocks that stand in for real HTTP + parsing
mock_fetcher = MagicMock()
mock_fetcher.fetch_url.return_value = "<html>item page</html>"

mock_item = MagicMock()
mock_item.name = "Cloak of Shadows"

mock_normalizer = MagicMock()
mock_normalizer.normalize.return_value = mock_item

mock_item_repo = MagicMock()
mock_item_repo.upsert.return_value = 42

mock_api = MagicMock()
mock_api.get_last_modified.return_value = None  # treat as needs-resync

with QueueRepository(":memory:") as qr:
    qr.register_update_page(PAGE_NAME, f"https://ddowiki.com/page/{PAGE_NAME}")
    qr.enqueue_items(links)

    syncer = DDOSyncer(mock_fetcher, mock_normalizer, mock_item_repo, qr)
    syncer._api_client = mock_api

    success, failures = syncer.process_queue()
    print(f"  Processed: {success} success, {failures} failed")

    stats = qr.get_queue_stats()
    print(f"  Final stats: pending={stats.pending}, complete={stats.complete}")

print()


# ── Example 5: Failed item retry logic ───────────────────────────────────────
print(DIVIDER)
print("Example 5: Retry logic — failed items reset to pending")
print(DIVIDER)

# First call raises; subsequent calls succeed
call_count = {"n": 0}

def flaky_fetch(url: str) -> str:
    call_count["n"] += 1
    if call_count["n"] == 1:
        raise ConnectionError("Transient network error")
    return "<html>item page</html>"

mock_fetcher_flaky = MagicMock()
mock_fetcher_flaky.fetch_url.side_effect = flaky_fetch

with QueueRepository(":memory:") as qr:
    qr.register_update_page(PAGE_NAME, f"https://ddowiki.com/page/{PAGE_NAME}")
    single_link = [links[0]]  # one item for clarity
    qr.enqueue_items(single_link)

    syncer = DDOSyncer(
        mock_fetcher_flaky, mock_normalizer, mock_item_repo, qr, max_retries=3
    )
    syncer._api_client = mock_api

    # First cycle — item fails
    s1, f1 = syncer.process_queue()
    stats = qr.get_queue_stats()
    print(f"  Cycle 1:  success={s1}, failed={f1}  (retry_count={stats.failed})")

    # Reset + second cycle — item succeeds
    reset = qr.reset_failed_to_pending(max_retries=3)
    print(f"  Reset {reset} failed item(s) to pending")
    s2, f2 = syncer.process_queue()
    print(f"  Cycle 2:  success={s2}, failed={f2}")
    stats2 = qr.get_queue_stats()
    print(f"  Final:    complete={stats2.complete}, failed={stats2.failed}")

print()


# ── Example 6: Full sync_all cycle ───────────────────────────────────────────
print(DIVIDER)
print("Example 6: Full sync_all cycle")
print(DIVIDER)

mock_fetcher_full = MagicMock()
mock_fetcher_full.fetch_url.return_value = SAMPLE_HTML  # update page + item pages

# After the first call (update page fetch), subsequent calls return item HTML
call_n = {"n": 0}

def smart_fetch(url: str) -> str:
    call_n["n"] += 1
    if call_n["n"] == 1:
        return SAMPLE_HTML  # this is the update page
    return "<html>item page</html>"

mock_fetcher_full.fetch_url.side_effect = smart_fetch

mock_api_stale = MagicMock()
mock_api_stale.get_last_modified.return_value = datetime(2025, 11, 2, tzinfo=UTC)

with QueueRepository(":memory:") as qr:
    syncer = DDOSyncer(mock_fetcher_full, mock_normalizer, mock_item_repo, qr)
    syncer._api_client = mock_api_stale
    syncer.register_update_page(PAGE_NAME)

    status = syncer.sync_all()
    print(f"  Queue stats after sync_all:")
    print(f"    pending:     {status.queue_stats.pending}")
    print(f"    complete:    {status.queue_stats.complete}")
    print(f"    failed:      {status.queue_stats.failed}")
    print(f"    total:       {status.queue_stats.total}")
    print(f"  Update pages:")
    for pname, pstatus in status.update_pages.items():
        print(f"    {pname}: needs_resync={pstatus.needs_resync}")

print()


# ── Example 7: Status snapshot ────────────────────────────────────────────────
print(DIVIDER)
print("Example 7: Status snapshot (get_status)")
print(DIVIDER)

with QueueRepository(":memory:") as qr:
    qr.register_update_page(PAGE_NAME, f"https://ddowiki.com/page/{PAGE_NAME}")
    qr.enqueue_items(links)

    syncer = DDOSyncer(mock_fetcher, mock_normalizer, mock_item_repo, qr)
    syncer._api_client = mock_api

    syncer.process_queue(limit=1)

    snap = syncer.get_status()
    print(f"  Queue stats:  {snap.queue_stats}")
    print(f"  Update pages: {list(snap.update_pages.keys())}")
    page_snap = snap.update_pages.get(PAGE_NAME)
    if page_snap:
        print(f"    {PAGE_NAME}.needs_resync = {page_snap.needs_resync}")

print()


# ── Example 8: File-based queue database ──────────────────────────────────────
print(DIVIDER)
print("Example 8: File-based queue database (persistent)")
print(DIVIDER)

db_path = Path(__file__).parent / "queue.db"
print(f"  Database: {db_path}")

# Write
with QueueRepository(str(db_path)) as qr:
    qr.register_update_page(PAGE_NAME, f"https://ddowiki.com/page/{PAGE_NAME}")
    qr.enqueue_items(links)
    stats = qr.get_queue_stats()
    print(f"  Written {stats.pending} pending items to {db_path.name}")

# Read back in a separate connection
with QueueRepository(str(db_path)) as qr:
    readback = qr.get_queue_stats()
    print(f"  Read back:  pending={readback.pending}, total={readback.total}")
    items = qr.get_pending_items()
    print(f"  First item: {items[0].item_name!r} → {items[0].status}")

db_path.unlink(missing_ok=True)
print(f"  Cleaned up {db_path.name}")

print()
print("All examples complete.")
