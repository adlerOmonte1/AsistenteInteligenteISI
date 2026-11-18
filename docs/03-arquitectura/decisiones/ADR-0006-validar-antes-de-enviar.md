# ADR-0006 · Validar la respuesta completa antes de enviarla

- Estado: Aceptada
- Fecha: 2026-11-17

## Contexto

El plan técnico preveía enviar la respuesta del LLM en streaming, token por token, para que el primer texto aparezca en menos de 3 segundos. Pero el validador de salida necesita la respuesta completa para comprobar correos, montos, plazos y resoluciones. Si se envía mientras se genera, un dato inventado llega a la pantalla del estudiante antes de que el validador pueda descartarlo.

## Decisión

El orquestador pide al LLM la respuesta completa (sin streaming), la valida y solo entonces la envía. El canal SSE se mantiene: entrega el texto en fragmentos y luego las opciones, las fuentes y el evento de fin. El streaming es de presentación, no de generación.

## Alternativas consideradas

- **Streaming real con validación al final.** Si la validación falla habría que «borrar» texto ya mostrado: confuso y el dato ya fue leído.
- **Validar por frases durante el streaming.** Complejo y frágil: un monto puede partirse entre fragmentos.

## Consecuencias

- La garantía de «cero datos inventados» se cumple por construcción.
- El tiempo hasta el primer texto es el de la respuesta completa del modelo. Con Flash-Lite y 600 tokens de salida se espera bajo 3 s; se mide en `Consulta.latencia_ms` y se revisa en el panel.
- La vía determinista no cambia: no hay generación.
