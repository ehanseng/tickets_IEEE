# Guía de Migración - Sistema de Tickets IEEE

Esta guía te ayudará a configurar el proyecto en un nuevo computador con Visual Studio.

## Repositorio GitHub
**URL**: https://github.com/ehanseng/tickets_IEEE.git

---

## Pasos para Migración

### 1. Instalar Software Necesario

#### En el nuevo computador, instala:

1. **Visual Studio 2022** (Community, Professional o Enterprise)
   - Asegúrate de incluir "Python development" workload

2. **Python 3.11 o superior**
   - Descarga desde: https://www.python.org/downloads/
   - Durante instalación: marca "Add Python to PATH"

3. **Git**
   - Descarga desde: https://git-scm.com/download/win
   - Usa configuración por defecto

4. **Google Chrome** (requerido para WhatsApp automation)
   - Descarga desde: https://www.google.com/chrome/

### 2. Clonar el Repositorio

Abre una terminal (PowerShell o CMD) y ejecuta:

```bash
# Navega a donde quieres guardar el proyecto
cd C:\Users\TuUsuario\Documents

# Clona el repositorio
git clone https://github.com/ehanseng/tickets_IEEE.git

# Entra al directorio
cd tickets_IEEE
```

### 3. Configurar el Entorno Virtual

```bash
# Crear entorno virtual
python -m venv .venv

# Activar el entorno virtual
.venv\Scripts\activate

# Actualizar pip
python -m pip install --upgrade pip

# Instalar dependencias
pip install -r requirements.txt
```

### 4. Transferir Archivos de Datos (IMPORTANTE)

Los siguientes archivos NO están en GitHub y DEBES copiarlos manualmente desde el computador viejo:

#### Archivos críticos a copiar:

1. **Base de datos**:
   - `tickets.db` (contiene todos los usuarios, tickets, campañas)

2. **Archivo de configuración**:
   - `.env` (contiene credenciales y configuración)

3. **Cloudflare Tunnel** (si usas el túnel):
   - `cloudflared.exe`
   - Archivo de configuración del túnel (si existe)

#### Cómo copiarlos:

**Opción A**: USB o disco externo
- Copia estos archivos a USB
- Pégalos en la raíz del proyecto clonado

**Opción B**: Red local
- Comparte la carpeta del proyecto viejo en la red
- Copia los archivos directamente

**Opción C**: Nube (OneDrive, Google Drive)
- Sube los archivos a la nube
- Descárgalos en el nuevo computador

### 5. Crear Archivo .env

Si no tienes el archivo `.env`, créalo con este contenido:

```env
# Configuración de la aplicación
SECRET_KEY=tu_clave_secreta_aqui_cambiala
DATABASE_URL=sqlite:///./tickets.db

# Credenciales de admin por defecto
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123

# Cloudflare Tunnel (opcional)
CLOUDFLARE_TUNNEL_TOKEN=tu_token_aqui
```

### 6. Iniciar la Aplicación

```bash
# Asegúrate de que el entorno virtual está activo
.venv\Scripts\activate

# Inicia el servidor
python main.py
```

La aplicación estará disponible en: http://localhost:8000

### 7. Configurar WhatsApp (Primer uso)

1. Abre: http://localhost:8000/admin/whatsapp
2. Haz clic en "Conectar WhatsApp"
3. Escanea el código QR con tu teléfono
4. Espera a que se conecte

**NOTA**: La sesión de WhatsApp NO se puede transferir. Debes escanear el QR nuevamente.

### 8. Configurar Cloudflare Tunnel (Opcional)

Si quieres acceso desde internet:

```bash
# Instala cloudflared
# Descarga desde: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/

# Ejecuta el tunnel
cloudflared tunnel run --url http://localhost:8000
```

O usa `start.bat` si ya tienes la configuración.

---

## Estructura del Proyecto

```
tickets_IEEE/
├── main.py                 # Aplicación principal FastAPI
├── whatsapp_client.py      # Cliente de WhatsApp
├── schemas.py              # Modelos de datos
├── requirements.txt        # Dependencias Python
├── .env                    # Configuración (NO en git)
├── tickets.db              # Base de datos (NO en git)
├── templates/              # Plantillas HTML
├── static/                 # Archivos estáticos
└── logs/                   # Logs de la aplicación
```

---

## Verificación de la Instalación

### Checklist:

- [ ] Python instalado y en PATH
- [ ] Git configurado
- [ ] Repositorio clonado
- [ ] Entorno virtual creado y activado
- [ ] Dependencias instaladas (`pip list` muestra paquetes)
- [ ] Archivo `.env` configurado
- [ ] Base de datos `tickets.db` copiada
- [ ] Servidor inicia sin errores (`python main.py`)
- [ ] Puedes acceder a http://localhost:8000
- [ ] Login funciona con admin/admin123
- [ ] WhatsApp conectado (si es necesario)

---

## Comandos Útiles

```bash
# Ver estado de git
git status

# Actualizar desde GitHub
git pull origin master

# Ver logs de la aplicación
type logs\app.log

# Listar paquetes instalados
pip list

# Reinstalar dependencias
pip install -r requirements.txt --force-reinstall
```

---

## Solución de Problemas Comunes

### Error: "Python no se reconoce como comando"
- Reinstala Python y marca "Add to PATH"
- O agrega manualmente: `C:\Python311\` y `C:\Python311\Scripts\`

### Error: "No module named 'fastapi'"
- Activa el entorno virtual: `.venv\Scripts\activate`
- Reinstala: `pip install -r requirements.txt`

### Error: "Database locked"
- Cierra todas las instancias de la aplicación
- Verifica que no haya otro proceso usando `tickets.db`

### WhatsApp no se conecta
- Asegúrate de tener Chrome instalado
- Elimina carpeta `whatsapp-session` y vuelve a escanear QR
- Verifica que el teléfono esté conectado a internet

### No puedo acceder desde internet
- Verifica que Cloudflare Tunnel esté corriendo
- Revisa los puertos del firewall (8000)
- Usa el tunnel URL que proporciona cloudflared

---

## Contacto y Soporte

- **Repositorio**: https://github.com/ehanseng/tickets_IEEE.git
- **Issues**: https://github.com/ehanseng/tickets_IEEE/issues

---

## Notas Importantes

1. **NO compartas** el archivo `.env` públicamente
2. **Haz backups** regulares de `tickets.db`
3. **Mantén actualizado** el código con `git pull`
4. **Usa entorno virtual** siempre que trabajes en el proyecto
5. **La sesión de WhatsApp** debe configurarse en cada computador

---

Última actualización: 2025-10-17
