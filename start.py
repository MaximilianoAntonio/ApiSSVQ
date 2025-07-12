#!/usr/bin/env python
"""
Script de inicio para Railway
"""
import os
import sys
import subprocess

def run_command(command):
    """Ejecuta un comando y muestra el resultado"""
    print(f"Ejecutando: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print(f"Salida: {result.stdout}")
    if result.stderr:
        print(f"Error: {result.stderr}")
    
    if result.returncode != 0:
        print(f"Comando falló con código: {result.returncode}")
        return False
    return True

def main():
    """Función principal de inicialización"""
    print("🚀 Iniciando despliegue en Railway...")
    
    # 1. Verificar variables de entorno importantes
    required_vars = ['DATABASE_URL', 'SECRET_KEY']
    for var in required_vars:
        if not os.environ.get(var):
            print(f"⚠️  Variable de entorno {var} no encontrada")
    
    # 2. Ejecutar migraciones
    print("📦 Ejecutando migraciones...")
    if not run_command("python manage.py migrate --noinput"):
        print("❌ Error en migraciones")
        sys.exit(1)
    
    # 3. Recolectar archivos estáticos
    print("🎨 Recolectando archivos estáticos...")
    if not run_command("python manage.py collectstatic --noinput"):
        print("❌ Error recolectando archivos estáticos")
        sys.exit(1)
    
    # 4. Crear superusuario si no existe
    print("👤 Verificando superusuario...")
    run_command("python manage.py shell -c \"from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(is_superuser=True).exists() or User.objects.create_superuser('admin', 'admin@example.com', 'admin123')\"")
    
    # 5. Iniciar servidor
    port = os.environ.get('PORT', '8000')
    print(f"🌐 Iniciando servidor en puerto {port}...")
    
    gunicorn_cmd = f"gunicorn gestor_vehiculos.wsgi:application --bind 0.0.0.0:{port} --workers 2 --timeout 120"
    os.system(gunicorn_cmd)

if __name__ == "__main__":
    main()
