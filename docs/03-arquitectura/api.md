# Contrato de la API

Todas las rutas van bajo `/api/v1/`. El contrato completo, con esquemas de petición y respuesta, está en [`api/openapi.yaml`](api/openapi.yaml), generado desde el código:

```bash
cd backend && python manage.py spectacular --file ../docs/03-arquitectura/api/openapi.yaml
```

Con el servidor de desarrollo levantado, la documentación navegable está en `http://localhost:8000/api/v1/docs/`.

## Formato de error

Todas las respuestas de error tienen la misma forma (`backend/comun/excepciones.py`):

```json
{ "detalle": "Revise los datos enviados.", "errores": { "pago": ["La sección «Pago» no puede quedar vacía; use «No indicado»."] } }
```

`detalle` se muestra como aviso; `errores` junto a cada campo del formulario.

## Públicos (sin login)

| Método | Ruta | Uso |
|---|---|---|
| POST | `/chat/` | `{sesion, mensaje, intent?, ficha?}` → eventos SSE (ver `flujo_consulta.md`) |
| POST | `/chat/{consulta_id}/feedback/` | `{sesion, util}`; solo la misma sesión puede calificar |
| GET | `/configuracion/publica/` | Bienvenida y aviso legal del widget |
| GET | `/procesos/` | Procesos visibles con número de fases publicadas |
| GET | `/procesos/{clave}/` | Proceso, fichas publicadas y documentos |
| GET | `/procesos/{clave}/fichas/{codigo}/` | Una ficha publicada |
| GET | `/documentos/?proceso=&tipo=&q=` | Biblioteca normativa (paginada) |
| GET | `/buscar/?q=` | Búsqueda por palabras en las fichas publicadas |
| GET | `/health/` | Estado de la API y de la base (monitoreo) |

## Panel (JWT `Authorization: Bearer …`)

| Método | Ruta | Uso | Rol mínimo |
|---|---|---|---|
| POST | `/auth/login/` · `/auth/refresh/` · `/auth/logout/` | Sesión; el refresh viaja en cookie HttpOnly | — |
| GET | `/auth/me/` | Usuario actual | lector |
| GET | `/fichas/?proceso=&estado=&publicacion=&q=` | Listado paginado | lector |
| POST, PATCH | `/fichas/` · `/fichas/{id}/` | Crear o editar (queda en borrador) | editor |
| POST | `/fichas/{id}/enviar-revision/` | Valida el contrato y pasa a revisión | editor |
| POST | `/fichas/{id}/aprobar/` · `/rechazar/` | Publica o devuelve con observaciones | revisor |
| POST | `/fichas/{id}/revertir/` | `{numero}`: publica una versión anterior | revisor |
| GET | `/fichas/{id}/historial/` | Versiones publicadas | lector |
| GET, POST, PATCH | `/intents/` · `/pendientes/` · `/plantillas/` | Gestión del conocimiento | editor (lectura: lector) |
| GET, POST, PATCH, DELETE | `/admin/documentos/` | Biblioteca del portal (multipart) | editor |
| POST, GET | `/cargas/` | Subir .docx/.pdf y ver las fichas propuestas | editor |
| GET | `/admin/procesos/` · `/facultades/` · `/programas/` | Catálogo | lector (escritura: superadmin) |
| POST | `/probador/` | Pregunta de prueba con traza; no se registra | editor |
| GET, POST | `/evaluaciones/` | Ejecutar el golden set y ver resultados | editor (lectura: lector) |
| GET, POST, PATCH | `/casos-evaluacion/` | Casos del golden set | editor |
| GET | `/conversaciones/` · `/metricas/resumen/` | Historial y métricas | lector |
| GET, POST, PATCH | `/usuarios/` | Cuentas | superadmin |
| GET, PATCH | `/configuracion/` | Parámetros del asistente | superadmin |

Si el usuario tiene una facultad asignada, los listados se filtran a esa facultad y los objetos de otra facultad responden 403.
