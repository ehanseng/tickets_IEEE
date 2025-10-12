#!/bin/bash

# Script de despliegue para ticket.ieeetadeo.org
# Este script NO debe subirse a GitHub

SERVER_IP="72.167.151.233"
SERVER_USER="svrvpsefjkcv"
SERVER_PASS="OzsO\$n63ddME"

echo "🔍 Explorando estructura del servidor..."

# Función para ejecutar comandos SSH
ssh_exec() {
    sshpass -p "$SERVER_PASS" ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" "$1"
}

# Explorar directorio home
echo "📂 Contenido del directorio home:"
ssh_exec "pwd && ls -la"

echo ""
echo "🔍 Buscando directorios de dominios..."
ssh_exec "find ~ -maxdepth 3 -type d -name '*ieeetadeo*' 2>/dev/null || echo 'No encontrado en home'"

echo ""
echo "🔍 Buscando estructura típica de hosting (public_html, www, domains)..."
ssh_exec "ls -la ~ | grep -E 'public_html|www|domains|httpdocs|htdocs'"

echo ""
echo "🔍 Si existe public_html o domains:"
ssh_exec "ls -la ~/public_html 2>/dev/null || ls -la ~/domains 2>/dev/null || ls -la ~/www 2>/dev/null || echo 'Ninguno encontrado'"

echo ""
echo "🔍 Buscando directorio 'ticket':"
ssh_exec "find ~ -maxdepth 4 -type d -name 'ticket' 2>/dev/null || echo 'No encontrado'"

echo ""
echo "✅ Exploración completada. Revisa la salida para determinar la ruta correcta."
