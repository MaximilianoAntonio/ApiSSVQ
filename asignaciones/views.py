# asignaciones/views.py
from django.shortcuts import render
from django.contrib.auth.models import Group
from django.utils import timezone
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
import requests
from django.http import JsonResponse
from django.db.models import Count, Q, Avg, Sum, Case, When, IntegerField
from datetime import datetime, timedelta
from django.db.models.functions import TruncDate, Extract

from .models import Vehiculo, Conductor, Asignacion, RegistroTurno
from .serializers import (
    VehiculoSerializer,
    ConductorSerializer,
    AsignacionSerializer,
    RegistroTurnoSerializer
)

from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from .services import asignar_vehiculos_automatico_lote

from rest_framework.views import APIView
from rest_framework.filters import SearchFilter, OrderingFilter

class UserGroupView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        groups = list(request.user.groups.values_list('name', flat=True))
        return Response({'groups': groups})

class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        groups = list(user.groups.values_list('name', flat=True))
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'username': user.username,
            'groups': groups,  # <-- Esto es lo importante
        })

@csrf_exempt
def nominatim_proxy(request):
    q = request.GET.get('q', '')
    # Agrega la región al texto de búsqueda para limitar resultados
    full_query = f"{q}, Región de Valparaíso, Chile"
    url = (
        "https://nominatim.openstreetmap.org/search"
        f"?format=json&countrycodes=cl&addressdetails=1&limit=20&q={full_query}"
    )
    r = requests.get(url, headers={'User-Agent': 'asignacion-app'})
    return JsonResponse(r.json(), safe=False)

class VehiculoViewSet(viewsets.ModelViewSet):
    queryset = Vehiculo.objects.all().order_by('marca', 'modelo')
    serializer_class = VehiculoSerializer
    permission_classes = [permissions.AllowAny]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    # Asegúrate que estos campos coincidan con tu modelo Vehiculo actual
    filterset_fields = ['estado', 'marca', 'tipo_vehiculo', 'capacidad_pasajeros']
    search_fields = ['patente', 'modelo', 'marca', 'anio', 'numero_chasis', 'numero_motor'] # Añadidos campos buscables
    ordering_fields = ['marca', 'modelo', 'capacidad_pasajeros', 'estado', 'tipo_vehiculo', 'anio'] # Añadido anio


class ConductorViewSet(viewsets.ModelViewSet):
    queryset = Conductor.objects.all().order_by('apellido', 'nombre')
    serializer_class = ConductorSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['estado_disponibilidad']
    search_fields = ['run', 'nombre', 'apellido', 'numero_licencia']
    ordering_fields = ['apellido', 'nombre', 'estado_disponibilidad']

    @action(detail=True, methods=['post'], url_path='iniciar-turno')
    def iniciar_turno(self, request, pk=None):
        conductor = self.get_object()
        
        # Si el conductor ya está en un turno, no permitir iniciar otro.
        if conductor.estado_disponibilidad in ['disponible', 'en_ruta']:
            return Response({'error': 'El conductor ya tiene un turno iniciado.'}, status=status.HTTP_400_BAD_REQUEST)

        RegistroTurno.objects.create(conductor=conductor, tipo='entrada', fecha_hora=timezone.now())
        conductor.estado_disponibilidad = 'disponible'
        conductor.save()
        serializer = self.get_serializer(conductor)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='finalizar-turno')
    def finalizar_turno(self, request, pk=None):
        conductor = self.get_object()

        # Si el conductor no está en un turno activo, no se puede finalizar.
        if conductor.estado_disponibilidad in ['dia_libre', 'no_disponible']:
            return Response({'error': 'El conductor no tiene un turno activo para finalizar.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if conductor.estado_disponibilidad == 'en_ruta':
            return Response({'error': 'No se puede finalizar el turno de un conductor que está en ruta.'}, status=status.HTTP_400_BAD_REQUEST)

        # Si el estado es 'disponible', se puede finalizar el turno.
        RegistroTurno.objects.create(conductor=conductor, tipo='salida', fecha_hora=timezone.now())
        conductor.estado_disponibilidad = 'dia_libre'
        conductor.save()
        serializer = self.get_serializer(conductor)
        return Response(serializer.data)


class RegistroTurnoViewSet(viewsets.ModelViewSet):
    """
    API endpoint para ver y editar registros de turno.
    """
    queryset = RegistroTurno.objects.all().order_by('-fecha_hora')
    serializer_class = RegistroTurnoSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'conductor': ['exact'],
        'fecha_hora': ['gte', 'lte', 'date'],
    }


class AsignacionViewSet(viewsets.ModelViewSet):
    queryset = Asignacion.objects.all().select_related('vehiculo', 'conductor').order_by('-fecha_hora_requerida_inicio')
    serializer_class = AsignacionSerializer
    permission_classes = [permissions.IsAuthenticated] # Cambiado para requerir autenticación para todas las acciones

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = {
        'estado': ['exact'],
        'vehiculo__patente': ['exact', 'icontains'], # Ajustado para buscar por patente
        'conductor__apellido': ['exact', 'icontains'],
        'fecha_hora_requerida_inicio': ['exact', 'gte', 'lte', 'date'],
        'solicitante_nombre': ['icontains'], # Para buscar por nombre del solicitante
        'solicitante_jerarquia': ['exact'], # Para filtrar por jerarquía
    }
    search_fields = ['destino_descripcion', 'vehiculo__patente', 'observaciones', 'solicitante_nombre']
    ordering_fields = ['fecha_hora_requerida_inicio', 'fecha_hora_fin_prevista', 'estado', 'solicitante_jerarquia'] # 'tipo_servicio' ELIMINADO

    @action(detail=False, methods=['post'], url_path='asignar-vehiculos-auto-lote', permission_classes=[AllowAny])
    def asignar_vehiculos_auto_lote(self, request):
        resultados = asignar_vehiculos_automatico_lote()
        return Response({'resultados': resultados})
    @action(detail=False, methods=['get'], url_path='estado-disponibilidad-conductores')
    def estado_disponibilidad_conductores(self, request):
        """
        Devuelve el estado de disponibilidad de todos los conductores.
        """
        conductores = Conductor.objects.all().order_by('apellido', 'nombre')
        serializer = ConductorSerializer(conductores, many=True)
        return Response(serializer.data)

    
    search_fields = ['destino_descripcion', 'vehiculo__patente', 'observaciones', 'solicitante_nombre']
    ordering_fields = ['fecha_hora_requerida_inicio', 'fecha_hora_fin_prevista', 'estado', 'solicitante_jerarquia'] # 'tipo_servicio' ELIMINADO

    @action(detail=False, methods=['post'], url_path='asignar-vehiculos-auto-lote', permission_classes=[AllowAny])
    def asignar_vehiculos_auto_lote(self, request):
        resultados = asignar_vehiculos_automatico_lote()
        return Response({'resultados': resultados})
    @action(detail=False, methods=['get'], url_path='estado-disponibilidad-conductores')
    def estado_disponibilidad_conductores(self, request):
        """
        Devuelve el estado de disponibilidad de todos los conductores.
        """
        conductores = Conductor.objects.all().order_by('apellido', 'nombre')
        serializer = ConductorSerializer(conductores, many=True)
        return Response(serializer.data)

class DashboardStatsView(APIView):
    """
    Vista API para proporcionar estadísticas del dashboard del sistema vehicular.
    Optimizada con agregaciones de Django ORM para máximo rendimiento.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Retorna estadísticas completas para el dashboard.
        
        Returns:
            JSON con las siguientes estadísticas:
            - resumen_general: Totales de vehículos, conductores, asignaciones
            - vehiculos_por_estado: Distribución de estados de vehículos
            - conductores_por_disponibilidad: Distribución de disponibilidad de conductores
            - asignaciones_por_estado: Distribución de estados de asignaciones
            - asignaciones_recientes: Asignaciones de los últimos 7 días
            - estadisticas_mensuales: Datos agregados del mes actual
            - proximos_vencimientos: Licencias próximas a vencer
            - performance_vehiculos: Estadísticas de uso de vehículos
        """
        try:
            # Fechas para filtros temporales
            hoy = timezone.now().date()
            hace_7_dias = hoy - timedelta(days=7)
            inicio_mes = hoy.replace(day=1)
            proximos_30_dias = hoy + timedelta(days=30)
            
            # ===============================
            # 1. RESUMEN GENERAL (Una sola consulta por modelo)
            # ===============================
            total_vehiculos = Vehiculo.objects.count()
            total_conductores = Conductor.objects.count()
            total_asignaciones = Asignacion.objects.count()
            
            # ===============================
            # 2. VEHÍCULOS POR ESTADO (Agregación optimizada)
            # ===============================
            vehiculos_por_estado = dict(
                Vehiculo.objects.values('estado')
                .annotate(cantidad=Count('id'))
                .values_list('estado', 'cantidad')
            )
            
            # ===============================
            # 3. CONDUCTORES POR DISPONIBILIDAD
            # ===============================
            conductores_por_disponibilidad = dict(
                Conductor.objects.values('estado_disponibilidad')
                .annotate(cantidad=Count('id'))
                .values_list('estado_disponibilidad', 'cantidad')
            )
            
            # ===============================
            # 4. ASIGNACIONES POR ESTADO
            # ===============================
            asignaciones_por_estado = dict(
                Asignacion.objects.values('estado')
                .annotate(cantidad=Count('id'))
                .values_list('estado', 'cantidad')
            )
            
            # ===============================
            # 5. ASIGNACIONES RECIENTES (últimos 7 días)
            # ===============================
            asignaciones_recientes = list(
                Asignacion.objects.filter(
                    fecha_hora_requerida_inicio__date__gte=hace_7_dias
                )
                .values('fecha_hora_requerida_inicio__date')
                .annotate(
                    fecha=TruncDate('fecha_hora_requerida_inicio'),
                    cantidad=Count('id')
                )
                .order_by('fecha')
                .values_list('fecha', 'cantidad')
            )
            
            # ===============================
            # 6. ESTADÍSTICAS DEL MES ACTUAL
            # ===============================
            asignaciones_mes = Asignacion.objects.filter(
                fecha_hora_requerida_inicio__date__gte=inicio_mes
            )
            
            estadisticas_mensuales = {
                'total_asignaciones': asignaciones_mes.count(),
                'completadas': asignaciones_mes.filter(estado='completada').count(),
                'activas': asignaciones_mes.filter(estado='activa').count(),
                'canceladas': asignaciones_mes.filter(estado='cancelada').count(),
                'distancia_total': asignaciones_mes.aggregate(
                    total=Sum('distancia_recorrida_km')
                )['total'] or 0,
                'promedio_pasajeros': asignaciones_mes.aggregate(
                    promedio=Avg('req_pasajeros')
                )['promedio'] or 0
            }
            
            # ===============================
            # 7. PRÓXIMOS VENCIMIENTOS DE LICENCIAS
            # ===============================
            conductores_vencimiento_proximo = list(
                Conductor.objects.filter(
                    fecha_vencimiento_licencia__lte=proximos_30_dias,
                    fecha_vencimiento_licencia__gte=hoy
                )
                .values('id', 'nombre', 'apellido', 'fecha_vencimiento_licencia', 'numero_licencia')
                .order_by('fecha_vencimiento_licencia')
            )
            
            # ===============================
            # 8. PERFORMANCE DE VEHÍCULOS (más utilizados)
            # ===============================
            vehiculos_performance = list(
                Vehiculo.objects.annotate(
                    total_asignaciones=Count('asignaciones_realizadas'),
                    asignaciones_completadas=Count(
                        'asignaciones_realizadas',
                        filter=Q(asignaciones_realizadas__estado='completada')
                    ),
                    distancia_total=Sum('asignaciones_realizadas__distancia_recorrida_km')
                )
                .filter(total_asignaciones__gt=0)
                .values(
                    'id', 'marca', 'modelo', 'patente', 'estado',
                    'total_asignaciones', 'asignaciones_completadas', 
                    'distancia_total', 'kilometraje'
                )
                .order_by('-total_asignaciones')[:10]
            )
            
            # ===============================
            # 9. DISTRIBUCIÓN POR TIPO DE VEHÍCULO
            # ===============================
            vehiculos_por_tipo = dict(
                Vehiculo.objects.values('tipo_vehiculo')
                .annotate(cantidad=Count('id'))
                .values_list('tipo_vehiculo', 'cantidad')
            )
            
            # ===============================
            # 10. ASIGNACIONES POR JERARQUÍA
            # ===============================
            asignaciones_por_jerarquia = dict(
                Asignacion.objects.values('solicitante_jerarquia')
                .annotate(cantidad=Count('id'))
                .values_list('solicitante_jerarquia', 'cantidad')
            )
            
            # ===============================
            # 11. ESTADÍSTICAS DE TURNOS (últimos 7 días)
            # ===============================
            registros_turno_recientes = RegistroTurno.objects.filter(
                fecha_hora__date__gte=hace_7_dias
            )
            
            turnos_estadisticas = {
                'total_registros': registros_turno_recientes.count(),
                'entradas': registros_turno_recientes.filter(tipo='entrada').count(),
                'salidas': registros_turno_recientes.filter(tipo='salida').count(),
            }
            
            # ===============================
            # RESPUESTA ESTRUCTURADA
            # ===============================
            dashboard_data = {
                'timestamp': timezone.now().isoformat(),
                'resumen_general': {
                    'total_vehiculos': total_vehiculos,
                    'total_conductores': total_conductores,
                    'total_asignaciones': total_asignaciones,
                    'vehiculos_disponibles': vehiculos_por_estado.get('disponible', 0),
                    'conductores_disponibles': conductores_por_disponibilidad.get('disponible', 0),
                    'asignaciones_activas': asignaciones_por_estado.get('activa', 0),
                },
                'vehiculos': {
                    'por_estado': vehiculos_por_estado,
                    'por_tipo': vehiculos_por_tipo,
                    'performance_top': vehiculos_performance,
                },
                'conductores': {
                    'por_disponibilidad': conductores_por_disponibilidad,
                    'vencimientos_proximos': conductores_vencimiento_proximo,
                    'total_con_licencia_vigente': Conductor.objects.filter(
                        fecha_vencimiento_licencia__gt=hoy
                    ).count(),
                },
                'asignaciones': {
                    'por_estado': asignaciones_por_estado,
                    'por_jerarquia': asignaciones_por_jerarquia,
                    'recientes_7_dias': dict(asignaciones_recientes),
                    'estadisticas_mensuales': estadisticas_mensuales,
                },
                'turnos': turnos_estadisticas,
                'alertas': {
                    'licencias_por_vencer': len(conductores_vencimiento_proximo),
                    'vehiculos_en_mantenimiento': vehiculos_por_estado.get('mantenimiento', 0),
                    'asignaciones_fallidas': asignaciones_por_estado.get('fallo_auto', 0),
                }
            }
            
            return Response(dashboard_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            # Log del error para debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error en DashboardStatsView: {str(e)}", exc_info=True)
            
            return Response(
                {
                    'error': 'Error interno del servidor al generar estadísticas',
                    'message': 'Por favor contacte al administrador del sistema'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



