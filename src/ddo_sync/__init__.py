"""ddo_sync — DDO Wiki update-page scrape queue and sync orchestration.

Public API:

    DDOSyncer         — top-level sync orchestrator
    QueueRepository   — SQLite scrape queue (update pages + items)
    WikiApiClient     — MediaWiki Action API thin client
    UpdatePageParser  — HTML parser for item links on update pages

Models:

    ItemLink, QueueItem, QueueStats, UpdatePageStatus, SyncStatus

Exceptions:

    DDOSyncError, UpdatePageError, WikiApiError, QueueDbError, QueueSchemaError

Example:

    >>> from ddo_sync import DDOSyncer, QueueRepository
    >>> from ddowiki_scraper import WikiFetcher
    >>> from item_normalizer import ItemNormalizer
    >>> from item_db import ItemRepository
    >>> with (
    ...     WikiFetcher(config) as fetcher,
    ...     ItemRepository("loot.db") as item_repo,
    ...     QueueRepository("queue.db") as queue_repo,
    ... ):
    ...     syncer = DDOSyncer(fetcher, ItemNormalizer(), item_repo, queue_repo)
    ...     syncer.register_update_page("Update_5_named_items")
    ...     status = syncer.sync_all()
"""

from ddo_sync.exceptions import (
    DDOSyncError,
    QueueDbError,
    QueueSchemaError,
    UpdatePageError,
    WikiApiError,
)
from ddo_sync.models import (
    ItemLink,
    QueueItem,
    QueueStats,
    SyncStatus,
    UpdatePageStatus,
)
from ddo_sync.queue_db import QueueRepository
from ddo_sync.syncer import DDOSyncer
from ddo_sync.update_page_parser import UpdatePageParser
from ddo_sync.wiki_api import WikiApiClient

__all__ = [
    # Orchestration
    "DDOSyncer",
    # Infrastructure
    "QueueRepository",
    "WikiApiClient",
    "UpdatePageParser",
    # Models
    "ItemLink",
    "QueueItem",
    "QueueStats",
    "SyncStatus",
    "UpdatePageStatus",
    # Exceptions
    "DDOSyncError",
    "UpdatePageError",
    "WikiApiError",
    "QueueDbError",
    "QueueSchemaError",
]
