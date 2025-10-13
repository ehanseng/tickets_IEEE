# ⚡ IEEE Tadeo Control System - Inicio en 3 Pasos

## 🎯 Inicio Super Rápido

```bash
# Paso 1: Ejecuta esto
start.bat

# Paso 2: Elige opción de túnel (1, 2 o 3)

# Paso 3: Abre http://localhost:8000/admin
```

**¡Eso es todo!** 🎉

---

## 📱 ¿Primera Vez con WhatsApp?

Cuando se abra la ventana de WhatsApp:

1. Espera el QR Code (15 segundos aprox)
2. Abre WhatsApp en tu teléfono
3. Ve a: **Configuración → Dispositivos vinculados**
4. Escanea el QR

**Solo lo haces UNA VEZ** - La sesión se guarda automáticamente.

---

## 🔗 URLs Importantes

| Servicio | URL |
|----------|-----|
| **Admin Panel** | http://localhost:8000/admin |
| **Portal Usuario** | http://localhost:8000/portal |
| **API Docs** | http://localhost:8000/docs |
| **WhatsApp Status** | http://localhost:3000/status |

**Credenciales:**
- Usuario: `admin`
- Password: `admin123`

---

## 🌐 Opciones de Túnel

```
[1] localtunnel  → Gratis, rápido, URL aleatoria
[2] ngrok        → Gratis*, estable, URL fija*
[3] Sin túnel    → Solo localhost (desarrollo)
```

---

## 🛑 Detener Todo

Presiona **Ctrl+C** en la ventana principal.

Se cerrarán automáticamente:
- ✅ WhatsApp
- ✅ Túnel
- ✅ FastAPI

---

## 📚 ¿Necesitas Más Info?

- **Guía detallada:** [INICIO_RAPIDO.md](INICIO_RAPIDO.md)
- **Guía completa:** [START_HERE.md](START_HERE.md)
- **Solo WhatsApp:** [COMO_INICIAR_WHATSAPP.md](COMO_INICIAR_WHATSAPP.md)

---

## ⚙️ Scripts Alternativos

```bash
start.bat          # Todo (WhatsApp + Túnel + FastAPI)
start-simple.bat   # Solo FastAPI
start-whatsapp.bat # Solo WhatsApp
```

---

## 🔧 Problemas Comunes

**Error: "Python no encontrado"**
```bash
# Instala Python 3.13+
# https://www.python.org/downloads/
```

**Error: "uv no encontrado"**
```bash
pip install uv
```

**Error: "Node.js no encontrado"**
```bash
# Instala Node.js
# https://nodejs.org/
```

**WhatsApp no conecta**
```bash
# Ve a la ventana de WhatsApp y escanea el QR
# O verifica: http://localhost:3000/status
```

**Puerto 8000 ocupado**
```bash
netstat -ano | findstr :8000
taskkill /PID <numero> /F
```

---

## ✅ Checklist Pre-inicio

- [ ] Python 3.13+ instalado
- [ ] Node.js instalado
- [ ] uv instalado (`pip install uv`)
- [ ] Archivo `.env` configurado (opcional)

---

## 🎓 Estructura del Proyecto

```
Ticket/
├── start.bat              ← EJECUTA ESTO
├── start-simple.bat
├── start-whatsapp.bat
├── INICIO_RAPIDO.md       ← Lee esto si tienes dudas
├── main.py                ← App principal
├── whatsapp-service/      ← Servicio de WhatsApp
│   └── server.js
├── templates/             ← HTML
├── static/                ← CSS, JS, imágenes
└── tickets.db             ← Base de datos
```

---

## 💡 Tips

1. **Primera vez:** Omite el túnel (opción 3) para configurar localmente
2. **Desarrollo:** Usa localtunnel (opción 1)
3. **Demo/Producción:** Usa ngrok (opción 2)
4. **No cierres las ventanas** de WhatsApp o túnel manualmente

---

## 🚨 Importante

- Cambia las credenciales por defecto en producción
- El túnel expone tu aplicación a internet
- La sesión de WhatsApp se guarda localmente
- Mantén actualizado el archivo `.env`

---

**IEEE Tadeo Student Branch** 🤖

Version 1.0 | Control System
