from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter
from .config import settings
from .database import engine, Base
from .api import creators
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
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
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

@app.get("/")
def read_root():
    return {
        "message": "TikTok Creator Scout API",
        "docs": "/docs",
        "graphql": "/graphql"
    }

@app.on_event("startup")
async def startup_event():
    logger.info("Starting TikTok Creator Scout API...")