"""
TikTok Creator-Scout - Script de Inicialización
Automatiza la configuración inicial del proyecto
"""

import os
import sys
import subprocess
import json
from pathlib import Path

class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_step(message):
    print(f"\n{Colors.BLUE}[STEP]{Colors.END} {message}")

def print_success(message):
    print(f"{Colors.GREEN}✓{Colors.END} {message}")

def print_error(message):
    print(f"{Colors.RED}✗{Colors.END} {message}")
    
def print_warning(message):
    print(f"{Colors.YELLOW}!{Colors.END} {message}")

def run_command(command, cwd=None):
    """Ejecuta un comando y retorna el resultado"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd, 
            capture_output=True, 
            text=True
        )
        if result.returncode == 0:
            return True, result.stdout
        else:
            return False, result.stderr
    except Exception as e:
        return False, str(e)

def check_prerequisites():
    """Verifica que estén instalados los prerequisitos"""
    print_step("Verificando prerequisitos...")
    
    prerequisites = {
        "Python": "python3 --version",
        "Node.js": "node --version",
        "PostgreSQL": "psql --version",
        "Redis": "redis-cli --version",
        "Docker": "docker --version",
        "Docker Compose": "docker-compose --version"
    }
    
    missing = []
    for name, command in prerequisites.items():
        success, _ = run_command(command)
        if success:
            print_success(f"{name} instalado")
        else:
            print_warning(f"{name} no encontrado")
            missing.append(name)
    
    if missing:
        print_error(f"\nFaltan prerequisitos: {', '.join(missing)}")
        print("Por favor, instala los componentes faltantes antes de continuar.")
        
        if "Docker" not in missing and "Docker Compose" not in missing:
            response = input("\n¿Deseas continuar con Docker? (y/n): ")
            if response.lower() == 'y':
                return True, True  # Continuar con Docker
        return False, False
    
    return True, False

def create_project_structure():
    """Crea la estructura de directorios del proyecto"""
    print_step("Creando estructura del proyecto...")
    
    directories = [
        "backend/app/models",
        "backend/app/schemas",
        "backend/app/services",
        "backend/app/api",
        "backend/app/graphql",
        "backend/app/utils",
        "frontend/src/components",
        "frontend/src/pages",
        "frontend/src/services",
        "frontend/public"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print_success("Estructura de directorios creada")

def setup_backend_env():
    """Configura el archivo .env del backend"""
    print_step("Configurando variables de entorno del backend...")
    
    env_content = """# Base de datos
DATABASE_URL=postgresql://tiktok_user:tiktok_pass@localhost/tiktok_scout

# Redis
REDIS_URL=redis://localhost:6379

# RapidAPI
RAPIDAPI_KEY=
RAPIDAPI_HOST=tiktok-scraper7.p.rapidapi.com

# Azure (opcional)
AZURE_STORAGE_CONNECTION_STRING=
AZURE_CONTAINER_NAME=tiktok-data

# OpenAI para Semantic Kernel (opcional)
OPENAI_API_KEY=

# Configuración API
API_V1_STR=/api/v1
PROJECT_NAME=TikTok Creator Scout

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000"]
"""
    
    env_file = Path("backend/.env")
    if env_file.exists():
        response = input(".env ya existe en backend. ¿Sobrescribir? (y/n): ")
        if response.lower() != 'y':
            print_warning("Manteniendo .env existente")
            return
    
    env_file.write_text(env_content)
    print_success(".env del backend creado")
    
    print_warning("\nIMPORTANTE: Añade tu RAPIDAPI_KEY en backend/.env")

def setup_frontend_env():
    """Configura el archivo .env del frontend"""
    print_step("Configurando variables de entorno del frontend...")
    
    env_content = """REACT_APP_API_URL=http://localhost:8000/api/v1
REACT_APP_GRAPHQL_URL=http://localhost:8000/graphql
"""
    
    env_file = Path("frontend/.env")
    env_file.write_text(env_content)
    print_success(".env del frontend creado")

def setup_database():
    """Configura la base de datos PostgreSQL"""
    print_step("Configurando base de datos PostgreSQL...")
    
    commands = [
        "CREATE USER tiktok_user WITH PASSWORD 'tiktok_pass';",
        "CREATE DATABASE tiktok_scout OWNER tiktok_user;",
        "GRANT ALL PRIVILEGES ON DATABASE tiktok_scout TO tiktok_user;"
    ]
    
    for cmd in commands:
        success, output = run_command(f'psql -U postgres -c "{cmd}"')
        if not success and "already exists" not in output:
            print_error(f"Error ejecutando: {cmd}")
            print(output)
            return False
    
    print_success("Base de datos configurada")
    return True

def install_backend_dependencies():
    """Instala las dependencias del backend"""
    print_step("Instalando dependencias del backend...")
    
    # Crear requirements.txt si no existe
    requirements_path = Path("backend/requirements.txt")
    if not requirements_path.exists():
        print_warning("requirements.txt no encontrado, creando uno nuevo...")
        requirements_content = """fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
alembic==1.12.1
pydantic==2.5.0
pydantic-settings==2.1.0
httpx==0.25.2
redis==5.0.1
celery==5.3.4
strawberry-graphql[fastapi]==0.215.1
scikit-learn==1.3.2
pandas==2.1.3
numpy==1.26.2
semantic-kernel==0.4.0.dev0
azure-storage-blob==12.19.0
python-dotenv==1.0.0
pytest==7.4.3
pytest-asyncio==0.21.1
"""
        requirements_path.write_text(requirements_content)
    
    # Crear entorno virtual
    success, _ = run_command("python3 -m venv venv", cwd="backend")
    if not success:
        print_error("Error creando entorno virtual")
        return False
    
    # Instalar dependencias
    pip_cmd = "venv/bin/pip" if os.name != 'nt' else "venv\\Scripts\\pip"
    success, output = run_command(f"{pip_cmd} install -r requirements.txt", cwd="backend")
    
    if success:
        print_success("Dependencias del backend instaladas")
        return True
    else:
        print_error("Error instalando dependencias del backend")
        print(output)
        return False

def install_frontend_dependencies():
    """Instala las dependencias del frontend"""
    print_step("Instalando dependencias del frontend...")
    
    # Crear package.json si no existe
    package_path = Path("frontend/package.json")
    if not package_path.exists():
        print_warning("package.json no encontrado, creando uno nuevo...")
        package_content = {
            "name": "tiktok-creator-scout",
            "version": "0.1.0",
            "private": True,
            "dependencies": {
                "@testing-library/jest-dom": "^5.17.0",
                "@testing-library/react": "^13.4.0",
                "@testing-library/user-event": "^13.5.0",
                "axios": "^1.6.0",
                "lucide-react": "^0.263.1",
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "react-scripts": "5.0.1",
                "recharts": "^2.8.0",
                "web-vitals": "^2.1.4"
            },
            "scripts": {
                "start": "react-scripts start",
                "build": "react-scripts build",
                "test": "react-scripts test",
                "eject": "react-scripts eject"
            },
            "eslintConfig": {
                "extends": [
                    "react-app",
                    "react-app/jest"
                ]
            },
            "browserslist": {
                "production": [
                    ">0.2%",
                    "not dead",
                    "not op_mini all"
                ],
                "development": [
                    "last 1 chrome version",
                    "last 1 firefox version",
                    "last 1 safari version"
                ]
            }
        }
        
        package_path.write_text(json.dumps(package_content, indent=2))
    
    success, output = run_command("npm install", cwd="frontend")
    
    if success:
        print_success("Dependencias del frontend instaladas")
        return True
    else:
        print_error("Error instalando dependencias del frontend")
        print(output)
        return False

def setup_docker():
    """Configura y ejecuta Docker"""
    print_step("Configurando Docker...")
    
    # Crear Dockerfile para backend si no existe
    backend_dockerfile = Path("backend/Dockerfile")
    if not backend_dockerfile.exists():
        dockerfile_content = """FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
"""
        backend_dockerfile.write_text(dockerfile_content)
    
    # Crear Dockerfile para frontend si no existe
    frontend_dockerfile = Path("frontend/Dockerfile")
    if not frontend_dockerfile.exists():
        dockerfile_content = """FROM node:16-alpine as build

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
"""
        frontend_dockerfile.write_text(dockerfile_content)
    
    print_success("Dockerfiles creados")
    
    response = input("\n¿Deseas iniciar los servicios con Docker Compose? (y/n): ")
    if response.lower() == 'y':
        print_step("Iniciando servicios con Docker Compose...")
        success, output = run_command("docker-compose up -d", cwd="backend")
        
        if success:
            print_success("Servicios iniciados con Docker Compose")
            print("\nServicios disponibles en:")
            print("- Backend API: http://localhost:8000")
            print("- Frontend: http://localhost:3000")
            print("- PostgreSQL: localhost:5432")
            print("- Redis: localhost:6379")
        else:
            print_error("Error iniciando servicios")
            print(output)

def create_sample_data():
    """Crea datos de ejemplo para testing"""
    print_step("¿Deseas crear datos de ejemplo? (y/n): ")
    response = input()
    
    if response.lower() != 'y':
        return
    
    sample_script = """
import asyncio
from app.database import SessionLocal
from app.services.tiktok_scraper import TikTokScraperService

async def create_sample_data():
    db = SessionLocal()
    scraper = TikTokScraperService()
    
    # Lista de creadores de ejemplo (reemplazar con usernames reales)
    sample_creators = [
        "creator1",
        "creator2",
        "creator3"
    ]
    
    print("Creando datos de ejemplo...")
    
    for username in sample_creators:
        try:
            creator = await scraper.scrape_and_save_creator(username, db)
            if creator:
                print(f"✓ {username} agregado")
            else:
                print(f"✗ Error con {username}")
        except Exception as e:
            print(f"✗ Error con {username}: {e}")
    
    db.close()
    print("\\nDatos de ejemplo creados")

if __name__ == "__main__":
    asyncio.run(create_sample_data())
"""
    
    script_path = Path("backend/create_sample_data.py")
    script_path.write_text(sample_script)
    
    print_success("Script de datos de ejemplo creado en backend/create_sample_data.py")
    print_warning("Edita el script con usernames reales antes de ejecutarlo")

def main():
    """Función principal del script de setup"""
    print(f"\n{Colors.GREEN}{'='*50}")
    print("TikTok Creator-Scout - Setup Automático")
    print(f"{'='*50}{Colors.END}\n")
    
    # Verificar prerequisitos
    can_continue, use_docker = check_prerequisites()
    if not can_continue:
        return
    
    # Crear estructura del proyecto
    create_project_structure()
    
    # Configurar archivos de entorno
    setup_backend_env()
    setup_frontend_env()
    
    if use_docker:
        # Setup con Docker
        setup_docker()
    else:
        # Setup manual
        # Configurar base de datos
        db_response = input("\n¿Configurar base de datos PostgreSQL? (y/n): ")
        if db_response.lower() == 'y':
            setup_database()
        
        # Instalar dependencias
        install_backend_dependencies()
        install_frontend_dependencies()
        
        # Crear datos de ejemplo
        create_sample_data()
        
        print(f"\n{Colors.GREEN}{'='*50}")
        print("✓ Setup completado!")
        print(f"{'='*50}{Colors.END}\n")
        
        print("Próximos pasos:")
        print("1. Añade tu RAPIDAPI_KEY en backend/.env")
        print("2. Inicia el backend: cd backend && source venv/bin/activate && uvicorn app.main:app --reload")
        print("3. Inicia el frontend: cd frontend && npm start")
        print("4. Accede a http://localhost:3000")
        
        print("\nDocumentación:")
        print("- API Docs: http://localhost:8000/docs")
        print("- GraphQL: http://localhost:8000/graphql")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Setup cancelado por el usuario{Colors.END}")
    except Exception as e:
        print(f"\n{Colors.RED}Error inesperado: {e}{Colors.END}")
        sys.exit(1)