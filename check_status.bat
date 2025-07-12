@echo off
echo ========================================
echo Verificación de estado de despliegue
echo ========================================
echo.

:: Verificar si existe .env
if not exist ".env" (
    echo [ERROR] Archivo .env no encontrado
    echo Ejecuta: copy .env.example .env
    echo Luego edita .env con tus valores
    echo.
    pause
    exit /b 1
)

:: Verificar Azure CLI
where az >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Azure CLI no instalado
    echo Ejecuta: winget install -e --id Microsoft.AzureCLI
    echo.
    pause
    exit /b 1
) else (
    echo [OK] Azure CLI instalado
)

:: Verificar Azure Developer CLI
where azd >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Azure Developer CLI no instalado
    echo Ejecuta: winget install -e --id Microsoft.Azd
    echo.
    pause
    exit /b 1
) else (
    echo [OK] Azure Developer CLI instalado
)

:: Verificar autenticación Azure CLI
az account show >nul 2>nul
if %errorlevel% neq 0 (
    echo [WARNING] No autenticado en Azure CLI
    echo Ejecuta: az login
    echo.
) else (
    echo [OK] Azure CLI autenticado
)

:: Verificar autenticación Azure Developer CLI
azd auth login --check-status >nul 2>nul
if %errorlevel% neq 0 (
    echo [WARNING] No autenticado en Azure Developer CLI
    echo Ejecuta: azd auth login
    echo.
) else (
    echo [OK] Azure Developer CLI autenticado
)

:: Verificar archivos de infraestructura
if not exist "infra\main.bicep" (
    echo [ERROR] Archivo de infraestructura faltante: infra\main.bicep
    pause
    exit /b 1
) else (
    echo [OK] Infraestructura preparada
)

:: Verificar azure.yaml
if not exist "azure.yaml" (
    echo [ERROR] Archivo de configuración faltante: azure.yaml
    pause
    exit /b 1
) else (
    echo [OK] Configuración azd preparada
)

:: Verificar requirements.txt
if not exist "requirements.txt" (
    echo [ERROR] Archivo requirements.txt faltante
    pause
    exit /b 1
) else (
    echo [OK] Dependencias de Python preparadas
)

echo.
echo ========================================
echo Estado del proyecto: LISTO PARA DESPLEGAR
echo ========================================
echo.
echo Siguiente paso: Ejecutar deploy.bat
echo.
pause
