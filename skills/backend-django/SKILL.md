---
name: backend-django
description: Implementa o modifica el backend Django + DRF del Asistente Académico UDH — apps por componente C4, servicios, permisos por rol, formato de error, proveedores de LLM, migraciones y pruebas con PostgreSQL + pgvector. Úsala al crear o cambiar un modelo, un endpoint, un servicio, una tarea del worker o un comando de manage.py, o cuando se mencione la API, el chat, el orquestador o la base de datos.
---

# Backend Django

Carga antes `contexto-proyecto`. Fuentes: `docs/03-arquitectura/modulos.md`, `modelo_datos.md`, `api.md` y los ADR.

## Stack fijado

Python 3.12 · Django 5.2 LTS · DRF · simplejwt · django-q2 (broker ORM) · drf-spectacular · PostgreSQL 16 + pgvector · httpx · rank-bm25 · PyYAML · pytest-django · ruff. No agregue dependencias sin justificarlo en un ADR: cada una es algo más que el Centro de Cómputo debe mantener.

## Dónde va cada cosa

| Qué | Dónde |
|---|---|
| Entidades e invariantes | `apps/<app>/models.py` (o paquete `models/`) |
| Casos de uso | `apps/<app>/services.py` (o paquete `services/`) |
| Entrada/salida HTTP | `views.py` + `serializers.py`; sin lógica de negocio |
| Permisos | `comun/permisos.py`: `EsLector`, `EsEditor`, `EsRevisor`, `EsSuperadmin`, `LecturaLectorEscrituraEditor`, `MismaFacultad` |
| Errores de negocio | `comun/excepciones.ErrorDeNegocio` (409); validación con `ValidationError` |
| Tareas en segundo plano | `apps/<app>/tasks.py`, encoladas con `async_task("apps.x.tasks.f", id)` |
| Comandos | `apps/<app>/management/commands/` |

Las dependencias entre apps siguen la tabla de `modulos.md`; no cree ciclos.

## Reglas no negociables

1. **El asistente lee `VersionFicha`**, nunca los campos de `Ficha`. Publicar crea una versión nueva (`services/publicacion.py`).
2. **Ninguna respuesta RAG sale sin `validacion.validar()`** sobre el texto completo de las fichas citadas.
3. **Ningún módulo importa `httpx` para hablar con un LLM**: use `obtener_llm()` / `obtener_embeddings()`. Procesos por lotes pasan `reintentos`; el chat no espera.
4. **Nunca mezcle vectores de proveedores distintos**: `SeccionIndexada.proveedor_embedding` y `EjemploIntent.proveedor_embedding` deben coincidir con el proveedor activo para compararse.
5. **Datos personales**: todo texto del estudiante que se guarde pasa por `analitica.services.enmascarar` (vía `registrar`).
6. **Meta.ordering no aplica con GROUP BY**: si anota con `Count`, ponga `.order_by()` explícito.
7. **Permisos en el backend siempre**, aunque el panel oculte el botón.

## Pruebas

- `apps/<app>/tests/test_*.py`; fixtures comunes en `backend/conftest.py` (`proceso`, `ficha_publicada`, `intent_fotos`, `editor`, `revisor`, `como(usuario)`).
- Corren contra PostgreSQL real (pgvector); el proveedor es `local` en `config/settings/test.py`.
- Nombre de la prueba = la regla que verifica (`test_quien_edita_no_puede_aprobar`).
- Proveedores externos: `httpx.MockTransport` (ver `apps/generacion/tests/test_gemini.py`).

## Al terminar

```bash
cd backend && .venv/Scripts/ruff format . && .venv/Scripts/ruff check . && .venv/Scripts/python manage.py makemigrations --check --dry-run && .venv/Scripts/python -m pytest
```

Si cambió un endpoint, regenere `docs/03-arquitectura/api/openapi.yaml` con `manage.py spectacular`. Si creó una app, actualice `workspace.dsl` y `modulos.md`.
