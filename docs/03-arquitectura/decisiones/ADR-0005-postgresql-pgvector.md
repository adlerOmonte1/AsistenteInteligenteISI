# ADR-0005 · PostgreSQL + pgvector como única base de datos

- Estado: Aceptada
- Fecha: 2026-11-17

## Contexto

El sistema necesita guardar datos relacionales (fichas, usuarios, consultas), vectores para la búsqueda semántica, una cola de tareas en segundo plano y una caché para los límites de mensajes. Cada servicio extra (Redis, una base vectorial) es algo más que el Centro de Cómputo debe instalar, respaldar y vigilar.

## Decisión

Una sola instancia de PostgreSQL 16 con la extensión pgvector para todo:

- datos del dominio;
- embeddings de secciones y de ejemplos, con índices HNSW de distancia coseno;
- cola de django-q2 (broker ORM);
- caché de Django (`DatabaseCache`) para el bloqueo de login y los límites por sesión e IP.

## Alternativas consideradas

- **ChromaDB o FAISS para vectores.** Otro almacén que sincronizar y respaldar por separado.
- **Redis para cola y caché.** Más rápido, pero innecesario con el volumen esperado (cientos de consultas al día).

## Consecuencias

- Un solo `pg_dump` respalda todo el estado del sistema (más la carpeta `media/` de documentos subidos).
- La imagen `pgvector/pgvector:pg16` es obligatoria; un PostgreSQL sin la extensión no sirve.
- Si el volumen creciera a miles de consultas por minuto, la caché y la cola deberían pasar a Redis; el cambio es de configuración.
