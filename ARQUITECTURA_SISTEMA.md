# 🏗️ Arquitectura del Sistema - IEEE Tadeo Control System

## 📊 Diagrama de Componentes

```
┌─────────────────────────────────────────────────────────────────┐
│                     IEEE Tadeo Control System                    │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                         start.bat                                │
│             Script de Inicialización Principal                   │
└───────┬──────────────────┬──────────────────┬───────────────────┘
        │                  │                  │
        │                  │                  │
        ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────────┐
│   WhatsApp   │  │    Túnel     │  │     FastAPI      │
│   Service    │  │   Público    │  │   Application    │
│  Puerto 3000 │  │              │  │   Puerto 8000    │
└──────┬───────┘  └──────┬───────┘  └────────┬─────────┘
       │                 │                   │
       │                 │                   │
       ▼                 ▼                   ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────────┐
│ whatsapp-web │  │ localtunnel  │  │   Endpoints:     │
│     .js      │  │   o ngrok    │  │   /admin         │
│              │  │              │  │   /portal        │
│ QR Auth      │  │ URL Pública  │  │   /api/*         │
│ Send Message │  │              │  │   /docs          │
└──────────────┘  └──────────────┘  └──────────────────┘
```

---

## 🔄 Flujo de Inicio

```
Usuario ejecuta start.bat
         │
         ├─→ [Paso 1/6] Verificación de Dependencias
         │       ├─→ Python 3.13+ ✓
         │       ├─→ Node.js ✓
         │       └─→ uv ✓
         │
         ├─→ [Paso 2/6] Creación de Directorios
         │       ├─→ qr_codes/
         │       ├─→ static/message_images/
         │       ├─→ static/whatsapp_images/
         │       └─→ logs/
         │
         ├─→ [Paso 3/6] Sincronización de Dependencias
         │       └─→ uv sync --quiet
         │
         ├─→ [Paso 4/6] Inicio de WhatsApp Service
         │       ├─→ Abrir ventana separada
         │       ├─→ npm install (si es necesario)
         │       ├─→ node server.js
         │       └─→ Generar QR (primera vez)
         │
         ├─→ [Paso 5/6] Inicio de Túnel
         │       ├─→ Usuario elige opción
         │       ├─→ [1] localtunnel --port 8000
         │       ├─→ [2] ngrok http 8000
         │       └─→ [3] Omitir (solo local)
         │
         └─→ [Paso 6/6] Inicio de FastAPI
                 └─→ uvicorn main:app --reload
```

---

## 🌐 Arquitectura de Red

```
                         INTERNET
                            │
                ┌───────────┴───────────┐
                │                       │
          ┌─────▼─────┐         ┌──────▼──────┐
          │  Túnel    │         │   Usuario   │
          │  Público  │         │   Externo   │
          └─────┬─────┘         └──────┬──────┘
                │                      │
                └──────────┬───────────┘
                           │
                    ┌──────▼──────┐
                    │  localhost  │
                    │ Puerto 8000 │
                    └──────┬──────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
    ┌────▼────┐      ┌─────▼─────┐    ┌─────▼─────┐
    │ FastAPI │      │ WhatsApp  │    │  SQLite   │
    │  main.py│◄─────┤  Service  │    │tickets.db │
    └────┬────┘      └───────────┘    └───────────┘
         │
    ┌────▼────────────────────────────┐
    │         Módulos Python          │
    ├─────────────────────────────────┤
    │ • models.py  (Base de datos)    │
    │ • schemas.py (Validaciones)     │
    │ • auth.py    (Autenticación)    │
    │ • email_service.py (Emails)     │
    │ • ticket_service.py (Tickets)   │
    │ • whatsapp_client.py (WA API)   │
    └─────────────────────────────────┘
```

---

## 🔌 API Endpoints

### Públicos
```
GET  /                    → Redirect a /login
GET  /login               → Login administrativo
GET  /portal              → Portal de usuarios
GET  /portal/login        → Login de usuarios
```

### Admin (Requiere autenticación)
```
GET  /admin               → Panel de control
GET  /admin/tickets       → Gestión de tickets
GET  /admin/events        → Gestión de eventos
GET  /admin/users         → Gestión de usuarios
GET  /admin/messages      → Mensajería masiva
```

### API REST
```
POST /api/tickets         → Crear ticket
GET  /api/tickets/{id}    → Obtener ticket
POST /api/validate        → Validar entrada
GET  /api/stats           → Estadísticas
```

### WhatsApp API (Puerto 3000)
```
GET  /status              → Estado de conexión
POST /send                → Enviar mensaje
POST /send-media          → Enviar con imagen
POST /send-bulk           → Envío masivo
POST /restart             → Reiniciar servicio
```

---

## 💾 Base de Datos (SQLite)

```
tickets.db
├─→ users               (Usuarios del sistema)
├─→ events              (Eventos)
├─→ tickets             (Tickets generados)
├─→ validations         (Validaciones de ingreso)
├─→ universities        (Universidades)
├─→ messages            (Historial de mensajes)
└─→ access_logs         (Logs de acceso)
```

---

## 📁 Estructura de Archivos

```
IEEE Tadeo Control System/
│
├─ 🚀 Scripts de Inicio
│  ├─ start.bat                  ← PRINCIPAL
│  ├─ start-simple.bat
│  ├─ start-whatsapp.bat
│  └─ start_production.sh
│
├─ 📖 Documentación
│  ├─ README_QUICK.md            ← Inicio rápido
│  ├─ INICIO_RAPIDO.md           ← Guía detallada
│  ├─ START_HERE.md              ← Guía completa
│  ├─ COMO_INICIAR_WHATSAPP.md
│  └─ ARQUITECTURA_SISTEMA.md    ← Este archivo
│
├─ 🐍 Backend Python (FastAPI)
│  ├─ main.py                    ← App principal
│  ├─ models.py                  ← Modelos DB
│  ├─ schemas.py                 ← Validaciones
│  ├─ auth.py                    ← JWT Auth
│  ├─ database.py                ← Config DB
│  ├─ ticket_service.py          ← Lógica tickets
│  ├─ email_service.py           ← Emails
│  ├─ whatsapp_client.py         ← Cliente WA
│  ├─ user_portal_routes.py      ← Portal usuarios
│  └─ birthday_checker.py        ← Cumpleaños
│
├─ 💬 Servicio WhatsApp (Node.js)
│  └─ whatsapp-service/
│     ├─ server.js               ← API WhatsApp
│     ├─ package.json
│     └─ whatsapp-session/       ← Sesión guardada
│
├─ 🎨 Frontend
│  ├─ templates/                 ← HTML Jinja2
│  │  ├─ base.html
│  │  ├─ dashboard.html
│  │  ├─ tickets.html
│  │  ├─ portal_dashboard.html
│  │  └─ ...
│  └─ static/                    ← CSS, JS, imágenes
│     ├─ favicon.svg
│     ├─ message_images/
│     └─ whatsapp_images/
│
├─ 💾 Base de Datos
│  └─ tickets.db                 ← SQLite
│
├─ 📦 Configuración
│  ├─ pyproject.toml             ← Config Python
│  ├─ .env                       ← Variables entorno
│  └─ .env.example
│
└─ 📄 Datos Generados
   ├─ qr_codes/                  ← QR tickets
   └─ logs/                      ← Logs sistema
```

---

## 🔐 Flujo de Autenticación

```
1. Usuario visita /login
         │
         ▼
2. Ingresa credenciales
         │
         ▼
3. auth.py valida contra DB
         │
    ┌────┴────┐
    │         │
    ▼         ▼
  Valid?    Invalid
    │         │
    │         └─→ Error 401
    │
    ▼
4. Genera JWT Token
         │
         ▼
5. Token en cookie HttpOnly
         │
         ▼
6. Redirect a /admin o /portal
         │
         ▼
7. Cada request verifica token
         │
    ┌────┴────┐
    │         │
    ▼         ▼
  Valid?   Expired?
    │         │
    │         └─→ Redirect /login
    │
    ▼
8. Acceso concedido
```

---

## 📧 Flujo de Mensajería

```
1. Admin selecciona usuarios
         │
         ▼
2. Escribe mensaje + imagen (opcional)
         │
         ▼
3. Selecciona canal (Email/WhatsApp)
         │
    ┌────┴────┐
    │         │
    ▼         ▼
  Email     WhatsApp
    │         │
    │         ▼
    │    4. whatsapp_client.py
    │         │
    │         ▼
    │    5. POST a localhost:3000/send-media
    │         │
    │         ▼
    │    6. whatsapp-web.js procesa
    │         │
    │         ▼
    │    7. Envía via WhatsApp Web
    │
    ▼
4. email_service.py
         │
         ▼
5. API Resend
         │
         ▼
6. Email enviado
```

---

## 🔄 Ciclo de Vida de un Ticket

```
1. Usuario registra en portal
         │
         ▼
2. FastAPI crea registro en DB
         │
         ▼
3. ticket_service.py genera QR
         │
         ▼
4. Guarda QR en qr_codes/
         │
         ▼
5. Envía email con QR
         │
         ▼
6. Usuario presenta QR en evento
         │
         ▼
7. Validador escanea QR
         │
         ▼
8. Sistema valida en DB
         │
    ┌────┴────┐
    │         │
    ▼         ▼
  Valid?   Invalid
    │         │
    │         └─→ Acceso denegado
    │
    ▼
9. Marca como validado
         │
         ▼
10. Guarda log de acceso
         │
         ▼
11. Acceso permitido ✓
```

---

## 🚀 Modos de Despliegue

### Desarrollo Local
```bash
start-simple.bat
# Solo FastAPI en localhost
```

### Desarrollo con WhatsApp
```bash
start-whatsapp.bat  # Ventana 1
start-simple.bat    # Ventana 2
```

### Testing con Túnel
```bash
start.bat
# Elige opción 1 (localtunnel)
```

### Demo/Producción
```bash
start.bat
# Elige opción 2 (ngrok)
```

### Producción en Servidor
```bash
./start_production.sh
# 4 workers uvicorn
```

---

## 📊 Tecnologías Utilizadas

| Componente | Tecnología | Version |
|------------|-----------|---------|
| Backend | FastAPI | 0.115+ |
| Base de Datos | SQLite | 3.x |
| Auth | JWT (python-jose) | 3.3+ |
| Frontend | Jinja2 + TailwindCSS | - |
| WhatsApp | whatsapp-web.js | 1.25+ |
| Email | Resend API | 2.16+ |
| QR Codes | qrcode + Pillow | 8.0+ |
| Túnel | localtunnel / ngrok | - |

---

## 🔒 Seguridad

1. **Autenticación JWT** con tokens HttpOnly
2. **Hashing de contraseñas** con bcrypt
3. **Validación de inputs** con Pydantic
4. **CORS configurado** para dominio específico
5. **Rate limiting** en endpoints críticos
6. **Sesiones de WhatsApp** encriptadas localmente

---

## 📈 Escalabilidad

### Actual (Desarrollo)
- SQLite (monousuario)
- 1 worker uvicorn
- WhatsApp Web (1 conexión)

### Futura (Producción)
- PostgreSQL (multiusuario)
- 4+ workers uvicorn
- WhatsApp Business API
- Redis para caché
- Load balancer

---

**IEEE Tadeo Student Branch** 🏗️

Última actualización: 2025
