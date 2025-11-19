@echo off
REM =====================================
REM Script de inicialización del proyecto
REM IEEE Tadeo Control System
REM =====================================

title IEEE Tadeo Control System
color 0A

echo.
echo ========================================
echo   IEEE Tadeo Control System
echo   Inicializacion Completa
echo ========================================
echo.
echo Este script iniciara:
echo   [1] Servicio de WhatsApp (puerto 3010)
echo   [2] Cloudflare Tunnel (https://ticket.ieeetadeo.org)
echo   [3] Aplicacion FastAPI (puerto 8010)
echo.
echo ========================================
echo.

REM Verificar que Python está disponible
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python no encontrado. Instala Python 3.13+
    pause
    exit /b 1
)

REM Verificar que Node.js está disponible (para WhatsApp)
where node >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js no encontrado. Instala Node.js para el servicio de WhatsApp
    pause
    exit /b 1
)

REM Verificar que el entorno virtual existe
if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Entorno virtual no encontrado. Creando...
    python -m venv .venv
    echo [INFO] Instalando dependencias...
    .venv\Scripts\python.exe -m pip install -r requirements.txt
)

REM Crear directorios necesarios
echo [1/7] Creando directorios necesarios...
if not exist "qr_codes" mkdir qr_codes
if not exist "static\message_images" mkdir static\message_images
if not exist "static\whatsapp_images" mkdir static\whatsapp_images
if not exist "logs" mkdir logs
echo      [OK] Directorios creados correctamente.
echo.

REM Configurar tarea programada de cumpleaños
echo [2/7] Verificando tarea programada de cumpleanos...
set TASK_NAME=IEEE_Birthday_Checker
schtasks /Query /TN "%TASK_NAME%" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo      [INFO] No se encontro tarea programada de cumpleanos.
    echo      [INFO] Configurando tarea automatica (diaria a las 9:00 AM)
    echo      [WARN] No se pudo crear automaticamente. Ejecuta: setup_daily_birthday_task.bat
) else (
    echo      [OK] Tarea programada ya configurada.
)
echo.

REM Verificar dependencias
echo [3/7] Verificando dependencias Python...
echo      [OK] Dependencias listas.
echo.

REM Iniciar servicio de WhatsApp en segundo plano
echo [4/7] Iniciando servicio de WhatsApp (puerto 3010)...
cd whatsapp-service 2>nul
if %ERRORLEVEL% EQU 0 (
    REM Instalar dependencias de Node.js si no existen
    if not exist "node_modules" (
        echo      [INFO] Instalando dependencias de Node.js...
        call npm install --silent
    )
    start "WhatsApp Service - IEEE Tadeo" cmd /k "echo [WhatsApp Service] Iniciando... && node server.js"
    echo      [OK] Servicio de WhatsApp iniciado en segundo plano.
    echo      [INFO] Ventana separada abierta - Escanea el QR si es la primera vez
    cd ..
) else (
    echo      [WARN] No se encontro el directorio whatsapp-service
    echo      [INFO] Asegurate de iniciar el servicio de WhatsApp manualmente si lo necesitas.
)
echo.

REM Iniciar túnel de Cloudflare
echo [5/7] Iniciando Cloudflare Tunnel...
where cloudflared >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    start "Cloudflare Tunnel - IEEE Tadeo" cmd /k "echo [Cloudflare Tunnel] Iniciando... && cloudflared tunnel run --token eyJhIjoiODU2NGNiMzE2YTgxNTM0ZTAyYTc5Y2MxNTgwZDRiOTUiLCJzIjoiUnZINFFrc29sZS9OYUVaK0UrYzRQUFVJRU1GOThyM3JseGNEeXl6SE9jWT0iLCJ0IjoiYWJiYTgxYjYtZjVlOS00ZTA3LWI0NTItZmZmNWNhOWVhNmU0In0="
    echo      [OK] Cloudflare Tunnel iniciado en segundo plano.
    echo      [INFO] URL publica: https://ticket.ieeetadeo.org
) else (
    echo      [WARN] cloudflared no encontrado.
    echo      [INFO] Instala desde: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/
    echo      [INFO] Aplicacion solo accesible localmente en: http://localhost:8010
)
echo.

REM Esperar un momento para que los servicios inicien
echo [6/7] Esperando a que los servicios inicien...
timeout /t 5 /nobreak >nul
echo      [OK] Servicios listos.
echo.

REM Iniciar aplicación FastAPI
echo [7/7] Iniciando aplicacion FastAPI (puerto 8010)...
echo.
echo ========================================
echo   ^|^| TODOS LOS SERVICIOS INICIADOS ^|^|
echo ========================================
echo.
echo   URLs del sistema:
echo   -----------------
echo   ^> URL Publica:  https://ticket.ieeetadeo.org
echo   ^> Panel Admin:  https://ticket.ieeetadeo.org/admin
echo   ^> API Docs:     https://ticket.ieeetadeo.org/docs
echo   ^> WhatsApp API: http://localhost:3010/status
echo.
echo   Credenciales por defecto:
echo   -------------------------
echo   Usuario: admin
echo   Password: admin123
echo.
echo   Sistema de Cumpleanos:
echo   ----------------------
echo   ^> Tarea programada: Diaria a las 9:00 AM
echo   ^> Ver estado en: Panel Admin ^> Usuarios
echo.
echo   [INFO] Presiona Ctrl+C para detener todos los servicios
echo ========================================
echo.
echo Logs de FastAPI:
echo ----------------

REM Ejecutar la aplicación (esto bloqueará hasta que se detenga)
.venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8010 --reload

REM Al cerrar este script, cerrar también las otras ventanas
echo.
echo.
echo ========================================
echo   Cerrando servicios...
echo ========================================
echo.
echo [INFO] Deteniendo WhatsApp Service...
taskkill /FI "WindowTitle eq WhatsApp Service - IEEE Tadeo*" /T /F 2>nul
echo [INFO] Deteniendo Cloudflare Tunnel...
taskkill /FI "WindowTitle eq Cloudflare Tunnel - IEEE Tadeo*" /T /F 2>nul
echo.
echo [OK] Todos los servicios han sido detenidos.
echo.
pause
