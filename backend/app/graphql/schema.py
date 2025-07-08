import strawberry
from typing import List, Optional
from datetime import datetime
from strawberry.types import Info
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.creator import Creator as CreatorModel
from ..services.segmentation import CreatorSegmentation
from ..services.analyzer import CreatorAnalyzer

@strawberry.type
class Creator:
    id: int
    username: str
    display_name: str
    avatar_url: Optional[str]
    bio: Optional[str]
    verified: bool
    
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

@strawberry.type
class CreatorMetrics:
    id: int
    creator_id: int
    followers_count: int
    likes_count: int
    videos_count: int
    daily_growth: Optional[float]
    weekly_growth: Optional[float]
    monthly_growth: Optional[float]
    timestamp: datetime

@strawberry.type
class SegmentAnalysis:
    segment_name: str
    creator_count: int
    avg_followers: float
    avg_engagement: float
    avg_growth: float
    ai_insights: Optional[str]

@strawberry.input
class CreatorFilter:
    min_followers: Optional[int] = None
    max_followers: Optional[int] = None
    min_engagement: Optional[float] = None
    min_posting_frequency: Optional[float] = None
    min_growth_rate: Optional[float] = None
    segments: Optional[List[str]] = None

@strawberry.type
class Query:
    @strawberry.field
    def creators(
        self, 
        info: Info,
        filters: Optional[CreatorFilter] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Creator]:
        db: Session = next(get_db())
        query = db.query(CreatorModel)
        
        if filters:
            if filters.min_followers:
                query = query.filter(CreatorModel.followers_count >= filters.min_followers)
            if filters.max_followers:
                query = query.filter(CreatorModel.followers_count <= filters.max_followers)
            if filters.min_engagement:
                query = query.filter(CreatorModel.engagement_rate >= filters.min_engagement)
            if filters.min_posting_frequency:
                query = query.filter(CreatorModel.posting_frequency >= filters.min_posting_frequency)
            if filters.min_growth_rate:
                query = query.filter(CreatorModel.growth_rate >= filters.min_growth_rate)
            if filters.segments:
                query = query.filter(CreatorModel.segment.in_(filters.segments))
        
        creators = query.offset(offset).limit(limit).all()
        return [Creator(**creator.__dict__) for creator in creators]
    
    @strawberry.field
    def creator(self, info: Info, username: str) -> Optional[Creator]:
        db: Session = next(get_db())
        creator = db.query(CreatorModel).filter(CreatorModel.username == username).first()
        return Creator(**creator.__dict__) if creator else None
    
    @strawberry.field
    async def segment_analysis(self, info: Info) -> List[SegmentAnalysis]:
        db: Session = next(get_db())
        segmentation = CreatorSegmentation()
        
        # Obtener todos los creadores
        creators = db.query(CreatorModel).all()
        segmented = segmentation.segment_creators(creators)
        
        analyses = []
        for segment_id, segment_creators in segmented.items():
            segment_name = segmentation.segments.get(segment_id, f"Segment {segment_id}")
            
            # Análisis con IA
            ai_analysis = await segmentation.analyze_segment_with_ai(segment_creators)
            
            analysis = SegmentAnalysis(
                segment_name=segment_name,
                creator_count=len(segment_creators),
                avg_followers=ai_analysis["metrics"]["avg_followers"],
                avg_engagement=ai_analysis["metrics"]["avg_engagement"],
                avg_growth=ai_analysis["metrics"]["avg_growth"],
                ai_insights=ai_analysis["segment_analysis"]
            )
            analyses.append(analysis)
        
        return analyses

@strawberry.type
class Mutation:
    @strawberry.mutation
    async def scrape_creator(self, info: Info, username: str) -> Creator:
        from ..services.tiktok_scraper import TikTokScraperService
        
        db: Session = next(get_db())
        scraper = TikTokScraperService()
        
        creator = await scraper.scrape_and_save_creator(username, db)
        if creator:
            # Actualizar análisis
            analyzer = CreatorAnalyzer()
            analyzer.update_creator_analytics(creator, db)
            
            return Creator(**creator.__dict__)
        else:
            raise Exception(f"Failed to scrape creator: {username}")
    
    @strawberry.mutation
    async def batch_scrape(self, info: Info, usernames: List[str]) -> List[Creator]:
        from ..services.tiktok_scraper import TikTokScraperService
        
        db: Session = next(get_db())
        scraper = TikTokScraperService()
        
        creators = await scraper.batch_scrape_creators(usernames, db)
        
        # Actualizar análisis para todos
        analyzer = CreatorAnalyzer()
        for creator in creators:
            analyzer.update_creator_analytics(creator, db)
        
        return [Creator(**c.__dict__) for c in creators]
    
    @strawberry.mutation
    def update_segments(self, info: Info) -> bool:
        db: Session = next(get_db())
        segmentation = CreatorSegmentation()
        
        creators = db.query(CreatorModel).all()
        segmentation.segment_creators(creators)
        
        db.commit()
        return True

schema = strawberry.Schema(query=Query, mutation=Mutation)