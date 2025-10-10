# 🤖 Configuración de Despliegue Automático desde GitHub

## 🎯 Objetivo
Cada vez que hagas `git push` a GitHub, automáticamente se subirán los archivos a tu servidor por SFTP.

---

## ✅ Archivos Creados

Se han creado dos workflows de GitHub Actions:

1. **`.github/workflows/deploy.yml`** - Deploy via FTP/FTPS
2. **`.github/workflows/deploy-sftp.yml`** - Deploy via SFTP (SSH) - **RECOMENDADO**

Usaremos el segundo (SFTP) porque es más seguro y funciona mejor.

---

## 📋 Paso 1: Configurar Secretos en GitHub

### 1.1 Ir a tu Repositorio
Ve a: https://github.com/ehanseng/tickets_IEEE

### 1.2 Abrir Configuración de Secretos
1. Click en **"Settings"** (arriba a la derecha)
2. En el menú izquierdo, click en **"Secrets and variables"**
3. Click en **"Actions"**
4. Click en **"New repository secret"**

### 1.3 Agregar los Siguientes Secretos

#### Secreto 1: SFTP_SERVER
- **Name**: `SFTP_SERVER`
- **Value**: `72.167.151.233`
- Click "Add secret"

#### Secreto 2: SFTP_USERNAME
- **Name**: `SFTP_USERNAME`
- **Value**: `svrvpsefjkcv`
- Click "Add secret"

#### Secreto 3: SFTP_PASSWORD
- **Name**: `SFTP_PASSWORD`
- **Value**: `OzsO$n63ddME`
- Click "Add secret"

#### Secreto 4: SFTP_REMOTE_PATH
- **Name**: `SFTP_REMOTE_PATH`
- **Value**: Aquí debes poner la ruta exacta en tu servidor

**⚠️ IMPORTANTE**: Necesitas averiguar la ruta exacta. Opciones comunes:
```
/home/ieeetadeo2006/public_html/ticket/
/home/ieeetadeo2006/domains/ieeetadeo.org/public_html/ticket/
/var/www/html/ieeetadeo.org/ticket/
```

**¿Cómo averiguar la ruta?**
1. Conéctate por SFTP con FileZilla usando los datos:
   - Host: `sftp://72.167.151.233`
   - Usuario: `svrvpsefjkcv`
   - Contraseña: `OzsO$n63ddME`
   - Puerto: 22

2. Navega hasta encontrar la carpeta del dominio `ieeetadeo.org` y dentro la carpeta `ticket`

3. En FileZilla, arriba verás la ruta completa. Cópiala.

4. Usa esa ruta completa como valor de `SFTP_REMOTE_PATH`

---

## 📋 Paso 2: Subir los Workflows a GitHub

### 2.1 Hacer Commit de los Workflows
```bash
cd "e:\erick\Documents\Personal\UTadeo\IEEE\Proyectos\Ticket"

git add .github/workflows/

git commit -m "Add automatic SFTP deployment workflow"

git push origin master
```

---

## 📋 Paso 3: Probar el Despliegue Automático

### Opción A: Hacer un Cambio y Push
```bash
# Hacer un cambio pequeño (por ejemplo, editar README.md)
echo "" >> README.md

git add README.md
git commit -m "Test automatic deployment"
git push origin master
```

### Opción B: Ejecutar Manualmente desde GitHub
1. Ve a tu repositorio: https://github.com/ehanseng/tickets_IEEE
2. Click en la pestaña **"Actions"**
3. En el menú izquierdo, click en **"Deploy to Server via SFTP (SSH)"**
4. Click en **"Run workflow"** (botón azul a la derecha)
5. Click en **"Run workflow"** (confirmar)

---

## 📋 Paso 4: Verificar que Funcionó

### 4.1 Ver el Progreso
1. Ve a la pestaña **"Actions"** en GitHub
2. Verás el workflow ejecutándose (punto amarillo)
3. Click en el workflow para ver detalles
4. Si todo está bien, verás ✅ verde

### 4.2 Revisar Errores (si los hay)
Si falla (❌ rojo):
1. Click en el workflow fallido
2. Click en el job "SFTP Deploy to Production"
3. Lee el error y ajusta los secretos si es necesario

---

## 🔧 Configuraciones Opcionales

### Desplegar Solo Archivos Específicos

Si quieres excluir más archivos, edita `.github/workflows/deploy-sftp.yml` y cambia:

```yaml
local_path: './*'
```

Por algo más específico como:

```yaml
local_path: './+(main.py|models.py|schemas.py|database.py|ticket_service.py|templates|static|pyproject.toml|uv.lock|requirements.txt)'
```

### Usar SSH Key en lugar de Contraseña (Más Seguro)

Si tienes una llave SSH privada para el servidor:

1. Abre tu llave privada (archivo `id_rsa` o similar)
2. Copia TODO el contenido (incluido `-----BEGIN RSA PRIVATE KEY-----` y `-----END RSA PRIVATE KEY-----`)
3. Crea un nuevo secreto en GitHub:
   - **Name**: `SSH_PRIVATE_KEY`
   - **Value**: Pega la llave completa
4. Edita `.github/workflows/deploy-sftp.yml` y comenta la línea `password`:

```yaml
# password: ${{ secrets.SFTP_PASSWORD }}  # Comentar esta línea
ssh_private_key: ${{ secrets.SSH_PRIVATE_KEY }}  # Usar esta en su lugar
```

---

## 📊 Resultado Final

### ✅ Cada vez que hagas:
```bash
git add .
git commit -m "Tu mensaje"
git push origin master
```

**GitHub automáticamente:**
1. ✅ Detecta el push
2. ✅ Ejecuta el workflow
3. ✅ Se conecta a tu servidor por SFTP
4. ✅ Sube todos los archivos actualizados
5. ✅ Mantiene sincronizado GitHub ↔️ Servidor

---

## ⚠️ IMPORTANTE: Archivos Excluidos

Los siguientes archivos **NO se subirán** al servidor (por seguridad):
- `.git/` (control de versiones)
- `tickets.db` (base de datos, se genera en el servidor)
- `qr_codes/*.png` (archivos generados)
- `__pycache__/` (archivos Python compilados)
- `.env` (variables de entorno, configúralo manualmente en el servidor)
- Scripts de despliegue local

**Debes crear manualmente en el servidor:**
- `.env` con tus credenciales SMTP

---

## 🔄 Actualización Manual del .env en el Servidor

Después del primer despliegue automático, conéctate al servidor y crea `.env`:

```bash
ssh svrvpsefjkcv@72.167.151.233
cd /ruta/al/directorio/ticket
nano .env
```

Pega:
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu-email@gmail.com
SMTP_PASSWORD=xxxx-xxxx-xxxx-xxxx
FROM_EMAIL=tu-email@gmail.com
FROM_NAME=IEEE Tadeo - Sistema de Tickets
BASE_URL=https://ticket.ieeetadeo.org
```

Guarda con `Ctrl+O`, `Enter`, `Ctrl+X`

---

## 📞 Próximos Pasos Después del Primer Despliegue

Una vez que los archivos estén en el servidor:

1. **Instalar dependencias** (solo primera vez):
```bash
ssh svrvpsefjkcv@72.167.151.233
cd /ruta/al/directorio/ticket
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.cargo/env
uv sync
```

2. **Iniciar la aplicación**:
```bash
uv run uvicorn main:app --host 0.0.0.0 --port 8000
```

3. **Configurar auto-inicio** con systemd o screen (ver DEPLOYMENT.md)

---

## ✅ CHECKLIST

- [ ] Secretos configurados en GitHub (SFTP_SERVER, SFTP_USERNAME, SFTP_PASSWORD, SFTP_REMOTE_PATH)
- [ ] Workflows subidos a GitHub (.github/workflows/)
- [ ] Primer push realizado
- [ ] Workflow ejecutado exitosamente en GitHub Actions
- [ ] Archivos verificados en el servidor
- [ ] Archivo .env creado manualmente en el servidor
- [ ] Dependencias instaladas en el servidor
- [ ] Aplicación iniciada y funcionando

---

## 🎉 ¡Listo!

Ahora cada vez que hagas cambios en tu código local y hagas `git push`, GitHub automáticamente los subirá a tu servidor.

**Workflow:**
```
Código Local → Git Push → GitHub → SFTP → Servidor → ✅
```

---

**¿Dudas? Avísame y te ayudo a configurar cada paso!** 🚀
