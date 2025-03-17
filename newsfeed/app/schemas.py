from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, EmailStr, Field

# User schemas
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserLogin(BaseModel):
    username: str
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None

class UserProfile(UserBase):
    id: int
    followers_count: int
    following_count: int
    posts_count: int
    created_at: datetime

    class Config:
        from_attributes = True

# Content schemas
class ContentBase(BaseModel):
    content_type: str
    content: str
    title: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class ContentCreate(ContentBase):
    pass

class ContentUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class ContentEngagement(BaseModel):
    engagement_type: str = Field(..., regex="^(like|comment|share)$")

class ContentResponse(ContentBase):
    id: int
    creator: Dict[str, Any]
    engagement: Dict[str, int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Feed schemas
class FeedItem(BaseModel):
    id: int
    content_id: int
    content_type: str
    title: Optional[str]
    content: str
    creator: str
    score: float
    created_at: datetime
    engagement: Dict[str, int]

    class Config:
        from_attributes = True

class FeedResponse(BaseModel):
    items: List[FeedItem]
    page: int
    total_pages: int
    total_items: int

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: Optional[str] = None 