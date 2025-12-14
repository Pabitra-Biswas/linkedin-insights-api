from app.services.scraper import LinkedInScraper
import pytest
from app.services.cache import CacheService
import asyncio


# tests/test_cache.py
@pytest.mark.asyncio
async def test_cache_ttl():
    cache = CacheService()
    await cache.cache_page("test", {"name": "Test"})
    await asyncio.sleep(301)  # Wait past TTL
    result = await cache.get_cached_page("test")
    assert result is None