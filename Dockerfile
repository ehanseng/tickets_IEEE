# Usar imagen oficial de Python 3.13
FROM python:3.13-slim

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instalar uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:${PATH}"

# Copiar archivos de configuración
COPY pyproject.toml uv.lock ./

# Instalar dependencias de Python
RUN uv sync --frozen

# Copiar el resto de la aplicación
COPY . .

# Crear directorios necesarios
RUN mkdir -p qr_codes

# Exponer puerto
EXPOSE 8000

# Comando para ejecutar la aplicación
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
