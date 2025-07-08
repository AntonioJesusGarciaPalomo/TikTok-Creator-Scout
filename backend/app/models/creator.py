from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

class Creator(Base):
    __tablename__ = "creators"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    user_id = Column(String, unique=True)
    display_name = Column(String)
    avatar_url = Column(String)
    bio = Column(String)
    verified = Column(Boolean, default=False)
    
    # Métricas básicas
    followers_count = Column(Integer, default=0)
    following_count = Column(Integer, default=0)
    likes_count = Column(Integer, default=0)
    videos_count = Column(Integer, default=0)
    
    # Métricas calculadas
    engagement_rate = Column(Float, default=0.0)
    avg_likes_per_video = Column(Float, default=0.0)
    avg_comments_per_video = Column(Float, default=0.0)
    growth_rate = Column(Float, default=0.0)
    posting_frequency = Column(Float, default=0.0)  # videos por semana
    
    # Segmentación
    segment = Column(String)
    potential_score = Column(Float, default=0.0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_scraped = Column(DateTime)
    
    # Relaciones
    metrics = relationship("CreatorMetrics", back_populates="creator")
    videos = relationship("Video", back_populates="creator")