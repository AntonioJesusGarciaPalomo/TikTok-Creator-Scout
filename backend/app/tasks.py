# backend/app/tasks.py
from celery import Task
from .celery_app import celery_app
from .database import SessionLocal
from .services.tiktok_scraper import TikTokScraperService
from .services.creator_search import CreatorSearchService
from .services.message_generator import MessageGeneratorService
from .services.message_sender import TikTokMessageSender
from .services.analyzer import CreatorAnalyzer
from .services.segmentation import CreatorSegmentation
from .models.creator import Creator
from .models.message import Message, MessageStatus
from .models.campaign import Campaign
import logging
import asyncio

logger = logging.getLogger(__name__)

class DatabaseTask(Task):
    """Clase base para tareas que usan la base de datos"""
    _db = None

    @property
    def db(self):
        if self._db is None:
            self._db = SessionLocal()
        return self._db

    def after_return(self, *args, **kwargs):
        if self._db is not None:
            self._db.close()
            self._db = None

# ========== SCRAPING TASKS ==========

@celery_app.task(base=DatabaseTask, bind=True)
def scrape_creator_task(self, username: str):
    """Tarea para scrapear un creador individual"""
    logger.info(f"Starting scrape task for creator: {username}")

    scraper = TikTokScraperService()

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    creator = loop.run_until_complete(
        scraper.scrape_and_save_creator(username, self.db)
    )

    if creator:
        logger.info(f"Successfully scraped creator: {username}")
        return {"success": True, "creator_id": creator.id, "username": username}
    else:
        logger.error(f"Failed to scrape creator: {username}")
        return {"success": False, "username": username}

@celery_app.task(base=DatabaseTask, bind=True)
def batch_scrape_creators_task(self, usernames: list):
    """Tarea para scrapear múltiples creadores"""
    logger.info(f"Starting batch scrape for {len(usernames)} creators")

    scraper = TikTokScraperService()

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    creators = loop.run_until_complete(
        scraper.batch_scrape_creators(usernames, self.db)
    )

    logger.info(f"Batch scrape complete: {len(creators)} creators scraped")
    return {
        "success": True,
        "total": len(usernames),
        "scraped": len(creators)
    }

# ========== SEARCH TASKS ==========

@celery_app.task(base=DatabaseTask, bind=True)
def search_and_scrape_task(self, search_type: str, query: str, filters: dict = None):
    """Búsqueda de creadores y scraping automático"""
    logger.info(f"Starting search task: {search_type} - {query}")

    search_service = CreatorSearchService()
    scraper = TikTokScraperService()

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    # Buscar creadores
    creators = loop.run_until_complete(
        search_service.discover_creators(search_type, query, filters, self.db)
    )

    logger.info(f"Found {len(creators)} creators")

    # Scrapear automáticamente
    usernames = [c["username"] for c in creators if c.get("username")][:50]

    if usernames:
        scraped_creators = loop.run_until_complete(
            scraper.batch_scrape_creators(usernames, self.db)
        )
        logger.info(f"Auto-scraped {len(scraped_creators)} creators")

        return {
            "success": True,
            "found": len(creators),
            "scraped": len(scraped_creators)
        }

    return {"success": True, "found": len(creators), "scraped": 0}

# ========== MESSAGE TASKS ==========

@celery_app.task(base=DatabaseTask, bind=True)
def generate_message_task(self, creator_id: int, campaign_id: int = None, use_ai: bool = True):
    """Genera un mensaje para un creador"""
    logger.info(f"Generating message for creator {creator_id}")

    creator = self.db.query(Creator).filter(Creator.id == creator_id).first()
    if not creator:
        logger.error(f"Creator {creator_id} not found")
        return {"success": False, "error": "Creator not found"}

    generator = MessageGeneratorService()

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    message_text = loop.run_until_complete(
        generator.generate_personalized_message(creator, use_ai=use_ai, db=self.db)
    )

    # Crear registro de mensaje
    message = Message(
        creator_id=creator_id,
        campaign_id=campaign_id,
        content=message_text,
        status=MessageStatus.DRAFT
    )
    self.db.add(message)
    self.db.commit()

    logger.info(f"Message generated for creator {creator_id}, message_id: {message.id}")

    return {"success": True, "message_id": message.id, "creator_id": creator_id}

@celery_app.task(base=DatabaseTask, bind=True)
def bulk_generate_messages_task(
    self,
    creator_ids: list,
    campaign_id: int = None,
    use_ai: bool = True
):
    """Genera mensajes para múltiples creadores"""
    logger.info(f"Bulk generating messages for {len(creator_ids)} creators")

    creators = self.db.query(Creator).filter(Creator.id.in_(creator_ids)).all()
    generator = MessageGeneratorService()

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    creator_messages = loop.run_until_complete(
        generator.bulk_generate_messages(creators, use_ai, db=self.db)
    )

    messages = generator.create_message_records(
        creator_messages,
        campaign_id,
        self.db
    )

    logger.info(f"Generated {len(messages)} messages")

    return {
        "success": True,
        "total": len(creator_ids),
        "generated": len(messages)
    }

@celery_app.task(base=DatabaseTask, bind=True)
def send_message_task(self, message_id: int):
    """Envía un mensaje individual"""
    logger.info(f"Sending message {message_id}")

    sender = TikTokMessageSender()

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    success = loop.run_until_complete(
        sender.send_message(message_id, self.db)
    )

    return {"success": success, "message_id": message_id}

@celery_app.task(base=DatabaseTask, bind=True)
def send_batch_messages_task(self, message_ids: list, delay: float = 5.0):
    """Envía un lote de mensajes"""
    logger.info(f"Sending batch of {len(message_ids)} messages")

    sender = TikTokMessageSender()

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    results = loop.run_until_complete(
        sender.send_batch_messages(message_ids, self.db, delay)
    )

    logger.info(f"Batch send complete: {len(results['success'])} sent, {len(results['failed'])} failed")

    return results

@celery_app.task(base=DatabaseTask, bind=True)
def process_queued_messages(self):
    """Procesa mensajes en cola (tarea periódica)"""
    logger.info("Processing queued messages")

    sender = TikTokMessageSender()
    queued = sender.get_queued_messages(self.db, limit=50)

    if not queued:
        logger.info("No queued messages to process")
        return {"success": True, "processed": 0}

    message_ids = [msg.id for msg in queued]

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    results = loop.run_until_complete(
        sender.send_batch_messages(message_ids, self.db, delay_between_messages=10.0)
    )

    logger.info(f"Processed {len(message_ids)} queued messages")

    return {
        "success": True,
        "processed": len(message_ids),
        "sent": len(results['success']),
        "failed": len(results['failed']),
        "skipped": len(results['skipped'])
    }

# ========== ANALYTICS TASKS ==========

@celery_app.task(base=DatabaseTask, bind=True)
def update_creator_analytics_task(self, creator_id: int):
    """Actualiza las analíticas de un creador"""
    logger.info(f"Updating analytics for creator {creator_id}")

    creator = self.db.query(Creator).filter(Creator.id == creator_id).first()
    if not creator:
        logger.error(f"Creator {creator_id} not found")
        return {"success": False, "error": "Creator not found"}

    analyzer = CreatorAnalyzer()
    analyzer.update_creator_analytics(creator, self.db)

    logger.info(f"Analytics updated for creator {creator_id}")

    return {"success": True, "creator_id": creator_id}

@celery_app.task(base=DatabaseTask, bind=True)
def update_all_creator_analytics(self):
    """Actualiza analíticas de todos los creadores (tarea periódica)"""
    logger.info("Updating analytics for all creators")

    creators = self.db.query(Creator).all()
    analyzer = CreatorAnalyzer()

    updated = 0
    for creator in creators:
        try:
            analyzer.update_creator_analytics(creator, self.db)
            updated += 1
        except Exception as e:
            logger.error(f"Error updating analytics for creator {creator.id}: {e}")

    logger.info(f"Updated analytics for {updated}/{len(creators)} creators")

    return {"success": True, "total": len(creators), "updated": updated}

@celery_app.task(base=DatabaseTask, bind=True)
def segment_creators_task(self, n_clusters: int = 5):
    """Segmenta todos los creadores"""
    logger.info(f"Segmenting creators with {n_clusters} clusters")

    creators = self.db.query(Creator).all()
    segmentation = CreatorSegmentation()

    segmented = segmentation.segment_creators(creators, n_clusters)
    self.db.commit()

    logger.info(f"Segmented {len(creators)} creators into {len(segmented)} segments")

    return {
        "success": True,
        "total_creators": len(creators),
        "segments": {k: len(v) for k, v in segmented.items()}
    }

# ========== CAMPAIGN TASKS ==========

@celery_app.task(base=DatabaseTask, bind=True)
def execute_campaign_task(self, campaign_id: int):
    """Ejecuta una campaña completa"""
    logger.info(f"Executing campaign {campaign_id}")

    campaign = self.db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        logger.error(f"Campaign {campaign_id} not found")
        return {"success": False, "error": "Campaign not found"}

    # 1. Obtener creadores objetivo
    query = self.db.query(Creator)
    if campaign.target_segment:
        query = query.filter(Creator.segment == campaign.target_segment)

    creators = query.all()
    segmentation = CreatorSegmentation()
    filtered_creators = segmentation.apply_filters(creators, campaign.filters or {})

    logger.info(f"Found {len(filtered_creators)} target creators for campaign")

    # 2. Generar mensajes
    generator = MessageGeneratorService()

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    creator_messages = loop.run_until_complete(
        generator.bulk_generate_messages(filtered_creators, use_ai=True, db=self.db)
    )

    messages = generator.create_message_records(
        creator_messages,
        campaign_id,
        self.db
    )

    logger.info(f"Generated {len(messages)} messages for campaign")

    # 3. Encolar mensajes si auto_send está activado
    if campaign.auto_send:
        sender = TikTokMessageSender()
        queued = sender.queue_messages_for_campaign(campaign_id, self.db)
        logger.info(f"Queued {queued} messages for auto-send")

    campaign.total_targets = len(filtered_creators)
    self.db.commit()

    return {
        "success": True,
        "campaign_id": campaign_id,
        "targets": len(filtered_creators),
        "messages_generated": len(messages)
    }
