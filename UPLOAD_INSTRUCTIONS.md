# 📤 Instrucciones para Subir al Servidor

## ✅ Archivo Listo
Se ha creado: **`deploy_package.zip`** (80 KB)

---

## 🚀 MÉTODO 1: FileZilla (Recomendado)

### 1. Descargar e Instalar FileZilla
- https://filezilla-project.org/download.php?type=client

### 2. Conectarse al Servidor
```
Protocolo: SFTP - SSH File Transfer Protocol
Host: 72.167.151.233
Puerto: 22
Usuario: svrvpsefjkcv
Contraseña: OzsO$n63ddME
```

### 3. Navegar al Directorio Correcto
Una vez conectado, busca uno de estos directorios:
- `/home/ieeetadeo2006/public_html/ticket/`
- `/home/ieeetadeo2006/domains/ieeetadeo.org/public_html/ticket/`
- `/var/www/html/ieeetadeo.org/ticket/`

💡 **Tip**: Si no puedes acceder a `/home/ieeetadeo2006/`, pídele al administrador que te dé acceso o que suba él los archivos.

### 4. Subir Archivos
**Opción A**: Subir el ZIP y descomprimirlo en el servidor
1. Sube `deploy_package.zip` al directorio
2. Conéctate por SSH y ejecuta:
   ```bash
   cd /ruta/al/directorio/ticket
   unzip deploy_package.zip
   ```

**Opción B**: Subir archivos directamente
1. Extrae `deploy_package.zip` localmente
2. Sube todo el contenido a la carpeta del servidor

---

## 🚀 MÉTODO 2: cPanel / Panel de Control

### Si tienes acceso a cPanel:
1. Entra a tu panel de control
2. Busca "File Manager" o "Administrador de Archivos"
3. Navega a: `public_html/ieeetadeo.org/ticket/` (o similar)
4. Sube `deploy_package.zip`
5. Click derecho → "Extract" / "Extraer"

---

## 🚀 MÉTODO 3: Git Directo (Mejor opción si tienes acceso)

Si puedes conseguir acceso SSH con el usuario `ieeetadeo2006`:

```bash
# Conectar al servidor
ssh ieeetadeo2006@72.167.151.233

# Navegar al directorio correcto
cd /ruta/al/directorio/ticket

# Clonar desde GitHub
git clone https://github.com/ehanseng/tickets_IEEE.git .

# Listo! Los archivos ya están sincronizados con GitHub
```

---

## ⚙️ DESPUÉS DE SUBIR LOS ARCHIVOS

### 1. Crear archivo .env
Conéctate por SSH y crea el archivo `.env`:

```bash
cd /ruta/al/directorio/ticket
cp .env.example .env
nano .env
```

Configura:
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu-email@gmail.com
SMTP_PASSWORD=xxxx-xxxx-xxxx-xxxx
FROM_EMAIL=tu-email@gmail.com
FROM_NAME=IEEE Tadeo - Sistema de Tickets
BASE_URL=https://ticket.ieeetadeo.org
```

### 2. Instalar uv (si no está instalado)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.cargo/env
```

### 3. Instalar Dependencias
```bash
cd /ruta/al/directorio/ticket
uv sync
```

### 4. Crear Directorios Necesarios
```bash
mkdir -p qr_codes
chmod 755 qr_codes
```

### 5. Iniciar la Aplicación

**Opción A: Inicio Manual (para pruebas)**
```bash
uv run python main.py
# O con Uvicorn
uv run uvicorn main:app --host 0.0.0.0 --port 8000
```

**Opción B: Con Systemd (producción)**
Ver [DEPLOYMENT.md](DEPLOYMENT.md) para configuración completa

**Opción C: Con Screen (temporal)**
```bash
screen -S tickets
uv run uvicorn main:app --host 0.0.0.0 --port 8000
# Presiona Ctrl+A luego D para desconectar
# Para reconectar: screen -r tickets
```

---

## 🌐 Configurar Nginx/Apache

### Si el servidor usa Nginx:
```bash
sudo nano /etc/nginx/sites-available/ticket.ieeetadeo.org
```

Agregar:
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
        alias /ruta/completa/al/directorio/ticket/qr_codes/;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/ticket.ieeetadeo.org /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Obtener SSL:
```bash
sudo certbot --nginx -d ticket.ieeetadeo.org
```

---

## ✅ Verificar que Funciona

Abre en navegador:
- http://ticket.ieeetadeo.org:8000/admin (si no está configurado nginx)
- https://ticket.ieeetadeo.org/admin (con nginx + SSL)

---

## 🆘 Si Necesitas Ayuda

### No tienes acceso a ieeetadeo2006:
Contacta al administrador del servidor y pídele:
1. Acceso SSH con el usuario `ieeetadeo2006`
2. O que él ejecute estos comandos por ti

### Alternativa: Hosting Python
Si tu servidor no soporta Python adecuadamente, considera:
- **PythonAnywhere** (gratis para proyectos pequeños)
- **Heroku** (gratis con limitaciones)
- **Railway.app** (despliegue automático desde GitHub)
- **Render.com** (gratis con limitaciones)

---

## 📞 Próximos Pasos

1. ✅ Sube los archivos (Método 1, 2 o 3)
2. ✅ Configura `.env`
3. ✅ Instala dependencias
4. ✅ Inicia la aplicación
5. ✅ Configura Nginx/Apache
6. ✅ Obtén certificado SSL
7. ✅ Verifica que funciona en https://ticket.ieeetadeo.org

**¿Qué método vas a usar para subir los archivos?** 🚀
