from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.database import (
    connect_to_mongo,
    close_mongo_connection,
    connect_to_redis,
    close_redis_connection,
    get_database,
    init_indexes,
)
from app.routes import pages


# -------------------- Logging Configuration --------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# -------------------- Application Lifespan --------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup and shutdown events
    """
    # Startup
    logger.info("🚀 Starting LinkedIn Insights API...")
    await connect_to_mongo()
    await connect_to_redis()

    # Initialize DB indexes (non-fatal if Mongo isn't available yet)
    try:
        if getattr(settings, "MONGODB_URL", None):
            db = await get_database()
            await init_indexes(db)
    except Exception as e:
        logger.warning("Skipping DB index initialization: %s", str(e))

    logger.info("✅ Application started successfully")
    yield

    # Shutdown
    logger.info("🛑 Shutting down...")
    await close_mongo_connection()
    await close_redis_connection()
    logger.info("✅ Shutdown complete")


# -------------------- FastAPI App --------------------
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="LinkedIn Insights Microservice - Scrape, Store, and Analyze LinkedIn Company Pages",
    lifespan=lifespan,
)


# -------------------- CORS Middleware --------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------- Routers --------------------
app.include_router(pages.router)


# -------------------- Root Endpoint --------------------
@app.get("/")
async def root():
    """
    Health check and API information
    """
    return {
        "message": "LinkedIn Insights API",
        "version": settings.APP_VERSION,
        "status": "operational",
        "endpoints": {
            "docs": "/docs",
            "pages": "/api/v1/pages",
        },
    }


# -------------------- Health Endpoint --------------------
@app.get("/health")
async def health_check():
    """
    Service health check
    """
    return {
        "status": "healthy",
        "service": "linkedin-insights",
        "version": settings.APP_VERSION,
    }


# -------------------- Local Development Runner --------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
