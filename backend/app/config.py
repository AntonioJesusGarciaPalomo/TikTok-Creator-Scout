from pydantic_settings import BaseSettings
from typing import Optional, List

class Settings(BaseSettings):
    # Database - Actualizado para psycopg3
    DATABASE_URL: str = "postgresql+psycopg://user:password@localhost/tiktok_scout"

    # RapidAPI - CRÍTICO: Aquí debes poner tu API key
    RAPIDAPI_KEY: str  # OBLIGATORIO - Sin default
    RAPIDAPI_HOST: str = "tiktok-scraper7.p.rapidapi.com"

    # OpenAI para generación de mensajes personalizados
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4-turbo-preview"

    # TikTok API para envío de mensajes
    TIKTOK_ACCESS_TOKEN: Optional[str] = None
    TIKTOK_CLIENT_KEY: Optional[str] = None
    TIKTOK_CLIENT_SECRET: Optional[str] = None

    # Rate Limiting para mensajes
    MAX_MESSAGES_PER_HOUR: int = 50
    MAX_MESSAGES_PER_DAY: int = 200

    # Configuración de búsqueda
    SEARCH_RESULTS_LIMIT: int = 100
    AUTO_SCRAPE_NEW_CREATORS: bool = True

    # Redis for caching
    REDIS_URL: str = "redis://localhost:6379"

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # Azure Storage (opcional)
    AZURE_STORAGE_CONNECTION_STRING: Optional[str] = None
    AZURE_CONTAINER_NAME: Optional[str] = "tiktok-data"

    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "TikTok Creator Scout"

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()