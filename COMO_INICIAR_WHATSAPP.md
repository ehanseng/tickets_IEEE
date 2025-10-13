# 📱 Cómo Iniciar WhatsApp - IEEE Tadeo Control System

## Paso 1: Ejecutar el Script

Abre una terminal (CMD o PowerShell) en la carpeta del proyecto y ejecuta:

```bash
start-whatsapp.bat
```

O simplemente **haz doble clic** en el archivo `start-whatsapp.bat`

---

## Paso 2: Esperar el Código QR

Verás algo como esto en la consola:

```
========================================
  Servicio de WhatsApp - IEEE Tadeo
========================================

[INFO] Inicializando cliente de WhatsApp...
[QR] Escanea este código QR con tu WhatsApp:

▄▄▄▄▄▄▄ ▄   ▄▄ ▄▄▄▄▄▄▄
█ ███ █ ██▀█▀█ █ ███ █
█ ▀▀▀ █ ▀▄ ▄█  █ ▀▀▀ █
▀▀▀▀▀▀▀ █ ▀ ▀ █ ▀▀▀▀▀▀▀
   (código QR continúa...)
```

---

## Paso 3: Escanear con tu Teléfono

### En tu teléfono:

1. **Abre WhatsApp**

2. **Ve al menú:**
   - **Android:** Toca los 3 puntos (⋮) arriba a la derecha → "Dispositivos vinculados"
   - **iPhone:** Ve a "Configuración" → "Dispositivos vinculados"

3. **Toca "Vincular un dispositivo"**

4. **Escanea el QR** que aparece en la consola de tu computadora

---

## Paso 4: Confirmar Conexión

Una vez escaneado, verás en la consola:

```
[OK] Autenticación exitosa
[OK] Cliente de WhatsApp está listo!
```

---

## ✅ Verificar que Funciona

Abre tu navegador y ve a:

```
http://localhost:3000/status
```

Si ves esto, ¡está funcionando! ✨

```json
{
  "ready": true,
  "qr": null,
  "message": "WhatsApp está conectado y listo"
}
```

---

## 🔧 Solución de Problemas

### El QR Code no aparece
- Espera unos 10-15 segundos
- Si no aparece, cierra y vuelve a ejecutar `start-whatsapp.bat`

### Error: "Node.js no encontrado"
Instala Node.js desde: https://nodejs.org/

### El QR Code expiró
- Cierra el servicio (Ctrl+C)
- Vuelve a ejecutar `start-whatsapp.bat`
- Aparecerá un nuevo código QR

### "WhatsApp no está conectado"
1. Asegúrate de haber escaneado el QR code
2. Verifica el estado en: http://localhost:3000/status
3. Si `ready` es `false`, vuelve a escanear el QR

### Se desconecta constantemente
- Verifica tu conexión a internet
- Mantén WhatsApp Web activo en tu teléfono
- No cierres WhatsApp en tu teléfono

---

## 🎯 Uso Rápido

Una vez conectado, puedes probar enviando un mensaje desde tu código Python:

```python
from whatsapp_client import WhatsAppClient

# Crear cliente
wa = WhatsAppClient()

# Verificar estado
if wa.is_ready():
    # Enviar mensaje
    result = wa.send_message(
        phone="+573001234567",
        message="¡Hola! Mensaje de prueba desde IEEE Tadeo Control System"
    )
    print(result)
```

---

## 📚 Documentación Completa

Para más información, consulta: [START_HERE.md](START_HERE.md)

---

**IEEE Tadeo Student Branch** 🤖
