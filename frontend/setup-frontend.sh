echo "🚀 Configurando Frontend de TikTok Creator Scout..."

# Instalar dependencias principales
echo "📦 Instalando dependencias de React..."
npm install react react-dom react-scripts

# Instalar dependencias de UI
echo "🎨 Instalando dependencias de UI..."
npm install recharts lucide-react

# Instalar Tailwind CSS
echo "💅 Instalando Tailwind CSS..."
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# Instalar otras utilidades
echo "🔧 Instalando utilidades..."
npm install axios

# Crear estructura de carpetas
echo "📁 Creando estructura de carpetas..."
mkdir -p src/components
mkdir -p src/services
mkdir -p src/pages
mkdir -p src/utils

# Crear archivo .env si no existe
if [ ! -f .env ]; then
    echo "⚙️ Creando archivo .env..."
    cat > .env << EOL
REACT_APP_API_URL=http://localhost:8000/api/v1
REACT_APP_GRAPHQL_URL=http://localhost:8000/graphql
EOL
fi

# Verificar que todos los archivos necesarios existen
echo "✅ Verificando archivos..."

# Lista de archivos necesarios
files_to_check=(
    "src/App.js"
    "src/index.js"
    "src/index.css"
    "src/components/Dashboard.js"
    "src/services/api.js"
    "public/index.html"
    "tailwind.config.js"
    "postcss.config.js"
)

missing_files=()

for file in "${files_to_check[@]}"; do
    if [ ! -f "$file" ]; then
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -eq 0 ]; then
    echo "✅ Todos los archivos necesarios están presentes"
else
    echo "⚠️ Archivos faltantes:"
    for file in "${missing_files[@]}"; do
        echo "   - $file"
    done
    echo ""
    echo "Por favor, crea estos archivos con el contenido proporcionado en la documentación"
fi

echo ""
echo "✨ Configuración del frontend completada!"
echo ""
echo "Próximos pasos:"
echo "1. Asegúrate de que todos los archivos estén en su lugar"
echo "2. Verifica que el backend esté corriendo en http://localhost:8000"
echo "3. Ejecuta: npm start"
echo "4. Abre http://localhost:3000 en tu navegador"