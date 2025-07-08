from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class CreatorBase(BaseModel):
    username: str
    display_name: str
    bio: Optional[str] = None
    verified: bool = False

class CreatorCreate(CreatorBase):
    pass

class CreatorResponse(CreatorBase):
    id: int
    user_id: str
    avatar_url: Optional[str]
    
    # Métricas
    followers_count: int
    following_count: int
    likes_count: int
    videos_count: int
    
    # Análisis
    engagement_rate: float
    avg_likes_per_video: float
    avg_comments_per_video: float
    growth_rate: float
    posting_frequency: float
    segment: Optional[str]
    potential_score: float
    
    created_at: datetime
    updated_at: datetime
    last_scraped: Optional[datetime]
    
    class Config:
        from_attributes = True

class CreatorFilter(BaseModel):
    min_followers: Optional[int] = None
    max_followers: Optional[int] = None
    min_engagement: Optional[float] = None
    min_posting_frequency: Optional[float] = None
    min_growth_rate: Optional[float] = None
    segments: Optional[List[str]] = None

class VideoResponse(BaseModel):
    id: int
    video_id: str
    description: str
    duration: int
    cover_url: str
    likes_count: int
    comments_count: int
    shares_count: int
    views_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True