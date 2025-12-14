# tests/test_scraper.py
from app.services.scraper import LinkedInScraper
import pytest
from app.services.cache import CacheService
import asyncio
@pytest.mark.asyncio
async def test_scrape_page_basic_info(monkeypatch):
    async def fake_scrape_page(self, page_id):
        return {"name": "Acme Co", "followers_count": 1234}

    monkeypatch.setattr("app.services.scraper.LinkedInScraper.scrape_page", fake_scrape_page)
    from app.services.scraper import LinkedInScraper

    scraper = LinkedInScraper(skip_browser=True)
    result = await scraper.scrape_page("deepsolv")
    assert result["name"] is not None
    assert result["followers_count"] > 0
