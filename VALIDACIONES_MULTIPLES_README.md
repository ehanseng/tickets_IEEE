# Sistema de Validaciones Múltiples

## Resumen de Cambios

Se ha implementado un sistema completo de validaciones múltiples que permite:

1. **Validaciones únicas (modo 'once')**: El ticket se puede validar una sola vez durante el evento
2. **Validaciones diarias (modo 'daily')**: El ticket se puede validar una vez por día durante la duración del evento

## Características Implementadas

### 1. Zona Horaria de Bogotá (UTC-5)

Todas las fechas y horas en el sistema ahora usan la zona horaria de Bogotá, Colombia:
- Las validaciones se registran con la hora local de Bogotá
- Las fechas existentes fueron ajustadas a UTC-5
- Nueva utilidad `timezone_utils.py` para manejo consistente de zonas horarias

### 2. Modos de Validación

#### Modo "once" (Una validación)
- El ticket se puede validar **una sola vez** durante todo el evento
- Después de la primera validación, el ticket queda marcado como usado
- Ideal para eventos de un solo día o acceso único

#### Modo "daily" (Una validación por día)
- El ticket se puede validar **una vez por día**
- Permite múltiples validaciones en días diferentes
- El sistema valida que no haya más de una validación por día
- Ideal para eventos de varios días (conferencias, talleres multi-día)

### 3. Registro Completo de Validaciones

- Todas las validaciones se registran en `validation_logs`
- Se guarda: fecha/hora, validador, éxito/fallo, notas
- Historial completo por ticket
- Estadísticas de validaciones por evento

## Cambios en la Base de Datos

### Tabla `tickets`
- **Nuevo campo**: `validation_mode` (TEXT, default='once')
  - Valores: 'once' o 'daily'

### Tabla `events`
- **Nuevo campo**: `event_duration_days` (INTEGER, default=1)
  - Duración del evento en días
- **Nuevo campo**: `event_end_date` (DATETIME, nullable)
  - Fecha de finalización del evento

### Tabla `validation_logs`
- Ya existía pero ahora se usa activamente
- Registra todas las validaciones (exitosas y fallidas)
- Columnas: ticket_id, validator_id, validated_at, success, notes

## Archivos Creados/Modificados

### Archivos Nuevos
1. `timezone_utils.py` - Utilidades para manejo de zona horaria de Bogotá
2. `migrate_multiple_validations.py` - Script de migración
3. `test_validation_system.py` - Script de pruebas
4. `VALIDACIONES_MULTIPLES_README.md` - Esta documentación

### Archivos Modificados
1. `models.py` - Agregados campos a Ticket y Event
2. `schemas.py` - Actualizados schemas para soportar nuevos campos
3. `main.py` - Nueva lógica de validación en endpoint `/validate/`
4. `ticket_service.py` - Uso de zona horaria de Bogotá

## Uso del Sistema

### Crear Ticket con Validación Única
```python
ticket = {
    "user_id": 1,
    "event_id": 1,
    "companions": 0,
    "validation_mode": "once"  # Por defecto
}
```

### Crear Ticket con Validación Diaria
```python
ticket = {
    "user_id": 1,
    "event_id": 1,
    "companions": 0,
    "validation_mode": "daily"
}
```

### Validar un Ticket

El endpoint `/validate/` ahora:

1. **Verifica el modo de validación** del ticket
2. **Consulta validaciones previas** en `validation_logs`
3. **Aplica la lógica según el modo**:
   - `once`: Rechaza si ya hay una validación
   - `daily`: Rechaza solo si ya hay una validación HOY
4. **Registra la validación** en `validation_logs`
5. **Retorna información adicional**:
   - `validation_count`: Número total de validaciones
   - `is_second_validation`: Si es una validación adicional
   - Mensaje apropiado según el contexto

### Respuestas de Validación

#### Ticket Válido (Primera vez)
```json
{
  "valid": true,
  "message": "Ticket válido - Acceso permitido. Primera validación",
  "validation_count": 1,
  "is_second_validation": false,
  "ticket": {...},
  "user": {...},
  "event": {...}
}
```

#### Ticket Válido (Modo Daily, Segunda validación)
```json
{
  "valid": true,
  "message": "Ticket válido - Acceso permitido. Validación #2. Última validación: 20/01/2025",
  "validation_count": 2,
  "is_second_validation": true,
  "ticket": {...},
  "user": {...},
  "event": {...}
}
```

#### Ticket Inválido (Ya usado hoy)
```json
{
  "valid": false,
  "message": "Ticket ya fue validado hoy a las 20/01/2025 14:30. En modo diario solo se permite 1 validación por día.",
  "validation_count": 1
}
```

## Migración de Datos Existentes

El script `migrate_multiple_validations.py` realizó:

1. ✅ Agregó campo `validation_mode` a todos los tickets (default='once')
2. ✅ Agregó campos de duración a eventos (default=1 día)
3. ✅ Migró tickets validados a `validation_logs`
4. ✅ Ajustó todas las fechas a zona horaria de Bogotá (UTC-5)

**Resultado**: 22 validaciones existentes fueron migradas correctamente.

## Verificación del Sistema

Ejecutar el script de pruebas:
```bash
python test_validation_system.py
```

Esto verifica:
- Estructura de base de datos
- Datos migrados
- Configuración de eventos
- Ejemplos de tickets y validaciones
- Estadísticas generales

## Zona Horaria - Funciones Útiles

### `get_bogota_now_naive()`
Obtiene la fecha/hora actual en Bogotá (sin timezone info, para SQLite)

### `format_datetime_bogota(dt, format='%Y-%m-%d %H:%M:%S')`
Formatea un datetime en zona horaria de Bogotá

### `is_same_day_bogota(dt1, dt2)`
Compara si dos fechas son el mismo día en zona horaria de Bogotá

### `get_day_start_bogota(dt=None)`
Obtiene el inicio del día (00:00:00) en Bogotá

### `get_day_end_bogota(dt=None)`
Obtiene el fin del día (23:59:59) en Bogotá

## Cómo Cambiar Tickets a Modo Daily

### Opción 1: API REST (Recomendado)

**Cambiar todos los tickets de un evento:**
```bash
POST /events/{event_id}/change-validation-mode
{
  "validation_mode": "daily"
}
```

**Cambiar tickets específicos:**
```bash
POST /tickets/batch-change-validation-mode
{
  "validation_mode": "daily",
  "ticket_ids": [1, 2, 3, 4, 5]
}
```

**Cambiar un solo ticket:**
```bash
PUT /tickets/{ticket_id}
{
  "validation_mode": "daily"
}
```

**Ver estadísticas:**
```bash
GET /events/{event_id}/validation-stats
```

### Opción 2: Script Python

```bash
# Listar eventos
python cambiar_tickets_a_daily.py --list

# Cambiar todos los tickets de un evento
python cambiar_tickets_a_daily.py 1

# Cambiar un ticket específico
python cambiar_tickets_a_daily.py --ticket 10
```

### Opción 3: SQL Directo

```sql
UPDATE tickets SET validation_mode = 'daily' WHERE event_id = 1;
```

**📖 Para más detalles:** Ver [COMO_CAMBIAR_A_MODO_DAILY.md](COMO_CAMBIAR_A_MODO_DAILY.md)

## Próximos Pasos (Opcional)

### Interfaz de Usuario
- [ ] Agregar selector de modo de validación al crear tickets (ya soportado en API)
- [ ] Mostrar historial de validaciones en detalle de ticket
- [ ] Dashboard con estadísticas de validaciones (API disponible)
- [ ] Botón para cambiar modo en masa desde UI

### Funcionalidades Adicionales
- [ ] Exportar reporte de validaciones por evento
- [ ] Notificaciones al validar tickets múltiples veces
- [ ] Límite configurable de validaciones diarias
- [ ] Validación por rango de horas del día

## Notas Importantes

1. **Compatibilidad**: Los campos `is_used` y `used_at` se mantienen por compatibilidad pero están marcados como deprecated
2. **Fuente de verdad**: `validation_logs` es ahora la fuente de verdad para validaciones
3. **Zona horaria**: TODAS las operaciones usan hora de Bogotá (UTC-5)
4. **Rendimiento**: Las consultas de validación están optimizadas con índices apropiados

## Soporte

Para reportar problemas o solicitar funcionalidades adicionales, contactar al equipo de desarrollo.

---
**Última actualización**: 2025-01-21
**Versión del sistema**: 2.0.0 (Validaciones Múltiples)
