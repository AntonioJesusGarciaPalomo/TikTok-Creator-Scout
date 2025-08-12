from pydantic_settings import BaseSettings
from typing import Optional, List

class Settings(BaseSettings):
    # Database - Actualizado para psycopg3
    DATABASE_URL: str = "postgresql+psycopg://user:password@localhost/tiktok_scout"
    
    # RapidAPI - CRÍTICO: Aquí debes poner tu API key
    RAPIDAPI_KEY: str  # OBLIGATORIO - Sin default
    RAPIDAPI_HOST: str = "tiktok-scraper7.p.rapidapi.com"
    
    # OpenAI para Semantic Kernel (opcional)
    OPENAI_API_KEY: Optional[str] = None
    
    # Redis for caching
    REDIS_URL: str = "redis://localhost:6379"
    
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