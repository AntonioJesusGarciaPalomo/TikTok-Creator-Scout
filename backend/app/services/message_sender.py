# backend/app/services/message_sender.py
import httpx
import asyncio
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..config import settings
from ..models.message import Message, MessageLog, MessageStatus
from ..models.creator import Creator
import logging
import redis
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

class RateLimiter:
    """Rate limiter usando Redis para controlar el envío de mensajes"""

    def __init__(self, redis_url: str = None):
        self.redis_url = redis_url or settings.REDIS_URL
        try:
            self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
            self.redis_client.ping()
            logger.info("Redis connected successfully for rate limiting")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.redis_client = None

    def check_hourly_limit(self) -> bool:
        """Verifica si se ha alcanzado el límite por hora"""
        if not self.redis_client:
            return True  # Si no hay Redis, permitir (fallback)

        key = f"messages:hourly:{datetime.utcnow().strftime('%Y%m%d%H')}"
        current = self.redis_client.get(key)

        if current and int(current) >= settings.MAX_MESSAGES_PER_HOUR:
            logger.warning(f"Hourly limit reached: {current}/{settings.MAX_MESSAGES_PER_HOUR}")
            return False

        return True

    def check_daily_limit(self) -> bool:
        """Verifica si se ha alcanzado el límite diario"""
        if not self.redis_client:
            return True

        key = f"messages:daily:{datetime.utcnow().strftime('%Y%m%d')}"
        current = self.redis_client.get(key)

        if current and int(current) >= settings.MAX_MESSAGES_PER_DAY:
            logger.warning(f"Daily limit reached: {current}/{settings.MAX_MESSAGES_PER_DAY}")
            return False

        return True

    def increment_counters(self):
        """Incrementa los contadores de mensajes enviados"""
        if not self.redis_client:
            return

        now = datetime.utcnow()
        hourly_key = f"messages:hourly:{now.strftime('%Y%m%d%H')}"
        daily_key = f"messages:daily:{now.strftime('%Y%m%d')}"

        # Incrementar y poner TTL
        pipe = self.redis_client.pipeline()
        pipe.incr(hourly_key)
        pipe.expire(hourly_key, 3600)  # 1 hora
        pipe.incr(daily_key)
        pipe.expire(daily_key, 86400)  # 24 horas
        pipe.execute()

    def get_current_counts(self) -> Dict[str, int]:
        """Obtiene los contadores actuales"""
        if not self.redis_client:
            return {"hourly": 0, "daily": 0}

        now = datetime.utcnow()
        hourly_key = f"messages:hourly:{now.strftime('%Y%m%d%H')}"
        daily_key = f"messages:daily:{now.strftime('%Y%m%d')}"

        hourly = self.redis_client.get(hourly_key) or 0
        daily = self.redis_client.get(daily_key) or 0

        return {
            "hourly": int(hourly),
            "daily": int(daily),
            "hourly_limit": settings.MAX_MESSAGES_PER_HOUR,
            "daily_limit": settings.MAX_MESSAGES_PER_DAY
        }


class TikTokMessageSender:
    """Servicio para enviar mensajes a creadores de TikTok"""

    def __init__(self):
        self.rate_limiter = RateLimiter()
        self.access_token = settings.TIKTOK_ACCESS_TOKEN
        self.client_key = settings.TIKTOK_CLIENT_KEY
        self.client_secret = settings.TIKTOK_CLIENT_SECRET

        if not self.access_token:
            logger.warning("TikTok API credentials not configured. Messages will be queued but not sent.")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def send_direct_message(self, recipient_username: str, message_content: str) -> Dict:
        """
        Envía un mensaje directo a un usuario de TikTok

        NOTA: Esta es una implementación de referencia. La API oficial de TikTok
        para envío de DMs requiere aprobación especial y acceso Business.
        """
        if not self.access_token:
            logger.warning("Simulating message send (no TikTok credentials)")
            return {
                "success": True,
                "simulated": True,
                "message": "Message would be sent in production"
            }

        # URL de la API de TikTok (esto es un ejemplo, la URL real puede variar)
        url = "https://open-api.tiktok.com/v1/message/send/"

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "recipient_username": recipient_username,
            "message": message_content,
            "client_key": self.client_key
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error sending message to {recipient_username}: {e}")
            raise

    def log_message_action(self, message: Message, action: str, details: str, db: Session):
        """Registra una acción en el log de mensajes"""
        log_entry = MessageLog(
            message_id=message.id,
            action=action,
            details=details,
            timestamp=datetime.utcnow()
        )
        db.add(log_entry)
        db.commit()

    async def send_message(self, message_id: int, db: Session) -> bool:
        """
        Envía un mensaje específico

        Returns:
            True si se envió exitosamente, False en caso contrario
        """
        # Verificar límites de rate
        if not self.rate_limiter.check_hourly_limit():
            logger.warning("Hourly rate limit reached")
            return False

        if not self.rate_limiter.check_daily_limit():
            logger.warning("Daily rate limit reached")
            return False

        # Obtener mensaje
        message = db.query(Message).filter(Message.id == message_id).first()
        if not message:
            logger.error(f"Message {message_id} not found")
            return False

        # Verificar que esté en estado apropiado
        if message.status not in [MessageStatus.QUEUED, MessageStatus.DRAFT, MessageStatus.FAILED]:
            logger.warning(f"Message {message_id} is in status {message.status}, cannot send")
            return False

        # Obtener información del creador
        creator = db.query(Creator).filter(Creator.id == message.creator_id).first()
        if not creator:
            logger.error(f"Creator {message.creator_id} not found")
            message.status = MessageStatus.FAILED
            message.error_message = "Creator not found"
            db.commit()
            return False

        # Actualizar estado a "sending"
        message.status = MessageStatus.SENDING
        db.commit()
        self.log_message_action(message, "sending", f"Sending message to {creator.username}", db)

        try:
            # Enviar mensaje
            result = await self.send_direct_message(creator.username, message.content)

            # Si fue exitoso
            if result.get("success") or result.get("simulated"):
                message.status = MessageStatus.SENT
                message.sent_at = datetime.utcnow()
                self.rate_limiter.increment_counters()

                self.log_message_action(
                    message,
                    "sent",
                    f"Message sent successfully to {creator.username}",
                    db
                )

                logger.info(f"Message {message.id} sent to {creator.username}")
                db.commit()
                return True

        except Exception as e:
            # Manejar error
            message.status = MessageStatus.FAILED
            message.error_message = str(e)
            message.retry_count += 1

            self.log_message_action(
                message,
                "failed",
                f"Failed to send: {str(e)}",
                db
            )

            logger.error(f"Failed to send message {message.id}: {e}")
            db.commit()
            return False

    async def send_batch_messages(
        self,
        message_ids: List[int],
        db: Session,
        delay_between_messages: float = 5.0
    ) -> Dict[str, List[int]]:
        """
        Envía un lote de mensajes con delay entre cada uno

        Args:
            message_ids: Lista de IDs de mensajes a enviar
            db: Sesión de base de datos
            delay_between_messages: Segundos de espera entre mensajes

        Returns:
            Diccionario con listas de éxitos y fallos
        """
        results = {
            "success": [],
            "failed": [],
            "skipped": []
        }

        for message_id in message_ids:
            # Verificar límites antes de cada mensaje
            if not self.rate_limiter.check_hourly_limit() or not self.rate_limiter.check_daily_limit():
                logger.warning(f"Rate limit reached, skipping remaining messages")
                results["skipped"].extend(message_ids[len(results["success"]) + len(results["failed"]):])
                break

            # Enviar mensaje
            success = await self.send_message(message_id, db)

            if success:
                results["success"].append(message_id)
            else:
                results["failed"].append(message_id)

            # Delay entre mensajes para evitar rate limiting
            if message_id != message_ids[-1]:  # No delay después del último
                await asyncio.sleep(delay_between_messages)

        logger.info(
            f"Batch complete: {len(results['success'])} sent, "
            f"{len(results['failed'])} failed, {len(results['skipped'])} skipped"
        )

        return results

    def queue_messages_for_campaign(self, campaign_id: int, db: Session) -> int:
        """
        Marca mensajes de una campaña como QUEUED para envío

        Returns:
            Número de mensajes encolados
        """
        messages = db.query(Message).filter(
            Message.campaign_id == campaign_id,
            Message.status == MessageStatus.DRAFT
        ).all()

        count = 0
        for message in messages:
            message.status = MessageStatus.QUEUED
            count += 1

        db.commit()
        logger.info(f"Queued {count} messages for campaign {campaign_id}")
        return count

    def get_queued_messages(self, db: Session, limit: int = 50) -> List[Message]:
        """Obtiene mensajes en cola para enviar"""
        return db.query(Message).filter(
            Message.status == MessageStatus.QUEUED
        ).order_by(Message.created_at).limit(limit).all()

    def get_sending_stats(self, db: Session, days: int = 7) -> Dict:
        """Obtiene estadísticas de envío de mensajes"""
        since = datetime.utcnow() - timedelta(days=days)

        stats = {
            "total_sent": db.query(Message).filter(
                Message.status == MessageStatus.SENT,
                Message.sent_at >= since
            ).count(),
            "total_failed": db.query(Message).filter(
                Message.status == MessageStatus.FAILED,
                Message.updated_at >= since
            ).count(),
            "total_queued": db.query(Message).filter(
                Message.status == MessageStatus.QUEUED
            ).count(),
            "total_responded": db.query(Message).filter(
                Message.status == MessageStatus.RESPONDED,
                Message.responded_at >= since
            ).count(),
            "rate_limits": self.rate_limiter.get_current_counts()
        }

        if stats["total_sent"] > 0:
            stats["response_rate"] = (stats["total_responded"] / stats["total_sent"]) * 100
        else:
            stats["response_rate"] = 0.0

        return stats
