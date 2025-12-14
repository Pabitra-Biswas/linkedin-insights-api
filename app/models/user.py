from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    user_id: str
    name: str
    profile_url: str
    profile_picture: Optional[str] = None
    headline: Optional[str] = None
    current_company: Optional[str] = None

class UserCreate(UserBase):
    pass

class UserInDB(UserBase):
    scraped_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

class UserResponse(UserInDB):
    pass