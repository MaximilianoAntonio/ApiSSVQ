# Guía de Instalación y Despliegue de Azure

## Paso 1: Instalar Azure CLI

### Windows (PowerShell como Administrador):
```powershell
# Opción 1: Usando winget (recomendado)
winget install -e --id Microsoft.AzureCLI

# Opción 2: Usando MSI Installer
# Descargar de: https://aka.ms/installazurecliwindows
```

### Verificar instalación:
```bash
az --version
```

## Paso 2: Instalar Azure Developer CLI (azd)

### Windows (PowerShell como Administrador):
```powershell
# Opción 1: Usando winget (recomendado)
winget install -e --id Microsoft.Azd

# Opción 2: Usando PowerShell script
powershell -ex AllSigned -c "Invoke-RestMethod 'https://aka.ms/install-azd.ps1' | Invoke-Expression"
```

### Verificar instalación:
```bash
azd version
```

## Paso 3: Autenticarse con Azure

```bash
# Autenticarse con Azure CLI
az login

# Autenticarse con Azure Developer CLI
azd auth login
```

## Paso 4: Configurar variables de entorno

Crear un archivo `.env` en la raíz del proyecto con:

```env
AZURE_ENV_NAME=gestor-vehiculos-dev
AZURE_LOCATION=eastus
AZURE_SUBSCRIPTION_ID=tu-subscription-id

DATABASE_ADMIN_PASSWORD=TuPasswordSegura123!
DJANGO_SECRET_KEY=tu-secret-key-muy-segura-aqui
DJANGO_DEBUG=False
CORS_ALLOWED_ORIGINS=*
```

## Paso 5: Desplegar la aplicación

```bash
# Inicializar el proyecto (solo la primera vez)
azd init

# Provisionar infraestructura y desplegar aplicación
azd up

# Para actualizaciones posteriores
azd deploy
```

## Paso 6: Verificar el despliegue

```bash
# Ver logs de la aplicación
azd logs

# Ver estado de los recursos
azd show
```

## Comandos útiles adicionales

```bash
# Ver el estado de la infraestructura
azd show

# Eliminar todos los recursos (¡cuidado!)
azd down

# Reiniciar la aplicación
azd deploy --force

# Ver variables de entorno configuradas
azd env get-values
```

## Solución de problemas comunes

1. **Error de autenticación**: Ejecutar `az login` y `azd auth login`
2. **Error de permisos**: Verificar que tienes permisos de Contributor en la suscripción
3. **Error de cuota**: Verificar que tienes cuota disponible en la región seleccionada
4. **Error de configuración**: Verificar que todas las variables de entorno están configuradas

## Enlaces útiles

- [Documentación Azure CLI](https://docs.microsoft.com/en-us/cli/azure/)
- [Documentación Azure Developer CLI](https://docs.microsoft.com/en-us/azure/developer/azure-developer-cli/)
- [Troubleshooting Guide](https://docs.microsoft.com/en-us/azure/developer/azure-developer-cli/troubleshoot)
