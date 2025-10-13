# Configurar Verificación Automática de Cumpleaños

## Opción 1: Script Automático (Recomendado)

### Pasos:

1. **Ejecutar el script de configuración**:
   - Doble clic en: `setup_daily_birthday_task.bat`
   - O desde terminal: `.\setup_daily_birthday_task.bat`

2. **Ingresar la hora deseada**:
   - El script te preguntará a qué hora ejecutar la verificación
   - Formato 24 horas: `09:00` (para las 9 AM)
   - Si no ingresas nada, usará `09:00` por defecto

3. **Listo!**
   - La tarea se creará automáticamente
   - Se ejecutará todos los días a la hora configurada

### Verificar que la tarea fue creada:

1. Presiona `Win + R`
2. Escribe: `taskschd.msc` y presiona Enter
3. Busca la tarea: **IEEE_Birthday_Checker**
4. Verifica que esté "Lista" y programada para ejecutarse diariamente

---

## Opción 2: Configuración Manual

Si prefieres crear la tarea manualmente:

### Pasos:

1. **Abrir Programador de Tareas**:
   - Presiona `Win + R`
   - Escribe: `taskschd.msc`
   - Presiona Enter

2. **Crear Nueva Tarea**:
   - Click derecho en "Biblioteca del Programador de tareas"
   - Selecciona "Crear tarea..."

3. **Pestaña "General"**:
   - Nombre: `IEEE_Birthday_Checker`
   - Descripción: `Verificación diaria de cumpleaños y envío automático de felicitaciones`
   - Selecciona: "Ejecutar aunque el usuario no haya iniciado sesión"
   - Marca: "Ejecutar con los privilegios más altos"

4. **Pestaña "Desencadenadores"**:
   - Click en "Nuevo..."
   - Iniciar la tarea: **Según una programación**
   - Configuración: **Diariamente**
   - Repetir cada: **1 días**
   - Hora: **09:00:00** (o la hora que prefieras)
   - Habilitado: ✓
   - Click "Aceptar"

5. **Pestaña "Acciones"**:
   - Click en "Nueva..."
   - Acción: **Iniciar un programa**
   - Programa/script: `cmd`
   - Agregar argumentos:
     ```
     /c cd /d "e:\erick\Documents\Personal\UTadeo\IEEE\Proyectos\Ticket" && uv run python birthday_checker.py >> logs\birthday_checker.log 2>&1
     ```
   - Click "Aceptar"

6. **Pestaña "Condiciones"**:
   - Desmarca: "Iniciar la tarea solo si el equipo está conectado a la corriente alterna"
   - Marca: "Activar la tarea si la ejecución se omite"

7. **Pestaña "Configuración"**:
   - Marca: "Permitir que la tarea se ejecute a petición"
   - Marca: "Ejecutar la tarea lo antes posible después de perder una ejecución programada"
   - Si la tarea ya se está ejecutando: "No iniciar una nueva instancia"

8. **Guardar**:
   - Click "Aceptar"
   - Ingresa tu contraseña de Windows si te la pide

---

## Verificar Funcionamiento

### Probar la tarea manualmente:

1. Abre el Programador de tareas
2. Encuentra la tarea: **IEEE_Birthday_Checker**
3. Click derecho → "Ejecutar"
4. Verifica los logs en: `logs\birthday_checker.log`

### Ver registros de ejecución:

- **En el Programador de Tareas**:
  - Selecciona la tarea
  - Ve a la pestaña "Historial"

- **En archivos de log**:
  - Abre: `logs\birthday_checker.log`
  - Verás el historial completo de ejecuciones

- **En la base de datos**:
  - Ve a http://127.0.0.1:8000/admin/users
  - Click en el badge junto a "Cumpleaños"
  - Verás todas las ejecuciones con estadísticas

---

## Modificar la Tarea

Si necesitas cambiar la hora o configuración:

1. Abre el Programador de tareas
2. Click derecho en **IEEE_Birthday_Checker**
3. Selecciona "Propiedades"
4. Modifica lo que necesites
5. Click "Aceptar"

---

## Eliminar la Tarea

Para desactivar la verificación automática:

1. Abre el Programador de tareas
2. Click derecho en **IEEE_Birthday_Checker**
3. Selecciona "Eliminar"
4. Confirma

---

## Solución de Problemas

### La tarea no se ejecuta:

1. **Verificar el estado**:
   - Abre el Programador de tareas
   - Verifica que la tarea esté "Lista" (no "Deshabilitada")

2. **Verificar el historial**:
   - Selecciona la tarea
   - Ve a la pestaña "Historial"
   - Busca errores

3. **Verificar logs**:
   - Abre: `logs\birthday_checker.log`
   - Revisa si hay errores

4. **Ejecutar manualmente**:
   - Click derecho en la tarea → "Ejecutar"
   - Si funciona manualmente pero no automáticamente, verifica:
     - Permisos de usuario
     - Condiciones de energía
     - Credenciales de Windows

### No se envían WhatsApp:

- **Verificar que el servicio esté corriendo**:
  - El servicio de WhatsApp debe estar activo 24/7
  - Considera usar `start.bat` o iniciar el servicio de WhatsApp como servicio de Windows

### No se envían Emails:

- **Verificar configuración de Resend**:
  - Revisa el archivo `.env`
  - Verifica que `RESEND_API_KEY` esté configurado

---

## Recomendaciones

1. **Mantener el servicio de WhatsApp corriendo**:
   - Usa `start.bat` para iniciar todos los servicios
   - O configura el servicio de WhatsApp como servicio de Windows

2. **Revisar logs periódicamente**:
   - Verifica `logs\birthday_checker.log` semanalmente
   - Revisa la base de datos desde la UI

3. **Probar antes de cumpleaños importantes**:
   - Usa el botón "Ejecutar Verificación Ahora" en la UI
   - Verifica que todo funcione correctamente

4. **Backup de la base de datos**:
   - Considera hacer backup de `tickets.db` regularmente
   - Especialmente de la tabla `birthday_check_logs`

---

## Hora Recomendada

Se recomienda ejecutar la verificación entre **8:00 AM** y **10:00 AM**:
- Los usuarios revisarán su correo temprano
- WhatsApp llegará en horario adecuado
- No interrumpe el sueño ni llega muy tarde

---

## Contacto

Si tienes problemas con la configuración, revisa:
- [BIRTHDAY_SYSTEM.md](BIRTHDAY_SYSTEM.md) - Documentación completa del sistema
- [START_HERE.md](START_HERE.md) - Guía de inicio general

**Última actualización:** Octubre 13, 2025
