from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..services.message_generator import MessageGeneratorService
from ..services.message_sender import TikTokMessageSender
from ..models.message import Message, MessageTemplate, MessageStatus
from ..models.creator import Creator
from ..schemas.message import (
    MessageTemplateCreate,
    MessageTemplateUpdate,
    MessageTemplateResponse,
    MessageCreate,
    MessageUpdate,
    MessageResponse,
    GenerateMessageRequest,
    BulkGenerateMessagesRequest,
    GenerateMessageResponse,
    SendMessageRequest,
    SendBatchMessagesRequest,
    BatchSendResponse,
    SendingStatsResponse
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/messages", tags=["messages"])

# ========== TEMPLATES ==========

@router.post("/templates", response_model=MessageTemplateResponse)
def create_template(template: MessageTemplateCreate, db: Session = Depends(get_db)):
    """Crea un nuevo template de mensaje"""
    db_template = MessageTemplate(**template.model_dump())
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template

@router.get("/templates", response_model=List[MessageTemplateResponse])
def get_templates(
    segment: str = None,
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """Lista todos los templates de mensajes"""
    query = db.query(MessageTemplate)

    if segment:
        query = query.filter(MessageTemplate.segment == segment)

    if active_only:
        query = query.filter(MessageTemplate.is_active == True)

    return query.all()

@router.get("/templates/{template_id}", response_model=MessageTemplateResponse)
def get_template(template_id: int, db: Session = Depends(get_db)):
    """Obtiene un template específico"""
    template = db.query(MessageTemplate).filter(MessageTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template

@router.put("/templates/{template_id}", response_model=MessageTemplateResponse)
def update_template(
    template_id: int,
    template_update: MessageTemplateUpdate,
    db: Session = Depends(get_db)
):
    """Actualiza un template"""
    template = db.query(MessageTemplate).filter(MessageTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    for field, value in template_update.model_dump(exclude_unset=True).items():
        setattr(template, field, value)

    db.commit()
    db.refresh(template)
    return template

@router.delete("/templates/{template_id}")
def delete_template(template_id: int, db: Session = Depends(get_db)):
    """Elimina un template"""
    template = db.query(MessageTemplate).filter(MessageTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    db.delete(template)
    db.commit()
    return {"message": "Template deleted successfully"}

# ========== MESSAGE GENERATION ==========

@router.post("/generate", response_model=GenerateMessageResponse)
async def generate_message(request: GenerateMessageRequest, db: Session = Depends(get_db)):
    """
    Genera un mensaje personalizado para un creador usando IA o templates

    - **creator_id**: ID del creador
    - **template_id**: ID del template a usar (opcional)
    - **use_ai**: Usar IA para generar (requiere OpenAI API key)
    - **tone**: Tono del mensaje (professional, casual, friendly)
    - **language**: Idioma (es, en, etc.)
    """
    # Verificar que el creador existe
    creator = db.query(Creator).filter(Creator.id == request.creator_id).first()
    if not creator:
        raise HTTPException(status_code=404, detail="Creator not found")

    generator = MessageGeneratorService()

    try:
        # Generar mensaje
        message_text = await generator.generate_personalized_message(
            creator=creator,
            template_id=request.template_id,
            use_ai=request.use_ai,
            tone=request.tone,
            db=db
        )

        # Crear registro de mensaje
        message = Message(
            creator_id=request.creator_id,
            template_id=request.template_id,
            content=message_text,
            status=MessageStatus.DRAFT
        )
        db.add(message)
        db.commit()
        db.refresh(message)

        return GenerateMessageResponse(
            message_id=message.id,
            creator_id=request.creator_id,
            content=message_text,
            status="draft"
        )

    except Exception as e:
        logger.error(f"Error generating message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate/bulk", response_model=List[GenerateMessageResponse])
async def bulk_generate_messages(
    request: BulkGenerateMessagesRequest,
    db: Session = Depends(get_db)
):
    """
    Genera mensajes para múltiples creadores

    - **creator_ids**: Lista de IDs de creadores
    - **campaign_id**: ID de campaña (opcional)
    - **use_ai**: Usar IA para generar
    - **tone**: Tono de los mensajes
    - **language**: Idioma
    """
    # Verificar que los creadores existen
    creators = db.query(Creator).filter(Creator.id.in_(request.creator_ids)).all()
    if not creators:
        raise HTTPException(status_code=404, detail="No creators found")

    generator = MessageGeneratorService()

    try:
        # Generar mensajes
        creator_messages = await generator.bulk_generate_messages(
            creators=creators,
            use_ai=request.use_ai,
            tone=request.tone,
            db=db
        )

        # Crear registros de mensajes
        messages = generator.create_message_records(
            creator_messages=creator_messages,
            campaign_id=request.campaign_id,
            db=db
        )

        return [
            GenerateMessageResponse(
                message_id=msg.id,
                creator_id=msg.creator_id,
                content=msg.content,
                status="draft"
            )
            for msg in messages
        ]

    except Exception as e:
        logger.error(f"Error in bulk generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ========== MESSAGE MANAGEMENT ==========

@router.get("/", response_model=List[MessageResponse])
def get_messages(
    campaign_id: int = None,
    status: MessageStatus = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Lista mensajes con filtros opcionales"""
    query = db.query(Message)

    if campaign_id:
        query = query.filter(Message.campaign_id == campaign_id)

    if status:
        query = query.filter(Message.status == status)

    messages = query.order_by(Message.created_at.desc()).offset(offset).limit(limit).all()
    return messages

@router.get("/{message_id}", response_model=MessageResponse)
def get_message(message_id: int, db: Session = Depends(get_db)):
    """Obtiene un mensaje específico"""
    message = db.query(Message).filter(Message.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    return message

@router.put("/{message_id}", response_model=MessageResponse)
def update_message(
    message_id: int,
    message_update: MessageUpdate,
    db: Session = Depends(get_db)
):
    """Actualiza un mensaje"""
    message = db.query(Message).filter(Message.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    for field, value in message_update.model_dump(exclude_unset=True).items():
        setattr(message, field, value)

    db.commit()
    db.refresh(message)
    return message

@router.delete("/{message_id}")
def delete_message(message_id: int, db: Session = Depends(get_db)):
    """Elimina un mensaje"""
    message = db.query(Message).filter(Message.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    db.delete(message)
    db.commit()
    return {"message": "Message deleted successfully"}

# ========== MESSAGE SENDING ==========

@router.post("/send", response_model=dict)
async def send_message(request: SendMessageRequest, db: Session = Depends(get_db)):
    """
    Envía un mensaje individual

    NOTA: Requiere credenciales de TikTok API configuradas
    """
    sender = TikTokMessageSender()

    success = await sender.send_message(request.message_id, db)

    if success:
        return {"success": True, "message_id": request.message_id}
    else:
        raise HTTPException(status_code=500, detail="Failed to send message")

@router.post("/send/batch", response_model=BatchSendResponse)
async def send_batch_messages(
    request: SendBatchMessagesRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Envía un lote de mensajes

    - **message_ids**: Lista de IDs de mensajes a enviar
    - **delay_between_messages**: Segundos entre cada mensaje (1-60)

    Los mensajes se envían en background respetando rate limits
    """
    sender = TikTokMessageSender()

    # Enviar en background
    background_tasks.add_task(
        sender.send_batch_messages,
        request.message_ids,
        db,
        request.delay_between_messages
    )

    return BatchSendResponse(
        total=len(request.message_ids),
        success=[],
        failed=[],
        skipped=[]
    )

@router.post("/queue/{campaign_id}")
def queue_campaign_messages(campaign_id: int, db: Session = Depends(get_db)):
    """Encola todos los mensajes de una campaña para envío"""
    sender = TikTokMessageSender()
    count = sender.queue_messages_for_campaign(campaign_id, db)

    return {
        "campaign_id": campaign_id,
        "messages_queued": count
    }

@router.get("/stats/sending", response_model=SendingStatsResponse)
def get_sending_stats(days: int = 7, db: Session = Depends(get_db)):
    """
    Obtiene estadísticas de envío de mensajes

    - **days**: Número de días hacia atrás (default: 7)
    """
    sender = TikTokMessageSender()
    stats = sender.get_sending_stats(db, days)

    return SendingStatsResponse(**stats)
