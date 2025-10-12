# Script de exploración del servidor
# NO SUBIR A GITHUB

$serverIP = "72.167.151.233"
$serverUser = "svrvpsefjkcv"
$serverPass = "OzsO`$n63ddME"

Write-Host "🔍 Explorando servidor..." -ForegroundColor Cyan

# Nota: Este script requiere que ejecutes manualmente los comandos SSH
# porque Windows no tiene sshpass nativo

Write-Host "`n📋 Ejecuta estos comandos manualmente:" -ForegroundColor Yellow
Write-Host "ssh $serverUser@$serverIP" -ForegroundColor Green
Write-Host "Contraseña: $serverPass`n" -ForegroundColor Green

Write-Host "Una vez conectado, ejecuta estos comandos para explorar:`n" -ForegroundColor Yellow

$commands = @(
    "pwd  # Ver directorio actual",
    "ls -la  # Ver contenido",
    "ls -la ~ | grep -E 'public_html|www|domains|httpdocs'  # Buscar carpetas web típicas",
    "find ~ -maxdepth 3 -type d -name '*ieeetadeo*' 2>/dev/null  # Buscar ieeetadeo",
    "find ~ -maxdepth 3 -type d -name 'ticket' 2>/dev/null  # Buscar ticket",
    "which python3  # Ver si hay Python",
    "python3 --version  # Versión de Python",
    "which nginx  # Ver si hay Nginx"
)

foreach ($cmd in $commands) {
    Write-Host $cmd -ForegroundColor Cyan
}

Write-Host "`n💡 Copia los resultados y pégalos aquí para continuar con el despliegue." -ForegroundColor Magenta
