# Gestor de Vehículos - API REST

Una aplicación Django REST API para la gestión de asignaciones de vehículos, desplegada en Azure.

## 🚀 Despliegue Rápido en Azure

### Prerequisitos
- Windows 10/11 con PowerShell
- Python 3.11 o superior
- Git

### Opción 1: Despliegue Automático (Recomendado)

1. **Ejecutar el script de despliegue**:
   ```cmd
   deploy.bat
   ```
   
   Este script automáticamente:
   - Verifica e instala las herramientas necesarias
   - Configura la autenticación
   - Despliega la aplicación a Azure

### Opción 2: Despliegue Manual

1. **Instalar Azure CLI**:
   ```powershell
   winget install -e --id Microsoft.AzureCLI
   ```

2. **Instalar Azure Developer CLI**:
   ```powershell
   winget install -e --id Microsoft.Azd
   ```

3. **Autenticarse**:
   ```bash
   az login
   azd auth login
   ```

4. **Configurar variables de entorno**:
   ```bash
   cp .env.example .env
   # Editar .env con tus valores
   ```

5. **Desplegar**:
   ```bash
   azd up
   ```

## 📋 Configuración

### Variables de Entorno Requeridas

Edita el archivo `.env` con estos valores:

```env
AZURE_ENV_NAME=gestor-vehiculos-dev
AZURE_LOCATION=eastus
AZURE_SUBSCRIPTION_ID=tu-subscription-id

DATABASE_ADMIN_PASSWORD=TuPasswordSegura123!
DJANGO_SECRET_KEY=tu-secret-key-muy-segura
DJANGO_DEBUG=False
CORS_ALLOWED_ORIGINS=*
```

### Generar Django Secret Key

```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## 🏗️ Arquitectura Azure

La aplicación despliega los siguientes recursos en Azure:

- **App Service**: Hospedaje de la aplicación Django
- **PostgreSQL Flexible Server**: Base de datos
- **Storage Account**: Archivos multimedia
- **Key Vault**: Gestión de secretos
- **Application Insights**: Monitoreo y logs
- **Log Analytics Workspace**: Centralización de logs

## 🔧 Comandos Útiles

```bash
# Ver logs de la aplicación
azd logs

# Ver estado de recursos
azd show

# Actualizar solo la aplicación
azd deploy

# Eliminar todos los recursos
azd down

# Ver variables de entorno
azd env get-values
```

## 📖 API Endpoints

Una vez desplegado, la API estará disponible en: `https://tu-app.azurewebsites.net/api/`

### Endpoints principales:
- `GET /health/` - Health check
- `GET /api/asignaciones/` - Lista de asignaciones
- `GET /api/conductores/` - Lista de conductores
- `GET /api/vehiculos/` - Lista de vehículos
- `POST /api/asignaciones/` - Crear nueva asignación

## 🐛 Solución de Problemas

### Error: "Mixed Content" - HTTP/HTTPS
Si ves este error:
```
The page was loaded over HTTPS, but requested an insecure XMLHttpRequest endpoint 'http://...'
```

**Solución rápida:**
1. Ejecutar: `update.bat`
2. Actualizar URLs del frontend a HTTPS
3. Ver guía completa: [HTTPS_FIX_GUIDE.md](HTTPS_FIX_GUIDE.md)

### Error: "Application Error"
1. Revisar logs: `azd logs`
2. Verificar configuración de base de datos
3. Verificar variables de entorno

### Error de autenticación
```bash
az login
azd auth login
```

### Error de permisos
- Verificar que tienes rol "Contributor" en la suscripción
- Verificar que la suscripción está activa

### Error de cuota
- Verificar cuota disponible en la región
- Considerar cambiar región en `.env`

## 🔧 Comandos de Mantenimiento

```bash
# Actualizar solo la aplicación (recomendado para cambios de código)
update.bat

# Ver logs en tiempo real
azd logs --follow

# Verificar estado de la aplicación
https://tu-app.azurewebsites.net/health/

## 📚 Documentación Adicional

- [Guía completa de despliegue](AZURE_DEPLOYMENT_GUIDE.md)
- [Documentación Azure CLI](https://docs.microsoft.com/en-us/cli/azure/)
- [Documentación Azure Developer CLI](https://docs.microsoft.com/en-us/azure/developer/azure-developer-cli/)

## 🤝 Contribuir

1. Fork el proyecto
2. Crear branch para feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Ver `LICENSE` para más detalles.
