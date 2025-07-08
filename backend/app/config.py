from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost/tiktok_scout"
    
    # RapidAPI
    RAPIDAPI_KEY: str
    RAPIDAPI_HOST: str = "tiktok-scraper7.p.rapidapi.com"
    
    # Redis for caching
    REDIS_URL: str = "redis://localhost:6379"
    
    # Azure Storage (opcional)
    AZURE_STORAGE_CONNECTION_STRING: Optional[str] = None
    AZURE_CONTAINER_NAME: Optional[str] = "tiktok-data"
    
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "TikTok Creator Scout"
    
    # CORS
    BACKEND_CORS_ORIGINS: list = ["http://localhost:3000"]
    
    class Config:
        env_file = ".env"

settings = Settings()