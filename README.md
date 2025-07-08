# TikTok Creator-Scout 🚀

Sistema inteligente para identificar, analizar y segmentar creadores de contenido con potencial en TikTok. Utiliza IA y machine learning para proporcionar insights valiosos sobre métricas de crecimiento, engagement y potencial de monetización.

![TikTok Creator Scout](https://img.shields.io/badge/TikTok-Creator_Scout-FF0050?style=for-the-badge&logo=tiktok&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![React](https://img.shields.io/badge/React-18.2-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688?style=for-the-badge&logo=fastapi&logoColor=white)

---

## 📋 Tabla de Contenidos

- [Características](#-características)
- [Arquitectura](#-arquitectura)
- [Requisitos](#-requisitos)
- [Instalación Rápida](#-instalación-rápida)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Configuración](#-configuración)
- [Uso](#-uso)
- [API Documentation](#-api-documentation)
- [Tecnologías](#-tecnologías)
- [Contribución](#-contribución)
- [Licencia](#-licencia)

---

## ✨ Características

### 🔍 Análisis Inteligente
- **Scraping Automático**: Extracción de métricas públicas usando la API de TikTok Scraper
- **Segmentación con IA**: Clasificación automática en 5 segmentos usando K-means clustering
- **Score de Potencial**: Algoritmo propietario que evalúa el potencial de cada creador (0-100)
- **Análisis Predictivo**: Proyecciones de crecimiento basadas en tendencias históricas

### 📊 Métricas Avanzadas
- Tasa de engagement real
- Frecuencia de publicación
- Crecimiento de seguidores (diario/semanal/mensual)
- Análisis de tendencias
- Comparativas por segmento

### 🎯 Segmentos Identificados
1. **Rising Stars** - Alto potencial, crecimiento explosivo
2. **Consistent Performers** - Métricas estables y confiables
3. **High Engagement** - Alta interacción, comunidad activa
4. **Growth Needed** - Requieren estrategia de crecimiento
5. **Emerging Talent** - Nuevos con potencial oculto

### 💻 Interfaz Moderna
- Dashboard interactivo con visualizaciones en tiempo real
- Filtros avanzados y búsqueda inteligente
- Vista de tarjetas y tabla
- Exportación de datos
- Modo responsivo

---

## 🏗️ Arquitectura

```mermaid
graph TB
    A[Frontend React] -->|API REST/GraphQL| B[Backend FastAPI]
    B --> C[PostgreSQL]
    B --> D[Redis Cache]
    B --> E[TikTok Scraper API]
    B --> F[ML Services]
    F --> G[Scikit-learn]
    F --> H[Semantic Kernel]
    
    subgraph "Stack Tecnológico"
        A
        B
        C
        D
    end
    
    subgraph "Servicios Externos"
        E
        H
    end
```

---

## 📋 Requisitos

### Obligatorios
- Python 3.9+
- Node.js 16+
- PostgreSQL 14+
- Redis 6+

### Opcionales
- Docker & Docker Compose
- Cuenta de Azure (para almacenamiento en la nube)

### APIs Requeridas
- **RapidAPI Key** para TikTok Scraper API
- **OpenAI API Key** (opcional, para análisis avanzado con IA)

---

## 🚀 Instalación Rápida

### Opción 1: Script Automático (Recomendado)

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/tiktok-creator-scout.git
cd tiktok-creator-scout

# Ejecutar script de instalación
python3 setup.py
```

El script automáticamente:
- ✅ Verifica prerequisitos
- ✅ Crea estructura de carpetas
- ✅ Instala dependencias
- ✅ Configura base de datos
- ✅ Genera archivos de configuración

### Opción 2: Docker Compose

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/tiktok-creator-scout.git
cd tiktok-creator-scout

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tu RAPIDAPI_KEY

# Iniciar servicios
docker-compose up -d
```

### Opción 3: Instalación Manual

Ver guías detalladas:
- [📘 Guía Backend](./backend/README.md)
- [📗 Guía Frontend](./frontend/README.md)

---

## 📁 Estructura del Proyecto

```
tiktok-creator-scout/
├── setup.py                    # Script de instalación automática
├── README.md                   # Este archivo
├── .gitignore
├── docker-compose.yml          # Orquestación de servicios
│
├── backend/                    # API y lógica de negocio
│   ├── app/
│   │   ├── main.py            # Punto de entrada FastAPI
│   │   ├── config.py          # Configuración
│   │   ├── database.py        # Conexión DB
│   │   ├── models/            # Modelos SQLAlchemy
│   │   ├── schemas/           # Esquemas Pydantic
│   │   ├── services/          # Lógica de negocio
│   │   ├── api/               # Endpoints REST
│   │   └── graphql/           # Schema GraphQL
│   ├── requirements.txt       # Dependencias Python
│   ├── Dockerfile
│   └── README.md
│
└── frontend/                   # Interfaz de usuario
    ├── src/
    │   ├── components/        # Componentes React
    │   ├── services/          # Llamadas API
    │   ├── App.js
    │   └── index.js
    ├── public/
    ├── package.json           # Dependencias Node
    ├── Dockerfile
    └── README.md
```

---

## ⚙️ Configuración

### 1. Variables de Entorno Backend (`backend/.env`)

```env
# Base de datos
DATABASE_URL=postgresql://user:password@localhost/tiktok_scout

# Redis
REDIS_URL=redis://localhost:6379

# RapidAPI (OBLIGATORIO)
RAPIDAPI_KEY=tu_clave_aqui
RAPIDAPI_HOST=tiktok-scraper7.p.rapidapi.com

# OpenAI (Opcional)
OPENAI_API_KEY=tu_clave_aqui

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000"]
```

### 2. Variables de Entorno Frontend (`frontend/.env`)

```env
REACT_APP_API_URL=http://localhost:8000/api/v1
REACT_APP_GRAPHQL_URL=http://localhost:8000/graphql
```

### 3. Obtener API Keys

1. **RapidAPI Key** (Obligatorio):
   - Ve a [TikTok Scraper API](https://rapidapi.com/maknimarc-pWFsrWbJJ9P/api/tiktok-scraper7)
   - Suscríbete al plan gratuito o de pago
   - Copia tu API Key

2. **OpenAI Key** (Opcional):
   - Ve a [OpenAI Platform](https://platform.openai.com)
   - Genera una API Key
   - Úsala para análisis avanzados con IA

---

## 💻 Uso

### 1. Iniciar Servicios

#### Backend
```bash
cd backend
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate     # Windows

uvicorn app.main:app --reload
```

#### Frontend
```bash
cd frontend
npm start
```

### 2. Acceder a la Aplicación

- 🌐 **Dashboard**: http://localhost:3000
- 📚 **API Docs**: http://localhost:8000/docs
- 🔍 **GraphQL**: http://localhost:8000/graphql

### 3. Agregar Creadores

#### Opción A: Desde el Dashboard
1. Click en "Agregar Creador"
2. Ingresa el username (sin @)
3. Espera el análisis automático

#### Opción B: API REST
```bash
curl -X POST http://localhost:8000/api/v1/creators/scrape \
  -H "Content-Type: application/json" \
  -d '{"usernames": ["username1", "username2"]}'
```

#### Opción C: GraphQL
```graphql
mutation {
  batchScrape(usernames: ["username1", "username2"]) {
    id
    username
    potentialScore
  }
}
```

### 4. Filtrar y Analizar

Usa los filtros del dashboard para encontrar creadores por:
- 📊 Rango de seguidores
- 💯 Engagement mínimo
- 📈 Tasa de crecimiento
- 🎯 Segmento específico
- 📅 Frecuencia de publicación

---

## 📖 API Documentation

### REST Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/v1/creators` | Lista todos los creadores |
| GET | `/api/v1/creators/{username}` | Obtiene un creador específico |
| POST | `/api/v1/creators/scrape` | Scrapea nuevos creadores |
| GET | `/api/v1/creators/segments/summary` | Resumen de segmentos |

### GraphQL Queries

```graphql
# Obtener creadores con filtros
query {
  creators(
    filters: {
      minFollowers: 10000
      minEngagement: 2.5
      segment: "Rising Stars"
    }
  ) {
    id
    username
    followersCount
    engagementRate
    potentialScore
  }
}

# Análisis de segmentos
query {
  segmentAnalysis {
    segmentName
    creatorCount
    avgEngagement
    aiInsights
  }
}
```

---

## 🛠️ Tecnologías

### Backend
- **FastAPI** - Framework web moderno y rápido
- **PostgreSQL** - Base de datos relacional
- **SQLAlchemy** - ORM
- **Strawberry GraphQL** - GraphQL en Python
- **Scikit-learn** - Machine Learning
- **Semantic Kernel** - Integración con IA
- **Redis** - Cache y colas de tareas
- **Celery** - Tareas asíncronas

### Frontend
- **React 18** - Librería UI
- **Recharts** - Visualizaciones
- **Tailwind CSS** - Estilos utility-first
- **Axios** - Cliente HTTP
- **Lucide React** - Iconos

### Infraestructura
- **Docker** - Containerización
- **Azure** - Cloud computing (opcional)
- **GitHub Actions** - CI/CD

---

## 🤝 Contribución

¡Las contribuciones son bienvenidas! Por favor:

1. Fork el proyecto
2. Crea tu feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la branch (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

### Guías de Desarrollo

- Sigue PEP 8 para Python
- Usa ESLint para JavaScript
- Escribe tests para nuevas funcionalidades
- Actualiza la documentación

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

---

## 👥 Equipo

- **Tu Nombre** - *Desarrollador Principal* - [@tuusuario](https://github.com/tuusuario)

---

## 🙏 Agradecimientos

- [RapidAPI](https://rapidapi.com) por la API de TikTok
- [Anthropic](https://anthropic.com) por Claude y Semantic Kernel
- La comunidad open source

---

<p align="center">
  Hecho con ❤️ por ingenieros en IA para creadores de contenido
</p>