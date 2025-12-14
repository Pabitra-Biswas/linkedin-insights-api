from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional, List, Dict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class PageRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.pages
    
    async def create_page(self, page_data: dict) -> str:
        """Insert new page document"""
        try:
            page_data['scraped_at'] = datetime.utcnow()
            page_data['last_updated'] = datetime.utcnow()
            
            result = await self.collection.insert_one(page_data)
            
            logger.info(f"✅ Page created in DB: {page_data['page_id']}")
            return str(result.inserted_id)
        

            
        except Exception as e:
            logger.error(f"❌ Page creation failed: {str(e)}")
            raise

    async def get_page_by_id(self, page_id: str) -> Optional[dict]:
        """Find page by page_id"""
        try:
            page = await self.collection.find_one({'page_id': page_id})
            if page:
                page['_id'] = str(page['_id'])
            return page
        except Exception as e:
            logger.error(f"❌ Page retrieval failed: {str(e)}")
            return None

    async def search_pages(
        self,
        follower_min: Optional[int] = None,
        follower_max: Optional[int] = None,
        industry: Optional[str] = None,
        name_query: Optional[str] = None,
        skip: int = 0,
        limit: int = 10
    ) -> List[dict]:
        """Advanced filtering with pagination"""
        try:
            query = {}
            
            # Follower range filter
            if follower_min is not None or follower_max is not None:
                query['followers_count'] = {}
                if follower_min is not None:
                    query['followers_count']['$gte'] = follower_min
                if follower_max is not None:
                    query['followers_count']['$lte'] = follower_max
            
            # Industry filter
            if industry:
                query['industry'] = {'$regex': industry, '$options': 'i'}
            
            # Name search (text search)
            if name_query:
                query['$text'] = {'$search': name_query}
            
            cursor = self.collection.find(query).skip(skip).limit(limit)
            pages = await cursor.to_list(length=limit)
            
            # Convert ObjectId to string
            for page in pages:
                page['_id'] = str(page['_id'])
            
            return pages
            
        except Exception as e:
            logger.error(f"❌ Page search failed: {str(e)}")
            return []

    async def update_page(self, page_id: str, update_data: dict) -> bool:
        """Update existing page"""
        try:
            update_data['last_updated'] = datetime.utcnow()
            
            result = await self.collection.update_one(
                {'page_id': page_id},
                {'$set': update_data}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"❌ Page update failed: {str(e)}")
            return False

    async def count_pages(self, query: dict = {}) -> int:
        """Count total pages matching query"""
        try:
            return await self.collection.count_documents(query)
        except:
            return 0