# API Documentation - SGD UGEL Ilo

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

Currently, the API does not require authentication (Phase 1 - MVP for internal network).

## Rate Limiting

- **Default**: 100 requests per minute per IP address
- **Configurable**: Set `RATE_LIMIT_PER_MINUTE` in `.env`

## Common Headers

```http
Content-Type: application/json
Accept: application/json
```

---

## Endpoints

### 1. Health Check

#### GET /health

Check if the API is running.

**Response: 200 OK**
```json
{
  "status": "healthy"
}
```

#### GET /health/detailed

Get detailed health status of all services.

**Response: 200 OK**
```json
{
  "status": "healthy",
  "checks": {
    "database": true,
    "redis": true,
    "minio": true,
    "celery": true
  }
}
```

**Response: 503 Service Unavailable** (if any service is down)
```json
{
  "status": "degraded",
  "checks": {
    "database": true,
    "redis": false,
    "minio": true,
    "celery": true
  }
}
```

---

### 2. Document Upload

#### POST /api/v1/documentos/upload

Upload a PDF or JPG document for processing.

**Request**

```http
POST /api/v1/documentos/upload
Content-Type: multipart/form-data

file: <binary file data>
```

**cURL Example**
```bash
curl -X POST http://localhost:8000/api/v1/documentos/upload \
  -F "file=@/path/to/document.pdf"
```

**Python Example**
```python
import requests

url = "http://localhost:8000/api/v1/documentos/upload"
files = {"file": open("document.pdf", "rb")}
response = requests.post(url, files=files)
print(response.json())
```

**Response: 202 Accepted**
```json
{
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "processing",
  "message": "Documento en cola de procesamiento"
}
```

**Validation Rules:**
- File type: `application/pdf` or `image/jpeg`
- Maximum size: 50MB (configurable via `MAX_UPLOAD_SIZE_MB`)
- File must not be empty

**Error Responses:**

**400 Bad Request** - Invalid file type
```json
{
  "error": "Invalid file type",
  "detail": "Only PDF and JPG files are supported",
  "timestamp": "2024-03-15T10:30:00Z",
  "request_id": "req_123456"
}
```

**413 Payload Too Large** - File too large
```json
{
  "error": "File too large",
  "detail": "Maximum file size is 50MB",
  "timestamp": "2024-03-15T10:30:00Z",
  "request_id": "req_123456"
}
```

---

### 3. Task Status

#### GET /api/v1/tasks/{task_id}

Get the status of a document processing task.

**Request**

```http
GET /api/v1/tasks/a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

**cURL Example**
```bash
curl http://localhost:8000/api/v1/tasks/a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

**Response: 200 OK** - Task in progress
```json
{
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "processing",
  "progress": 45,
  "current_step": "Extracting metadata",
  "documento_id": null,
  "error": null
}
```

**Response: 200 OK** - Task completed
```json
{
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "completed",
  "progress": 100,
  "current_step": "Completed",
  "documento_id": "doc_uuid_here",
  "error": null
}
```

**Response: 200 OK** - Task failed
```json
{
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "error",
  "progress": 30,
  "current_step": "OCR extraction",
  "documento_id": null,
  "error": "Failed to extract text from document"
}
```

**Status Values:**
- `pending`: Task is queued but not started
- `processing`: Task is being processed
- `completed`: Task completed successfully
- `error`: Task failed after all retries

---

### 4. Document Search

#### POST /api/v1/documentos/search

Search documents using semantic search.

**Request**

```http
POST /api/v1/documentos/search
Content-Type: application/json

{
  "query": "resoluciones directorales sobre permisos docentes",
  "filters": {
    "tipo_documento": "Resolución Directoral",
    "fecha_desde": "2024-01-01",
    "fecha_hasta": "2024-12-31"
  },
  "page": 1,
  "page_size": 10
}
```

**Request Body Schema:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| query | string | Yes | Search query in natural language (3-500 chars) |
| filters | object | No | Optional filters |
| filters.tipo_documento | string | No | Filter by document type |
| filters.fecha_desde | string | No | Filter by start date (YYYY-MM-DD) |
| filters.fecha_hasta | string | No | Filter by end date (YYYY-MM-DD) |
| page | integer | No | Page number (default: 1, min: 1) |
| page_size | integer | No | Results per page (default: 10, min: 1, max: 50) |

**cURL Example**
```bash
curl -X POST http://localhost:8000/api/v1/documentos/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "oficios sobre licencias",
    "page": 1,
    "page_size": 10
  }'
```

**Python Example**
```python
import requests

url = "http://localhost:8000/api/v1/documentos/search"
payload = {
    "query": "resoluciones directorales 2024",
    "filters": {
        "tipo_documento": "Resolución Directoral",
        "fecha_desde": "2024-01-01"
    },
    "page": 1,
    "page_size": 10
}
response = requests.post(url, json=payload)
print(response.json())
```

**Response: 200 OK**
```json
{
  "results": [
    {
      "documento": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "filename": "RD-001-2024.pdf",
        "tipo_documento": "Resolución Directoral",
        "tema_principal": "Designación de comisión evaluadora",
        "fecha_documento": "2024-03-15",
        "entidades_clave": [
          "UGEL Ilo",
          "Comisión Evaluadora",
          "Prof. Juan Pérez"
        ],
        "resumen_corto": "Resolución que designa a los miembros de la comisión evaluadora para el proceso de contratación docente 2024.",
        "minio_url": "http://localhost:9000/documentos-ugel/2024/uuid_RD-001-2024.pdf?X-Amz-...",
        "created_at": "2024-03-15T10:30:00Z",
        "status": "completed"
      },
      "relevance_score": 0.15
    },
    {
      "documento": {
        "id": "660e8400-e29b-41d4-a716-446655440001",
        "filename": "RD-002-2024.pdf",
        "tipo_documento": "Resolución Directoral",
        "tema_principal": "Aprobación de plan de trabajo",
        "fecha_documento": "2024-03-20",
        "entidades_clave": [
          "UGEL Ilo",
          "Dirección de Gestión Pedagógica"
        ],
        "resumen_corto": "Resolución que aprueba el plan de trabajo anual de la Dirección de Gestión Pedagógica.",
        "minio_url": "http://localhost:9000/documentos-ugel/2024/uuid_RD-002-2024.pdf?X-Amz-...",
        "created_at": "2024-03-20T14:15:00Z",
        "status": "completed"
      },
      "relevance_score": 0.23
    }
  ],
  "total": 25,
  "page": 1,
  "total_pages": 3
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| results | array | Array of search results |
| results[].documento | object | Document metadata |
| results[].relevance_score | float | Cosine similarity score (0-1, lower is more similar) |
| total | integer | Total number of matching documents |
| page | integer | Current page number |
| total_pages | integer | Total number of pages |

**Error Responses:**

**400 Bad Request** - Invalid query
```json
{
  "error": "Validation error",
  "detail": "Query must be between 3 and 500 characters",
  "timestamp": "2024-03-15T10:30:00Z",
  "request_id": "req_123456"
}
```

**422 Unprocessable Entity** - Invalid filters
```json
{
  "error": "Validation error",
  "detail": "Invalid date format. Use YYYY-MM-DD",
  "timestamp": "2024-03-15T10:30:00Z",
  "request_id": "req_123456"
}
```

---

### 5. Get Document by ID

#### GET /api/v1/documentos/{documento_id}

Get detailed information about a specific document.

**Request**

```http
GET /api/v1/documentos/550e8400-e29b-41d4-a716-446655440000
```

**Response: 200 OK**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "RD-001-2024.pdf",
  "tipo_documento": "Resolución Directoral",
  "tema_principal": "Designación de comisión evaluadora",
  "fecha_documento": "2024-03-15",
  "entidades_clave": [
    "UGEL Ilo",
    "Comisión Evaluadora",
    "Prof. Juan Pérez"
  ],
  "resumen_corto": "Resolución que designa a los miembros de la comisión evaluadora para el proceso de contratación docente 2024.",
  "minio_url": "http://localhost:9000/documentos-ugel/2024/uuid_RD-001-2024.pdf?X-Amz-...",
  "file_size_bytes": 2457600,
  "content_type": "application/pdf",
  "num_pages": 5,
  "created_at": "2024-03-15T10:30:00Z",
  "processed_at": "2024-03-15T10:31:30Z",
  "status": "completed"
}
```

**Response: 404 Not Found**
```json
{
  "error": "Document not found",
  "detail": "No document found with ID: 550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-03-15T10:30:00Z",
  "request_id": "req_123456"
}
```

---

### 6. List Documents

#### GET /api/v1/documentos

Get a paginated list of all documents.

**Request**

```http
GET /api/v1/documentos?page=1&page_size=20&tipo_documento=Oficio&status=completed
```

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| page | integer | No | Page number (default: 1) |
| page_size | integer | No | Results per page (default: 20, max: 100) |
| tipo_documento | string | No | Filter by document type |
| status | string | No | Filter by status (processing, completed, error) |
| fecha_desde | string | No | Filter by start date (YYYY-MM-DD) |
| fecha_hasta | string | No | Filter by end date (YYYY-MM-DD) |

**Response: 200 OK**
```json
{
  "documents": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "filename": "RD-001-2024.pdf",
      "tipo_documento": "Resolución Directoral",
      "tema_principal": "Designación de comisión evaluadora",
      "fecha_documento": "2024-03-15",
      "created_at": "2024-03-15T10:30:00Z",
      "status": "completed"
    }
  ],
  "total": 150,
  "page": 1,
  "total_pages": 8
}
```

---

## Error Handling

### Error Response Format

All errors follow this format:

```json
{
  "error": "Error type",
  "detail": "Detailed error message",
  "timestamp": "2024-03-15T10:30:00Z",
  "request_id": "req_123456"
}
```

### HTTP Status Codes

| Code | Description | Common Causes |
|------|-------------|---------------|
| 200 | OK | Request successful |
| 202 | Accepted | Async task created |
| 400 | Bad Request | Invalid input, validation failed |
| 404 | Not Found | Resource not found |
| 413 | Payload Too Large | File size exceeds limit |
| 422 | Unprocessable Entity | Invalid data format |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Service temporarily unavailable |

---

## Rate Limiting

The API implements rate limiting to prevent abuse:

- **Default**: 100 requests per minute per IP
- **Headers**: Rate limit info is included in response headers

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1710504600
```

When rate limit is exceeded:

**Response: 429 Too Many Requests**
```json
{
  "error": "Rate limit exceeded",
  "detail": "Maximum 100 requests per minute. Try again in 30 seconds.",
  "timestamp": "2024-03-15T10:30:00Z",
  "request_id": "req_123456"
}
```

---

## Pagination

All list endpoints support pagination:

**Request Parameters:**
- `page`: Page number (starts at 1)
- `page_size`: Number of results per page

**Response Format:**
```json
{
  "results": [...],
  "total": 150,
  "page": 1,
  "total_pages": 15,
  "page_size": 10
}
```

---

## Filtering

### Date Filters

Use ISO 8601 date format (YYYY-MM-DD):

```json
{
  "filters": {
    "fecha_desde": "2024-01-01",
    "fecha_hasta": "2024-12-31"
  }
}
```

### Document Type Filter

Common document types:
- `Oficio`
- `Oficio Múltiple`
- `Resolución Directoral`
- `Informe`
- `Solicitud`
- `Memorándum`
- `Carta`

---

## Webhooks (Future Feature)

Webhooks will be available in Phase 2 to notify external systems when:
- Document processing is completed
- Document processing fails
- New documents match specific criteria

---

## SDK Examples

### Python SDK

```python
import requests

class SGDClient:
    def __init__(self, base_url="http://localhost:8000/api/v1"):
        self.base_url = base_url
    
    def upload_document(self, file_path):
        url = f"{self.base_url}/documentos/upload"
        with open(file_path, "rb") as f:
            files = {"file": f}
            response = requests.post(url, files=files)
        return response.json()
    
    def get_task_status(self, task_id):
        url = f"{self.base_url}/tasks/{task_id}"
        response = requests.get(url)
        return response.json()
    
    def search_documents(self, query, filters=None, page=1, page_size=10):
        url = f"{self.base_url}/documentos/search"
        payload = {
            "query": query,
            "filters": filters or {},
            "page": page,
            "page_size": page_size
        }
        response = requests.post(url, json=payload)
        return response.json()

# Usage
client = SGDClient()

# Upload
result = client.upload_document("document.pdf")
task_id = result["task_id"]

# Check status
status = client.get_task_status(task_id)
print(status)

# Search
results = client.search_documents("resoluciones 2024")
for item in results["results"]:
    print(item["documento"]["tema_principal"])
```

### JavaScript/TypeScript SDK

```typescript
class SGDClient {
  constructor(private baseUrl: string = "http://localhost:8000/api/v1") {}

  async uploadDocument(file: File): Promise<any> {
    const formData = new FormData();
    formData.append("file", file);
    
    const response = await fetch(`${this.baseUrl}/documentos/upload`, {
      method: "POST",
      body: formData,
    });
    
    return response.json();
  }

  async getTaskStatus(taskId: string): Promise<any> {
    const response = await fetch(`${this.baseUrl}/tasks/${taskId}`);
    return response.json();
  }

  async searchDocuments(
    query: string,
    filters?: any,
    page: number = 1,
    pageSize: number = 10
  ): Promise<any> {
    const response = await fetch(`${this.baseUrl}/documentos/search`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        query,
        filters: filters || {},
        page,
        page_size: pageSize,
      }),
    });
    
    return response.json();
  }
}

// Usage
const client = new SGDClient();

// Upload
const file = document.querySelector('input[type="file"]').files[0];
const result = await client.uploadDocument(file);

// Search
const results = await client.searchDocuments("oficios 2024");
console.log(results);
```

---

## Testing

### Using cURL

```bash
# Health check
curl http://localhost:8000/health

# Upload document
curl -X POST http://localhost:8000/api/v1/documentos/upload \
  -F "file=@document.pdf"

# Check task status
curl http://localhost:8000/api/v1/tasks/TASK_ID

# Search documents
curl -X POST http://localhost:8000/api/v1/documentos/search \
  -H "Content-Type: application/json" \
  -d '{"query": "resoluciones 2024", "page": 1, "page_size": 10}'
```

### Using Postman

Import the OpenAPI spec from:
```
http://localhost:8000/openapi.json
```

Or access the interactive API docs:
```
http://localhost:8000/docs
```

---

## Support

For API support:
- Documentation: http://localhost:8000/docs
- Issues: [Repository URL]/issues
- Email: [Support email]
