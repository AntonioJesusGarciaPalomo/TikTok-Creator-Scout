# Frontend - TikTok Creator Scout

## 📁 Ubicación de Archivos

### 1. **Dashboard Component**
- **Archivo**: `src/components/Dashboard.js`
- **Contenido**: El código completo del Dashboard React que te proporcioné
- **Descripción**: Componente principal que muestra todas las métricas y gráficos

### 2. **App Component**
- **Archivo**: `src/App.js`
- **Contenido**:
```javascript
import React from 'react';
import Dashboard from './components/Dashboard';
import './index.css';

function App() {
  return (
    <div className="App">
      <Dashboard />
    </div>
  );
}

export default App;
```

### 3. **Index (Punto de entrada)**
- **Archivo**: `src/index.js`
- **Contenido**:
```javascript
import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

### 4. **Estilos CSS**
- **Archivo**: `src/index.css`
- **Contenido**:
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

/* Estilos adicionales aquí */
```

### 5. **API Service**
- **Archivo**: `src/services/api.js`
- **Contenido**: El servicio API que maneja todas las llamadas HTTP

### 6. **HTML Principal**
- **Archivo**: `public/index.html`
- **Contenido**: El HTML base con el div root

### 7. **Configuración de Tailwind**
- **Archivo**: `tailwind.config.js` (en la raíz del frontend)
- **Contenido**: La configuración de Tailwind CSS

### 8. **PostCSS Config**
- **Archivo**: `postcss.config.js` (en la raíz del frontend)
- **Contenido**: Configuración para procesar Tailwind

### 9. **Variables de Entorno**
- **Archivo**: `.env` (en la raíz del frontend)
- **Contenido**:
```
REACT_APP_API_URL=http://localhost:8000/api/v1
REACT_APP_GRAPHQL_URL=http://localhost:8000/graphql
```

## 🛠️ Pasos de Instalación

1. **Navega a la carpeta frontend**:
   ```bash
   cd frontend
   ```

2. **Crea todos los archivos necesarios** con el contenido proporcionado

3. **Instala las dependencias**:
   ```bash
   npm install
   ```

4. **Verifica que el backend esté corriendo** en http://localhost:8000

5. **Inicia el frontend**:
   ```bash
   npm start
   ```

## 📂 Estructura Final

```
frontend/
├── public/
│   ├── index.html
│   └── favicon.ico
├── src/
│   ├── components/
│   │   └── Dashboard.js    ← AQUÍ VA EL CÓDIGO PRINCIPAL DEL DASHBOARD
│   ├── services/
│   │   └── api.js         ← Servicio para llamadas API
│   ├── App.js             ← Componente raíz
│   ├── index.js           ← Punto de entrada
│   └── index.css          ← Estilos con Tailwind
├── .env                   ← Variables de entorno
├── package.json
├── tailwind.config.js     ← Configuración de Tailwind
├── postcss.config.js      ← Configuración de PostCSS
└── README.md

```

## 🎯 Componentes Opcionales

Si quieres dividir el Dashboard en componentes más pequeños:

### CreatorCard Component
- **Archivo**: `src/components/CreatorCard.js`
- **Uso**: Para mostrar información individual de cada creador

### FilterPanel Component
- **Archivo**: `src/components/FilterPanel.js`
- **Uso**: Panel de filtros como componente separado

### Charts Component
- **Archivo**: `src/components/Charts.js`
- **Uso**: Todos los gráficos en un componente separado

## 🚨 Solución de Problemas

### Error: "Module not found"
- Verifica que todos los archivos estén en las ubicaciones correctas
- Asegúrate de haber instalado todas las dependencias con `npm install`

### Error: "Cannot connect to API"
- Verifica que el backend esté corriendo en http://localhost:8000
- Revisa el archivo `.env` para confirmar las URLs

### Tailwind CSS no funciona
- Asegúrate de tener `tailwind.config.js` y `postcss.config.js`
- Verifica que `@tailwind` esté importado en `index.css`

## 🔄 Actualización de Datos

Para actualizar los datos en el Dashboard:

1. El Dashboard se actualiza automáticamente al cargar
2. Puedes añadir un botón de refresh:
```javascript
<button onClick={fetchData}>
  Actualizar Datos
</button>
```

3. Para scraping de nuevos creadores, usa la API GraphQL o REST desde el backend