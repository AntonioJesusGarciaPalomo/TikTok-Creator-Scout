import numpy as np
from typing import List, Dict, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import pandas as pd
from ..models.creator import Creator
from ..models.metrics import CreatorMetrics
import logging

logger = logging.getLogger(__name__)

class CreatorAnalyzer:
    def __init__(self):
        self.scaler = StandardScaler()
        
    def calculate_growth_rate(self, creator: Creator, db: Session) -> Dict[str, float]:
        """Calcula las tasas de crecimiento basándose en métricas históricas"""
        # Obtener métricas de los últimos 30 días
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        metrics = db.query(CreatorMetrics).filter(
            CreatorMetrics.creator_id == creator.id,
            CreatorMetrics.timestamp >= thirty_days_ago
        ).order_by(CreatorMetrics.timestamp).all()
        
        if len(metrics) < 2:
            return {"daily": 0.0, "weekly": 0.0, "monthly": 0.0}
        
        # Calcular crecimiento
        first_metric = metrics[0]
        last_metric = metrics[-1]
        days_diff = (last_metric.timestamp - first_metric.timestamp).days
        
        if days_diff == 0 or first_metric.followers_count == 0:
            return {"daily": 0.0, "weekly": 0.0, "monthly": 0.0}
        
        total_growth = (last_metric.followers_count - first_metric.followers_count) / first_metric.followers_count
        daily_growth = total_growth / days_diff
        
        return {
            "daily": daily_growth * 100,
            "weekly": daily_growth * 7 * 100,
            "monthly": daily_growth * 30 * 100
        }
    
    def calculate_potential_score(self, creator: Creator, growth_rates: Dict[str, float]) -> float:
        """Calcula un score de potencial basado en múltiples factores"""

        avg_engagement_value = 0
        if creator.followers_count > 0:
            avg_engagement_value = min((creator.avg_likes_per_video + creator.avg_comments_per_video) / creator.followers_count * 100, 1)

        # Factores para el score
        factors = {
            "engagement_rate": creator.engagement_rate,
            "posting_frequency": min(creator.posting_frequency / 7, 1),  # Normalizado a 0-1
            "growth_rate": min(growth_rates["weekly"] / 10, 1),  # 10% semanal = 1.0
            "avg_engagement": avg_engagement_value,
            "consistency": 1.0 if creator.posting_frequency >= 3 else creator.posting_frequency / 3
        }
        
        # Pesos para cada factor
        weights = {
            "engagement_rate": 0.3,
            "posting_frequency": 0.2,
            "growth_rate": 0.25,
            "avg_engagement": 0.15,
            "consistency": 0.1
        }
        
        # Calcular score ponderado
        score = sum(factors[key] * weights[key] for key in factors)
        return min(score * 100, 100)  # Score de 0-100
    
    def update_creator_analytics(self, creator: Creator, db: Session):
        """Actualiza las métricas analíticas de un creador"""
        growth_rates = self.calculate_growth_rate(creator, db)
        potential_score = self.calculate_potential_score(creator, growth_rates)
        
        creator.growth_rate = growth_rates["weekly"]
        creator.potential_score = potential_score
        
        db.commit()