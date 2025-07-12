@echo off
echo =======================================
echo Actualizando aplicación en Azure
echo =======================================
echo.

:: Verificar si Azure CLI está instalado
where az >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Azure CLI no instalado
    echo Ejecuta: winget install -e --id Microsoft.AzureCLI
    pause
    exit /b 1
)

:: Verificar si Azure Developer CLI está instalado  
where azd >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Azure Developer CLI no instalado
    echo Ejecuta: winget install -e --id Microsoft.Azd
    pause
    exit /b 1
)

:: Verificar autenticación
azd auth login --check-status >nul 2>nul
if %errorlevel% neq 0 (
    echo [WARNING] No autenticado en Azure Developer CLI
    echo Ejecutando autenticación...
    azd auth login
    if %errorlevel% neq 0 (
        echo [ERROR] Falló la autenticación
        pause
        exit /b 1
    )
)

echo [INFO] Desplegando solo la aplicación (sin infraestructura)...
azd deploy

if %errorlevel% equ 0 (
    echo.
    echo =======================================
    echo ✅ Aplicación actualizada exitosamente
    echo =======================================
    echo.
    echo Verifica tu aplicación en:
    azd show | findstr "SERVICE_GESTORVEHICULOS_URI"
    echo.
    echo Para ver logs en tiempo real:
    echo azd logs --follow
    echo.
) else (
    echo.
    echo =======================================
    echo ❌ Error en la actualización
    echo =======================================
    echo.
    echo Para ver detalles del error:
    echo azd logs
    echo.
)

pause
