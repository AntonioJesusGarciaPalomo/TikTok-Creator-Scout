# backend/app/services/message_generator.py
from typing import Dict, Optional, List
from openai import AsyncOpenAI
from jinja2 import Template
from sqlalchemy.orm import Session
from ..config import settings
from ..models.creator import Creator
from ..models.message import MessageTemplate, Message, MessageStatus
import logging

logger = logging.getLogger(__name__)

class MessageGeneratorService:
    """Servicio para generar mensajes personalizados usando IA"""

    def __init__(self):
        self.client = None
        if settings.OPENAI_API_KEY:
            self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        else:
            logger.warning("OpenAI API key not configured. Message generation will use templates only.")

    def get_creator_context(self, creator: Creator) -> Dict:
        """Extrae contexto relevante del creador para personalización"""
        return {
            "creator_name": creator.display_name or creator.username,
            "username": creator.username,
            "followers_count": f"{creator.followers_count:,}",
            "followers_count_k": f"{creator.followers_count / 1000:.1f}K" if creator.followers_count >= 1000 else str(creator.followers_count),
            "engagement_rate": f"{creator.engagement_rate:.2f}%",
            "segment": creator.segment or "General",
            "potential_score": f"{creator.potential_score:.1f}",
            "videos_count": creator.videos_count,
            "posting_frequency": f"{creator.posting_frequency:.1f}",
            "verified": "verificado" if creator.verified else "no verificado",
            "avg_likes": f"{int(creator.avg_likes_per_video):,}",
            "growth_rate": f"{creator.growth_rate:.2f}%"
        }

    def render_template(self, template_text: str, context: Dict) -> str:
        """Renderiza un template con Jinja2"""
        try:
            template = Template(template_text)
            return template.render(**context)
        except Exception as e:
            logger.error(f"Error rendering template: {e}")
            return template_text

    async def generate_with_ai(
        self,
        creator: Creator,
        segment_info: Optional[str] = None,
        tone: str = "professional",
        language: str = "es"
    ) -> str:
        """Genera un mensaje personalizado usando OpenAI GPT"""
        if not self.client:
            logger.error("OpenAI client not initialized")
            return None

        context = self.get_creator_context(creator)

        # Construir prompt para OpenAI
        system_prompt = f"""Eres un experto en marketing de influencers y outreach personalizado.
Tu tarea es escribir mensajes cortos, personalizados y atractivos para contactar a creadores de TikTok.

Tono: {tone}
Idioma: {language}

El mensaje debe:
- Ser breve (máximo 150 palabras)
- Ser genuino y personalizado
- Mencionar algo específico del creador
- Ser directo y claro sobre la propuesta
- Terminar con un call-to-action
- No ser spam ni genérico"""

        user_prompt = f"""Genera un mensaje personalizado para contactar a este creador de TikTok:

Nombre: {context['creator_name']} (@{context['username']})
Seguidores: {context['followers_count']}
Engagement: {context['engagement_rate']}
Segmento: {context['segment']}
Score de Potencial: {context['potential_score']}/100
Videos: {context['videos_count']}
Frecuencia de publicación: {context['posting_frequency']} videos/semana
Crecimiento: {context['growth_rate']} semanal

{segment_info or ''}

El objetivo es establecer una colaboración o partnership."""

        try:
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=300
            )

            message = response.choices[0].message.content.strip()
            logger.info(f"Mensaje generado con IA para {creator.username}")
            return message

        except Exception as e:
            logger.error(f"Error generating message with AI: {e}")
            return None

    def get_segment_specific_template(self, segment: str) -> str:
        """Retorna un template específico para cada segmento"""
        templates = {
            "Rising Stars": """¡Hola {{creator_name}}! 👋

He estado siguiendo tu contenido y me impresiona tu crecimiento explosivo ({{growth_rate}} de crecimiento semanal).
Con {{followers_count_k}} seguidores y un engagement de {{engagement_rate}}, definitivamente eres una estrella en ascenso.

Me encantaría explorar oportunidades de colaboración que puedan ayudarte a acelerar aún más tu crecimiento.

¿Tienes 15 minutos esta semana para una llamada rápida?

Saludos,
[Tu nombre]""",

            "Consistent Performers": """Hola {{creator_name}},

Admiro la consistencia de tu contenido - {{posting_frequency}} videos por semana con un engagement sostenido de {{engagement_rate}}.
Eso demuestra profesionalismo y dedicación.

Trabajo con marcas que buscan exactamente este tipo de confiabilidad en sus colaboradores.

¿Te interesaría conocer algunas oportunidades que podrían ser perfectas para ti?

Quedamos en contacto,
[Tu nombre]""",

            "High Engagement": """¡{{creator_name}}! 🎯

Tu comunidad es increíble - {{engagement_rate}} de engagement es excepcional.
Es claro que has construido una audiencia muy comprometida y activa.

Tengo algunas propuestas de marcas que valoran exactamente esto: calidad sobre cantidad.

¿Charlamos esta semana?

¡Saludos!
[Tu nombre]""",

            "Emerging Talent": """Hola {{creator_name}},

Vi tu contenido y veo mucho potencial. Aunque estás comenzando, tu score de potencial ({{potential_score}}/100)
muestra que tienes lo necesario para crecer significativamente.

Me especializo en ayudar a creadores emergentes como tú a conseguir sus primeras colaboraciones con marcas.

¿Te gustaría que hablemos sobre cómo podemos trabajar juntos?

Un saludo,
[Tu nombre]""",

            "Growth Needed": """Hola {{creator_name}},

He revisado tu perfil y creo que con algunas estrategias específicas, podrías aumentar considerablemente
tu engagement y crecimiento.

Trabajo con creadores ayudándoles a optimizar su contenido y conseguir colaboraciones que impulsen su audiencia.

¿Te interesa que conversemos sobre esto?

Saludos,
[Tu nombre]"""
        }

        return templates.get(segment, templates["Emerging Talent"])

    async def generate_personalized_message(
        self,
        creator: Creator,
        template_id: Optional[int] = None,
        use_ai: bool = True,
        tone: str = "professional",
        db: Optional[Session] = None
    ) -> str:
        """
        Genera un mensaje personalizado para un creador

        Args:
            creator: El creador para quien generar el mensaje
            template_id: ID del template a usar (opcional)
            use_ai: Si usar IA para generar (si no, usa templates)
            tone: Tono del mensaje
            db: Sesión de base de datos

        Returns:
            Mensaje personalizado
        """
        # Intentar generar con IA si está habilitado
        if use_ai and self.client:
            segment_info = None
            if creator.segment:
                segment_info = f"Este creador pertenece al segmento '{creator.segment}'."

            ai_message = await self.generate_with_ai(
                creator=creator,
                segment_info=segment_info,
                tone=tone
            )

            if ai_message:
                return ai_message

        # Fallback: usar template
        context = self.get_creator_context(creator)

        # Si hay template_id, buscar en DB
        if template_id and db:
            template_record = db.query(MessageTemplate).filter(
                MessageTemplate.id == template_id
            ).first()

            if template_record:
                return self.render_template(template_record.template_text, context)

        # Si no hay template específico, usar template del segmento
        segment_template = self.get_segment_specific_template(creator.segment or "Emerging Talent")
        return self.render_template(segment_template, context)

    async def bulk_generate_messages(
        self,
        creators: List[Creator],
        use_ai: bool = True,
        tone: str = "professional",
        db: Optional[Session] = None
    ) -> Dict[int, str]:
        """
        Genera mensajes para múltiples creadores

        Returns:
            Diccionario {creator_id: message}
        """
        messages = {}

        for creator in creators:
            try:
                message = await self.generate_personalized_message(
                    creator=creator,
                    use_ai=use_ai,
                    tone=tone,
                    db=db
                )
                messages[creator.id] = message
                logger.info(f"Mensaje generado para {creator.username}")
            except Exception as e:
                logger.error(f"Error generando mensaje para {creator.username}: {e}")
                messages[creator.id] = None

        return messages

    def create_message_records(
        self,
        creator_messages: Dict[int, str],
        campaign_id: Optional[int] = None,
        db: Session = None
    ) -> List[Message]:
        """
        Crea registros de mensajes en la base de datos

        Args:
            creator_messages: Diccionario {creator_id: message_text}
            campaign_id: ID de campaña (opcional)
            db: Sesión de base de datos

        Returns:
            Lista de mensajes creados
        """
        if not db:
            logger.error("Database session required")
            return []

        created_messages = []

        for creator_id, message_text in creator_messages.items():
            if not message_text:
                continue

            message = Message(
                creator_id=creator_id,
                campaign_id=campaign_id,
                content=message_text,
                status=MessageStatus.DRAFT
            )
            db.add(message)
            created_messages.append(message)

        db.commit()
        logger.info(f"Creados {len(created_messages)} registros de mensajes")

        return created_messages
