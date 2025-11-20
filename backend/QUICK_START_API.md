# Quick Start - API REST

## ✅ Task 5 Completado

La API REST con FastAPI ha sido completamente implementada con todos los endpoints requeridos.

## Archivos Implementados

### 1. Aplicación Principal
- **`app/main.py`** - Aplicación FastAPI con CORS, manejo de excepciones y health checks

### 2. Endpoints
- **`app/api/v1/endpoints/documentos.py`** - Todos los endpoints de documentos:
  - Upload de documentos
  - Estado de tareas
  - Búsqueda semántica

### 3. Documentación
- **`API_REFERENCE.md`** - Referencia completa de la API
- **`TASK_5_COMPLETION_SUMMARY.md`** - Resumen detallado de implementación

## Endpoints Implementados

### Health Checks
- ✅ `GET /health` - Health check básico
- ✅ `GET /health/detailed` - Health check con verificación de servicios

### Documentos
- ✅ `POST /api/v1/documentos/upload` - Subir documento (PDF/JPG)
- ✅ `GET /api/v1/documentos/tasks/{task_id}` - Estado de procesamiento
- ✅ `POST /api/v1/documentos/search` - Búsqueda semántica

## Características Implementadas

### 5.1 Aplicación FastAPI Base ✅
- Configuración de CORS para desarrollo
- Manejo global de excepciones (ValidationError, Exception)
- Health checks básico y detallado
- Logging estructurado con structlog
- Eventos de startup/shutdown

### 5.2 Endpoint de Upload ✅
- Validación de tipo de archivo (PDF/JPG)
- Validación de tamaño (máx 50MB)
- Guardado temporal de archivos
- Encolado de tarea Celery
- Respuesta HTTP 202 con task_id

### 5.3 Endpoint de Estado de Tarea ✅
- Consulta de estado con AsyncResult
- Manejo de estados: pending, processing, completed, error
- Respuesta con progreso y resultado

### 5.4 Endpoint de Búsqueda Semántica ✅
- Generación de query embedding con AIService
- Búsqueda vectorial con pgvector (operador <=>)
- Filtros por tipo_documento, fecha_desde, fecha_hasta
- Paginación (page, page_size)
- Respuesta con relevance_score

## Cómo Iniciar la API

### Prerequisitos
```bash
# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales
```

### Iniciar Servidor
```bash
# Desarrollo (con auto-reload)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Producción
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Acceder a Documentación
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Pruebas Rápidas

### 1. Health Check
```bash
curl http://localhost:8000/health
```

### 2. Upload (requiere Celery)
```bash
curl -X POST http://localhost:8000/api/v1/documentos/upload \
  -F "file=@test.pdf"
```

### 3. Task Status
```bash
curl http://localhost:8000/api/v1/documentos/tasks/{task_id}
```

### 4. Search (requiere DB y Google API)
```bash
curl -X POST http://localhost:8000/api/v1/documentos/search \
  -H "Content-Type: application/json" \
  -d '{"query": "oficio", "page": 1, "page_size": 10}'
```

## Servicios Requeridos

Para funcionalidad completa, necesitas:

1. **PostgreSQL con pgvector** (puerto 5432)
   - Base de datos: sgd_ugel
   - Extensión pgvector instalada

2. **Redis** (puerto 6379)
   - Broker para Celery

3. **MinIO** (puerto 9000)
   - Almacenamiento de archivos
   - Bucket: documentos-ugel

4. **Celery Workers**
   ```bash
   celery -A app.workers.celery_app worker --loglevel=info
   ```

5. **Google API Key**
   - Para Gemini (metadatos)
   - Para text-embedding-004 (embeddings)

## Iniciar con Docker Compose

```bash
# Iniciar todos los servicios
docker-compose up -d

# Ver logs
docker-compose logs -f backend

# Detener servicios
docker-compose down
```

## Estructura de Respuestas

### Upload Response
```json
{
  "task_id": "uuid",
  "status": "processing",
  "message": "Documento encolado"
}
```

### Task Status Response
```json
{
  "task_id": "uuid",
  "status": "completed",
  "progress": 100,
  "documento_id": "uuid"
}
```

### Search Response
```json
{
  "results": [
    {
      "documento": { /* metadatos completos */ },
      "relevance_score": 0.234
    }
  ],
  "total": 15,
  "page": 1,
  "total_pages": 2
}
```

## Próximos Pasos

Con la API completada, puedes:

1. **Probar endpoints** con Swagger UI o curl
2. **Desarrollar frontend** (Task 6) que consuma esta API
3. **Configurar despliegue** (Task 7) con Docker Compose

## Troubleshooting

### Error: Module not found
```bash
pip install -r requirements.txt
```

### Error: Database connection
```bash
# Verificar que PostgreSQL esté corriendo
docker-compose ps postgres

# Verificar variables de entorno
cat .env | grep DATABASE_URL
```

### Error: Redis connection
```bash
# Verificar que Redis esté corriendo
docker-compose ps redis

# Probar conexión
redis-cli ping
```

### Error: Google API
```bash
# Verificar API key
cat .env | grep GOOGLE_API_KEY

# Verificar que la API esté habilitada en Google Cloud Console
```

## Soporte

Para más información, consulta:
- `API_REFERENCE.md` - Referencia completa de endpoints
- `TASK_5_COMPLETION_SUMMARY.md` - Detalles de implementación
- Swagger UI: http://localhost:8000/docs
