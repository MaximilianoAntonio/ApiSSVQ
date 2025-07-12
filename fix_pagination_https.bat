@echo off
echo ========================================
echo SOLUCIONANDO PROBLEMA DE PAGINACION HTTP
echo ========================================
echo.

echo [INFO] El problema está en que la paginación de Django 
echo       está devolviendo URLs HTTP en lugar de HTTPS.
echo.
echo [INFO] Soluciones implementadas:
echo       ✅ Paginador personalizado que fuerza HTTPS
echo       ✅ Middleware mejorado para corregir URLs
echo       ✅ Configuración Django para detectar HTTPS
echo       ✅ Variables de entorno Azure específicas
echo.

:: Verificar herramientas
where az >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Azure CLI no instalado
    echo [INFO] Instalando Azure CLI...
    winget install -e --id Microsoft.AzureCLI --silent
)

where azd >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Azure Developer CLI no instalado
    echo [INFO] Instalando Azure Developer CLI...
    winget install -e --id Microsoft.Azd --silent
    echo [INFO] Reinicia el terminal después de la instalación
    pause
    exit /b 0
)

echo [INFO] Desplegando correcciones de paginación...
echo.

:: Configurar PATH
set "PATH=%PATH%;%USERPROFILE%\.azd\bin"

:: Autenticar si es necesario
azd auth login --check-status >nul 2>nul
if %errorlevel% neq 0 (
    echo [INFO] Configurando autenticación...
    azd auth login
)

:: Desplegar solo la aplicación
echo [INFO] Desplegando aplicación con correcciones...
azd deploy

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo ✅ CORRECCIONES APLICADAS EXITOSAMENTE
    echo ========================================
    echo.
    echo [TEST] Verifica que la paginación funciona:
    echo.
    echo 1. Visita: https://apissvq.azurewebsites.net/api/vehiculos/
    echo 2. Las URLs 'next' y 'previous' deben ser HTTPS
    echo 3. Tu frontend ya no debe tener errores Mixed Content
    echo.
    echo [DEBUG] Para ver logs:
    echo azd logs --follow
    echo.
) else (
    echo.
    echo ========================================
    echo ❌ ERROR EN EL DESPLIEGUE
    echo ========================================
    echo.
    echo [DEBUG] Ver logs de error:
    echo azd logs
    echo.
)

pause
