from app.services.scraper import LinkedInScraper
import pytest
from app.services.cache import CacheService
import asyncio

# tests/test_api.py
@pytest.mark.asyncio
async def test_get_page_endpoint(client):
    response = await client.get("/api/v1/pages/deepsolv")
    assert response.status_code == 200
    assert response.json()['data']['page_id'] == "deepsolv"