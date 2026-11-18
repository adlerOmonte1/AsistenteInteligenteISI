# Asistente Académico UDH

Portal de consultas de trámites del P.A. de Ingeniería de Sistemas e Informática (Universidad de Huánuco), con asistente conversacional híbrido (intents + RAG con validación de salida) y panel de mantenimiento.

## Estructura

```
backend/          API y worker · Django 5.2 + DRF + django-q2 · una app por componente C4
frontend/         Workspace Angular 22: portal, admin (panel), widget (<udh-chat>), shared
knowledge-base/   Base de conocimiento de la Fase 2 (fichas, intents, golden sets) y catálogo
docs/             00-proyecto · 01-levantamiento · 02-base-conocimiento · 03-arquitectura (C4, API, datos)
infra/            Docker Compose de producción y desarrollo, Nginx, respaldos
scripts/          validar_c4.py (modelo C4 frente al código)
skills/           Skills para trabajar con Claude Code (ver CLAUDE.md)
.github/          CI: arquitectura, backend, frontend, imágenes
```

## Arranque en desarrollo

Requisitos: Python 3.12+, Node 24, Docker.

```bash
docker compose -f infra/docker-compose.dev.yml up -d
```

```bash
cd backend && python -m venv .venv && .venv/Scripts/pip install -r requirements/dev.txt
```

```bash
cd backend && .venv/Scripts/python manage.py migrate && .venv/Scripts/python manage.py createcachetable && .venv/Scripts/python manage.py importar_conocimiento
```

```bash
cd backend && .venv/Scripts/python manage.py runserver
```

```bash
cd frontend && npm install && npm run start:portal
```

Portal: http://localhost:4200 · Panel: `npm run start:admin` → http://localhost:4201 · Widget: `npm run start:widget`.

Cuentas de demostración: `DEMO_PASSWORD=<ver .env.example> python manage.py crear_usuarios_demo`.

Sin API key el sistema usa el proveedor `local` (respuestas extractivas, sin costo). Para Gemini, defina `LLM_PROVEEDOR=gemini`, `EMBED_PROVEEDOR=gemini`, `LLM_API_KEY` y ejecute `python manage.py reindexar`.

## Verificación

```bash
cd backend && .venv/Scripts/python -m pytest && .venv/Scripts/ruff check .
```

```bash
cd frontend && npm run build && npm test
```

```bash
python scripts/validar_c4.py
```

## Documentación

Índice completo: [`docs/INDICE.md`](docs/INDICE.md).

- [Bases del sistema](docs/00-proyecto/bases_del_sistema.md) · [Estado de la base de conocimiento](docs/02-base-conocimiento/estado_conocimiento.md)
- [Modelo C4](docs/03-arquitectura/modelo-c4/modelo_c4.md) · [Decisiones (ADR)](docs/03-arquitectura/decisiones/README.md) · [Módulos](docs/03-arquitectura/modulos.md) · [API](docs/03-arquitectura/api.md)
- [Guía de desarrollo](docs/04-desarrollo/guia_desarrollo.md) · [Activar Gemini](docs/04-desarrollo/guia_gemini.md)
- [Guía de despliegue](docs/05-despliegue/guia_despliegue.md) · [Operación](docs/05-despliegue/operacion.md) · [Widget](docs/05-despliegue/integracion_widget.md)
- [Plan de pruebas](docs/06-pruebas/plan_pruebas.md)
