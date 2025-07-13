# Dashboard API Documentation

## Endpoint: Dashboard Stats

### URL
```
GET /api/dashboard/stats/
```

### Autenticación
Requiere autenticación con token válido en el header:
```
Authorization: Token your_token_here
```

### Respuesta

El endpoint retorna un objeto JSON con las siguientes secciones:

#### 1. Resumen General
```json
{
  "resumen_general": {
    "total_vehiculos": 25,
    "total_conductores": 18,
    "total_asignaciones": 156,
    "vehiculos_disponibles": 12,
    "conductores_disponibles": 8,
    "asignaciones_activas": 5
  }
}
```

#### 2. Estadísticas de Vehículos
```json
{
  "vehiculos": {
    "por_estado": {
      "disponible": 12,
      "en_uso": 5,
      "mantenimiento": 3,
      "reservado": 5
    },
    "por_tipo": {
      "automovil": 10,
      "camioneta": 8,
      "minibus": 4,
      "station_wagon": 3
    },
    "performance_top": [
      {
        "id": 1,
        "marca": "Toyota",
        "modelo": "Corolla",
        "patente": "ABC123",
        "estado": "disponible",
        "total_asignaciones": 25,
        "asignaciones_completadas": 23,
        "distancia_total": 1250.5,
        "kilometraje": 45000.0
      }
    ]
  }
}
```

#### 3. Estadísticas de Conductores
```json
{
  "conductores": {
    "por_disponibilidad": {
      "disponible": 8,
      "en_ruta": 5,
      "dia_libre": 3,
      "no_disponible": 2
    },
    "vencimientos_proximos": [
      {
        "id": 5,
        "nombre": "Juan",
        "apellido": "Pérez",
        "fecha_vencimiento_licencia": "2025-08-15",
        "numero_licencia": "12345678"
      }
    ],
    "total_con_licencia_vigente": 16
  }
}
```

#### 4. Estadísticas de Asignaciones
```json
{
  "asignaciones": {
    "por_estado": {
      "completada": 120,
      "activa": 5,
      "programada": 15,
      "cancelada": 8,
      "pendiente_auto": 5,
      "fallo_auto": 3
    },
    "por_jerarquia": {
      "3": 45,
      "2": 65,
      "1": 35,
      "0": 11
    },
    "recientes_7_dias": {
      "2025-07-06": 8,
      "2025-07-07": 12,
      "2025-07-08": 6,
      "2025-07-09": 15,
      "2025-07-10": 9,
      "2025-07-11": 11,
      "2025-07-12": 7
    },
    "estadisticas_mensuales": {
      "total_asignaciones": 68,
      "completadas": 45,
      "activas": 5,
      "canceladas": 3,
      "distancia_total": 2875.5,
      "promedio_pasajeros": 2.8
    }
  }
}
```

#### 5. Estadísticas de Turnos
```json
{
  "turnos": {
    "total_registros": 56,
    "entradas": 28,
    "salidas": 28
  }
}
```

#### 6. Alertas del Sistema
```json
{
  "alertas": {
    "licencias_por_vencer": 3,
    "vehiculos_en_mantenimiento": 3,
    "asignaciones_fallidas": 3
  }
}
```

### Características de Optimización

1. **Consultas Agregadas**: Utiliza `Count()`, `Sum()`, `Avg()` de Django ORM
2. **Consultas Mínimas**: Optimizado para reducir el número de queries a la base de datos
3. **Filtros Temporales**: Datos de últimos 7 días y mes actual
4. **Manejo de Errores**: Respuestas estructuradas para errores
5. **Logging**: Registro de errores para debugging

### Códigos de Respuesta

- `200 OK`: Estadísticas generadas exitosamente
- `401 Unauthorized`: Token de autenticación inválido o faltante
- `500 Internal Server Error`: Error interno del servidor

### Uso en Frontend

```javascript
// Ejemplo de uso en el frontend
const fetchDashboardStats = async () => {
  try {
    const response = await fetch('/api/dashboard/stats/', {
      headers: {
        'Authorization': `Token ${localStorage.getItem('token')}`,
        'Content-Type': 'application/json'
      }
    });
    
    if (response.ok) {
      const data = await response.json();
      // Usar los datos para poblar gráficos y widgets
      updateDashboardCharts(data);
    }
  } catch (error) {
    console.error('Error fetching dashboard stats:', error);
  }
};
```

### Consideraciones de Performance

- Las consultas están optimizadas con agregaciones en base de datos
- Se evitan consultas N+1 mediante el uso de `annotate()` y `values()`
- Los resultados pueden ser cacheados en Redis para mayor performance
- Recomendado hacer polling cada 30-60 segundos en el frontend

### Futuras Mejoras

1. **Cache**: Implementar cache de Redis para consultas frecuentes
2. **Filtros Temporales**: Agregar parámetros para rangos de fechas personalizados
3. **Paginación**: Para listas de performance de vehículos
4. **WebSockets**: Para actualizaciones en tiempo real
