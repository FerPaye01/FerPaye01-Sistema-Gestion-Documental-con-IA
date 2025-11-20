# SGD - Sistema de Gestión Documental Inteligente

**Versión**: 2.0  
**Estado**: ✅ Producción  
**Última actualización**: Noviembre 2025

## 📋 Descripción

Sistema de Gestión Documental (SGD) inteligente que implementa búsqueda semántica con IA, extracción automática de metadatos, OCR y clasificación de documentos administrativos.

> 📚 **Documentación completa en la carpeta [`docs/`](docs/)**

## 🎯 Características Principales

- **Búsqueda Semántica**: Búsqueda vectorial con embeddings de Google AI
- **Extracción de Metadatos**: Clasificación automática con Gemini LLM
- **OCR Inteligente**: Extracción de texto de PDFs con Tesseract
- **Fragmentación Automática**: División de documentos en fragmentos procesables
- **Sistema de Auditoría**: Registro completo de cambios
- **API RESTful**: Endpoints documentados con Swagger
- **Frontend Moderno**: Interfaz React/Vite

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (React)                      │
│                   http://localhost:3000                  │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│              Backend API (FastAPI)                       │
│              http://localhost:8000                       │
├─────────────────────────────────────────────────────────┤
│  • Búsqueda Vectorial    • Metadatos    • OCR           │
│  • Embeddings            • Auditoría    • Almacenamiento│
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
   ┌────▼──┐  ┌─────▼──┐  ┌─────▼──┐
   │  BD   │  │ Redis  │  │ MinIO  │
   │  PG   │  │ Cache  │  │ Storage│
   └───────┘  └────────┘  └────────┘
```

## 🚀 Inicio Rápido

### Requisitos
- Docker & Docker Compose
- Python 3.11+ (para desarrollo local)
- Node.js 18+ (para frontend)

### Instalación

1. **Clonar repositorio**
```bash
git clone <repo-url>
cd proyecto-sgd
```

2. **Configurar variables de entorno**
```bash
cp backend/.env.example backend/.env
# Editar backend/.env con tus credenciales
```

3. **Iniciar servicios**
```bash
docker-compose up -d
```

4. **Acceder a la aplicación**
- Frontend: http://localhost:3000
- API: http://localhost:8000
- Docs: http://localhost:8000/docs

**Para más detalles, ver:** [docs/INSTALACION.md](docs/INSTALACION.md)

## 📁 Estructura del Proyecto

```
proyecto-sgd/
├── backend/
│   ├── app/
│   │   ├── api/v1/
│   │   │   ├── endpoints/
│   │   │   │   └── documentos.py      # Endpoints principales
│   │   │   └── router.py              # Rutas API
│   │   ├── models/
│   │   │   ├── base.py                # Base ORM
│   │   │   └── documento.py           # Modelos de datos
│   │   ├── services/
│   │   │   ├── ai_service.py          # Gemini LLM
│   │   │   ├── ocr_service.py         # Tesseract OCR
│   │   │   ├── text_service.py        # Procesamiento texto
│   │   │   └── storage_service.py     # MinIO
│   │   ├── workers/
│   │   │   ├── celery_app.py          # Celery config
│   │   │   └── tasks.py               # Tareas async
│   │   ├── main.py                    # App principal
│   │   ├── database.py                # Conexión BD
│   │   └── config.py                  # Configuración
│   ├── Dockerfile.simple
│   └── requirements.txt
├── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
├── docker-compose.yml                 # Orquestación
├── init-db-complete.sql               # Script BD
├── .kiro/
│   └── specs/sgd-enhancements/        # Especificaciones
└── README.md
```

## 🔧 Configuración

### Variables de Entorno (.env)

```env
# Database
DATABASE_URL=postgresql://sgd_user:sgd_pass@postgres:5432/sgd_ugel

# Redis & Celery
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0

# MinIO
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=documentos-ugel

# Google AI
GOOGLE_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.5-pro
EMBEDDING_MODEL=models/text-embedding-004

# App
API_BASE_URL=http://localhost:8000
ENVIRONMENT=development
```

## 📚 Documentación

| Documento | Descripción |
|-----------|-------------|
| [docs/COMIENZA_AQUI.md](docs/COMIENZA_AQUI.md) | Punto de entrada para todos |
| [docs/INSTALACION.md](docs/INSTALACION.md) | Guía de instalación paso a paso |
| [docs/API.md](docs/API.md) | Documentación completa de endpoints |
| [docs/ARQUITECTURA.md](docs/ARQUITECTURA.md) | Diseño y arquitectura del sistema |
| [docs/DESARROLLO.md](docs/DESARROLLO.md) | Guía para desarrolladores |
| [docs/REFERENCIA_RAPIDA.md](docs/REFERENCIA_RAPIDA.md) | Comandos y URLs esenciales |
| [docs/SEGURIDAD.md](docs/SEGURIDAD.md) | Guía de seguridad |
| [docs/INDICE.md](docs/INDICE.md) | Índice completo de documentación |

## 🔌 API Endpoints

**Para documentación completa de endpoints, ver:** [docs/API.md](docs/API.md)

### Ejemplos Rápidos

**Subir documento**
```bash
curl -X POST http://localhost:8000/api/v1/documentos/upload \
  -F "file=@documento.pdf"
```

**Buscar documentos**
```bash
curl -X POST http://localhost:8000/api/v1/documentos/search \
  -H "Content-Type: application/json" \
  -d '{"query": "resolución"}'
```

**Listar documentos**
```bash
curl http://localhost:8000/api/v1/documentos
```

## 🗄️ Base de Datos

### Tablas Principales

**documentos**
- Metadatos de documentos
- Clasificación automática
- Estado de procesamiento
- Auditoría de cambios

**fragmentos**
- Fragmentos de texto
- Embeddings vectoriales (768 dimensiones)
- Índices HNSW para búsqueda rápida

**audit_log**
- Historial de cambios
- Trazabilidad completa
- Información de usuario

## 🔍 Búsqueda Semántica

La búsqueda funciona mediante:

1. **Generación de embedding**: Query → Google AI → Vector (768 dims)
2. **Búsqueda vectorial**: Cosine similarity en PostgreSQL
3. **Filtrado**: Threshold de similitud (1.0)
4. **Ranking**: Ordenamiento por relevancia

## 🛠️ Desarrollo

### Backend

```bash
# Instalar dependencias
cd backend
pip install -r requirements.txt

# Ejecutar servidor
python -m uvicorn app.main:app --reload

# Ejecutar tests
pytest
```

### Frontend

```bash
# Instalar dependencias
cd frontend
npm install

# Ejecutar dev server
npm run dev

# Build producción
npm run build
```

## 📊 Monitoreo

### Health Check
```bash
curl http://localhost:8000/health
```

### Logs
```bash
docker-compose logs -f backend
docker-compose logs -f celery
```

### Base de Datos
```bash
docker exec sgd-postgres psql -U sgd_user -d sgd_ugel -c "\dt"
```

## 🚨 Troubleshooting

Para solucionar problemas comunes, ver:
- [docs/REFERENCIA_RAPIDA.md](docs/REFERENCIA_RAPIDA.md#-solución-rápida-de-problemas)
- [docs/INSTALACION.md](docs/INSTALACION.md#-solución-de-problemas)
- [docs/SEGURIDAD.md](docs/SEGURIDAD.md) (problemas de seguridad)


## 👥 Contacto

Para soporte o consultas, contactar al equipo de desarrollo.
