from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # App Config
    APP_NAME: str = "LinkedIn Insights API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # MongoDB
    MONGODB_URL: str
    MONGODB_DB_NAME: str = "linkedin_insights"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_TTL: int = 300  # 5 minutes
    
    # Local storage (replaces S3)
    LOCAL_STORAGE_PATH: str = "./data/uploads"

# OpenAI (optional; replaced by Gemini by default)
    OPENAI_API_KEY: Optional[str] = None

    # Google Gemini (langchain-google-genai)
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.0-flash"

    # Scraping
    SCRAPE_TIMEOUT: int = 30
    HEADLESS_MODE: bool = True
    
    
    # LinkedIn Credentials (ADD THIS)
    LINKEDIN_EMAIL: Optional[str] = None
    LINKEDIN_PASSWORD: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()