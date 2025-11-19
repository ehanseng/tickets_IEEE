@echo off
REM =====================================
REM Script para detener todos los servicios
REM IEEE Tadeo Control System
REM =====================================

title IEEE Tadeo Control System - STOP
color 0C

echo.
echo ========================================
echo   IEEE Tadeo Control System
echo   Deteniendo Todos los Servicios
echo ========================================
echo.

echo [1/4] Deteniendo aplicacion FastAPI...
REM Matar procesos de uvicorn en el puerto 8010
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8010 ^| findstr LISTENING') do (
    echo      [INFO] Deteniendo proceso FastAPI (PID: %%a)
    taskkill /PID %%a /F >nul 2>&1
)
echo      [OK] FastAPI detenido.
echo.

echo [2/4] Deteniendo servicio de WhatsApp...
REM Matar ventana de WhatsApp Service por título
taskkill /FI "WindowTitle eq WhatsApp Service - IEEE Tadeo*" /T /F >nul 2>&1
REM También buscar procesos de node en puerto 3010
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :3010 ^| findstr LISTENING') do (
    echo      [INFO] Deteniendo proceso WhatsApp (PID: %%a)
    taskkill /PID %%a /F >nul 2>&1
)
echo      [OK] WhatsApp Service detenido.
echo.

echo [3/4] Deteniendo Cloudflare Tunnel...
REM Matar ventana de Cloudflare por título
taskkill /FI "WindowTitle eq Cloudflare Tunnel - IEEE Tadeo*" /T /F >nul 2>&1
REM También matar procesos de cloudflared
taskkill /IM cloudflared.exe /F >nul 2>&1
echo      [OK] Cloudflare Tunnel detenido.
echo.

echo [4/4] Limpiando procesos residuales...
REM Matar cualquier proceso de Python que esté ejecutando uvicorn
for /f "tokens=2" %%a in ('tasklist /FI "IMAGENAME eq python.exe" /FO LIST ^| findstr PID') do (
    REM Verificar si el proceso tiene "uvicorn" en la línea de comandos
    wmic process where "ProcessId=%%a" get CommandLine 2>nul | findstr /I "uvicorn" >nul
    if !ERRORLEVEL! EQU 0 (
        echo      [INFO] Deteniendo proceso Python/Uvicorn (PID: %%a)
        taskkill /PID %%a /F >nul 2>&1
    )
)
echo      [OK] Limpieza completada.
echo.

echo ========================================
echo   TODOS LOS SERVICIOS DETENIDOS
echo ========================================
echo.
echo [INFO] Sistema completamente detenido.
echo [INFO] Para reiniciar, ejecuta: start.bat
echo.

pause
