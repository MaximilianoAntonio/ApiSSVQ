#!/usr/bin/env python
"""
Script de inicio para Railway
"""
import os
import sys
import subprocess
import django

def run_command(command, shell=True):
    """Ejecuta un comando y muestra el resultado"""
    print(f"🔧 Ejecutando: {command}")
    result = subprocess.run(command, shell=shell, capture_output=True, text=True)
    
    if result.stdout:
        print(f"✅ Salida: {result.stdout}")
    if result.stderr:
        print(f"⚠️  Error: {result.stderr}")
    
    if result.returncode != 0:
        print(f"❌ Comando falló con código: {result.returncode}")
        return False
    return True

def setup_django():
    """Configurar Django"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestor_vehiculos.settings')
    try:
        django.setup()
        return True
    except Exception as e:
        print(f"❌ Error configurando Django: {e}")
        return False

def main():
    """Función principal de inicialización"""
    print("🚀 Iniciando despliegue en Railway...")
    
    # 1. Verificar variables de entorno importantes
    print("🔍 Verificando variables de entorno...")
    required_vars = ['SECRET_KEY']
    for var in required_vars:
        if not os.environ.get(var):
            print(f"⚠️  Variable de entorno {var} no encontrada")
        else:
            print(f"✅ Variable {var} configurada")
    
    # Configurar Django
    if not setup_django():
        sys.exit(1)
    
    # 2. Verificar si necesitamos migraciones
    print("📦 Verificando migraciones...")
    if not run_command("python manage.py showmigrations --plan"):
        print("❌ Error verificando migraciones")
    
    # 3. Ejecutar migraciones
    print("📦 Ejecutando migraciones...")
    if not run_command("python manage.py migrate --noinput"):
        print("❌ Error en migraciones")
        # No salir aquí, continuar
    
    # 4. Recolectar archivos estáticos
    print("🎨 Recolectando archivos estáticos...")
    if not run_command("python manage.py collectstatic --noinput --clear"):
        print("❌ Error recolectando archivos estáticos")
        # No salir aquí, continuar
    
    # 5. Crear superusuario si no existe (opcional)
    print("👤 Verificando superusuario...")
    try:
        create_superuser_cmd = """
from django.contrib.auth import get_user_model;
User = get_user_model();
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123');
    print('Superusuario creado: admin/admin123')
else:
    print('Superusuario ya existe')
"""
        run_command(f'python manage.py shell -c "{create_superuser_cmd}"')
    except Exception as e:
        print(f"⚠️  No se pudo crear superusuario: {e}")
    
    # 6. Iniciar servidor
    port = os.environ.get('PORT', '8000')
    print(f"🌐 Iniciando servidor en puerto {port}...")
    
    # Configuración optimizada para Railway
    gunicorn_cmd = [
        'gunicorn',
        'gestor_vehiculos.wsgi:application',
        '--bind', f'0.0.0.0:{port}',
        '--workers', '2',
        '--timeout', '120',
        '--keep-alive', '2',
        '--max-requests', '1000',
        '--max-requests-jitter', '100',
        '--access-logfile', '-',
        '--error-logfile', '-',
        '--log-level', 'info'
    ]
    
    print(f"🚀 Comando final: {' '.join(gunicorn_cmd)}")
    
    # Ejecutar Gunicorn
    try:
        subprocess.run(gunicorn_cmd, check=True)
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido por el usuario")
    except Exception as e:
        print(f"❌ Error ejecutando servidor: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
