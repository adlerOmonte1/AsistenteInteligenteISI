# Guía de desarrollo

Cómo levantar el proyecto en una computadora del equipo y cómo trabajar sobre él.

## 1. Requisitos

| Herramienta | Versión |
|---|---|
| Python | 3.12 o superior |
| Node.js | 24 (con npm 11) |
| Docker Desktop | Para la base de datos de desarrollo |
| Git | Cualquiera reciente |

## 2. Primera vez

Base de datos (PostgreSQL 16 + pgvector en el puerto **5433**, para no chocar con un PostgreSQL local):

```bash
docker compose -f infra/docker-compose.dev.yml up -d
```

Backend (en Windows, `.venv/Scripts/`; en Linux o macOS, `.venv/bin/`):

```bash
cd backend && python -m venv .venv && .venv/Scripts/pip install -r requirements/dev.txt
```

```bash
cd backend && .venv/Scripts/python manage.py migrate && .venv/Scripts/python manage.py createcachetable
```

```bash
cd backend && .venv/Scripts/python manage.py importar_conocimiento --sin-indexar && .venv/Scripts/python manage.py reindexar
```

Cuentas de prueba, una por rol (`demo-centro`, `demo-revisor`, `demo-editor`, `demo-lector`); la contraseña está en `DEMO_PASSWORD` de `.env.example`:

```bash
cd backend && DEMO_PASSWORD=<la de .env.example> .venv/Scripts/python manage.py crear_usuarios_demo
```

Frontend:

```bash
cd frontend && npm install
```

## 3. Día a día

| Qué | Comando | Dirección |
|---|---|---|
| API | `cd backend && .venv/Scripts/python manage.py runserver` | http://localhost:8000/api/v1/docs/ |
| Worker (evaluaciones, propuestas, indexación al publicar) | `cd backend && .venv/Scripts/python manage.py qcluster` | — |
| Portal | `cd frontend && npm run start:portal` | http://localhost:4200 |
| Panel | `cd frontend && npm run start:admin` | http://localhost:4201 |
| Widget | `cd frontend && npm run start:widget` | http://localhost:4202 |

El portal y el panel redirigen `/api` y `/media` a `localhost:8000` (`frontend/proxy.conf.json`).

Sin `backend/.env` el sistema usa el proveedor `local`: responde copiando las fichas y no gasta nada. Para usar Gemini, ver [`guia_gemini.md`](guia_gemini.md).

## 4. Antes de cada Pull Request

```bash
cd backend && .venv/Scripts/ruff format . && .venv/Scripts/ruff check . && .venv/Scripts/python -m pytest
```

```bash
cd frontend && npm run format && npm run build && npm test
```

```bash
python scripts/validar_c4.py
```

```bash
python knowledge-base/herramientas/validar_contrato.py knowledge-base/procesos
```

El CI repite todo esto en cada PR (`.github/workflows/ci.yml`).

## 5. Tareas frecuentes

**Agregar un endpoint.** En la app que corresponda: serializer → vista con su permiso de `comun/permisos.py` → `urls.py` → prueba en `tests/`. Regenerar el contrato:

```bash
cd backend && .venv/Scripts/python manage.py spectacular --file ../docs/03-arquitectura/api/openapi.yaml
```

**Cambiar un modelo.** Editar `models.py`, luego `makemigrations` y revisar la migración generada. Nunca editar una migración ya subida a `main`.

**Agregar una pantalla al panel.** `frontend/projects/admin/src/app/features/<feature>/pages/<pagina>/`, servicio HTTP en `data-access/`, ruta con `data: { rol: '…' }` en `app.routes.ts`, opción en el menú de `core/layout/shell.ts`. Si la feature es nueva, agregarla al modelo C4.

**Agregar un proceso.** Carpeta en `knowledge-base/procesos/<clave>/` con el formato del contrato (copiar `bachiller_conv_ppp/`), entrada en `knowledge-base/catalogo.yaml`, validar e importar con `--proceso <clave>`.

## 6. Convenciones

Ver [`convenciones.md`](convenciones.md).
