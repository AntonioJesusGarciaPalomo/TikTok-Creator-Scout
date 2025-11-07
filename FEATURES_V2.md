# TikTok Creator Scout v2.0 - Nuevas Funcionalidades 🚀

## 📌 Resumen de Mejoras

La versión 2.0 introduce un sistema completo de **descubrimiento, análisis y outreach automatizado** para creadores de TikTok. Las nuevas funcionalidades permiten:

- ✅ **Búsqueda avanzada** de creadores por múltiples criterios
- ✅ **Generación automática** de mensajes personalizados con IA
- ✅ **Envío automatizado** de mensajes vía TikTok con rate limiting
- ✅ **Gestión de campañas** de outreach completas
- ✅ **Tareas asíncronas** con Celery para procesamiento en background

---

## 🔍 1. Sistema de Búsqueda Avanzada de Creadores

### Tipos de Búsqueda

#### 🏷️ Búsqueda por Hashtag
Descubre creadores que publican contenido con hashtags específicos.

```bash
POST /api/v1/search/execute
{
  "search_type": "hashtag",
  "query": "fitness",
  "filters": {
    "min_followers": 10000,
    "max_followers": 500000
  },
  "auto_scrape": true,
  "save_search": true
}
```

#### 🔑 Búsqueda por Palabras Clave
Encuentra creadores basándote en keywords en sus videos.

```bash
POST /api/v1/search/execute
{
  "search_type": "keyword",
  "query": "recetas veganas",
  "filters": {
    "min_videos": 50,
    "verified_only": false
  },
  "auto_scrape": true
}
```

#### 📈 Búsqueda de Trending
Descubre creadores en tendencia.

```bash
POST /api/v1/search/execute
{
  "search_type": "trending",
  "query": "",
  "filters": {
    "min_followers": 50000
  },
  "auto_scrape": true
}
```

#### 🎵 Búsqueda por Música
Encuentra creadores que usan música específica.

```bash
POST /api/v1/search/execute
{
  "search_type": "music",
  "query": "7123456789",
  "filters": {},
  "auto_scrape": true
}
```

### Búsqueda Múltiple en Paralelo

Ejecuta varias búsquedas simultáneamente y obtén resultados deduplicados:

```bash
POST /api/v1/search/bulk
{
  "searches": [
    {"type": "hashtag", "query": "fitness", "filters": {"min_followers": 10000}},
    {"type": "hashtag", "query": "workout", "filters": {"min_followers": 10000}},
    {"type": "keyword", "query": "gym motivation"}
  ],
  "auto_scrape": true,
  "deduplicate": true
}
```

### Características de Búsqueda

- ✅ **Auto-scraping**: Scrape automático de creadores descubiertos
- ✅ **Filtros avanzados**: min/max followers, videos count, verified status
- ✅ **Historial**: Todas las búsquedas se guardan en la base de datos
- ✅ **Retry automático**: 3 intentos con exponential backoff
- ✅ **Deduplicación**: Elimina creadores duplicados en búsquedas múltiples

---

## 💬 2. Generación de Mensajes Personalizados con IA

### Generación Individual

Genera un mensaje personalizado para un creador específico:

```bash
POST /api/v1/messages/generate
{
  "creator_id": 123,
  "template_id": null,
  "use_ai": true,
  "tone": "professional",
  "language": "es"
}
```

### Generación Masiva

Genera mensajes para múltiples creadores:

```bash
POST /api/v1/messages/generate/bulk
{
  "creator_ids": [123, 456, 789],
  "campaign_id": 1,
  "use_ai": true,
  "tone": "friendly",
  "language": "es"
}
```

### Personalización por Segmento

El sistema genera mensajes específicos según el segmento del creador:

#### Rising Stars
```
¡Hola @creator! 👋

He estado siguiendo tu contenido y me impresiona tu crecimiento
explosivo (15.5% de crecimiento semanal). Con 25.3K seguidores
y un engagement de 8.2%, definitivamente eres una estrella en ascenso.

Me encantaría explorar oportunidades de colaboración...
```

#### High Engagement
```
¡@creator! 🎯

Tu comunidad es increíble - 12.5% de engagement es excepcional.
Es claro que has construido una audiencia muy comprometida y activa.

Tengo algunas propuestas de marcas que valoran exactamente esto...
```

### Variables de Personalización

El sistema utiliza estas variables para personalizar mensajes:

- `{{creator_name}}` - Nombre del creador
- `{{username}}` - Usuario de TikTok
- `{{followers_count}}` - Número de seguidores
- `{{followers_count_k}}` - Seguidores en formato K (25.3K)
- `{{engagement_rate}}` - Tasa de engagement
- `{{segment}}` - Segmento del creador
- `{{potential_score}}` - Score de potencial
- `{{videos_count}}` - Cantidad de videos
- `{{posting_frequency}}` - Videos por semana
- `{{growth_rate}}` - Tasa de crecimiento

### Templates Personalizados

Crea tus propios templates:

```bash
POST /api/v1/messages/templates
{
  "name": "Colaboración Marca",
  "segment": "Rising Stars",
  "subject": "Oportunidad de Colaboración",
  "template_text": "Hola {{creator_name}}! 👋\n\nHe visto tu contenido...",
  "is_active": true
}
```

### Modos de Generación

1. **IA (OpenAI GPT-4)**: Mensajes únicos y contextualizados
2. **Templates**: Mensajes basados en plantillas con variables
3. **Híbrido**: Templates mejorados por IA

---

## 📤 3. Envío Automatizado de Mensajes

### Envío Individual

```bash
POST /api/v1/messages/send
{
  "message_id": 456
}
```

### Envío en Lote

```bash
POST /api/v1/messages/send/batch
{
  "message_ids": [456, 457, 458, 459],
  "delay_between_messages": 10.0
}
```

### Rate Limiting Inteligente

El sistema incluye protección automática contra rate limiting:

- ✅ **Límite por hora**: Configurable (default: 50 mensajes/hora)
- ✅ **Límite diario**: Configurable (default: 200 mensajes/día)
- ✅ **Contador en Redis**: Tracking en tiempo real
- ✅ **Auto-pausa**: Se detiene automáticamente al alcanzar límites
- ✅ **Retry automático**: Reintenta mensajes fallidos

### Estados de Mensajes

- `draft` - Mensaje creado pero no enviado
- `queued` - En cola para envío
- `sending` - Enviando actualmente
- `sent` - Enviado exitosamente
- `failed` - Falló el envío
- `responded` - El creador respondió

### Estadísticas de Envío

```bash
GET /api/v1/messages/stats/sending?days=7
```

Respuesta:
```json
{
  "total_sent": 150,
  "total_failed": 5,
  "total_queued": 25,
  "total_responded": 12,
  "response_rate": 8.0,
  "rate_limits": {
    "hourly": 15,
    "daily": 150,
    "hourly_limit": 50,
    "daily_limit": 200
  }
}
```

---

## 🎯 4. Gestión de Campañas

### Crear Campaña

```bash
POST /api/v1/campaigns
{
  "name": "Campaña Fitness Q1 2024",
  "description": "Outreach a creadores fitness 10K-100K",
  "target_segment": "Rising Stars",
  "filters": {
    "min_followers": 10000,
    "max_followers": 100000,
    "min_engagement": 5.0
  },
  "auto_send": false,
  "daily_limit": 50,
  "messages_per_hour": 10
}
```

### Generar Mensajes para Campaña

```bash
POST /api/v1/campaigns/1/generate-messages?use_ai=true&tone=professional
```

Esto automáticamente:
1. Busca creadores que cumplen los criterios
2. Genera mensajes personalizados para cada uno
3. Los guarda como `draft` en la campaña

### Iniciar Campaña

```bash
POST /api/v1/campaigns/1/start
```

### Encolar Mensajes

```bash
POST /api/v1/messages/queue/1
```

Encola todos los mensajes `draft` de la campaña para envío automático.

### Estadísticas de Campaña

```bash
GET /api/v1/campaigns/1/stats
```

Respuesta:
```json
{
  "campaign_id": 1,
  "campaign_name": "Campaña Fitness Q1 2024",
  "is_active": true,
  "total_targets": 250,
  "messages_sent": 180,
  "messages_failed": 5,
  "responses_received": 15,
  "response_rate": 8.33,
  "stats_by_status": {
    "draft": 20,
    "queued": 30,
    "sent": 180,
    "failed": 5,
    "responded": 15
  }
}
```

---

## ⚙️ 5. Tareas Asíncronas con Celery

### Tareas de Scraping

```python
# Scrapear un creador
from app.tasks import scrape_creator_task
result = scrape_creator_task.delay("username")

# Scrapear múltiples creadores
from app.tasks import batch_scrape_creators_task
result = batch_scrape_creators_task.delay(["user1", "user2", "user3"])

# Búsqueda y scraping automático
from app.tasks import search_and_scrape_task
result = search_and_scrape_task.delay("hashtag", "fitness", {"min_followers": 10000})
```

### Tareas de Mensajería

```python
# Generar mensaje
from app.tasks import generate_message_task
result = generate_message_task.delay(creator_id=123, campaign_id=1, use_ai=True)

# Generar múltiples mensajes
from app.tasks import bulk_generate_messages_task
result = bulk_generate_messages_task.delay([123, 456, 789], campaign_id=1)

# Enviar mensaje
from app.tasks import send_message_task
result = send_message_task.delay(message_id=456)

# Enviar lote
from app.tasks import send_batch_messages_task
result = send_batch_messages_task.delay([456, 457, 458], delay=10.0)
```

### Tareas Periódicas

El sistema incluye tareas automáticas que se ejecutan periódicamente:

#### Procesar Cola de Mensajes
- **Frecuencia**: Cada 5 minutos
- **Función**: Envía mensajes en cola respetando rate limits

#### Actualizar Analíticas
- **Frecuencia**: Cada hora
- **Función**: Recalcula métricas y scores de todos los creadores

### Tareas de Campaña

```python
# Ejecutar campaña completa
from app.tasks import execute_campaign_task
result = execute_campaign_task.delay(campaign_id=1)
```

Esta tarea:
1. Filtra creadores según criterios de la campaña
2. Genera mensajes personalizados para todos
3. Los encola automáticamente si `auto_send=true`

---

## 🔧 Configuración

### Variables de Entorno

Actualiza tu archivo `.env`:

```bash
# OpenAI para generación de mensajes (OBLIGATORIO para IA)
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4-turbo-preview

# TikTok API para envío de mensajes (Opcional)
TIKTOK_ACCESS_TOKEN=tu_token
TIKTOK_CLIENT_KEY=tu_client_key
TIKTOK_CLIENT_SECRET=tu_client_secret

# Rate Limiting
MAX_MESSAGES_PER_HOUR=50
MAX_MESSAGES_PER_DAY=200

# Búsqueda
SEARCH_RESULTS_LIMIT=100
AUTO_SCRAPE_NEW_CREATORS=True

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### Iniciar Workers de Celery

```bash
# Worker principal
celery -A app.celery_app worker --loglevel=info

# Worker con Beat (tareas periódicas)
celery -A app.celery_app worker --beat --loglevel=info

# Flower (monitoreo)
celery -A app.celery_app flower
```

---

## 📊 Casos de Uso

### Caso 1: Descubrir y Contactar Creadores de Fitness

```bash
# 1. Buscar creadores
POST /api/v1/search/bulk
{
  "searches": [
    {"type": "hashtag", "query": "fitness", "filters": {"min_followers": 10000}},
    {"type": "hashtag", "query": "workout"},
    {"type": "keyword", "query": "gym motivation"}
  ],
  "auto_scrape": true,
  "deduplicate": true
}

# 2. Crear campaña
POST /api/v1/campaigns
{
  "name": "Fitness Influencers 2024",
  "target_segment": "Rising Stars",
  "filters": {"min_followers": 10000, "min_engagement": 5.0},
  "auto_send": true
}

# 3. Generar mensajes
POST /api/v1/campaigns/1/generate-messages?use_ai=true

# 4. Revisar y enviar
POST /api/v1/messages/queue/1
```

### Caso 2: Outreach Personalizado a Segmento Específico

```bash
# 1. Segmentar creadores
POST /api/v1/creators/segment

# 2. Obtener Rising Stars
GET /api/v1/creators?segment=Rising+Stars&min_engagement=7.0

# 3. Generar mensajes personalizados
POST /api/v1/messages/generate/bulk
{
  "creator_ids": [123, 456, 789],
  "use_ai": true,
  "tone": "friendly"
}

# 4. Enviar gradualmente
POST /api/v1/messages/send/batch
{
  "message_ids": [1, 2, 3],
  "delay_between_messages": 15.0
}
```

### Caso 3: Campaña Automatizada Completa

```bash
# Ejecutar en background con Celery
from app.tasks import execute_campaign_task
execute_campaign_task.delay(campaign_id=1)
```

Esto ejecuta automáticamente:
1. Búsqueda de creadores objetivo
2. Scraping de datos
3. Análisis y segmentación
4. Generación de mensajes con IA
5. Envío automatizado con rate limiting

---

## 🚀 Mejoras de Rendimiento

### Optimizaciones Implementadas

1. **Búsquedas en Paralelo**: Múltiples búsquedas simultáneas con `asyncio.gather`
2. **Batch Operations**: Scraping y mensajería en lotes
3. **Redis Caching**: Rate limiting y contadores en Redis
4. **Background Tasks**: Celery para operaciones pesadas
5. **Retry Logic**: Reintentos automáticos con exponential backoff
6. **Connection Pooling**: Pool de conexiones HTTP con `httpx`

### Escalabilidad

- ✅ Soporta procesamiento de miles de creadores
- ✅ Envío de cientos de mensajes por hora
- ✅ Múltiples workers de Celery en paralelo
- ✅ Distribución de carga con Redis

---

## 📈 Métricas y Monitoreo

### Endpoints de Estadísticas

```bash
# Estadísticas de envío
GET /api/v1/messages/stats/sending?days=7

# Estadísticas de campaña
GET /api/v1/campaigns/1/stats

# Historial de búsquedas
GET /api/v1/search/history?limit=50

# Health check
GET /health
```

### Monitoreo con Flower

Accede a `http://localhost:5555` para:
- Ver tareas en ejecución
- Historial de tareas
- Métricas de workers
- Reintentar tareas fallidas

---

## 🔐 Seguridad y Mejores Prácticas

### Rate Limiting
- Configuración conservadora por defecto
- Contadores en Redis para precisión
- Pausas automáticas al alcanzar límites

### Validación de Datos
- Todos los endpoints usan Pydantic schemas
- Validación de entrada estricta
- Sanitización de datos

### Logging Completo
- Logs de todas las operaciones
- Tracking de errores
- Auditoría de mensajes enviados

### Retry y Error Handling
- 3 reintentos automáticos en operaciones críticas
- Exponential backoff
- Graceful degradation

---

## 🎓 Próximos Pasos

1. **Configurar credenciales**: OpenAI API key y TikTok API tokens
2. **Iniciar servicios**: Redis, PostgreSQL, Celery workers
3. **Probar búsquedas**: Descubrir creadores en tu nicho
4. **Crear templates**: Personalizar mensajes para tu marca
5. **Lanzar campaña**: Iniciar tu primera campaña de outreach

¡Estás listo para escalar tu outreach a creadores de TikTok! 🚀
