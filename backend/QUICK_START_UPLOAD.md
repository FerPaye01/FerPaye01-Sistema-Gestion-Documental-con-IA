# Quick Start: Document Upload Endpoint

## Start the Services

```bash
# Start all services with Docker Compose
docker-compose up -d

# Or start individually
docker-compose up -d postgres redis minio
docker-compose up backend worker
```

## Test the Upload Endpoint

### 1. Run Verification Script
```bash
cd backend
python verify_upload_endpoint.py
```

### 2. Upload a Document with cURL
```bash
# Upload a PDF
curl -X POST "http://localhost:8000/api/v1/documentos/upload" \
  -F "file=@your-document.pdf"

# Response:
# {
#   "task_id": "a1b2c3d4-...",
#   "status": "processing",
#   "message": "Documento 'your-document.pdf' encolado para procesamiento"
# }
```

### 3. Check Task Status
```bash
# Replace {task_id} with the ID from step 2
curl "http://localhost:8000/api/v1/documentos/tasks/{task_id}"

# Response (processing):
# {
#   "task_id": "a1b2c3d4-...",
#   "status": "processing",
#   "progress": 45
# }

# Response (completed):
# {
#   "task_id": "a1b2c3d4-...",
#   "status": "completed",
#   "progress": 100,
#   "documento_id": "f1e2d3c4-..."
# }
```

## API Documentation

Once the backend is running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Common Issues

### "Connection refused"
- Make sure backend is running: `docker-compose ps backend`
- Check logs: `docker-compose logs backend`

### "Task not found"
- Make sure Celery worker is running: `docker-compose ps worker`
- Check worker logs: `docker-compose logs worker`

### "File too large"
- Maximum file size is 50MB
- Adjust `MAX_UPLOAD_SIZE_MB` in `.env` if needed

### "Invalid file type"
- Only PDF and JPG files are supported
- Check file MIME type

## Monitor Processing

### Watch Celery Worker Logs
```bash
docker-compose logs -f worker
```

### Watch Backend Logs
```bash
docker-compose logs -f backend
```

## Example: Upload with Python

```python
import requests
import time

# Upload document
with open("document.pdf", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/v1/documentos/upload",
        files={"file": f}
    )

data = response.json()
task_id = data["task_id"]
print(f"Task ID: {task_id}")

# Poll for status
while True:
    status_response = requests.get(
        f"http://localhost:8000/api/v1/documentos/tasks/{task_id}"
    )
    status_data = status_response.json()
    
    print(f"Status: {status_data['status']}, Progress: {status_data.get('progress', 0)}%")
    
    if status_data["status"] == "completed":
        print(f"Document ID: {status_data['documento_id']}")
        break
    elif status_data["status"] == "error":
        print(f"Error: {status_data['error']}")
        break
    
    time.sleep(2)
```

## Next Steps

- Implement search endpoint (Task 5.4)
- Create React upload component (Task 6.2)
- Add authentication (Future)
