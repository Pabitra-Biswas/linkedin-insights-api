from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Dict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class PostRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.posts

    async def create_posts(self, posts_data: List[Dict]) -> int:
        """
        Bulk insert posts into MongoDB
        """
        try:
            if not posts_data:
                return 0

            for post in posts_data:
                post["scraped_at"] = datetime.utcnow()

            result = await self.collection.insert_many(posts_data)
            inserted_count = len(result.inserted_ids)

            logger.info(f"✅ {inserted_count} posts inserted")
            return inserted_count

        except Exception as e:
            logger.error(f"❌ Posts creation failed: {e}")
            return 0

    async def get_posts_by_page(
        self,
        page_id: str,
        skip: int = 0,
        limit: int = 15
    ) -> List[Dict]:
        """
        Get posts for a specific page with pagination
        """
        try:
            cursor = (
                self.collection
                .find({"page_id": page_id})
                .sort("posted_at", -1)
                .skip(skip)
                .limit(limit)
            )

            posts = await cursor.to_list(length=limit)

            for post in posts:
                post["_id"] = str(post["_id"])

            return posts

        except Exception as e:
            logger.error(f"❌ Posts retrieval failed: {e}")
            return []

    async def count_posts(self, page_id: str) -> int:
        """
        Count total posts for a page
        """
        try:
            return await self.collection.count_documents({"page_id": page_id})
        except Exception as e:
            logger.error(f"❌ Post count failed: {e}")
            return 0
