"""Tests for ddo_sync.update_page_parser.UpdatePageParser."""

from __future__ import annotations

import pytest

from ddo_sync.exceptions import UpdatePageError
from ddo_sync.models import ItemLink
from ddo_sync.update_page_parser import UpdatePageParser

from tests.ddo_sync.conftest import EMPTY_PAGE_HTML, UPDATE_PAGE_HTML


@pytest.fixture
def parser() -> UpdatePageParser:
    return UpdatePageParser(base_url="https://ddowiki.com")


class TestParse:
    def test_returns_item_links(self, parser: UpdatePageParser):
        links = parser.parse(UPDATE_PAGE_HTML, "Update_5_named_items")
        assert isinstance(links, list)
        assert all(isinstance(lnk, ItemLink) for lnk in links)

    def test_finds_three_unique_items(self, parser: UpdatePageParser):
        links = parser.parse(UPDATE_PAGE_HTML, "Update_5_named_items")
        assert len(links) == 3

    def test_item_names(self, parser: UpdatePageParser):
        links = parser.parse(UPDATE_PAGE_HTML, "Update_5_named_items")
        names = {lnk.item_name for lnk in links}
        assert names == {"Sword of Shadow", "Shield of Light", "Ring of Fire"}

    def test_absolute_urls(self, parser: UpdatePageParser):
        links = parser.parse(UPDATE_PAGE_HTML, "Update_5_named_items")
        for lnk in links:
            assert lnk.wiki_url.startswith("https://ddowiki.com/page/Item:")

    def test_update_page_key_injected(self, parser: UpdatePageParser):
        links = parser.parse(UPDATE_PAGE_HTML, "Update_5_named_items")
        assert all(lnk.update_page == "Update_5_named_items" for lnk in links)

    def test_deduplication(self, parser: UpdatePageParser):
        """Sword of Shadow appears twice in the HTML but only once in results."""
        links = parser.parse(UPDATE_PAGE_HTML, "Update_5_named_items")
        urls = [lnk.wiki_url for lnk in links]
        assert len(urls) == len(set(urls))

    def test_non_item_links_excluded(self, parser: UpdatePageParser):
        """The /page/Update_5_named_items link must not appear in results."""
        links = parser.parse(UPDATE_PAGE_HTML, "Update_5_named_items")
        for lnk in links:
            assert "/page/Item:" in lnk.wiki_url

    def test_empty_html_raises(self, parser: UpdatePageParser):
        with pytest.raises(UpdatePageError):
            parser.parse("", "Update_5_named_items")

    def test_whitespace_only_html_raises(self, parser: UpdatePageParser):
        with pytest.raises(UpdatePageError):
            parser.parse("   \n\t  ", "Update_5_named_items")

    def test_no_item_links_returns_empty_list(self, parser: UpdatePageParser):
        links = parser.parse(EMPTY_PAGE_HTML, "Update_5_named_items")
        assert links == []

    def test_url_encoded_name_decoded(self, parser: UpdatePageParser):
        html = "<a href=\"/page/Item:Ghal%27s_Ring\">Ghal's Ring</a>"
        links = parser.parse(html, "Update_5_named_items")
        assert links[0].item_name == "Ghal's Ring"

    def test_underscores_replaced_by_spaces(self, parser: UpdatePageParser):
        html = "<a href=\"/page/Item:Sword_of_Shadow\">Sword of Shadow</a>"
        links = parser.parse(html, "Update_5_named_items")
        assert links[0].item_name == "Sword of Shadow"

    def test_custom_base_url(self):
        custom = UpdatePageParser(base_url="https://staging.ddowiki.com")
        html = "<a href=\"/page/Item:Test_Item\">Test Item</a>"
        links = custom.parse(html, "Update_1")
        assert links[0].wiki_url.startswith("https://staging.ddowiki.com")

    def test_base_url_trailing_slash_stripped(self):
        parser = UpdatePageParser(base_url="https://ddowiki.com/")
        html = "<a href=\"/page/Item:Foo\">Foo</a>"
        links = parser.parse(html, "Update_1")
        assert "//page" not in links[0].wiki_url
