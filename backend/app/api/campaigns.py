from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models.campaign import Campaign
from ..models.message import Message, MessageStatus
from ..models.creator import Creator
from ..services.message_generator import MessageGeneratorService
from ..services.segmentation import CreatorSegmentation
from ..schemas.campaign import (
    CampaignCreate,
    CampaignUpdate,
    CampaignResponse,
    CampaignWithStats
)
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/campaigns", tags=["campaigns"])

@router.post("/", response_model=CampaignResponse)
def create_campaign(campaign: CampaignCreate, db: Session = Depends(get_db)):
    """
    Crea una nueva campaña de outreach

    - **name**: Nombre de la campaña
    - **description**: Descripción
    - **target_segment**: Segmento objetivo (Rising Stars, High Engagement, etc.)
    - **filters**: Filtros adicionales (min_followers, min_engagement, etc.)
    - **auto_send**: Enviar mensajes automáticamente
    - **daily_limit**: Límite de mensajes por día
    - **messages_per_hour**: Rate limiting
    """
    db_campaign = Campaign(**campaign.model_dump())
    db.add(db_campaign)
    db.commit()
    db.refresh(db_campaign)
    return db_campaign

@router.get("/", response_model=List[CampaignResponse])
def get_campaigns(
    active_only: bool = False,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Lista todas las campañas"""
    query = db.query(Campaign)

    if active_only:
        query = query.filter(Campaign.is_active == True)

    campaigns = query.order_by(Campaign.created_at.desc()).offset(offset).limit(limit).all()
    return campaigns

@router.get("/{campaign_id}", response_model=CampaignWithStats)
def get_campaign(campaign_id: int, db: Session = Depends(get_db)):
    """Obtiene una campaña específica con estadísticas"""
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()

    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    # Calcular estadísticas adicionales
    pending_messages = db.query(Message).filter(
        Message.campaign_id == campaign_id,
        Message.status == MessageStatus.DRAFT
    ).count()

    queued_messages = db.query(Message).filter(
        Message.campaign_id == campaign_id,
        Message.status == MessageStatus.QUEUED
    ).count()

    # Convertir a dict y agregar stats
    campaign_dict = {
        **{c.name: getattr(campaign, c.name) for c in campaign.__table__.columns},
        "pending_messages": pending_messages,
        "queued_messages": queued_messages
    }

    return campaign_dict

@router.put("/{campaign_id}", response_model=CampaignResponse)
def update_campaign(
    campaign_id: int,
    campaign_update: CampaignUpdate,
    db: Session = Depends(get_db)
):
    """Actualiza una campaña"""
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()

    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    for field, value in campaign_update.model_dump(exclude_unset=True).items():
        setattr(campaign, field, value)

    db.commit()
    db.refresh(campaign)
    return campaign

@router.delete("/{campaign_id}")
def delete_campaign(campaign_id: int, db: Session = Depends(get_db)):
    """Elimina una campaña"""
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()

    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    db.delete(campaign)
    db.commit()
    return {"message": "Campaign deleted successfully"}

@router.post("/{campaign_id}/start")
def start_campaign(campaign_id: int, db: Session = Depends(get_db)):
    """Inicia una campaña"""
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()

    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    campaign.is_active = True
    campaign.started_at = datetime.utcnow()
    db.commit()

    return {"message": "Campaign started", "campaign_id": campaign_id}

@router.post("/{campaign_id}/stop")
def stop_campaign(campaign_id: int, db: Session = Depends(get_db)):
    """Detiene una campaña"""
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()

    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    campaign.is_active = False
    db.commit()

    return {"message": "Campaign stopped", "campaign_id": campaign_id}

@router.post("/{campaign_id}/complete")
def complete_campaign(campaign_id: int, db: Session = Depends(get_db)):
    """Marca una campaña como completada"""
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()

    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    campaign.is_active = False
    campaign.completed_at = datetime.utcnow()
    db.commit()

    return {"message": "Campaign completed", "campaign_id": campaign_id}

@router.post("/{campaign_id}/generate-messages")
async def generate_campaign_messages(
    campaign_id: int,
    background_tasks: BackgroundTasks,
    use_ai: bool = True,
    tone: str = "professional",
    db: Session = Depends(get_db)
):
    """
    Genera mensajes para todos los creadores objetivo de la campaña

    - **use_ai**: Usar IA para generación
    - **tone**: Tono de los mensajes (professional, casual, friendly)

    Los mensajes se generan en background
    """
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()

    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    # Obtener creadores según filtros de la campaña
    query = db.query(Creator)

    # Aplicar segmento objetivo
    if campaign.target_segment:
        query = query.filter(Creator.segment == campaign.target_segment)

    # Aplicar filtros adicionales
    filters = campaign.filters or {}
    segmentation = CreatorSegmentation()
    creators = query.all()
    filtered_creators = segmentation.apply_filters(creators, filters)

    if not filtered_creators:
        raise HTTPException(status_code=404, detail="No creators found matching campaign criteria")

    # Actualizar total_targets
    campaign.total_targets = len(filtered_creators)
    db.commit()

    # Generar mensajes en background
    async def generate_messages_task():
        generator = MessageGeneratorService()
        try:
            creator_messages = await generator.bulk_generate_messages(
                creators=filtered_creators,
                use_ai=use_ai,
                tone=tone,
                db=db
            )

            messages = generator.create_message_records(
                creator_messages=creator_messages,
                campaign_id=campaign_id,
                db=db
            )

            logger.info(f"Generated {len(messages)} messages for campaign {campaign_id}")

        except Exception as e:
            logger.error(f"Error generating messages for campaign {campaign_id}: {e}")

    background_tasks.add_task(generate_messages_task)

    return {
        "message": "Message generation started",
        "campaign_id": campaign_id,
        "target_creators": len(filtered_creators)
    }

@router.get("/{campaign_id}/messages")
def get_campaign_messages(
    campaign_id: int,
    status: MessageStatus = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Obtiene los mensajes de una campaña"""
    query = db.query(Message).filter(Message.campaign_id == campaign_id)

    if status:
        query = query.filter(Message.status == status)

    messages = query.order_by(Message.created_at.desc()).offset(offset).limit(limit).all()
    return messages

@router.get("/{campaign_id}/stats")
def get_campaign_stats(campaign_id: int, db: Session = Depends(get_db)):
    """Obtiene estadísticas detalladas de una campaña"""
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()

    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    # Estadísticas por estado de mensaje
    stats_by_status = {}
    for status in MessageStatus:
        count = db.query(Message).filter(
            Message.campaign_id == campaign_id,
            Message.status == status
        ).count()
        stats_by_status[status.value] = count

    return {
        "campaign_id": campaign_id,
        "campaign_name": campaign.name,
        "is_active": campaign.is_active,
        "total_targets": campaign.total_targets,
        "messages_sent": campaign.messages_sent,
        "messages_failed": campaign.messages_failed,
        "responses_received": campaign.responses_received,
        "response_rate": campaign.response_rate,
        "stats_by_status": stats_by_status,
        "started_at": campaign.started_at,
        "completed_at": campaign.completed_at
    }
