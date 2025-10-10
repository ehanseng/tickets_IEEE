# ⚡ Guía Rápida de Despliegue

## 🎯 Opción 1: Despliegue Rápido con Script (Linux)

```bash
# 1. Clonar repositorio
git clone https://github.com/ehanseng/tickets_IEEE.git
cd tickets_IEEE

# 2. Configurar variables de entorno
cp .env.example .env
nano .env  # Editar con tus credenciales SMTP

# 3. Dar permisos de ejecución al script
chmod +x start_production.sh

# 4. Ejecutar
./start_production.sh
```

La aplicación estará disponible en `http://localhost:8000`

---

## 🐳 Opción 2: Despliegue con Docker

```bash
# 1. Clonar repositorio
git clone https://github.com/ehanseng/tickets_IEEE.git
cd tickets_IEEE

# 2. Configurar variables de entorno
cp .env.example .env
nano .env  # Editar con tus credenciales SMTP

# 3. Construir y ejecutar
docker-compose up -d

# Ver logs
docker-compose logs -f
```

La aplicación estará disponible en `http://localhost:8000`

---

## 🖥️ Opción 3: Despliegue en Servidor con Nginx + Systemd

Ver guía completa en [DEPLOYMENT.md](DEPLOYMENT.md)

**Resumen:**
1. Instalar Python 3.13+ y uv
2. Clonar repositorio en `/var/www/tickets-ieee`
3. Configurar `.env`
4. Crear servicio systemd
5. Configurar Nginx como proxy reverso
6. Obtener certificado SSL con Let's Encrypt

---

## ⚙️ Configuración Mínima Requerida

### Variables de Entorno (.env)

```bash
# SMTP (obligatorio para envío de tickets)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu-email@gmail.com
SMTP_PASSWORD=xxxx-xxxx-xxxx-xxxx  # Contraseña de aplicación
FROM_EMAIL=tu-email@gmail.com
FROM_NAME=IEEE Tadeo - Sistema de Tickets

# URL base
BASE_URL=https://tu-dominio.com  # Cambiar en producción
```

### Obtener Contraseña de Aplicación de Gmail

1. [Ir a Seguridad de Google](https://myaccount.google.com/security)
2. Activar verificación en 2 pasos
3. Buscar "Contraseñas de aplicaciones"
4. Generar nueva contraseña para "Correo"
5. Copiar contraseña de 16 dígitos a `.env`

---

## 🔍 Verificación Post-Despliegue

Verifica que todo funcione correctamente:

### 1. API
```bash
curl http://localhost:8000/docs
```
Deberías ver la documentación Swagger.

### 2. Panel de Administración
Abre en navegador:
- Dashboard: http://localhost:8000/admin
- Usuarios: http://localhost:8000/admin/users
- Eventos: http://localhost:8000/admin/events
- Tickets: http://localhost:8000/admin/tickets
- Validación: http://localhost:8000/admin/validate

### 3. Logs
```bash
# Si usas systemd
sudo journalctl -u tickets-ieee -f

# Si usas Docker
docker-compose logs -f

# Si usas el script
# Los logs aparecerán en la terminal
```

---

## 🛠️ Comandos Útiles

### Con Script (Linux)
```bash
./start_production.sh          # Iniciar
Ctrl+C                          # Detener
```

### Con Docker
```bash
docker-compose up -d            # Iniciar en background
docker-compose down             # Detener
docker-compose restart          # Reiniciar
docker-compose logs -f          # Ver logs
docker-compose pull && docker-compose up -d  # Actualizar
```

### Con Systemd
```bash
sudo systemctl start tickets-ieee      # Iniciar
sudo systemctl stop tickets-ieee       # Detener
sudo systemctl restart tickets-ieee    # Reiniciar
sudo systemctl status tickets-ieee     # Ver estado
sudo journalctl -u tickets-ieee -f     # Ver logs
```

---

## 🔄 Actualizar la Aplicación

### Con Git
```bash
git pull origin master
uv sync
# Reiniciar según el método que uses
```

### Con Docker
```bash
git pull origin master
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

---

## 🆘 Solución Rápida de Problemas

### Puerto 8000 ya en uso
```bash
# Encontrar proceso usando el puerto
sudo lsof -i :8000

# Matar proceso
kill -9 <PID>
```

### Permisos de base de datos
```bash
chmod 664 tickets.db
chmod 775 qr_codes/
```

### Verificar servicio
```bash
# Systemd
sudo systemctl status tickets-ieee

# Docker
docker-compose ps
```

---

## 📊 Accesos Iniciales

Una vez desplegado, accede al panel de administración en:

**http://TU_DOMINIO/admin**

o

**http://TU_IP:8000/admin**

No hay autenticación por defecto. Se recomienda configurar un proxy reverso con autenticación básica o implementar autenticación en la aplicación.

---

## 📞 Soporte

- **Documentación completa**: [README.md](README.md)
- **Guía de despliegue**: [DEPLOYMENT.md](DEPLOYMENT.md)
- **Repositorio**: https://github.com/ehanseng/tickets_IEEE

---

**Desarrollado con ❤️ para IEEE UTadeo**
