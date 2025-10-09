# Configuración SMTP para Envío de Correos

Este documento explica cómo configurar el envío de correos electrónicos para el sistema de tickets.

## 📧 Servicios SMTP Recomendados (Gratis)

### Opción 1: Gmail SMTP (Recomendado para desarrollo)

**Límites:** 500 correos/día (15,000/mes)

**Ventajas:**
- ✅ Fácil de configurar
- ✅ Gratuito
- ✅ Confiable
- ✅ No requiere tarjeta de crédito

**Configuración:**

1. **Activar verificación en 2 pasos:**
   - Ve a tu cuenta de Google: https://myaccount.google.com/
   - Ir a "Seguridad"
   - Activar "Verificación en 2 pasos"

2. **Crear contraseña de aplicación:**
   - En "Seguridad" → "Contraseñas de aplicaciones"
   - Seleccionar "Correo" y "Otra aplicación"
   - Copiar la contraseña de 16 dígitos generada

3. **Crear archivo `.env` en la raíz del proyecto:**

```env
# Configuración SMTP - Gmail
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu-email@gmail.com
SMTP_PASSWORD=xxxx-xxxx-xxxx-xxxx
FROM_EMAIL=tu-email@gmail.com
FROM_NAME=IEEE Tadeo - Sistema de Tickets

# URL base del sistema
BASE_URL=http://127.0.0.1:8000
```

---

### Opción 2: Brevo (Sendinblue) - Recomendado para producción

**Límites:** 300 correos/día (9,000/mes)

**Ventajas:**
- ✅ Diseñado para envío masivo
- ✅ Panel de control con estadísticas
- ✅ Plantillas de correo
- ✅ No requiere tarjeta de crédito
- ✅ Mejor entregabilidad

**Configuración:**

1. **Crear cuenta en Brevo:**
   - Registrarse en: https://www.brevo.com/
   - Verificar cuenta y dominio de correo

2. **Obtener credenciales SMTP:**
   - Ir a "Settings" → "SMTP & API"
   - Copiar:
     - SMTP Server: smtp-relay.brevo.com
     - Port: 587
     - Login: (tu email)
     - SMTP Key: (generar una nueva)

3. **Crear archivo `.env`:**

```env
# Configuración SMTP - Brevo
SMTP_HOST=smtp-relay.brevo.com
SMTP_PORT=587
SMTP_USER=tu-email@ejemplo.com
SMTP_PASSWORD=tu-smtp-key-de-brevo
FROM_EMAIL=tu-email@ejemplo.com
FROM_NAME=IEEE Tadeo - Sistema de Tickets

# URL base del sistema
BASE_URL=http://127.0.0.1:8000
```

---

### Opción 3: Mailgun

**Límites:** 100 correos/día (3,000/mes) gratis

**Configuración:**

```env
SMTP_HOST=smtp.mailgun.org
SMTP_PORT=587
SMTP_USER=postmaster@tu-dominio.mailgun.org
SMTP_PASSWORD=tu-password-de-mailgun
FROM_EMAIL=noreply@tu-dominio.com
FROM_NAME=IEEE Tadeo - Sistema de Tickets
BASE_URL=http://127.0.0.1:8000
```

---

### Opción 4: SendGrid

**Límites:** 100 correos/día (3,000/mes) gratis

**Configuración:**

```env
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=tu-api-key-de-sendgrid
FROM_EMAIL=tu-email@ejemplo.com
FROM_NAME=IEEE Tadeo - Sistema de Tickets
BASE_URL=http://127.0.0.1:8000
```

---

## 🚀 Configuración para Producción

Cuando despliegues en un servidor, cambia la URL base:

```env
BASE_URL=https://tu-dominio.com
```

---

## 🔒 Seguridad

**IMPORTANTE:**
- ❌ **NUNCA** subas el archivo `.env` a GitHub
- ✅ El archivo `.env` ya está en `.gitignore`
- ✅ Usa variables de entorno del servidor en producción
- ✅ Rota las contraseñas periódicamente

---

## 🧪 Modo de Desarrollo (Sin SMTP)

Si no configuras SMTP, el sistema funcionará en modo de desarrollo:
- Los correos NO se enviarán
- La información (URL, PIN) se imprimirá en la consola
- Útil para pruebas sin configurar correo

---

## ✅ Verificar Configuración

Después de crear el archivo `.env`, reinicia el servidor:

```bash
uv run uvicorn main:app --reload
```

Deberías ver en la consola:

```
✓ SMTP configurado: tu-email@gmail.com via smtp.gmail.com:587
```

Si ves:

```
⚠️  SMTP no configurado - Los correos se simularán
```

Revisa que el archivo `.env` esté en la raíz del proyecto y tenga las variables correctas.

---

## 📊 Comparación de Servicios

| Servicio | Límite Diario | Límite Mensual | Configuración | Recomendado Para |
|----------|---------------|----------------|---------------|------------------|
| **Gmail** | 500 | 15,000 | ⭐⭐⭐ Muy Fácil | Desarrollo/Pruebas |
| **Brevo** | 300 | 9,000 | ⭐⭐ Fácil | Producción |
| **Mailgun** | 100 | 3,000 | ⭐⭐ Fácil | Proyectos pequeños |
| **SendGrid** | 100 | 3,000 | ⭐⭐ Fácil | Proyectos pequeños |

---

## 🎯 Recomendación Final

**Para tu caso (2,000 mensajes/mes):**

1. **Desarrollo/Pruebas:** Usa **Gmail SMTP** (más fácil y rápido de configurar)
2. **Producción:** Usa **Brevo** (mejor entregabilidad y estadísticas)

---

## 🆘 Solución de Problemas

### Error: "Authentication failed"
- Verifica que las credenciales sean correctas
- En Gmail, asegúrate de usar la contraseña de aplicación (no la contraseña normal)
- Verifica que la verificación en 2 pasos esté activa

### Error: "Connection refused"
- Verifica el puerto (debe ser 587 para STARTTLS)
- Verifica que no haya firewall bloqueando el puerto

### Los correos llegan a Spam
- Configura SPF y DKIM en tu dominio
- Usa Brevo o SendGrid que tienen mejor reputación
- Evita palabras spam en el asunto

### Los correos no se envían
- Revisa los logs en la consola
- Verifica que el archivo `.env` esté en la raíz
- Reinicia el servidor después de cambiar `.env`
