# backend/app/services/creator_search.py
import httpx
from typing import Dict, List, Optional, Set
from datetime import datetime
import asyncio
from ..config import settings
from ..models.creator import Creator
from ..models.campaign import CreatorSearch
from sqlalchemy.orm import Session
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

class CreatorSearchService:
    """Servicio avanzado para búsqueda y descubrimiento de creadores"""

    def __init__(self):
        self.base_url = f"https://{settings.RAPIDAPI_HOST}"
        self.headers = {
            "X-RapidAPI-Key": settings.RAPIDAPI_KEY,
            "X-RapidAPI-Host": settings.RAPIDAPI_HOST
        }
        self.results_limit = settings.SEARCH_RESULTS_LIMIT

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def search_by_hashtag(self, hashtag: str, count: int = 50) -> List[Dict]:
        """Busca videos por hashtag y extrae creadores únicos"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                # Remover # si está presente
                hashtag = hashtag.lstrip('#')

                logger.info(f"Buscando videos con hashtag: #{hashtag}")
                response = await client.get(
                    f"{self.base_url}/challenge/videos",
                    headers=self.headers,
                    params={
                        "challenge_id": hashtag,
                        "count": count
                    }
                )
                response.raise_for_status()
                data = response.json()

                videos = data.get("data", {}).get("videos", [])
                logger.info(f"Encontrados {len(videos)} videos para #{hashtag}")

                return videos
            except Exception as e:
                logger.error(f"Error buscando hashtag #{hashtag}: {e}")
                return []

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def search_by_keyword(self, keyword: str, count: int = 50) -> List[Dict]:
        """Busca videos por palabra clave"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                logger.info(f"Buscando videos con keyword: {keyword}")
                response = await client.get(
                    f"{self.base_url}/search/videos",
                    headers=self.headers,
                    params={
                        "keywords": keyword,
                        "count": count
                    }
                )
                response.raise_for_status()
                data = response.json()

                videos = data.get("data", {}).get("videos", [])
                logger.info(f"Encontrados {len(videos)} videos para keyword: {keyword}")

                return videos
            except Exception as e:
                logger.error(f"Error buscando keyword '{keyword}': {e}")
                return []

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def search_trending_creators(self, count: int = 50) -> List[Dict]:
        """Obtiene creadores en tendencia"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                logger.info("Buscando creadores en tendencia")
                response = await client.get(
                    f"{self.base_url}/trending/videos",
                    headers=self.headers,
                    params={"count": count}
                )
                response.raise_for_status()
                data = response.json()

                videos = data.get("data", {}).get("videos", [])
                logger.info(f"Encontrados {len(videos)} videos en tendencia")

                return videos
            except Exception as e:
                logger.error(f"Error buscando trending: {e}")
                return []

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def search_by_music(self, music_id: str, count: int = 50) -> List[Dict]:
        """Busca videos que usan una música específica"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                logger.info(f"Buscando videos con música ID: {music_id}")
                response = await client.get(
                    f"{self.base_url}/music/videos",
                    headers=self.headers,
                    params={
                        "music_id": music_id,
                        "count": count
                    }
                )
                response.raise_for_status()
                data = response.json()

                videos = data.get("data", {}).get("videos", [])
                logger.info(f"Encontrados {len(videos)} videos con la música")

                return videos
            except Exception as e:
                logger.error(f"Error buscando música {music_id}: {e}")
                return []

    def extract_creators_from_videos(self, videos: List[Dict]) -> List[Dict]:
        """Extrae información única de creadores de una lista de videos"""
        creators_dict = {}

        for video in videos:
            author = video.get("author", {})
            user_id = author.get("id")

            if user_id and user_id not in creators_dict:
                creators_dict[user_id] = {
                    "user_id": user_id,
                    "username": author.get("uniqueId"),
                    "display_name": author.get("nickname"),
                    "avatar_url": author.get("avatarMedium"),
                    "verified": author.get("verified", False),
                    "followers_count": author.get("stats", {}).get("followerCount", 0),
                    "likes_count": author.get("stats", {}).get("heartCount", 0),
                    "videos_count": author.get("stats", {}).get("videoCount", 0),
                    "signature": author.get("signature", "")
                }

        return list(creators_dict.values())

    def apply_filters(self, creators: List[Dict], filters: Dict) -> List[Dict]:
        """Aplica filtros a la lista de creadores"""
        filtered = creators

        if "min_followers" in filters:
            filtered = [c for c in filtered if c.get("followers_count", 0) >= filters["min_followers"]]

        if "max_followers" in filters:
            filtered = [c for c in filtered if c.get("followers_count", 0) <= filters["max_followers"]]

        if "min_videos" in filters:
            filtered = [c for c in filtered if c.get("videos_count", 0) >= filters["min_videos"]]

        if "verified_only" in filters and filters["verified_only"]:
            filtered = [c for c in filtered if c.get("verified", False)]

        return filtered

    async def discover_creators(
        self,
        search_type: str,
        query: str,
        filters: Optional[Dict] = None,
        db: Optional[Session] = None
    ) -> List[Dict]:
        """
        Descubre creadores basado en diferentes criterios

        Args:
            search_type: 'hashtag', 'keyword', 'trending', 'music'
            query: El término de búsqueda (hashtag, keyword, music_id)
            filters: Filtros opcionales (min_followers, max_followers, etc.)
            db: Sesión de base de datos (opcional, para guardar búsqueda)

        Returns:
            Lista de creadores descubiertos
        """
        videos = []

        # Ejecutar búsqueda según el tipo
        if search_type == "hashtag":
            videos = await self.search_by_hashtag(query)
        elif search_type == "keyword":
            videos = await self.search_by_keyword(query)
        elif search_type == "trending":
            videos = await self.search_trending_creators()
        elif search_type == "music":
            videos = await self.search_by_music(query)
        else:
            logger.error(f"Tipo de búsqueda desconocido: {search_type}")
            return []

        # Extraer creadores únicos
        creators = self.extract_creators_from_videos(videos)
        logger.info(f"Extraídos {len(creators)} creadores únicos")

        # Aplicar filtros si existen
        if filters:
            creators = self.apply_filters(creators, filters)
            logger.info(f"Después de filtros: {len(creators)} creadores")

        # Guardar búsqueda en DB si se proporcionó sesión
        if db:
            search_record = CreatorSearch(
                search_type=search_type,
                query=query,
                filters=filters or {},
                results_count=len(creators),
                last_executed=datetime.utcnow()
            )
            db.add(search_record)
            db.commit()
            logger.info(f"Búsqueda guardada en DB con ID: {search_record.id}")

        return creators

    async def bulk_discover_creators(
        self,
        searches: List[Dict],
        db: Optional[Session] = None
    ) -> Dict[str, List[Dict]]:
        """
        Ejecuta múltiples búsquedas en paralelo

        IMPORTANTE: Para operaciones paralelas, cada búsqueda crea su propia sesión de DB
        para evitar problemas de concurrencia. El parámetro db se ignora en bulk.

        Args:
            searches: Lista de búsquedas [{"type": "hashtag", "query": "fitness", "filters": {...}}, ...]
            db: Sesión de base de datos (ignorado en bulk operations)

        Returns:
            Diccionario con resultados por búsqueda
        """
        from ..database import SessionLocal

        async def discover_with_own_session(search: Dict):
            """Wrapper que crea su propia sesión para cada búsqueda"""
            session = SessionLocal()
            try:
                return await self.discover_creators(
                    search_type=search.get("type"),
                    query=search.get("query"),
                    filters=search.get("filters"),
                    db=session
                )
            finally:
                session.close()

        tasks = []
        for search in searches:
            task = discover_with_own_session(search)
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Organizar resultados
        organized_results = {}
        for i, search in enumerate(searches):
            key = f"{search.get('type')}:{search.get('query')}"
            if isinstance(results[i], list):
                organized_results[key] = results[i]
            else:
                logger.error(f"Error en búsqueda {key}: {results[i]}")
                organized_results[key] = []

        return organized_results

    def deduplicate_creators(self, creator_lists: List[List[Dict]]) -> List[Dict]:
        """Elimina creadores duplicados de múltiples listas"""
        seen_ids: Set[str] = set()
        unique_creators = []

        for creator_list in creator_lists:
            for creator in creator_list:
                user_id = creator.get("user_id")
                if user_id and user_id not in seen_ids:
                    seen_ids.add(user_id)
                    unique_creators.append(creator)

        logger.info(f"Deduplicados: {len(unique_creators)} creadores únicos de múltiples búsquedas")
        return unique_creators
