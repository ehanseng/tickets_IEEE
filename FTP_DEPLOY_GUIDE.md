# 🚀 Guía de Despliegue Automático FTP

## ✅ Configuración Completada

Se ha creado el workflow: **`.github/workflows/deploy-ftp.yml`**

Cada vez que hagas `git push` a GitHub, automáticamente se subirán los archivos a tu servidor por FTP.

---

## 📋 PASO 1: Averiguar la Ruta FTP Correcta (IMPORTANTE)

### 1.1 Descargar FileZilla
https://filezilla-project.org/download.php?type=client

### 1.2 Conectarse al Servidor
En FileZilla, usa estos datos:

- **Host**: `ticket.ieeetadeo.org`
- **Usuario**: `adminIEEEtadeo@ticket.ieeetadeo.org`
- **Contraseña**: `Rn5GkEcwQpCE3LK`
- **Puerto**: `21`

### 1.3 Identificar la Ruta
Una vez conectado, verás la estructura de carpetas. La ruta puede ser:

- `/` (si ya estás en la carpeta correcta del dominio)
- `/public_html/`
- `/htdocs/`
- `/www/`
- O alguna carpeta específica

**Anota esta ruta exacta** - la necesitarás para el siguiente paso.

---

## 📋 PASO 2: Configurar Secretos en GitHub

### 2.1 Ir a tu Repositorio
https://github.com/ehanseng/tickets_IEEE

### 2.2 Configurar Secretos
1. Click en **"Settings"** (arriba a la derecha)
2. En el menú izquierdo: **"Secrets and variables"** → **"Actions"**
3. Click en **"New repository secret"**

### 2.3 Agregar 4 Secretos

#### Secreto 1: FTP_SERVER
- Name: `FTP_SERVER`
- Secret: `ticket.ieeetadeo.org`
- Click "Add secret"

#### Secreto 2: FTP_USERNAME
- Name: `FTP_USERNAME`
- Secret: `adminIEEEtadeo@ticket.ieeetadeo.org`
- Click "Add secret"

#### Secreto 3: FTP_PASSWORD
- Name: `FTP_PASSWORD`
- Secret: `Rn5GkEcwQpCE3LK`
- Click "Add secret"

#### Secreto 4: FTP_REMOTE_PATH
- Name: `FTP_REMOTE_PATH`
- Secret: **LA RUTA QUE VISTE EN FILEZILLA**
  - Ejemplos: `/`, `/public_html/`, `/htdocs/`, etc.
- Click "Add secret"

---

## 📋 PASO 3: Probar el Despliegue

### Opción A: Ejecución Manual (Recomendado para la primera vez)

1. Ve a tu repositorio: https://github.com/ehanseng/tickets_IEEE
2. Click en la pestaña **"Actions"**
3. En el menú izquierdo, click en **"Deploy via FTP to ticket.ieeetadeo.org"**
4. Click en **"Run workflow"** (botón gris a la derecha)
5. Click en **"Run workflow"** (confirmar en el modal)
6. Espera 1-2 minutos

**Resultado:**
- ✅ **Verde** = ¡Funcionó! Los archivos se subieron al servidor
- ❌ **Rojo** = Error. Click en el workflow para ver qué falló

### Opción B: Push Automático

Simplemente haz cambios y push:

```bash
# Hacer un cambio pequeño
echo "" >> README.md

# Commit y push
git add README.md
git commit -m "Test automatic FTP deployment"
git push origin master
```

GitHub automáticamente desplegará al servidor.

---

## 📊 Verificar Estado del Despliegue

### Ver Progreso en Tiempo Real
1. Ve a **"Actions"** en GitHub
2. Verás el workflow ejecutándose (punto amarillo 🟡)
3. Click en él para ver detalles
4. Cuando termine:
   - ✅ Verde = Éxito
   - ❌ Rojo = Error

### Si Hay Errores
Click en el paso que falló para ver el mensaje de error. Errores comunes:

- **"Authentication failed"**: Revisa usuario/contraseña en secretos
- **"Permission denied"**: Revisa la ruta `FTP_REMOTE_PATH`
- **"Connection timeout"**: El servidor FTP puede estar bloqueado

---

## 🎯 ¿Qué Archivos se Subirán?

Se subirán todos los archivos del proyecto **EXCEPTO**:

- `.git/` (control de versiones)
- `tickets.db` (base de datos, se crea en el servidor)
- `qr_codes/*.png` (archivos generados)
- `__pycache__/` (Python cache)
- `.env` (variables de entorno)
- Archivos de documentación de despliegue

---

## ⚙️ Configuración Post-Despliegue en el Servidor

Después del primer despliegue exitoso, necesitas configurar el servidor:

### 1. Crear archivo .env

Conéctate por SSH (si tienes acceso) o usa el File Manager de tu hosting:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu-email@gmail.com
SMTP_PASSWORD=xxxx-xxxx-xxxx-xxxx
FROM_EMAIL=tu-email@gmail.com
FROM_NAME=IEEE Tadeo - Sistema de Tickets
BASE_URL=https://ticket.ieeetadeo.org
```

### 2. Instalar Dependencias (requiere SSH)

```bash
# Instalar uv
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.cargo/env

# Instalar dependencias
cd /ruta/al/directorio
uv sync
```

### 3. Iniciar la Aplicación

```bash
# Opción con uv
uv run uvicorn main:app --host 0.0.0.0 --port 8000

# O con screen para mantenerlo corriendo
screen -S tickets
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2
# Presiona Ctrl+A, luego D para desconectar
```

### 4. Configurar Servidor Web

Si tu hosting usa cPanel, configura una "Python App" que apunte a `main.py`.

Si tienes acceso a Nginx/Apache, configura un proxy reverso (ver DEPLOYMENT.md).

---

## 🔄 Workflow de Desarrollo

### Flujo Normal de Trabajo

```
1. Haces cambios en tu código local
2. git add .
3. git commit -m "Descripción del cambio"
4. git push origin master
5. GitHub automáticamente despliega al servidor
6. ¡Listo! Los cambios están en producción
```

### Actualizar sin Desplegar

Si NO quieres que se despliegue automáticamente con cada push:

1. Edita `.github/workflows/deploy-ftp.yml`
2. Comenta o elimina la sección `push:` en `on:`
3. Mantén solo `workflow_dispatch:` para ejecución manual

---

## ✅ CHECKLIST

- [ ] FileZilla instalado
- [ ] Conectado por FTP y ruta identificada
- [ ] 4 secretos configurados en GitHub (FTP_SERVER, FTP_USERNAME, FTP_PASSWORD, FTP_REMOTE_PATH)
- [ ] Workflow ejecutado manualmente por primera vez
- [ ] Workflow completado exitosamente (✅ verde)
- [ ] Archivos verificados en el servidor
- [ ] Archivo .env creado en el servidor
- [ ] Dependencias instaladas (si tienes SSH)
- [ ] Aplicación corriendo

---

## 🆘 Solución de Problemas

### No puedo conectarme por FTP
- Verifica que el firewall no bloquee puerto 21
- Prueba con un cliente FTP diferente
- Contacta a tu proveedor de hosting

### El workflow falla con "Authentication failed"
- Verifica que los secretos estén correctamente escritos
- Usuario completo: `adminIEEEtadeo@ticket.ieeetadeo.org`
- Contraseña exacta: `Rn5GkEcwQpCE3LK`

### El workflow falla con "Directory not found"
- Revisa `FTP_REMOTE_PATH` en los secretos
- Debe terminar con `/` (ejemplo: `/public_html/`)

### Los archivos se subieron pero la app no funciona
- Necesitas instalar dependencias en el servidor
- Necesitas crear el archivo `.env`
- Necesitas iniciar la aplicación con Python/Uvicorn

---

## 📞 Próximos Pasos

1. ✅ Configura los 4 secretos en GitHub
2. ✅ Ejecuta el workflow manualmente
3. ✅ Verifica que los archivos estén en el servidor
4. ✅ Crea el archivo `.env` en el servidor
5. ✅ Instala dependencias y ejecuta la aplicación

---

**¡Listo! Ahora tienes despliegue continuo automático con GitHub → FTP → Servidor** 🚀

**¿Necesitas ayuda con algún paso?**
