# 🚀 Guía de Despliegue - Sistema de Tickets IEEE

## 📋 Índice
1. [Requisitos del Servidor](#requisitos-del-servidor)
2. [Despliegue en Servidor Linux](#despliegue-en-servidor-linux)
3. [Configuración con Nginx](#configuración-con-nginx)
4. [Configuración con Systemd](#configuración-con-systemd)
5. [Variables de Entorno](#variables-de-entorno)
6. [Actualizaciones](#actualizaciones)

---

## 📦 Requisitos del Servidor

### Sistema Operativo
- Ubuntu 20.04+ / Debian 11+ / CentOS 8+
- Python 3.13+
- Git

### Paquetes Necesarios
```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Python 3.13 (si no está disponible)
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install python3.13 python3.13-venv python3.13-dev -y

# Instalar dependencias del sistema
sudo apt install git nginx certbot python3-certbot-nginx curl -y

# Instalar uv (gestor de paquetes)
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.cargo/env
```

---

## 🖥️ Despliegue en Servidor Linux

### 1. Clonar el Repositorio

```bash
# Crear directorio para la aplicación
sudo mkdir -p /var/www/tickets-ieee
sudo chown -R $USER:$USER /var/www/tickets-ieee

# Clonar el repositorio
cd /var/www/tickets-ieee
git clone https://github.com/ehanseng/tickets_IEEE.git .
```

### 2. Configurar el Entorno

```bash
# Instalar dependencias
uv sync

# Crear archivo de variables de entorno
cp .env.example .env
nano .env
```

Configurar las variables de entorno (ver sección [Variables de Entorno](#variables-de-entorno))

### 3. Crear Directorios Necesarios

```bash
# Crear directorio para QR codes
mkdir -p qr_codes

# Configurar permisos
chmod 755 qr_codes
```

### 4. Probar la Aplicación

```bash
# Ejecutar en modo desarrollo
uv run python main.py
```

Verifica que funcione visitando `http://TU_IP:8000`

---

## 🌐 Configuración con Nginx

### 1. Crear Configuración de Nginx

```bash
sudo nano /etc/nginx/sites-available/tickets-ieee
```

Agregar el siguiente contenido:

```nginx
server {
    listen 80;
    server_name tu-dominio.com www.tu-dominio.com;

    # Límites de tamaño para uploads
    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support (si se necesita en el futuro)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Servir archivos estáticos directamente
    location /qr_codes/ {
        alias /var/www/tickets-ieee/qr_codes/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

### 2. Activar el Sitio

```bash
# Crear enlace simbólico
sudo ln -s /etc/nginx/sites-available/tickets-ieee /etc/nginx/sites-enabled/

# Verificar configuración
sudo nginx -t

# Reiniciar Nginx
sudo systemctl restart nginx
```

### 3. Configurar SSL con Let's Encrypt

```bash
# Obtener certificado SSL
sudo certbot --nginx -d tu-dominio.com -d www.tu-dominio.com

# Verificar renovación automática
sudo certbot renew --dry-run
```

---

## ⚙️ Configuración con Systemd

### 1. Crear Servicio Systemd

```bash
sudo nano /etc/systemd/system/tickets-ieee.service
```

Agregar el siguiente contenido:

```ini
[Unit]
Description=Sistema de Tickets IEEE - FastAPI Application
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/var/www/tickets-ieee
Environment="PATH=/var/www/tickets-ieee/.venv/bin"
EnvironmentFile=/var/www/tickets-ieee/.env
ExecStart=/root/.cargo/bin/uv run uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10

# Logging
StandardOutput=append:/var/log/tickets-ieee/access.log
StandardError=append:/var/log/tickets-ieee/error.log

# Seguridad
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

### 2. Crear Directorios de Logs

```bash
sudo mkdir -p /var/log/tickets-ieee
sudo chown -R www-data:www-data /var/log/tickets-ieee
```

### 3. Configurar Permisos

```bash
# Cambiar propietario de la aplicación
sudo chown -R www-data:www-data /var/www/tickets-ieee

# Permisos para base de datos
sudo chmod 664 /var/www/tickets-ieee/tickets.db
sudo chmod 775 /var/www/tickets-ieee
```

### 4. Iniciar el Servicio

```bash
# Recargar systemd
sudo systemctl daemon-reload

# Habilitar inicio automático
sudo systemctl enable tickets-ieee

# Iniciar servicio
sudo systemctl start tickets-ieee

# Verificar estado
sudo systemctl status tickets-ieee
```

### 5. Comandos Útiles

```bash
# Ver logs en tiempo real
sudo journalctl -u tickets-ieee -f

# Reiniciar servicio
sudo systemctl restart tickets-ieee

# Detener servicio
sudo systemctl stop tickets-ieee

# Ver logs de errores
sudo tail -f /var/log/tickets-ieee/error.log

# Ver logs de acceso
sudo tail -f /var/log/tickets-ieee/access.log
```

---

## 🔐 Variables de Entorno

Crear archivo `.env` con las siguientes variables:

```bash
# Configuración SMTP (Gmail)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu-email@gmail.com
SMTP_PASSWORD=xxxx-xxxx-xxxx-xxxx  # Contraseña de aplicación de Gmail
FROM_EMAIL=tu-email@gmail.com
FROM_NAME=IEEE Tadeo - Sistema de Tickets

# URL base del sistema (cambiar en producción)
BASE_URL=https://tu-dominio.com

# Configuración de la aplicación (opcional)
# WORKERS=4  # Número de workers de Uvicorn
```

### Obtener Contraseña de Aplicación de Gmail

1. Ve a [https://myaccount.google.com/security](https://myaccount.google.com/security)
2. Activa la verificación en 2 pasos
3. Ve a "Contraseñas de aplicaciones"
4. Genera una nueva contraseña para "Correo"
5. Usa esa contraseña de 16 dígitos en `SMTP_PASSWORD`

---

## 🔄 Actualizaciones

### Actualizar la Aplicación

```bash
# Ir al directorio de la aplicación
cd /var/www/tickets-ieee

# Obtener últimos cambios
git pull origin master

# Actualizar dependencias
uv sync

# Reiniciar servicio
sudo systemctl restart tickets-ieee
```

### Backup de Base de Datos

```bash
# Crear backup manual
cp /var/www/tickets-ieee/tickets.db /var/www/tickets-ieee/backup_$(date +%Y%m%d_%H%M%S).db

# Automatizar backups (agregar a crontab)
sudo crontab -e

# Agregar línea para backup diario a las 2 AM
0 2 * * * cp /var/www/tickets-ieee/tickets.db /var/www/tickets-ieee/backups/backup_$(date +\%Y\%m\%d).db && find /var/www/tickets-ieee/backups/ -mtime +30 -delete
```

---

## 🔥 Firewall (UFW)

```bash
# Permitir SSH
sudo ufw allow ssh

# Permitir HTTP y HTTPS
sudo ufw allow 'Nginx Full'

# Activar firewall
sudo ufw enable

# Verificar estado
sudo ufw status
```

---

## 🐛 Solución de Problemas

### Verificar si el servicio está corriendo
```bash
sudo systemctl status tickets-ieee
```

### Verificar logs de errores
```bash
sudo journalctl -u tickets-ieee -n 50 --no-pager
```

### Verificar que Nginx está funcionando
```bash
sudo systemctl status nginx
sudo nginx -t
```

### Verificar permisos de archivos
```bash
ls -la /var/www/tickets-ieee/
ls -la /var/www/tickets-ieee/tickets.db
```

### Reiniciar todo
```bash
sudo systemctl restart tickets-ieee
sudo systemctl restart nginx
```

---

## 📊 Monitoreo

### Recursos del Sistema
```bash
# Uso de CPU y memoria
htop

# Espacio en disco
df -h

# Logs del servicio
sudo journalctl -u tickets-ieee --since "1 hour ago"
```

---

## 🔒 Seguridad Adicional

### 1. Configurar Fail2Ban
```bash
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 2. Mantener el Sistema Actualizado
```bash
sudo apt update && sudo apt upgrade -y
```

### 3. Configurar Backups Automáticos
Considera usar herramientas como:
- `rsync` para backups incrementales
- `borgbackup` para backups encriptados
- Servicios en la nube (AWS S3, Google Cloud Storage)

---

## 📞 Soporte

Para reportar problemas o consultas sobre el despliegue:
- Repositorio: https://github.com/ehanseng/tickets_IEEE
- Documentación: [README.md](README.md)

---

**Desarrollado con ❤️ para IEEE UTadeo**
