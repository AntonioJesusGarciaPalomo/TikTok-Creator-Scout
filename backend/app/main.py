from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter
from .config import settings
from .database import engine, Base
from .api import creators, search, messages, campaigns
from .graphql.schema import schema
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear tablas
Base.metadata.create_all(bind=engine)

# Crear aplicación
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description="API para descubrimiento, análisis y outreach de creadores de TikTok",
    version="2.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GraphQL
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")

# Rutas REST
app.include_router(creators.router, prefix=f"{settings.API_V1_STR}")
app.include_router(search.router, prefix=f"{settings.API_V1_STR}")
app.include_router(messages.router, prefix=f"{settings.API_V1_STR}")
app.include_router(campaigns.router, prefix=f"{settings.API_V1_STR}")

@app.get("/")
def read_root():
    return {
        "message": "TikTok Creator Scout API v2.0",
        "docs": "/docs",
        "graphql": "/graphql",
        "features": [
            "Creator Discovery & Search",
            "AI-Powered Message Generation",
            "Campaign Management",
            "Automated Outreach",
            "Analytics & Segmentation"
        ]
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "version": "2.0.0"
    }

@app.on_event("startup")
async def startup_event():
    logger.info("Starting TikTok Creator Scout API v2.0...")
    logger.info("New features: Creator Search, Message Generation, Campaigns")