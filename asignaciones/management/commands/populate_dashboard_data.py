# management/commands/populate_dashboard_data.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random
from asignaciones.models import Vehiculo, Conductor, Asignacion, RegistroTurno


class Command(BaseCommand):
    help = 'Popula la base de datos con datos de prueba para el dashboard'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clean',
            action='store_true',
            help='Limpia todos los datos antes de poblar',
        )

    def handle(self, *args, **options):
        if options['clean']:
            self.stdout.write('Limpiando datos existentes...')
            Asignacion.objects.all().delete()
            RegistroTurno.objects.all().delete()
            Vehiculo.objects.all().delete()
            Conductor.objects.all().delete()

        self.stdout.write('Creando vehículos...')
        self.create_vehiculos()
        
        self.stdout.write('Creando conductores...')
        self.create_conductores()
        
        self.stdout.write('Creando asignaciones...')
        self.create_asignaciones()
        
        self.stdout.write('Creando registros de turno...')
        self.create_registros_turno()
        
        self.stdout.write(
            self.style.SUCCESS('¡Datos de prueba creados exitosamente!')
        )

    def create_vehiculos(self):
        """Crear vehículos de prueba."""
        vehiculos_data = [
            ('Toyota', 'Corolla', 'ABC001', 'disponible', 'automovil', 2020, 4),
            ('Ford', 'Transit', 'ABC002', 'en_uso', 'minibus', 2019, 15),
            ('Chevrolet', 'Spark', 'ABC003', 'mantenimiento', 'automovil', 2021, 4),
            ('Nissan', 'NV200', 'ABC004', 'disponible', 'camioneta', 2018, 7),
            ('Hyundai', 'H1', 'ABC005', 'reservado', 'minibus', 2017, 12),
            ('Toyota', 'Hilux', 'ABC006', 'disponible', 'camioneta', 2022, 5),
            ('Ford', 'Fiesta', 'ABC007', 'en_uso', 'automovil', 2020, 4),
            ('Chevrolet', 'Aveo', 'ABC008', 'disponible', 'automovil', 2019, 4),
            ('Nissan', 'Sentra', 'ABC009', 'mantenimiento', 'automovil', 2021, 4),
            ('Hyundai', 'Accent', 'ABC010', 'disponible', 'automovil', 2018, 4),
            ('Toyota', 'Hiace', 'ABC011', 'en_uso', 'minibus', 2020, 14),
            ('Ford', 'Ranger', 'ABC012', 'disponible', 'camioneta', 2021, 5),
            ('Chevrolet', 'S10', 'ABC013', 'reservado', 'camioneta', 2019, 5),
            ('Nissan', 'Frontier', 'ABC014', 'disponible', 'camioneta', 2020, 5),
            ('Hyundai', 'Porter', 'ABC015', 'mantenimiento', 'camioneta', 2018, 3),
        ]

        for marca, modelo, patente, estado, tipo, anio, capacidad in vehiculos_data:
            Vehiculo.objects.create(
                marca=marca,
                modelo=modelo,
                patente=patente,
                estado=estado,
                tipo_vehiculo=tipo,
                anio=anio,
                capacidad_pasajeros=capacidad,
                kilometraje=random.randint(10000, 150000),
                numero_chasis=f'VIN{patente}',
                numero_motor=f'MOT{patente}'
            )

    def create_conductores(self):
        """Crear conductores de prueba."""
        conductores_data = [
            ('Juan', 'Pérez', '12.345.678-9', '12345678', 'disponible', 15),
            ('María', 'González', '98.765.432-1', '87654321', 'en_ruta', 45),
            ('Carlos', 'Rodríguez', '11.222.333-4', '11223344', 'disponible', 60),
            ('Ana', 'Martínez', '55.666.777-8', '55667788', 'dia_libre', 90),
            ('Luis', 'López', '99.888.777-6', '99887776', 'disponible', 120),
            ('Patricia', 'Silva', '44.333.222-1', '44332211', 'en_ruta', 30),
            ('Roberto', 'Torres', '77.888.999-0', '77889900', 'no_disponible', 180),
            ('Carmen', 'Ruiz', '66.555.444-3', '66554443', 'disponible', 75),
            ('Fernando', 'Morales', '33.444.555-6', '33445556', 'dia_libre', 40),
            ('Lucia', 'Herrera', '22.111.000-9', '22110009', 'disponible', 25),
            ('Diego', 'Castillo', '88.999.000-1', '88990001', 'en_ruta', 65),
            ('Valeria', 'Mendoza', '11.000.999-8', '11000998', 'disponible', 35),
        ]

        for nombre, apellido, run, licencia, estado, dias_vence in conductores_data:
            fecha_vencimiento = timezone.now().date() + timedelta(days=dias_vence)
            
            Conductor.objects.create(
                nombre=nombre,
                apellido=apellido,
                run=run,
                numero_licencia=licencia,
                fecha_vencimiento_licencia=fecha_vencimiento,
                estado_disponibilidad=estado,
                telefono=f'+569{random.randint(10000000, 99999999)}',
                email=f'{nombre.lower()}.{apellido.lower()}@ssvq.cl',
                tipos_vehiculo_habilitados='automovil,camioneta,minibus'
            )

    def create_asignaciones(self):
        """Crear asignaciones de prueba."""
        vehiculos = list(Vehiculo.objects.all())
        conductores = list(Conductor.objects.all())
        
        destinos = [
            'Hospital Regional', 'Municipalidad', 'Aeropuerto', 
            'Universidad', 'Tribunal', 'Ministerio',
            'Centro Médico', 'Estadio Municipal', 'Puerto',
            'Biblioteca Central', 'Comisaría', 'Bomberos'
        ]
        
        estados = ['completada', 'activa', 'programada', 'cancelada', 'pendiente_auto']
        jerarquias = [3, 2, 1, 0]
        
        # Crear asignaciones de los últimos 30 días
        for i in range(80):
            dias_atras = random.randint(0, 30)
            fecha_asignacion = timezone.now() - timedelta(days=dias_atras)
            
            vehiculo = random.choice(vehiculos) if random.random() > 0.1 else None
            conductor = random.choice(conductores) if vehiculo else None
            
            estado = random.choice(estados)
            if dias_atras > 7:  # Asignaciones más antiguas tienden a estar completadas
                estado = random.choice(['completada', 'cancelada'])
            
            Asignacion.objects.create(
                vehiculo=vehiculo,
                conductor=conductor,
                destino_descripcion=random.choice(destinos),
                origen_descripcion='Oficina Central',
                fecha_hora_requerida_inicio=fecha_asignacion,
                req_pasajeros=random.randint(1, 8),
                req_tipo_vehiculo_preferente=random.choice(['automovil', 'camioneta', 'minibus']),
                estado=estado,
                solicitante_jerarquia=random.choice(jerarquias),
                solicitante_nombre=f'Funcionario {i+1}',
                solicitante_telefono=f'+569{random.randint(10000000, 99999999)}',
                responsable_nombre=f'Responsable {i+1}',
                fecha_asignacion_funcionario=fecha_asignacion,
                distancia_recorrida_km=random.uniform(5.0, 150.0) if estado == 'completada' else None,
                observaciones=f'Observación para asignación {i+1}' if random.random() > 0.7 else None
            )

    def create_registros_turno(self):
        """Crear registros de turno de prueba."""
        conductores = list(Conductor.objects.all())
        
        # Crear registros de los últimos 14 días
        for i in range(100):
            dias_atras = random.randint(0, 14)
            fecha_registro = timezone.now() - timedelta(
                days=dias_atras,
                hours=random.randint(6, 18),
                minutes=random.randint(0, 59)
            )
            
            conductor = random.choice(conductores)
            tipo = random.choice(['entrada', 'salida'])
            
            RegistroTurno.objects.create(
                conductor=conductor,
                fecha_hora=fecha_registro,
                tipo=tipo,
                notas=f'Registro {tipo} - {conductor.nombre}' if random.random() > 0.8 else None
            )
