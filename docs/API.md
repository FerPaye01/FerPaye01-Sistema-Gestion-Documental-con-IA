# Documentación API - SGD UGEL Ilo

**Base URL**: `http://localhost:8000/api/v1`  
**Formato**: JSON  
**Autenticación**: No requerida (desarrollo)

## 📚 Endpoints

### Health Check

#### GET /health
Verificar que el servicio está activo.

```http
GET /health HTTP/1.1
Host: localhost:8000
```

**Respuesta (200 OK)**
```json
{
  "status": "healthy",
  "service": "sgd-ugel-api",
  "version": "0.1.0"
}
```

---

### Documentos

#### POST /documentos/upload
Subir un nuevo documento para procesamiento.

```http
POST /documentos/upload HTTP/1.1
Host: localhost:8000
Content-Type: multipart/form-data

file: <binary PDF data>
```

**Parámetros**
- `file` (required): Archivo PDF

**Respuesta (202 Accepted)**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "message": "Documento en cola de procesamiento"
}
```

**Errores**
- `400`: Archivo no válido
- `413`: Archivo muy grande (>50MB)

---

#### GET /documentos/tasks/{task_id}
Obtener estado del procesamiento de un documento.

```http
GET /documentos/tasks/550e8400-e29b-41d4-a716-446655440000 HTTP/1.1
Host: localhost:8000
```

**Respuesta (200 OK)**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "progress": 65,
  "stage": "Generando embeddings (15/48)",
  "info": {
    "progress": 65,
    "stage": "Generando embeddings (15/48)"
  }
}
```

**Estados posibles**
- `pending`: En cola
- `processing`: Procesando
- `completed`: Completado
- `error`: Error en procesamiento

---

#### GET /documentos
Listar documentos.

```http
GET /documentos?page=1&page_size=10 HTTP/1.1
Host: localhost:8000
```

**Parámetros Query**
- `page` (optional): Número de página (default: 1)
- `page_size` (optional): Documentos por página (default: 10)
- `status` (optional): Filtrar por estado (processing, completed, error)
- `tipo_documento` (optional): Filtrar por tipo

**Respuesta (200 OK)**
```json
{
  "results": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "filename": "resolucion_2025.pdf",
      "tipo_documento": "Resolución Directorial",
      "tema_principal": "Aprobación de presupuesto",
      "fecha_documento": "2025-01-15",
      "status": "completed",
      "created_at": "2025-01-20T10:30:00Z",
      "num_pages": 5
    }
  ],
  "total": 42,
  "page": 1,
  "total_pages": 5
}
```

---

#### GET /documentos/{id}
Obtener detalles de un documento específico.

```http
GET /documentos/550e8400-e29b-41d4-a716-446655440000 HTTP/1.1
Host: localhost:8000
```

**Respuesta (200 OK)**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "resolucion_2025.pdf",
  "minio_url": "http://minio:9000/documentos-ugel/...",
  "tipo_documento": "Resolución Directorial",
  "tema_principal": "Aprobación de presupuesto",
  "fecha_documento": "2025-01-15",
  "entidades_clave": ["Dirección", "Presupuesto", "2025"],
  "resumen_corto": "Se aprueba el presupuesto anual...",
  "file_size_bytes": 245632,
  "num_pages": 5,
  "status": "completed",
  "created_at": "2025-01-20T10:30:00Z",
  "processed_at": "2025-01-20T10:35:00Z"
}
```

---

#### DELETE /documentos/{id}
Eliminar un documento.

```http
DELETE /documentos/550e8400-e29b-41d4-a716-446655440000 HTTP/1.1
Host: localhost:8000
```

**Respuesta (200 OK)**
```json
{
  "message": "Documento eliminado exitosamente",
  "id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

### Búsqueda

#### POST /documentos/search
Búsqueda semántica de documentos.

```http
POST /documentos/search HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "query": "resolución presupuesto",
  "page": 1,
  "page_size": 10,
  "filters": {
    "tipo_documento": "Resolución Directorial",
    "fecha_desde": "2025-01-01",
    "fecha_hasta": "2025-12-31"
  }
}
```

**Parámetros Body**
- `query` (required): Texto a buscar
- `page` (optional): Número de página (default: 1)
- `page_size` (optional): Resultados por página (default: 10)
- `filters` (optional): Filtros adicionales

**Respuesta (200 OK)**
```json
{
  "results": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "filename": "resolucion_2025.pdf",
      "tipo_documento": "Resolución Directorial",
      "tema_principal": "Aprobación de presupuesto",
      "relevancia": 0.92,
      "fragmento": "Se aprueba el presupuesto anual para el año 2025..."
    }
  ],
  "total": 5,
  "page": 1,
  "total_pages": 1,
  "query": "resolución presupuesto"
}
```

**Notas**
- La búsqueda es semántica (entiende significado, no solo palabras clave)
- `relevancia`: Score de 0 a 1 (1 = más relevante)
- Solo devuelve documentos con status='completed'

---

## 🔄 Flujo de Procesamiento

```
1. Upload (POST /documentos/upload)
   ↓
2. Polling (GET /documentos/tasks/{task_id})
   ├─ Extracción OCR
   ├─ Extracción de metadatos (Gemini)
   ├─ Fragmentación de texto
   └─ Generación de embeddings
   ↓
3. Completado (status='completed')
   ↓
4. Búsqueda (POST /documentos/search)
```

---

## 📊 Tipos de Documento

Categorías válidas para `tipo_documento`:

- `Oficio`
- `Oficio Múltiple`
- `Resolución Directorial`
- `Informe`
- `Solicitud`
- `Memorándum`
- `Acta`
- `Varios`

---

## ⚠️ Códigos de Error

| Código | Descripción |
|--------|-------------|
| 200 | OK - Solicitud exitosa |
| 202 | Accepted - Procesamiento iniciado |
| 400 | Bad Request - Parámetros inválidos |
| 404 | Not Found - Recurso no encontrado |
| 413 | Payload Too Large - Archivo muy grande |
| 500 | Internal Server Error - Error del servidor |

---

## 🔐 Límites

- **Tamaño máximo de archivo**: 50 MB
- **Timeout de procesamiento**: 5 minutos
- **Máximo de resultados por búsqueda**: 50
- **Máximo de documentos por página**: 100

---

## 💡 Ejemplos de Uso

### Ejemplo 1: Subir y procesar documento

```bash
# 1. Subir documento
RESPONSE=$(curl -X POST http://localhost:8000/api/v1/documentos/upload \
  -F "file=@documento.pdf")

TASK_ID=$(echo $RESPONSE | jq -r '.task_id')
echo "Task ID: $TASK_ID"

# 2. Esperar a que se procese
while true; do
  STATUS=$(curl -s http://localhost:8000/api/v1/documentos/tasks/$TASK_ID)
  PROGRESS=$(echo $STATUS | jq -r '.progress')
  STAGE=$(echo $STATUS | jq -r '.stage')
  
  echo "Progreso: $PROGRESS% - $STAGE"
  
  if [ "$PROGRESS" = "100" ]; then
    break
  fi
  
  sleep 2
done

echo "¡Procesamiento completado!"
```

### Ejemplo 2: Buscar documentos

```bash
curl -X POST http://localhost:8000/api/v1/documentos/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "presupuesto 2025",
    "page": 1,
    "page_size": 5
  }' | jq '.'
```

### Ejemplo 3: Listar documentos completados

```bash
curl "http://localhost:8000/api/v1/documentos?status=completed&page_size=20" | jq '.'
```

---

## 📖 Documentación Interactiva

Acceder a Swagger UI para probar endpoints interactivamente:

```
http://localhost:8000/docs
```

O ReDoc:

```
http://localhost:8000/redoc
```
