# 🎂 Configuración del Sistema de Cumpleaños

## Descripción

Este sistema envía automáticamente correos de felicitación a los usuarios en su cumpleaños.

## Características

- ✅ Campo de cumpleaños en el perfil del usuario
- ✅ Envío automático de correos de cumpleaños
- ✅ Diseño hermoso con animaciones CSS
- ✅ Ejecución diaria mediante cron job

## Archivos Involucrados

1. **models.py** - Campo `birthday` agregado al modelo User
2. **migrate_add_birthday.py** - Script de migración de base de datos
3. **user_portal_routes.py** - API endpoints actualizados para incluir birthday
4. **portal_dashboard.html** - Formulario de perfil con campo de fecha de nacimiento
5. **email_service.py** - Función `send_birthday_email()` para enviar correos
6. **birthday_checker.py** - Script que verifica cumpleaños diarios

## Instalación

### 1. Ejecutar Migración

```bash
# En local
python migrate_add_birthday.py

# En servidor
cd /ruta/al/proyecto
uv run python migrate_add_birthday.py
```

### 2. Configurar Cron Job en el Servidor

El script `birthday_checker.py` debe ejecutarse diariamente, preferiblemente en la mañana (por ejemplo, a las 8:00 AM).

#### Opción A: Cron Job (Linux/Unix)

```bash
# Conectar al servidor
ssh svrvpsefjkcv@72.167.151.233

# Cambiar a usuario del proyecto
sudo su - ieeetadeo2006

# Editar crontab
crontab -e

# Agregar la siguiente línea (ejecutar a las 8:00 AM todos los días)
0 8 * * * cd /ruta/al/proyecto && /path/to/uv run python birthday_checker.py >> /ruta/al/proyecto/birthday_logs.txt 2>&1
```

**Ejemplo específico para el servidor:**

```bash
0 8 * * * cd ~/domains/ieeetadeo.org/public_html/ticket && ~/.cargo/bin/uv run python birthday_checker.py >> ~/domains/ieeetadeo.org/public_html/ticket/birthday_logs.txt 2>&1
```

**Explicación:**
- `0 8 * * *` - Ejecutar a las 8:00 AM todos los días
- `cd /ruta/al/proyecto` - Cambiar al directorio del proyecto
- `uv run python birthday_checker.py` - Ejecutar el script con el entorno virtual
- `>> birthday_logs.txt 2>&1` - Guardar logs de salida y errores

#### Opción B: Systemd Timer (Alternativa más robusta)

1. Crear servicio:

```bash
sudo nano /etc/systemd/system/birthday-check.service
```

Contenido:

```ini
[Unit]
Description=Birthday Email Checker
After=network.target

[Service]
Type=oneshot
User=ieeetadeo2006
WorkingDirectory=/ruta/al/proyecto
ExecStart=/path/to/uv run python birthday_checker.py
StandardOutput=append:/ruta/al/proyecto/birthday_logs.txt
StandardError=append:/ruta/al/proyecto/birthday_logs.txt
```

2. Crear timer:

```bash
sudo nano /etc/systemd/system/birthday-check.timer
```

Contenido:

```ini
[Unit]
Description=Run Birthday Checker Daily at 8 AM
Requires=birthday-check.service

[Timer]
OnCalendar=daily
OnCalendar=*-*-* 08:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

3. Habilitar y activar:

```bash
sudo systemctl enable birthday-check.timer
sudo systemctl start birthday-check.timer

# Verificar status
sudo systemctl status birthday-check.timer
sudo systemctl list-timers
```

## Verificar que funciona

### Probar manualmente

```bash
cd /ruta/al/proyecto
uv run python birthday_checker.py
```

Salida esperada:

```
=== Verificador de Cumpleaños - 2025-10-12 ===
Buscando usuarios con cumpleaños en 12/10...

Encontrados 1 cumpleaños hoy:
------------------------------------------------------------

>> Enviando correo a:
   Nombre: Juan Pérez
   Email: juan@example.com
   [OK] Correo enviado exitosamente

============================================================
RESUMEN:
  Total de cumpleaños: 1
  Correos enviados: 1
  Errores: 0
============================================================
```

### Ver logs

```bash
# Ver últimas 50 líneas del log
tail -n 50 birthday_logs.txt

# Ver logs en tiempo real
tail -f birthday_logs.txt
```

## Uso para Usuarios

### Agregar Cumpleaños

1. Los usuarios ingresan al portal: `https://ticket.ieeetadeo.org/portal/login`
2. Van a la pestaña **"Mi Perfil"**
3. Ingresan su **Fecha de Nacimiento**
4. Clic en **"Guardar Cambios"**

### ¿Qué sucede en su cumpleaños?

El día de su cumpleaños, a las 8:00 AM, el usuario recibirá un correo electrónico con:

- 🎂 Mensaje de felicitación personalizado
- 🎈 Diseño hermoso con animaciones
- 🎉 Saludo del equipo de IEEE Tadeo

## Solución de Problemas

### El correo no se envía

1. **Verificar SMTP configurado:**

```bash
# Revisar archivo .env
cat .env | grep SMTP
```

Debe tener:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu-email@gmail.com
SMTP_PASSWORD=xxxx-xxxx-xxxx-xxxx
FROM_EMAIL=tu-email@gmail.com
```

2. **Verificar logs:**

```bash
tail -n 100 birthday_logs.txt
```

3. **Probar manualmente:**

```bash
uv run python birthday_checker.py
```

### El cron job no se ejecuta

1. **Verificar que el cron está activo:**

```bash
crontab -l
```

2. **Verificar logs del sistema:**

```bash
grep CRON /var/log/syslog
```

3. **Verificar permisos:**

```bash
ls -la birthday_checker.py
chmod +x birthday_checker.py
```

### No hay cumpleaños en la base de datos

```bash
# Verificar usuarios con cumpleaños
sqlite3 tickets.db "SELECT name, email, birthday FROM users WHERE birthday IS NOT NULL;"
```

## Mantenimiento

### Cambiar la hora de envío

Editar el cron job:

```bash
crontab -e

# Cambiar de 8:00 AM a 10:00 AM
0 10 * * * cd /ruta/al/proyecto && uv run python birthday_checker.py >> birthday_logs.txt 2>&1
```

### Rotar logs (opcional)

```bash
# Crear script de rotación
nano rotate_birthday_logs.sh
```

Contenido:

```bash
#!/bin/bash
cd /ruta/al/proyecto
if [ -f birthday_logs.txt ]; then
    mv birthday_logs.txt birthday_logs_$(date +%Y%m%d).txt
    touch birthday_logs.txt
    # Eliminar logs de más de 30 días
    find . -name "birthday_logs_*.txt" -mtime +30 -delete
fi
```

Agregar a cron (ejecutar el primer día del mes):

```bash
0 0 1 * * /ruta/al/proyecto/rotate_birthday_logs.sh
```

## Despliegue en Producción

### Checklist

- [ ] Ejecutar migración en el servidor
- [ ] Configurar cron job o systemd timer
- [ ] Verificar configuración SMTP en .env
- [ ] Hacer prueba manual
- [ ] Verificar que se generan los logs
- [ ] Documentar hora de envío al equipo

### Comandos Rápidos

```bash
# SSH al servidor
ssh svrvpsefjkcv@72.167.151.233
sudo su - ieeetadeo2006

# Ir al directorio
cd ~/domains/ieeetadeo.org/public_html/ticket

# Actualizar código
git pull origin master

# Ejecutar migración
uv run python migrate_add_birthday.py

# Configurar cron
crontab -e
# Agregar: 0 8 * * * cd ~/domains/ieeetadeo.org/public_html/ticket && ~/.cargo/bin/uv run python birthday_checker.py >> ~/domains/ieeetadeo.org/public_html/ticket/birthday_logs.txt 2>&1

# Probar
uv run python birthday_checker.py
```

## Notas Adicionales

- El script verifica solo usuarios que tengan el campo `birthday` configurado
- Si no hay SMTP configurado, el script imprimirá un mensaje pero no fallará
- Los correos se envían con diseño HTML y versión de texto plano
- La edad se calcula automáticamente si se tiene el año de nacimiento

---

**¿Necesitas ayuda?** Revisa los logs en `birthday_logs.txt` o contacta al equipo de desarrollo.
