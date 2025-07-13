# tests/test_dashboard.py
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from asignaciones.models import Vehiculo, Conductor, Asignacion


class DashboardStatsViewTest(TestCase):
    """
    Tests para el endpoint de estadísticas del dashboard.
    """

    def setUp(self):
        """Configuración inicial para los tests."""
        # Crear usuario y token para autenticación
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.token = Token.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        
        # Crear datos de prueba
        self._create_test_data()

    def _create_test_data(self):
        """Crear datos de prueba para los tests."""
        # Crear vehículos
        self.vehiculo1 = Vehiculo.objects.create(
            marca='Toyota',
            modelo='Corolla',
            patente='ABC123',
            estado='disponible',
            tipo_vehiculo='automovil',
            anio=2020,
            capacidad_pasajeros=4
        )
        
        self.vehiculo2 = Vehiculo.objects.create(
            marca='Ford',
            modelo='Transit',
            patente='XYZ789',
            estado='en_uso',
            tipo_vehiculo='minibus',
            anio=2019,
            capacidad_pasajeros=12
        )
        
        # Crear conductores
        self.conductor1 = Conductor.objects.create(
            nombre='Juan',
            apellido='Pérez',
            numero_licencia='12345678',
            fecha_vencimiento_licencia=timezone.now().date() + timedelta(days=15),
            estado_disponibilidad='disponible'
        )
        
        self.conductor2 = Conductor.objects.create(
            nombre='María',
            apellido='González',
            numero_licencia='87654321',
            fecha_vencimiento_licencia=timezone.now().date() + timedelta(days=60),
            estado_disponibilidad='en_ruta'
        )
        
        # Crear asignaciones
        self.asignacion1 = Asignacion.objects.create(
            vehiculo=self.vehiculo1,
            conductor=self.conductor1,
            destino_descripcion='Hospital Regional',
            fecha_hora_requerida_inicio=timezone.now(),
            req_pasajeros=2,
            estado='activa',
            solicitante_jerarquia=3,
            solicitante_nombre='Dr. Smith'
        )
        
        self.asignacion2 = Asignacion.objects.create(
            vehiculo=self.vehiculo2,
            conductor=self.conductor2,
            destino_descripcion='Municipalidad',
            fecha_hora_requerida_inicio=timezone.now() - timedelta(days=1),
            req_pasajeros=5,
            estado='completada',
            solicitante_jerarquia=2,
            solicitante_nombre='Coordinador López',
            distancia_recorrida_km=25.5
        )

    def test_dashboard_stats_successful_response(self):
        """Test que el endpoint retorna una respuesta exitosa con la estructura correcta."""
        url = reverse('dashboard-stats')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        # Verificar estructura de respuesta
        data = response.json()
        expected_keys = [
            'timestamp',
            'resumen_general',
            'vehiculos',
            'conductores',
            'asignaciones',
            'turnos',
            'alertas'
        ]
        
        for key in expected_keys:
            self.assertIn(key, data)

    def test_dashboard_stats_resumen_general(self):
        """Test que el resumen general contiene los datos correctos."""
        url = reverse('dashboard-stats')
        response = self.client.get(url)
        
        data = response.json()
        resumen = data['resumen_general']
        
        self.assertEqual(resumen['total_vehiculos'], 2)
        self.assertEqual(resumen['total_conductores'], 2)
        self.assertEqual(resumen['total_asignaciones'], 2)
        self.assertEqual(resumen['vehiculos_disponibles'], 1)
        self.assertEqual(resumen['conductores_disponibles'], 1)
        self.assertEqual(resumen['asignaciones_activas'], 1)

    def test_dashboard_stats_vehiculos_por_estado(self):
        """Test que las estadísticas de vehículos por estado son correctas."""
        url = reverse('dashboard-stats')
        response = self.client.get(url)
        
        data = response.json()
        vehiculos_por_estado = data['vehiculos']['por_estado']
        
        self.assertEqual(vehiculos_por_estado.get('disponible', 0), 1)
        self.assertEqual(vehiculos_por_estado.get('en_uso', 0), 1)

    def test_dashboard_stats_conductores_por_disponibilidad(self):
        """Test que las estadísticas de conductores por disponibilidad son correctas."""
        url = reverse('dashboard-stats')
        response = self.client.get(url)
        
        data = response.json()
        conductores_por_disponibilidad = data['conductores']['por_disponibilidad']
        
        self.assertEqual(conductores_por_disponibilidad.get('disponible', 0), 1)
        self.assertEqual(conductores_por_disponibilidad.get('en_ruta', 0), 1)

    def test_dashboard_stats_vencimientos_proximos(self):
        """Test que detecta correctamente las licencias próximas a vencer."""
        url = reverse('dashboard-stats')
        response = self.client.get(url)
        
        data = response.json()
        vencimientos = data['conductores']['vencimientos_proximos']
        
        # Debe haber 1 conductor con licencia próxima a vencer (en 15 días)
        self.assertEqual(len(vencimientos), 1)
        self.assertEqual(vencimientos[0]['nombre'], 'Juan')

    def test_dashboard_stats_unauthorized(self):
        """Test que requiere autenticación."""
        # Remover credenciales
        self.client.credentials()
        
        url = reverse('dashboard-stats')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 401)

    def test_dashboard_stats_performance_optimizada(self):
        """Test que verifica que las consultas están optimizadas."""
        from django.test.utils import override_settings
        from django.db import connection
        
        url = reverse('dashboard-stats')
        
        # Resetear queries
        connection.queries_log.clear()
        
        response = self.client.get(url)
        
        # Verificar que la respuesta es exitosa
        self.assertEqual(response.status_code, 200)
        
        # El número de consultas debería ser razonable (menos de 20)
        num_queries = len(connection.queries)
        self.assertLess(num_queries, 20, 
                       f"Demasiadas consultas DB: {num_queries}. "
                       f"Optimizar agregaciones.")

    def test_dashboard_stats_estadisticas_mensuales(self):
        """Test que las estadísticas mensuales calculan correctamente."""
        url = reverse('dashboard-stats')
        response = self.client.get(url)
        
        data = response.json()
        estadisticas_mensuales = data['asignaciones']['estadisticas_mensuales']
        
        self.assertGreaterEqual(estadisticas_mensuales['total_asignaciones'], 1)
        self.assertGreaterEqual(estadisticas_mensuales['completadas'], 0)
        self.assertIsInstance(estadisticas_mensuales['distancia_total'], (int, float))
        self.assertIsInstance(estadisticas_mensuales['promedio_pasajeros'], (int, float))

    def tearDown(self):
        """Limpieza después de cada test."""
        # Django automaticamente limpia la DB de test
        pass


class DashboardStatsIntegrationTest(TestCase):
    """
    Tests de integración para el dashboard con datos más complejos.
    """

    def setUp(self):
        """Configuración con datos más complejos."""
        self.user = User.objects.create_user(
            username='integration_user',
            password='testpass123'
        )
        self.token = Token.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        
        # Crear múltiples vehículos y conductores para tests más realistas
        self._create_large_dataset()

    def _create_large_dataset(self):
        """Crear un dataset más grande para tests de integración."""
        # Crear 10 vehículos de diferentes tipos y estados
        vehiculos_data = [
            ('Toyota', 'Corolla', 'ABC001', 'disponible', 'automovil'),
            ('Ford', 'Transit', 'ABC002', 'en_uso', 'minibus'),
            ('Chevrolet', 'Spark', 'ABC003', 'mantenimiento', 'automovil'),
            ('Nissan', 'NV200', 'ABC004', 'disponible', 'camioneta'),
            ('Hyundai', 'H1', 'ABC005', 'reservado', 'minibus'),
        ]
        
        for i, (marca, modelo, patente, estado, tipo) in enumerate(vehiculos_data):
            Vehiculo.objects.create(
                marca=marca,
                modelo=modelo,
                patente=patente,
                estado=estado,
                tipo_vehiculo=tipo,
                anio=2018 + i,
                capacidad_pasajeros=4 if tipo == 'automovil' else 8
            )

    def test_dashboard_with_large_dataset(self):
        """Test con un dataset más grande para verificar performance."""
        url = reverse('dashboard-stats')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        
        # Verificar que se manejan correctamente múltiples vehículos
        self.assertEqual(data['resumen_general']['total_vehiculos'], 5)
        
        # Verificar distribución por tipo
        vehiculos_por_tipo = data['vehiculos']['por_tipo']
        self.assertGreater(len(vehiculos_por_tipo), 1)
