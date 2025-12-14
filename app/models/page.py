from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class PageBase(BaseModel):
    page_id: str
    name: str
    url: str
    linkedin_id: Optional[str] = None
    profile_picture: Optional[str] = None
    description: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None
    followers_count: int = 0
    head_count: Optional[str] = None
    specialities: List[str] = []

class PageCreate(PageBase):
    pass

class PageInDB(PageBase):
    scraped_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class PageResponse(PageInDB):
    pass