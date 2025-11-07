from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base
import enum

class MessageStatus(str, enum.Enum):
    """Estados de un mensaje"""
    DRAFT = "draft"
    QUEUED = "queued"
    SENDING = "sending"
    SENT = "sent"
    FAILED = "failed"
    RESPONDED = "responded"

class MessageTemplate(Base):
    """Plantillas de mensajes para diferentes segmentos"""
    __tablename__ = "message_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    segment = Column(String)  # Para qué segmento es este template
    subject = Column(String)  # Asunto o título del mensaje
    template_text = Column(Text)  # Texto con variables {{variable}}

    # Variables disponibles en el template
    # {{creator_name}}, {{follower_count}}, {{engagement_rate}}, {{potential_score}}, etc.

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    messages = relationship("Message", back_populates="template")

class Message(Base):
    """Mensajes enviados a creadores"""
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)

    # Relaciones
    creator_id = Column(Integer, ForeignKey("creators.id"), nullable=False)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=True)
    template_id = Column(Integer, ForeignKey("message_templates.id"), nullable=True)

    # Contenido del mensaje
    subject = Column(String)
    content = Column(Text)  # Mensaje personalizado final

    # Estado y tracking
    status = Column(Enum(MessageStatus), default=MessageStatus.DRAFT)
    scheduled_at = Column(DateTime, nullable=True)  # Para programar envíos
    sent_at = Column(DateTime, nullable=True)
    responded_at = Column(DateTime, nullable=True)

    # Respuesta del creador
    response_text = Column(Text, nullable=True)

    # Error tracking
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    creator = relationship("Creator", backref="messages")
    campaign = relationship("Campaign", back_populates="messages")
    template = relationship("MessageTemplate", back_populates="messages")

class MessageLog(Base):
    """Log de intentos de envío de mensajes"""
    __tablename__ = "message_logs"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("messages.id"), nullable=False)

    action = Column(String)  # 'sent', 'failed', 'queued', etc.
    details = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

    message = relationship("Message", backref="logs")
