@echo off
chcp 65001 >nul
echo ========================================
echo IEEE Tadeo Control System
echo Configuracion de Tarea Programada
echo ========================================
echo.
echo Este script configurara una tarea programada de Windows
echo para ejecutar la verificacion de cumpleanos diariamente.
echo.

set SCRIPT_DIR=%~dp0
set SCRIPT_DIR=%SCRIPT_DIR:~0,-1%

echo [INFO] Directorio del proyecto: %SCRIPT_DIR%
echo.

REM Verificar si uv esta instalado
where uv >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] 'uv' no esta instalado o no esta en el PATH
    echo        Por favor instala uv primero: https://docs.astral.sh/uv/
    pause
    exit /b 1
)

echo [OK] UV encontrado
echo.

REM Preguntar la hora de ejecucion
echo A que hora deseas que se ejecute la verificacion diaria?
echo (Formato 24 horas, ejemplo: 09:00 para las 9 AM)
set /p HORA="Ingresa la hora (HH:MM): "

if "%HORA%"=="" (
    set HORA=09:00
    echo [INFO] Usando hora por defecto: 09:00
)

echo.
echo [INFO] La tarea se ejecutara diariamente a las %HORA%
echo.

REM Crear el comando para la tarea programada
set TASK_NAME=IEEE_Birthday_Checker
set PYTHON_SCRIPT=%SCRIPT_DIR%\birthday_checker.py

echo [INFO] Creando tarea programada...
echo        Nombre: %TASK_NAME%
echo        Script: %PYTHON_SCRIPT%
echo        Hora: %HORA%
echo.

REM Eliminar tarea si ya existe
schtasks /Query /TN "%TASK_NAME%" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [INFO] Eliminando tarea existente...
    schtasks /Delete /TN "%TASK_NAME%" /F >nul 2>&1
)

REM Crear la tarea programada
schtasks /Create /TN "%TASK_NAME%" /TR "cmd /c cd /d \"%SCRIPT_DIR%\" && uv run python birthday_checker.py >> logs\birthday_checker.log 2>&1" /SC DAILY /ST %HORA% /F

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo [OK] Tarea programada creada exitosamente!
    echo ========================================
    echo.
    echo Detalles:
    echo   - Nombre: %TASK_NAME%
    echo   - Frecuencia: Diaria
    echo   - Hora: %HORA%
    echo   - Logs: %SCRIPT_DIR%\logs\birthday_checker.log
    echo.
    echo La verificacion de cumpleanos se ejecutara automaticamente
    echo todos los dias a las %HORA%.
    echo.
    echo Para ver o modificar la tarea:
    echo   1. Abre "Programador de tareas" de Windows
    echo   2. Busca: %TASK_NAME%
    echo.
) else (
    echo.
    echo [ERROR] No se pudo crear la tarea programada
    echo         Intenta ejecutar este script como Administrador
    echo.
)

pause
