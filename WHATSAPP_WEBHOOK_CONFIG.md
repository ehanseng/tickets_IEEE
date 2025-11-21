# Configuración del Webhook de WhatsApp

Este documento explica cómo configurar el webhook de WhatsApp en Meta for Developers.

## ¿Qué es un Webhook?

Un webhook es un endpoint (URL) en tu servidor que Meta llamará automáticamente cuando:
- Alguien envíe un mensaje a tu número de WhatsApp Business
- Cambie el estado de un mensaje que enviaste (entregado, leído, fallido, etc.)
- Ocurran otros eventos relacionados con WhatsApp

## Paso 1: Configurar el Token de Verificación

1. Abre tu archivo `.env` (o créalo si no existe copiando `.env.example`)
2. Agrega o modifica esta línea:

```bash
WHATSAPP_WEBHOOK_VERIFY_TOKEN=mi_token_secreto_muy_seguro_123
```

⚠️ **IMPORTANTE**: Cambia `mi_token_secreto_muy_seguro_123` por un string aleatorio y seguro. Este token es como una contraseña que solo tú y Meta conocen.

**Ejemplo de un token seguro:**
```bash
WHATSAPP_WEBHOOK_VERIFY_TOKEN=IEEE_WA_2025_x8k9L2mP4nQ7
```

## Paso 2: Obtener la URL del Webhook

Tu URL del webhook depende de dónde esté desplegado tu servidor:

### Opción A: Servidor en Producción (recomendado)

Si tu servidor está en producción (por ejemplo, en ticket.ieeetadeo.org):

```
URL del webhook: https://ticket.ieeetadeo.org/webhooks/whatsapp
```

### Opción B: Servidor Local (solo para pruebas)

Si estás probando localmente, necesitas exponer tu servidor local a internet usando una herramienta como **ngrok**:

1. Descarga ngrok: https://ngrok.com/download
2. Ejecuta ngrok:
   ```bash
   ngrok http 8000
   ```
3. Ngrok te dará una URL como: `https://abc123.ngrok.io`
4. Tu URL del webhook será: `https://abc123.ngrok.io/webhooks/whatsapp`

⚠️ **NOTA**: La URL de ngrok cambia cada vez que lo reinicies (a menos que uses una cuenta de pago).

## Paso 3: Configurar el Webhook en Meta for Developers

1. Ve a [Meta for Developers](https://developers.facebook.com/)
2. Selecciona tu app de WhatsApp
3. En el menú lateral, ve a **WhatsApp > Configuration**
4. En la sección **Webhook**, haz clic en **Edit**

5. Completa los campos:

   **Callback URL (URL de devolución de llamada):**
   ```
   https://ticket.ieeetadeo.org/webhooks/whatsapp
   ```
   *(O tu URL de ngrok si estás probando localmente)*

   **Verify Token (Token de verificación):**
   ```
   IEEE_WA_2025_x8k9L2mP4nQ7
   ```
   *(Usa exactamente el mismo token que pusiste en tu archivo `.env`)*

6. Haz clic en **Verify and Save**

## Paso 4: Verificación

Si todo está configurado correctamente:

1. Meta enviará una petición GET a tu webhook
2. Tu servidor verificará que el token coincida
3. Si el token es correcto, Meta mostrará ✅ **Webhook configured successfully**

### Si la verificación falla:

**Error común 1: "Verification failed"**
- Verifica que el token en `.env` sea exactamente igual al que pusiste en Meta
- Asegúrate de que no tenga espacios al inicio o final
- Verifica que reiniciaste el servidor después de modificar `.env`

**Error común 2: "Connection failed" o "Timeout"**
- Verifica que tu servidor esté corriendo (`http://0.0.0.0:8000`)
- Si usas ngrok, verifica que esté corriendo y la URL sea correcta
- Si estás en producción, verifica que el dominio esté activo y el puerto 443 (HTTPS) esté abierto

**Error común 3: "SSL certificate error"**
- Meta requiere HTTPS (no HTTP)
- Si estás en producción, asegúrate de tener un certificado SSL válido
- Ngrok proporciona HTTPS automáticamente

## Paso 5: Suscribirse a Eventos

Después de configurar el webhook, debes suscribirte a los eventos que quieres recibir:

1. En la misma página de **Configuration**, busca **Webhook fields**
2. Haz clic en **Manage**
3. Suscríbete a estos campos (recomendados):

   ✅ **messages** - Para recibir mensajes que te envíen
   ✅ **message_status** - Para saber si tus mensajes fueron entregados/leídos

4. Haz clic en **Subscribe**

## ¿Qué Hace el Webhook?

Actualmente, el webhook está configurado para:

- ✅ **Registrar todos los eventos** en los logs del servidor
- ✅ **Confirmar recepción** a Meta (retorna 200 OK)
- 📝 **Logging de mensajes recibidos**: Muestra quién envió el mensaje
- 📝 **Logging de estados**: Muestra cuándo un mensaje fue entregado/leído

### Ver los Logs

Para ver los eventos que llegan al webhook, revisa los logs de tu servidor:

```bash
# Si usas el servidor directamente
tail -f nohup.out

# O revisa la consola donde está corriendo el servidor
```

Verás mensajes como:
```
[WEBHOOK] Evento de WhatsApp recibido:
[WEBHOOK] Mensaje recibido de 573001234567 (Tipo: text, ID: wamid.xxx)
[WEBHOOK] Estado de mensaje wamid.xxx: delivered (Destinatario: 573001234567)
```

## Funcionalidades Futuras (Opcional)

Puedes extender el webhook para:

- 📊 Guardar estados de mensajes en la base de datos
- 🤖 Responder automáticamente a ciertos mensajes
- 📈 Generar métricas de entrega y lectura
- 💬 Crear un bot de atención al cliente

El código está en [main.py:1724-1779](main.py#L1724-L1779) y está listo para agregar más funcionalidades.

## Solución de Problemas

### Verificar que el Endpoint Funciona

Puedes probar manualmente el endpoint de verificación:

```bash
curl "https://ticket.ieeetadeo.org/webhooks/whatsapp?hub.mode=subscribe&hub.verify_token=IEEE_WA_2025_x8k9L2mP4nQ7&hub.challenge=12345"
```

Deberías recibir: `12345` (el challenge)

### Ver Logs del Webhook en Meta

1. Ve a **WhatsApp > Configuration**
2. Busca **Webhook > Recent Deliveries**
3. Ahí verás todos los intentos de Meta de enviar eventos a tu webhook
4. Puedes ver el payload completo y la respuesta de tu servidor

## Seguridad

⚠️ **Importante:**
- **Nunca** compartas tu `WHATSAPP_WEBHOOK_VERIFY_TOKEN`
- **Nunca** lo subas a repositorios públicos (usa `.env` y `.gitignore`)
- Cambia el token si sospechas que fue comprometido
- Usa HTTPS siempre (Meta lo requiere)

## Recursos Adicionales

- [Documentación oficial de Webhooks de WhatsApp](https://developers.facebook.com/docs/whatsapp/cloud-api/webhooks)
- [Ejemplos de payloads de webhooks](https://developers.facebook.com/docs/whatsapp/cloud-api/webhooks/payload-examples)
- [Guía de ngrok](https://ngrok.com/docs)
