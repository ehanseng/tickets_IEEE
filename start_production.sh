#!/bin/bash

# Script de inicio para producción
# Sistema de Tickets IEEE

echo "🚀 Iniciando Sistema de Tickets IEEE en modo producción..."

# Verificar que existe el archivo .env
if [ ! -f .env ]; then
    echo "❌ Error: No se encuentra el archivo .env"
    echo "Por favor, copia .env.example a .env y configura las variables necesarias:"
    echo "  cp .env.example .env"
    echo "  nano .env"
    exit 1
fi

# Crear directorios necesarios
echo "📁 Creando directorios necesarios..."
mkdir -p qr_codes
mkdir -p logs

# Verificar que uv está instalado
if ! command -v uv &> /dev/null; then
    echo "❌ Error: uv no está instalado"
    echo "Instala uv con: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Instalar/actualizar dependencias
echo "📦 Instalando dependencias..."
uv sync

# Iniciar aplicación
echo "✅ Iniciando aplicación..."
echo "🌐 La aplicación estará disponible en http://0.0.0.0:8000"
echo "📝 Presiona Ctrl+C para detener"

# Ejecutar con 4 workers para mejor rendimiento
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4 --log-level info
