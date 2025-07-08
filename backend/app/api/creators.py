from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models.creator import Creator
from ..schemas.creator import CreatorResponse, CreatorFilter
from ..services.segmentation import CreatorSegmentation

router = APIRouter(prefix="/creators", tags=["creators"])

@router.get("/", response_model=List[CreatorResponse])
def get_creators(
    db: Session = Depends(get_db),
    min_followers: Optional[int] = Query(None),
    min_engagement: Optional[float] = Query(None),
    min_posting_frequency: Optional[float] = Query(None),
    min_growth_rate: Optional[float] = Query(None),
    segment: Optional[str] = Query(None),
    limit: int = Query(100, le=1000),
    offset: int = Query(0)
):
    """Obtiene creadores con filtros opcionales"""
    query = db.query(Creator)
    
    if min_followers:
        query = query.filter(Creator.followers_count >= min_followers)
    if min_engagement:
        query = query.filter(Creator.engagement_rate >= min_engagement)
    if min_posting_frequency:
        query = query.filter(Creator.posting_frequency >= min_posting_frequency)
    if min_growth_rate:
        query = query.filter(Creator.growth_rate >= min_growth_rate)
    if segment:
        query = query.filter(Creator.segment == segment)
    
    creators = query.offset(offset).limit(limit).all()
    return creators

@router.get("/{username}", response_model=CreatorResponse)
def get_creator(username: str, db: Session = Depends(get_db)):
    """Obtiene un creador específico"""
    creator = db.query(Creator).filter(Creator.username == username).first()
    if not creator:
        raise HTTPException(status_code=404, detail="Creator not found")
    return creator

@router.get("/segments/summary")
def get_segments_summary(db: Session = Depends(get_db)):
    """Obtiene resumen de segmentos"""
    segmentation = CreatorSegmentation()
    creators = db.query(Creator).all()
    
    segments = {}
    for creator in creators:
        if creator.segment not in segments:
            segments[creator.segment] = {
                "count": 0,
                "avg_followers": 0,
                "avg_engagement": 0,
                "avg_growth": 0,
                "creators": []
            }
        
        segment = segments[creator.segment]
        segment["count"] += 1
        segment["avg_followers"] += creator.followers_count
        segment["avg_engagement"] += creator.engagement_rate
        segment["avg_growth"] += creator.growth_rate
        segment["creators"].append({
            "username": creator.username,
            "potential_score": creator.potential_score
        })
    
    # Calcular promedios
    for segment_data in segments.values():
        count = segment_data["count"]
        if count > 0:
            segment_data["avg_followers"] /= count
            segment_data["avg_engagement"] /= count
            segment_data["avg_growth"] /= count
    
    return segments