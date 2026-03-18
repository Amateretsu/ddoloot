# DDOLoot

[![CI](https://github.com/Amateretsu/ddoloot/actions/workflows/ci.yml/badge.svg?event=push)](https://github.com/Amateretsu/ddoloot/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/Amateretsu/ddoloot/branch/main/graph/badge.svg)](https://codecov.io/gh/Amateretsu/ddoloot)
[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

DDOLoot is a data pipeline that discovers, scrapes, and stores item data from [ddowiki.com](https://ddowiki.com) — the community wiki for Dungeons & Dragons Online. It automatically finds every update page listing named items, fetches each item's wiki page, normalizes the data into typed models, and persists everything to a local SQLite database.

---

## Architecture

The project is split into four independent packages that compose into a single pipeline:

```
ddowiki_scraper   →   item_normalizer   →   item_db
       ↑                                        ↑
       └──────────── ddo_sync ──────────────────┘
```

| Package | Responsibility |
|---|---|
| [`ddowiki_scraper`](docs/ddowiki_scraper.md) | Ethical HTTP client for ddowiki.com — rate limiting, retries, robots.txt |
| [`item_normalizer`](docs/item_normalizer.md) | HTML parser + type coercion → validated `DDOItem` models |
| [`item_db`](docs/item_db.md) | SQLite persistence — CRUD, search, and schema management |
| [`ddo_sync`](docs/ddo_sync.md) | Orchestrator — discovers update pages, manages a scrape queue, drives the full pipeline |

---

## Installation

**Prerequisites:** Python 3.9+

```bash
git clone https://github.com/Amateretsu/ddoloot.git
cd ddoloot
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -e ".[test]"
```

The `ddoloot` CLI command is installed automatically as a console script entry point.

---

## Quick Start

### Run a full sync

Discovers every `Update_<N>_named_items` page on the wiki, queues all linked items, and syncs them to the local database:

```bash
ddoloot
```

### Check status

```bash
ddoloot --status
```

### Sync specific update pages

```bash
ddoloot --page "Update_69_named_items" "Update_70_named_items"
```

### Limit items processed per run

```bash
ddoloot --limit 50
```

### Retry previously failed items

```bash
ddoloot --reset-failed
```

### Enable verbose logging

```bash
ddoloot --verbose
```

### Run via Python directly

```bash
python main.py [options]
```

---

## CLI Reference

```
usage: ddoloot [-h] [--status | --discover | --reset-failed]
               [--page PAGE [PAGE ...]] [--limit N]
               [--rate-limit SECONDS] [--verbose]

optional arguments:
  --status              Print database and queue statistics, then exit
  --discover            List discovered update pages without syncing
  --reset-failed        Reset all failed queue items back to pending, then exit
  --page PAGE [PAGE …]  Sync one or more named update pages instead of all
  --limit N             Maximum number of items to process in this run
  --rate-limit SECONDS  Override the default inter-request delay (default: 2.5s)
  --verbose             Enable DEBUG-level logging
```

**Exit codes:**

| Code | Meaning |
|---|---|
| `0` | Success — all processed items synced cleanly |
| `1` | Fatal error — startup failed or unhandled exception |
| `2` | Partial — sync completed but some items failed |

---

## Project Structure

```
ddoloot/
├── main.py                     # Thin entry point (forwards to ddo_sync.cli)
├── pyproject.toml              # Project metadata and dependencies
│
├── src/
│   ├── ddowiki_scraper/        # HTTP client package
│   ├── item_normalizer/        # HTML parsing & normalization package
│   ├── item_db/                # SQLite persistence package
│   └── ddo_sync/               # Orchestration & CLI package
│
├── tests/
│   ├── conftest.py
│   ├── ddowiki_scraper/
│   ├── item_normalizer/
│   ├── item_db/
│   └── ddo_sync/
│
├── examples/                   # Runnable usage examples per package
├── docs/                       # Package-level documentation
└── data/
    ├── loot.db                 # Item database (generated)
    └── queue.db                # Scrape queue database (generated)
```

---

## Programmatic Usage

The packages can be used independently of the CLI.

### Fetch and normalize a single item

```python
from ddowiki_scraper import WikiFetcher, WikiFetcherConfig
from item_normalizer import ItemNormalizer

config = WikiFetcherConfig(rate_limit_delay=2.5)
with WikiFetcher(config) as fetcher:
    html = fetcher.fetch_item_page("Mantle_of_the_Worldshaper")

normalizer = ItemNormalizer()
item = normalizer.normalize(html, wiki_url="https://ddowiki.com/page/Item:Mantle_of_the_Worldshaper")
print(item.name, item.minimum_level)
```

### Store and query items

```python
from item_db import ItemRepository, ItemFilter

with ItemRepository("data/loot.db") as repo:
    repo.upsert(item)

    results = repo.search(ItemFilter(slot="Cloak", minimum_level=20))
    for r in results:
        print(r.name, r.enchantments)
```

### Run the full pipeline in code

```python
from ddowiki_scraper import WikiFetcher, WikiFetcherConfig
from item_normalizer import ItemNormalizer
from item_db import ItemRepository
from ddo_sync import DDOSyncer, QueueRepository, UpdatePageDiscoverer

config = WikiFetcherConfig()
with WikiFetcher(config) as fetcher, \
     ItemRepository("data/loot.db") as item_repo, \
     QueueRepository("data/queue.db") as queue_repo:

    syncer = DDOSyncer(fetcher, ItemNormalizer(), item_repo, queue_repo)
    syncer.discover_and_register_all()
    status = syncer.sync_all()
    print(f"Synced {status.synced} items, {status.failed} failed")
```

---

## Development

### Running tests

```bash
pytest
pytest --cov=src --cov-report=term-missing   # with coverage
pytest -x -q                                  # stop on first failure, quiet
```

### Linting and formatting

```bash
ruff check src tests
black src tests
isort src tests
mypy src
```

### Adding a new package

1. Create `src/<package_name>/` with `__init__.py` and `exceptions.py`
2. Add to `[tool.setuptools.packages.find]` in `pyproject.toml`
3. Add to `[tool.isort] known_first_party` in `pyproject.toml`
4. Create `tests/<package_name>/` with a `conftest.py`

---

## Data Model

The core data model is `DDOItem` from `item_normalizer.models`. All fields are optional except `name`, `wiki_url`, and `scraped_at`.

```
DDOItem
├── name                  str
├── item_type             str | None
├── slot                  str | None
├── minimum_level         int | None
├── required_race         str | None
├── required_class        str | None
├── binding               str | None
├── material              str | None
├── hardness              int | None
├── durability            int | None
├── base_value            int | None        (total copper pieces)
├── weight                float | None      (pounds)
├── enchantments          list[Enchantment]
│   └── Enchantment
│       ├── name          str
│       └── value         int | None        (e.g. +5 → 5, VI → 6)
├── weapon_stats          WeaponStats | None
│   ├── damage_dice       str               (e.g. "1d8")
│   ├── damage_bonus      int | None
│   ├── damage_type       list[str]
│   ├── critical_range    str               (e.g. "19-20")
│   ├── critical_multiplier int | None
│   ├── enchantment_bonus int | None
│   ├── handedness        str | None
│   ├── proficiency       str | None
│   └── weapon_type       str | None
├── armor_stats           ArmorStats | None
│   ├── armor_type        str | None
│   ├── armor_bonus       int | None
│   ├── max_dex_bonus     int | None
│   ├── armor_check_penalty int | None
│   └── arcane_spell_failure int | None     (percentage)
├── named_set             NamedSet | None
│   └── name              str
├── source                ItemSource | None
│   └── quests            list[str]
├── flavor_text           str | None
├── wiki_url              str
└── scraped_at            datetime          (UTC)
```

**Currency:** `base_value` is stored as copper pieces (cp). Conversion: 1 pp = 1,000 cp · 1 gp = 100 cp · 1 sp = 10 cp.

---

## Scraping Ethics

DDOLoot scrapes ddowiki.com responsibly:

- **Rate limiting**: 2.5 second default delay between requests (configurable, minimum 1.0s)
- **robots.txt**: Respected by default (`WikiFetcherConfig.respect_robots_txt = True`)
- **User-Agent**: Identifies the scraper by name so site operators can contact the project
- **No aggressive crawling**: Items are only re-fetched when their wiki page is updated

---

## License

MIT — see [LICENSE](LICENSE) for details.

## Acknowledgments

- [ddowiki.com](https://ddowiki.com) for maintaining the item database that makes this project possible.
- The DDO community for decades of meticulous item documentation.
