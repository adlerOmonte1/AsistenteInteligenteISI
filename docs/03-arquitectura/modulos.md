# Módulos del sistema

Cada módulo corresponde a un componente del modelo C4 (`modelo-c4/workspace.dsl`). Para cada uno: responsabilidad, de qué depende, qué expone y las reglas que no se deben romper.

## Backend (`backend/apps/`)

Las dependencias van en un solo sentido. Un módulo no importa a otro que no figure en su columna «Depende de».

| Módulo | Responsabilidad | Depende de | Expone |
|---|---|---|---|
| `cuentas` | Usuarios administrativos, roles, login con bloqueo, JWT con refresh en cookie. | — | `/auth/*`, `/usuarios/` |
| `sistema` | Configuración editable (umbrales, límite de gasto, textos), salud, tareas programadas. | — | `/health/`, `/configuracion/`, `/configuracion/publica/` |
| `conocimiento` | Catálogo (facultad, programa, proceso), fichas con versiones, intents, pendientes, plantillas, documentos, importador, ciclo de publicación, propuesta desde documentos. | recuperacion (indexar), evaluacion (humo), generacion (propuesta) | `/procesos/`, `/documentos/`, `/buscar/` (públicos); `/fichas/`, `/intents/`, `/pendientes/`, `/plantillas/`, `/admin/*`, `/cargas/` (panel) |
| `generacion` | Proveedores de LLM y embeddings (Gemini, OpenAI compatible, local), prompt de la vía RAG, costo y presupuesto. | analitica (gasto del mes) | Servicios internos |
| `nlu` | Normalización, sinónimos, entidades (fase, tipo de traslado, anexo), clasificador k vecinos. | generacion | Servicios internos |
| `recuperacion` | Índice de secciones publicadas y búsqueda híbrida BM25 + pgvector con RRF. | generacion | Servicios internos |
| `validacion` | Extrae correos, montos, plazos y resoluciones y verifica que estén en las fichas citadas. | — | Servicio interno |
| `dialogo` | Canal SSE, límites por sesión e IP, orquestador, router por confianza, respuestas deterministas, probador. | nlu, recuperacion, generacion, validacion, conocimiento, analitica, sistema | `/chat/`, `/chat/{id}/feedback/`, `/probador/` |
| `evaluacion` | Golden set, ejecución en segundo plano, métricas frente a metas. | dialogo | `/evaluaciones/`, `/casos-evaluacion/` |
| `analitica` | Registro anonimizado de consultas, métricas del panel, purga por retención. | — | `/conversaciones/`, `/metricas/resumen/` |

### Reglas por módulo

**conocimiento**
- El asistente y el portal leen siempre `VersionFicha`, nunca los campos de `Ficha` (ADR-0007).
- Una ficha publicada no se borra: se marca con `reemplazada_por`.
- Quien editó una ficha no puede aprobarla, salvo el rol `superadmin`.
- Subir un documento solo crea fichas en borrador.

**generacion**
- Ningún otro módulo importa `httpx` ni conoce un proveedor concreto: usan `obtener_llm()` y `obtener_embeddings()` (ADR-0004).
- El texto del estudiante va siempre en el mensaje de usuario, nunca en el de sistema.
- Al superar el límite de gasto o con el LLM apagado, la vía RAG no llama al modelo.

**recuperacion y nlu**
- Solo se comparan vectores del mismo proveedor. Si el proveedor falla y entra el respaldo local, la búsqueda usa solo BM25 y el clasificador cae a RAG.
- Cambiar `EMBED_PROVEEDOR` o `EMBED_MODELO` exige `manage.py reindexar`.

**dialogo**
- La respuesta se arma y se valida completa antes del primer evento SSE (ADR-0006).
- El canal limita por sesión y por IP con topes distintos (ADR-0011).

**analitica**
- `Consulta.pregunta` se guarda enmascarada; ninguna vista expone datos que identifiquen al estudiante.

**cuentas**
- El access token nunca se guarda en el navegador fuera de la memoria; el refresh va en cookie `HttpOnly`, `Secure`, `SameSite=Strict`, con rotación y lista negra (ADR-0010).

## Frontend (`frontend/projects/`)

| Proyecto | Responsabilidad | Reglas |
|---|---|---|
| `shared` | Modelos TypeScript espejo de los serializers, `ChatPanel`, `ChatStream` (SSE con fetch), sesión anónima, `MarkdownPipe` seguro, estilos base. | Sin dependencias de un proyecto concreto. `ChatStream` se provee en `ChatPanel` para tomar el `API_URL` del contenedor. |
| `portal` | Sitio público. Features: `inicio`, `tramite`, `documentos`, `buscar`, `asistente`, `acerca`. | Solo endpoints públicos. Sin login. |
| `admin` | Panel. Features: `auth`, `dashboard`, `conocimiento`, `intents`, `pendientes`, `documentos`, `calidad`, `probador`, `evaluacion`, `conversaciones`, `usuarios`, `configuracion`. | Ruta con `data.rol`; el backend vuelve a validar el permiso. Cada feature consume la API a través de su `data-access/`. |
| `widget` | `<udh-chat>` como Web Component. | Shadow DOM, zoneless, sin `HttpClient` (usa `fetch`) para un bundle mínimo. Nombre de archivo sin hash. |

Convenciones comunes: componentes standalone, `inject()`, signals, `input()`/`output()`, control de flujo `@if`/`@for`, `ChangeDetectionStrategy.OnPush`, sin NgModules ni zone.js.
