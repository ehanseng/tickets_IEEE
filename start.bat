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
echo   [1] Servicio de WhatsApp (puerto 3000)
echo   [2] Tunel publico (localtunnel o ngrok)
echo   [3] Aplicacion FastAPI (puerto 8000)
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

REM Verificar que uv está disponible
where uv >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] uv no encontrado. Instala uv con: pip install uv
    pause
    exit /b 1
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
    echo      [INFO] Configurando tarea automatica (diaria a las 9:00 AM)...

    set SCRIPT_DIR=%~dp0
    set SCRIPT_DIR=%SCRIPT_DIR:~0,-1%

    schtasks /Create /TN "%TASK_NAME%" /TR "cmd /c cd /d \"%SCRIPT_DIR%\" && uv run python birthday_checker.py >> logs\birthday_checker.log 2>&1" /SC DAILY /ST 09:00 /F >nul 2>&1

    if %ERRORLEVEL% EQU 0 (
        echo      [OK] Tarea programada creada exitosamente!
        echo      [INFO] Verificacion de cumpleanos: Diariamente a las 9:00 AM
    ) else (
        echo      [WARN] No se pudo crear la tarea programada automaticamente.
        echo      [INFO] Puedes crearla manualmente ejecutando: setup_daily_birthday_task.bat
    )
) else (
    echo      [OK] Tarea programada ya configurada.
)
echo.

REM Sincronizar dependencias
echo [3/7] Sincronizando dependencias Python...
call uv sync --quiet
if %ERRORLEVEL% NEQ 0 (
    echo      [ERROR] Fallo al sincronizar dependencias
    pause
    exit /b 1
)
echo      [OK] Dependencias sincronizadas correctamente.
echo.

REM Iniciar servicio de WhatsApp en segundo plano
echo [4/7] Iniciando servicio de WhatsApp (puerto 3000)...
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

REM Iniciar túnel público
echo [5/7] Iniciando tunel publico (puerto 8000)...
echo.
echo      Opciones de tunel:
echo      [1] localtunnel (gratuito, rapido)
echo      [2] ngrok (requiere cuenta, mas estable)
echo      [3] Omitir tunel (solo local)
echo.
set /p TUNNEL_CHOICE="      Elige una opcion (1/2/3): "

if "%TUNNEL_CHOICE%"=="1" (
    where npx >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        start "Localtunnel - IEEE Tadeo" cmd /k "echo [Localtunnel] Iniciando tunel... && npx localtunnel --port 8000"
        echo      [OK] Localtunnel iniciado en segundo plano.
        echo      [INFO] Copia la URL que aparece en la ventana separada
    ) else (
        echo      [ERROR] npx no encontrado. Instala Node.js.
    )
) else if "%TUNNEL_CHOICE%"=="2" (
    where ngrok >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        start "Ngrok - IEEE Tadeo" cmd /k "echo [Ngrok] Iniciando tunel... && ngrok http 8000"
        echo      [OK] Ngrok iniciado en segundo plano.
        echo      [INFO] Copia la URL que aparece en la ventana separada
    ) else (
        echo      [ERROR] ngrok no encontrado. Instala desde: https://ngrok.com/download
    )
) else (
    echo      [INFO] Omitiendo tunel. Aplicacion solo accesible localmente.
)
echo.

REM Esperar un momento para que los servicios inicien
echo [6/7] Esperando a que los servicios inicien...
timeout /t 5 /nobreak >nul
echo      [OK] Servicios listos.
echo.

REM Iniciar aplicación FastAPI
echo [7/7] Iniciando aplicacion FastAPI (puerto 8000)...
echo.
echo ========================================
echo   ^|^| TODOS LOS SERVICIOS INICIADOS ^|^|
echo ========================================
echo.
echo   URLs del sistema:
echo   -----------------
echo   ^> Panel Admin:  http://localhost:8000/admin
echo   ^> API Docs:     http://localhost:8000/docs
echo   ^> WhatsApp API: http://localhost:3000/status
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
call uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload

REM Al cerrar este script, cerrar también las otras ventanas
echo.
echo.
echo ========================================
echo   Cerrando servicios...
echo ========================================
echo.
echo [INFO] Deteniendo WhatsApp Service...
taskkill /FI "WindowTitle eq WhatsApp Service - IEEE Tadeo*" /T /F 2>nul
echo [INFO] Deteniendo Localtunnel...
taskkill /FI "WindowTitle eq Localtunnel - IEEE Tadeo*" /T /F 2>nul
echo [INFO] Deteniendo Ngrok...
taskkill /FI "WindowTitle eq Ngrok - IEEE Tadeo*" /T /F 2>nul
echo.
echo [OK] Todos los servicios han sido detenidos.
echo.
pause
