from typing import List, Dict
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import pandas as pd
from sqlalchemy.orm import Session
from ..models.creator import Creator
import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
import settings
import logging

logger = logging.getLogger(__name__)

class CreatorSegmentation:
    def __init__(self):
        self.scaler = StandardScaler()
        self.segments = {
            0: "Rising Stars",           # Alto potencial, crecimiento rápido
            1: "Consistent Performers",  # Buenos números, estables
            2: "High Engagement",        # Alta interacción pero menos seguidores
            3: "Growth Needed",          # Necesitan estrategia de crecimiento
            4: "Emerging Talent"         # Nuevos con potencial
        }
        
        # Inicializar Semantic Kernel solo si hay API key
        if settings.OPENAI_API_KEY:
            self.kernel = sk.Kernel()
            self.kernel.add_text_completion_service(
                "openai-chat",
                OpenAIChatCompletion(
                    "gpt-4",
                    api_key=settings.OPENAI_API_KEY  # FIX: Usar variable de entorno
                )
            )
        else:
            self.kernel = None
            logger.warning("OpenAI API key not configured, AI analysis will be disabled")
    
    def prepare_features(self, creators: List[Creator]) -> np.ndarray:
        """Prepara las características para clustering"""
        features = []
        for creator in creators:
            features.append([
                creator.followers_count,
                creator.engagement_rate,
                creator.posting_frequency,
                creator.growth_rate,
                creator.avg_likes_per_video,
                creator.potential_score
            ])
        
        return np.array(features)
    
    def segment_creators(self, creators: List[Creator], n_clusters: int = 5) -> Dict[int, List[Creator]]:
        """Segmenta creadores usando K-means clustering"""
        if len(creators) < n_clusters:
            logger.warning(f"Not enough creators ({len(creators)}) for {n_clusters} clusters")
            n_clusters = max(2, len(creators))
        
        # Preparar datos
        features = self.prepare_features(creators)
        features_scaled = self.scaler.fit_transform(features)
        
        # Clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        clusters = kmeans.fit_predict(features_scaled)
        
        # Asignar segmentos
        segmented = {}
        for i, creator in enumerate(creators):
            cluster = clusters[i]
            creator.segment = self.segments.get(cluster, f"Segment {cluster}")
            
            if cluster not in segmented:
                segmented[cluster] = []
            segmented[cluster].append(creator)
        
        return segmented
    
    async def analyze_segment_with_ai(self, segment: List[Creator]) -> Dict:
        """Usa IA para analizar un segmento y generar insights"""
        # Preparar datos del segmento
        avg_followers = np.mean([c.followers_count for c in segment])
        avg_engagement = np.mean([c.engagement_rate for c in segment])
        avg_growth = np.mean([c.growth_rate for c in segment])

        # Si no hay kernel configurado, devolver análisis básico
        if not self.kernel:
            return {
                "segment_analysis": "AI analysis not available (OpenAI API key not configured)",
                "metrics": {
                    "avg_followers": avg_followers,
                    "avg_engagement": avg_engagement,
                    "avg_growth": avg_growth
                }
            }
        
        prompt = f"""
        Analiza este segmento de creadores de TikTok:
        - Número de creadores: {len(segment)}
        - Promedio de seguidores: {avg_followers:.0f}
        - Tasa de engagement promedio: {avg_engagement:.2f}%
        - Crecimiento semanal promedio: {avg_growth:.2f}%
        
        Proporciona:
        1. Características principales del segmento
        2. Estrategias de crecimiento recomendadas
        3. Oportunidades de monetización
        """
        
        skill = self.kernel.skills.get_function("text", "complete")
        result = await skill.invoke_async(prompt)
        
        return {
            "segment_analysis": result,
            "metrics": {
                "avg_followers": avg_followers,
                "avg_engagement": avg_engagement,
                "avg_growth": avg_growth
            }
        }
    
    def apply_filters(self, creators: List[Creator], filters: Dict) -> List[Creator]:
        """Aplica filtros a la lista de creadores"""
        filtered = creators
        
        if "min_followers" in filters:
            filtered = [c for c in filtered if c.followers_count >= filters["min_followers"]]
        
        if "max_followers" in filters:
            filtered = [c for c in filtered if c.followers_count <= filters["max_followers"]]
        
        if "min_engagement" in filters:
            filtered = [c for c in filtered if c.engagement_rate >= filters["min_engagement"]]
        
        if "min_posting_frequency" in filters:
            filtered = [c for c in filtered if c.posting_frequency >= filters["min_posting_frequency"]]
        
        if "min_growth_rate" in filters:
            filtered = [c for c in filtered if c.growth_rate >= filters["min_growth_rate"]]
        
        if "segments" in filters:
            filtered = [c for c in filtered if c.segment in filters["segments"]]
        
        return filtered