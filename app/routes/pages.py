from fastapi import APIRouter, Depends, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional
from datetime import datetime
import logging

from app.database import get_database, get_redis
from app.repositories.page_repo import PageRepository
from app.repositories.post_repo import PostRepository
from app.repositories.user_repo import UserRepository
from app.services.scraper import LinkedInScraper
from app.services.storage import storage as LocalStorageService
from app.services.cache import CacheService
from app.services.ai_summary import AISummaryService
from app.config import settings  # ✅ IMPORT SETTINGS

router = APIRouter(prefix="/api/v1/pages", tags=["Pages"])
logger = logging.getLogger(__name__)


@router.get("/{page_id}")
async def get_page_details(
    page_id: str,
    force_refresh: bool = Query(False, description="Force re-scrape even if data exists"),
    db: AsyncIOMotorDatabase = Depends(get_database),
    redis=Depends(get_redis),
):
    """
    Get LinkedIn page details
    Flow:
    1. Cache
    2. Database
    3. Scrape LinkedIn
    """
    try:
        # ✅ Normalize page_id to lowercase
        page_id = page_id.lower().strip()
        
        cache_service = CacheService(redis)
        page_repo = PageRepository(db)

        # 1️⃣ Cache
        if not force_refresh:
            cached_page = await cache_service.get_cached_page(page_id)
            if cached_page:
                return {"success": True, "source": "cache", "data": cached_page}

        # 2️⃣ Database
        page = await page_repo.get_page_by_id(page_id)
        if page and not force_refresh:
            await cache_service.cache_page(page_id, page)
            return {"success": True, "source": "database", "data": page}

        # 3️⃣ Scrape
        logger.info(f"🔍 Scraping LinkedIn page: {page_id}")

        # ✅ Pass LinkedIn credentials
        scraper = LinkedInScraper(
            email=settings.LINKEDIN_EMAIL,
            password=settings.LINKEDIN_PASSWORD
        )
        
        storage_service = LocalStorageService
        post_repo = PostRepository(db)
        user_repo = UserRepository(db)

        try:
            scraped_data = await scraper.scrape_page(page_id)

            # Page image
            if scraped_data.get("profile_picture"):
                try:
                    s3_url = await storage_service.process_page_images(
                        page_id, scraped_data["profile_picture"]
                    )
                    if s3_url:
                        scraped_data["profile_picture"] = s3_url
                except Exception as e:
                    logger.warning(f"⚠️ Failed to upload page image to S3: {e}")

            posts = scraped_data.pop("posts", [])
            employees = scraped_data.pop("employees", [])

            logger.info(f"📊 Scraped {len(posts)} posts and {len(employees)} employees")

            # Post images
            for post in posts:
                if post.get("media_urls"):
                    try:
                        post["media_urls"] = await storage_service.process_post_images(
                            page_id, post["post_id"], post["media_urls"]
                        )
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to upload post images: {e}")

            # Employee images
            for emp in employees:
                if emp.get("profile_picture"):
                    try:
                        emp["profile_picture"] = await storage_service.process_user_images(
                            emp["user_id"], emp["profile_picture"]
                        )
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to upload employee image: {e}")

            # Store page
            if page:
                await page_repo.update_page(page_id, scraped_data)
                logger.info(f"✅ Updated page: {page_id}")
            else:
                await page_repo.create_page(scraped_data)
                logger.info(f"✅ Created page: {page_id}")

            # Store posts & users
            if posts:
                await post_repo.create_posts(posts)
                logger.info(f"✅ Stored {len(posts)} posts")
            else:
                logger.warning(f"⚠️ No posts to store for {page_id}")
                
            if employees:
                await user_repo.create_users(employees)
                logger.info(f"✅ Stored {len(employees)} employees")
            else:
                logger.warning(f"⚠️ No employees to store for {page_id}")

            complete_page = await page_repo.get_page_by_id(page_id)
            await cache_service.cache_page(page_id, complete_page)

            return {
                "success": True,
                "source": "scraped",
                "data": complete_page,
                "stats": {
                    "posts_scraped": len(posts),
                    "employees_scraped": len(employees),
                },
            }

        finally:
            scraper.close()

    except ValueError as e:
        logger.error(f"❌ Page not found: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"❌ get_page_details error for {page_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/")
async def search_pages(
    follower_min: Optional[int] = Query(None),
    follower_max: Optional[int] = Query(None),
    industry: Optional[str] = Query(None),
    name: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """Search LinkedIn pages with filters and pagination"""
    try:
        page_repo = PageRepository(db)
        skip = (page - 1) * page_size

        pages = await page_repo.search_pages(
            follower_min=follower_min,
            follower_max=follower_max,
            industry=industry,
            name_query=name,
            skip=skip,
            limit=page_size,
        )

        query = {}
        if follower_min or follower_max:
            query["followers_count"] = {}
            if follower_min:
                query["followers_count"]["$gte"] = follower_min
            if follower_max:
                query["followers_count"]["$lte"] = follower_max
        if industry:
            query["industry"] = {"$regex": industry, "$options": "i"}
        if name:
            query["$text"] = {"$search": name}

        total = await page_repo.count_pages(query)
        total_pages = (total + page_size - 1) // page_size

        return {
            "success": True,
            "data": pages,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_items": total,
                "total_pages": total_pages,
            },
        }

    except Exception as e:
        logger.error(f"❌ search_pages error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{page_id}/posts")
async def get_page_posts(
    page_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(15, ge=1, le=50),
    db: AsyncIOMotorDatabase = Depends(get_database),
    redis=Depends(get_redis),
):
    """Get page posts with pagination"""
    try:
        # Normalize page_id
        page_id = page_id.lower().strip()
        
        cache_service = CacheService(redis)
        post_repo = PostRepository(db)

        if page == 1:
            cached_posts = await cache_service.get_cached_posts(page_id)
            if cached_posts:
                return {
                    "success": True,
                    "source": "cache",
                    "data": cached_posts[:page_size],
                }

        skip = (page - 1) * page_size
        posts = await post_repo.get_posts_by_page(page_id, skip, page_size)

        if page == 1 and posts:
            await cache_service.cache_posts(page_id, posts)

        total = await post_repo.count_posts(page_id)
        total_pages = (total + page_size - 1) // page_size

        return {
            "success": True,
            "source": "database",
            "data": posts,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_items": total,
                "total_pages": total_pages,
            },
        }

    except Exception as e:
        logger.error(f"❌ get_page_posts error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{page_id}/employees")
async def get_page_employees(
    page_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """Get employees of a LinkedIn page"""
    try:
        # Normalize page_id
        page_id = page_id.lower().strip()
        
        user_repo = UserRepository(db)
        skip = (page - 1) * page_size

        users = await user_repo.get_users_by_company(page_id, skip, page_size)
        total = await user_repo.count_users(page_id)
        total_pages = (total + page_size - 1) // page_size

        return {
            "success": True,
            "data": users,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_items": total,
                "total_pages": total_pages,
            },
        }

    except Exception as e:
        logger.error(f"❌ get_page_employees error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{page_id}/ai-summary")
async def get_ai_summary(
    page_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """AI-powered business insights"""
    try:
        # Normalize page_id
        page_id = page_id.lower().strip()
        
        page_repo = PageRepository(db)
        page = await page_repo.get_page_by_id(page_id)

        if not page:
            raise HTTPException(status_code=404, detail="Page not found")

        ai_service = AISummaryService()
        summary = await ai_service.generate_page_summary(page)

        return {
            "success": True,
            "page_id": page_id,
            "page_name": page.get("name"),
            "ai_summary": summary,
            "generated_at": datetime.utcnow().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ get_ai_summary error: {e}")
        raise HTTPException(status_code=500, detail=str(e))