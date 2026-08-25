# Railway Deployment Guide

## Pre-requisitos

- Cuenta en [Railway.app](https://railway.app)
- GitHub account conectada a Railway
- Repository en GitHub (ya configurado)

## Pasos de Deployment

### 1. Crear Proyecto en Railway

```bash
# Opción A: Vía CLI
railway login
railway init
railway up

# Opción B: Vía Web
# 1. Ve a https://railway.app
# 2. Click "New Project"
# 3. "Deploy from GitHub repo"
# 4. Selecciona: vicboma1/claude-ia-mcp-tools-auth
# 5. Autoriza los permisos necesarios
```

### 2. Configurar Environment Variables

En Railway Dashboard:

```
PORT = 5000
FLASK_ENV = production
FLASK_SECRET_KEY = (auto-generated, update for production)
```

### 3. Configurar Secrets (Production)

```
RAILWAY_TOKEN = <tu-railway-token>
```

En GitHub Settings → Secrets:

```
RAILWAY_TOKEN = <token-from-railway>
```

### 4. Verificar Deployment

Una vez desplegado:

```bash
# Obtener URL de Railway
railway open

# O visita el dashboard
https://railway.app/project/...
```

## Testing en Railway

### Test 1: Home Page

```bash
curl https://claude-ia-mcp-tools-auth-staging.up.railway.app/
# Debería retornar HTML con "MCP OAuth Authentication"
```

### Test 2: Check Auth Status

```bash
curl https://claude-ia-mcp-tools-auth-staging.up.railway.app/auth/status
# Respuesta:
# {"authenticated": false}
```

### Test 3: Complete Flow

```bash
# 1. Start auth flow (redirect)
curl -L https://claude-ia-mcp-tools-auth-staging.up.railway.app/auth/start

# 2. Visit auth callback URL in browser
# 3. Copy token from page

# 4. Use token
curl -H "Authorization: Bearer TOKEN" \
  https://claude-ia-mcp-tools-auth-staging.up.railway.app/auth/status
```

## Monitoreo

### Logs en Railway

```bash
# Ver logs en tiempo real
railway logs

# O en Dashboard → Deployments → View Logs
```

### Healthcheck

Railway ejecuta healthcheck automático cada 30 segundos:

```
GET http://localhost:5000/
Expected: 200 OK + HTML
```

## Troubleshooting

### Issue: App crashes en startup

```bash
# Ver logs
railway logs --tail 50

# Posibles causas:
# - Puerto incorrecto
# - Dependencias faltantes
# - Variables de entorno no configuradas
```

### Issue: CSRF token error

```
# Solución: Actualizar FLASK_SECRET_KEY en Railway
FLASK_SECRET_KEY = <nuevo-valor-seguro>
```

### Issue: 502 Bad Gateway

```
# Revisar health check
# Asegurar que puerto 5000 está correcto
# Verificar logs para errores
```

## Continuous Deployment

Después de configurable inicial, cada push a `main`:

```
Git Push → GitHub Actions
         → Run Tests
         → Build Docker Image
         → Deploy to Railway
         → Health Check
         → Done!
```

## Production Checklist

- [ ] FLASK_SECRET_KEY configurado con valor seguro
- [ ] Railway environment set to "production"
- [ ] Logs monitoreados
- [ ] Health checks respondiendo
- [ ] Tokens persistiendo correctamente
- [ ] SSL/HTTPS habilitado (Railway lo hace automáticamente)

## URLs Útiles

- **Dashboard:** https://railway.app
- **Documentation:** https://docs.railway.app
- **Support:** https://railway.app/support
