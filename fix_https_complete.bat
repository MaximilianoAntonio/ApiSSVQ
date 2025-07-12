@echo off
echo ========================================
echo SOLUCION COMPLETA PARA ERROR HTTPS
echo ========================================
echo.

echo [PASO 1] Instalando herramientas necesarias...
echo.

:: Instalar Azure CLI
echo Instalando Azure CLI...
winget install -e --id Microsoft.AzureCLI --silent
if %errorlevel% neq 0 (
    echo [WARNING] Error instalando Azure CLI, pero continuando...
)

:: Instalar Azure Developer CLI  
echo Instalando Azure Developer CLI...
winget install -e --id Microsoft.Azd --silent
if %errorlevel% neq 0 (
    echo [WARNING] Error instalando Azure Developer CLI, pero continuando...
)

echo.
echo [PASO 2] Configurando autenticación...
echo.

:: Refrescar PATH para que reconozca azd
set "PATH=%PATH%;%USERPROFILE%\.azd\bin"
set "PATH=%PATH%;C:\Program Files\Microsoft Azure CLI"

:: Verificar si azd está disponible
where azd >nul 2>nul
if %errorlevel% neq 0 (
    echo [INFO] Azure CLI no disponible en esta sesión.
    echo [INFO] Cierra y vuelve a abrir el terminal, luego ejecuta:
    echo         azd auth login
    echo         azd deploy
    echo.
    goto :configuracion_frontend
)

:: Autenticación
echo Configurando autenticación...
azd auth login

echo.
echo [PASO 3] Desplegando correcciones...
echo.

azd deploy

:configuracion_frontend
echo.
echo ========================================
echo CONFIGURACION DEL FRONTEND REQUERIDA
echo ========================================
echo.
echo El problema principal esta en tu FRONTEND.
echo Necesitas cambiar las URLs de HTTP a HTTPS.
echo.
echo En tu aplicación frontend, busca y cambia:
echo.
echo ❌ INCORRECTO:
echo    const API_BASE_URL = 'http://apissvq.azurewebsites.net/api';
echo.
echo ✅ CORRECTO:
echo    const API_BASE_URL = 'https://apissvq.azurewebsites.net/api';
echo.
echo Archivos que debes revisar en tu frontend:
echo - vehicleService.js
echo - axios/config
echo - Variables de entorno (.env)
echo - Archivos de configuración
echo.
echo BUSCA ESTAS LINEAS Y CAMBIALAS:
echo - http://apissvq.azurewebsites.net  →  https://apissvq.azurewebsites.net
echo - Cualquier referencia HTTP a tu API
echo.

echo ========================================
echo VERIFICACION
echo ========================================
echo.
echo 1. Verifica que tu API funciona en HTTPS:
echo    https://apissvq.azurewebsites.net/health/
echo.
echo 2. Actualiza tu frontend para usar HTTPS
echo.
echo 3. Prueba la aplicación
echo.

pause
