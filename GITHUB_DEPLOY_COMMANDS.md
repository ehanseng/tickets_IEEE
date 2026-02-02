# 🚀 Flujo de Despliegue con GitHub

Este proyecto usa **GitHub + Túnel SSH** para el despliegue. No se usa SFTP ni FTP.

## 📋 Flujo de Trabajo

### 1. Desarrollo Local

```bash
# Hacer cambios en tu código local
# Probar localmente
uv run uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### 2. Commit y Push a GitHub

```bash
# Agregar cambios
git add .

# Hacer commit
git commit -m "Descripción de los cambios"

# Push a GitHub
git push origin master
```

### 3. Actualizar en el Servidor

```bash
# Conectar al servidor vía SSH
ssh svrvpsefjkcv@72.167.151.233

# Cambiar al usuario correcto (si es necesario)
sudo su - ieeetadeo2006

# Ir al directorio del proyecto
cd ~/domains/ieeetadeo.org/public_html/ticket

# Obtener últimos cambios de GitHub
git pull origin master

# Si hay nuevas dependencias, actualizar
uv sync

# Reiniciar el servidor
screen -X -S tickets quit
screen -S tickets
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2
# Presiona Ctrl+A luego D para desconectar
```

## 🔧 Comandos Útiles

### Ver logs del servidor

```bash
# Reconectar a la sesión screen
screen -r tickets

# Salir sin matar el servidor
# Presiona Ctrl+A luego D
```

### Verificar estado

```bash
# Ver si el servidor está corriendo
ps aux | grep uvicorn

# Ver qué proceso usa el puerto 8000
netstat -tulpn | grep :8000
# o
lsof -i :8000
```

### Reiniciar el servidor

```bash
# Matar el servidor actual
screen -X -S tickets quit

# Iniciar de nuevo
screen -S tickets
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2
# Ctrl+A, D
```

## 🔄 Migrar Base de Datos

Cuando hay cambios en el modelo de datos:

```bash
# Conectar al servidor
ssh svrvpsefjkcv@72.167.151.233
sudo su - ieeetadeo2006
cd ~/domains/ieeetadeo.org/public_html/ticket

# Ejecutar script de migración
uv run python migrate_add_birthday.py
# o el nombre del script de migración correspondiente
```

## 🎂 Configurar Correos de Cumpleaños (Cron Job)

```bash
# Editar crontab
crontab -e

# Agregar esta línea para enviar correos a las 8:00 AM diariamente
0 8 * * * cd ~/domains/ieeetadeo.org/public_html/ticket && ~/.cargo/bin/uv run python birthday_checker.py >> ~/domains/ieeetadeo.org/public_html/ticket/birthday_logs.txt 2>&1

# Guardar y salir (Ctrl+O, Enter, Ctrl+X)

# Verificar que se guardó
crontab -l

# Ver logs de cumpleaños
tail -f ~/domains/ieeetadeo.org/public_html/ticket/birthday_logs.txt
```

## 📝 Notas Importantes

- **Siempre usa GitHub** para subir cambios, no SFTP ni FTP
- **Haz commit localmente** antes de probar en el servidor
- **Prueba primero local** antes de push a GitHub
- El servidor usa **túnel SSH** para acceso desde fuera
- La base de datos **MySQL** está en el servidor y se configura mediante variables de entorno en `.env`

## ❌ Solución de Problemas

### Error: git pull falla con conflictos

```bash
# Ver estado
git status

# Si hay cambios locales no deseados, descartarlos
git reset --hard origin/master

# Si hay cambios importantes, hacer stash
git stash
git pull origin master
git stash pop
```

### Error: Puerto 8000 ocupado

```bash
# Matar proceso en puerto 8000
screen -X -S tickets quit

# O encontrar PID y matar
lsof -i :8000
kill -9 <PID>
```

### Error: No se encuentran módulos

```bash
# Reinstalar dependencias
uv sync

# O forzar reinstalación
rm -rf .venv
uv sync
```

## ✅ Checklist de Despliegue

- [ ] Cambios probados localmente
- [ ] Commit hecho con mensaje descriptivo
- [ ] Push a GitHub exitoso
- [ ] Conectado al servidor vía SSH
- [ ] `git pull` ejecutado en el servidor
- [ ] Migraciones ejecutadas (si aplica)
- [ ] Servidor reiniciado
- [ ] Verificado en el navegador que funciona

---

**¿Necesitas ayuda?** Revisa los logs del servidor con `screen -r tickets` o los logs de cumpleaños con `tail -f birthday_logs.txt`
