# Sistema de Cumpleaños - Documentación

## Descripción General

El sistema de cumpleaños verifica automáticamente todos los días si hay usuarios que cumplen años y les envía felicitaciones por Email y WhatsApp. Este documento describe la implementación completa del sistema.

---

## Componentes del Sistema

### 1. **Base de Datos**

#### Tabla: `birthday_check_logs`
Registra cada ejecución del verificador de cumpleaños.

**Columnas:**
- `id`: Identificador único
- `executed_at`: Fecha y hora de ejecución
- `birthdays_found`: Cantidad de cumpleaños encontrados
- `emails_sent`: Emails enviados exitosamente
- `emails_failed`: Emails que fallaron
- `whatsapp_sent`: WhatsApp enviados exitosamente
- `whatsapp_failed`: WhatsApp que fallaron
- `whatsapp_available`: Si el servicio de WhatsApp estaba disponible
- `execution_type`: Tipo de ejecución (`automatic` o `manual`)
- `notes`: Notas adicionales sobre la ejecución

**Modelo:** `models.BirthdayCheckLog` (línea 135-148 en [models.py](models.py))

---

### 2. **Verificador de Cumpleaños**

**Archivo:** [birthday_checker.py](birthday_checker.py)

**Función Principal:** `check_and_send_birthday_emails(execution_type="automatic")`

**Proceso:**
1. Verifica si el servicio de WhatsApp está disponible
2. Busca usuarios que cumplen años hoy (día y mes)
3. Para cada usuario:
   - Envía email de felicitación con imagen personalizada
   - Envía mensaje de WhatsApp (si está disponible y tiene número)
4. Registra la ejecución en la tabla `birthday_check_logs`

**Ejecución Automática:**
Se recomienda configurar un cron job o tarea programada:
```bash
# Linux/Mac - Crontab
0 9 * * * cd /ruta/proyecto && uv run python birthday_checker.py

# Windows - Programador de tareas
# Ejecutar birthday_checker.py todos los días a las 9:00 AM
```

---

### 3. **API Endpoints**

#### `GET /birthdays/last-check`
Obtiene información de la última ejecución del sistema.

**Autenticación:** Requiere token de admin

**Respuesta exitosa:**
```json
{
  "has_logs": true,
  "last_check": {
    "id": 1,
    "executed_at": "2025-10-13T09:00:00",
    "time_since": "Hace 2 horas",
    "hours_since": 2,
    "birthdays_found": 3,
    "emails_sent": 3,
    "emails_failed": 0,
    "whatsapp_sent": 2,
    "whatsapp_failed": 1,
    "whatsapp_available": true,
    "execution_type": "automatic",
    "notes": null,
    "success_rate": {
      "email": "100.0%",
      "whatsapp": "66.7%"
    }
  }
}
```

**Respuesta sin logs:**
```json
{
  "has_logs": false,
  "message": "No hay registros de ejecuciones anteriores"
}
```

**Código:** [main.py](main.py#L520-L581)

---

#### `POST /birthdays/check-now`
Ejecuta manualmente el verificador de cumpleaños.

**Autenticación:** Requiere token de admin

**Respuesta exitosa:**
```json
{
  "success": true,
  "message": "Verificación de cumpleaños ejecutada exitosamente",
  "result": {
    "birthdays_found": 3,
    "emails_sent": 3,
    "whatsapp_sent": 2
  }
}
```

**Respuesta de error:**
```json
{
  "detail": "Error al ejecutar verificación: [mensaje de error]"
}
```

**Código:** [main.py](main.py#L584-L606)

---

### 4. **Interfaz de Usuario**

#### Indicador en Tabla de Usuarios

En la página de gestión de usuarios ([/admin/users](http://localhost:8000/admin/users)), se agregó un indicador visual en la columna "Cumpleaños" que muestra:

- **Badge informativo**: Muestra cuándo fue la última verificación
  - Verde: Menos de 24 horas
  - Amarillo: Entre 24 y 48 horas
  - Rojo: Más de 48 horas
  - "Nunca": No hay registros

**Ubicación:** Header de la columna "Cumpleaños" en [templates/users.html](templates/users.html#L91-L106)

#### Modal de Información Detallada

Al hacer clic en el badge, se abre un modal que muestra:
- Fecha y hora de la última ejecución
- Tipo de ejecución (Manual/Automática)
- Cantidad de cumpleaños encontrados
- Estadísticas de envío (Email y WhatsApp)
- Tasas de éxito
- Notas adicionales

**Funcionalidad adicional:**
- Botón "Ejecutar Verificación Ahora" para ejecutar manualmente
- Auto-actualización de datos después de ejecución manual

**Código:** [templates/users.html](templates/users.html#L289-L319) (Modal)
**JavaScript:** [templates/users.html](templates/users.html#L720-L915) (Funciones)

---

## Flujo Completo del Sistema

```
┌─────────────────────────────────────┐
│   CRON JOB / TAREA PROGRAMADA       │
│   (Ejecuta diariamente a las 9 AM)  │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   birthday_checker.py               │
│   - Verifica WhatsApp disponible    │
│   - Busca cumpleaños de hoy         │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   Para cada usuario con cumpleaños  │
│   ┌───────────────────────────────┐ │
│   │ 1. Enviar Email               │ │
│   │ 2. Enviar WhatsApp (si puede)│ │
│   └───────────────────────────────┘ │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   Guardar log en DB                 │
│   (birthday_check_logs)             │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   Admin ve el resultado en UI       │
│   - Badge con tiempo transcurrido   │
│   - Modal con detalles completos    │
└─────────────────────────────────────┘
```

---

## Ejecución Manual desde UI

El administrador puede ejecutar manualmente el verificador:

1. Ir a **Gestión de Usuarios** ([/admin/users](http://localhost:8000/admin/users))
2. Hacer clic en el badge informativo junto a "Cumpleaños"
3. En el modal, hacer clic en **"Ejecutar Verificación Ahora"**
4. Confirmar la acción
5. El sistema ejecutará la verificación y mostrará los resultados

---

## Configuración de Ejecución Automática

### Windows (Programador de Tareas)

1. Abrir "Programador de tareas"
2. Crear tarea básica:
   - **Nombre:** "Birthday Checker - IEEE Tadeo"
   - **Desencadenador:** Diariamente a las 9:00 AM
   - **Acción:** Iniciar programa
     - **Programa:** `C:\ruta\a\uv.exe`
     - **Argumentos:** `run python birthday_checker.py`
     - **Directorio:** `e:\erick\Documents\Personal\UTadeo\IEEE\Proyectos\Ticket`

### Linux/Mac (Crontab)

```bash
# Editar crontab
crontab -e

# Agregar línea (ejecutar diariamente a las 9 AM)
0 9 * * * cd /ruta/proyecto && /ruta/uv run python birthday_checker.py >> logs/birthday_checker.log 2>&1
```

---

## Archivos Modificados/Creados

### Archivos Creados
1. **migrate_birthday_log.py** - Script de migración para crear tabla
2. **add_birthday_endpoints.py** - Script para agregar endpoints a main.py
3. **BIRTHDAY_SYSTEM.md** - Esta documentación

### Archivos Modificados
1. **models.py** (línea 135-148)
   - Agregado modelo `BirthdayCheckLog`

2. **birthday_checker.py** (línea 21-172)
   - Agregado parámetro `execution_type`
   - Agregado registro en base de datos

3. **main.py** (línea 7, 518-606)
   - Agregado import de `desc` de SQLAlchemy
   - Agregado endpoint `GET /birthdays/last-check`
   - Agregado endpoint `POST /birthdays/check-now`

4. **templates/users.html**
   - Agregado badge informativo en header (línea 91-106)
   - Agregado modal de información (línea 289-319)
   - Agregado JavaScript para cargar y mostrar datos (línea 720-915)

---

## Pruebas Recomendadas

### 1. Prueba de Endpoint Last Check
```bash
curl -X GET "http://localhost:8000/birthdays/last-check" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 2. Prueba de Ejecución Manual
```bash
curl -X POST "http://localhost:8000/birthdays/check-now" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 3. Prueba desde UI
1. Iniciar servidor: `uv run uvicorn main:app --reload`
2. Acceder a http://localhost:8000/admin/users
3. Verificar que el badge aparece junto a "Cumpleaños"
4. Hacer clic en el badge y verificar modal
5. Ejecutar verificación manual

---

## Solución de Problemas

### El badge muestra "Error"
- **Causa:** No se puede conectar al endpoint
- **Solución:** Verificar que el servidor esté corriendo y que el token de autenticación sea válido

### El badge muestra "Nunca"
- **Causa:** No hay registros en la tabla `birthday_check_logs`
- **Solución:** Ejecutar una verificación manual desde el modal

### Los mensajes no se envían
- **Causa posible 1:** Servicio de WhatsApp no disponible
  - Verificar que el servicio esté corriendo en puerto 3000
- **Causa posible 2:** Configuración de email incorrecta
  - Verificar variables de entorno en `.env`

### La tarea programada no se ejecuta
- **Windows:** Verificar en Programador de tareas que la tarea esté habilitada
- **Linux/Mac:** Verificar crontab con `crontab -l`

---

## Próximas Mejoras Sugeridas

1. **Historial completo**: Agregar endpoint `/birthdays/history` para ver todas las ejecuciones
2. **Notificaciones**: Alertar al admin si una verificación falla
3. **Configuración de horario**: Permitir cambiar la hora de ejecución desde UI
4. **Plantillas personalizables**: Permitir editar mensajes de cumpleaños
5. **Reportes**: Generar reporte mensual de cumpleaños enviados

---

## Contacto y Soporte

Si encuentras algún problema o tienes sugerencias, por favor documéntalas en el sistema.

**Última actualización:** Octubre 13, 2025
**Versión del sistema:** 1.0.0
