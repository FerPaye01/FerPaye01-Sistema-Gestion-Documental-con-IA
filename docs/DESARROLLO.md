# Guía de Desarrollo - SGD

## 🛠️ Configuración del Entorno de Desarrollo

### Requisitos
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Git
- Editor: VS Code, PyCharm, o similar

### Setup Inicial

```bash
# 1. Clonar repositorio
git clone <repo-url>
cd proyecto-sgd

# 2. Crear entorno virtual Python
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# 3. Instalar dependencias backend
cd backend
pip install -r requirements.txt

# 4. Instalar dependencias frontend
cd ../frontend
npm install

# 5. Volver a raíz
cd ..

# 6. Iniciar servicios Docker
docker-compose up -d
```

## 📁 Estructura de Carpetas

```
proyecto-sgd/
├── backend/
│   ├── app/
│   │   ├── api/v1/
│   │   │   ├── endpoints/
│   │   │   │   └── documentos.py
│   │   │   └── router.py
│   │   ├── models/
│   │   │   ├── base.py
│   │   │   └── documento.py
│   │   ├── services/
│   │   │   ├── ai_service.py
│   │   │   ├── ocr_service.py
│   │   │   ├── text_service.py
│   │   │   └── storage_service.py
│   │   ├── workers/
│   │   │   ├── celery_app.py
│   │   │   └── tasks.py
│   │   ├── main.py
│   │   ├── database.py
│   │   └── config.py
│   ├── tests/
│   ├── Dockerfile.simple
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── App.tsx
│   ├── public/
│   └── package.json
├── docker-compose.yml
├── init-db-complete.sql
└── .kiro/
    └── specs/sgd-enhancements/
```

## 🚀 Desarrollo Backend

### Ejecutar servidor en desarrollo

```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

El servidor se reiniciará automáticamente al cambiar archivos.

### Estructura de un Endpoint

```python
# backend/app/api/v1/endpoints/documentos.py

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.documento import Documento
import structlog

router = APIRouter(prefix="/documentos", tags=["documentos"])
logger = structlog.get_logger()

@router.post("/upload")
async def upload_documento(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Subir un nuevo documento"""
    try:
        # Validar archivo
        if not file.filename.endswith('.pdf'):
            raise ValueError("Solo se aceptan archivos PDF")
        
        # Procesar archivo
        logger.info("document_upload_started", filename=file.filename)
        
        # Crear tarea Celery
        task = process_document.delay(file_path)
        
        return {
            "task_id": str(task.id),
            "status": "processing"
        }
    except Exception as e:
        logger.error("upload_error", error=str(e))
        raise
```

### Crear un Servicio

```python
# backend/app/services/mi_servicio.py

import structlog
from typing import Optional

logger = structlog.get_logger()

class MiServicio:
    """Descripción del servicio"""
    
    def __init__(self):
        self.config = {}
    
    def procesar(self, datos: str) -> dict:
        """Procesar datos"""
        try:
            logger.info("procesamiento_iniciado", datos_length=len(datos))
            
            # Lógica aquí
            resultado = self._hacer_algo(datos)
            
            logger.info("procesamiento_completado", resultado=resultado)
            return resultado
        except Exception as e:
            logger.error("procesamiento_error", error=str(e))
            raise
    
    def _hacer_algo(self, datos: str) -> dict:
        """Método privado"""
        return {"resultado": datos}

# Uso
servicio = MiServicio()
resultado = servicio.procesar("datos")
```

### Crear una Tarea Celery

```python
# backend/app/workers/tasks.py

from celery import shared_task
import structlog

logger = structlog.get_logger()

@shared_task(bind=True, max_retries=3)
def mi_tarea(self, parametro: str):
    """Descripción de la tarea"""
    try:
        logger.info("tarea_iniciada", parametro=parametro)
        
        # Lógica aquí
        resultado = procesar(parametro)
        
        logger.info("tarea_completada", resultado=resultado)
        return resultado
    except Exception as exc:
        logger.error("tarea_error", error=str(exc))
        # Reintentar después de 60 segundos
        raise self.retry(exc=exc, countdown=60)
```

### Testing Backend

```bash
# Ejecutar todos los tests
pytest

# Ejecutar tests específicos
pytest backend/tests/test_documentos.py

# Con cobertura
pytest --cov=app backend/tests/
```

### Estructura de un Test

```python
# backend/tests/test_documentos.py

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture
def documento_fixture():
    """Fixture para crear un documento de prueba"""
    return {
        "filename": "test.pdf",
        "content": b"PDF content"
    }

def test_upload_documento(documento_fixture):
    """Test de upload de documento"""
    response = client.post(
        "/api/v1/documentos/upload",
        files={"file": documento_fixture}
    )
    assert response.status_code == 202
    assert "task_id" in response.json()

def test_get_documento():
    """Test de obtener documento"""
    response = client.get("/api/v1/documentos/123")
    assert response.status_code in [200, 404]
```

## 🎨 Desarrollo Frontend

### Ejecutar servidor en desarrollo

```bash
cd frontend
npm run dev
```

Acceder a http://localhost:5173

### Estructura de un Componente

```typescript
// frontend/src/components/MiComponente.tsx

import React, { useState, useEffect } from 'react';
import { api } from '../services/api';

interface Props {
  id: string;
}

export const MiComponente: React.FC<Props> = ({ id }) => {
  const [datos, setDatos] = useState(null);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    cargarDatos();
  }, [id]);

  const cargarDatos = async () => {
    try {
      setCargando(true);
      const respuesta = await api.get(`/documentos/${id}`);
      setDatos(respuesta.data);
    } catch (err) {
      setError(err.message);
    } finally {
      setCargando(false);
    }
  };

  if (cargando) return <div>Cargando...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!datos) return <div>Sin datos</div>;

  return (
    <div>
      <h2>{datos.filename}</h2>
      <p>{datos.tema_principal}</p>
    </div>
  );
};
```

### Servicio API

```typescript
// frontend/src/services/api.ts

import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para errores
api.interceptors.response.use(
  response => response,
  error => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

export const documentosAPI = {
  upload: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/documentos/upload', formData);
  },
  
  getStatus: (taskId: string) => api.get(`/documentos/tasks/${taskId}`),
  
  search: (query: string, page: number = 1) =>
    api.post('/documentos/search', { query, page, page_size: 10 }),
  
  list: (page: number = 1) => api.get(`/documentos?page=${page}`),
  
  get: (id: string) => api.get(`/documentos/${id}`),
  
  delete: (id: string) => api.delete(`/documentos/${id}`),
};
```

## 🔍 Debugging

### Backend

```python
# Usar print para debugging rápido
print(f"DEBUG: {variable}")

# Usar logging estructurado
logger.info("evento", variable=valor, otro=dato)

# Usar debugger
import pdb; pdb.set_trace()
```

### Frontend

```typescript
// Console logging
console.log('DEBUG:', variable);
console.error('ERROR:', error);

// React DevTools
// Instalar extensión en navegador

// Network tab en DevTools
// Ver requests/responses
```

## 📝 Convenciones de Código

### Python
- PEP 8: 4 espacios de indentación
- Type hints: `def funcion(param: str) -> dict:`
- Docstrings: """Descripción de la función"""
- Nombres: snake_case para funciones y variables

### TypeScript
- 2 espacios de indentación
- Interfaces para tipos complejos
- Nombres: camelCase para variables, PascalCase para componentes
- Comentarios: // para líneas, /* */ para bloques

## 🚀 Workflow de Desarrollo

### 1. Crear rama
```bash
git checkout -b feature/mi-feature
```

### 2. Hacer cambios
```bash
# Editar archivos
# Probar localmente
```

### 3. Commit
```bash
git add .
git commit -m "feat: descripción del cambio"
```

### 4. Push
```bash
git push origin feature/mi-feature
```

### 5. Pull Request
- Crear PR en GitHub
- Describir cambios
- Esperar revisión

## 🧪 Testing

### Backend
```bash
# Tests unitarios
pytest backend/tests/unit/

# Tests de integración
pytest backend/tests/integration/

# Con cobertura
pytest --cov=app --cov-report=html
```

### Frontend
```bash
# Tests unitarios
npm test

# Con cobertura
npm test -- --coverage
```

## 📚 Recursos Útiles

### Documentación
- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy](https://docs.sqlalchemy.org/)
- [React](https://react.dev/)
- [PostgreSQL](https://www.postgresql.org/docs/)

### Herramientas
- [Postman](https://www.postman.com/) - Testing API
- [DBeaver](https://dbeaver.io/) - Gestor BD
- [VS Code](https://code.visualstudio.com/) - Editor

## 🐛 Troubleshooting

### Error: "ModuleNotFoundError"
```bash
# Reinstalar dependencias
pip install -r requirements.txt
```

### Error: "Port already in use"
```bash
# Cambiar puerto en docker-compose.yml
# O liberar el puerto
lsof -i :8000  # Ver qué usa el puerto
kill -9 <PID>  # Matar proceso
```

### Error: "Database connection failed"
```bash
# Verificar que PostgreSQL está corriendo
docker-compose ps

# Reiniciar PostgreSQL
docker-compose restart postgres
```

## 💡 Tips de Productividad

1. **Hot reload**: Cambios se aplican automáticamente
2. **Swagger UI**: Probar endpoints en http://localhost:8000/docs
3. **Logging**: Usar logging estructurado para debugging
4. **Type hints**: Ayudan a detectar errores temprano
5. **Tests**: Escribir tests mientras desarrollas

## 📞 Soporte

Para preguntas o problemas:
1. Revisar documentación
2. Buscar en issues existentes
3. Crear nuevo issue con detalles
4. Contactar al equipo de desarrollo
