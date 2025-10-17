# 🚀 Guía Rápida: WhatsApp en 5 Minutos

## ¿Qué tengo que hacer?

### 1️⃣ Instalar Node.js (si no lo tienes)

**Descargar:** https://nodejs.org/
- Elige la versión **LTS** (recomendada)
- Instala con las opciones por defecto
- Reinicia tu terminal/PowerShell

**Verificar:**
```bash
node --version
# Debe mostrar: v18.x.x o superior
```

### 2️⃣ Instalar dependencias del servicio

```bash
cd whatsapp-service
npm install
```

Esto descargará las bibliotecas necesarias (toma 1-2 minutos).

### 3️⃣ Iniciar el servicio

```bash
npm start
```

Verás algo como esto:
```
[OK] Servidor WhatsApp API corriendo en http://localhost:3000
[INFO] Inicializando cliente de WhatsApp...
[QR] Escanea este código QR con tu WhatsApp:

   ████ ▄▄▄▄▄ █▀█ █▄▄▀▄█
   █  █ █   █ ▄▄█▀ ▀█  ▄█
   █▄▄█ █▄▄▄█ ▄█▄▀▄ ▀ ▄ █
   ... (código QR)
```

### 4️⃣ Escanear QR con tu celular

**⚠️ IMPORTANTE:** Te recomiendo usar **WhatsApp Business** (no tu WhatsApp personal)

**Con WhatsApp Business:**
1. Descarga **WhatsApp Business** desde tu tienda de apps
2. Configúralo con tu número (puede ser el mismo que usas personalmente)
3. Abre WhatsApp Business
4. Ve a **Configuración** → **Dispositivos Vinculados**
5. Toca **"Vincular un dispositivo"**
6. Escanea el QR que apareció en tu terminal

**Con WhatsApp Personal** (alternativa):
1. Abre tu WhatsApp normal
2. Ve a **Configuración** → **Dispositivos Vinculados**
3. Toca **"Vincular un dispositivo"**
4. Escanea el QR

Una vez escaneado, verás:
```
[OK] Cliente de WhatsApp está listo!
```

### 5️⃣ Probar que funciona

Abre **otra terminal/PowerShell** (deja la anterior corriendo) y ejecuta:

```bash
# Desde el directorio principal del proyecto
uv run python test_whatsapp.py
```

Verás un menú:
```
===============================================================
TEST DE SERVICIO DE WHATSAPP
===============================================================

[1] Verificando estado del servicio...
   Estado: WhatsApp está conectado y listo
   Listo: ✓ Sí

   ✓ WhatsApp está listo para enviar mensajes

===============================================================
MENÚ DE PRUEBAS
===============================================================
1. Enviar mensaje de prueba
2. Enviar mensaje de cumpleaños
3. Verificar estado
4. Salir

Selecciona una opción:
```

**Prueba enviándote un mensaje:**
1. Selecciona opción `1`
2. Ingresa tu número: `+573054497235` (o tu número personal)
3. Escribe un mensaje: `Hola, esto es una prueba!`
4. ¡Deberías recibir el mensaje en tu WhatsApp! 📱

## ✅ ¡Listo! ¿Y ahora qué?

### Enviar cumpleaños automáticamente

El sistema ya está integrado. Cuando ejecutes:
```bash
uv run python birthday_checker.py
```

El script automáticamente:
- ✅ Enviará email (como siempre)
- ✅ **Enviará WhatsApp** (si el servicio está corriendo)

### Mantener el servicio corriendo siempre

Para que funcione 24/7, necesitas mantener el servicio Node.js corriendo:

**Opción fácil: screen (en servidor Linux)**
```bash
screen -S whatsapp
cd whatsapp-service
npm start
# Presiona Ctrl+A, luego D para desconectar
# screen -r whatsapp  # Para reconectar
```

**Opción profesional: PM2**
```bash
npm install -g pm2
cd whatsapp-service
pm2 start server.js --name whatsapp-service
pm2 save
```

### Cambiar de número más tarde

Si quieres usar otro número después:
```bash
# 1. Detener el servicio (Ctrl+C)
# 2. Borrar la sesión
rm -rf whatsapp-service/whatsapp-session

# 3. Iniciar de nuevo
cd whatsapp-service
npm start

# 4. Escanear con el nuevo número
```

## ❓ Problemas comunes

### "npm: command not found"
→ Node.js no está instalado. Descárgalo de https://nodejs.org/

### "WhatsApp no está listo"
→ Asegúrate de que el servicio Node.js esté corriendo en la otra terminal

### "Este número no está registrado en WhatsApp"
→ Verifica el formato del número: `+573054497235` (con + y código de país)

### "Error: EADDRINUSE"
→ El puerto 3000 ya está en uso. Mata el proceso:
```bash
# Windows PowerShell
netstat -ano | findstr :3000
taskkill /PID <número> /F

# Linux/Mac
lsof -ti:3000 | xargs kill
```

## 🔒 Seguridad

- ✅ **100% seguro** usar con WhatsApp Business
- ⚠️ **Cuidado** con WhatsApp personal (puede haber restricciones)
- 📊 **Límite recomendado:** Máximo 50-100 mensajes por día
- ⏱️ **Delay:** Ya incluido (2 segundos entre mensajes)

## 💰 Costo

**$0.00** - Completamente GRATIS
- Sin costo por mensaje
- Sin suscripción mensual
- Sin límite de mensajes (con moderación)

## 📞 ¿Necesitas ayuda?

Lee la documentación completa:
```bash
cat whatsapp-service/README.md
```

---

**¡Listo para enviar WhatsApp! 🎉**

**Commit:** 75b5289
