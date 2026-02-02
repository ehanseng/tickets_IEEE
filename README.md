# 🎫 IEEE Tadeo Control System

Sistema integral de gestión para IEEE Tadeo Student Branch que incluye control de eventos, mensajería masiva, gestión de usuarios y más.

## 🚀 Características Principales

### 🎟️ Sistema de Tickets y Eventos
- ✅ Generación automática de tickets con códigos QR encriptados
- ✅ Validación en tiempo real con escáner QR
- ✅ Control de acceso y registro de asistencia
- ✅ Gestión completa de eventos (crear, editar, activar/desactivar)
- ✅ Envío automático de tickets por email
- ✅ Portal de usuario para consultar tickets personales

### 📧 Sistema de Mensajería Masiva
- ✅ Envío de mensajes por **Email** y **WhatsApp**
- ✅ Soporte para imágenes adjuntas
- ✅ Mensajes personalizados con variables (nombre, apodo)
- ✅ Enlaces con texto personalizado
- ✅ Histórico completo de campañas enviadas
- ✅ Estadísticas de entrega en tiempo real
- ✅ Estados de WhatsApp: enviado, entregado, fallido
- ✅ Detalles de destinatarios por campaña
- ✅ Eliminar campañas antiguas

### 👥 Gestión de Usuarios
- ✅ Registro completo de usuarios con validación
- ✅ Campos personalizados: universidad, membresía IEEE, cumpleaños
- ✅ Portal de autogestión para usuarios
- ✅ Filtros y búsqueda avanzada
- ✅ Gestión de universidades afiliadas
- ✅ Control de membresía IEEE con ID

### 🎂 Sistema de Cumpleaños
- ✅ Envío automático de emails de felicitación
- ✅ Soporte para apodos personalizados
- ✅ Plantilla de email personalizada
- ✅ Registro de fecha de cumpleaños en perfil

### 🎓 Gestión de Universidades
- ✅ Registro de universidades asociadas
- ✅ Código abreviado para identificación rápida
- ✅ Asignación de universidad a usuarios
- ✅ Estadísticas por universidad en dashboard

### 🔐 Control de Acceso
- ✅ Sistema de autenticación para administradores
- ✅ Portal separado para usuarios regulares
- ✅ Gestión de múltiples administradores
- ✅ Tokens JWT para seguridad

### 📊 Dashboard y Reportes
- ✅ Estadísticas generales del sistema
- ✅ Gráficos de distribución por universidad
- ✅ Métricas de membresía IEEE
- ✅ Resumen de eventos y tickets

## 📋 Requisitos

- Python 3.13+
- uv (gestor de paquetes)
- Node.js 18+ (para servicio de WhatsApp)
- Cuenta de Resend.com (para envío de emails)
- WhatsApp Web (para mensajería)

## 🛠️ Instalación

### 1. Instalar dependencias de Python
```bash
uv sync
```

### 2. Configurar variables de entorno
Crea un archivo `.env` en la raíz del proyecto:

```env
# Email (Resend)
RESEND_API_KEY=tu_api_key_de_resend
FROM_EMAIL=info@tudominio.org
FROM_NAME=IEEE Tadeo - Control System

# Base de datos MySQL
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=ieeetadeo
MYSQL_PASSWORD=tu_password
MYSQL_DATABASE=ieeetadeo

# JWT para autenticación
SECRET_KEY=tu_clave_secreta_aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 3. Instalar servicio de WhatsApp
```bash
cd whatsapp-service
npm install
```

### 4. Ejecutar el sistema

**Terminal 1 - Servidor principal:**
```bash
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Servicio de WhatsApp:**
```bash
cd whatsapp-service
node server.js
```

El servidor estará disponible en `http://localhost:8070`

## 📚 Módulos del Sistema

### 🖥️ Panel de Administración

#### Dashboard Principal
**URL:** `http://localhost:8070/admin`

- Estadísticas generales (usuarios, eventos, tickets)
- Distribución de usuarios por universidad
- Métricas de membresía IEEE
- Accesos rápidos a todas las funcionalidades

#### Gestión de Usuarios
**URL:** `http://localhost:8070/admin/users`

**Funcionalidades:**
- Registrar nuevos usuarios con información completa
- Ver lista de todos los usuarios con filtros
- Editar información de usuarios
- Buscar por nombre, email o universidad
- Ver membresía IEEE y fecha de cumpleaños

**Campos de usuario:**
- Nombre completo
- Email
- Teléfono (código de país + número)
- Universidad afiliada
- ID de membresía IEEE (opcional)
- Fecha de cumpleaños (opcional)
- Identificación (opcional)
- Apodo (para emails personalizados)

#### Gestión de Eventos
**URL:** `http://localhost:8070/admin/events`

**Funcionalidades:**
- Crear nuevos eventos con descripción completa
- Editar eventos existentes
- Activar/desactivar eventos
- Ver cantidad de tickets por evento
- Configurar ubicación y fecha

**Campos de evento:**
- Nombre del evento
- Descripción detallada
- Ubicación
- Fecha y hora
- Estado (activo/inactivo)

#### Gestión de Tickets
**URL:** `http://localhost:8070/admin/tickets`

**Funcionalidades:**
- Generar tickets para usuarios y eventos
- Visualizar código QR del ticket
- Descargar QR como imagen
- Copiar código para validación manual
- Ver estado (usado/disponible)
- Filtrar por evento o usuario
- Envío automático por email al generar

#### Validación de Entrada
**URL:** `http://localhost:8070/admin/validate`

**Funcionalidades:**
- **Escáner QR con cámara:** Valida tickets en tiempo real
- **Validación manual:** Ingresa el código manualmente
- Historial de validaciones recientes
- Alertas visuales (verde = permitido, rojo = denegado)
- Información del usuario y evento al validar

#### Sistema de Mensajería Masiva
**URL:** `http://localhost:8070/admin/messages`

**Funcionalidades:**
- Enviar mensajes por Email y/o WhatsApp
- Adjuntar imágenes (PNG, JPG, JPEG)
- Seleccionar destinatarios específicos o todos
- Agregar enlaces con texto personalizado
- Personalizar mensajes con variables:
  - `{nombre}` - Nombre del usuario
  - `{apodo}` - Apodo del usuario (si está definido)
- Preview del mensaje antes de enviar
- Confirmación antes de enviar

**Ejemplo de mensaje personalizado:**
```
Hola {apodo}! 👋

Te invitamos al próximo evento de IEEE Tadeo...
```

#### Histórico de Campañas
**URL:** `http://localhost:8070/admin/campaigns`

**Funcionalidades:**
- Ver todas las campañas enviadas
- Estadísticas de envío (exitosos/fallidos)
- Filtrar por fecha o asunto
- Ver detalles completos de cada campaña
- Eliminar campañas antiguas

**Detalles de campaña incluyen:**
- Asunto y mensaje completo
- Imagen adjunta (si la hay)
- Lista de destinatarios
- Estado de entrega por usuario (Email y WhatsApp)
- Fecha de envío
- Creado por (administrador)

#### Gestión de Universidades
**URL:** `http://localhost:8070/admin/universities`

**Funcionalidades:**
- Crear nuevas universidades
- Editar información
- Código corto (ej: "UTadeo", "UNAL")
- Ver cantidad de usuarios por universidad

### 👤 Portal de Usuario

**URL:** `http://localhost:8070/portal`

**Funcionalidades:**
- Login seguro con email y contraseña
- Ver tickets personales
- Dashboard con información de perfil
- Editar información personal:
  - Cambiar contraseña
  - Actualizar teléfono
  - Agregar/editar universidad
  - Agregar ID de membresía IEEE
  - Configurar fecha de cumpleaños
- Ver estado de membresía IEEE
- Historial de eventos asistidos

## 🔧 Flujos de Trabajo

### Flujo 1: Organizar un Evento

1. **Crear el evento**
   - Ve a `/admin/events`
   - Clic en "Crear Nuevo Evento"
   - Completa información y guarda

2. **Generar tickets**
   - Ve a `/admin/tickets`
   - Selecciona usuarios y el evento
   - Genera tickets (se envían automáticamente por email)

3. **Día del evento - Validar entrada**
   - Ve a `/admin/validate`
   - Activa la cámara
   - Escanea QR de los asistentes
   - Sistema confirma acceso

### Flujo 2: Enviar Mensaje Masivo

1. **Ir a mensajería**
   - Ve a `/admin/messages`

2. **Configurar mensaje**
   - Escribe asunto y mensaje
   - Personaliza con variables {nombre} o {apodo}
   - Adjunta imagen si es necesario
   - Agrega enlace opcional

3. **Seleccionar destinatarios**
   - Selecciona usuarios específicos
   - O marca "Seleccionar todos"

4. **Elegir canales**
   - Marca Email y/o WhatsApp
   - Preview del mensaje

5. **Enviar**
   - Clic en "Enviar Mensaje"
   - Confirma el envío
   - Ve estadísticas en tiempo real

6. **Ver resultados**
   - Ve a `/admin/campaigns`
   - Clic en la campaña
   - Revisa estado de cada destinatario

### Flujo 3: Gestionar Usuario

1. **Registro inicial**
   - Admin crea usuario en `/admin/users`
   - Usuario recibe credenciales

2. **Usuario completa perfil**
   - Usuario accede a `/portal`
   - Actualiza información personal
   - Agrega membresía IEEE si aplica
   - Configura fecha de cumpleaños

3. **Cumpleaños**
   - Sistema envía email automático el día del cumpleaños
   - Email personalizado con nombre/apodo

## 📡 API REST

### Documentación Interactiva
- **Swagger UI:** `http://localhost:8070/docs`
- **ReDoc:** `http://localhost:8070/redoc`

### Endpoints Principales

#### Autenticación
- `POST /auth/login` - Login de administrador
- `POST /auth/portal/login` - Login de usuario
- `POST /auth/register-admin` - Registrar administrador

#### Usuarios
- `GET /users/` - Listar usuarios
- `POST /users/` - Crear usuario
- `GET /users/{id}` - Obtener usuario
- `PUT /users/{id}` - Actualizar usuario
- `GET /users/{id}/tickets` - Tickets del usuario

#### Eventos
- `GET /events/` - Listar eventos
- `POST /events/` - Crear evento
- `PUT /events/{id}` - Actualizar evento
- `PATCH /events/{id}/toggle-active` - Activar/desactivar

#### Tickets
- `GET /tickets/` - Listar tickets
- `POST /tickets/` - Generar ticket
- `GET /tickets/{id}/qr` - Obtener QR
- `POST /validate/` - Validar ticket

#### Mensajería
- `POST /messages/bulk-send` - Enviar mensaje masivo
- `GET /campaigns/` - Listar campañas
- `GET /campaigns/{id}` - Detalles de campaña
- `DELETE /campaigns/{id}` - Eliminar campaña

#### Universidades
- `GET /universities/` - Listar universidades
- `POST /universities/` - Crear universidad
- `PUT /universities/{id}` - Actualizar universidad

#### WhatsApp
- `GET /whatsapp/status` - Estado del servicio
- `POST /whatsapp/restart` - Reiniciar cliente
- `POST /webhooks/whatsapp-status` - Webhook de estados

## 🏗️ Estructura del Proyecto

```
Ticket/
├── main.py                      # API principal y rutas admin
├── models.py                    # Modelos de base de datos
├── schemas.py                   # Esquemas Pydantic
├── database.py                  # Configuración SQLAlchemy
├── ticket_service.py            # Generación de QR
├── email_service.py             # Servicio de emails (Resend)
├── whatsapp_client.py           # Cliente de WhatsApp
├── user_portal_routes.py        # Rutas del portal de usuario
├── birthday_service.py          # Servicio de cumpleaños
├── templates/                   # Plantillas HTML
│   ├── base.html               # Base con Tailwind CSS
│   ├── admin_login.html        # Login de administrador
│   ├── dashboard.html          # Dashboard principal
│   ├── users.html              # Gestión de usuarios
│   ├── events.html             # Gestión de eventos
│   ├── tickets.html            # Gestión de tickets
│   ├── validate.html           # Validación con QR
│   ├── messages.html           # Mensajería masiva
│   ├── campaigns.html          # Histórico de campañas
│   ├── campaign_details.html   # Detalles de campaña
│   ├── universities.html       # Gestión de universidades
│   ├── portal_login.html       # Login de usuarios
│   └── portal_dashboard.html   # Portal de usuario
├── whatsapp-service/           # Servicio Node.js
│   ├── server.js               # API de WhatsApp
│   ├── package.json            # Dependencias Node
│   └── .wwebjs_auth/           # Sesión de WhatsApp
├── static/                      # Archivos estáticos
│   ├── favicon.svg             # Ícono del sitio
│   └── message_images/         # Imágenes de campañas
├── qr_codes/                    # QR generados
├── .env                         # Variables de entorno
├── pyproject.toml              # Dependencias Python
└── README.md                   # Esta documentación
```

## 🔒 Seguridad

### Autenticación
- Tokens JWT para sesiones de administrador
- Contraseñas hasheadas con bcrypt
- Tokens con expiración configurable
- Separación de roles (admin vs usuario)

### Tickets
- Códigos únicos generados con SHA-256
- QR con 64 caracteres imposibles de adivinar
- Validación de un solo uso
- Registro de fecha/hora de validación

### Datos
- Base de datos MySQL con integridad referencial
- Validación de datos con Pydantic
- Sanitización de inputs

## 🎨 Tecnologías Utilizadas

### Backend
- **FastAPI** - Framework web moderno y rápido
- **SQLAlchemy** - ORM para base de datos
- **Pydantic** - Validación de datos
- **MySQL** - Base de datos
- **JWT** - Autenticación
- **qrcode** - Generación de QR
- **Pillow** - Procesamiento de imágenes

### Email
- **Resend** - Servicio de envío de emails
- **HTML/CSS** - Plantillas responsive

### WhatsApp
- **Node.js** - Runtime para servicio
- **whatsapp-web.js** - Cliente de WhatsApp
- **Express** - API REST

### Frontend
- **Tailwind CSS** - Framework CSS
- **Jinja2** - Motor de plantillas
- **JavaScript vanilla** - Interactividad
- **html5-qrcode** - Escáner QR en navegador

## 💡 Consejos de Uso

### Para Eventos
1. Crea el evento con al menos 1 semana de anticipación
2. Genera y envía tickets 3-5 días antes del evento
3. Prueba el escáner QR el día antes
4. Ten un plan B (validación manual) por si falla internet

### Para Mensajería
1. Usa el campo "apodo" para mensajes más personales
2. Las imágenes se comprimen automáticamente para WhatsApp
3. Revisa el preview antes de enviar
4. Los estados de WhatsApp se actualizan en tiempo real

### Para WhatsApp
1. Mantén WhatsApp Web conectado en el servidor
2. No cierres sesión en WhatsApp Web manualmente
3. Si se desconecta, reinicia el servicio de Node.js
4. El primer mensaje demora más (conexión inicial)

### Para Usuarios
1. Asegúrate de que los usuarios tengan email válido
2. Configura el ID de membresía IEEE correctamente
3. Las fechas de cumpleaños activan emails automáticos
4. Los usuarios pueden actualizar su propia información

## 🐛 Solución de Problemas

### WhatsApp no envía mensajes
```bash
# Reiniciar servicio de WhatsApp
cd whatsapp-service
node server.js
# Escanear QR si es necesario
```

### Emails no se envían
- Verifica que `RESEND_API_KEY` esté configurado en `.env`
- Confirma que el dominio esté verificado en Resend
- Revisa los logs del servidor

### Error de encoding en Windows
- El sistema usa `->` en lugar de `→` para compatibilidad
- Si ves errores de charset, verifica la consola use UTF-8

### Cámara no funciona para QR
- Usa HTTPS o localhost (requerido por navegadores)
- Verifica permisos de cámara en el navegador
- Prueba con Chrome o Edge (mejor soporte)
- Alternativa: usa validación manual

### Base de datos corrupta
```bash
# Backup de la base de datos MySQL
mysqldump -u ieeetadeo -p ieeetadeo > backup.sql

# Si necesitas empezar de cero, recrea las tablas
python -c "from database import Base, engine; import models; Base.metadata.create_all(bind=engine)"
```

## 📈 Estadísticas y Métricas

El sistema rastrea:
- Total de usuarios registrados
- Eventos creados y activos
- Tickets generados y validados
- Mensajes enviados por canal
- Tasa de entrega de emails
- Tasa de entrega de WhatsApp
- Distribución por universidad
- Miembros IEEE vs no miembros

## 🚀 Deployment en Producción

### Con Cloudflare Tunnel (Recomendado)
```bash
# Instalar cloudflared
# Windows: descarga desde cloudflare.com

# Crear túnel
cloudflared tunnel create tu-tunnel

# Configurar y correr
cloudflared tunnel run tu-tunnel
```

### Variables de Entorno en Producción
```env
# Cambiar valores por defecto
SECRET_KEY=clave_super_segura_y_larga_random
MYSQL_PASSWORD=clave_segura_de_produccion

# Configurar dominio real
FROM_EMAIL=info@tudominio.com
FROM_NAME=IEEE Tadeo - Control System
```

## 📞 Soporte y Contacto

**IEEE Tadeo Student Branch**
- Sistema desarrollado para control interno
- Para reportar bugs o sugerencias, contacta al equipo de desarrollo

## 📝 Licencia

Este proyecto es de uso interno para IEEE - Universidad Tadeo Lozano.

---

**Desarrollado con ❤️ para IEEE UTadeo Student Branch**

*Sistema actualizado - Enero 2025*
