from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

class CreatorMetrics(Base):
    __tablename__ = "creator_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    creator_id = Column(Integer, ForeignKey("creators.id"))
    
    # Snapshot de métricas en un momento específico
    followers_count = Column(Integer)
    likes_count = Column(Integer)
    videos_count = Column(Integer)
    
    # Métricas calculadas
    daily_growth = Column(Float)
    weekly_growth = Column(Float)
    monthly_growth = Column(Float)
    
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    creator = relationship("Creator", back_populates="metrics")

class Video(Base):
    __tablename__ = "videos"
    
    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(String, unique=True)
    creator_id = Column(Integer, ForeignKey("creators.id"))
    
    # Información del video
    description = Column(String)
    duration = Column(Integer)
    cover_url = Column(String)
    video_url = Column(String)
    
    # Métricas
    likes_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    shares_count = Column(Integer, default=0)
    views_count = Column(Integer, default=0)
    
    # Metadata
    hashtags = Column(JSON)
    music_info = Column(JSON)
    created_at = Column(DateTime)
    scraped_at = Column(DateTime, default=datetime.utcnow)
    
    creator = relationship("Creator", back_populates="videos")