# 🎫 Sistema de Tickets IEEE

Sistema de control de ingreso a eventos mediante códigos QR con encriptación.

## 🚀 Características

- ✅ Registro de usuarios y eventos
- ✅ Generación automática de tickets con QR codes únicos
- ✅ Datos encriptados en cada QR
- ✅ Validación de tickets en tiempo real
- ✅ Control de tickets ya utilizados
- ✅ **Panel de administración web completo**
- ✅ **Escáner QR desde navegador**
- ✅ API REST completa
- ✅ Documentación interactiva (Swagger)

## 📋 Requisitos

- Python 3.13+
- uv (gestor de paquetes)

## 🛠️ Instalación

1. Instalar dependencias:
```bash
uv sync
```

2. Ejecutar el servidor:
```bash
uv run python main.py
```

El servidor estará disponible en `http://localhost:8000`

## 📚 Uso

### 🖥️ Panel de Administración Web

El sistema incluye una **interfaz web completa** para gestión:

- **Dashboard**: http://localhost:8000/admin
  - Estadísticas generales
  - Resumen de eventos activos
  - Accesos rápidos

- **Gestión de Usuarios**: http://localhost:8000/admin/users
  - Registrar nuevos usuarios
  - Ver lista de usuarios
  - Ver cantidad de tickets por usuario

- **Gestión de Eventos**: http://localhost:8000/admin/events
  - Crear nuevos eventos
  - Ver eventos activos/inactivos
  - Ver cantidad de tickets por evento

- **Gestión de Tickets**: http://localhost:8000/admin/tickets
  - Generar tickets para usuarios
  - Ver código del ticket
  - **Copiar código** para validación manual
  - Descargar QR como imagen
  - Ver estado (usado/disponible)

- **Validación de Entrada**: http://localhost:8000/admin/validate
  - **Escáner QR con cámara**
  - Validación manual por código
  - Historial de validaciones
  - Alertas visuales

### 📷 Validación con Escáner QR

**Opción 1: Escanear QR**
1. Ve a http://localhost:8000/admin/validate
2. Haz clic en "📷 Activar Cámara"
3. Permite el acceso a la cámara cuando el navegador lo solicite
4. Apunta al código QR del ticket
5. El sistema validará automáticamente y mostrará:
   - ✅ Verde: Acceso permitido
   - ❌ Rojo: Acceso denegado (ya usado o inválido)

**Opción 2: Validación Manual**
1. En la página de tickets, copia el código del ticket (botón 📋 Copiar)
2. Ve a la página de validación
3. Pega el código en el campo "Código del Ticket"
4. Haz clic en "Validar Ticket"

### 🔧 Flujo de Trabajo Completo

#### 1. Registrar un Usuario
- Ve a http://localhost:8000/admin/users
- Haz clic en "➕ Registrar Nuevo Usuario"
- Completa el formulario (nombre, email, teléfono)
- Haz clic en "Registrar Usuario"

#### 2. Crear un Evento
- Ve a http://localhost:8000/admin/events
- Haz clic en "➕ Crear Nuevo Evento"
- Completa el formulario (nombre, descripción, ubicación, fecha)
- Haz clic en "Crear Evento"

#### 3. Generar Tickets
- Ve a http://localhost:8000/admin/tickets
- Haz clic en "➕ Generar Nuevo Ticket"
- Selecciona un usuario y un evento
- Haz clic en "Generar Ticket"
- Se mostrará el QR automáticamente
- Puedes descargar el QR o copiar el código

#### 4. Validar en la Entrada
- En el día del evento, ve a http://localhost:8000/admin/validate
- Activa la cámara y escanea los QR de los asistentes
- O ingresa manualmente el código del ticket
- El sistema mostrará si el acceso es permitido o denegado

## 📡 API REST (Uso Avanzado)

### Documentación Interactiva
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Endpoints principales

#### Usuarios
- `POST /users/` - Crear usuario
- `GET /users/` - Listar usuarios
- `GET /users/{id}` - Obtener usuario

#### Eventos
- `POST /events/` - Crear evento
- `GET /events/` - Listar eventos
- `GET /events/{id}` - Obtener evento

#### Tickets
- `POST /tickets/` - Crear ticket
- `GET /tickets/` - Listar tickets
- `GET /tickets/{id}` - Obtener ticket
- `GET /tickets/{id}/qr` - Obtener imagen QR
- `GET /tickets/{id}/qr-base64` - Obtener QR en base64

#### Validación
- `POST /validate/` - Validar ticket por código
- `POST /validate/qr` - Validar QR escaneado

### Ejemplos de uso con curl

#### Crear usuario
```bash
curl -X POST "http://localhost:8000/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Juan Pérez",
    "email": "juan@example.com",
    "phone": "1234567890"
  }'
```

#### Crear evento
```bash
curl -X POST "http://localhost:8000/events/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Conferencia IEEE 2025",
    "description": "Conferencia anual de tecnología",
    "location": "Universidad Tadeo",
    "event_date": "2025-11-15T18:00:00"
  }'
```

#### Generar ticket
```bash
curl -X POST "http://localhost:8000/tickets/" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "event_id": 1
  }'
```

#### Validar ticket
```bash
curl -X POST "http://localhost:8000/validate/" \
  -H "Content-Type: application/json" \
  -d '{
    "ticket_code": "codigo_del_ticket_aqui"
  }'
```

## 🏗️ Estructura del Proyecto

```
Ticket/
├── main.py              # Aplicación principal FastAPI + rutas admin
├── models.py            # Modelos de base de datos
├── schemas.py           # Esquemas Pydantic
├── database.py          # Configuración de base de datos
├── ticket_service.py    # Servicio de generación de QR
├── templates/           # Templates HTML para admin
│   ├── base.html       # Template base
│   ├── dashboard.html  # Dashboard principal
│   ├── users.html      # Gestión de usuarios
│   ├── events.html     # Gestión de eventos
│   ├── tickets.html    # Gestión de tickets
│   └── validate.html   # Validación con escáner QR
├── pyproject.toml       # Dependencias del proyecto
├── tickets.db           # Base de datos SQLite (auto-generada)
└── qr_codes/           # Carpeta con QR generados (auto-generada)
```

## 🔒 Seguridad

- El QR contiene el **código único del ticket** (hash SHA-256 de 64 caracteres)
- Cada ticket tiene un código único generado con **SHA-256**
- Los tickets solo pueden usarse **una vez**
- Se registra fecha y hora de uso
- QR optimizado para escaneo rápido (64 caracteres vs 300+)
- El código es imposible de adivinar o duplicar

## 💡 Consejos de Uso

1. **Para eventos presenciales**: Usa el escáner QR desde una tablet o laptop en la entrada
2. **Para validación rápida**: Ten una persona con el escáner y otra con validación manual
3. **Backup**: Descarga todos los QR antes del evento por si hay problemas de conexión
4. **Pruebas**: Genera tickets de prueba y valídalos antes del evento real

## 🐛 Solución de Problemas

### La cámara no funciona
- Verifica que el navegador tenga permisos para acceder a la cámara
- Usa HTTPS o localhost (las cámaras solo funcionan en contextos seguros)
- Intenta con otro navegador (Chrome/Edge recomendados)
- Si falla, usa validación manual

### Ticket no valida
- Verifica que el código esté completo al copiar/pegar
- Asegúrate de que el ticket no haya sido usado previamente
- Revisa que el evento esté activo

### Base de datos
- La base de datos SQLite se crea automáticamente
- Para resetear: elimina el archivo `tickets.db` y reinicia el servidor

## 🚧 Próximas Mejoras

- [ ] Envío de tickets por email
- [ ] Categorías de tickets (VIP, general, estudiante)
- [ ] Reportes y estadísticas avanzadas
- [ ] Exportar datos a Excel/CSV
- [ ] Integración con sistemas de pago
- [ ] Autenticación y roles (admin, validador, etc.)
- [ ] App móvil nativa para validación
- [ ] Soporte multi-idioma

## 📞 Soporte

Este proyecto es para IEEE - Universidad Tadeo Lozano

Para reportar problemas o sugerencias, contacta al equipo de desarrollo.

---

**Desarrollado con ❤️ para IEEE UTadeo**
