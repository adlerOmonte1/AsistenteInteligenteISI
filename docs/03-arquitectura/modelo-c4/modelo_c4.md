# Modelo C4

El modelo formal está en [`workspace.dsl`](workspace.dsl) (Structurizr DSL) y es la fuente de verdad: de él salen las vistas navegables y contra él se valida el código en el CI (`scripts/validar_c4.py`). Este documento lo explica nivel por nivel con diagramas Mermaid que se leen directamente en GitHub.

Para ver el modelo interactivo:

```bash
docker run -it --rm -p 8080:8080 -v "$PWD/docs/03-arquitectura/modelo-c4:/usr/local/structurizr" structurizr/lite
```

## Nivel 1 · Contexto

Quién usa el sistema y con qué sistemas externos se relaciona.

```mermaid
flowchart LR
  E([Estudiante])
  ED([Editor])
  R([Revisor - Coordinacion])
  CC([Centro de Computo])
  S[[Asistente Academico UDH]]
  W[Web institucional UDH]
  L[Proveedor de LLM y embeddings]

  E -- consulta tramites y conversa --> S
  E -- navega --> W
  W -- inserta el widget --> S
  ED -- edita fichas e intents --> S
  R -- aprueba o rechaza cambios --> S
  CC -- cuentas, configuracion, despliegue --> S
  S -- embeddings y redaccion RAG --> L
```

| Elemento | Responsabilidad |
|---|---|
| Asistente Académico UDH | Portal de consultas, asistente conversacional y panel de mantenimiento. |
| Proveedor de LLM | Único servicio externo. Calcula embeddings y redacta respuestas abiertas. Es intercambiable (ADR-0004). |
| Web institucional | Opcional: puede insertar el widget con dos líneas de HTML. El sistema no depende de ella (ADR-0009). |

## Nivel 2 · Contenedores

```mermaid
flowchart LR
  subgraph Navegador
    P[Portal - Angular]
    WG[Widget udh-chat - Angular Elements]
    A[Panel - Angular]
    SH[(Libreria compartida)]
  end
  N[Nginx - HTTPS y estaticos]
  API[API - Django 5.2 + DRF]
  WK[Worker - django-q2]
  DB[(PostgreSQL 16 + pgvector)]
  L[Proveedor de LLM]

  P --- SH
  WG --- SH
  A --- SH
  P -- JSON y SSE --> N
  WG -- SSE --> N
  A -- JSON + JWT --> N
  N -- proxy /api --> API
  API --> DB
  WK --> DB
  API -- REST --> L
  WK -- REST --> L
```

| Contenedor | Tecnología | Responsabilidad | Ruta |
|---|---|---|---|
| Portal | Angular 22 | Sitio público: trámites, fases, documentos, buscador, asistente. | `frontend/projects/portal` |
| Widget | Angular Elements | `<udh-chat>` con Shadow DOM para cualquier página. | `frontend/projects/widget` |
| Panel | Angular 22 | Mantenimiento del conocimiento y calidad. Solo personal con cuenta. | `frontend/projects/admin` |
| Librería compartida | Angular library | Modelos del dominio, cliente SSE y componente de conversación. | `frontend/projects/shared` |
| API | Django 5.2 + DRF | Canal del chat, endpoints públicos y del panel. | `backend` |
| Worker | django-q2 | Indexación, prueba de humo, golden set, propuestas de fichas, purga. | `backend` (mismo código) |
| Base de datos | PostgreSQL 16 + pgvector | Datos, embeddings con índice HNSW, cola de tareas y caché. | — |
| Servidor web | Nginx | HTTPS, archivos de las tres SPA, proxy a la API, documentos subidos. | `infra/nginx` |

Hay una sola base de datos y ningún servicio de IA propio: es lo que mantiene bajo el costo de operación (ADR-0005).

## Nivel 3 · Componentes de la API

Cada componente es una app de Django en `backend/apps/`.

```mermaid
flowchart TB
  DLG[dialogo - canal, orquestador, router]
  NLU[nlu - clasificador de intents]
  REC[recuperacion - BM25 + pgvector]
  GEN[generacion - proveedores LLM y gasto]
  VAL[validacion - validador de salida]
  CON[conocimiento - fichas, versiones, importador]
  EVA[evaluacion - golden set]
  ANA[analitica - registro y metricas]
  CUE[cuentas - usuarios y JWT]
  SIS[sistema - configuracion y salud]

  DLG --> NLU
  DLG --> REC
  DLG --> GEN
  DLG --> VAL
  DLG --> CON
  DLG --> ANA
  DLG --> SIS
  NLU --> GEN
  REC --> GEN
  CON --> REC
  CON --> EVA
  EVA --> DLG
  GEN --> ANA
```

La responsabilidad, las dependencias permitidas y las reglas de cada componente están en [`../modulos.md`](../modulos.md).

## Nivel 3 · Componentes del panel y del portal

| Contenedor | Componente (feature) | Ruta |
|---|---|---|
| Panel | auth, dashboard, conocimiento, intents, pendientes, documentos, calidad, probador, evaluacion, conversaciones, usuarios, configuracion | `frontend/projects/admin/src/app/features/<feature>` |
| Portal | inicio, tramite, documentos, buscar, asistente, acerca | `frontend/projects/portal/src/app/features/<feature>` |

Cada feature tiene `pages/` (componentes enrutables) y, si consume la API, `data-access/` (servicios HTTP). Ningún componente llama a `HttpClient` directamente.

## Nivel 4 · Código

El nivel de código no se dibuja a mano: se desactualizaría con el primer cambio. Sus fuentes son:

- el modelo de datos: [`../modelo_datos.md`](../modelo_datos.md);
- el contrato de la API: [`../api/openapi.yaml`](../api/openapi.yaml), generado desde el código con `python manage.py spectacular`;
- el flujo de una consulta: [`../flujo_consulta.md`](../flujo_consulta.md).

## Regla de mantenimiento

Quien crea, renombra o elimina una app de Django o una feature de Angular actualiza `workspace.dsl` **en el mismo Pull Request**. El CI ejecuta `python scripts/validar_c4.py`, que falla si una ruta del código no tiene elemento en el modelo o si el modelo apunta a una ruta que ya no existe.
