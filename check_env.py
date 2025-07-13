#!/usr/bin/env python3
"""
Script para verificar las variables de entorno y la configuración
"""
import os

def check_environment():
    print("=== VERIFICACIÓN DE VARIABLES DE ENTORNO ===")
    
    # Variables importantes
    important_vars = [
        'DEBUG',
        'RAILWAY_ENVIRONMENT', 
        'RAILWAY_PUBLIC_DOMAIN',
        'AZURE_SQL_NAME',
        'AZURE_SQL_USER',
        'AZURE_SQL_HOST',
        'HTTP_X_FORWARDED_PROTO'
    ]
    
    for var in important_vars:
        value = os.environ.get(var, 'NOT SET')
        if var in ['AZURE_SQL_PASSWORD']:
            value = '***HIDDEN***' if value != 'NOT SET' else 'NOT SET'
        print(f"{var}: {value}")
    
    print("\n=== CONFIGURACIÓN DETECTADA ===")
    
    # Detectar entorno
    is_railway = 'RAILWAY_ENVIRONMENT' in os.environ
    is_debug = os.environ.get('DEBUG', 'True').lower() in ['true', '1', 'yes']
    has_forwarded_proto = 'HTTP_X_FORWARDED_PROTO' in os.environ
    
    print(f"¿Es Railway?: {is_railway}")
    print(f"¿DEBUG activado?: {is_debug}")
    print(f"¿X-Forwarded-Proto presente?: {has_forwarded_proto}")
    
    # Recomendaciones
    print("\n=== RECOMENDACIONES ===")
    if is_debug and is_railway:
        print("⚠️  DEBUG está activado en producción. Agregar: DEBUG=False")
    
    if not is_railway:
        print("ℹ️  No se detectó entorno Railway. Agregar: RAILWAY_ENVIRONMENT=production")
    
    print("\n=== VARIABLES REQUERIDAS EN RAILWAY ===")
    required_vars = {
        'DEBUG': 'False',
        'RAILWAY_ENVIRONMENT': 'production',
        'AZURE_SQL_NAME': 'ssvq',
        'AZURE_SQL_USER': 'ssvqdb@ssvq',
        'AZURE_SQL_PASSWORD': 'ssvq1!flota',
        'AZURE_SQL_HOST': 'ssvq.database.windows.net',
        'AZURE_SQL_PORT': '1433'
    }
    
    for var, recommended_value in required_vars.items():
        current = os.environ.get(var, 'NOT SET')
        if var == 'AZURE_SQL_PASSWORD':
            current = '***HIDDEN***' if current != 'NOT SET' else 'NOT SET'
            recommended_value = '***HIDDEN***'
        
        status = "✅" if current != 'NOT SET' else "❌"
        print(f"{status} {var} = {recommended_value}")

if __name__ == "__main__":
    check_environment()
