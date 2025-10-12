# Script para subir archivos vía SFTP
# Requiere WinSCP o FileZilla instalado

$server = "72.167.151.233"
$username = "svrvpsefjkcv"
$password = "OzsO`$n63ddME"
$localPath = "E:\erick\Documents\Personal\UTadeo\IEEE\Proyectos\Ticket"

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "OPCIONES DE DESPLIEGUE" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

Write-Host "`n1️⃣ OPCIÓN 1: Usar FileZilla (Recomendado)" -ForegroundColor Yellow
Write-Host "   Host: sftp://$server" -ForegroundColor Green
Write-Host "   Usuario: $username" -ForegroundColor Green
Write-Host "   Contraseña: $password" -ForegroundColor Green
Write-Host "   Puerto: 22" -ForegroundColor Green
Write-Host "`n   Pasos:"
Write-Host "   - Abre FileZilla"
Write-Host "   - Conéctate con los datos de arriba"
Write-Host "   - Navega a /home/ieeetadeo2006/public_html/ticket (o donde corresponda)"
Write-Host "   - Sube todos los archivos del proyecto"

Write-Host "`n2️⃣ OPCIÓN 2: Usar WinSCP" -ForegroundColor Yellow
Write-Host "   - Descarga WinSCP: https://winscp.net/"
Write-Host "   - Protocolo: SFTP"
Write-Host "   - Host: $server"
Write-Host "   - Puerto: 22"
Write-Host "   - Usuario: $username"
Write-Host "   - Contraseña: $password"

Write-Host "`n3️⃣ OPCIÓN 3: Panel de Control Web" -ForegroundColor Yellow
Write-Host "   Si tu hosting tiene cPanel o similar:"
Write-Host "   - Accede al panel de control"
Write-Host "   - Busca 'File Manager' o 'Administrador de Archivos'"
Write-Host "   - Navega a la carpeta del dominio ieeetadeo.org/ticket"
Write-Host "   - Sube los archivos directamente desde el navegador"

Write-Host "`n4️⃣ OPCIÓN 4: Git desde el servidor (Mejor opción)" -ForegroundColor Yellow
Write-Host "   Si tienes acceso SSH al servidor con el usuario correcto:"
Write-Host "   ssh ieeetadeo2006@$server"
Write-Host "   cd /ruta/al/directorio/ticket"
Write-Host "   git clone https://github.com/ehanseng/tickets_IEEE.git ."

Write-Host "`n=====================================" -ForegroundColor Cyan
Write-Host "ARCHIVOS A SUBIR" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Desde: $localPath"
Write-Host "`nArchivos principales:"
Write-Host "  - main.py"
Write-Host "  - models.py"
Write-Host "  - schemas.py"
Write-Host "  - database.py"
Write-Host "  - ticket_service.py"
Write-Host "  - pyproject.toml"
Write-Host "  - uv.lock"
Write-Host "  - /templates/"
Write-Host "  - .env (crear con credenciales SMTP)"
Write-Host "`nNO subir:"
Write-Host "  - tickets.db (se generará automáticamente)"
Write-Host "  - qr_codes/ (se generará automáticamente)"
Write-Host "  - .git/"
Write-Host "  - __pycache__/"

Write-Host "`n=====================================" -ForegroundColor Cyan
Write-Host "DESPUÉS DE SUBIR LOS ARCHIVOS" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Necesitarás ejecutar en el servidor:"
Write-Host "  1. Instalar dependencias: uv sync"
Write-Host "  2. Configurar .env"
Write-Host "  3. Iniciar aplicación: uv run python main.py"
Write-Host "`nContacta al administrador del servidor para estos pasos."

Write-Host "`n💡 ¿Tienes acceso a cPanel u otro panel de control? [S/N]" -ForegroundColor Magenta
