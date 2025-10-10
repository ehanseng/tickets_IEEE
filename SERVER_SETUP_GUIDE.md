# 🖥️ Guía de Configuración del Servidor

## 🎯 Problema Actual

Los archivos están en el servidor, pero muestra una lista de archivos en lugar de la aplicación.

**Causa**: El servidor web no está configurado para ejecutar aplicaciones Python/FastAPI.

---

## 📋 Solución según Tu Tipo de Hosting

### ✅ OPCIÓN 1: cPanel (Hosting Compartido)

Si tu hosting tiene cPanel:

#### Paso 1: Acceder a cPanel
1. Ve a tu panel de cPanel (usualmente `tudominio.com/cpanel`)
2. Busca **"Setup Python App"** o **"Python Selector"**

#### Paso 2: Crear Python Application
1. Click en **"Create Application"**
2. Configura:
   - **Python version**: 3.9 o superior (la más reciente disponible)
   - **Application root**: `/home/ieeetadeo2006/ticket` (o tu ruta completa)
   - **Application URL**: `ticket.ieeetadeo.org` o `/`
   - **Application startup file**: `passenger_wsgi.py`
   - **Application entry point**: `application`

#### Paso 3: Instalar Dependencias
1. En cPanel, en la sección de la app Python creada
2. Click en **"Run pip install"** o abrir terminal
3. Ejecutar:
```bash
pip install -r requirements.txt
```

#### Paso 4: Crear .env
1. En cPanel File Manager, navega a tu carpeta
2. Crea archivo `.env` con:
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu-email@gmail.com
SMTP_PASSWORD=xxxx-xxxx-xxxx-xxxx
FROM_EMAIL=tu-email@gmail.com
FROM_NAME=IEEE Tadeo - Sistema de Tickets
BASE_URL=https://ticket.ieeetadeo.org
```

#### Paso 5: Reiniciar Aplicación
1. En cPanel Python App, click en **"Restart"**
2. Espera 30 segundos
3. Visita `https://ticket.ieeetadeo.org`

---

### ✅ OPCIÓN 2: VPS con SSH (Acceso Root)

Si tienes un VPS con acceso root:

#### Paso 1: Instalar Dependencias del Sistema
```bash
ssh usuario@72.167.151.233

# Instalar Python 3.13 y dependencias
sudo apt update
sudo apt install python3.13 python3.13-venv nginx -y

# Instalar uv
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.cargo/env
```

#### Paso 2: Configurar la Aplicación
```bash
# Ir al directorio de la aplicación
cd /ruta/donde/estan/los/archivos

# Crear .env
nano .env
# Pega la configuración de arriba

# Instalar dependencias
uv sync
```

#### Paso 3: Crear Servicio Systemd
```bash
sudo nano /etc/systemd/system/tickets-ieee.service
```

Pega:
```ini
[Unit]
Description=Sistema de Tickets IEEE
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/ruta/completa/al/directorio
Environment="PATH=/ruta/completa/al/directorio/.venv/bin"
EnvironmentFile=/ruta/completa/al/directorio/.env
ExecStart=/home/usuario/.cargo/bin/uv run uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Iniciar servicio
sudo systemctl daemon-reload
sudo systemctl enable tickets-ieee
sudo systemctl start tickets-ieee
```

#### Paso 4: Configurar Nginx
```bash
sudo nano /etc/nginx/sites-available/ticket
```

Pega:
```nginx
server {
    listen 80;
    server_name ticket.ieeetadeo.org;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /qr_codes/ {
        alias /ruta/completa/al/directorio/qr_codes/;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/ticket /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# SSL (opcional pero recomendado)
sudo certbot --nginx -d ticket.ieeetadeo.org
```

---

### ✅ OPCIÓN 3: Sin Acceso SSH (Hosting Muy Limitado)

Si tu hosting NO soporta Python apps:

#### Alternativa: PythonAnywhere (Gratis)

1. **Crea cuenta en PythonAnywhere**: https://www.pythonanywhere.com/
2. **Web Apps** → **Add a new web app**
3. **Manual configuration** → **Python 3.10**
4. **Upload código** o clonar desde GitHub:
   ```bash
   git clone https://github.com/ehanseng/tickets_IEEE.git
   ```
5. **Configurar WSGI file**:
   ```python
   import sys
   path = '/home/tuusuario/tickets_IEEE'
   if path not in sys.path:
       sys.path.append(path)

   from main import app as application
   ```
6. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```
7. **Reload web app**

---

## 🔍 Verificar Qué Tipo de Servidor Tienes

### Método 1: Ver Panel de Control
- ¿Tienes acceso a un panel web? (cPanel, Plesk, DirectAdmin)
- Si sí → Usa OPCIÓN 1

### Método 2: Revisar por SSH
Conéctate y ejecuta:
```bash
# Ver si tienes sudo
sudo -l

# Ver servidor web instalado
which nginx
which apache2

# Ver Python disponible
python3 --version
```

- Si tienes `sudo` → Usa OPCIÓN 2 (VPS)
- Si NO tienes `sudo` y NO hay Python → Usa OPCIÓN 3 (PythonAnywhere)

---

## 📞 Dime Tu Situación

Para ayudarte mejor, responde:

1. **¿Tienes acceso a cPanel u otro panel de control?** (Sí/No)
2. **¿Tienes acceso SSH con permisos sudo?** (Sí/No)
3. **¿Qué sale cuando haces** `python3 --version` en SSH?

Con esta info te daré los pasos exactos para tu caso. 🚀

---

## ✅ Archivos Creados

Para facilitar la configuración, se han creado:

1. **`.htaccess`** - Para Apache/Passenger (cPanel)
2. **`passenger_wsgi.py`** - Entry point para Passenger
3. **`index.html`** - Página temporal mientras se configura
4. **`requirements.txt`** - Dependencias para pip

Una vez configurado correctamente, la aplicación responderá en:
- **https://ticket.ieeetadeo.org/admin** - Panel de administración
- **https://ticket.ieeetadeo.org/docs** - Documentación API

---

**¿Qué opción se ajusta a tu servidor?** Dime y te guío paso a paso. 🎯
