# SGD - Sistema de Gestión Documental Inteligente

📚 **Documentación completa en la carpeta [`docs/`](docs/)**

## 📙 Descripción

Sistema de Gestión Documental (SGD) inteligente que implementa búsqueda semántica con IA, extracción automática de metadatos, OCR y clasificación de documentos administrativos.

## � *Estado del Proyecto

Actualmente el proyecto se encuentra en **producción**. El sistema está completamente funcional y listo para desplegar. Se espera mejorar el proyecto con el paso del tiempo, aprendiendo nuevos patrones de diseño y nuevas formas de presentar la información.

**Versión**: 2.0  
**Última actualización**: Noviembre 2025

## 📌 Índice

- [Descripción](#-descripción)
- [Estado del Proyecto](#-estado-del-proyecto)
- [Características](#-características-principales)
- [Acceso al Proyecto](#-acceso-al-proyecto)
- [Tecnologías Utilizadas](#-tecnologías-utilizadas)
- [Personas Desarrolladoras](#-personas-desarrolladoras)
- [Licencia](#-licencia)

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

## � Acceiso al Proyecto

### Clonar el código fuente:
```bash
git clone https://github.com/FerPaye01/Sistema-de-Gesti-n-Documental-Inteligente.git
cd Sistema-de-Gesti-n-Documental-Inteligente
```

### Instalación rápida:
```bash
# 1. Configurar variables de entorno
cp backend/.env.example backend/.env

# 2. Instalar dependencias (opcional para desarrollo local)
cd backend && pip install -r requirements.txt
cd ../frontend && npm install

# 3. Iniciar servicios
docker-compose up -d

# 4. Acceder a la aplicación
# Frontend: http://localhost:3000
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

**Para instalación detallada, ver:** [docs/INSTALACION.md](docs/INSTALACION.md)

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

## � DTecnologías Utilizadas

**Backend:**
- FastAPI: Framework web Python
- PostgreSQL + pgvector: Base de datos con búsqueda vectorial
- SQLAlchemy: ORM para base de datos
- Celery: Cola de tareas asincrónicas
- Redis: Cache y broker de mensajes
- Google Gemini: Extracción de metadatos con IA
- Google Text Embedding: Generación de embeddings
- Tesseract: OCR para extracción de texto

**Frontend:**
- React: Librería de UI
- Vite: Build tool y dev server
- TypeScript: Tipado estático
- TailwindCSS: Framework de estilos
- Axios: Cliente HTTP

**Infraestructura:**
- Docker: Containerización
- Docker Compose: Orquestación de servicios
- MinIO: Almacenamiento de objetos

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

## 🧪 Prueba Final - Comandos Completos

### 1. Limpieza Completa
```bash
# Detener servicios y eliminar volúmenes
docker-compose down -v

# Eliminar imágenes
docker rmi proyecto-sgd-backend proyecto-sgd-frontend proyecto-sgd-celery

# Limpiar sistema Docker (opcional)
docker system prune -a -f
```

### 2. Reconstruir y Subir
```bash
# Reconstruir imágenes desde cero
docker-compose build --no-cache

# Iniciar servicios
docker-compose up -d

# Esperar a que todo esté listo (30 segundos)
Start-Sleep -Seconds 30
```

### 3. Verificar que Funciona
```bash
# Ver estado de servicios
docker-compose ps

# Health check del backend
curl http://localhost:8000/health

# Ver logs del backend
docker-compose logs backend --tail=20

# Ver logs de PostgreSQL
docker-compose logs postgres --tail=20
```

### 4. Acceder a la Aplicación
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **MinIO**: http://localhost:9001

### 5. Pruebas Rápidas
```bash
# Verificar base de datos
docker exec sgd-postgres psql -U sgd_user -d sgd_ugel -c "\dt"

# Verificar Redis
docker exec sgd-redis redis-cli ping

# Verificar MinIO
curl http://localhost:9000/minio/health/live
```

### 6. Detener Todo
```bash
# Detener servicios (sin borrar datos)
docker-compose stop

# Detener y borrar todo (incluyendo datos)
docker-compose down -v
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


## � ‍💻 Personas Desarrolladoras

**Oscar Fernando Paye Cahui** - Autor

- 🐙 GitHub: [@FerPaye01](https://github.com/FerPaye01)
- 💼 LinkedIn: [oscar-paye01](https://www.linkedin.com/in/oscar-paye01/)

## 📜 Licencia

Este proyecto está bajo la licencia MIT. Consulta el archivo LICENSE para más detalles.

---

**¿Preguntas o sugerencias?** Abre un issue en GitHub o contacta al equipo de desarrollo.
