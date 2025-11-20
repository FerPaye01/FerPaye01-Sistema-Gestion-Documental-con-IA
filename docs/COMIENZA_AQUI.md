# 🚀 COMIENZA AQUÍ - SGD

Bienvenido al Sistema de Gestión Documental Inteligente.

Este archivo te guiará por los primeros pasos.

---

## ⏱️ ¿Cuánto tiempo tienes?

### ⚡ 5 minutos
Quiero ver qué es esto rápidamente.

→ Lee: [README.md](README.md) (Sección "Características Principales")

### 🕐 30 minutos
Quiero instalar y probar.

→ Sigue: [INSTALACION.md](INSTALACION.md)

### 📚 2 horas
Quiero entender cómo funciona.

→ Estudia: [ARQUITECTURA.md](ARQUITECTURA.md)

### 💻 Quiero desarrollar
Quiero contribuir código.

→ Lee: [DESARROLLO.md](DESARROLLO.md)

---

## 🎯 ¿Cuál es tu rol?

### 👤 Soy Usuario
Quiero usar el sistema.

**Pasos:**
1. [INSTALACION.md](INSTALACION.md) - Instalar
2. http://localhost:3000 - Acceder
3. [REFERENCIA_RAPIDA.md](REFERENCIA_RAPIDA.md) - Usar

**Tiempo**: 30 minutos

---

### 👨‍💻 Soy Desarrollador Backend
Quiero crear endpoints y servicios.

**Pasos:**
1. [README.md](README.md) - Entender proyecto
2. [INSTALACION.md](INSTALACION.md) - Instalar
3. [ARQUITECTURA.md](ARQUITECTURA.md) - Entender diseño
4. [DESARROLLO.md](DESARROLLO.md) - Aprender a desarrollar
5. [API.md](API.md) - Ver endpoints
6. `backend/app/` - Explorar código

**Tiempo**: 2-3 horas

---

### 🎨 Soy Desarrollador Frontend
Quiero crear componentes y UI.

**Pasos:**
1. [README.md](README.md) - Entender proyecto
2. [INSTALACION.md](INSTALACION.md) - Instalar
3. [ARQUITECTURA.md](ARQUITECTURA.md) - Entender diseño
4. [DESARROLLO.md](DESARROLLO.md) - Aprender a desarrollar
5. [API.md](API.md) - Ver endpoints disponibles
6. `frontend/src/` - Explorar código

**Tiempo**: 2-3 horas

---

### 🏗️ Soy DevOps / Infraestructura
Quiero configurar y desplegar.

**Pasos:**
1. [README.md](README.md) - Entender proyecto
2. [INSTALACION.md](INSTALACION.md) - Instalar
3. `docker-compose.yml` - Revisar configuración
4. `init-db-complete.sql` - Revisar BD
5. [REFERENCIA_RAPIDA.md](REFERENCIA_RAPIDA.md) - Comandos útiles

**Tiempo**: 1-2 horas

---

### 📊 Soy Project Manager
Quiero entender el proyecto.

**Pasos:**
1. [README.md](README.md) - Descripción general
2. [ARQUITECTURA.md](ARQUITECTURA.md) - Resumen técnico
3. `.kiro/specs/sgd-enhancements/` - Especificaciones
4. [REFERENCIA_RAPIDA.md](REFERENCIA_RAPIDA.md) - Comandos útiles

**Tiempo**: 1 hora

---

## 🚀 Instalación Rápida (3 pasos)

### Paso 1: Clonar
```bash
git clone <repo-url>
cd proyecto-sgd
```

### Paso 2: Configurar
```bash
cp .env.example .env
# Editar .env con tu Google API Key
```

### Paso 3: Iniciar
```bash
docker-compose up -d
```

**Listo.** Accede a http://localhost:3000

---

## 🌐 URLs Importantes

| Servicio | URL |
|----------|-----|
| **Frontend** | http://localhost:3000 |
| **API** | http://localhost:8000 |
| **API Docs** | http://localhost:8000/docs |
| **MinIO** | http://localhost:9001 |

---

## 📚 Documentación Completa

| Documento | Para Qué |
|-----------|----------|
| [README.md](README.md) | Descripción general |
| [INSTALACION.md](INSTALACION.md) | Instalar paso a paso |
| [API.md](API.md) | Endpoints disponibles |
| [ARQUITECTURA.md](ARQUITECTURA.md) | Cómo funciona |
| [DESARROLLO.md](DESARROLLO.md) | Cómo desarrollar |
| [REFERENCIA_RAPIDA.md](REFERENCIA_RAPIDA.md) | Comandos útiles |
| [INDICE.md](INDICE.md) | Índice completo |

---

## ❓ Preguntas Frecuentes

### ¿Qué necesito para instalar?
- Docker & Docker Compose
- Google API Key (para IA)
- 4GB RAM mínimo

### ¿Cuánto tarda la instalación?
- Descarga: 5-10 minutos (depende de internet)
- Inicialización: 2-3 minutos
- Total: 10-15 minutos

### ¿Qué puedo hacer con esto?
- Subir documentos PDF
- Buscar documentos por contenido
- Extraer metadatos automáticamente
- Clasificar documentos

### ¿Cómo obtengo una Google API Key?
1. Ir a https://console.cloud.google.com/
2. Crear proyecto
3. Habilitar APIs: Gemini, Text Embedding
4. Crear credenciales (API Key)
5. Copiar en `.env`

### ¿Hay problemas?
→ Ver: [REFERENCIA_RAPIDA.md - Troubleshooting](REFERENCIA_RAPIDA.md#-solución-rápida-de-problemas)

---

## 🎓 Aprende Más

### Conceptos Clave
- **Búsqueda Vectorial**: Buscar por significado, no por palabras
- **Embeddings**: Representación numérica de texto
- **OCR**: Extracción de texto de imágenes/PDFs
- **LLM**: Inteligencia Artificial (Gemini)

### Tecnologías
- **Backend**: FastAPI (Python)
- **Frontend**: React (TypeScript)
- **BD**: PostgreSQL + pgvector
- **Cache**: Redis
- **Storage**: MinIO
- **Orquestación**: Docker Compose

---

## ✅ Checklist de Inicio

- [ ] Cloné el repositorio
- [ ] Instalé Docker
- [ ] Obtuve Google API Key
- [ ] Ejecuté `docker-compose up -d`
- [ ] Accedí a http://localhost:3000
- [ ] Leí README.md
- [ ] Probé subir un documento
- [ ] Probé buscar documentos

---

## 🆘 Necesito Ayuda

### Problema: No puedo instalar
→ [INSTALACION.md - Solución de Problemas](INSTALACION.md#-solución-de-problemas)

### Problema: No funciona la búsqueda
→ [REFERENCIA_RAPIDA.md - Troubleshooting](REFERENCIA_RAPIDA.md#-solución-rápida-de-problemas)

### Problema: No entiendo la arquitectura
→ [ARQUITECTURA.md](ARQUITECTURA.md)

### Problema: Quiero desarrollar
→ [DESARROLLO.md](DESARROLLO.md)

---

## 🎉 ¡Listo!

Ya tienes todo lo que necesitas para empezar.

**Próximo paso**: Abre [README.md](README.md)

---

## 📞 Contacto

- **Documentación**: Ver archivos .md
- **Código**: Ver carpetas `backend/` y `frontend/`
- **Especificaciones**: Ver `.kiro/specs/`
- **Problemas**: Revisar logs con `docker-compose logs`

---

**¡Bienvenido al proyecto SGD!** 🚀

Comienza con [README.md](README.md) →
