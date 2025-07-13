#!/usr/bin/env python
"""
Script para probar el endpoint del dashboard.
Ejecutar desde el directorio raíz del proyecto Django.

Uso:
python test_dashboard_endpoint.py

Asegúrate de tener el servidor Django corriendo en localhost:8000
"""

import requests
import json
import sys
from datetime import datetime

def test_dashboard_endpoint():
    """Probar el endpoint del dashboard."""
    
    print("=== PRUEBA DEL ENDPOINT DASHBOARD ===\n")
    
    # Configuración
    BASE_URL = "http://localhost:8000/api"
    
    # Paso 1: Obtener token de autenticación
    print("1. Obteniendo token de autenticación...")
    
    login_data = {
        'username': 'admin',  # Cambiar por un usuario real
        'password': 'admin123'  # Cambiar por la contraseña real
    }
    
    try:
        login_response = requests.post(f"{BASE_URL}/get-token/", data=login_data)
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            token = token_data['token']
            print(f"✓ Token obtenido: {token[:20]}...")
        else:
            print(f"✗ Error al obtener token: {login_response.status_code}")
            print(f"Respuesta: {login_response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Error de conexión al obtener token: {e}")
        return False
    
    # Paso 2: Probar endpoint del dashboard
    print("\n2. Probando endpoint del dashboard...")
    
    headers = {
        'Authorization': f'Token {token}',
        'Content-Type': 'application/json'
    }
    
    try:
        dashboard_response = requests.get(
            f"{BASE_URL}/dashboard/stats/", 
            headers=headers
        )
        
        if dashboard_response.status_code == 200:
            print("✓ Endpoint del dashboard funcionando correctamente")
            
            # Analizar respuesta
            dashboard_data = dashboard_response.json()
            
            print("\n3. Análisis de la respuesta:")
            print(f"   - Timestamp: {dashboard_data.get('timestamp', 'N/A')}")
            
            # Resumen general
            resumen = dashboard_data.get('resumen_general', {})
            print(f"\n   RESUMEN GENERAL:")
            print(f"   - Total vehículos: {resumen.get('total_vehiculos', 0)}")
            print(f"   - Total conductores: {resumen.get('total_conductores', 0)}")
            print(f"   - Total asignaciones: {resumen.get('total_asignaciones', 0)}")
            print(f"   - Vehículos disponibles: {resumen.get('vehiculos_disponibles', 0)}")
            print(f"   - Conductores disponibles: {resumen.get('conductores_disponibles', 0)}")
            print(f"   - Asignaciones activas: {resumen.get('asignaciones_activas', 0)}")
            
            # Vehículos
            vehiculos = dashboard_data.get('vehiculos', {})
            print(f"\n   VEHÍCULOS:")
            print(f"   - Por estado: {vehiculos.get('por_estado', {})}")
            print(f"   - Por tipo: {vehiculos.get('por_tipo', {})}")
            print(f"   - Top performance: {len(vehiculos.get('performance_top', []))} vehículos")
            
            # Conductores
            conductores = dashboard_data.get('conductores', {})
            print(f"\n   CONDUCTORES:")
            print(f"   - Por disponibilidad: {conductores.get('por_disponibilidad', {})}")
            print(f"   - Vencimientos próximos: {len(conductores.get('vencimientos_proximos', []))}")
            print(f"   - Con licencia vigente: {conductores.get('total_con_licencia_vigente', 0)}")
            
            # Asignaciones
            asignaciones = dashboard_data.get('asignaciones', {})
            print(f"\n   ASIGNACIONES:")
            print(f"   - Por estado: {asignaciones.get('por_estado', {})}")
            estadisticas_mensuales = asignaciones.get('estadisticas_mensuales', {})
            print(f"   - Este mes: {estadisticas_mensuales.get('total_asignaciones', 0)} asignaciones")
            print(f"   - Distancia total mes: {estadisticas_mensuales.get('distancia_total', 0):.1f} km")
            
            # Alertas
            alertas = dashboard_data.get('alertas', {})
            print(f"\n   ALERTAS:")
            print(f"   - Licencias por vencer: {alertas.get('licencias_por_vencer', 0)}")
            print(f"   - Vehículos en mantenimiento: {alertas.get('vehiculos_en_mantenimiento', 0)}")
            print(f"   - Asignaciones fallidas: {alertas.get('asignaciones_fallidas', 0)}")
            
            # Guardar respuesta completa
            print(f"\n4. Guardando respuesta completa en 'dashboard_response.json'...")
            with open('dashboard_response.json', 'w', encoding='utf-8') as f:
                json.dump(dashboard_data, f, indent=2, ensure_ascii=False, default=str)
            print("✓ Respuesta guardada")
            
            return True
            
        else:
            print(f"✗ Error en endpoint del dashboard: {dashboard_response.status_code}")
            print(f"Respuesta: {dashboard_response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Error de conexión al probar dashboard: {e}")
        return False

def test_dashboard_performance():
    """Probar performance del endpoint haciendo múltiples requests."""
    
    print("\n=== PRUEBA DE PERFORMANCE ===\n")
    
    BASE_URL = "http://localhost:8000/api"
    
    # Obtener token (reutilizar lógica anterior)
    login_data = {
        'username': 'admin',
        'password': 'admin123'
    }
    
    try:
        login_response = requests.post(f"{BASE_URL}/get-token/", data=login_data)
        token = login_response.json()['token']
        
        headers = {
            'Authorization': f'Token {token}',
            'Content-Type': 'application/json'
        }
        
        # Hacer 10 requests y medir tiempo
        import time
        tiempos = []
        
        print("Ejecutando 10 requests para medir performance...")
        
        for i in range(10):
            start_time = time.time()
            response = requests.get(f"{BASE_URL}/dashboard/stats/", headers=headers)
            end_time = time.time()
            
            if response.status_code == 200:
                tiempo_respuesta = (end_time - start_time) * 1000  # en milisegundos
                tiempos.append(tiempo_respuesta)
                print(f"Request {i+1}: {tiempo_respuesta:.2f}ms")
            else:
                print(f"Request {i+1}: ERROR {response.status_code}")
        
        if tiempos:
            print(f"\nRESULTADOS DE PERFORMANCE:")
            print(f"- Tiempo promedio: {sum(tiempos)/len(tiempos):.2f}ms")
            print(f"- Tiempo mínimo: {min(tiempos):.2f}ms")
            print(f"- Tiempo máximo: {max(tiempos):.2f}ms")
            
            if sum(tiempos)/len(tiempos) < 500:  # menos de 500ms
                print("✓ Performance aceptable")
            else:
                print("⚠ Performance podría mejorarse")
                
    except Exception as e:
        print(f"Error en test de performance: {e}")

if __name__ == "__main__":
    print(f"Iniciando pruebas del dashboard - {datetime.now()}")
    
    # Test básico
    success = test_dashboard_endpoint()
    
    if success:
        # Test de performance solo si el básico fue exitoso
        test_dashboard_performance()
        print(f"\n=== PRUEBAS COMPLETADAS ===")
    else:
        print(f"\n=== PRUEBAS FALLIDAS ===")
        print("Verifica que:")
        print("1. El servidor Django esté corriendo (python manage.py runserver)")
        print("2. Las credenciales de usuario sean correctas")
        print("3. El endpoint esté configurado correctamente")
        sys.exit(1)
