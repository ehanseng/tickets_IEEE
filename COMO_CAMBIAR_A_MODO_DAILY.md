# Cómo Cambiar Tickets a Modo Daily (Validación Diaria)

Esta guía te muestra todas las formas de cambiar tickets del modo `'once'` (una validación) al modo `'daily'` (una validación por día).

## 🎯 Casos de Uso

El modo `'daily'` es útil para:
- **Conferencias multi-día**: Validar entrada cada día
- **Talleres de varios días**: Controlar asistencia diaria
- **Eventos de fin de semana**: Validar sábado y domingo por separado

---

## Método 1: API REST (Recomendado para Frontend)

### Cambiar Todos los Tickets de un Evento

**Endpoint:** `POST /events/{event_id}/change-validation-mode`

**Request:**
```json
{
  "validation_mode": "daily"
}
```

**Ejemplo con cURL:**
```bash
curl -X POST "http://localhost:8070/events/1/change-validation-mode" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TU_TOKEN_AQUI" \
  -d '{"validation_mode": "daily"}'
```

**Respuesta:**
```json
{
  "success": true,
  "message": "107 tickets actualizados a modo 'daily'",
  "event_id": 1,
  "event_name": "1st IEEE Affinity and Special Interest Groups Meeting",
  "updated_count": 107,
  "validation_mode": "daily"
}
```

### Cambiar Solo Algunos Tickets de un Evento

**Request:**
```json
{
  "validation_mode": "daily",
  "ticket_ids": [1, 2, 3, 4, 5]
}
```

**Ejemplo con cURL:**
```bash
curl -X POST "http://localhost:8070/events/1/change-validation-mode" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TU_TOKEN_AQUI" \
  -d '{
    "validation_mode": "daily",
    "ticket_ids": [1, 2, 3, 4, 5]
  }'
```

### Cambiar Tickets por IDs (Sin importar el evento)

**Endpoint:** `POST /tickets/batch-change-validation-mode`

**Request:**
```json
{
  "validation_mode": "daily",
  "ticket_ids": [10, 20, 30, 40]
}
```

**Ejemplo con cURL:**
```bash
curl -X POST "http://localhost:8070/tickets/batch-change-validation-mode" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TU_TOKEN_AQUI" \
  -d '{
    "validation_mode": "daily",
    "ticket_ids": [10, 20, 30, 40]
  }'
```

### Cambiar un Solo Ticket

**Endpoint:** `PUT /tickets/{ticket_id}`

**Request:**
```json
{
  "validation_mode": "daily"
}
```

**Ejemplo con cURL:**
```bash
curl -X PUT "http://localhost:8070/tickets/1" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TU_TOKEN_AQUI" \
  -d '{"validation_mode": "daily"}'
```

---

## Método 2: Script Python (Recomendado para Operaciones Manuales)

### Opción A: Usar el Script Interactivo

```bash
# Ver todos los eventos disponibles
python cambiar_tickets_a_daily.py --list

# Cambiar todos los tickets de un evento específico
python cambiar_tickets_a_daily.py 1

# Cambiar un ticket específico
python cambiar_tickets_a_daily.py --ticket 10

# Cambiar TODOS los tickets (¡CUIDADO!)
python cambiar_tickets_a_daily.py --all
```

**Ejemplo de ejecución:**
```bash
$ python cambiar_tickets_a_daily.py 1

=== Cambiar tickets a modo DAILY ===
Evento: 1st IEEE Affinity and Special Interest Groups Meeting
Fecha: 2025-11-21 14:00:00
Tickets a modificar: 107

¿Deseas cambiar 107 tickets al modo 'daily'? (s/n): s

[OK] 107 tickets cambiados a modo 'daily'

Ejemplos de tickets actualizados:
  - Ticket #110 (Erick Hansen): modo 'daily'
  - Ticket #109 (Diana Salavarrieta): modo 'daily'
  - Ticket #108 (Juliana Gonzalez): modo 'daily'
```

### Opción B: Script SQL Personalizado

Crea tu propio script SQL:

```sql
-- Ver estado actual
SELECT
    e.id as event_id,
    e.name,
    COUNT(t.id) as total_tickets,
    SUM(CASE WHEN t.validation_mode = 'daily' THEN 1 ELSE 0 END) as daily_tickets
FROM events e
LEFT JOIN tickets t ON e.id = t.event_id
GROUP BY e.id;

-- Cambiar tickets de un evento específico
UPDATE tickets
SET validation_mode = 'daily'
WHERE event_id = 1;

-- Verificar cambios
SELECT validation_mode, COUNT(*) as count
FROM tickets
WHERE event_id = 1
GROUP BY validation_mode;
```

Ejecutar:
```bash
mysql -u ieeetadeo -p ieeetadeo < mi_script.sql
```

---

## Método 3: SQL Directo

### Usando MySQL en la terminal

```bash
# Abrir la base de datos MySQL
mysql -u ieeetadeo -p ieeetadeo

# Cambiar todos los tickets de un evento
UPDATE tickets SET validation_mode = 'daily' WHERE event_id = 1;

# Verificar cambios
SELECT validation_mode, COUNT(*) as count FROM tickets WHERE event_id = 1 GROUP BY validation_mode;

# Salir
EXIT;
```

### Cambiar tickets según condiciones

```sql
-- Cambiar tickets de usuarios IEEE
UPDATE tickets
SET validation_mode = 'daily'
WHERE user_id IN (SELECT id FROM users WHERE is_ieee_member = 1);

-- Cambiar tickets de un evento específico que no han sido validados
UPDATE tickets
SET validation_mode = 'daily'
WHERE event_id = 1 AND is_used = 0;

-- Cambiar tickets creados después de una fecha
UPDATE tickets
SET validation_mode = 'daily'
WHERE event_id = 1 AND created_at > '2025-11-01';
```

---

## Método 4: Crear Tickets Nuevos en Modo Daily

Cuando creas nuevos tickets, simplemente especifica el modo:

**Request:**
```json
{
  "user_id": 1,
  "event_id": 1,
  "companions": 0,
  "validation_mode": "daily"
}
```

**Ejemplo con cURL:**
```bash
curl -X POST "http://localhost:8070/tickets/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TU_TOKEN_AQUI" \
  -d '{
    "user_id": 1,
    "event_id": 1,
    "companions": 0,
    "validation_mode": "daily"
  }'
```

---

## 📊 Ver Estadísticas de Validación

**Endpoint:** `GET /events/{event_id}/validation-stats`

```bash
curl -X GET "http://localhost:8070/events/1/validation-stats" \
  -H "Authorization: Bearer TU_TOKEN_AQUI"
```

**Respuesta:**
```json
{
  "event_id": 1,
  "event_name": "1st IEEE Affinity and Special Interest Groups Meeting",
  "total_tickets": 107,
  "validation_modes": {
    "once": 0,
    "daily": 107
  },
  "validations": {
    "total_validations": 22,
    "validated_tickets": 22,
    "pending_tickets": 85
  }
}
```

---

## ⚠️ Consideraciones Importantes

### Antes de Cambiar a Modo Daily

1. **Verificar duración del evento:**
   - El modo daily es para eventos de varios días
   - Para eventos de 1 día, usar modo 'once'

2. **Tickets ya validados:**
   - Los tickets ya validados PUEDEN cambiar a modo daily
   - Permitirá nuevas validaciones en días diferentes
   - La primera validación se mantiene en el historial

3. **No afecta validaciones existentes:**
   - Las validaciones previas se mantienen en `validation_logs`
   - El historial completo se preserva

### Después de Cambiar a Modo Daily

1. **Comportamiento esperado:**
   - Primera validación: "Ticket válido - Acceso permitido"
   - Segunda validación (mismo día): "Ticket ya fue validado hoy..."
   - Segunda validación (otro día): "Ticket válido - Acceso permitido. Validación #2"

2. **Configurar duración del evento:**
```sql
-- Actualizar evento para reflejar varios días
UPDATE events
SET
    event_duration_days = 3,
    event_end_date = DATE_ADD(event_date, INTERVAL 2 DAY)
WHERE id = 1;
```

---

## 🔄 Volver a Modo 'Once'

Si necesitas revertir los cambios:

```bash
# API
curl -X POST "http://localhost:8070/events/1/change-validation-mode" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TU_TOKEN_AQUI" \
  -d '{"validation_mode": "once"}'

# SQL
mysql -u ieeetadeo -p ieeetadeo -e "UPDATE tickets SET validation_mode = 'once' WHERE event_id = 1"

# Script Python
python cambiar_tickets_a_daily.py 1
# (El script te preguntará qué modo usar)
```

---

## 📝 Ejemplo Completo: Evento de 3 Días

```bash
# 1. Actualizar el evento
mysql -u ieeetadeo -p ieeetadeo -e "
UPDATE events
SET event_duration_days = 3,
    event_end_date = DATE_ADD(event_date, INTERVAL 2 DAY)
WHERE id = 1;
"

# 2. Cambiar todos los tickets a modo daily
python cambiar_tickets_a_daily.py 1

# 3. Verificar estadísticas
curl -X GET "http://localhost:8070/events/1/validation-stats" \
  -H "Authorization: Bearer TU_TOKEN_AQUI"

# 4. Listo para validar!
# - Día 1: Primera validación permitida
# - Día 2: Segunda validación permitida
# - Día 3: Tercera validación permitida
# - Mismo día: Solo 1 validación por día
```

---

## 🆘 Solución de Problemas

### Error: "Debes especificar al menos un ticket_id"
- Solución: Asegúrate de incluir `ticket_ids` en el request o quitarlo por completo para cambiar todos

### Error: "Evento no encontrado"
- Solución: Verifica que el event_id existe con `python cambiar_tickets_a_daily.py --list`

### Los tickets no cambian
- Solución: Verifica que tengas permisos de administrador (token válido)

### ¿Cómo sé qué tickets están en modo daily?
```bash
curl -X GET "http://localhost:8070/events/1/validation-stats" \
  -H "Authorization: Bearer TU_TOKEN_AQUI"
```

---

## 📚 Referencias

- [VALIDACIONES_MULTIPLES_README.md](VALIDACIONES_MULTIPLES_README.md) - Documentación completa del sistema
- [cambiar_tickets_a_daily.py](cambiar_tickets_a_daily.py) - Script interactivo
- [update_ticket_to_daily_example.sql](update_ticket_to_daily_example.sql) - Ejemplos SQL

---

**¿Preguntas?** Consulta la documentación principal o contacta al equipo de desarrollo.
