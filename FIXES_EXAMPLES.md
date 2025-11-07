# EJEMPLOS DE CORRECCIONES PARA PROBLEMAS CRÍTICOS

## 1. Corregir Credenciales Hardcodeadas en config.py

### ANTES (INCORRECTO):
```python
# /backend/app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+psycopg://user:password@localhost/tiktok_scout"
    RAPIDAPI_KEY: str
```

### DESPUÉS (CORRECTO):
```python
# /backend/app/config.py
from pydantic_settings import BaseSettings
from pydantic import Field, validator

class Settings(BaseSettings):
    # Base de datos - REQUERIDO desde .env
    DATABASE_URL: str = Field(..., description="PostgreSQL connection string")
    
    # RapidAPI - REQUERIDO desde .env
    RAPIDAPI_KEY: str = Field(..., min_length=10, description="RapidAPI key")
    RAPIDAPI_HOST: str = "tiktok-scraper7.p.rapidapi.com"
    
    # OpenAI - OPCIONAL
    OPENAI_API_KEY: Optional[str] = Field(None, description="Required for AI message generation")
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    
    @validator('RAPIDAPI_KEY')
    def validate_api_key(cls, v):
        if not v or len(v) < 10:
            raise ValueError('RAPIDAPI_KEY must be at least 10 characters')
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

### .env File (NO COMMITEAR):
```bash
# /backend/.env
DATABASE_URL=postgresql://user:password@localhost/tiktok_scout
RAPIDAPI_KEY=your_actual_key_here
OPENAI_API_KEY=your_openai_key_here
REDIS_URL=redis://localhost:6379
```

---

## 2. Corregir docker-compose.yml

### ANTES (INCORRECTO):
```yaml
# /backend/docker-compose.yml
services:
  db:
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: tiktok_scout
```

### DESPUÉS (CORRECTO):
```yaml
# /backend/docker-compose.yml
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-tiktok_user}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB:-tiktok_scout}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db/${POSTGRES_DB}
      - REDIS_URL=redis://redis:6379
      - RAPIDAPI_KEY=${RAPIDAPI_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - db
      - redis
    volumes:
      - ./app:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

volumes:
  postgres_data:
```

### .env File para Docker:
```bash
# /backend/.env.docker
POSTGRES_USER=tiktok_user
POSTGRES_PASSWORD=secure_password_here
POSTGRES_DB=tiktok_scout
RAPIDAPI_KEY=your_key_here
OPENAI_API_KEY=your_key_here
```

---

## 3. Corregir Import Faltante en campaign.py

### ANTES (INCORRECTO):
```python
# /backend/app/models/campaign.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, Float
# FALTA: ForeignKey

class CreatorSearch(Base):
    __tablename__ = "creator_searches"
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=True)
    # ^ ERROR: ForeignKey no está importado
```

### DESPUÉS (CORRECTO):
```python
# /backend/app/models/campaign.py
from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean, Text, 
    JSON, Float, ForeignKey  # AGREGADO
)
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

class Campaign(Base):
    __tablename__ = "campaigns"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(Text)
    # ... resto de campos ...
    
    messages = relationship("Message", back_populates="campaign")
    searches = relationship("CreatorSearch", back_populates="campaign")

class CreatorSearch(Base):
    __tablename__ = "creator_searches"
    
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=True)  # AHORA FUNCIONA
    
    search_type = Column(String)
    query = Column(String)
    
    campaign = relationship("Campaign", back_populates="searches")
```

---

## 4. Validar Query Parameters en API

### ANTES (INCORRECTO):
```python
# /backend/app/api/creators.py
@router.get("/")
def get_creators(
    db: Session = Depends(get_db),
    min_followers: Optional[int] = Query(None),  # Sin validación
    min_engagement: Optional[float] = Query(None),  # Sin validación
    limit: int = Query(100)  # Sin límite máximo
):
    query = db.query(Creator)
    
    if min_followers:
        query = query.filter(Creator.followers_count >= min_followers)
```

### DESPUÉS (CORRECTO):
```python
# /backend/app/api/creators.py
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import Field
from typing import Optional

@router.get("/", response_model=List[CreatorResponse])
def get_creators(
    db: Session = Depends(get_db),
    min_followers: Optional[int] = Query(None, ge=0, description="Minimum followers"),
    max_followers: Optional[int] = Query(None, ge=0, description="Maximum followers"),
    min_engagement: Optional[float] = Query(None, ge=0.0, le=100.0, description="Minimum engagement %"),
    min_posting_frequency: Optional[float] = Query(None, ge=0.0, description="Minimum videos/week"),
    min_growth_rate: Optional[float] = Query(None, le=100.0, ge=-100.0, description="Minimum growth %"),
    segment: Optional[str] = Query(None, max_length=50),
    limit: int = Query(100, ge=1, le=1000, description="Results limit"),
    offset: int = Query(0, ge=0, description="Results offset")
):
    """
    Get creators with optional filters
    
    - **min_followers**: Minimum follower count
    - **max_followers**: Maximum follower count
    - **min_engagement**: Minimum engagement rate (0-100%)
    - **segment**: Creator segment filter
    - **limit**: Results per page (1-1000)
    - **offset**: Pagination offset
    """
    query = db.query(Creator)
    
    if min_followers is not None:
        query = query.filter(Creator.followers_count >= min_followers)
    
    if max_followers is not None:
        query = query.filter(Creator.followers_count <= max_followers)
    
    if min_engagement is not None:
        query = query.filter(Creator.engagement_rate >= min_engagement)
    
    if segment:
        query = query.filter(Creator.segment == segment)
    
    creators = query.offset(offset).limit(limit).all()
    return creators
```

---

## 5. Mejorar Exception Handling

### ANTES (INCORRECTO):
```python
# /backend/app/services/tiktok_scraper.py
async def get_user_info(self, username: str) -> Dict:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(...)
            response.raise_for_status()
            return response.json()  # Sin validación
        except Exception as e:  # Demasiado genérico
            logger.error(f"Error: {e}")
            return None
```

### DESPUÉS (CORRECTO):
```python
# /backend/app/services/tiktok_scraper.py
import httpx
import json
from typing import Dict, Optional

async def get_user_info(self, username: str) -> Optional[Dict]:
    """Obtiene información del usuario de TikTok con validación de respuesta"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.base_url}/user/info",
                headers=self.headers,
                params={"unique_id": username}
            )
            response.raise_for_status()
            
            # Validar que la respuesta sea JSON válida
            try:
                data = response.json()
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON response for user {username}: {response.text[:100]}")
                return None
            
            # Validar estructura de la respuesta
            if not isinstance(data, dict) or 'data' not in data:
                logger.error(f"Unexpected response format for user {username}")
                return None
            
            return data
            
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error fetching user {username}: {e.response.status_code}")
        return None
    except httpx.RequestError as e:
        logger.error(f"Request error fetching user {username}: {e}")
        return None
    except Exception as e:
        logger.exception(f"Unexpected error fetching user {username}")
        return None
```

---

## 6. Crear .env.example

### CREAR ARCHIVO:
```bash
# /backend/.env.example
# Copy this file to .env and fill in your actual values
# DO NOT commit the .env file with actual secrets

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================
DATABASE_URL=postgresql://user:password@localhost:5432/tiktok_scout

# ============================================================================
# EXTERNAL APIS
# ============================================================================
# RapidAPI Configuration (REQUIRED)
RAPIDAPI_KEY=your_rapidapi_key_here
RAPIDAPI_HOST=tiktok-scraper7.p.rapidapi.com

# OpenAI Configuration (OPTIONAL - for AI message generation)
OPENAI_API_KEY=sk-your_openai_key_here
OPENAI_MODEL=gpt-4-turbo-preview

# TikTok API (OPTIONAL - for sending messages)
TIKTOK_ACCESS_TOKEN=your_tiktok_token_here
TIKTOK_CLIENT_KEY=your_client_key_here
TIKTOK_CLIENT_SECRET=your_client_secret_here

# ============================================================================
# CACHE & MESSAGE QUEUE
# ============================================================================
REDIS_URL=redis://localhost:6379
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# ============================================================================
# AZURE STORAGE (OPTIONAL)
# ============================================================================
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;...
AZURE_CONTAINER_NAME=tiktok-data

# ============================================================================
# API CONFIGURATION
# ============================================================================
API_V1_STR=/api/v1
PROJECT_NAME=TikTok Creator Scout

# ============================================================================
# CORS CONFIGURATION
# ============================================================================
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:8080"]

# ============================================================================
# RATE LIMITING
# ============================================================================
MAX_MESSAGES_PER_HOUR=50
MAX_MESSAGES_PER_DAY=200

# ============================================================================
# SEARCH CONFIGURATION
# ============================================================================
SEARCH_RESULTS_LIMIT=100
AUTO_SCRAPE_NEW_CREATORS=true
```

---

## 7. Agregar Índices en Base de Datos

### ANTES (INCORRECTO):
```python
# /backend/app/models/creator.py
class Creator(Base):
    __tablename__ = "creators"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    engagement_rate = Column(Float, default=0.0)  # Sin índice
    growth_rate = Column(Float, default=0.0)  # Sin índice
    segment = Column(String)  # Sin índice
```

### DESPUÉS (CORRECTO):
```python
# /backend/app/models/creator.py
class Creator(Base):
    __tablename__ = "creators"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    user_id = Column(String, unique=True, index=True)
    
    # Métricas con índices para búsquedas frecuentes
    followers_count = Column(Integer, default=0, index=True)
    engagement_rate = Column(Float, default=0.0, index=True)
    growth_rate = Column(Float, default=0.0, index=True)
    posting_frequency = Column(Float, default=0.0, index=True)
    
    # Segmentación con índice
    segment = Column(String, index=True)
    potential_score = Column(Float, default=0.0, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

---

## 8. Extraer Event Loop Utility

### ANTES (DUPLICADO):
```python
# /backend/app/tasks.py - REPETIDO 8 VECES
@celery_app.task
def scrape_creator_task(self, username: str):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    # ... resto del código ...

@celery_app.task
def batch_scrape_creators_task(self, usernames: list):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    # ... resto del código ...
```

### DESPUÉS (UTILITY FUNCTION):
```python
# /backend/app/utils/helpers.py
import asyncio
import logging

logger = logging.getLogger(__name__)

def get_event_loop() -> asyncio.AbstractEventLoop:
    """
    Obtiene o crea un event loop para usar en Celery tasks.
    
    Esta función maneja los casos especiales donde el event loop
    puede estar cerrado o no disponible.
    
    Returns:
        asyncio.AbstractEventLoop: El event loop disponible o uno nuevo
    """
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            logger.debug("Event loop is closed, creating a new one")
            raise RuntimeError("Event loop is closed")
        return loop
    except RuntimeError as e:
        logger.debug(f"Event loop not available: {e}, creating new one")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop

# Uso en tasks.py
from .utils.helpers import get_event_loop

@celery_app.task(base=DatabaseTask, bind=True)
def scrape_creator_task(self, username: str):
    logger.info(f"Starting scrape task for creator: {username}")
    
    scraper = TikTokScraperService()
    
    loop = get_event_loop()  # AQUÍ - sin duplicación
    
    creator = loop.run_until_complete(
        scraper.scrape_and_save_creator(username, self.db)
    )
    
    if creator:
        logger.info(f"Successfully scraped creator: {username}")
        return {"success": True, "creator_id": creator.id}
    else:
        logger.error(f"Failed to scrape creator: {username}")
        return {"success": False, "username": username}
```

---

## 9. Mejorar Error Handling en Frontend

### ANTES (INCORRECTO):
```javascript
// /frontend/src/components/Dashboard.js
const fetchData = async () => {
    try {
        setLoading(true);
        const creatorsData = await api.getCreators();
        setCreators(creatorsData);
        
        const segmentsData = await api.getSegmentsSummary();
        setSegments(segmentsData);
    } catch (error) {
        console.error('Error fetching data:', error);
        // Usuario no ve nada - solo log en consola
    } finally {
        setLoading(false);
    }
};
```

### DESPUÉS (CORRECTO):
```javascript
// /frontend/src/components/Dashboard.js
const [error, setError] = useState(null);
const [retrying, setRetrying] = useState(false);

const fetchData = async (showRetry = true) => {
    try {
        setLoading(true);
        setError(null);
        
        const creatorsData = await api.getCreators();
        setCreators(creatorsData);
        
        const segmentsData = await api.getSegmentsSummary();
        setSegments(segmentsData);
    } catch (error) {
        const errorMessage = error?.response?.data?.detail || 
                           error?.message || 
                           'Error loading data. Please try again.';
        
        setError(errorMessage);
        console.error('Error fetching data:', error);
    } finally {
        setLoading(false);
    }
};

const handleRetry = async () => {
    setRetrying(true);
    await fetchData();
    setRetrying(false);
};

// En el render:
{error && (
    <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
        <div className="flex justify-between items-center">
            <div>
                <h3 className="text-red-800 font-semibold">Error</h3>
                <p className="text-red-700">{error}</p>
            </div>
            <button
                onClick={handleRetry}
                disabled={retrying}
                className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50"
            >
                {retrying ? 'Retrying...' : 'Retry'}
            </button>
        </div>
    </div>
)}
```

---

## 10. Validar Inputs en Frontend

### ANTES (INCORRECTO):
```javascript
// /frontend/src/components/FilterPanel.js
<input
    type="text"
    value={filters.search}
    onChange={(e) => handleInputChange('search', e.target.value)}
    placeholder="Nombre o @username"
/>
```

### DESPUÉS (CORRECTO):
```javascript
// /frontend/src/components/FilterPanel.js
<input
    type="text"
    value={filters.search}
    onChange={(e) => {
        const value = e.target.value;
        // Validar longitud
        if (value.length > 50) {
            return;
        }
        // Validar caracteres (alfanuméricos, espacios, guiones)
        if (!/^[a-zA-Z0-9\s\-@._]*$/.test(value)) {
            return;
        }
        handleInputChange('search', value);
    }}
    onBlur={(e) => {
        const value = e.target.value.trim();
        handleInputChange('search', value);
    }}
    maxLength={50}
    placeholder="Nombre o @username"
    aria-label="Search creators by name or username"
    className="pl-10 w-full rounded-lg border border-gray-300 shadow-sm focus:ring-blue-500 focus:border-blue-500"
/>
```

