import logging
import os
from pathlib import Path
from typing import List, Optional

import aiofiles
import aiohttp

from app.config import settings

logger = logging.getLogger(__name__)


class LocalStorageService:
    """Simple local storage service to replace S3 functionality.

    Methods mirror the behaviours previously expected by routes:
    - process_page_images(page_id, image_url)
    - process_post_images(page_id, post_id, image_urls)
    - process_user_images(user_id, image_url)
    """

    def __init__(self, base_path: Optional[str] = None):
        self.base_path = Path(base_path or settings.LOCAL_STORAGE_PATH)
        self.base_path.mkdir(parents=True, exist_ok=True)

    async def _fetch_bytes(self, url: str) -> Optional[bytes]:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as resp:
                    if resp.status != 200:
                        logger.warning("Failed to fetch %s -> status %s", url, resp.status)
                        return None
                    return await resp.read()
        except Exception as e:
            logger.warning("Error fetching %s: %s", url, str(e))
            return None

    async def _save_bytes(self, filename: str, content: bytes) -> str:
        path = self.base_path / filename
        try:
            async with aiofiles.open(path, "wb") as f:
                await f.write(content)
            logger.info("Saved file to %s", str(path))
            return f"file://{path.absolute()}"
        except Exception as e:
            logger.exception("Failed saving file %s: %s", filename, str(e))
            raise

    async def _process_single_image(self, filename_prefix: str, image_url: str) -> Optional[str]:
        if not image_url:
            return None

        # Already local
        if image_url.startswith("file://") or image_url.startswith("/"):
            return image_url

        content = await self._fetch_bytes(image_url)
        if not content:
            return None

        ext = os.path.splitext(image_url.split("?")[0])[1] or ".jpg"
        filename = f"{filename_prefix}{ext}"
        return await self._save_bytes(filename, content)

    async def process_page_images(self, page_id: str, image_url: str) -> Optional[str]:
        return await self._process_single_image(f"page_{page_id}", image_url)

    async def process_post_images(self, page_id: str, post_id: str, image_urls: List[str]) -> List[str]:
        results = []
        for idx, url in enumerate(image_urls):
            filename = f"post_{post_id}_{idx}"
            res = await self._process_single_image(filename, url)
            if res:
                results.append(res)
        return results

    async def process_user_images(self, user_id: str, image_url: str) -> Optional[str]:
        return await self._process_single_image(f"user_{user_id}", image_url)


storage = LocalStorageService()
