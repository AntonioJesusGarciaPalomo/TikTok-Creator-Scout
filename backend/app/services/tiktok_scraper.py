# backend/app/services/tiktok_scraper.py
import httpx
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import asyncio
from ..config import settings
from ..models.creator import Creator
from ..models.metrics import CreatorMetrics, Video
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)

class TikTokScraperService:
    def __init__(self):
        self.base_url = f"https://{settings.RAPIDAPI_HOST}"
        self.headers = {
            "X-RapidAPI-Key": settings.RAPIDAPI_KEY,
            "X-RapidAPI-Host": settings.RAPIDAPI_HOST
        }
        
    async def get_user_info(self, username: str) -> Dict:
        """Obtiene información del usuario de TikTok"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/user/info",
                    headers=self.headers,
                    params={"unique_id": username}
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.error(f"Error fetching user info for {username}: {e}")
                return None
    
    async def get_user_videos(self, user_id: str, count: int = 30) -> List[Dict]:
        """Obtiene los videos de un usuario"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/user/videos",
                    headers=self.headers,
                    params={
                        "user_id": user_id,
                        "count": count
                    }
                )
                response.raise_for_status()
                return response.json().get("data", {}).get("videos", [])
            except Exception as e:
                logger.error(f"Error fetching videos for user {user_id}: {e}")
                return []
    
    async def get_video_comments(self, video_id: str) -> List[Dict]:
        """Obtiene los comentarios de un video"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/comment/list",
                    headers=self.headers,
                    params={"url": f"https://www.tiktok.com/@user/video/{video_id}"}
                )
                response.raise_for_status()
                return response.json().get("data", {}).get("comments", [])
            except Exception as e:
                logger.error(f"Error fetching comments for video {video_id}: {e}")
                return []
    
    def calculate_posting_frequency(self, videos: List[Dict]) -> float:
        """Calcula la frecuencia de publicación (videos por semana)"""
        if len(videos) < 2:
            return 0.0
        
        # Ordenar videos por fecha
        sorted_videos = sorted(videos, key=lambda x: x.get("create_time", 0))
        
        # Calcular días entre primer y último video
        first_date = datetime.fromtimestamp(sorted_videos[0].get("create_time", 0))
        last_date = datetime.fromtimestamp(sorted_videos[-1].get("create_time", 0))
        
        days_diff = (last_date - first_date).days
        if days_diff == 0:
            return 0.0
        
        # Videos por semana
        return (len(videos) / days_diff) * 7
    
    def calculate_engagement_rate(self, creator_data: Dict, videos: List[Dict]) -> float:
        """Calcula la tasa de engagement"""
        if not videos or creator_data.get("stats", {}).get("followerCount", 0) == 0:
            return 0.0
        
        total_engagement = sum(
            video.get("stats", {}).get("diggCount", 0) + 
            video.get("stats", {}).get("commentCount", 0) + 
            video.get("stats", {}).get("shareCount", 0)
            for video in videos
        )
        
        followers = creator_data.get("stats", {}).get("followerCount", 1)
        avg_engagement = total_engagement / len(videos)
        
        return (avg_engagement / followers) * 100
    
    async def scrape_and_save_creator(self, username: str, db: Session) -> Optional[Creator]:
        """Scrapea y guarda información de un creador"""
        # Obtener información del usuario
        user_data = await self.get_user_info(username)
        if not user_data:
            return None
        
        user_info = user_data.get("data", {}).get("user", {})
        stats = user_info.get("stats", {})
        
        # Obtener videos del usuario
        user_id = user_info.get("id")
        videos = await self.get_user_videos(user_id)
        
        # Calcular métricas
        posting_frequency = self.calculate_posting_frequency(videos)
        engagement_rate = self.calculate_engagement_rate(user_info, videos)
        
        # Calcular promedios
        avg_likes = sum(v.get("stats", {}).get("diggCount", 0) for v in videos) / len(videos) if videos else 0
        avg_comments = sum(v.get("stats", {}).get("commentCount", 0) for v in videos) / len(videos) if videos else 0
        
        # Crear o actualizar creador
        creator = db.query(Creator).filter(Creator.username == username).first()
        if not creator:
            creator = Creator(
                username=username,
                user_id=user_id,
                display_name=user_info.get("nickname"),
                avatar_url=user_info.get("avatarMedium"),
                bio=user_info.get("signature"),
                verified=user_info.get("verified", False)
            )
            db.add(creator)
        
        # Actualizar métricas
        creator.followers_count = stats.get("followerCount", 0)
        creator.following_count = stats.get("followingCount", 0)
        creator.likes_count = stats.get("heartCount", 0)
        creator.videos_count = stats.get("videoCount", 0)
        creator.engagement_rate = engagement_rate
        creator.avg_likes_per_video = avg_likes
        creator.avg_comments_per_video = avg_comments
        creator.posting_frequency = posting_frequency
        creator.last_scraped = datetime.utcnow()
        
        # Guardar videos
        for video_data in videos[:10]:  # Guardar últimos 10 videos
            video_id = video_data.get("id")
            video = db.query(Video).filter(Video.video_id == video_id).first()
            if not video:
                video = Video(
                    video_id=video_id,
                    creator_id=creator.id,
                    description=video_data.get("desc"),
                    duration=video_data.get("duration"),
                    cover_url=video_data.get("cover"),
                    likes_count=video_data.get("stats", {}).get("diggCount", 0),
                    comments_count=video_data.get("stats", {}).get("commentCount", 0),
                    shares_count=video_data.get("stats", {}).get("shareCount", 0),
                    views_count=video_data.get("stats", {}).get("playCount", 0),
                    created_at=datetime.fromtimestamp(video_data.get("createTime", 0))
                )
                db.add(video)
        
        # Guardar snapshot de métricas
        metrics = CreatorMetrics(
            creator_id=creator.id,
            followers_count=creator.followers_count,
            likes_count=creator.likes_count,
            videos_count=creator.videos_count
        )
        db.add(metrics)
        
        db.commit()
        db.refresh(creator)
        
        return creator
    
    async def batch_scrape_creators(self, usernames: List[str], db: Session):
        """Scrapea múltiples creadores de forma concurrente"""
        tasks = []
        for username in usernames:
            task = self.scrape_and_save_creator(username, db)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        successful = [r for r in results if isinstance(r, Creator)]
        failed = [usernames[i] for i, r in enumerate(results) if not isinstance(r, Creator)]
        
        logger.info(f"Scraped {len(successful)} creators successfully")
        if failed:
            logger.warning(f"Failed to scrape: {failed}")
        
        return successful