@echo off
echo ==================================================
echo      Gestor Vehiculos - Despliegue a Azure
echo ==================================================
echo.

:: Verificar si Azure CLI está instalado
where az >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Azure CLI no está instalado.
    echo Por favor, instalar desde: https://aka.ms/installazurecliwindows
    echo O usar: winget install -e --id Microsoft.AzureCLI
    pause
    exit /b 1
)

:: Verificar si Azure Developer CLI está instalado
where azd >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Azure Developer CLI no está instalado.
    echo Por favor, instalar usando: winget install -e --id Microsoft.Azd
    pause
    exit /b 1
)

echo [INFO] Verificando autenticación con Azure...
az account show >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] No estás autenticado con Azure CLI
    echo Ejecutando 'az login'...
    az login
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Falló la autenticación con Azure CLI
        pause
        exit /b 1
    )
)

echo [INFO] Verificando autenticación con Azure Developer CLI...
azd auth login --check-status >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] No estás autenticado con Azure Developer CLI
    echo Ejecutando 'azd auth login'...
    azd auth login
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Falló la autenticación con Azure Developer CLI
        pause
        exit /b 1
    )
)

:: Verificar si existe archivo .env
if not exist ".env" (
    echo [WARNING] Archivo .env no encontrado
    echo Copiando .env.example a .env...
    copy .env.example .env
    echo.
    echo [IMPORTANT] Por favor, edita el archivo .env con tus valores reales antes de continuar
    echo Presiona cualquier tecla cuando hayas configurado el archivo .env...
    pause
)

echo [INFO] Iniciando despliegue con Azure Developer CLI...
echo.

:: Ejecutar azd up
azd up

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ==================================================
    echo     ¡Despliegue completado exitosamente!
    echo ==================================================
    echo.
    echo Para ver los logs de la aplicación, ejecuta:
    echo   azd logs
    echo.
    echo Para ver el estado de los recursos, ejecuta:
    echo   azd show
    echo.
    azd show
) else (
    echo.
    echo ==================================================
    echo        Error durante el despliegue
    echo ==================================================
    echo.
    echo Para diagnosticar el problema:
    echo 1. Revisa los logs: azd logs
    echo 2. Verifica la configuración: azd env get-values
    echo 3. Consulta la documentación: AZURE_DEPLOYMENT_GUIDE.md
)

echo.
pause
