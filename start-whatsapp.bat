@echo off
REM =====================================
REM Iniciar Servicio de WhatsApp
REM IEEE Tadeo Control System
REM =====================================

title WhatsApp Service - IEEE Tadeo Control System
color 0E

echo.
echo ========================================
echo   IEEE Tadeo Control System
echo   Servicio de WhatsApp
echo ========================================
echo.

REM Verificar que Node.js está instalado
where node >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js no encontrado.
    echo Por favor, instala Node.js desde: https://nodejs.org/
    pause
    exit /b 1
)

REM Verificar que el directorio existe
if not exist "whatsapp-service" (
    echo [ERROR] No se encuentra el directorio whatsapp-service
    echo Asegurate de estar en la raiz del proyecto
    pause
    exit /b 1
)

REM Ir al directorio del servicio
cd whatsapp-service

REM Verificar que existen las dependencias
if not exist "node_modules" (
    echo [INFO] Instalando dependencias de Node.js...
    call npm install
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Fallo al instalar dependencias
        pause
        exit /b 1
    )
    echo [OK] Dependencias instaladas correctamente
    echo.
)

REM Crear directorio para sesión de WhatsApp
if not exist "whatsapp-session" mkdir whatsapp-session

REM Crear directorio para imágenes
if not exist "..\static\whatsapp_images" mkdir ..\static\whatsapp_images

echo [OK] Iniciando servicio de WhatsApp...
echo.
echo ========================================
echo   INSTRUCCIONES:
echo ========================================
echo.
echo 1. Espera a que aparezca el codigo QR
echo 2. Abre WhatsApp en tu telefono
echo 3. Ve a: Configuracion ^> Dispositivos vinculados
echo 4. Toca "Vincular un dispositivo"
echo 5. Escanea el codigo QR que aparece abajo
echo.
echo Servicio corriendo en: http://localhost:3000
echo.
echo Endpoints disponibles:
echo   - GET  http://localhost:3000/status
echo   - POST http://localhost:3000/send
echo   - POST http://localhost:3000/send-media
echo   - POST http://localhost:3000/send-bulk
echo.
echo Presiona Ctrl+C para detener
echo ========================================
echo.

REM Ejecutar el servidor
node server.js

REM Volver al directorio raíz al cerrar
cd ..
pause
