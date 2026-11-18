# ADR-0003 · Clasificador de intents por k vecinos sobre embeddings

- Estado: Aceptada
- Fecha: 2026-11-17

## Contexto

La arquitectura de la Fase 2 proponía Rasa como referencia. Rasa exige un servicio propio, un ciclo de entrenamiento y conocimientos que el personal administrativo no tiene; cada cambio de ejemplos requeriría reentrenar y redesplegar. La base de conocimiento ya tiene más de 10 ejemplos por intent.

## Decisión

El clasificador (`backend/apps/nlu/services.py`) busca los 7 ejemplos más cercanos a la pregunta (embeddings, distancia coseno, índice HNSW en pgvector) y vota por intent:

```
confianza = similitud del mejor vecino del intent ganador × proporción del voto de ese intent
```

Una pregunta idéntica a un ejemplo recibe confianza 1 sin votación. No hay entrenamiento: agregar o corregir ejemplos desde el panel tiene efecto en cuanto se calculan sus embeddings.

## Alternativas consideradas

- **Rasa / Dialogflow CX.** Servicio extra, entrenamiento y, en Dialogflow, costo por consulta y dependencia de Google Cloud.
- **Clasificación con el LLM.** Una llamada por pregunta: más costo y latencia, y respuestas no deterministas.

## Consecuencias

- Los umbrales de la Fase 2 (0,75 y 0,40) eran para probabilidades de Rasa; con esta fórmula hay que calibrarlos con el golden set para cada proveedor de embeddings. Se ajustan desde el panel.
- Cada pregunta cuesta un embedding (fracciones de centavo; cuenta en la cuota del plan gratuito).
- Solo se comparan ejemplos calculados con el proveedor activo (`EjemploIntent.proveedor_embedding`); si el proveedor falla, el clasificador no responde y la pregunta va a la vía RAG por palabras.
