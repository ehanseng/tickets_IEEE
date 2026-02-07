# Guía de Desarrollo para Nuevos Módulos IEEE Tadeo

Esta guía establece el stack tecnológico y las convenciones que deben seguir todos los módulos del ecosistema IEEE Tadeo para mantener consistencia y facilitar la integración.

---

## Stack Tecnológico Requerido

| Componente | Tecnología | Versión Mínima |
|------------|------------|----------------|
| **Lenguaje** | Python | 3.13+ |
| **Framework Web** | FastAPI | 0.115+ |
| **Servidor ASGI** | Uvicorn | 0.32+ |
| **ORM** | SQLAlchemy | 2.0+ |
| **Base de Datos** | MySQL | 8.0+ |
| **Driver MySQL** | PyMySQL | 1.1+ |
| **Validación** | Pydantic | 2.0+ |
| **Templates HTML** | Jinja2 | 3.1+ |
| **Frontend CSS** | Tailwind CSS | vía CDN |
| **Íconos** | Font Awesome | 6.x vía CDN |
| **Gestor de paquetes** | uv (recomendado) o pip | |

---

## Estructura de Proyecto Recomendada

```
mi_modulo/
├── main.py              # FastAPI app principal
├── models.py            # Modelos SQLAlchemy
├── schemas.py           # Schemas Pydantic
├── database.py          # Conexión a BD
├── nucleo_client.py     # Cliente API del núcleo (ya incluido en starter)
├── templates/           # Templates Jinja2 + Tailwind
│   ├── base.html
│   └── *.html
├── static/              # Archivos estáticos (CSS, JS, imágenes)
├── .env                 # Variables de entorno (NO commitear)
├── .env.example         # Ejemplo de variables
├── requirements.txt     # Dependencias
├── test_conexion.py     # Script para probar conexión al núcleo
└── README.md
```

---

## Dependencias Base

### requirements.txt

```txt
fastapi>=0.115.0
uvicorn[standard]>=0.32.0
sqlalchemy>=2.0.0
pymysql>=1.1.0
pydantic>=2.0.0
python-dotenv>=1.0.0
jinja2>=3.1.0
python-multipart>=0.0.12
requests>=2.32.0
```

### Instalación con pip

```bash
pip install -r requirements.txt
```

### Instalación con uv (recomendado)

```bash
uv sync
```

---

## Configuración de Variables de Entorno

### .env.example

```env
# Base de datos MySQL local del módulo
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=tu_usuario
MYSQL_PASSWORD=tu_password
MYSQL_DATABASE=nombre_modulo_db

# API del Núcleo IEEE Tadeo
NUCLEO_API_URL=https://ticket.ieeetadeo.org/api/external
NUCLEO_API_KEY=tu_api_key_aqui
```

**Importante:** Cada módulo debe tener su propia base de datos MySQL separada.

---

## Código Base

### database.py

```python
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "mi_modulo")

DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}?charset=utf8mb4"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### main.py

```python
from fastapi import FastAPI, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import engine, get_db, Base
import models

# Crear tablas automáticamente
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Mi Módulo - IEEE Tadeo")

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configurar templates
templates = Jinja2Templates(directory="templates")


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
```

### models.py (ejemplo)

```python
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from datetime import datetime
from database import Base


class MiModelo(Base):
    __tablename__ = "mi_tabla"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(200), nullable=False)
    descripcion = Column(Text, nullable=True)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

### schemas.py (ejemplo)

```python
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class MiModeloBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    activo: bool = True


class MiModeloCreate(MiModeloBase):
    pass


class MiModeloResponse(MiModeloBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
```

---

## Plantilla HTML Base

### templates/base.html

```html
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Mi Módulo{% endblock %} - IEEE Tadeo</title>

    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>

    <!-- Font Awesome -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">

    <!-- Configuración Tailwind -->
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        ieee: '#0066cc',
                    }
                }
            }
        }
    </script>

    {% block extra_head %}{% endblock %}
</head>
<body class="bg-gray-100 min-h-screen">
    <!-- Header -->
    <header class="bg-ieee text-white shadow-lg">
        <div class="max-w-7xl mx-auto px-4 py-4">
            <div class="flex items-center justify-between">
                <h1 class="text-xl font-bold">
                    <i class="fas fa-microchip mr-2"></i>
                    {% block header_title %}Mi Módulo{% endblock %}
                </h1>
                <nav>
                    {% block nav %}{% endblock %}
                </nav>
            </div>
        </div>
    </header>

    <!-- Contenido principal -->
    <main class="max-w-7xl mx-auto px-4 py-6">
        {% block content %}{% endblock %}
    </main>

    <!-- Footer -->
    <footer class="bg-gray-800 text-gray-400 text-center py-4 mt-8">
        <p class="text-sm">IEEE Tadeo Student Branch &copy; 2025</p>
    </footer>

    {% block extra_scripts %}{% endblock %}
</body>
</html>
```

### templates/index.html (ejemplo)

```html
{% extends "base.html" %}

{% block title %}Inicio{% endblock %}
{% block header_title %}Mi Módulo IEEE Tadeo{% endblock %}

{% block content %}
<div class="bg-white rounded-lg shadow-sm p-6">
    <h2 class="text-2xl font-bold text-gray-800 mb-4">
        <i class="fas fa-home text-ieee mr-2"></i>
        Bienvenido
    </h2>
    <p class="text-gray-600">
        Este es el módulo de ejemplo para IEEE Tadeo.
    </p>
</div>
{% endblock %}
```

---

## Integración con el Núcleo

El archivo `nucleo_client.py` incluido en el starter permite:

### Autenticación SSO

```python
from nucleo_client import verify_user_token

# Cuando el usuario llega desde el núcleo con un token
user_data = verify_user_token(token)
# user_data contiene: id, name, email, branch_role, etc.
```

### Obtener Miembros

```python
from nucleo_client import get_all_members

members = get_all_members()
for m in members:
    print(f"{m['name']} - {m['email']}")
```

### Probar Conexión

```bash
python test_conexion.py
```

---

## Comandos de Desarrollo

### Crear entorno virtual

```bash
# Con venv estándar
python -m venv .venv
source .venv/bin/activate      # Linux/Mac
.venv\Scripts\activate         # Windows

# Con uv
uv venv
source .venv/bin/activate
```

### Instalar dependencias

```bash
pip install -r requirements.txt
# o
uv sync
```

### Ejecutar en desarrollo

```bash
uvicorn main:app --reload --port 8000
# o
python main.py
# o con uv
uv run uvicorn main:app --reload --port 8000
```

### Crear base de datos MySQL

```sql
CREATE DATABASE mi_modulo_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'mi_usuario'@'localhost' IDENTIFIED BY 'mi_password';
GRANT ALL PRIVILEGES ON mi_modulo_db.* TO 'mi_usuario'@'localhost';
FLUSH PRIVILEGES;
```

---

## Reglas y Convenciones

### Base de Datos

- **Usar MySQL** — No SQLite ni otras bases de datos
- **Charset UTF8MB4** — Para soporte completo de emojis y caracteres especiales
- **Base de datos separada** — Cada módulo tiene su propia BD

### Autenticación

- **Usar SSO del núcleo** — No crear sistema de login propio
- **API Key por módulo** — Cada módulo recibe su propia API Key

### Frontend

- **Tailwind CSS vía CDN** — No instalar localmente
- **Color IEEE: #0066cc** — Usar `text-ieee`, `bg-ieee`, etc.
- **Font Awesome** — Para íconos consistentes
- **Diseño responsivo** — Mobile-first

### Código

- **Type hints** — Usar tipado en Python
- **Docstrings** — Documentar funciones públicas
- **Schemas Pydantic** — Para validación de entrada/salida
- **Models SQLAlchemy** — Para ORM

### Puertos

Coordinar para evitar conflictos:
- **8000** — Módulo Proyectos
- **8001** — Módulo Asistencia
- **8002** — Módulo Tesorería
- **8070** — Núcleo (producción)

---

## Recursos

- **Documentación FastAPI:** https://fastapi.tiangolo.com/
- **Documentación SQLAlchemy:** https://docs.sqlalchemy.org/
- **Documentación Tailwind CSS:** https://tailwindcss.com/docs
- **API del Núcleo:** Contactar al administrador para documentación

---

## Soporte

Para dudas sobre la integración con el núcleo o solicitar API Keys, contactar al equipo de desarrollo de IEEE Tadeo.
