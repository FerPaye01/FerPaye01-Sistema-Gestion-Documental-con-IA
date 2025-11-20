# Upload Endpoint Documentation

## Overview

The upload endpoint implements the document ingestion flow (Flujo 1) as an asynchronous process using Celery. This ensures the API remains responsive while documents are processed in the background.

## Endpoint: POST /api/v1/documentos/upload

### Description

Uploads a document (PDF or JPG) and queues it for asynchronous processing. The endpoint immediately returns HTTP 202 Accepted with a task ID for tracking.

### Request

**Method:** `POST`  
**URL:** `/api/v1/documentos/upload`  
**Content-Type:** `multipart/form-data`

**Parameters:**
- `file` (required): PDF or JPG file (max 50MB)

**Example using cURL:**
```bash
curl -X POST "http://localhost:8000/api/v1/documentos/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@documento.pdf"
```

**Example using Python requests:**
```python
import requests

with open("documento.pdf", "rb") as f:
    files = {"file": f}
    response = requests.post(
        "http://localhost:8000/api/v1/documentos/upload",
        files=files
    )
    
print(response.json())
```

**Example using JavaScript fetch:**
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);

const response = await fetch('http://localhost:8000/api/v1/documentos/upload', {
  method: 'POST',
  body: formData
});

const data = await response.json();
console.log(data);
```

### Response

**Status Code:** `202 Accepted`

**Response Body:**
```json
{
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "processing",
  "message": "Documento 'documento.pdf' encolado para procesamiento"
}
```

**Fields:**
- `task_id` (string): Unique identifier for the Celery task
- `status` (string): Current status ("processing")
- `message` (string): Human-readable message

### Error Responses

#### 400 Bad Request - Invalid File Type
```json
{
  "detail": "Tipo de archivo no soportado. Tipos permitidos: application/pdf, image/jpeg, image/jpg"
}
```

#### 413 Request Entity Too Large - File Too Large
```json
{
  "detail": "Archivo demasiado grande. Tamaño máximo: 50MB"
}
```

#### 422 Unprocessable Entity - Missing File
```json
{
  "detail": [
    {
      "loc": ["body", "file"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

#### 500 Internal Server Error
```json
{
  "detail": "Error interno al procesar la solicitud"
}
```

## Endpoint: GET /api/v1/documentos/tasks/{task_id}

### Description

Retrieves the status of a document processing task.

### Request

**Method:** `GET`  
**URL:** `/api/v1/documentos/tasks/{task_id}`

**Path Parameters:**
- `task_id` (required): Task ID returned by the upload endpoint

**Example:**
```bash
curl "http://localhost:8000/api/v1/documentos/tasks/a1b2c3d4-e5f6-7890-abcd-ef1234567890"
```

### Response

**Status Code:** `200 OK`

**Response Body (Processing):**
```json
{
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "processing",
  "progress": 45
}
```

**Response Body (Completed):**
```json
{
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "completed",
  "progress": 100,
  "documento_id": "f1e2d3c4-b5a6-7890-1234-567890abcdef"
}
```

**Response Body (Error):**
```json
{
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "error",
  "error": "No se pudo extraer texto suficiente del documento"
}
```

**Fields:**
- `task_id` (string): Task identifier
- `status` (string): Task status ("pending", "processing", "completed", "error")
- `progress` (integer, optional): Progress percentage (0-100)
- `documento_id` (UUID, optional): Document ID (only when completed)
- `error` (string, optional): Error message (only when failed)

## Processing Pipeline (Flujo 1)

When a document is uploaded, the following pipeline is executed asynchronously:

1. **Storage** (10%): Upload file to MinIO
2. **Text Extraction** (20%): OCR hybrid (PyMuPDF → pytesseract)
3. **Text Cleaning** (30%): Normalization and cleaning
4. **Chunking** (40%): Fragmentation with overlap
5. **Metadata Extraction** (50%): Gemini LLM call
6. **Database Insert** (60%): Create document record
7. **Embedding Generation** (60-90%): Generate embeddings for each chunk
8. **Finalization** (95%): Update document status to completed

## Validation Rules

### File Type
- **Allowed:** `application/pdf`, `image/jpeg`, `image/jpg`
- **Rejected:** All other MIME types

### File Size
- **Maximum:** 50MB (52,428,800 bytes)
- **Minimum:** No explicit minimum (but must contain extractable text)

### File Content
- PDF files must be readable (not corrupted)
- Images must be in valid JPEG format
- Documents must contain at least 10 characters of extractable text

## Implementation Details

### Asynchronous Processing

The endpoint uses Celery for asynchronous processing:

```python
# Queue task (non-blocking)
task = process_document.apply_async(
    args=[temp_path, filename, content_type]
)

# Return immediately with task ID
return UploadResponse(
    task_id=task.id,
    status="processing",
    message=f"Documento '{filename}' encolado para procesamiento"
)
```

### Temporary File Handling

Files are saved temporarily before processing:

1. File is uploaded via multipart/form-data
2. Content is read into memory for validation
3. File is saved to `/tmp/sgd-uploads/` with unique name
4. Celery task processes the file
5. Temporary file is deleted after processing (success or failure)

### Error Handling

The endpoint implements comprehensive error handling:

- **Validation errors:** Return 400/413/422 with descriptive messages
- **Processing errors:** Logged and handled by Celery task
- **Retry logic:** Celery task retries up to 3 times with exponential backoff
- **Cleanup:** Temporary files are always deleted

## Monitoring and Logging

All operations are logged using structured logging (structlog):

```python
logger.info(
    "document_processing_task_queued",
    filename=filename,
    task_id=task.id,
    file_size_bytes=file_size_bytes
)
```

Log events include:
- `file_saved_temporarily`: File saved to temp directory
- `document_processing_task_queued`: Task queued successfully
- `invalid_file_type`: Invalid file type rejected
- `file_too_large`: File size exceeded
- `upload_endpoint_error`: Unexpected error

## Testing

Run the verification script:

```bash
cd backend
python verify_upload_endpoint.py
```

This tests:
- ✓ Endpoint exists at correct path
- ✓ File type validation
- ✓ File size validation
- ✓ Successful upload returns 202
- ✓ Task ID is returned
- ✓ Task status endpoint works

## Integration with Frontend

### React Example

```typescript
async function uploadDocument(file: File) {
  const formData = new FormData();
  formData.append('file', file);
  
  try {
    const response = await fetch('/api/v1/documentos/upload', {
      method: 'POST',
      body: formData
    });
    
    if (response.status === 202) {
      const data = await response.json();
      // Start polling for status
      pollTaskStatus(data.task_id);
    } else {
      const error = await response.json();
      console.error('Upload failed:', error.detail);
    }
  } catch (error) {
    console.error('Network error:', error);
  }
}

async function pollTaskStatus(taskId: string) {
  const interval = setInterval(async () => {
    const response = await fetch(`/api/v1/documentos/tasks/${taskId}`);
    const data = await response.json();
    
    if (data.status === 'completed') {
      clearInterval(interval);
      console.log('Document processed:', data.documento_id);
    } else if (data.status === 'error') {
      clearInterval(interval);
      console.error('Processing failed:', data.error);
    } else {
      console.log('Progress:', data.progress + '%');
    }
  }, 2000); // Poll every 2 seconds
}
```

## Security Considerations

1. **File Type Validation:** Only PDF and JPG files are accepted
2. **File Size Limit:** 50MB maximum to prevent DoS attacks
3. **Temporary File Cleanup:** Files are deleted after processing
4. **Error Messages:** Generic error messages to avoid information leakage
5. **CORS:** Configured to allow only frontend origin

## Future Enhancements

- [ ] Add authentication/authorization
- [ ] Implement rate limiting per user
- [ ] Add virus scanning before processing
- [ ] Support batch uploads
- [ ] Add webhook notifications for task completion
- [ ] Implement file deduplication

## Related Documentation

- [Celery Tasks](../../workers/README_CELERY.md)
- [AI Service](../../../services/README_AI_SERVICE.md)
- [Database Schema](../../../../schema.sql)
- [API Schemas](../../../models/schemas.py)
