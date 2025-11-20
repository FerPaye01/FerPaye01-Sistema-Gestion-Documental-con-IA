# Arquitectura - SGD UGEL Ilo

## 🏗️ Visión General

```
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND (React/Vite)                    │
│                    http://localhost:3000                     │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/REST
┌────────────────────────▼────────────────────────────────────┐
│                  BACKEND API (FastAPI)                       │
│                 http://localhost:8000                        │
├─────────────────────────────────────────────────────────────┤
│  Endpoints:                                                  │
│  • POST   /documentos/upload      - Subir documento         │
│  • GET    /documentos/tasks/{id}  - Estado procesamiento    │
│  • GET    /documentos             - Listar documentos       │
│  • POST   /documentos/search      - Búsqueda semántica      │
│  • GET    /documentos/{id}        - Obtener documento       │
│  • DELETE /documentos/{id}        - Eliminar documento      │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
   ┌────▼──────┐  ┌─────▼──────┐  ┌─────▼──────┐
   │ PostgreSQL │  │   Redis    │  │   MinIO    │
   │ + pgvector │  │   Cache    │  │  Storage   │
   │            │  │   Broker   │  │            │
   └────────────┘  └────────────┘  └────────────┘
        │                │
        │                └──────────────┐
        │                               │
   ┌────▼──────────────────────────────▼──────┐
   │         CELERY WORKER (Async Tasks)      │
   ├──────────────────────────────────────────┤
   │ • OCR (Tesseract)                        │
   │ • Extracción de metadatos (Gemini)      │
   │ • Generación de embeddings (Google AI)  │
   │ • Fragmentación de texto                │
   └──────────────────────────────────────────┘
```

## 📊 Flujo de Procesamiento de Documentos

```
1. UPLOAD
   └─ Usuario sube PDF
   └─ Validación de archivo
   └─ Almacenamiento temporal
   └─ Creación de tarea Celery
   └─ Respuesta: task_id

2. PROCESAMIENTO (Celery Worker)
   ├─ OCR (Tesseract)
   │  └─ Extrae texto del PDF
   │
   ├─ Metadatos (Gemini LLM)
   │  ├─ Clasificación (tipo_documento)
   │  ├─ Tema principal
   │  ├─ Fecha del documento
   │  ├─ Entidades clave
   │  └─ Resumen corto
   │
   ├─ Fragmentación
   │  ├─ División en chunks (800 caracteres)
   │  ├─ Overlap (100 caracteres)
   │  └─ Posicionamiento
   │
   ├─ Embeddings (Google AI)
   │  ├─ Generación de vectores (768 dims)
   │  ├─ Almacenamiento en BD
   │  └─ Indexación HNSW
   │
   └─ Almacenamiento
      ├─ Documento en MinIO
      ├─ Metadatos en PostgreSQL
      ├─ Fragmentos en PostgreSQL
      └─ Auditoría en audit_log

3. BÚSQUEDA
   ├─ Query del usuario
   ├─ Generación de embedding (Google AI)
   ├─ Búsqueda vectorial (cosine similarity)
   ├─ Filtrado por threshold (1.0)
   ├─ Ranking por relevancia
   └─ Respuesta con resultados
```

## 🗄️ Modelo de Datos

### Tabla: documentos
```sql
CREATE TABLE documentos (
    id UUID PRIMARY KEY,
    filename VARCHAR(255),
    minio_url TEXT,
    minio_object_name VARCHAR(500),
    
    -- Metadatos extraídos
    tipo_documento VARCHAR(100),
    tema_principal TEXT,
    fecha_documento DATE,
    entidades_clave TEXT[],
    resumen_corto TEXT,
    
    -- Sistema
    file_size_bytes BIGINT,
    content_type VARCHAR(50),
    num_pages INTEGER,
    
    -- Timestamps
    upload_timestamp TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE,
    processed_at TIMESTAMP,
    
    -- Estado
    status VARCHAR(20),  -- processing, completed, error
    error_message TEXT,
    created_by VARCHAR(100)
);
```

### Tabla: fragmentos
```sql
CREATE TABLE fragmentos (
    id UUID PRIMARY KEY,
    documento_id UUID REFERENCES documentos(id) ON DELETE CASCADE,
    
    -- Contenido
    texto TEXT,
    posicion INTEGER,
    
    -- Vector embedding (768 dimensiones)
    embedding vector(768),
    
    created_at TIMESTAMP
);

-- Índice HNSW para búsqueda rápida
CREATE INDEX idx_fragmentos_embedding ON fragmentos 
USING hnsw (embedding vector_cosine_ops);
```

### Tabla: audit_log
```sql
CREATE TABLE audit_log (
    id UUID PRIMARY KEY,
    documento_id UUID REFERENCES documentos(id) ON DELETE CASCADE,
    
    action VARCHAR(20),  -- CREATE, UPDATE, DELETE
    old_values JSONB,
    new_values JSONB,
    user_id VARCHAR(100),
    
    timestamp TIMESTAMP WITH TIME ZONE
);
```

## 🔄 Componentes Principales

### Backend (FastAPI)

**Estructura:**
```
backend/app/
├── api/v1/
│   ├── endpoints/
│   │   └── documentos.py      # Lógica de endpoints
│   └── router.py              # Rutas
├── models/
│   ├── base.py                # Base ORM
│   └── documento.py           # Modelos SQLAlchemy
├── services/
│   ├── ai_service.py          # Gemini LLM
│   ├── ocr_service.py         # Tesseract OCR
│   ├── text_service.py        # Procesamiento texto
│   └── storage_service.py     # MinIO
├── workers/
│   ├── celery_app.py          # Configuración Celery
│   └── tasks.py               # Tareas async
├── main.py                    # Aplicación FastAPI
├── database.py                # Conexión BD
└── config.py                  # Configuración
```

### Servicios Clave

#### ai_service.py
- Integración con Google Gemini
- Extracción de metadatos
- Generación de embeddings

#### ocr_service.py
- Extracción de texto con Tesseract
- Procesamiento de PDFs
- Validación de contenido

#### text_service.py
- Fragmentación de texto
- Limpieza y normalización
- Procesamiento de chunks

#### storage_service.py
- Integración con MinIO
- Almacenamiento de archivos
- Gestión de URLs

### Frontend (React/Vite)

**Características:**
- Interfaz moderna y responsiva
- Búsqueda en tiempo real
- Visualización de documentos
- Gestión de uploads

## 🔐 Seguridad

### Autenticación
- Actualmente: Sin autenticación (desarrollo)
- Producción: Implementar JWT o OAuth2

### Validación
- Validación de tipos con Pydantic
- Validación de archivos (tipo, tamaño)
- Sanitización de inputs

### Base de Datos
- Credenciales en variables de entorno
- Conexiones con SSL (producción)
- Backups automáticos

## 📈 Escalabilidad

### Horizontal
- Múltiples workers Celery
- Load balancer para API
- Réplicas de PostgreSQL

### Vertical
- Aumentar recursos de contenedores
- Optimizar índices de BD
- Caché con Redis

## 🔍 Búsqueda Vectorial

### Proceso
1. **Query embedding**: Convertir texto a vector (768 dims)
2. **Similarity search**: Buscar vectores similares
3. **Ranking**: Ordenar por similitud (cosine distance)
4. **Filtering**: Aplicar threshold (1.0)

### Índices
- HNSW (Hierarchical Navigable Small World)
- Optimizado para búsqueda rápida
- Escalable a millones de vectores

### Performance
- Búsqueda: ~100ms para 10K documentos
- Indexación: ~50ms por documento
- Memoria: ~3GB para 100K documentos

## 🚀 Deployment

### Desarrollo
```bash
docker-compose up -d
```

### Producción
- Usar docker-compose con configuración de prod
- Configurar HTTPS/SSL
- Implementar autenticación
- Configurar backups automáticos
- Monitoreo y alertas

## 📊 Monitoreo

### Métricas Clave
- Documentos procesados
- Tiempo de procesamiento
- Errores de OCR
- Latencia de búsqueda
- Uso de recursos

### Logs
- Structured logging con JSON
- Niveles: DEBUG, INFO, WARNING, ERROR
- Centralización con ELK (opcional)

## 🔧 Configuración

### Variables de Entorno
```env
# Database
DATABASE_URL=postgresql://...

# Redis
REDIS_URL=redis://...

# MinIO
MINIO_ENDPOINT=...
MINIO_ACCESS_KEY=...
MINIO_SECRET_KEY=...

# Google AI
GOOGLE_API_KEY=...
GEMINI_MODEL=gemini-2.5-pro
EMBEDDING_MODEL=models/text-embedding-004

# App
API_BASE_URL=http://localhost:8000
ENVIRONMENT=development
```

## 📚 Tecnologías

| Componente | Tecnología |
|-----------|-----------|
| Backend | FastAPI, Python 3.11 |
| Frontend | React, Vite, TypeScript |
| Base de Datos | PostgreSQL 15 + pgvector |
| Cache | Redis 7 |
| Storage | MinIO |
| Task Queue | Celery |
| OCR | Tesseract |
| LLM | Google Gemini |
| Embeddings | Google Text Embedding |
| Orquestación | Docker Compose |

## 🔄 Ciclo de Vida del Documento

```
NUEVO
  ↓
UPLOAD → VALIDACIÓN → PROCESAMIENTO → INDEXACIÓN → COMPLETADO
                           ↓
                        ERROR → RETRY
```

## 📝 Notas de Arquitectura

- **Asincronía**: Celery para tareas largas
- **Escalabilidad**: Diseño modular y desacoplado
- **Resiliencia**: Reintentos automáticos
- **Auditoría**: Registro completo de cambios
- **Performance**: Índices optimizados y caché
