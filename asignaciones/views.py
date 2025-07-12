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
from django.db.models import Count, Q, Avg, Sum, Max, Min
from django.db.models.functions import TruncDate, TruncMonth, TruncYear
from datetime import datetime, timedelta
import json

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
    permission_classes = [permissions.AllowAny]
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
    permission_classes = [permissions.AllowAny]

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
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'conductor': ['exact'],
        'fecha_hora': ['gte', 'lte', 'date'],
    }


class AsignacionViewSet(viewsets.ModelViewSet):
    queryset = Asignacion.objects.all().select_related('vehiculo', 'conductor').order_by('-fecha_hora_requerida_inicio')
    serializer_class = AsignacionSerializer
    permission_classes = [permissions.AllowAny] # Cambiado para permitir acceso sin autenticación

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
    API endpoint para obtener estadísticas del dashboard de mantenimiento
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        # Obtener parámetros de filtro temporal
        fecha_inicio = request.GET.get('fecha_inicio')
        fecha_fin = request.GET.get('fecha_fin')
        tipo_periodo = request.GET.get('tipo_periodo', 'diario')  # diario, mensual, anual
        
        # Configurar filtros de fecha
        filtros = {}
        if fecha_inicio:
            try:
                filtros['fecha_hora_requerida_inicio__gte'] = datetime.fromisoformat(fecha_inicio.replace('Z', '+00:00'))
            except:
                pass
        if fecha_fin:
            try:
                filtros['fecha_hora_requerida_inicio__lte'] = datetime.fromisoformat(fecha_fin.replace('Z', '+00:00'))
            except:
                pass
                
        # Si no hay fechas específicas, usar últimos 30 días
        if not fecha_inicio and not fecha_fin:
            fecha_fin_default = timezone.now()
            fecha_inicio_default = fecha_fin_default - timedelta(days=30)
            filtros['fecha_hora_requerida_inicio__gte'] = fecha_inicio_default
            filtros['fecha_hora_requerida_inicio__lte'] = fecha_fin_default
        
        # Obtener estadísticas generales
        stats_generales = self.get_stats_generales(filtros)
        
        # Obtener estadísticas de vehículos
        stats_vehiculos = self.get_stats_vehiculos(filtros)
        
        # Obtener estadísticas de conductores
        stats_conductores = self.get_stats_conductores(filtros)
        
        # Obtener datos para mapa de asignaciones
        stats_mapa = self.get_stats_mapa(filtros)
        
        # Obtener tendencias temporales
        tendencias = self.get_tendencias_temporales(filtros, tipo_periodo)
        
        return Response({
            'general': stats_generales,
            'vehiculos': stats_vehiculos,
            'conductores': stats_conductores,
            'mapa': stats_mapa,
            'tendencias': tendencias,
            'metadatos': {
                'fecha_generacion': timezone.now(),
                'filtros_aplicados': filtros,
                'tipo_periodo': tipo_periodo
            }
        })
    
    def get_stats_generales(self, filtros):
        asignaciones = Asignacion.objects.filter(**filtros)
        
        total_asignaciones = asignaciones.count()
        asignaciones_completadas = asignaciones.filter(estado='completada').count()
        asignaciones_activas = asignaciones.filter(estado='activa').count()
        asignaciones_canceladas = asignaciones.filter(estado='cancelada').count()
        
        # Calcular distancia total recorrida
        distancia_total = asignaciones.filter(
            distancia_recorrida_km__isnull=False
        ).aggregate(
            total=Sum('distancia_recorrida_km')
        )['total'] or 0
        
        # Calcular tiempo promedio de viaje (estimado)
        tiempo_promedio = asignaciones.filter(
            fecha_hora_fin_prevista__isnull=False
        ).count()
        
        # Vehículos y conductores únicos utilizados
        vehiculos_utilizados = asignaciones.values('vehiculo').distinct().count()
        conductores_utilizados = asignaciones.values('conductor').distinct().count()
        
        return {
            'total_asignaciones': total_asignaciones,
            'asignaciones_completadas': asignaciones_completadas,
            'asignaciones_activas': asignaciones_activas,
            'asignaciones_canceladas': asignaciones_canceladas,
            'tasa_completitud': round((asignaciones_completadas / total_asignaciones * 100) if total_asignaciones > 0 else 0, 2),
            'distancia_total_km': round(distancia_total, 2),
            'vehiculos_utilizados': vehiculos_utilizados,
            'conductores_utilizados': conductores_utilizados,
            'vehiculos_disponibles': Vehiculo.objects.filter(estado='disponible').count(),
            'vehiculos_en_mantenimiento': Vehiculo.objects.filter(estado='mantenimiento').count(),
            'conductores_disponibles': Conductor.objects.filter(estado_disponibilidad='disponible').count(),
            'conductores_en_ruta': Conductor.objects.filter(estado_disponibilidad='en_ruta').count()
        }
    
    def get_stats_vehiculos(self, filtros):
        asignaciones = Asignacion.objects.filter(**filtros)
        
        # Uso por vehículo
        uso_por_vehiculo = asignaciones.values(
            'vehiculo__id', 'vehiculo__patente', 'vehiculo__marca', 'vehiculo__modelo', 'vehiculo__tipo_vehiculo'
        ).annotate(
            total_viajes=Count('id'),
            distancia_total=Sum('distancia_recorrida_km'),
            kilometraje_actual=Max('vehiculo__kilometraje')
        ).order_by('-total_viajes')[:10]
        
        # Distribución por tipo de vehículo
        distribucion_tipo = asignaciones.values('vehiculo__tipo_vehiculo').annotate(
            count=Count('id')
        ).order_by('vehiculo__tipo_vehiculo')
        
        # Estado de la flota
        estado_flota = Vehiculo.objects.values('estado').annotate(
            count=Count('id')
        ).order_by('estado')
        
        # Análisis detallado de mantenimiento con barras de progreso
        vehiculos_mantenimiento = []
        for vehiculo in Vehiculo.objects.all():
            # Definir intervalos de mantenimiento según tipo de vehículo
            intervalos_mantenimiento = {
                'automovil': {'menor': 10000, 'mayor': 50000, 'critico': 100000},
                'camioneta': {'menor': 12000, 'mayor': 60000, 'critico': 120000},
                'minibus': {'menor': 8000, 'mayor': 40000, 'critico': 80000},
                'default': {'menor': 10000, 'mayor': 50000, 'critico': 100000}
            }
            
            intervalo = intervalos_mantenimiento.get(vehiculo.tipo_vehiculo, intervalos_mantenimiento['default'])
            km_actual = vehiculo.kilometraje or 0
            
            # Calcular próximo mantenimiento menor
            km_desde_ultimo_menor = km_actual % intervalo['menor']
            km_hasta_proximo_menor = intervalo['menor'] - km_desde_ultimo_menor
            progreso_menor = round((km_desde_ultimo_menor / intervalo['menor']) * 100, 1)
            
            # Calcular próximo mantenimiento mayor
            km_desde_ultimo_mayor = km_actual % intervalo['mayor']
            km_hasta_proximo_mayor = intervalo['mayor'] - km_desde_ultimo_mayor
            progreso_mayor = round((km_desde_ultimo_mayor / intervalo['mayor']) * 100, 1)
            
            # Determinar estado de mantenimiento
            if km_actual >= intervalo['critico']:
                estado_mant = 'critico'
                prioridad = 1
            elif progreso_mayor >= 90:
                estado_mant = 'urgente'
                prioridad = 2
            elif progreso_mayor >= 75:
                estado_mant = 'proximo'
                prioridad = 3
            elif progreso_menor >= 90:
                estado_mant = 'menor_urgente'
                prioridad = 4
            else:
                estado_mant = 'ok'
                prioridad = 5
            
            vehiculos_mantenimiento.append({
                'id': vehiculo.id,
                'patente': vehiculo.patente,
                'marca': vehiculo.marca,
                'modelo': vehiculo.modelo,
                'tipo_vehiculo': vehiculo.tipo_vehiculo,
                'kilometraje_actual': km_actual,
                'estado_vehiculo': vehiculo.estado,
                'mantenimiento': {
                    'estado': estado_mant,
                    'prioridad': prioridad,
                    'menor': {
                        'progreso': progreso_menor,
                        'km_hasta_proximo': km_hasta_proximo_menor,
                        'intervalo': intervalo['menor']
                    },
                    'mayor': {
                        'progreso': progreso_mayor,
                        'km_hasta_proximo': km_hasta_proximo_mayor,
                        'intervalo': intervalo['mayor']
                    },
                    'critico': {
                        'limite': intervalo['critico'],
                        'superado': km_actual >= intervalo['critico']
                    }
                }
            })
        
        # Ordenar por prioridad de mantenimiento
        vehiculos_mantenimiento.sort(key=lambda x: x['mantenimiento']['prioridad'])
        
        # Estadísticas de mantenimiento
        stats_mantenimiento = {
            'total_vehiculos': len(vehiculos_mantenimiento),
            'criticos': len([v for v in vehiculos_mantenimiento if v['mantenimiento']['estado'] == 'critico']),
            'urgentes': len([v for v in vehiculos_mantenimiento if v['mantenimiento']['estado'] == 'urgente']),
            'proximos': len([v for v in vehiculos_mantenimiento if v['mantenimiento']['estado'] == 'proximo']),
            'menor_urgente': len([v for v in vehiculos_mantenimiento if v['mantenimiento']['estado'] == 'menor_urgente']),
            'ok': len([v for v in vehiculos_mantenimiento if v['mantenimiento']['estado'] == 'ok'])
        }
        
        return {
            'uso_por_vehiculo': list(uso_por_vehiculo),
            'distribucion_tipo': list(distribucion_tipo),
            'estado_flota': list(estado_flota),
            'vehiculos_necesitan_mantenimiento': vehiculos_mantenimiento[:20],  # Top 20 prioritarios
            'analisis_mantenimiento': vehiculos_mantenimiento,
            'estadisticas_mantenimiento': stats_mantenimiento
        }
    
    def get_stats_conductores(self, filtros):
        from datetime import timedelta
        from django.db.models import Avg, Sum
        
        asignaciones = Asignacion.objects.filter(**filtros)
        
        # Desempeño por conductor
        desempeño_conductores = asignaciones.values(
            'conductor__id', 'conductor__nombre', 'conductor__apellido', 'conductor__numero_licencia'
        ).annotate(
            total_viajes=Count('id'),
            viajes_completados=Count('id', filter=Q(estado='completada')),
            distancia_total=Sum('distancia_recorrida_km'),
            tasa_completitud=Count('id', filter=Q(estado='completada')) * 100.0 / Count('id')
        ).order_by('-total_viajes')[:10]
        
        # Estado actual de conductores
        estado_conductores = Conductor.objects.values('estado_disponibilidad').annotate(
            count=Count('id')
        ).order_by('estado_disponibilidad')
        
        # Análisis profundo de horarios de trabajo
        analisis_horarios = []
        fecha_inicio_analisis = timezone.now() - timedelta(days=30)  # Últimos 30 días
        
        for conductor in Conductor.objects.all():
            # Obtener todos los registros de turno del conductor en el período
            registros_turno = RegistroTurno.objects.filter(
                conductor=conductor,
                fecha_hora__gte=fecha_inicio_analisis
            ).order_by('fecha_hora')
            
            # Calcular estadísticas de trabajo
            total_horas_trabajadas = 0
            dias_trabajados = set()
            turnos_completos = 0
            horarios_entrada = []
            horarios_salida = []
            
            # Agrupar registros por día para calcular turnos completos
            registros_por_dia = {}
            for registro in registros_turno:
                fecha = registro.fecha_hora.date()
                if fecha not in registros_por_dia:
                    registros_por_dia[fecha] = {'entrada': None, 'salida': None}
                
                if registro.tipo == 'entrada':
                    registros_por_dia[fecha]['entrada'] = registro.fecha_hora
                    horarios_entrada.append(registro.fecha_hora.hour + registro.fecha_hora.minute / 60.0)
                elif registro.tipo == 'salida':
                    registros_por_dia[fecha]['salida'] = registro.fecha_hora
                    horarios_salida.append(registro.fecha_hora.hour + registro.fecha_hora.minute / 60.0)
            
            # Calcular horas trabajadas y días efectivos
            for fecha, registros in registros_por_dia.items():
                if registros['entrada'] and registros['salida']:
                    # Turno completo
                    duracion = registros['salida'] - registros['entrada']
                    horas = duracion.total_seconds() / 3600
                    total_horas_trabajadas += horas
                    turnos_completos += 1
                    dias_trabajados.add(fecha)
                elif registros['entrada'] or registros['salida']:
                    # Turno incompleto - estimar 8 horas si solo hay entrada o salida
                    if registros['entrada']:
                        dias_trabajados.add(fecha)
                        total_horas_trabajadas += 8  # Estimación
            
            # Calcular promedios y estadísticas
            dias_trabajados_count = len(dias_trabajados)
            horas_promedio_dia = total_horas_trabajadas / dias_trabajados_count if dias_trabajados_count > 0 else 0
            hora_entrada_promedio = sum(horarios_entrada) / len(horarios_entrada) if horarios_entrada else 8.0
            hora_salida_promedio = sum(horarios_salida) / len(horarios_salida) if horarios_salida else 17.0
            
            # Calcular proyección mensual
            dias_restantes_mes = 30 - dias_trabajados_count
            horas_proyectadas_mes = total_horas_trabajadas + (dias_restantes_mes * horas_promedio_dia * 0.8)  # Factor de ajuste
            
            # Determinar estado del conductor
            if dias_trabajados_count == 0:
                estado_trabajo = 'inactivo'
                eficiencia = 0
            elif horas_promedio_dia >= 8:
                estado_trabajo = 'completo'
                eficiencia = min(100, (horas_promedio_dia / 8) * 100)
            elif horas_promedio_dia >= 6:
                estado_trabajo = 'regular'
                eficiencia = (horas_promedio_dia / 8) * 100
            else:
                estado_trabajo = 'bajo'
                eficiencia = (horas_promedio_dia / 8) * 100
            
            # Obtener asignaciones del conductor para calcular eficiencia en viajes
            asignaciones_conductor = asignaciones.filter(conductor=conductor)
            viajes_totales = asignaciones_conductor.count()
            viajes_completados = asignaciones_conductor.filter(estado='completada').count()
            eficiencia_viajes = (viajes_completados / viajes_totales * 100) if viajes_totales > 0 else 0
            
            analisis_horarios.append({
                'id': conductor.id,
                'nombre': conductor.nombre,
                'apellido': conductor.apellido,
                'numero_licencia': conductor.numero_licencia,
                'estado_disponibilidad': conductor.estado_disponibilidad,
                'horarios': {
                    'total_horas_trabajadas': round(total_horas_trabajadas, 2),
                    'dias_trabajados': dias_trabajados_count,
                    'turnos_completos': turnos_completos,
                    'horas_promedio_dia': round(horas_promedio_dia, 2),
                    'hora_entrada_promedio': round(hora_entrada_promedio, 2),
                    'hora_salida_promedio': round(hora_salida_promedio, 2),
                    'estado_trabajo': estado_trabajo,
                    'eficiencia_horario': round(eficiencia, 1),
                    'proyeccion_mensual': {
                        'horas_proyectadas': round(horas_proyectadas_mes, 2),
                        'dias_restantes': dias_restantes_mes,
                        'meta_horas_mes': 160  # 20 días * 8 horas
                    }
                },
                'rendimiento': {
                    'total_viajes': viajes_totales,
                    'viajes_completados': viajes_completados,
                    'eficiencia_viajes': round(eficiencia_viajes, 1),
                    'viajes_por_dia': round(viajes_totales / dias_trabajados_count, 2) if dias_trabajados_count > 0 else 0
                }
            })
        
        # Ordenar por eficiencia general (combinando horarios y viajes)
        for conductor in analisis_horarios:
            conductor['eficiencia_general'] = (
                conductor['horarios']['eficiencia_horario'] * 0.6 + 
                conductor['rendimiento']['eficiencia_viajes'] * 0.4
            )
        
        analisis_horarios.sort(key=lambda x: x['eficiencia_general'], reverse=True)
        
        # Estadísticas generales de conductores
        stats_horarios = {
            'total_conductores': len(analisis_horarios),
            'activos': len([c for c in analisis_horarios if c['horarios']['estado_trabajo'] != 'inactivo']),
            'completos': len([c for c in analisis_horarios if c['horarios']['estado_trabajo'] == 'completo']),
            'regulares': len([c for c in analisis_horarios if c['horarios']['estado_trabajo'] == 'regular']),
            'bajos': len([c for c in analisis_horarios if c['horarios']['estado_trabajo'] == 'bajo']),
            'inactivos': len([c for c in analisis_horarios if c['horarios']['estado_trabajo'] == 'inactivo']),
            'horas_promedio_flota': round(sum([c['horarios']['horas_promedio_dia'] for c in analisis_horarios]) / len(analisis_horarios), 2) if analisis_horarios else 0,
            'eficiencia_promedio': round(sum([c['eficiencia_general'] for c in analisis_horarios]) / len(analisis_horarios), 1) if analisis_horarios else 0
        }
        
        return {
            'desempeño_conductores': list(desempeño_conductores),
            'estado_conductores': list(estado_conductores),
            'analisis_horarios': analisis_horarios,
            'estadisticas_horarios': stats_horarios
        }
    
    def get_stats_mapa(self, filtros):
        asignaciones = Asignacion.objects.filter(
            **filtros,
            origen_lat__isnull=False,
            origen_lon__isnull=False,
            destino_lat__isnull=False,
            destino_lon__isnull=False
        ).values(
            'origen_lat', 'origen_lon', 'destino_lat', 'destino_lon',
            'origen_descripcion', 'destino_descripcion', 'estado',
            'vehiculo__patente', 'conductor__nombre', 'conductor__apellido',
            'fecha_hora_requerida_inicio'
        )[:100]  # Limitar para rendimiento
        
        return {
            'asignaciones_con_coordenadas': list(asignaciones)
        }
    
    def get_tendencias_temporales(self, filtros, tipo_periodo):
        asignaciones = Asignacion.objects.filter(**filtros)
        
        if tipo_periodo == 'diario':
            tendencias = asignaciones.annotate(
                periodo=TruncDate('fecha_hora_requerida_inicio')
            ).values('periodo').annotate(
                total_asignaciones=Count('id'),
                completadas=Count('id', filter=Q(estado='completada')),
                canceladas=Count('id', filter=Q(estado='cancelada'))
            ).order_by('periodo')
            
        elif tipo_periodo == 'mensual':
            tendencias = asignaciones.annotate(
                periodo=TruncMonth('fecha_hora_requerida_inicio')
            ).values('periodo').annotate(
                total_asignaciones=Count('id'),
                completadas=Count('id', filter=Q(estado='completada')),
                canceladas=Count('id', filter=Q(estado='cancelada'))
            ).order_by('periodo')
            
        elif tipo_periodo == 'anual':
            tendencias = asignaciones.annotate(
                periodo=TruncYear('fecha_hora_requerida_inicio')
            ).values('periodo').annotate(
                total_asignaciones=Count('id'),
                completadas=Count('id', filter=Q(estado='completada')),
                canceladas=Count('id', filter=Q(estado='cancelada'))
            ).order_by('periodo')
        
        return list(tendencias)



