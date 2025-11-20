# Referencia Rápida - SGD

## 🚀 Comandos Esenciales

### Docker
```bash
# Iniciar servicios
docker-compose up -d

# Ver estado
docker-compose ps

# Ver logs
docker-compose logs -f backend

# Detener
docker-compose down

# Limpiar todo
docker-compose down -v
```

### Backend
```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar servidor
python -m uvicorn app.main:app --reload

# Ejecutar tests
pytest

# Ejecutar Celery worker
celery -A app.workers.celery_app worker --loglevel=info
```

### Frontend
```bash
# Instalar dependencias
npm install

# Ejecutar dev server
npm run dev

# Build producción
npm run build

# Ejecutar tests
npm test
```

## 🌐 URLs Importantes

| Servicio | URL |
|----------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |
| API Docs (ReDoc) | http://localhost:8000/redoc |
| MinIO Console | http://localhost:9001 |
| PostgreSQL | localhost:5432 |
| Redis | localhost:6379 |

## 📋 Endpoints Principales

```bash
# Subir documento
curl -X POST http://localhost:8000/api/v1/documentos/upload \
  -F "file=@documento.pdf"

# Buscar documentos
curl -X POST http://localhost:8000/api/v1/documentos/search \
  -H "Content-Type: application/json" \
  -d '{"query": "presupuesto"}'

# Listar documentos
curl http://localhost:8000/api/v1/documentos

# Obtener documento
curl http://localhost:8000/api/v1/documentos/{id}

# Eliminar documento
curl -X DELETE http://localhost:8000/api/v1/documentos/{id}

# Health check
curl http://localhost:8000/health
```

## 🗄️ Comandos Base de Datos

```bash
# Conectar a PostgreSQL
docker exec -it sgd-postgres psql -U sgd_user -d sgd_ugel

# Ver tablas
\dt

# Ver estructura de tabla
\d documentos

# Contar documentos
SELECT COUNT(*) FROM documentos;

# Ver documentos completados
SELECT id, filename, status FROM documentos WHERE status='completed';

# Ver fragmentos de un documento
SELECT * FROM fragmentos WHERE documento_id='<id>';

# Salir
\q
```

## 📁 Archivos Importantes

| Archivo | Propósito |
|---------|-----------|
| `docker-compose.yml` | Orquestación de servicios |
| `init-db-complete.sql` | Script de inicialización BD |
| `backend/requirements.txt` | Dependencias Python |
| `frontend/package.json` | Dependencias Node |
| `.env` | Variables de entorno |
| `backend/app/main.py` | Aplicación principal |
| `backend/app/models/documento.py` | Modelos de datos |

## 🔧 Configuración Rápida

### Cambiar puerto del frontend
```yaml
# docker-compose.yml
frontend:
  ports:
    - "3001:3000"  # Cambiar 3000 a 3001
```

### Cambiar puerto del backend
```yaml
# docker-compose.yml
backend:
  ports:
    - "8001:8000"  # Cambiar 8000 a 8001
```

### Aumentar tamaño máximo de archivo
```env
# .env
MAX_UPLOAD_SIZE_MB=100  # Cambiar de 50 a 100
```

## 🐛 Solución Rápida de Problemas

| Problema | Solución |
|----------|----------|
| Contenedores no inician | `docker-compose down -v && docker-compose up -d` |
| Puerto en uso | Cambiar puerto en docker-compose.yml |
| BD no se inicializa | `docker-compose restart postgres` |
| API no responde | `docker-compose logs backend` |
| Frontend no carga | Verificar que backend está corriendo |
| Búsqueda sin resultados | Verificar que documentos están procesados |

## 📊 Monitoreo Rápido

```bash
# Ver estado de servicios
docker-compose ps

# Ver logs en tiempo real
docker-compose logs -f

# Ver logs específicos
docker-compose logs backend
docker-compose logs celery
docker-compose logs postgres

# Ver uso de recursos
docker stats

# Verificar conectividad BD
docker exec sgd-postgres pg_isready -U sgd_user
```

## 🔐 Credenciales por Defecto

| Servicio | Usuario | Contraseña |
|----------|---------|-----------|
| PostgreSQL | sgd_user | sgd_pass |
| MinIO | minioadmin | minioadmin |
| Redis | (sin auth) | - |

## 📝 Estructura de Respuesta API

### Éxito (200 OK)
```json
{
  "results": [...],
  "total": 10,
  "page": 1,
  "total_pages": 1
}
```

### Error (400 Bad Request)
```json
{
  "detail": "Descripción del error"
}
```

### Procesamiento (202 Accepted)
```json
{
  "task_id": "uuid",
  "status": "processing"
}
```

## 🎯 Flujo Típico de Uso

1. **Subir documento**
   ```bash
   curl -X POST http://localhost:8000/api/v1/documentos/upload \
     -F "file=@documento.pdf"
   ```

2. **Obtener task_id de respuesta**
   ```json
   {"task_id": "550e8400-e29b-41d4-a716-446655440000"}
   ```

3. **Esperar procesamiento**
   ```bash
   curl http://localhost:8000/api/v1/documentos/tasks/550e8400-e29b-41d4-a716-446655440000
   ```

4. **Buscar documento**
   ```bash
   curl -X POST http://localhost:8000/api/v1/documentos/search \
     -H "Content-Type: application/json" \
     -d '{"query": "palabra clave"}'
   ```

## 🔄 Ciclo de Desarrollo

```
1. Hacer cambios en código
   ↓
2. Guardar archivo (hot reload automático)
   ↓
3. Probar en navegador/Postman
   ↓
4. Ver logs si hay errores
   ↓
5. Commit y push
```

## 📚 Documentación Completa

- `README.md` - Descripción general
- `INSTALACION.md` - Guía de instalación
- `API.md` - Documentación de endpoints
- `ARQUITECTURA.md` - Diseño del sistema
- `DESARROLLO.md` - Guía de desarrollo
- `ARCHIVOS_CRITICOS.md` - Archivos importantes

## 💡 Tips Útiles

1. **Swagger UI**: Probar endpoints interactivamente en `/docs`
2. **Logs estructurados**: Buscar eventos específicos en logs
3. **Hot reload**: Cambios se aplican sin reiniciar
4. **Database browser**: Usar DBeaver para explorar BD
5. **Postman**: Guardar requests frecuentes en colecciones

## 🆘 Contacto Rápido

- **Documentación**: Ver archivos .md en raíz
- **Logs**: `docker-compose logs`
- **Health check**: `curl http://localhost:8000/health`
- **API Docs**: http://localhost:8000/docs
