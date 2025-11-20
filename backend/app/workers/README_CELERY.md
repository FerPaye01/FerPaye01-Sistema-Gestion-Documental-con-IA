# Celery Workers - Procesamiento Asíncrono de Documentos

## Descripción General

Este módulo implementa el sistema de procesamiento asíncrono de documentos usando Celery con Redis como broker. El pipeline completo procesa documentos PDF y JPG, extrayendo texto, metadatos y generando embeddings para búsqueda semántica.

## Arquitectura

```
Usuario → FastAPI → Redis (Broker) → Celery Worker → PostgreSQL + MinIO
                                    ↓
                              Google AI APIs
                           (Gemini + Embeddings)
```

## Componentes

### 1. `celery_app.py`
Configuración principal de Celery:
- **Broker**: Redis para cola de mensajes
- **Backend**: Redis para almacenar resultados
- **Serialización**: JSON
- **Timezone**: America/Lima
- **Concurrency**: 2 workers por defecto
- **Reintentos**: Automáticos con backoff exponencial

### 2. `tasks.py`
Implementación de la tarea `process_document`:

#### Pipeline de Procesamiento

1. **Storage** (10%): Subir archivo a MinIO
2. **Text Extraction** (20%): OCR híbrido (PyMuPDF → pytesseract)
3. **Text Cleaning** (30%): Normalización y limpieza
4. **Chunking** (40%): Fragmentación con overlap de 100 caracteres
5. **Metadata Extraction** (50%): Llamada a Gemini LLM
6. **Database Insert** (60%): Crear registro de documento
7. **Embedding Generation** (60-90%): Generar embeddings para cada fragmento
8. **Finalization** (95%): Actualizar estado a 'completed'

#### Manejo de Errores

- **Max Retries**: 3 intentos
- **Retry Delays**: Exponencial (60s, 300s, 900s)
- **Error Logging**: Estructurado con stack traces
- **Estado en DB**: Actualiza documento a 'error' con mensaje descriptivo

#### Actualización de Progreso

La tarea actualiza su estado usando `self.update_state()`:
```python
self.update_state(
    state='PROGRESS',
    meta={'progress': 50, 'stage': 'Extrayendo metadatos con IA'}
)
```

Esto permite al frontend mostrar progreso en tiempo real consultando el endpoint `/api/v1/tasks/{task_id}`.

## Uso

### Iniciar Worker

```bash
# Desarrollo (1 worker, auto-reload)
celery -A app.workers.celery_app worker --loglevel=info --concurrency=2

# Producción (múltiples workers)
celery -A app.workers.celery_app worker --loglevel=warning --concurrency=4
```

### Monitorear Tareas

```bash
# Flower (interfaz web de monitoreo)
celery -A app.workers.celery_app flower

# Acceder a http://localhost:5555
```

### Encolar Tarea desde FastAPI

```python
from app.workers.tasks import process_document

# Encolar tarea
task = process_document.delay(temp_path, filename, content_type)

# Obtener task_id
task_id = task.id

# Consultar estado
from celery.result import AsyncResult
result = AsyncResult(task_id)
print(result.state)  # PENDING, PROGRESS, SUCCESS, FAILURE
print(result.info)   # Metadata (progress, stage, etc.)
```

## Configuración

Variables de entorno requeridas (`.env`):

```bash
# Redis
REDIS_URL=redis://redis:6379/0

# Celery
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Database
DATABASE_URL=postgresql://user:pass@postgres:5432/sgd_ugel

# MinIO
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=documentos-ugel
MINIO_SECURE=false

# Google AI
GOOGLE_API_KEY=your_api_key_here
```

## Verificación

Ejecutar script de verificación:

```bash
cd backend
python verify_celery.py
```

Este script verifica:
- ✓ Instancia de Celery configurada
- ✓ Configuración de broker y backend
- ✓ Tareas registradas
- ✓ Configuración de reintentos
- ✓ Configuración de progreso

## Logging

El sistema usa `structlog` para logging estructurado:

```python
logger.info(
    "document_processing_started",
    filename=filename,
    content_type=content_type,
    task_id=self.request.id
)
```

Logs incluyen:
- `document_processing_started`: Inicio de procesamiento
- `storage_upload_completed`: Archivo subido a MinIO
- `text_extraction_completed`: Texto extraído
- `metadata_extraction_completed`: Metadatos extraídos
- `embedding_generation_completed`: Embeddings generados
- `document_processing_completed`: Procesamiento exitoso
- `document_processing_failed`: Error en procesamiento

## Troubleshooting

### Worker no se conecta a Redis

```bash
# Verificar que Redis esté corriendo
docker-compose ps redis

# Verificar conectividad
redis-cli -h localhost -p 6379 ping
```

### Tareas quedan en PENDING

- Verificar que el worker esté corriendo
- Verificar que el worker tenga acceso a las mismas variables de entorno
- Revisar logs del worker para errores

### Errores de importación

```bash
# Asegurarse de que el PYTHONPATH incluya el directorio backend
export PYTHONPATH="${PYTHONPATH}:/path/to/backend"
```

### Memory leaks

El worker se reinicia automáticamente cada 50 tareas (`worker_max_tasks_per_child=50`) para prevenir memory leaks.

## Métricas y Monitoreo

### Métricas Clave

- **Throughput**: Documentos procesados por minuto
- **Latency**: Tiempo promedio de procesamiento
- **Error Rate**: Porcentaje de tareas fallidas
- **Queue Length**: Número de tareas pendientes

### Flower Dashboard

Acceder a `http://localhost:5555` para ver:
- Tareas activas, completadas y fallidas
- Gráficos de throughput
- Estado de workers
- Logs en tiempo real

## Escalabilidad

### Horizontal Scaling

Agregar más workers:

```bash
# Worker 1
celery -A app.workers.celery_app worker --loglevel=info --concurrency=2 -n worker1@%h

# Worker 2
celery -A app.workers.celery_app worker --loglevel=info --concurrency=2 -n worker2@%h
```

### Vertical Scaling

Aumentar concurrency por worker:

```bash
celery -A app.workers.celery_app worker --loglevel=info --concurrency=4
```

**Nota**: Cada tarea consume recursos significativos (llamadas a Google AI), por lo que se recomienda concurrency=2-4 por worker.

## Seguridad

- **API Keys**: Nunca hardcodear, usar variables de entorno
- **Rate Limiting**: Google AI tiene límites de rate, el sistema reintenta automáticamente
- **Validación**: Todos los inputs son validados antes de procesamiento
- **Cleanup**: Archivos temporales se eliminan después de procesamiento

## Referencias

- [Celery Documentation](https://docs.celeryq.dev/)
- [Redis Documentation](https://redis.io/docs/)
- [Flower Documentation](https://flower.readthedocs.io/)
