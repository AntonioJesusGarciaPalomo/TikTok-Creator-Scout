# Backend - TikTok Creator Scout

API REST y GraphQL construida con FastAPI para analizar y segmentar creadores de TikTok usando machine learning e inteligencia artificial.

## 📋 Tabla de Contenidos

- [Arquitectura](#-arquitectura)
- [Estructura de Archivos](#-estructura-de-archivos)
- [Instalación](#-instalación)
- [Configuración](#-configuración)
- [Modelos de Datos](#-modelos-de-datos)
- [Servicios](#-servicios)
- [API Endpoints](#-api-endpoints)
- [GraphQL Schema](#-graphql-schema)
- [Testing](#-testing)
- [Deployment](#-deployment)

---

## 🏗️ Arquitectura

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│                 │     │                  │     │                 │
│  FastAPI App    │────▶│  PostgreSQL DB   │     │  Redis Cache    │
│                 │     │                  │     │                 │
└────────┬────────┘     └──────────────────┘     └─────────────────┘
         │                                                  ▲
         │                                                  │
         ▼                                                  │
┌─────────────────┐     ┌──────────────────┐              │
│                 │     │                  │              │
│  GraphQL API    │     │  TikTok Scraper  │──────────────┘
│                 │     │                  │
└─────────────────┘     └────────┬─────────┘
                                 │
                                 ▼
                        ┌──────────────────┐
                        │                  │
                        │  ML Services     │
                        │  - Clustering    │
                        │  - Analysis      │
                        └──────────────────┘
```

---

## 📁 Estructura de Archivos

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Punto de entrada de FastAPI
│   ├── config.py               # Configuración y variables de entorno
│   ├── database.py             # Configuración de la base de datos
│   │
│   ├── models/                 # Modelos de SQLAlchemy
│   │   ├── __init__.py
│   │   ├── creator.py          # Modelo de creadores
│   │   └── metrics.py          # Modelo de métricas
│   │
│   ├── schemas/                # Esquemas de Pydantic
│   │   ├── __init__.py
│   │   ├── creator.py          # DTOs de creadores
│   │   └── metrics.py          # DTOs de métricas
│   │
│   ├── services/               # Lógica de negocio
│   │   ├── __init__.py
│   │   ├── tiktok_scraper.py   # Servicio de scraping
│   │   ├── analyzer.py         # Análisis de datos
│   │   └── segmentation.py     # Segmentación con ML
│   │
│   ├── api/                    # Endpoints REST
│   │   ├── __init__.py
│   │   ├── creators.py         # Rutas de creadores
│   │   └── analytics.py        # Rutas de análisis
│   │
│   ├── graphql/                # GraphQL
│   │   ├── __init__.py
│   │   ├── schema.py           # Schema GraphQL
│   │   └── resolvers.py        # Resolvers
│   │
│   └── utils/                  # Utilidades
│       ├── __init__.py
│       └── helpers.py
│
├── tests/                      # Tests
│   ├── __init__.py
│   ├── test_api.py
│   └── test_services.py
│
├── alembic/                    # Migraciones de DB
│   └── versions/
│
├── requirements.txt            # Dependencias Python
├── .env                        # Variables de entorno
├── .env.example               # Ejemplo de variables
├── Dockerfile                 # Imagen Docker
├── docker-compose.yml         # Orquestación
└── README.md                  # Este archivo
```

---

## 🚀 Instalación

### Prerequisitos

- Python 3.9 o superior
- PostgreSQL 14+
- Redis 6+
- pip y virtualenv

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/tiktok-creator-scout.git
cd tiktok-creator-scout/backend
```

### 2. Crear entorno virtual

```bash
# Linux/Mac
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar base de datos

```bash
# Crear usuario y base de datos
sudo -u postgres psql

postgres=# CREATE USER tiktok_user WITH PASSWORD 'tiktok_pass';
postgres=# CREATE DATABASE tiktok_scout OWNER tiktok_user;
postgres=# GRANT ALL PRIVILEGES ON DATABASE tiktok_scout TO tiktok_user;
postgres=# \q
```

### 5. Configurar variables de entorno

```bash
cp .env.example .env
# Editar .env con tus valores
```

### 6. Ejecutar migraciones

```bash
# Inicializar Alembic (solo la primera vez)
alembic init alembic

# Crear primera migración
alembic revision --autogenerate -m "Initial migration"

# Aplicar migraciones
alembic upgrade head
```

### 7. Iniciar el servidor

```bash
# Desarrollo
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Producción
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

---

## ⚙️ Configuración

### Variables de Entorno (.env)

```env
# Base de datos
DATABASE_URL=postgresql://tiktok_user:tiktok_pass@localhost/tiktok_scout

# Redis
REDIS_URL=redis://localhost:6379

# RapidAPI (OBLIGATORIO)
RAPIDAPI_KEY=tu_api_key_aqui
RAPIDAPI_HOST=tiktok-scraper7.p.rapidapi.com

# Azure Storage (Opcional)
AZURE_STORAGE_CONNECTION_STRING=
AZURE_CONTAINER_NAME=tiktok-data

# OpenAI (Opcional - para Semantic Kernel)
OPENAI_API_KEY=

# Configuración API
API_V1_STR=/api/v1
PROJECT_NAME=TikTok Creator Scout

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000"]

# Seguridad
SECRET_KEY=tu-secret-key-super-segura
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Configuración de Logging

```python
# app/config.py
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["default"],
    },
}
```

---

## 📊 Modelos de Datos

### Creator Model

```python
class Creator(Base):
    __tablename__ = "creators"
    
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, index=True)
    user_id = Column(String, unique=True)
    display_name = Column(String)
    avatar_url = Column(String)
    bio = Column(String)
    verified = Column(Boolean, default=False)
    
    # Métricas básicas
    followers_count = Column(Integer, default=0)
    following_count = Column(Integer, default=0)
    likes_count = Column(Integer, default=0)
    videos_count = Column(Integer, default=0)
    
    # Métricas calculadas
    engagement_rate = Column(Float, default=0.0)
    avg_likes_per_video = Column(Float, default=0.0)
    avg_comments_per_video = Column(Float, default=0.0)
    growth_rate = Column(Float, default=0.0)
    posting_frequency = Column(Float, default=0.0)
    
    # Segmentación
    segment = Column(String)
    potential_score = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_scraped = Column(DateTime)
```

### Metrics Model

```python
class CreatorMetrics(Base):
    __tablename__ = "creator_metrics"
    
    id = Column(Integer, primary_key=True)
    creator_id = Column(Integer, ForeignKey("creators.id"))
    
    # Snapshot de métricas
    followers_count = Column(Integer)
    likes_count = Column(Integer)
    videos_count = Column(Integer)
    
    # Tasas de crecimiento
    daily_growth = Column(Float)
    weekly_growth = Column(Float)
    monthly_growth = Column(Float)
    
    timestamp = Column(DateTime, default=datetime.utcnow)
```

---

## 🔧 Servicios

### TikTok Scraper Service

```python
# Funciones principales
- get_user_info(username: str) -> Dict
- get_user_videos(user_id: str, count: int) -> List[Dict]
- get_video_comments(video_id: str) -> List[Dict]
- calculate_posting_frequency(videos: List[Dict]) -> float
- calculate_engagement_rate(creator_data: Dict, videos: List[Dict]) -> float
- scrape_and_save_creator(username: str, db: Session) -> Creator
```

### Analyzer Service

```python
# Funciones principales
- calculate_growth_rate(creator: Creator, db: Session) -> Dict[str, float]
- calculate_potential_score(creator: Creator, growth_rates: Dict[str, float]) -> float
- update_creator_analytics(creator: Creator, db: Session) -> None
```

### Segmentation Service

```python
# Funciones principales
- prepare_features(creators: List[Creator]) -> np.ndarray
- segment_creators(creators: List[Creator], n_clusters: int = 5) -> Dict[int, List[Creator]]
- analyze_segment_with_ai(segment: List[Creator]) -> Dict
- apply_filters(creators: List[Creator], filters: Dict) -> List[Creator]
```

---

## 🔌 API Endpoints

### REST API

#### Creadores

```http
# Listar creadores con filtros
GET /api/v1/creators?min_followers=1000&min_engagement=2.5&segment=Rising Stars

# Obtener un creador específico
GET /api/v1/creators/{username}

# Scrapear nuevo creador
POST /api/v1/creators/scrape
{
  "username": "creador_username"
}

# Scrapear múltiples creadores
POST /api/v1/creators/batch-scrape
{
  "usernames": ["username1", "username2", "username3"]
}

# Resumen de segmentos
GET /api/v1/creators/segments/summary
```

#### Analytics

```http
# Análisis de tendencias
GET /api/v1/analytics/trends?period=7d

# Predicciones de crecimiento
GET /api/v1/analytics/predictions/{username}

# Exportar datos
GET /api/v1/analytics/export?format=csv
```

---

## 🔍 GraphQL Schema

### Queries

```graphql
type Query {
  # Obtener creadores con filtros
  creators(
    filters: CreatorFilter
    limit: Int = 100
    offset: Int = 0
  ): [Creator!]!
  
  # Obtener un creador específico
  creator(username: String!): Creator
  
  # Análisis de segmentos
  segmentAnalysis: [SegmentAnalysis!]!
}

input CreatorFilter {
  minFollowers: Int
  maxFollowers: Int
  minEngagement: Float
  minPostingFrequency: Float
  minGrowthRate: Float
  segments: [String!]
}
```

### Mutations

```graphql
type Mutation {
  # Scrapear un creador
  scrapeCreator(username: String!): Creator!
  
  # Scrapear múltiples creadores
  batchScrape(usernames: [String!]!): [Creator!]!
  
  # Actualizar segmentos
  updateSegments: Boolean!
}
```

### Tipos

```graphql
type Creator {
  id: Int!
  username: String!
  displayName: String!
  avatarUrl: String
  bio: String
  verified: Boolean!
  
  # Métricas
  followersCount: Int!
  likesCount: Int!
  videosCount: Int!
  engagementRate: Float!
  growthRate: Float!
  postingFrequency: Float!
  
  # Análisis
  segment: String
  potentialScore: Float!
  
  # Timestamps
  createdAt: DateTime!
  updatedAt: DateTime!
  lastScraped: DateTime
}
```

---

## 🧪 Testing

### Ejecutar tests

```bash
# Todos los tests
pytest

# Con coverage
pytest --cov=app tests/

# Tests específicos
pytest tests/test_api.py::test_create_creator
```

### Ejemplo de test

```python
# tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_creators():
    response = client.get("/api/v1/creators")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_scrape_creator():
    response = client.post(
        "/api/v1/creators/scrape",
        json={"username": "testuser"}
    )
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"
```

---

## 🚀 Deployment

### Docker

```bash
# Construir imagen
docker build -t tiktok-scout-backend .

# Ejecutar contenedor
docker run -d \
  --name tiktok-backend \
  -p 8000:8000 \
  --env-file .env \
  tiktok-scout-backend
```

### Docker Compose

```bash
# Iniciar todos los servicios
docker-compose up -d

# Ver logs
docker-compose logs -f backend

# Detener servicios
docker-compose down
```

### Azure Container Instances

```bash
# Construir y push a ACR
az acr build --registry myregistry --image tiktok-backend:latest .

# Desplegar en ACI
az container create \
  --resource-group myResourceGroup \
  --name tiktok-backend \
  --image myregistry.azurecr.io/tiktok-backend:latest \
  --dns-name-label tiktok-api \
  --ports 8000
```

---

## 🔧 Mantenimiento

### Actualizar dependencias

```bash
# Actualizar requirements.txt
pip freeze > requirements.txt

# Actualizar una dependencia específica
pip install --upgrade fastapi
```

### Limpiar base de datos

```python
# scripts/clean_db.py
from app.database import SessionLocal, engine
from app.models import Base

# Eliminar todas las tablas
Base.metadata.drop_all(bind=engine)

# Recrear tablas
Base.metadata.create_all(bind=engine)
```

### Backup de base de datos

```bash
# Crear backup
pg_dump -U tiktok_user -h localhost tiktok_scout > backup_$(date +%Y%m%d).sql

# Restaurar backup
psql -U tiktok_user -h localhost tiktok_scout < backup_20240115.sql
```

---

## 📈 Monitoreo

### Logs

```python
# Configurar logging
import logging
from app.config import LOGGING_CONFIG

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

# Usar en tu código
logger.info(f"Scraping creator: {username}")
logger.error(f"Error scraping: {e}")
```

### Health Check

```python
# app/api/health.py
@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    try:
        # Verificar DB
        db.execute("SELECT 1")
        
        # Verificar Redis
        redis_client.ping()
        
        return {
            "status": "healthy",
            "database": "connected",
            "redis": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
```

---

## 🆘 Solución de Problemas

### Error: "Connection refused" PostgreSQL

```bash
# Verificar que PostgreSQL esté corriendo
sudo service postgresql status
sudo service postgresql start

# Verificar conexión
psql -U tiktok_user -h localhost -d tiktok_scout
```

### Error: "Module not found"

```bash
# Asegurarse de estar en el entorno virtual
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Reinstalar dependencias
pip install -r requirements.txt
```

### Error: Rate limit en RapidAPI

Implementar retry con backoff exponencial:

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def fetch_with_retry(self, url, params):
    # Tu código aquí
    pass
```

---

## 📚 Recursos Adicionales

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Strawberry GraphQL](https://strawberry.rocks/)
- [TikTok Scraper API](https://rapidapi.com/maknimarc-pWFsrWbJJ9P/api/tiktok-scraper7)

---

<p align="center">
  Backend desarrollado con ❤️ usando las mejores prácticas de Python
</p>