# 🔒 Solución para Error de Mixed Content (HTTP/HTTPS)

## Problema Identificado

Tu aplicación frontend en `https://ssvqflota.azurewebsites.net` está intentando hacer peticiones HTTP (no seguras) a tu API en `http://apissvq.azurewebsites.net`, lo cual viola la política de Mixed Content Security Policy.

**Error exacto:**
```
The page at 'https://ssvqflota.azurewebsites.net/vehiculos' was loaded over HTTPS, 
but requested an insecure XMLHttpRequest endpoint 'http://apissvq.azurewebsites.net/api/vehiculos/?page=2'. 
This request has been blocked; the content must be served over HTTPS.
```

## ✅ Soluciones Implementadas

### 1. Configuración de Azure App Service
- ✅ `httpsOnly: true` - Fuerza HTTPS en el servidor
- ✅ Headers de seguridad configurados
- ✅ CORS configurado correctamente

### 2. Configuración Django Mejorada
- ✅ `SECURE_SSL_REDIRECT = True` - Redirige HTTP a HTTPS
- ✅ Headers de seguridad HSTS
- ✅ Middleware personalizado para forzar HTTPS

### 3. Endpoints de Debug
- ✅ `/health/` endpoint con información de protocolo

## 🚀 Cómo Aplicar las Correcciones

### Opción 1: Actualización Rápida (Solo App)
```bash
update.bat
```

### Opción 2: Actualización Manual
```bash
# Desplegar solo la aplicación
azd deploy

# Ver logs para verificar
azd logs
```

## 🔍 Verificar la Solución

### 1. Verificar que la API responde en HTTPS
```bash
# Debe responder exitosamente
curl https://apissvq.azurewebsites.net/health/
```

### 2. Verificar información de protocolo
Visita: `https://apissvq.azurewebsites.net/health/`

Debes ver algo como:
```json
{
  "status": "healthy",
  "request_info": {
    "is_secure": true,
    "scheme": "https",
    "full_url": "https://apissvq.azurewebsites.net/health/"
  },
  "https_only": true
}
```

## 🔧 Configuración del Frontend

**IMPORTANTE:** También necesitas actualizar tu aplicación frontend para usar HTTPS:

### En tu aplicación frontend, cambia:
```javascript
// ❌ Incorrecto - HTTP
const API_BASE_URL = 'http://apissvq.azurewebsites.net/api';

// ✅ Correcto - HTTPS
const API_BASE_URL = 'https://apissvq.azurewebsites.net/api';
```

### Verifica todas las URLs en tu frontend:
- Configuración de axios/fetch
- Variables de entorno
- Archivos de configuración

## 📊 Headers de Respuesta Esperados

Después de la actualización, tu API debe incluir estos headers:

```http
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
```

## 🐛 Debugging Adicional

### Si el problema persiste:

1. **Verificar logs en tiempo real:**
   ```bash
   azd logs --follow
   ```

2. **Verificar configuración CORS:**
   ```bash
   curl -H "Origin: https://ssvqflota.azurewebsites.net" \
        -H "Access-Control-Request-Method: GET" \
        -H "Access-Control-Request-Headers: Content-Type" \
        -X OPTIONS \
        https://apissvq.azurewebsites.net/api/vehiculos/
   ```

3. **Verificar redirección HTTP -> HTTPS:**
   ```bash
   curl -I http://apissvq.azurewebsites.net/api/vehiculos/
   # Debe retornar 301/302 redirect a HTTPS
   ```

## 💡 Puntos Clave

1. **Azure App Service automáticamente proporciona HTTPS** con certificados gestionados
2. **El problema está en el frontend** - debe usar URLs HTTPS
3. **Los middlewares Django** aseguran redirección automática
4. **CORS está configurado** para permitir peticiones cross-origin

## 🎯 Próximos Pasos

1. ✅ Ejecutar `update.bat` para aplicar correcciones
2. 🔄 Actualizar URLs en el frontend a HTTPS
3. 🧪 Verificar que `/health/` responde correctamente
4. 🚀 Probar la aplicación completa

¡Con estos cambios, tu aplicación debe funcionar correctamente con HTTPS! 🎉
