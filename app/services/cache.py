import json
import logging
from typing import Optional, Any
from app.database import get_redis
from app.config import settings

logger = logging.getLogger(__name__)

class CacheService:
    def __init__(self, redis_client=None):
        self.redis = redis_client
        self.ttl = settings.REDIS_TTL
    
    async def get_cached_page(self, page_id: str) -> Optional[dict]:
        """Retrieve cached page data"""
        try:
            cache_key = f"page:{page_id}"
            cached_data = await self.redis.get(cache_key)
            
            if cached_data:
                logger.info(f"✅ Cache HIT for page: {page_id}")
                return json.loads(cached_data)
            else:
                logger.info(f"❌ Cache MISS for page: {page_id}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Cache retrieval error: {str(e)}")
            return None
    
    async def cache_page(self, page_id: str, page_data: dict):
        """Store page data in cache with TTL"""
        try:
            cache_key = f"page:{page_id}"
            serialized_data = json.dumps(page_data, default=str)
            
            await self.redis.setex(
                cache_key,
                self.ttl,
                serialized_data
            )
            
            logger.info(f"✅ Cached page: {page_id} (TTL: {self.ttl}s)")
            
        except Exception as e:
            logger.error(f"❌ Cache storage error: {str(e)}")
    
    async def invalidate_cache(self, page_id: str):
        """Delete cached entry"""
        try:
            cache_key = f"page:{page_id}"
            await self.redis.delete(cache_key)
            logger.info(f"✅ Invalidated cache for: {page_id}")
            
        except Exception as e:
            logger.error(f"❌ Cache invalidation error: {str(e)}")
    
    async def get_cached_posts(self, page_id: str) -> Optional[list]:
        """Retrieve cached posts"""
        try:
            cache_key = f"posts:{page_id}"
            cached_data = await self.redis.get(cache_key)
            return json.loads(cached_data) if cached_data else None
        except:
            return None
    
    async def cache_posts(self, page_id: str, posts_data: list):
        """Cache posts data"""
        try:
            cache_key = f"posts:{page_id}"
            await self.redis.setex(
                cache_key,
                self.ttl,
                json.dumps(posts_data, default=str)
            )
        except Exception as e:
            logger.error(f"❌ Posts cache error: {str(e)}")
