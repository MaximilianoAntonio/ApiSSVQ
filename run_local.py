#!/usr/bin/env python
"""
Script para ejecutar localmente con SQLite
"""
import os
import subprocess
import sys

def run_local():
    """Ejecutar servidor de desarrollo local"""
    print("🏠 Configurando entorno local con SQLite...")
    
    # No configurar variables de DB para usar SQLite por defecto
    os.environ['DEBUG'] = 'True'
    
    print("📦 Ejecutando migraciones...")
    subprocess.run([sys.executable, "manage.py", "migrate"], check=True)
    
    print("🎨 Recolectando archivos estáticos...")
    subprocess.run([sys.executable, "manage.py", "collectstatic", "--noinput"], check=True)
    
    print("👤 Creando superusuario si no existe...")
    try:
        subprocess.run([
            sys.executable, "manage.py", "shell", "-c",
            "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'admin123')"
        ], check=True)
        print("✅ Superusuario: admin/admin123")
    except:
        print("⚠️  Superusuario ya existe o error creándolo")
    
    print("🚀 Iniciando servidor de desarrollo...")
    print("📍 Admin: http://127.0.0.1:8000/admin/")
    print("📍 API: http://127.0.0.1:8000/api/")
    
    subprocess.run([sys.executable, "manage.py", "runserver"], check=True)

if __name__ == "__main__":
    run_local()
