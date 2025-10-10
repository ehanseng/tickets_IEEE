"""
WSGI Configuration for Passenger (cPanel/Shared Hosting)
Este archivo es necesario si tu hosting usa Passenger para ejecutar apps Python
"""

import sys
import os

# Agregar el directorio de la aplicación al path
INTERP = os.path.expanduser("~/ticket/.venv/bin/python3")
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

# Obtener el directorio actual
cwd = os.getcwd()
sys.path.insert(0, cwd)

# Importar la aplicación FastAPI
from main import app as application

# Passenger espera un objeto llamado 'application'
# FastAPI ya proporciona esto a través de ASGI/WSGI
