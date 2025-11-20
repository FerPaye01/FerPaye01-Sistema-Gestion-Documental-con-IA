# SGD - Frontend

Sistema de Gestión Documental - Interfaz de Usuario

## Tecnologías

- **React 18+** - Biblioteca de UI
- **Vite** - Build tool y dev server
- **TypeScript** - Tipado estático
- **TailwindCSS** - Framework de estilos
- **react-pdf** - Visualización de documentos PDF
- **axios** - Cliente HTTP para API REST

## Estructura del Proyecto

```
src/
├── components/     # Componentes React reutilizables
├── services/       # Servicios de API y lógica de negocio
├── types/          # Definiciones de tipos TypeScript
├── App.tsx         # Componente principal
├── main.tsx        # Punto de entrada
└── index.css       # Estilos globales (TailwindCSS)
```

## Configuración

### Variables de Entorno

El frontend se conecta al backend a través del proxy configurado en `vite.config.ts`:
- Todas las peticiones a `/api` se redirigen a `http://backend:8000`

### Desarrollo Local

1. Instalar dependencias:
```bash
npm install
```

2. Iniciar servidor de desarrollo:
```bash
npm run dev
```

El servidor estará disponible en `http://localhost:3000`

### Build para Producción

```bash
npm run build
```

Los archivos optimizados se generarán en el directorio `dist/`

## Scripts Disponibles

- `npm run dev` - Inicia el servidor de desarrollo con hot reload
- `npm run build` - Compila TypeScript y genera build de producción
- `npm run preview` - Previsualiza el build de producción
- `npm run lint` - Ejecuta ESLint para verificar código

## Componentes Principales

### UploadComponent
Permite la carga de documentos PDF/JPG con drag & drop, validación y seguimiento de progreso.

### SearchComponent
Interfaz de búsqueda semántica con filtros y paginación de resultados.

### DocumentViewer
Visualizador de PDFs con controles de navegación, zoom, descarga e impresión.

## Integración con Backend

El frontend consume la API REST del backend:

- `POST /api/v1/documentos/upload` - Carga de documentos
- `GET /api/v1/tasks/{task_id}` - Estado de procesamiento
- `POST /api/v1/documentos/search` - Búsqueda semántica

Ver `src/services/api.ts` para la configuración del cliente HTTP.

## Diseño Responsivo

La aplicación está optimizada para:
- Desktop (1024px+)
- Tablet (768px - 1023px)
- Móvil (< 768px)

TailwindCSS proporciona utilidades responsivas con prefijos `sm:`, `md:`, `lg:`, `xl:`
