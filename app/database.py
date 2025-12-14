from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import settings
import redis.asyncio as aioredis

class Database:
    client: AsyncIOMotorClient = None
    redis_client = None

db = Database()

async def get_database() -> AsyncIOMotorDatabase:
    return db.client[settings.MONGODB_DB_NAME]

async def connect_to_mongo():
    if not getattr(settings, "MONGODB_URL", None):
        print("⚠️ MONGODB_URL not configured; skipping MongoDB connection")
        return

    try:
        db.client = AsyncIOMotorClient(settings.MONGODB_URL)

        # Try to ping the server a few times to ensure it's reachable
        max_attempts = 6
        for attempt in range(1, max_attempts + 1):
            try:
                await db.client.admin.command("ping")
                print("✅ Connected to MongoDB")
                break
            except Exception:
                print(f"⚠️ Mongo ping attempt {attempt}/{max_attempts} failed, retrying...")
                if attempt == max_attempts:
                    raise
                await asyncio.sleep(2)
    except Exception as e:
        # Log the exception and keep going; index init will handle unavailability gracefully
        print(f"❌ Failed to connect to MongoDB: {e}")

async def close_mongo_connection():
    db.client.close()
    print("❌ Closed MongoDB connection")

async def connect_to_redis():
    db.redis_client = await aioredis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True
    )
    print("✅ Connected to Redis")

async def close_redis_connection():
    await db.redis_client.close()
    print("❌ Closed Redis connection")

async def get_redis():
    return db.redis_client

async def init_indexes(database: AsyncIOMotorDatabase):
    """Create database indexes for optimization"""
    # Pages indexes
    await database.pages.create_index("page_id", unique=True)
    await database.pages.create_index("followers_count")
    await database.pages.create_index("industry")
    await database.pages.create_index([("name", "text")])
    
    # Posts indexes
    await database.posts.create_index("page_id")
    await database.posts.create_index("posted_at")
    
    # Users indexes
    await database.users.create_index("user_id", unique=True)
    await database.users.create_index("current_company")
    
    print("✅ Database indexes created")