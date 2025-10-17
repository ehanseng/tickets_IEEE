# 📱 Servicio de WhatsApp para IEEE Tadeo

Servicio Node.js que proporciona una API REST para enviar mensajes de WhatsApp usando whatsapp-web.js.

## 🚀 Características

- ✅ **100% GRATIS** - Sin costos por mensaje
- ✅ **Sin SIM físico** - Usa tu WhatsApp existente
- ✅ **API REST simple** - Integración fácil con Python
- ✅ **Envío individual y masivo** - Flexible para diferentes casos de uso
- ✅ **Verificación de números** - Valida antes de enviar
- ✅ **Reconexión automática** - Manejo robusto de desconexiones

## 📋 Requisitos

- Node.js v18 o superior
- npm (viene con Node.js)
- WhatsApp instalado en tu celular

## 🔧 Instalación

### 1. Instalar Node.js

**Windows:**
```bash
# Descarga e instala desde: https://nodejs.org/
# Recomendado: Versión LTS (Long Term Support)
```

Verifica la instalación:
```bash
node --version  # Debe mostrar v18.x o superior
npm --version
```

### 2. Instalar dependencias del servicio

```bash
cd whatsapp-service
npm install
```

Esto instalará:
- `whatsapp-web.js` - Cliente de WhatsApp
- `express` - Servidor web
- `qrcode-terminal` - Para mostrar QR en consola
- `cors` - Manejo de CORS

## 🎯 Uso

### Iniciar el servicio

```bash
cd whatsapp-service
npm start
```

Verás algo como:
```
[OK] Servidor WhatsApp API corriendo en http://localhost:3000
[INFO] Inicializando cliente de WhatsApp...
[QR] Escanea este código QR con tu WhatsApp:
```

### Escanear código QR

**¡IMPORTANTE! Lee esto antes de escanear:**

1. **Opción Recomendada: WhatsApp Business**
   - Descarga WhatsApp Business (app azul/verde) desde tu tienda de apps
   - Configura con tu número
   - Ve a Settings → Linked Devices → Link a Device
   - Escanea el QR que aparece en la consola
   - ✅ **Ventaja:** No afecta tu WhatsApp personal

2. **Opción Alternativa: WhatsApp Personal**
   - Abre tu WhatsApp normal
   - Ve a Settings → Linked Devices → Link a Device
   - Escanea el QR
   - ⚠️ **Precaución:** Usar con cuidado

Una vez escaneado, verás:
```
[OK] Cliente de WhatsApp está listo!
```

### Cambiar de número después

Para usar otro número:
```bash
# 1. Detener el servicio (Ctrl+C)
# 2. Eliminar la sesión guardada
rm -rf whatsapp-session

# 3. Iniciar de nuevo
npm start

# 4. Escanear nuevo QR con el otro número
```

## 📡 API Endpoints

### GET / - Estado del servicio
```bash
curl http://localhost:3000/
```

Respuesta:
```json
{
  "service": "WhatsApp API Service",
  "version": "1.0.0",
  "status": "ready",
  "hasQR": false
}
```

### GET /status - Estado de conexión
```bash
curl http://localhost:3000/status
```

### POST /send - Enviar mensaje individual
```bash
curl -X POST http://localhost:3000/send \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+573054497235",
    "message": "Hola desde IEEE Tadeo!"
  }'
```

### POST /send-bulk - Enviar múltiples mensajes
```bash
curl -X POST http://localhost:3000/send-bulk \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"phone": "+573054497235", "message": "Hola!"},
      {"phone": "+573012345678", "message": "¡Feliz cumpleaños!"}
    ]
  }'
```

### POST /restart - Reiniciar cliente
```bash
curl -X POST http://localhost:3000/restart
```

## 🐍 Integración con Python

El proyecto incluye un cliente Python listo para usar:

```python
from whatsapp_client import WhatsAppClient

client = WhatsAppClient()

# Verificar estado
if client.is_ready():
    # Enviar mensaje
    result = client.send_message(
        phone="+573054497235",
        message="¡Hola desde Python!"
    )

    if result['success']:
        print("Mensaje enviado!")
```

### Script de prueba
```bash
# Desde el directorio principal del proyecto
uv run python test_whatsapp.py
```

## ⚙️ Ejecución en Producción

### Mantener el servicio corriendo 24/7

**Opción 1: PM2 (Recomendado)**
```bash
# Instalar PM2 globalmente
npm install -g pm2

# Iniciar servicio con PM2
cd whatsapp-service
pm2 start server.js --name whatsapp-service

# Ver logs
pm2 logs whatsapp-service

# Reiniciar
pm2 restart whatsapp-service

# Configurar para iniciar automáticamente
pm2 startup
pm2 save
```

**Opción 2: nohup (Linux/Mac)**
```bash
cd whatsapp-service
nohup npm start > whatsapp.log 2>&1 &
```

**Opción 3: screen (Linux)**
```bash
screen -S whatsapp
cd whatsapp-service
npm start
# Presiona Ctrl+A, luego D para desconectar
# screen -r whatsapp  # Para reconectar
```

## 🔒 Seguridad y Buenas Prácticas

### ⚠️ Riesgo de Ban

WhatsApp no permite oficialmente el uso de APIs no oficiales. Para reducir el riesgo:

1. **No envíes spam** - Máximo 50-100 mensajes por día
2. **Espera entre mensajes** - El script ya incluye delay de 2 segundos
3. **No envíes a desconocidos** - Solo a usuarios del sistema
4. **Usa WhatsApp Business** - Es menos restrictivo
5. **Ten un número backup** - Por si acaso

### 🛡️ Protección

- El servicio guarda la sesión en `whatsapp-session/`
- **No compartas** esta carpeta - contiene tu autenticación
- Agrega a `.gitignore`:
```
whatsapp-session/
```

## 🐛 Problemas Comunes

### "WhatsApp no está conectado"
- Verifica que el servicio Node.js esté corriendo
- Revisa que hayas escaneado el QR
- Intenta reiniciar: `POST /restart`

### "Este número no está registrado en WhatsApp"
- El número no tiene WhatsApp instalado
- Verifica el formato: +573054497235

### "Error al enviar mensaje"
- Puede ser restricción temporal de WhatsApp
- Espera unas horas y vuelve a intentar
- Reduce la cantidad de mensajes

### Servicio se desconecta
- El servicio intentará reconectarse automáticamente
- Si no funciona, reinicia manualmente

## 📊 Logs y Monitoreo

```bash
# Ver logs en tiempo real
pm2 logs whatsapp-service

# Ver estado
pm2 status

# Métricas
pm2 monit
```

## 🔄 Actualizar a un número virtual

Cuando quieras cambiar a un número virtual:

1. Compra un número virtual (Twilio, etc)
2. Instala WhatsApp con ese número
3. Elimina `whatsapp-session/`
4. Reinicia el servicio
5. Escanea con el nuevo número

## 📞 Soporte

- **Documentación oficial:** https://wwebjs.dev/
- **GitHub:** https://github.com/pedroslopez/whatsapp-web.js
- **Issues del proyecto:** Contacta al administrador

## 📝 Notas

- El servicio se ejecuta en **puerto 3000** (configurable en server.js)
- La sesión persiste entre reinicios
- Los mensajes se envían inmediatamente
- No hay límite de caracteres (pero WhatsApp tiene límites)

---

**Creado con ❤️ para IEEE Student Branch UTADEO**
