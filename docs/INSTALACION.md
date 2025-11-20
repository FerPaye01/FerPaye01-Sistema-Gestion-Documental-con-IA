# Guía de Instalación - SGD UGEL Ilo

## 📋 Requisitos Previos

### Sistema Operativo
- Windows 10/11, macOS, o Linux
- Docker Desktop instalado
- Docker Compose v2.0+

### Credenciales Necesarias
- Google API Key (para Gemini y embeddings)
- Acceso a internet para descargar imágenes Docker

## 🔧 Instalación Paso a Paso

### 1. Preparar el Entorno

```bash
# Clonar el proyecto
git clone https://github.com/FerPaye01/Sistema-de-Gesti-n-Documental-Inteligente.git
cd Sistema-de-Gesti-n-Documental-Inteligente

# Crear archivo .env desde la plantilla
cp backend/.env.example backend/.env
```

### 2. Instalar Dependencias

**Backend:**
```bash
cd backend
pip install -r requirements.txt
cd ..
```

**Frontend:**
```bash
cd frontend
npm install
cd ..
```

### 3. Configurar Variables de Entorno

Editar `backend/.env` con tus valores:

```env
# Google AI (REQUERIDO)
GOOGLE_API_KEY=AIzaSy...  # Tu API key de Google Cloud
# Obtén tu clave en: https://makersuite.google.com/app/apikey

# Base de Datos (usar valores por defecto para desarrollo)
DATABASE_URL=postgresql://sgd_user:sgd_pass@postgres:5432/sgd_ugel

# MinIO (usar valores por defecto para desarrollo)
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
```

### 4. Iniciar Servicios

```bash
# Iniciar todos los servicios
docker-compose up -d

# Verificar que todo está corriendo
docker-compose ps
```

**Salida esperada:**
```
NAME                COMMAND                  SERVICE      STATUS
sgd-postgres        "docker-entrypoint.s…"   postgres     Up (healthy)
sgd-redis           "redis-server"           redis        Up (healthy)
sgd-minio           "/usr/bin/docker-ent…"   minio        Up (healthy)
sgd-backend         "uvicorn app.main:ap…"   backend      Up
sgd-celery          "celery -A app.worker…"  celery       Up
sgd-frontend        "vite --host 0.0.0.0…"   frontend     Up
```

### 5. Verificar Instalación

```bash
# Health check del backend
curl http://localhost:8000/health

# Respuesta esperada:
# {"status":"healthy","service":"sgd-ugel-api"}
```

### 6. Acceder a la Aplicación

- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **MinIO Console**: http://localhost:9001 (minioadmin/minioadmin)

## 🐛 Solución de Problemas

### Problema: Contenedores no inician

```bash
# Ver logs detallados
docker-compose logs backend

# Reiniciar servicios
docker-compose restart

# Limpiar y reiniciar desde cero
docker-compose down -v
docker-compose up -d
```

### Problema: Base de datos no se inicializa

```bash
# Verificar que PostgreSQL está corriendo
docker-compose logs postgres

# Reiniciar solo PostgreSQL
docker-compose restart postgres

# Esperar 30 segundos y verificar
docker-compose exec postgres psql -U sgd_user -d sgd_ugel -c "\dt"
```

### Problema: Google API Key inválida

```bash
# Verificar que la clave está en .env
cat .env | grep GOOGLE_API_KEY

# Reiniciar backend
docker-compose restart backend

# Ver logs
docker-compose logs backend | grep -i "google\|api"
```

### Problema: Puerto ya en uso

```bash
# Cambiar puertos en docker-compose.yml
# Ejemplo: cambiar 3000:3000 a 3001:3000

# O liberar el puerto
# Windows: netstat -ano | findstr :3000
# Linux/Mac: lsof -i :3000
```

## 📊 Verificación Post-Instalación

### 1. Verificar Base de Datos

```bash
docker-compose exec postgres psql -U sgd_user -d sgd_ugel -c "
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public';"
```

**Tablas esperadas:**
- documentos
- fragmentos
- audit_log

### 2. Verificar Servicios

```bash
# Backend
curl http://localhost:8000/health/detailed

# Redis
docker-compose exec redis redis-cli ping

# MinIO
curl http://localhost:9000/minio/health/live
```

### 3. Probar Upload de Documento

```bash
# Crear un PDF de prueba o usar uno existente
curl -X POST http://localhost:8000/api/v1/documentos/upload \
  -F "file=@documento.pdf"

# Respuesta esperada:
# {"task_id": "uuid", "status": "processing"}
```

## 🔄 Actualización

### Actualizar a nueva versión

```bash
# Detener servicios
docker-compose down

# Actualizar código
git pull origin main

# Reconstruir imágenes
docker-compose build --no-cache

# Iniciar nuevamente
docker-compose up -d
```

## 🛑 Detener la Aplicación

```bash
# Detener sin eliminar datos
docker-compose stop

# Detener y eliminar contenedores
docker-compose down

# Detener, eliminar contenedores y volúmenes (CUIDADO: borra datos)
docker-compose down -v
```

## 📝 Notas Importantes

- **Primera ejecución**: Puede tardar 2-3 minutos en iniciar todos los servicios
- **Google API Key**: Es obligatoria para que funcione la IA
- **Datos persistentes**: Se guardan en volúmenes Docker
- **Desarrollo**: Cambios en código se recargan automáticamente
- **Producción**: Revisar configuración de seguridad antes de desplegar

## 🆘 Soporte

Si encuentras problemas:

1. Revisar logs: `docker-compose logs`
2. Verificar archivo `.env`
3. Confirmar que Docker está corriendo
4. Intentar limpiar y reiniciar: `docker-compose down -v && docker-compose up -d`
