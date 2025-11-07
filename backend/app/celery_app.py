# backend/app/celery_app.py
from celery import Celery
from .config import settings

celery_app = Celery(
    "tiktok_creator_scout",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=['app.tasks']
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutos
    task_soft_time_limit=25 * 60,  # 25 minutos
)

# Configuración de tareas periódicas (opcional)
celery_app.conf.beat_schedule = {
    'process-queued-messages': {
        'task': 'app.tasks.process_queued_messages',
        'schedule': 300.0,  # Cada 5 minutos
    },
    'update-creator-analytics': {
        'task': 'app.tasks.update_all_creator_analytics',
        'schedule': 3600.0,  # Cada hora
    },
}

if __name__ == '__main__':
    celery_app.start()
