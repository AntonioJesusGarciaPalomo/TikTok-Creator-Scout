from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..services.creator_search import CreatorSearchService
from ..services.tiktok_scraper import TikTokScraperService
from ..schemas.campaign import (
    ExecuteSearchRequest,
    BulkSearchRequest,
    SearchResultsResponse,
    BulkSearchResponse,
    CreatorSearchResponse,
    CreatorSearchCreate
)
from ..models.campaign import CreatorSearch
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/search", tags=["search"])

@router.post("/execute", response_model=SearchResultsResponse)
async def execute_search(
    request: ExecuteSearchRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Ejecuta una búsqueda de creadores

    - **search_type**: hashtag, keyword, trending, music
    - **query**: término de búsqueda
    - **filters**: filtros opcionales (min_followers, max_followers, etc.)
    - **auto_scrape**: scrape automático de creadores descubiertos
    - **save_search**: guardar búsqueda en base de datos
    """
    search_service = CreatorSearchService()

    try:
        # Ejecutar búsqueda
        creators = await search_service.discover_creators(
            search_type=request.search_type,
            query=request.query,
            filters=request.filters,
            db=db if request.save_search else None
        )

        # Si auto_scrape está activado, scrape en background
        if request.auto_scrape and creators:
            scraper = TikTokScraperService()
            usernames = [c["username"] for c in creators if c.get("username")]

            # Programar scraping en background
            background_tasks.add_task(
                scraper.batch_scrape_creators,
                usernames[:50],  # Límite de 50 por tanda
                db
            )
            logger.info(f"Scheduled background scraping for {len(usernames[:50])} creators")

        return SearchResultsResponse(
            search_type=request.search_type,
            query=request.query,
            total_found=len(creators),
            creators=creators,
            filters_applied=request.filters or {}
        )

    except Exception as e:
        logger.error(f"Error executing search: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/bulk", response_model=BulkSearchResponse)
async def bulk_search(
    request: BulkSearchRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Ejecuta múltiples búsquedas en paralelo

    Ejemplo de payload:
    ```json
    {
        "searches": [
            {"type": "hashtag", "query": "fitness", "filters": {"min_followers": 10000}},
            {"type": "keyword", "query": "recetas saludables", "filters": {"max_followers": 500000}}
        ],
        "auto_scrape": true,
        "deduplicate": true
    }
    ```
    """
    search_service = CreatorSearchService()

    try:
        # Ejecutar búsquedas en paralelo
        results = await search_service.bulk_discover_creators(request.searches, db)

        # Procesar resultados
        results_by_search = {}
        all_creators = []

        for key, creators in results.items():
            search_parts = key.split(":", 1)
            search_type = search_parts[0]
            query = search_parts[1] if len(search_parts) > 1 else ""

            results_by_search[key] = SearchResultsResponse(
                search_type=search_type,
                query=query,
                total_found=len(creators),
                creators=creators,
                filters_applied={}
            )

            all_creators.append(creators)

        # Deduplicar si se solicita
        if request.deduplicate:
            unique_creators = search_service.deduplicate_creators(all_creators)
        else:
            unique_creators = [c for sublist in all_creators for c in sublist]

        # Auto-scrape en background
        if request.auto_scrape and unique_creators:
            scraper = TikTokScraperService()
            usernames = [c["username"] for c in unique_creators if c.get("username")]

            background_tasks.add_task(
                scraper.batch_scrape_creators,
                usernames[:100],  # Límite de 100
                db
            )
            logger.info(f"Scheduled background scraping for {len(usernames[:100])} creators")

        return BulkSearchResponse(
            total_searches=len(request.searches),
            total_creators_found=sum(len(c) for c in all_creators),
            unique_creators=len(unique_creators),
            results_by_search=results_by_search
        )

    except Exception as e:
        logger.error(f"Error executing bulk search: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history", response_model=List[CreatorSearchResponse])
def get_search_history(
    limit: int = 50,
    campaign_id: int = None,
    db: Session = Depends(get_db)
):
    """Obtiene el historial de búsquedas"""
    query = db.query(CreatorSearch)

    if campaign_id:
        query = query.filter(CreatorSearch.campaign_id == campaign_id)

    searches = query.order_by(CreatorSearch.created_at.desc()).limit(limit).all()
    return searches

@router.get("/{search_id}", response_model=CreatorSearchResponse)
def get_search(search_id: int, db: Session = Depends(get_db)):
    """Obtiene una búsqueda específica"""
    search = db.query(CreatorSearch).filter(CreatorSearch.id == search_id).first()

    if not search:
        raise HTTPException(status_code=404, detail="Search not found")

    return search

@router.delete("/{search_id}")
def delete_search(search_id: int, db: Session = Depends(get_db)):
    """Elimina una búsqueda del historial"""
    search = db.query(CreatorSearch).filter(CreatorSearch.id == search_id).first()

    if not search:
        raise HTTPException(status_code=404, detail="Search not found")

    db.delete(search)
    db.commit()

    return {"message": "Search deleted successfully"}
