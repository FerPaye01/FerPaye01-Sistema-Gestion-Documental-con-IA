# 🔐 Guía de Seguridad - SGD

## ⚠️ CRÍTICO: Antes de Subir a GitHub

### 1. Nunca Subas Archivos `.env`

El archivo `.env` contiene credenciales sensibles:
- Google API Keys
- Contraseñas de base de datos
- Claves de acceso MinIO
- Tokens de autenticación

**Estos archivos NUNCA deben estar en GitHub.**

### 2. Usa `.env.example`

Se proporciona `backend/.env.example` como plantilla.

**Para configurar localmente:**
```bash
cp backend/.env.example backend/.env
# Editar backend/.env con tus credenciales reales
```

### 3. Verifica `.gitignore`

El archivo `.gitignore` debe incluir:
```
.env
.env.local
backend/.env
frontend/.env
```

**Verifica que está configurado:**
```bash
git check-ignore backend/.env
# Debe devolver: backend/.env
```

---

## 🔑 Gestión de Credenciales

### Google API Key

**Obtener:**
1. Ir a https://makersuite.google.com/app/apikey
2. Crear nueva API Key
3. Copiar en `backend/.env`

**Seguridad:**
- ❌ NO compartir públicamente
- ❌ NO subir a GitHub
- ✅ Usar variables de entorno
- ✅ Rotar regularmente

### Credenciales de Base de Datos

**Desarrollo:**
```env
DATABASE_URL=postgresql://sgd_user:sgd_pass@postgres:5432/sgd_ugel
```

**Producción:**
- Cambiar contraseña por defecto
- Usar credenciales fuertes
- Almacenar en gestor de secretos

### MinIO

**Desarrollo:**
```env
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
```

**Producción:**
- Cambiar credenciales por defecto
- Usar credenciales fuertes
- Habilitar HTTPS (MINIO_SECURE=true)

---

## 🛡️ Checklist de Seguridad Antes de GitHub

- [ ] `.env` NO está en el repositorio
- [ ] `.gitignore` incluye `*.env`
- [ ] No hay API Keys en el código
- [ ] No hay contraseñas en comentarios
- [ ] No hay tokens en archivos de configuración
- [ ] `.env.example` está presente como plantilla
- [ ] Documentación de configuración está actualizada

---

## 🔒 Seguridad en Producción

### 1. Variables de Entorno

**Usar gestor de secretos:**
- AWS Secrets Manager
- Azure Key Vault
- HashiCorp Vault
- GitHub Secrets (para CI/CD)

### 2. HTTPS/SSL

```yaml
# docker-compose.yml (producción)
MINIO_SECURE=true
```

### 3. Autenticación API

Implementar:
- JWT tokens
- OAuth2
- API Keys con rotación

### 4. Base de Datos

- Cambiar credenciales por defecto
- Usar conexiones SSL
- Backups encriptados
- Acceso restringido por IP

### 5. Logs

- No loguear credenciales
- Usar niveles de log apropiados
- Centralizar logs (ELK, CloudWatch)

---

## 📋 Archivos Sensibles a Proteger

| Archivo | Contiene | Acción |
|---------|----------|--------|
| `.env` | Credenciales | ❌ NO subir |
| `backend/.env` | API Keys | ❌ NO subir |
| `frontend/.env` | URLs sensibles | ❌ NO subir |
| `.env.example` | Plantilla | ✅ Subir |
| `docker-compose.yml` | Configuración | ✅ Subir |

---

## 🚀 Flujo Seguro para GitHub

### 1. Preparar Repositorio

```bash
# Verificar que .env no está tracked
git status

# Si está, remover del historio
git rm --cached backend/.env
git commit -m "Remove .env from tracking"
```

### 2. Crear `.env.example`

```bash
cp backend/.env backend/.env.example
# Editar .env.example y reemplazar valores sensibles
```

### 3. Actualizar `.gitignore`

```bash
echo "backend/.env" >> .gitignore
git add .gitignore
git commit -m "Update .gitignore to protect .env files"
```

### 4. Verificar Antes de Push

```bash
# Ver qué se va a subir
git diff --cached

# Verificar que no hay .env
git ls-files | grep -E "\.env$"
# No debe devolver nada
```

### 5. Push Seguro

```bash
git push origin main
```

---

## 🔍 Verificación Post-Push

### En GitHub

1. Ir a tu repositorio
2. Verificar que NO hay archivos `.env`
3. Verificar que `.env.example` está presente
4. Revisar commits para credenciales expuestas

### Si Accidentalmente Subiste Credenciales

**ACCIÓN INMEDIATA:**

1. Revocar credenciales expuestas
2. Generar nuevas credenciales
3. Usar `git filter-branch` para limpiar historio
4. Forzar push: `git push --force-with-lease`

**Ejemplo:**
```bash
# Revocar Google API Key
# Generar nueva en https://makersuite.google.com/app/apikey

# Actualizar .env local
# Hacer commit y push
```

---

## 📚 Recursos de Seguridad

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [GitHub Security Best Practices](https://docs.github.com/en/code-security)
- [12 Factor App - Config](https://12factor.net/config)
- [Secrets Management](https://www.vaultproject.io/)

---

## 🆘 Soporte

Si cometiste un error de seguridad:

1. **Revocar credenciales inmediatamente**
2. **Generar nuevas credenciales**
3. **Limpiar historio de Git**
4. **Notificar al equipo**

---

**Recuerda: La seguridad es responsabilidad de todos.**

Nunca compartas credenciales. Nunca subas `.env` a GitHub.

✅ **Seguridad primero, siempre.**
