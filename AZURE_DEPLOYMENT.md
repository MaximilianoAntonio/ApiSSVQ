# Despliegue en Azure - Guía de Configuración

Esta guía te ayudará a desplegar tu API Django "Gestor de Vehículos" en Azure usando Azure Developer CLI (azd).

## Prerrequisitos

1. **Azure Developer CLI (azd)**: [Instalar azd](https://docs.microsoft.com/en-us/azure/developer/azure-developer-cli/install-azd)
2. **Azure CLI**: [Instalar Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
3. **Python 3.11+**
4. **Una suscripción de Azure activa**

## Configuración Inicial

### 1. Autenticación con Azure

```bash
# Iniciar sesión en Azure
azd auth login

# Verificar la suscripción activa
az account show
```

### 2. Configurar Variables de Entorno

Copia el archivo `.env.example` a `.env` y configura las variables:

```bash
cp .env.example .env
```

Edita el archivo `.env` con tus valores:

```bash
# Azure Environment Configuration
AZURE_ENV_NAME=gestor-vehiculos-prod          # Nombre único para tu entorno
AZURE_LOCATION=eastus                         # Región de Azure
AZURE_SUBSCRIPTION_ID=tu-subscription-id     # ID de tu suscripción

# Database Configuration
DATABASE_ADMIN_PASSWORD=TuPasswordSeguro123!  # Password para PostgreSQL

# Django Configuration
DJANGO_SECRET_KEY=tu-secret-key-super-seguro  # Generar una clave segura
DJANGO_DEBUG=False                            # False para producción
CORS_ALLOWED_ORIGINS=https://tu-frontend.com # URLs permitidas para CORS
```

### 3. Generar Django Secret Key

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## Despliegue

### 1. Inicializar el Proyecto

```bash
# Inicializar azd en el directorio del proyecto
azd init

# Cuando se pregunte, selecciona:
# - Use code from current directory
# - Confirm the service name: gestor-vehiculos-api
```

### 2. Desplegar a Azure

```bash
# Provisionar infraestructura y desplegar aplicación
azd up
```

Este comando:
- Crea todos los recursos de Azure (App Service, PostgreSQL, Storage, Key Vault, etc.)
- Despliega tu código Django
- Configura las variables de entorno automáticamente
- Ejecuta las migraciones de Django

### 3. Verificar el Despliegue

```bash
# Ver el estado de la aplicación
azd show

# Ver logs de la aplicación
azd logs
```

## Recursos Creados

El despliegue creará los siguientes recursos en Azure:

- **Resource Group**: Contenedor para todos los recursos
- **App Service Plan**: Plan de hosting (Linux, SKU B1)
- **App Service**: Aplicación web Django
- **PostgreSQL Flexible Server**: Base de datos
- **Storage Account**: Almacenamiento para archivos media
- **Key Vault**: Gestión segura de secretos
- **Application Insights**: Monitoreo y telemetría
- **Log Analytics Workspace**: Centralización de logs

## Configuración Post-Despliegue

### 1. Acceder a la Aplicación

La URL de tu aplicación estará disponible tras el despliegue:
```
https://app-gestor-vehiculos-[hash].azurewebsites.net
```

### 2. Crear Superusuario de Django

```bash
# Conectar al App Service para ejecutar comandos Django
az webapp ssh --name app-gestor-vehiculos-[hash] --resource-group rg-gestor-vehiculos-[env]

# Una vez conectado, ejecutar:
python manage.py createsuperuser
```

### 3. Configurar Dominio Personalizado (Opcional)

Si tienes un dominio personalizado:

```bash
# Configurar dominio personalizado
az webapp config hostname add --webapp-name app-gestor-vehiculos-[hash] --resource-group rg-gestor-vehiculos-[env] --hostname tu-dominio.com
```

## Gestión del Entorno

### Actualizar la Aplicación

```bash
# Desplegar cambios de código
azd deploy

# O renovar toda la infraestructura
azd up
```

### Ver Logs

```bash
# Logs en tiempo real
azd logs --follow

# Logs históricos
az webapp log tail --name app-gestor-vehiculos-[hash] --resource-group rg-gestor-vehiculos-[env]
```

### Gestionar Variables de Entorno

```bash
# Ver configuración actual
az webapp config appsettings list --name app-gestor-vehiculos-[hash] --resource-group rg-gestor-vehiculos-[env]

# Actualizar una variable
az webapp config appsettings set --name app-gestor-vehiculos-[hash] --resource-group rg-gestor-vehiculos-[env] --settings "DJANGO_DEBUG=False"
```

### Escalar la Aplicación

```bash
# Escalar horizontalmente (más instancias)
az appservice plan update --name asp-gestor-vehiculos-[hash] --resource-group rg-gestor-vehiculos-[env] --number-of-workers 2

# Escalar verticalmente (más recursos por instancia)
az appservice plan update --name asp-gestor-vehiculos-[hash] --resource-group rg-gestor-vehiculos-[env] --sku S1
```

## Monitoreo

### Application Insights

- Dashboard de métricas disponible en Azure Portal
- Monitoreo de rendimiento automático
- Alertas configurables

### Logs Estructurados

Los logs se envían automáticamente a:
- Application Insights
- Log Analytics Workspace
- Azure Monitor

## Seguridad

### Configuraciones Implementadas

- **HTTPS Obligatorio**: Todas las conexiones redirigidas a HTTPS
- **Managed Identity**: Autenticación sin credenciales hardcodeadas
- **Key Vault**: Gestión segura de secretos
- **Storage Access**: Acceso controlado por RBAC
- **Database**: SSL requerido, firewall configurado
- **CORS**: Configurado según las variables de entorno

### Mejores Prácticas

1. **Nunca hardcodear credenciales** en el código
2. **Usar variables de entorno** para configuración
3. **Rotar secretos regularmente**
4. **Monitorear accesos** y actividad
5. **Mantener dependencias actualizadas**

## Resolución de Problemas

### Problemas Comunes

1. **Error de conexión a la base de datos**:
   ```bash
   # Verificar configuración de firewall
   az postgres flexible-server firewall-rule list --name postgres-[hash] --resource-group rg-gestor-vehiculos-[env]
   ```

2. **Error de autenticación con Storage**:
   ```bash
   # Verificar permisos de Managed Identity
   az role assignment list --assignee [managed-identity-id] --all
   ```

3. **Variables de entorno no configuradas**:
   ```bash
   # Verificar y actualizar app settings
   az webapp config appsettings list --name app-gestor-vehiculos-[hash] --resource-group rg-gestor-vehiculos-[env]
   ```

### Comandos Útiles de Diagnóstico

```bash
# Estado general de recursos
azd show

# Logs detallados
azd logs --follow

# Información de la base de datos
az postgres flexible-server show --name postgres-[hash] --resource-group rg-gestor-vehiculos-[env]

# Estado del App Service
az webapp show --name app-gestor-vehiculos-[hash] --resource-group rg-gestor-vehiculos-[env]
```

## Limpieza de Recursos

Para eliminar todos los recursos y evitar cargos:

```bash
# Eliminar todo el entorno
azd down --force --purge
```

## Soporte y Recursos Adicionales

- [Documentación de Azure App Service](https://docs.microsoft.com/en-us/azure/app-service/)
- [Azure Developer CLI Documentation](https://docs.microsoft.com/en-us/azure/developer/azure-developer-cli/)
- [Django Deployment Best Practices](https://docs.djangoproject.com/en/stable/howto/deployment/)
- [Azure PostgreSQL Documentation](https://docs.microsoft.com/en-us/azure/postgresql/)

---

## Notas Importantes

- **Costos**: Los recursos creados incurren en costos. Revisa la [calculadora de precios de Azure](https://azure.microsoft.com/pricing/calculator/).
- **Escalabilidad**: La configuración inicial usa SKUs básicos. Ajusta según tus necesidades de producción.
- **Backup**: Configura backups automáticos para la base de datos en entornos de producción.
- **SSL Certificates**: Para dominios personalizados, configura certificados SSL apropiados.
