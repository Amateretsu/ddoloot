"""Basic usage examples for the ddowiki_scraper package.

Demonstrates synchronous fetching, asynchronous fetching, batch operations,
error handling, and custom configuration.

Run this script directly:
    python examples/basic_usage.py

Or run individual sections by importing the functions.

Note: These examples make real HTTP requests to ddowiki.com. The default
configuration enforces a 2.5-second delay between requests to be a
respectful scraper. Running all examples will take around 30-60 seconds.
"""

import asyncio
import sys

from loguru import logger

from ddowiki_scraper import (
    FetchError,
    RateLimiter,
    RobotsTxtError,
    WikiFetcher,
    WikiFetcherConfig,
)


# ---------------------------------------------------------------------------
# 1. Basic synchronous fetch
# ---------------------------------------------------------------------------

def example_sync_single_item() -> None:
    """Fetch a single item page synchronously using a context manager."""
    print("\n--- Example 1: Synchronous single item fetch ---")

    config = WikiFetcherConfig(
        rate_limit_delay=2.5,
        respect_robots_txt=True,
    )

    with WikiFetcher(config) as fetcher:
        try:
            html = fetcher.fetch_item_page("Mantle of the Worldshaper")
            print(f"Fetched {len(html):,} bytes")
            print(f"Page title found: {'Mantle of the Worldshaper' in html}")
        except RobotsTxtError as e:
            print(f"Blocked by robots.txt: {e}")
        except FetchError as e:
            print(f"Fetch failed (HTTP {e.status_code}): {e}")


# ---------------------------------------------------------------------------
# 2. Synchronous fetch with URL encoding
# ---------------------------------------------------------------------------

def example_sync_special_characters() -> None:
    """Fetch an item whose name contains special characters (apostrophes, etc.)."""
    print("\n--- Example 2: Item name with special characters ---")

    config = WikiFetcherConfig(rate_limit_delay=2.5)

    with WikiFetcher(config) as fetcher:
        items = [
            "Epic Elyd Edge",           # spaces → underscores
            "Bullywug Priestess' Staff",  # apostrophe → URL-encoded
        ]
        for item_name in items:
            try:
                html = fetcher.fetch_item_page(item_name)
                print(f"  '{item_name}': {len(html):,} bytes")
            except FetchError as e:
                print(f"  '{item_name}': failed — {e}")


# ---------------------------------------------------------------------------
# 3. Synchronous fetch for a category/arbitrary URL
# ---------------------------------------------------------------------------

def example_sync_category_page() -> None:
    """Fetch an arbitrary DDO Wiki page (category listing, update history, etc.)."""
    print("\n--- Example 3: Category page fetch ---")

    config = WikiFetcherConfig(rate_limit_delay=2.5)
    category_url = "https://ddowiki.com/page/Category:Items"

    with WikiFetcher(config) as fetcher:
        try:
            html = fetcher.fetch_url(category_url)
            print(f"Category page: {len(html):,} bytes")
            print(f"Contains item links: {'Item:' in html}")
        except FetchError as e:
            print(f"Failed to fetch category: {e}")
        except ValueError as e:
            # fetch_url validates that the URL belongs to the configured domain
            print(f"Invalid URL: {e}")


# ---------------------------------------------------------------------------
# 4. Asynchronous single item fetch
# ---------------------------------------------------------------------------

async def example_async_single_item() -> None:
    """Fetch a single item page asynchronously."""
    print("\n--- Example 4: Asynchronous single item fetch ---")

    config = WikiFetcherConfig(rate_limit_delay=2.5)

    async with WikiFetcher(config) as fetcher:
        try:
            html = await fetcher.fetch_item_page_async("Sword of Shadow")
            print(f"Fetched {len(html):,} bytes (async)")
        except FetchError as e:
            print(f"Async fetch failed: {e}")


# ---------------------------------------------------------------------------
# 5. Batch asynchronous fetch
# ---------------------------------------------------------------------------

async def example_async_batch() -> None:
    """Fetch multiple item pages concurrently, respecting a semaphore limit."""
    print("\n--- Example 5: Batch asynchronous fetch ---")

    config = WikiFetcherConfig(
        rate_limit_delay=2.5,
        max_concurrent=3,   # At most 3 simultaneous requests
    )

    items = [
        "Mantle of the Worldshaper",
        "Epic Elyd Edge",
        "Bracers of the Demon's Consort",
        "Ring of Spell Storing",
    ]

    async with WikiFetcher(config) as fetcher:
        results = await fetcher.fetch_multiple_async(items)

    successful = {name: html for name, html in results.items() if html is not None}
    failed = [name for name, html in results.items() if html is None]

    print(f"Fetched {len(successful)}/{len(items)} items successfully")
    for name, html in successful.items():
        print(f"  '{name}': {len(html):,} bytes")
    for name in failed:
        print(f"  '{name}': FAILED")


# ---------------------------------------------------------------------------
# 6. Error handling patterns
# ---------------------------------------------------------------------------

def example_error_handling() -> None:
    """Demonstrate granular error handling for common failure scenarios."""
    print("\n--- Example 6: Error handling ---")

    config = WikiFetcherConfig(rate_limit_delay=2.5)

    with WikiFetcher(config) as fetcher:
        # 404 — item does not exist on the wiki
        try:
            fetcher.fetch_item_page("This Item Does Not Exist XYZ123")
        except FetchError as e:
            if e.status_code == 404:
                print(f"Item not found (404): skipping")
            else:
                print(f"Unexpected HTTP error ({e.status_code}): {e}")

        # Wrong domain — fetch_url rejects URLs outside ddowiki.com
        try:
            fetcher.fetch_url("https://example.com/page/Item:Test")
        except ValueError as e:
            print(f"Domain validation caught: {e}")

        # Catch-all for any fetcher error
        try:
            fetcher.fetch_item_page("Mantle of the Worldshaper")
        except RobotsTxtError:
            print("Blocked by robots.txt — do not retry this URL")
        except FetchError as e:
            print(f"Fetch failed after retries: {e}")


# ---------------------------------------------------------------------------
# 7. Custom configuration
# ---------------------------------------------------------------------------

def example_custom_config() -> None:
    """Show how to tune the fetcher for different scraping requirements."""
    print("\n--- Example 7: Custom configuration ---")

    # Conservative config — slower but more polite
    polite_config = WikiFetcherConfig(
        rate_limit_delay=5.0,       # 5 seconds between requests
        max_retries=5,              # More retries for flaky connections
        timeout=60,                 # Generous timeout
        max_concurrent=1,           # No concurrency
        respect_robots_txt=True,
        user_agent="DDOLoot/0.0.1 (github.com/jstnbelter/ddoloot; respectful scraping)",
    )
    print(f"Polite config headers: {list(polite_config.get_request_headers().keys())}")
    print(f"Rate limit delay: {polite_config.rate_limit_delay}s")

    # Check rate limiter state directly
    limiter = RateLimiter(delay=polite_config.rate_limit_delay)
    print(f"Rate limiter ready: {limiter.is_ready()}")
    print(f"Time until ready: {limiter.get_time_until_ready():.1f}s")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    # Suppress verbose loguru output for the examples — set to WARNING level
    logger.remove()
    logger.add(sys.stderr, level="WARNING")

    print("DDOLoot — ddowiki_scraper usage examples")
    print("=" * 45)
    print("Note: examples 1-6 make live HTTP requests to ddowiki.com.")
    print("Comment out any section you do not want to run.\n")

    # Sync examples (run sequentially)
    example_sync_special_characters()
    example_sync_category_page()
    example_error_handling()
    example_custom_config()

    # Async examples (run in an event loop)
    asyncio.run(example_async_single_item())
    asyncio.run(example_async_batch())

    # Full sync example last (also live)
    example_sync_single_item()


if __name__ == "__main__":
    main()
