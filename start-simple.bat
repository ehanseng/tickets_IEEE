@echo off
REM =====================================
REM Script simplificado - Solo FastAPI
REM IEEE Tadeo Control System
REM =====================================

title IEEE Tadeo Control System - FastAPI
color 0B

echo.
echo ========================================
echo   IEEE Tadeo Control System
echo   Modo: Solo FastAPI (sin WhatsApp/Tunel)
echo ========================================
echo.

REM Crear directorios
if not exist "qr_codes" mkdir qr_codes
if not exist "static\message_images" mkdir static\message_images

REM Sincronizar dependencias
echo Sincronizando dependencias...
call uv sync
echo.

REM Iniciar aplicación
echo Iniciando aplicacion FastAPI...
echo.
echo Aplicacion disponible en: http://localhost:8000
echo Admin panel: http://localhost:8000/admin
echo.
echo Presiona Ctrl+C para detener
echo.

call uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload

pause
