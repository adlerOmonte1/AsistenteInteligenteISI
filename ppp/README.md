# Proceso D — Prácticas Pre Profesionales (PPP), Plan 2021

Entregable de la Fase 2: base de conocimiento y flujo conversacional del proceso de PPP.

## Contenido

| Archivo | Qué contiene |
|---|---|
| `informe_ppp.md` | Sección del proceso para el informe final de la fase |
| `fichas/` | 8 fichas: condiciones, 4 etapas, anulación, anexos y actores |
| `datos_clave.json` | Correos, pagos, plazos y anexos en formato estructurado |
| `intents.yaml` | 14 intenciones, 210 frases de ejemplo, entidades y desvíos |
| `flujo.md` | Flujo principal, diagnóstico de etapa y verificación de condiciones (Mermaid) |
| `plantillas.md` | 61 respuestas redactadas, con trato de usted |
| `golden_set.csv` | 50 preguntas de prueba con su respuesta esperada |
| `pendientes.md` | 10 datos por confirmar con Coordinación |

## Convenciones

- Prefijo de IDs: `PPP_`. Fichas de etapa `PPP_E0n`; fichas transversales `PPP_T0n`.
- Fuente única: documento consolidado de la Fase 1 y los criterios acordados con Coordinación.
- Los datos no confirmados llevan `estado: pendiente` y se responden con `DATO_PENDIENTE`.
- Referencias a otros procesos solo por ID: `CPP_*`, `TRA_*`, `BAC_*`, `GEN_*`.

## Cómo actualizar un dato

1. Cambiar la ficha correspondiente en `fichas/`.
2. Cambiar el mismo dato en `datos_clave.json`.
3. Ajustar la plantilla y la fila del golden set indicadas en `pendientes.md`.
