# Imagen única para la API (gunicorn) y el worker (qcluster).
# Se construye desde la raíz del repositorio para incluir knowledge-base/:
#   docker build -f backend/Dockerfile -t asistente-api .
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DJANGO_SETTINGS_MODULE=config.settings.prod \
    CARPETA_CONOCIMIENTO=/app/knowledge-base/procesos \
    MEDIA_ROOT=/app/media

WORKDIR /app/backend

RUN useradd --create-home --uid 1000 asistente

COPY backend/requirements/ requirements/
RUN pip install -r requirements/prod.txt

COPY backend/ .
COPY knowledge-base/ /app/knowledge-base/

RUN mkdir -p /app/media && chown -R asistente:asistente /app/media

USER asistente
EXPOSE 8000

CMD ["gunicorn", "config.wsgi", "--bind", "0.0.0.0:8000", "--worker-class", "gthread", "--workers", "2", "--threads", "8", "--timeout", "120", "--access-logfile", "-"]
