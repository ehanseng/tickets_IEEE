# Guía de Inicio Rápido - IEEE Tadeo Control System

## Scripts Disponibles

### 🚀 `start.bat` - Inicio Completo (RECOMENDADO)
Inicia todos los servicios necesarios para el proyecto de forma interactiva:
- ✅ Servicio de WhatsApp (puerto 3000)
- ✅ Túnel público con localtunnel o ngrok (para acceso externo)
- ✅ Aplicación FastAPI (puerto 8000)

**Características:**
- 🔍 Verifica automáticamente todas las dependencias
- 📦 Instala dependencias de Node.js si es necesario
- 🪟 Abre ventanas separadas para cada servicio
- 🎯 Te permite elegir el tipo de túnel (localtunnel, ngrok, o ninguno)
- 🛑 Cierra todos los servicios automáticamente al presionar Ctrl+C

**Uso:**
```bash
start.bat
```

**Guía detallada:** Ver [INICIO_RAPIDO.md](INICIO_RAPIDO.md)

**Requisitos:**
- Python 3.13+
- Node.js
- uv (`pip install uv`)
- npx (incluido con Node.js)
- ngrok (opcional, para túnel estable)

---

### ⚡ `start-simple.bat` - Inicio Rápido
Inicia solo la aplicación FastAPI, ideal para desarrollo local sin WhatsApp.

**Uso:**
```bash
start-simple.bat
```

**Requisitos:**
- Python 3.13+
- uv (`pip install uv`)

---

### 💬 `start-whatsapp.bat` - Solo WhatsApp
Inicia únicamente el servicio de WhatsApp.

**Uso:**
```bash
start-whatsapp.bat
```

**Requisitos:**
- Node.js

---

## Servicios y Puertos

| Servicio | Puerto | URL |
|----------|--------|-----|
| FastAPI | 8000 | http://localhost:8000 |
| WhatsApp Service | 3000 | http://localhost:3000 |
| Admin Panel | 8000 | http://localhost:8000/admin |
| Login | 8000 | http://localhost:8000/login |

---

## Primera Vez

### 1. Instalar Dependencias

```bash
# Instalar uv (si no lo tienes)
pip install uv

# Instalar Node.js (para WhatsApp)
# Descarga desde: https://nodejs.org/

# Sincronizar dependencias del proyecto
uv sync
```

### 2. Configurar Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
# Base URL para tickets
BASE_URL=http://localhost:8000

# Email (Resend)
RESEND_API_KEY=tu_clave_resend

# Seguridad JWT
SECRET_KEY=tu_clave_secreta_jwt
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 3. Iniciar Servicios

**Opción A: Todo (recomendado para producción)**
```bash
start.bat
```

**Opción B: Solo FastAPI (desarrollo rápido)**
```bash
start-simple.bat
```

---

## Servicio de WhatsApp

### 📱 Opción 1: Usar el script (RECOMENDADO)
```bash
start-whatsapp.bat
```

Este script:
- ✅ Verifica que Node.js esté instalado
- ✅ Instala dependencias automáticamente si es necesario
- ✅ Crea directorios necesarios
- ✅ Muestra el código QR para vincular WhatsApp
- ✅ Te da instrucciones paso a paso

### Opción 2: Manual
```bash
cd whatsapp-service
npm install          # Solo la primera vez
node server.js
```

---

### 📲 Cómo vincular WhatsApp (IMPORTANTE)

1. **Ejecuta el servicio** con `start-whatsapp.bat`
2. **Espera el QR Code** - Aparecerá en la consola (cuadrado hecho de puntos)
3. **En tu teléfono:**
   - Abre **WhatsApp**
   - Ve a: **Configuración > Dispositivos vinculados**
   - Toca **"Vincular un dispositivo"**
   - Escanea el código QR de la consola
4. **¡Listo!** Verás el mensaje: `[OK] Cliente de WhatsApp está listo!`

### ✅ Verificar que funciona

Abre en tu navegador: http://localhost:3000/status

Deberías ver algo como:
```json
{
  "ready": true,
  "qr": null,
  "message": "WhatsApp está conectado y listo"
}
```

### 🔌 Endpoints disponibles

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/status` | GET | Estado de conexión |
| `/send` | POST | Enviar mensaje individual |
| `/send-media` | POST | Enviar mensaje con imagen |
| `/send-bulk` | POST | Enviar mensajes masivos |
| `/restart` | POST | Reiniciar servicio |

---

## Túnel Público

Para exponer tu aplicación local a internet (necesario para webhooks):

**Con localtunnel (incluido en start.bat):**
```bash
npx localtunnel --port 8000
```

**Con ngrok (alternativa):**
```bash
ngrok http 8000
```

---

## Comandos Útiles

```bash
# Sincronizar dependencias
uv sync

# Instalar nueva dependencia
uv add nombre-paquete

# Ejecutar app en modo desarrollo
uv run uvicorn main:app --reload

# Ejecutar migraciones
uv run python migrate_*.py

# Ver estado de Git
git status

# Crear commit
git add .
git commit -m "mensaje"
git push
```

---

## Estructura del Proyecto

```
Ticket/
├── start.bat              # Script principal de inicio
├── start-simple.bat       # Script simplificado
├── main.py               # Aplicación FastAPI
├── whatsapp_client.py    # Cliente de WhatsApp
├── email_service.py      # Servicio de email
├── models.py             # Modelos de base de datos
├── schemas.py            # Schemas Pydantic
├── database.py           # Configuración DB
├── auth.py               # Autenticación JWT
├── tickets.db            # Base de datos SQLite
├── templates/            # Templates HTML
├── static/               # Archivos estáticos
├── qr_codes/            # Códigos QR generados
└── whatsapp-service/    # Servicio Node.js de WhatsApp
```

---

## Solución de Problemas

### Error: "Python no encontrado"
```bash
# Verifica la instalación
python --version

# Debe ser 3.13+
```

### Error: "uv no encontrado"
```bash
pip install uv
```

### Error: "Node.js no encontrado"
Descarga e instala desde: https://nodejs.org/

### El servicio de WhatsApp no inicia
```bash
cd whatsapp-service
npm install
node server.js
```

### No se puede conectar a WhatsApp
1. Escanea el código QR que aparece en la consola
2. Espera a que se sincronice
3. Verifica el estado en: http://localhost:3000/status

---

## Credenciales por Defecto

**Admin:**
- Usuario: `admin`
- Contraseña: `admin123`

⚠️ **IMPORTANTE:** Cambia estas credenciales en producción.

---

## Soporte

Para reportar problemas o solicitar ayuda:
- Repositorio: [GitHub](https://github.com/tu-usuario/ticket)
- IEEE Tadeo: ieee@utadeo.edu.co

---

**Desarrollado con ❤️ por IEEE Tadeo Student Branch**
