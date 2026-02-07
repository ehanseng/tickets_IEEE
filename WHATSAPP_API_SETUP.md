# Configuración de WhatsApp Business API

Este documento explica cómo obtener las credenciales necesarias para usar la API oficial de WhatsApp Business de Meta.

## Requisitos Previos

1. Una cuenta de Facebook
2. Una cuenta de Facebook Business
3. Un número de teléfono que NO esté registrado en WhatsApp (o que esté dispuesto a migrar)

## Paso 1: Crear una App en Meta for Developers

1. Ve a [Meta for Developers](https://developers.facebook.com/)
2. Haz clic en **"My Apps"** → **"Create App"**
3. Selecciona el tipo **"Business"**
4. Completa la información:
   - **App Name**: "Sistema de Tickets IEEE" (o el nombre que prefieras)
   - **App Contact Email**: Tu email
   - **Business Account**: Selecciona o crea una cuenta de negocio
5. Haz clic en **"Create App"**

## Paso 2: Agregar WhatsApp al App

1. En el dashboard de tu app, busca **"WhatsApp"** en la lista de productos
2. Haz clic en **"Set up"**
3. Selecciona tu **Business Portfolio** (o crea uno nuevo)

## Paso 3: Configurar el Número de Teléfono

1. En la sección de WhatsApp, ve a **"API Setup"**
2. Verás un número de prueba proporcionado por Meta (opcional para testing)
3. Para usar tu propio número:
   - Haz clic en **"Add phone number"**
   - Selecciona **"Add a new number"**
   - Ingresa tu número de teléfono
   - Verifica el número con el código SMS que recibirás
   - Acepta los términos de WhatsApp Business

⚠️ **IMPORTANTE**: El número que agregues NO puede estar registrado en WhatsApp personal. Si ya lo está, deberás eliminarlo primero desde la app de WhatsApp.

## Paso 4: Obtener las Credenciales

### Phone Number ID
1. En **"API Setup"**, verás una sección **"From"**
2. Copia el **Phone Number ID** (es un número largo como `123456789012345`)

### Access Token

**Opción A: Token Temporal (para pruebas - 24 horas)**
1. En **"API Setup"**, verás **"Temporary access token"**
2. Copia el token
3. ⚠️ Este token expira en 24 horas

**Opción B: Token Permanente (recomendado para producción)**
1. Ve a **"Tools" → "Graph API Explorer"**
2. Selecciona tu app en el dropdown
3. Haz clic en **"Generate Access Token"**
4. Selecciona los permisos:
   - `whatsapp_business_messaging`
   - `whatsapp_business_management`
5. Genera el token
6. Para hacerlo permanente:
   - Ve a **"Settings" → "Basic"**
   - Copia el **App ID** y **App Secret**
   - Usa la herramienta de extensión de tokens o configura un System User

### Business Account ID
1. Ve a **"WhatsApp" → "Getting Started"**
2. En la sección superior, verás **"WhatsApp Business Account ID"**
3. Copia el ID

## Paso 5: Configurar el Archivo .env

Copia las credenciales obtenidas a tu archivo `.env`:

```bash
# WhatsApp Business API (Cloud API de Meta)
WHATSAPP_PHONE_NUMBER_ID=123456789012345
WHATSAPP_BUSINESS_ACCOUNT_ID=987654321098765
WHATSAPP_ACCESS_TOKEN=EAAxxxxxxxxxxxxxxxxxx
WHATSAPP_API_VERSION=v18.0
```

## Paso 6: Probar la Configuración

1. Reinicia el servidor FastAPI
2. Intenta enviar un mensaje de prueba
3. El mensaje llegará al número que hayas verificado

## Números de Prueba (Sandbox)

Meta proporciona un número de prueba gratuito que puedes usar para desarrollo:

1. En **"API Setup"**, verás **"Test number"**
2. Para recibir mensajes en tu número personal:
   - Haz clic en **"Add recipient phone number"**
   - Ingresa tu número personal
   - Envía el código de verificación que recibirás por WhatsApp
3. Ahora puedes enviar mensajes de prueba a tu número personal

⚠️ **Límites del número de prueba:**
- Solo puede enviar a números que hayas agregado como recipientes
- Limitado a 250 conversaciones por mes
- Tiene marca de agua "Test number"

## Migrar a Producción

Para usar tu propio número en producción:

1. Agrega un **método de pago** en la cuenta de Facebook Business
2. Completa la **Business Verification** (puede tomar varios días)
3. Solicita **acceso a la API de producción**
4. Una vez aprobado, podrás enviar mensajes a cualquier número

## Precios

- **Conversaciones gratuitas**: 1000 conversaciones iniciadas por usuario por mes
- **Conversaciones pagadas**: Varían según el país (~$0.005 - $0.09 USD por conversación)
- Una **conversación** dura 24 horas desde el primer mensaje

Más información: [WhatsApp Pricing](https://developers.facebook.com/docs/whatsapp/pricing)

## Soporte y Documentación

- [Documentación oficial](https://developers.facebook.com/docs/whatsapp/cloud-api)
- [Guía de inicio rápido](https://developers.facebook.com/docs/whatsapp/cloud-api/get-started)
- [API Reference](https://developers.facebook.com/docs/whatsapp/cloud-api/reference/messages)
- [Soporte de Meta](https://developers.facebook.com/support/)

## Solución de Problemas Comunes

### Error: "Phone number not registered"
- Asegúrate de que el número esté verificado en el dashboard de Meta
- Verifica que el Phone Number ID sea correcto

### Error: "Invalid access token"
- El token temporal expiró (dura 24 horas)
- Genera un nuevo token o usa un token permanente

### Error: "Recipient phone number not in allowed list"
- Si usas el número de prueba, agrega el destinatario en "Add recipient"
- O migra a producción para enviar a cualquier número

### No recibo mensajes
- Verifica que el número destinatario esté en formato internacional sin "+" (ej: 573001234567)
- Revisa los logs del servidor para ver errores específicos
