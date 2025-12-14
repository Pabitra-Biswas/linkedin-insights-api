from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Dict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class UserRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.users

    async def create_users(self, users_data: List[Dict]) -> int:
        """
        Bulk insert users into MongoDB
        """
        try:
            if not users_data:
                return 0

            for user in users_data:
                user["scraped_at"] = datetime.utcnow()

            result = await self.collection.insert_many(users_data)
            inserted_count = len(result.inserted_ids)

            logger.info(f"✅ {inserted_count} users inserted")
            return inserted_count

        except Exception as e:
            logger.error(f"❌ Users creation failed: {e}")
            return 0

    async def get_users_by_company(
        self,
        company_id: str,
        skip: int = 0,
        limit: int = 20
    ) -> List[Dict]:
        """
        Get employees for a specific company with pagination
        """
        try:
            cursor = (
                self.collection
                .find({"current_company": company_id})
                .skip(skip)
                .limit(limit)
            )

            users = await cursor.to_list(length=limit)

            for user in users:
                user["_id"] = str(user["_id"])

            return users

        except Exception as e:
            logger.error(f"❌ Users retrieval failed: {e}")
            return []

    async def count_users(self, company_id: str) -> int:
        """
        Count total employees for a company
        """
        try:
            return await self.collection.count_documents(
                {"current_company": company_id}
            )
        except Exception as e:
            logger.error(f"❌ Users count failed: {e}")
            return 0
