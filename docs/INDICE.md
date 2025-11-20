# Índice de Documentación - SGD

## 📚 Documentación Disponible

### 🚀 Para Empezar
1. **[README.md](README.md)** - Descripción general del proyecto
   - Características principales
   - Arquitectura de alto nivel
   - Inicio rápido
   - Estructura del proyecto

2. **[INSTALACION.md](INSTALACION.md)** - Guía paso a paso de instalación
   - Requisitos previos
   - Configuración del entorno
   - Verificación post-instalación
   - Solución de problemas

3. **[REFERENCIA_RAPIDA.md](REFERENCIA_RAPIDA.md)** - Comandos y URLs esenciales
   - Comandos Docker
   - URLs importantes
   - Endpoints principales
   - Troubleshooting rápido

### 📖 Documentación Técnica
4. **[API.md](API.md)** - Documentación completa de endpoints
   - Descripción de cada endpoint
   - Parámetros y respuestas
   - Códigos de error
   - Ejemplos de uso

5. **[ARQUITECTURA.md](ARQUITECTURA.md)** - Diseño del sistema
   - Visión general de la arquitectura
   - Flujo de procesamiento
   - Modelo de datos
   - Componentes principales
   - Tecnologías utilizadas

6. **[DESARROLLO.md](DESARROLLO.md)** - Guía para desarrolladores
   - Configuración del entorno de desarrollo
   - Estructura de carpetas
   - Cómo crear endpoints
   - Cómo crear servicios
   - Testing
   - Convenciones de código

### 📋 Especificaciones
7. **[.kiro/specs/sgd-enhancements/requirements.md](.kiro/specs/sgd-enhancements/requirements.md)** - Requisitos del proyecto
   - Especificaciones funcionales
   - Requisitos técnicos
   - Casos de uso

8. **[.kiro/specs/sgd-enhancements/tasks.md](.kiro/specs/sgd-enhancements/tasks.md)** - Tareas del proyecto
   - Lista de tareas
   - Estado de implementación
   - Prioridades

### 🔧 Configuración
9. **[docker-compose.yml](docker-compose.yml)** - Orquestación de servicios
   - Configuración de PostgreSQL
   - Configuración de Redis
   - Configuración de MinIO
   - Configuración del backend
   - Configuración del frontend

10. **[init-db-complete.sql](init-db-complete.sql)** - Script de inicialización BD
    - Creación de tablas
    - Creación de índices
    - Permisos de usuario

11. **[.env.example](.env.example)** - Variables de entorno (si existe)
    - Configuración de base de datos
    - Configuración de Google AI
    - Configuración de MinIO

### 📁 Código Fuente
12. **[backend/](backend/)** - Código del backend
    - `app/main.py` - Aplicación principal
    - `app/api/v1/endpoints/documentos.py` - Endpoints
    - `app/models/documento.py` - Modelos de datos
    - `app/services/` - Servicios
    - `app/workers/` - Tareas Celery

13. **[frontend/](frontend/)** - Código del frontend
    - `src/components/` - Componentes React
    - `src/pages/` - Páginas
    - `src/services/` - Servicios API

14. **[.kiro/](kiro/)** - Configuración de Kiro IDE
    - Especificaciones del proyecto
    - Tareas de desarrollo

---

## 🎯 Guías por Rol

### 👤 Usuario Final
1. Leer: [README.md](README.md)
2. Seguir: [INSTALACION.md](INSTALACION.md)
3. Usar: [REFERENCIA_RAPIDA.md](REFERENCIA_RAPIDA.md)

### 👨‍💻 Desarrollador Backend
1. Leer: [README.md](README.md)
2. Seguir: [INSTALACION.md](INSTALACION.md)
3. Estudiar: [ARQUITECTURA.md](ARQUITECTURA.md)
4. Consultar: [DESARROLLO.md](DESARROLLO.md)
5. Implementar: [API.md](API.md)

### 🎨 Desarrollador Frontend
1. Leer: [README.md](README.md)
2. Seguir: [INSTALACION.md](INSTALACION.md)
3. Estudiar: [ARQUITECTURA.md](ARQUITECTURA.md)
4. Consultar: [DESARROLLO.md](DESARROLLO.md)
5. Integrar: [API.md](API.md)

### 🏗️ DevOps / Infraestructura
1. Leer: [README.md](README.md)
2. Configurar: [docker-compose.yml](docker-compose.yml)
3. Inicializar: [init-db-complete.sql](init-db-complete.sql)
4. Monitorear: [REFERENCIA_RAPIDA.md](REFERENCIA_RAPIDA.md)

### 📊 Project Manager
1. Leer: [README.md](README.md)
2. Revisar: [.kiro/specs/sgd-enhancements/requirements.md](.kiro/specs/sgd-enhancements/requirements.md)
3. Seguimiento: [.kiro/specs/sgd-enhancements/tasks.md](.kiro/specs/sgd-enhancements/tasks.md)

---

## 📊 Mapa de Contenidos

```
INICIO
  ├─ README.md (¿Qué es?)
  ├─ INSTALACION.md (¿Cómo instalar?)
  └─ REFERENCIA_RAPIDA.md (¿Cómo usar?)

DESARROLLO
  ├─ ARQUITECTURA.md (¿Cómo funciona?)
  ├─ DESARROLLO.md (¿Cómo desarrollar?)
  ├─ API.md (¿Qué endpoints hay?)
  └─ backend/ + frontend/ (Código)

ESPECIFICACIONES
  ├─ requirements.md (¿Qué se requiere?)
  └─ tasks.md (¿Qué se debe hacer?)

CONFIGURACIÓN
  ├─ docker-compose.yml (¿Cómo orquestar?)
  ├─ init-db-complete.sql (¿Cómo inicializar BD?)
  └─ .env (¿Qué variables?)
```

---

## 🔍 Búsqueda Rápida

### ¿Cómo...?

| Pregunta | Documento |
|----------|-----------|
| ...instalar el proyecto? | [INSTALACION.md](INSTALACION.md) |
| ...ejecutar el servidor? | [REFERENCIA_RAPIDA.md](REFERENCIA_RAPIDA.md) |
| ...crear un endpoint? | [DESARROLLO.md](DESARROLLO.md) |
| ...usar la API? | [API.md](API.md) |
| ...entender la arquitectura? | [ARQUITECTURA.md](ARQUITECTURA.md) |
| ...solucionar problemas? | [REFERENCIA_RAPIDA.md](REFERENCIA_RAPIDA.md) |
| ...configurar variables? | [INSTALACION.md](INSTALACION.md) |
| ...hacer un deploy? | [ARQUITECTURA.md](ARQUITECTURA.md) |

---

## 📈 Progresión de Lectura Recomendada

### Semana 1: Fundamentos
- [ ] Leer README.md
- [ ] Seguir INSTALACION.md
- [ ] Explorar REFERENCIA_RAPIDA.md
- [ ] Acceder a http://localhost:3000

### Semana 2: Desarrollo
- [ ] Estudiar ARQUITECTURA.md
- [ ] Leer DESARROLLO.md
- [ ] Revisar API.md
- [ ] Hacer cambios simples

### Semana 3: Profundización
- [ ] Entender flujo completo
- [ ] Crear nuevos endpoints
- [ ] Escribir tests
- [ ] Optimizar código

---

## 🎓 Recursos de Aprendizaje

### Documentación Oficial
- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy](https://docs.sqlalchemy.org/)
- [React](https://react.dev/)
- [PostgreSQL](https://www.postgresql.org/docs/)
- [Docker](https://docs.docker.com/)

### Herramientas Útiles
- [Postman](https://www.postman.com/) - Testing API
- [DBeaver](https://dbeaver.io/) - Gestor BD
- [VS Code](https://code.visualstudio.com/) - Editor
- [Docker Desktop](https://www.docker.com/products/docker-desktop) - Orquestación

---

## 📞 Soporte

### Problemas Comunes
- Ver: [REFERENCIA_RAPIDA.md - Solución Rápida de Problemas](REFERENCIA_RAPIDA.md#-solución-rápida-de-problemas)

### Documentación Específica
- Buscar en los archivos .md correspondientes
- Revisar comentarios en el código
- Consultar logs: `docker-compose logs`

### Contacto
- Equipo de desarrollo
- Issues en repositorio
- Documentación en línea

---

## 📝 Notas Importantes

1. **Mantener actualizado**: Actualizar documentación con cambios
2. **Ejemplos**: Incluir ejemplos prácticos en documentación
3. **Claridad**: Usar lenguaje claro y conciso
4. **Estructura**: Mantener estructura consistente
5. **Links**: Verificar que los links funcionan

---

## 🔄 Actualización de Documentación

Cuando hagas cambios:
1. Actualiza el archivo .md correspondiente
2. Actualiza este INDICE.md si es necesario
3. Verifica que los links funcionan
4. Commit con mensaje descriptivo

---

**Última actualización**: Noviembre 2025  
**Versión**: 2.0  
**Estado**: ✅ Completa
