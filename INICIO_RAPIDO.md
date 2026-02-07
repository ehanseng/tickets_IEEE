# 🚀 Inicio Rápido - IEEE Tadeo Control System

## Ejecutar Todo el Sistema

### Opción 1: Inicio Completo (Recomendado)

Ejecuta este comando o haz **doble clic** en el archivo:

```bash
start.bat
```

Este script iniciará **automáticamente**:

1. ✅ **Servicio de WhatsApp** (puerto 3000)
2. ✅ **Túnel público** (localtunnel o ngrok)
3. ✅ **Aplicación FastAPI** (puerto 8000)

---

## 📋 Proceso Paso a Paso

Cuando ejecutes `start.bat`, verás algo como esto:

```
========================================
  IEEE Tadeo Control System
  Inicializacion Completa
========================================

Este script iniciara:
  [1] Servicio de WhatsApp (puerto 3000)
  [2] Tunel publico (localtunnel o ngrok)
  [3] Aplicacion FastAPI (puerto 8000)

========================================

[1/6] Creando directorios necesarios...
      [OK] Directorios creados correctamente.

[2/6] Sincronizando dependencias Python...
      [OK] Dependencias sincronizadas correctamente.

[3/6] Iniciando servicio de WhatsApp (puerto 3000)...
      [OK] Servicio de WhatsApp iniciado en segundo plano.
      [INFO] Ventana separada abierta - Escanea el QR si es la primera vez

[4/6] Iniciando tunel publico (puerto 8000)...

      Opciones de tunel:
      [1] localtunnel (gratuito, rapido)
      [2] ngrok (requiere cuenta, mas estable)
      [3] Omitir tunel (solo local)

      Elige una opcion (1/2/3): _
```

---

## 🌐 Opciones de Túnel

### 1️⃣ Localtunnel (Recomendado para desarrollo)
- **Ventajas:** Gratuito, no requiere cuenta, instalación rápida
- **Desventajas:** URL aleatoria que cambia cada vez
- **Comando manual:** `npx localtunnel --port 8000`

### 2️⃣ Ngrok (Recomendado para producción/demos)
- **Ventajas:** URLs más estables, mejor rendimiento
- **Desventajas:** Requiere cuenta gratuita
- **Instalación:** https://ngrok.com/download
- **Comando manual:** `ngrok http 8000`

### 3️⃣ Omitir túnel
- Solo accesible desde `localhost`
- Ideal para desarrollo sin necesidad de acceso externo

---

## 📱 Primera Vez con WhatsApp

Si es la **primera vez** que ejecutas el servicio de WhatsApp:

1. Se abrirá una **ventana separada** con el título "WhatsApp Service - IEEE Tadeo"
2. Espera a que aparezca el **código QR** (cuadrado de puntos)
3. **En tu teléfono:**
   - Abre WhatsApp
   - Ve a: **Configuración → Dispositivos vinculados**
   - Toca **"Vincular un dispositivo"**
   - Escanea el código QR de la ventana

4. Verás: `[OK] Cliente de WhatsApp está listo!`

**Nota:** La sesión se guarda. No necesitarás escanear el QR de nuevo.

---

## 🎯 URLs del Sistema

Una vez iniciado todo, tendrás acceso a:

| Servicio | URL | Descripción |
|----------|-----|-------------|
| Panel Admin | http://localhost:8070/admin | Panel de administración |
| Portal Usuario | http://localhost:8070/portal | Portal de usuarios |
| Login Admin | http://localhost:8070/login | Login administrativo |
| API Docs | http://localhost:8070/docs | Documentación Swagger |
| WhatsApp Status | http://localhost:3000/status | Estado de WhatsApp |
| Túnel Público | (Ver ventana del túnel) | URL pública temporal |

---

## 🔐 Credenciales por Defecto

**Administrador:**
- Usuario: `admin`
- Contraseña: `admin123`

⚠️ **IMPORTANTE:** Cambia estas credenciales en producción

---

## 🛑 Detener el Sistema

Para detener **todos** los servicios:

1. En la ventana principal donde corre FastAPI, presiona **Ctrl+C**
2. El script automáticamente cerrará:
   - ✅ Servicio de WhatsApp
   - ✅ Túnel público (localtunnel o ngrok)
   - ✅ Aplicación FastAPI

---

## 📂 Estructura de Ventanas

Al ejecutar `start.bat`, se abrirán **3 ventanas**:

```
┌─────────────────────────────────────┐
│ [1] Ventana Principal - FastAPI    │  ← Aquí verás los logs principales
│     - Logs de la aplicación         │
│     - Ctrl+C para detener todo      │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ [2] WhatsApp Service - IEEE Tadeo   │  ← QR Code y logs de WhatsApp
│     - Código QR (primera vez)       │
│     - Logs de mensajes enviados     │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ [3] Localtunnel/Ngrok - IEEE Tadeo  │  ← URL pública del túnel
│     - URL pública temporal          │
│     - Copia esta URL para acceso    │
└─────────────────────────────────────┘
```

---

## 🔧 Solución de Problemas

### Error: "Python no encontrado"
```bash
# Verifica que Python esté instalado
python --version
# Debe ser 3.13 o superior
```

### Error: "uv no encontrado"
```bash
pip install uv
```

### Error: "Node.js no encontrado"
Descarga desde: https://nodejs.org/

### WhatsApp no se conecta
1. Verifica que Node.js esté instalado: `node --version`
2. Ve a la ventana "WhatsApp Service - IEEE Tadeo"
3. Escanea el QR code si aparece
4. Verifica el estado en: http://localhost:3000/status

### El túnel no inicia
**Para localtunnel:**
```bash
# Instalar manualmente
npm install -g localtunnel
# Ejecutar
npx localtunnel --port 8000
```

**Para ngrok:**
1. Descarga desde: https://ngrok.com/download
2. Extrae el archivo
3. Añade al PATH o ejecuta desde su carpeta
```bash
ngrok http 8000
```

### Puerto 8000 ya en uso
```bash
# Ver qué proceso está usando el puerto
netstat -ano | findstr :8000

# Matar el proceso (reemplaza PID)
taskkill /PID <numero_proceso> /F
```

---

## 🎓 Scripts Alternativos

Si no necesitas todo, usa estos scripts más simples:

```bash
# Solo FastAPI (sin WhatsApp ni túnel)
start-simple.bat

# Solo WhatsApp
start-whatsapp.bat
```

---

## 📚 Documentación Adicional

- [START_HERE.md](START_HERE.md) - Guía completa del sistema
- [COMO_INICIAR_WHATSAPP.md](COMO_INICIAR_WHATSAPP.md) - Guía detallada de WhatsApp
- [README.md](README.md) - Documentación del proyecto

---

## 💡 Consejos

1. **Primera vez:** Usa opción [3] (omitir túnel) para configurar todo localmente primero
2. **Desarrollo:** Usa localtunnel [1] para pruebas rápidas
3. **Demos/Producción:** Usa ngrok [2] para URLs más estables
4. **Mantén las ventanas abiertas:** No cierres las ventanas de WhatsApp o túnel manualmente

---

## ✅ Checklist de Inicio

- [ ] Python 3.13+ instalado
- [ ] Node.js instalado
- [ ] uv instalado (`pip install uv`)
- [ ] Archivo `.env` configurado
- [ ] Ejecutar `start.bat`
- [ ] Escanear QR de WhatsApp (primera vez)
- [ ] Elegir opción de túnel
- [ ] Copiar URL pública (si usas túnel)
- [ ] Acceder a http://localhost:8070/admin
- [ ] Probar login con credenciales por defecto

---

**¡Listo para usar! 🎉**

**IEEE Tadeo Student Branch** - Control System v1.0
