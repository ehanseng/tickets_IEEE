# ✅ Lista de Verificación para Despliegue en Servidor Personal

## 📋 Pre-requisitos

### Información que necesitas tener lista:
- [ ] IP o dominio de tu servidor
- [ ] Acceso SSH al servidor (usuario y contraseña o llave SSH)
- [ ] Cuenta de Gmail con contraseña de aplicación configurada
- [ ] Dominio (opcional, pero recomendado para SSL)

---

## 🚀 Pasos de Despliegue

### 1️⃣ Preparar el Servidor (Una sola vez)

```bash
# Conectarse al servidor
ssh usuario@tu-servidor-ip

# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Python 3.13
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install python3.13 python3.13-venv python3.13-dev -y

# Instalar otras dependencias
sudo apt install git nginx certbot python3-certbot-nginx curl -y

# Instalar uv
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.cargo/env
```

### 2️⃣ Clonar y Configurar la Aplicación

```bash
# Crear directorio
sudo mkdir -p /var/www/tickets-ieee
sudo chown -R $USER:$USER /var/www/tickets-ieee

# Clonar repositorio
cd /var/www/tickets-ieee
git clone https://github.com/ehanseng/tickets_IEEE.git .

# Configurar variables de entorno
cp .env.example .env
nano .env
```

**Configurar en .env:**
```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu-email@gmail.com
SMTP_PASSWORD=xxxx-xxxx-xxxx-xxxx  # Tu contraseña de aplicación
FROM_EMAIL=tu-email@gmail.com
FROM_NAME=IEEE Tadeo - Sistema de Tickets
BASE_URL=https://tu-dominio.com  # o http://tu-ip:8000
```

```bash
# Instalar dependencias
uv sync

# Crear directorios
mkdir -p qr_codes
mkdir -p logs
```

### 3️⃣ Crear Servicio Systemd

```bash
sudo nano /etc/systemd/system/tickets-ieee.service
```

**Copiar este contenido:**
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

StandardOutput=append:/var/log/tickets-ieee/access.log
StandardError=append:/var/log/tickets-ieee/error.log

NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

```bash
# Crear directorios de logs
sudo mkdir -p /var/log/tickets-ieee
sudo chown -R www-data:www-data /var/log/tickets-ieee

# Configurar permisos
sudo chown -R www-data:www-data /var/www/tickets-ieee

# Iniciar servicio
sudo systemctl daemon-reload
sudo systemctl enable tickets-ieee
sudo systemctl start tickets-ieee
sudo systemctl status tickets-ieee
```

### 4️⃣ Configurar Nginx (Opcional pero recomendado)

```bash
sudo nano /etc/nginx/sites-available/tickets-ieee
```

**Copiar este contenido (reemplazar tu-dominio.com):**
```nginx
server {
    listen 80;
    server_name tu-dominio.com www.tu-dominio.com;

    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    location /qr_codes/ {
        alias /var/www/tickets-ieee/qr_codes/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

```bash
# Activar sitio
sudo ln -s /etc/nginx/sites-available/tickets-ieee /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 5️⃣ Configurar SSL (Si tienes dominio)

```bash
# Obtener certificado SSL gratis con Let's Encrypt
sudo certbot --nginx -d tu-dominio.com -d www.tu-dominio.com

# Verificar renovación automática
sudo certbot renew --dry-run
```

### 6️⃣ Configurar Firewall

```bash
# Permitir SSH, HTTP y HTTPS
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable
sudo ufw status
```

---

## ✅ Verificación

### Verificar que el servicio está corriendo
```bash
sudo systemctl status tickets-ieee
```

### Verificar logs
```bash
sudo journalctl -u tickets-ieee -f
```

### Verificar en navegador
- **Con dominio**: https://tu-dominio.com/admin
- **Sin dominio**: http://tu-ip:8000/admin

---

## 🔄 Comandos de Mantenimiento

### Ver logs en tiempo real
```bash
sudo journalctl -u tickets-ieee -f
```

### Reiniciar aplicación
```bash
sudo systemctl restart tickets-ieee
```

### Actualizar aplicación
```bash
cd /var/www/tickets-ieee
git pull origin master
uv sync
sudo systemctl restart tickets-ieee
```

### Backup de base de datos
```bash
cp /var/www/tickets-ieee/tickets.db /var/www/tickets-ieee/backup_$(date +%Y%m%d_%H%M%S).db
```

### Ver estado de Nginx
```bash
sudo systemctl status nginx
```

---

## 🆘 Solución de Problemas

### El servicio no inicia
```bash
# Ver logs de error
sudo journalctl -u tickets-ieee -n 50 --no-pager

# Verificar permisos
ls -la /var/www/tickets-ieee/
sudo chown -R www-data:www-data /var/www/tickets-ieee
```

### Error de puerto en uso
```bash
# Encontrar qué está usando el puerto 8000
sudo lsof -i :8000
# Detener ese proceso o cambiar el puerto en el servicio
```

### Error de base de datos
```bash
# Verificar permisos
sudo chmod 664 /var/www/tickets-ieee/tickets.db
sudo chown www-data:www-data /var/www/tickets-ieee/tickets.db
```

### Nginx no funciona
```bash
# Verificar configuración
sudo nginx -t

# Ver logs
sudo tail -f /var/log/nginx/error.log
```

---

## 📊 Monitoreo

### Uso de recursos
```bash
# CPU y memoria
htop

# Espacio en disco
df -h

# Procesos de Python
ps aux | grep python
```

### Logs de acceso
```bash
sudo tail -f /var/log/tickets-ieee/access.log
```

### Logs de errores
```bash
sudo tail -f /var/log/tickets-ieee/error.log
```

---

## 🎯 Acceso a la Aplicación

Una vez desplegado, podrás acceder a:

- **Dashboard**: https://tu-dominio.com/admin
- **Gestión de Usuarios**: https://tu-dominio.com/admin/users
- **Gestión de Eventos**: https://tu-dominio.com/admin/events
- **Gestión de Tickets**: https://tu-dominio.com/admin/tickets
- **Validación QR**: https://tu-dominio.com/admin/validate
- **API Docs**: https://tu-dominio.com/docs

---

## 🔒 Seguridad

### Backups automáticos
```bash
# Editar crontab
sudo crontab -e

# Agregar backup diario a las 2 AM
0 2 * * * cp /var/www/tickets-ieee/tickets.db /var/www/tickets-ieee/backups/backup_$(date +\%Y\%m\%d).db && find /var/www/tickets-ieee/backups/ -mtime +30 -delete
```

### Mantener sistema actualizado
```bash
# Actualizar paquetes
sudo apt update && sudo apt upgrade -y

# Actualizar certificados SSL (automático, pero puedes forzar)
sudo certbot renew
```

---

## 📞 Soporte

- **Repositorio**: https://github.com/ehanseng/tickets_IEEE
- **Documentación completa**: [DEPLOYMENT.md](DEPLOYMENT.md)
- **Guía rápida**: [QUICK_START.md](QUICK_START.md)

---

**¡Éxito en el despliegue! 🚀**
