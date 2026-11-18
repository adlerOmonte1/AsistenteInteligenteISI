# ADR-0004 · Proveedor de LLM intercambiable por REST, con proveedor local

- Estado: Aceptada
- Fecha: 2026-11-17

## Contexto

El plan técnico proponía `litellm` para cambiar de proveedor. Es una dependencia grande que cambia con frecuencia, y solo se necesitan dos operaciones: generar texto y calcular embeddings. Además, el equipo necesita trabajar sin API key y el sistema debe seguir respondiendo si el proveedor cae o se agota la cuota.

## Decisión

`backend/apps/generacion/proveedores/` define dos interfaces (`ProveedorLLM.generar`, `ProveedorEmbeddings.embeber`) y tres adaptadores por REST con `httpx`:

| Proveedor | Uso |
|---|---|
| `gemini` | Google AI Studio. Por defecto: `gemini-2.5-flash-lite` y `gemini-embedding-001` (768 dimensiones, normalizados). |
| `openai` | Cualquier API compatible con OpenAI (OpenAI, DeepSeek, Groq…), con `LLM_URL_BASE`. |
| `local` | Sin red ni costo: embeddings léxicos y respuesta extractiva que copia las secciones. |

Se elige con variables de entorno (`LLM_PROVEEDOR`, `EMBED_PROVEEDOR`). Ningún otro módulo conoce un proveedor concreto.

## Alternativas consideradas

- **litellm.** Más proveedores listos, pero una dependencia pesada para dos llamadas.
- **SDK oficial de Google.** Ata el código a un proveedor.
- **Modelo local (Ollama).** Requiere un servidor con GPU o mucha RAM, que el Centro de Cómputo no garantiza.

## Consecuencias

- Cambiar de proveedor es cambiar el `.env` y ejecutar `manage.py reindexar` (los embeddings de proveedores distintos no son comparables).
- Si el proveedor falla, la vía RAG usa el modo extractivo: la respuesta es menos fluida, pero nunca inventa.
- Los procesos por lotes (`reindexar`) reintentan ante el límite por minuto y se detienen ante el límite diario; el chat no espera.
