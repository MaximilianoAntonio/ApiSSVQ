#!/usr/bin/env python
"""
Script para diagnosticar error 500 en Railway sin cambiar la base de datos.
Ejecutar desde el directorio raíz del proyecto Django.

Uso:
python diagnose_railway_error.py
"""

import os
import sys
import subprocess
from pathlib import Path

def print_section(title):
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print('='*60)

def check_django_setup():
    """Verificar que Django esté configurado correctamente."""
    print_section("VERIFICACIÓN DE DJANGO")
    
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestor_vehiculos.settings')
        import django
        django.setup()
        print("✅ Django configurado correctamente")
        return True
    except Exception as e:
        print(f"❌ Error configurando Django: {e}")
        return False

def check_imports():
    """Verificar que todos los imports necesarios funcionen."""
    print_section("VERIFICACIÓN DE IMPORTS")
    
    imports_to_test = [
        ('django.db.models', 'Count, Q, Avg, Sum'),
        ('rest_framework', 'APIView, Response, status'),
        ('asignaciones.models', 'Vehiculo, Conductor, Asignacion'),
        ('asignaciones.serializers', 'VehiculoSerializer'),
        ('django.utils', 'timezone'),
        ('datetime', 'datetime, timedelta'),
    ]
    
    all_imports_ok = True
    
    for module, components in imports_to_test:
        try:
            __import__(module)
            print(f"✅ {module} - OK")
        except ImportError as e:
            print(f"❌ {module} - ERROR: {e}")
            all_imports_ok = False
    
    return all_imports_ok

def check_models():
    """Verificar que los modelos sean accesibles."""
    print_section("VERIFICACIÓN DE MODELOS")
    
    try:
        from asignaciones.models import Vehiculo, Conductor, Asignacion, RegistroTurno
        
        # Test básico de cada modelo
        models_to_test = [
            ('Vehiculo', Vehiculo),
            ('Conductor', Conductor),
            ('Asignacion', Asignacion),
            ('RegistroTurno', RegistroTurno),
        ]
        
        for name, model in models_to_test:
            try:
                count = model.objects.count()
                print(f"✅ {name} - {count} registros")
            except Exception as e:
                print(f"❌ {name} - ERROR: {e}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error importando modelos: {e}")
        return False

def check_dashboard_views():
    """Verificar que las vistas del dashboard se puedan importar."""
    print_section("VERIFICACIÓN DE VISTAS DEL DASHBOARD")
    
    try:
        from asignaciones.views import DashboardStatsView, DashboardStatsViewSafe
        print("✅ DashboardStatsView importada correctamente")
        print("✅ DashboardStatsViewSafe importada correctamente")
        return True
    except Exception as e:
        print(f"❌ Error importando vistas del dashboard: {e}")
        return False

def check_settings():
    """Verificar configuraciones críticas."""
    print_section("VERIFICACIÓN DE SETTINGS")
    
    try:
        from django.conf import settings
        
        critical_settings = [
            'SECRET_KEY',
            'DEBUG',
            'ALLOWED_HOSTS',
            'INSTALLED_APPS',
            'MIDDLEWARE',
            'DATABASES',
        ]
        
        for setting in critical_settings:
            if hasattr(settings, setting):
                value = getattr(settings, setting)
                if setting == 'SECRET_KEY':
                    print(f"✅ {setting} - Configurado ({'*' * 20})")
                elif setting == 'DATABASES':
                    engine = value.get('default', {}).get('ENGINE', 'No configurado')
                    print(f"✅ {setting} - Engine: {engine}")
                else:
                    print(f"✅ {setting} - {value}")
            else:
                print(f"❌ {setting} - NO CONFIGURADO")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verificando settings: {e}")
        return False

def check_url_patterns():
    """Verificar que las URLs estén configuradas correctamente."""
    print_section("VERIFICACIÓN DE URLs")
    
    try:
        from django.urls import reverse
        
        urls_to_test = [
            'dashboard-stats',
            'dashboard-stats-safe',
            'get-token',
            'user-groups',
        ]
        
        for url_name in urls_to_test:
            try:
                url = reverse(url_name)
                print(f"✅ {url_name} - {url}")
            except Exception as e:
                print(f"❌ {url_name} - ERROR: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verificando URLs: {e}")
        return False

def test_safe_dashboard():
    """Probar la vista segura del dashboard."""
    print_section("PRUEBA DE DASHBOARD SEGURO")
    
    try:
        from django.test import RequestFactory
        from django.contrib.auth.models import User
        from asignaciones.views import DashboardStatsViewSafe
        
        # Crear request factory
        factory = RequestFactory()
        request = factory.get('/api/dashboard/stats/safe/')
        
        # Crear usuario mock
        request.user = User.objects.first()
        if not request.user:
            print("⚠️  No hay usuarios en la base de datos. Creando usuario de prueba...")
            request.user = User.objects.create_user('test', 'test@test.com', 'test123')
        
        # Probar la vista
        view = DashboardStatsViewSafe()
        response = view.get(request)
        
        print(f"✅ Vista DashboardStatsViewSafe - Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Dashboard funciona correctamente")
            return True
        else:
            print(f"❌ Dashboard retornó error: {response.data}")
            return False
        
    except Exception as e:
        print(f"❌ Error probando dashboard: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

def generate_report():
    """Generar reporte de diagnóstico."""
    print_section("REPORTE DE DIAGNÓSTICO")
    
    print("📋 Resumen de verificaciones:")
    
    checks = [
        ("Django Setup", check_django_setup),
        ("Imports", check_imports),
        ("Modelos", check_models),
        ("Vistas Dashboard", check_dashboard_views),
        ("Settings", check_settings),
        ("URLs", check_url_patterns),
        ("Dashboard Seguro", test_safe_dashboard),
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            result = check_func()
            results[name] = result
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} - {name}")
        except Exception as e:
            results[name] = False
            print(f"❌ ERROR - {name}: {e}")
    
    print(f"\n📊 Resultados: {sum(results.values())}/{len(results)} checks pasaron")
    
    # Recomendaciones
    print_section("RECOMENDACIONES")
    
    if not results.get("Django Setup"):
        print("🔧 Problema crítico con Django setup - revisar settings.py")
    
    if not results.get("Imports"):
        print("🔧 Problemas con imports - revisar requirements.txt y dependencias")
    
    if not results.get("Modelos"):
        print("🔧 Problemas con modelos - revisar conexión a base de datos")
    
    if not results.get("Dashboard Seguro"):
        print("🔧 Problema específico con dashboard - usar /api/dashboard/stats/safe/ para debug")
    
    if all(results.values()):
        print("🎉 Todas las verificaciones pasaron. El problema podría ser específico de Railway.")
        print("📝 Próximos pasos:")
        print("   1. Verificar variables de entorno en Railway")
        print("   2. Revisar logs de Railway después del deploy")
        print("   3. Probar endpoint /api/dashboard/stats/safe/ en Railway")

def main():
    print("🚀 DIAGNÓSTICO DE ERROR 500 EN RAILWAY")
    print("Manteniendo configuración de base de datos actual")
    
    # Verificar que estamos en el directorio correcto
    if not Path("manage.py").exists():
        print("❌ Error: No se encontró manage.py. Ejecuta desde el directorio raíz del proyecto.")
        sys.exit(1)
    
    generate_report()
    
    print("\n" + "="*60)
    print("🔍 DIAGNÓSTICO COMPLETADO")
    print("="*60)
    
    print("\n💡 SIGUIENTES PASOS:")
    print("1. Si todas las verificaciones pasan localmente, el problema está en Railway")
    print("2. Verificar variables de entorno en Railway Dashboard")
    print("3. Usar /api/dashboard/stats/safe/ para debugging en Railway")
    print("4. Revisar logs específicos en Railway después del deploy")

if __name__ == "__main__":
    main()
