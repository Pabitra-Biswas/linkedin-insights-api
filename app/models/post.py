from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class CommentModel(BaseModel):
    comment_id: str
    author_name: str
    author_profile: Optional[str] = None
    content: str
    posted_at: Optional[datetime] = None

class PostBase(BaseModel):
    post_id: str
    page_id: str
    content: str
    posted_at: Optional[datetime] = None
    likes_count: int = 0
    comments_count: int = 0
    shares_count: int = 0
    media_urls: List[str] = []
    comments: List[CommentModel] = []

class PostCreate(PostBase):
    pass

class PostInDB(PostBase):
    scraped_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class PostResponse(PostInDB):
    pass