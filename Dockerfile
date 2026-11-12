# Dockerfile para app Flask de análisis operativo
FROM python:3.12-slim

# Instalar uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivos de dependencias
COPY pyproject.toml ./

# Instalar dependencias con uv
RUN uv sync --no-cache

# Copiar el resto del proyecto
COPY . .

# Exponer puerto
ENV PORT=5000
EXPOSE $PORT

# Comando de inicio
CMD ["uv", "run", "flask", "--app", "wsgi", "run", "--host", "0.0.0.0", "--port", "5000"]
