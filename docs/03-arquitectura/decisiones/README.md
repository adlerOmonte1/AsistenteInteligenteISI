# Decisiones de arquitectura (ADR)

Cada decisión que cambia la forma de construir o de operar el sistema se registra aquí, con su contexto y sus consecuencias. Una decisión no se edita para cambiarla: se escribe una nueva que la **reemplaza** y se marca la anterior como `Reemplazada por ADR-00NN`.

| ADR | Decisión | Estado |
|---|---|---|
| [0001](ADR-0001-monorepo-por-componentes.md) | Monorepo con una carpeta por contenedor C4 | Aceptada |
| [0002](ADR-0002-arquitectura-hibrida.md) | Arquitectura híbrida: intents + fichas y RAG con validación | Aceptada |
| [0003](ADR-0003-clasificador-knn.md) | Clasificador de intents por k vecinos sobre embeddings | Aceptada |
| [0004](ADR-0004-proveedor-llm-intercambiable.md) | Proveedor de LLM intercambiable por REST, con proveedor local | Aceptada |
| [0005](ADR-0005-postgresql-pgvector.md) | PostgreSQL + pgvector como única base de datos | Aceptada |
| [0006](ADR-0006-validar-antes-de-enviar.md) | Validar la respuesta completa antes de enviarla | Aceptada |
| [0007](ADR-0007-borrador-y-version-publicada.md) | Borrador separado de la versión publicada | Aceptada |
| [0008](ADR-0008-importador-tolerante.md) | Importador tolerante y catálogo de procesos | Aceptada |
| [0009](ADR-0009-portal-propio.md) | Portal web propio en lugar de integrarse a la web institucional | Aceptada |
| [0010](ADR-0010-jwt-refresh-en-cookie.md) | JWT con access en memoria y refresh en cookie HttpOnly | Aceptada |
| [0011](ADR-0011-limite-por-sesion-e-ip.md) | Límite de mensajes por sesión y por IP | Aceptada |
| [0012](ADR-0012-versiones-de-framework.md) | Django 5.2 LTS y Angular 22 sin zone.js | Aceptada |

## Plantilla

```markdown
# ADR-00NN · Título en forma de decisión

- Estado: Propuesta | Aceptada | Reemplazada por ADR-00NN
- Fecha: AAAA-MM-DD

## Contexto
Qué problema hay y qué restricciones pesan.

## Decisión
Qué se hace, en una o dos frases claras.

## Alternativas consideradas
Qué más se evaluó y por qué no se eligió.

## Consecuencias
Qué se gana, qué se pierde y qué obliga a hacer de ahora en adelante.
```
