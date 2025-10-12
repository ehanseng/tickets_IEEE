# 🚀 Comandos para Despliegue con GitHub

## PASO 1: Conectar al Servidor
```bash
ssh svrvpsefjkcv@72.167.151.233
# Contraseña: OzsO$n63ddME
```

---

## PASO 2: Cambiar al Usuario Correcto
```bash
# Intentar cambiar a usuario ieeetadeo2006
sudo su - ieeetadeo2006

# Si pide contraseña y no funciona, contacta al admin
```

---

## PASO 3: Encontrar Directorio Ticket
```bash
# Ver dónde estás
pwd

# Listar contenido
ls -la

# Buscar directorio ticket
find ~ -maxdepth 4 -name 'ticket' -type d 2>/dev/null

# Opciones comunes (prueba una por una):
cd ~/public_html/ticket
# O
cd ~/domains/ieeetadeo.org/public_html/ticket
# O
cd ~/public_html/ieeetadeo.org/ticket
# O
cd ~/www/ieeetadeo.org/ticket

# Verificar que estás en el lugar correcto
pwd
```

---

## PASO 4: Verificar Git
```bash
# Verificar si git está instalado
which git
git --version

# Si no está instalado:
# CentOS/AlmaLinux/Rocky:
sudo yum install git -y

# Ubuntu/Debian:
sudo apt install git -y
```

---

## PASO 5: Clonar Repositorio
```bash
# Ver contenido actual
ls -la

# IMPORTANTE: Si hay archivos, hacer backup primero
mkdir ~/backup_ticket_$(date +%Y%m%d_%H%M%S)
cp -r * ~/backup_ticket_$(date +%Y%m%d_%H%M%S)/ 2>/dev/null

# Si la carpeta está vacía, clonar directamente:
git clone https://github.com/ehanseng/tickets_IEEE.git .

# Si la carpeta NO está vacía y quieres reemplazar todo:
rm -rf * .git 2>/dev/null  # ¡CUIDADO! Esto borra todo
git clone https://github.com/ehanseng/tickets_IEEE.git .

# Verificar que se clonó correctamente
ls -la
# Deberías ver: main.py, models.py, templates/, etc.
```

---

## PASO 6: Configurar Variables de Entorno
```bash
# Copiar ejemplo de .env
cp .env.example .env

# Editar archivo .env
nano .env

# Presiona estas teclas en nano:
# - Edita las líneas con tus credenciales
# - Ctrl + O para guardar
# - Enter para confirmar
# - Ctrl + X para salir
```

**Contenido del .env:**
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu-email@gmail.com
SMTP_PASSWORD=xxxx-xxxx-xxxx-xxxx
FROM_EMAIL=tu-email@gmail.com
FROM_NAME=IEEE Tadeo - Sistema de Tickets
BASE_URL=https://ticket.ieeetadeo.org
```

---

## PASO 7: Instalar uv (Gestor de Paquetes)
```bash
# Verificar si uv ya está instalado
which uv

# Si no está, instalar:
curl -LsSf https://astral.sh/uv/install.sh | sh

# Recargar el PATH
source $HOME/.cargo/env

# Verificar instalación
uv --version
```

---

## PASO 8: Verificar Python
```bash
# Verificar Python
python3 --version

# Si es menor a 3.10, puede funcionar pero idealmente necesitas 3.13+
# Para instalar Python 3.13 (requiere permisos sudo):

# CentOS/AlmaLinux/Rocky:
sudo yum install python3.13 -y

# Ubuntu/Debian:
sudo apt install python3.13 -y
```

---

## PASO 9: Instalar Dependencias
```bash
# Estar en el directorio del proyecto
cd ~/ruta/al/directorio/ticket

# Instalar dependencias con uv
uv sync

# Si uv no funciona, usar pip:
python3 -m pip install -r requirements.txt --user
```

---

## PASO 10: Crear Directorios Necesarios
```bash
# Crear directorio para QR codes
mkdir -p qr_codes

# Dar permisos
chmod 755 qr_codes
```

---

## PASO 11: Probar la Aplicación
```bash
# Opción 1: Ejecución simple (para probar)
uv run python main.py

# Opción 2: Con uvicorn (mejor para producción)
uv run uvicorn main:app --host 0.0.0.0 --port 8000

# Opción 3: Con screen (mantiene corriendo después de desconectar)
screen -S tickets
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2
# Presiona Ctrl+A luego D para desconectar
# Para volver: screen -r tickets
# Para matar: screen -X -S tickets quit
```

---

## PASO 12: Verificar que Funciona

Abre en navegador:
- http://ticket.ieeetadeo.org:8000/admin
- http://72.167.151.233:8000/admin

Si funciona, verás el panel de administración!

---

## 🔄 ACTUALIZACIONES FUTURAS

Para actualizar la aplicación desde GitHub:

```bash
# Conectar al servidor
ssh svrvpsefjkcv@72.167.151.233
sudo su - ieeetadeo2006

# Ir al directorio
cd ~/ruta/al/directorio/ticket

# Obtener últimos cambios
git pull origin master

# Actualizar dependencias
uv sync

# Reiniciar aplicación
# Si usas screen:
screen -X -S tickets quit
screen -S tickets
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2
# Ctrl+A, D para desconectar

# Si usas systemd (después de configurar):
sudo systemctl restart tickets-ieee
```

---

## ❌ SOLUCIÓN DE PROBLEMAS

### Error: Permission denied
```bash
# Verificar permisos
ls -la
# Cambiar propietario si es necesario
sudo chown -R ieeetadeo2006:ieeetadeo2006 .
```

### Error: git command not found
```bash
sudo yum install git -y  # CentOS
sudo apt install git -y  # Ubuntu
```

### Error: uv command not found
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.cargo/env
```

### Error: Port 8000 already in use
```bash
# Encontrar qué proceso está usando el puerto
sudo lsof -i :8000
# Matar ese proceso
kill -9 <PID>
```

### No puedo cambiar a usuario ieeetadeo2006
**Contacta al administrador del servidor** y pídele:
1. Acceso SSH con usuario ieeetadeo2006
2. O que ejecute estos comandos por ti
3. O que te agregue al grupo de ieeetadeo2006

---

## 📞 SIGUIENTE PASO DESPUÉS DE FUNCIONAR

Una vez que la aplicación funcione en puerto 8000, necesitarás:

1. **Configurar Nginx/Apache** para que funcione en puerto 80/443
2. **Obtener certificado SSL** para HTTPS
3. **Configurar systemd** para auto-inicio

Ver [DEPLOYMENT.md](DEPLOYMENT.md) para instrucciones detalladas.

---

## ✅ CHECKLIST

- [ ] Conectado al servidor
- [ ] Cambiado a usuario ieeetadeo2006
- [ ] Navegado a directorio ticket
- [ ] Git instalado
- [ ] Repositorio clonado
- [ ] Archivo .env configurado
- [ ] uv instalado
- [ ] Dependencias instaladas
- [ ] Directorios creados
- [ ] Aplicación iniciada
- [ ] Verificado en navegador

---

**¡Listo! Ahora ejecuta los comandos paso a paso y pégame aquí los resultados para ayudarte con cualquier error.** 🚀
