# API Reference - SGD UGEL Ilo

## Base URL
```
http://localhost:8000
```

## Endpoints

### Health Checks

#### GET /health
Basic health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "sgd-ugel-api"
}
```

#### GET /health/detailed
Detailed health check with service dependencies.

**Response:**
```json
{
  "status": "healthy",
  "service": "sgd-ugel-api",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "checks": {
    "database": true,
    "redis": true,
    "minio": true,
    "celery": true
  }
}
```

**Status Codes:**
- `200 OK` - All services healthy
- `503 Service Unavailable` - One or more services degraded

---

### Document Management

#### POST /api/v1/documentos/upload
Upload a document (PDF or JPG) for processing.

**Request:**
- Content-Type: `multipart/form-data`
- Body: `file` (PDF or JPG, max 50MB)

**Response (202 Accepted):**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "message": "Documento 'ejemplo.pdf' encolado para procesamiento"
}
```

**Error Responses:**
- `400 Bad Request` - Invalid file type
- `413 Request Entity Too Large` - File exceeds 50MB
- `500 Internal Server Error` - Server error

**Example (curl):**
```bash
curl -X POST http://localhost:8000/api/v1/documentos/upload \
  -F "file=@documento.pdf"
```

---

#### GET /api/v1/documentos/tasks/{task_id}
Get the status of a document processing task.

**Parameters:**
- `task_id` (path) - Task ID returned from upload endpoint

**Response:**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "progress": 100,
  "documento_id": "660e8400-e29b-41d4-a716-446655440001"
}
```

**Status Values:**
- `pending` - Task not started yet
- `processing` - Task in progress
- `completed` - Task completed successfully
- `error` - Task failed

**Example (curl):**
```bash
curl http://localhost:8000/api/v1/documentos/tasks/550e8400-e29b-41d4-a716-446655440000
```

---

#### POST /api/v1/documentos/search
Semantic search for documents.

**Request:**
```json
{
  "query": "oficio múltiple sobre licencias",
  "filters": {
    "tipo_documento": "Oficio Múltiple",
    "fecha_desde": "2024-01-01",
    "fecha_hasta": "2024-12-31"
  },
  "page": 1,
  "page_size": 10
}
```

**Request Fields:**
- `query` (required, string, 3-500 chars) - Search query
- `filters` (optional, object) - Search filters
  - `tipo_documento` (optional, string) - Document type filter
  - `fecha_desde` (optional, date) - Start date filter (YYYY-MM-DD)
  - `fecha_hasta` (optional, date) - End date filter (YYYY-MM-DD)
- `page` (optional, integer, default: 1) - Page number
- `page_size` (optional, integer, default: 10, max: 50) - Results per page

**Response:**
```json
{
  "results": [
    {
      "documento": {
        "id": "660e8400-e29b-41d4-a716-446655440001",
        "filename": "oficio_001_2024.pdf",
        "minio_url": "https://minio.example.com/...",
        "tipo_documento": "Oficio Múltiple",
        "tema_principal": "Licencias por motivos personales",
        "fecha_documento": "2024-03-15",
        "entidades_clave": ["Dirección Regional", "UGEL Ilo"],
        "resumen_corto": "Oficio que establece procedimientos para solicitud de licencias...",
        "file_size_bytes": 1048576,
        "content_type": "application/pdf",
        "num_pages": 3,
        "created_at": "2024-03-15T10:30:00.000Z",
        "processed_at": "2024-03-15T10:31:00.000Z",
        "status": "completed",
        "error_message": null
      },
      "relevance_score": 0.234
    }
  ],
  "total": 15,
  "page": 1,
  "total_pages": 2
}
```

**Response Fields:**
- `results` (array) - List of search results
  - `documento` (object) - Document metadata
  - `relevance_score` (float) - Cosine distance (0-2, lower = more similar)
- `total` (integer) - Total number of results
- `page` (integer) - Current page number
- `total_pages` (integer) - Total number of pages

**Error Responses:**
- `422 Unprocessable Entity` - Invalid query (too short, invalid filters)
- `500 Internal Server Error` - Search error

**Example (curl):**
```bash
curl -X POST http://localhost:8000/api/v1/documentos/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "resolución directoral",
    "page": 1,
    "page_size": 10
  }'
```

**Example with filters (curl):**
```bash
curl -X POST http://localhost:8000/api/v1/documentos/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "oficio múltiple",
    "filters": {
      "tipo_documento": "Oficio Múltiple",
      "fecha_desde": "2024-01-01",
      "fecha_hasta": "2024-12-31"
    },
    "page": 1,
    "page_size": 10
  }'
```

---

## Error Response Format

All error responses follow this structure:

```json
{
  "error": "Error Type",
  "detail": "Detailed error message or validation errors",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "path": "/api/v1/documentos/search"
}
```

---

## CORS Configuration

The API allows requests from:
- `http://localhost:3000` (React development server)
- `http://localhost:5173` (Vite development server)

All HTTP methods and headers are allowed for development.

---

## Interactive Documentation

The API provides interactive documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These interfaces allow you to:
- View all endpoints and their schemas
- Test endpoints directly from the browser
- Download OpenAPI specification

---

## Authentication

Currently, the API does not require authentication (Phase 1 - MVP).

Future phases will implement:
- Phase 2: JWT-based authentication
- Phase 3: Active Directory/LDAP integration

---

## Rate Limiting

No rate limiting is currently implemented at the API level.

Google AI API calls have internal rate limiting with automatic retries:
- Max retries: 3
- Backoff: Exponential (2s, 4s, 8s)

---

## Logging

All requests and errors are logged using structured logging (structlog).

Log format:
```json
{
  "event": "search_request_received",
  "query": "oficio múltiple",
  "filters": {...},
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

---

## Performance Targets

- Search response time: p95 < 3s, p99 < 5s
- Upload response time: p95 < 2s (enqueuing only)
- Concurrent users: 50 without degradation
- Document processing: 10 docs/minute with 3 workers
