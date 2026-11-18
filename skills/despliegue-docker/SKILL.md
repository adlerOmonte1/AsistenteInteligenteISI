---
name: despliegue-docker
description: Infraestructura y despliegue del Asistente Académico UDH — Dockerfiles, docker-compose de producción, desarrollo y demostración, Nginx con HTTPS y SSE, certbot, respaldos, CI de GitHub Actions y guías del Centro de Cómputo. Úsala al tocar infra/, .github/, los Dockerfile o las guías de docs/05-despliegue, o cuando se pregunte cómo instalar, actualizar, respaldar o diagnosticar el sistema en un servidor.
---

# Despliegue con Docker

Fuentes: `docs/05-despliegue/guia_despliegue.md`, `operacion.md` e `integracion_widget.md`.

## Piezas

| Archivo | Qué hace |
|---|---|
| `backend/Dockerfile` | Imagen única de API (gunicorn gthread 2×8) y worker (`qcluster`); incluye `knowledge-base/` |
| `infra/nginx/Dockerfile` | Compila portal, admin y widget con Node y los sirve con Nginx |
| `infra/nginx/default.conf.template` | HTTPS, `/` portal, `/admin/`, `/widget/`, `/api/` (SSE sin búfer), `/media/`; usa `${DOMINIO}` |
| `infra/docker-compose.yml` | Producción: `db`, `api`, `worker`, `web`, `certbot` (perfil `certificados`) |
| `infra/docker-compose.dev.yml` | Solo PostgreSQL + pgvector en el puerto 5433 |
| `infra/docker-compose.http.yml` | Superposición sin HTTPS para demostraciones |
| `infra/scripts/respaldo.sh`, `restaurar.sh` | `pg_dump` + `media/`, 14 días de retención |
| `.github/workflows/ci.yml` | Arquitectura, backend (con pgvector), frontend, imágenes |

Siempre desde la raíz: `docker compose -f infra/docker-compose.yml --env-file .env …`.

## Reglas no negociables

1. **Secretos solo en `.env`** (permisos 600), nunca en el repositorio ni en una imagen. `.dockerignore` excluye `.env` y `backend/.env`.
2. **`/api/v1/chat/` sin búfer en Nginx** (`proxy_buffering off`); si no, el SSE llega de golpe.
3. **La API confía solo en `X-Real-IP` puesto por Nginx** para los límites por IP.
4. **`localhost` en `ALLOWED_HOSTS` de producción**: lo necesita el healthcheck de Docker.
5. **Migraciones al arrancar `api`**; el worker espera a que la API esté sana.
6. **El certificado se pide antes de levantar `web`** (certbot `--standalone`); las renovaciones van por `webroot`.
7. **Cambiar de proveedor de embeddings exige `reindexar`.**

## Verificación local de imágenes

```bash
docker build -f backend/Dockerfile -t asistente-api .
```

```bash
docker build -f infra/nginx/Dockerfile -t asistente-web .
```

Si cambia un paso de instalación, actualice `guia_despliegue.md` en el mismo cambio: el Centro de Cómputo instala siguiendo esa guía al pie de la letra.
