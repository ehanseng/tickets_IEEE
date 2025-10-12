# 🚀 Pasos Manuales de Despliegue en ticket.ieeetadeo.org

## 📋 Información del Servidor
- **IP**: 72.167.151.233
- **Usuario**: svrvpsefjkcv
- **Dominio**: ticket.ieeetadeo.org

---

## Paso 1: Conectarse al Servidor

Abre tu terminal (PowerShell, CMD, o Git Bash) y ejecuta:

```bash
ssh svrvpsefjkcv@72.167.151.233
```

Cuando pida contraseña, ingresa: `OzsO$n63ddME`

---

## Paso 2: Explorar y Encontrar la Carpeta Correcta

Una vez conectado, ejecuta estos comandos para encontrar dónde está la carpeta del dominio:

```bash
# Ver dónde estás
pwd

# Ver contenido del directorio actual
ls -la

# Buscar carpetas típicas de hosting
ls -la ~ | grep -E 'public_html|www|domains|httpdocs|htdocs'

# Buscar específicamente ieeetadeo
find ~ -maxdepth 3 -type d -name '*ieeetadeo*' 2>/dev/null

# Buscar carpeta ticket
find ~ -maxdepth 3 -type d -name 'ticket' 2>/dev/null
```

**📝 IMPORTANTE**: Anota la ruta completa donde encontraste la carpeta `ticket` dentro de `ieeetadeo.org`

Ejemplo posible:
- `~/domains/ieeetadeo.org/public_html/ticket`
- `~/public_html/ieeetadeo.org/ticket`
- `~/www/ieeetadeo.org/ticket`

---

## Paso 3: Ir a la Carpeta Correcta

Reemplaza `RUTA_ENCONTRADA` con la ruta que encontraste:

```bash
cd RUTA_ENCONTRADA
pwd  # Verificar que estás en el lugar correcto
```

---

## Paso 4: Verificar Software Disponible

```bash
# Verificar Python
which python3
python3 --version

# Verificar Git
which git
git --version

# Verificar permisos sudo
sudo -l

# Verificar si existe uv
which uv
```

**Copia los resultados de estos comandos y pégalos en el chat para continuar**

---

## Paso 5: Clonar el Repositorio (Ejecutar después de confirmar la ruta)

```bash
# Hacer backup de cualquier contenido existente (si hay)
ls -la
# Si hay archivos, hacer backup:
# mkdir ~/backup_ticket_$(date +%Y%m%d)
# cp -r * ~/backup_ticket_$(date +%Y%m%d)/

# Clonar el repositorio de GitHub
git clone https://github.com/ehanseng/tickets_IEEE.git .

# O si la carpeta no está vacía:
cd ..
rm -rf ticket  # ¡CUIDADO! Solo si estás seguro
mkdir ticket
cd ticket
git clone https://github.com/ehanseng/tickets_IEEE.git .
```

---

## Paso 6: Verificar que se Clonó Correctamente

```bash
ls -la
# Deberías ver archivos como: main.py, models.py, templates/, etc.
```

---

## 🔄 Próximos Pasos Después de la Exploración

Una vez que me confirmes:
1. ✅ La ruta exacta donde está la carpeta `ticket`
2. ✅ La versión de Python disponible
3. ✅ Si tienes permisos sudo
4. ✅ Qué servidor web usa (Nginx, Apache, etc.)

Podré proporcionarte los comandos exactos para:
- Instalar dependencias
- Configurar el entorno
- Configurar el servicio
- Configurar SSL

---

## 📞 Mientras Tanto

Ejecuta los comandos del **Paso 2** y **Paso 4**, y pega aquí los resultados para que pueda preparar los siguientes pasos específicos para tu configuración.
