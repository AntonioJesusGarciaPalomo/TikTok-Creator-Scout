from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

class Campaign(Base):
    """Campañas de outreach a creadores"""
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(Text)

    # Configuración
    target_segment = Column(String)  # Qué segmento targetear
    filters = Column(JSON)  # Filtros aplicados (followers, engagement, etc.)

    # Configuración de mensajería
    auto_send = Column(Boolean, default=False)  # Enviar automáticamente
    daily_limit = Column(Integer, default=50)  # Límite de mensajes por día
    messages_per_hour = Column(Integer, default=10)  # Rate limiting

    # Estado
    is_active = Column(Boolean, default=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Estadísticas
    total_targets = Column(Integer, default=0)
    messages_sent = Column(Integer, default=0)
    messages_failed = Column(Integer, default=0)
    responses_received = Column(Integer, default=0)
    response_rate = Column(Float, default=0.0)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    messages = relationship("Message", back_populates="campaign")
    searches = relationship("CreatorSearch", back_populates="campaign")

class CreatorSearch(Base):
    """Búsquedas guardadas de creadores"""
    __tablename__ = "creator_searches"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=True)

    # Tipo de búsqueda
    search_type = Column(String)  # 'hashtag', 'trend', 'keyword', 'location', 'challenge'

    # Parámetros de búsqueda
    query = Column(String)  # Hashtag, keyword, etc.
    location = Column(String, nullable=True)
    category = Column(String, nullable=True)

    # Filtros adicionales
    filters = Column(JSON)  # Filtros de followers, engagement, etc.

    # Resultados
    results_count = Column(Integer, default=0)
    last_executed = Column(DateTime, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    campaign = relationship("Campaign", back_populates="searches")
