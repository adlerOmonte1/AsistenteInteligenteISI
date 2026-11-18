# ADR-0002 · Arquitectura híbrida: intents + fichas y RAG con validación

- Estado: Aceptada
- Fecha: 2026-11-17 (formaliza el diseño de la Fase 2)

## Contexto

Las consultas de los estudiantes son de dos tipos: cerradas y críticas («¿a qué correo envío el plan?») y abiertas o mal formuladas («trabajo hace dos años en soporte, ¿me sirve?»). Un sistema solo con intents falla ante lo no previsto; uno solo con LLM puede inventar un correo o un monto, y un dato inventado en un trámite académico causa daño real al estudiante.

## Decisión

Se adopta la arquitectura de `docs/03-arquitectura/base-conocimiento/arquitectura_hibrida.md`:

1. Un clasificador de intents decide la vía según su confianza.
2. Con confianza alta, la **vía determinista** copia las secciones de la ficha, sin generación.
3. Con confianza media, se ofrecen los dos intents más probables (desambiguación).
4. Con confianza baja, la **vía RAG** recupera secciones de fichas publicadas y el LLM redacta solo con ellas.
5. Un **validador de salida** comprueba que cada correo, monto, plazo y resolución de la respuesta exista en las fichas citadas; si no, se deriva a Coordinación.

Las fichas son la única fuente para las dos vías y para el portal.

## Alternativas consideradas

- **Solo RAG.** Más simple, pero cada respuesta depende del modelo y del costo por llamada, y las preguntas frecuentes no necesitan redacción.
- **Solo intents (Rasa, Dialogflow).** Exige prever cada pregunta y entrenar un modelo; no responde paráfrasis no previstas.

## Consecuencias

- La mayoría de preguntas se responde sin llamar al LLM: costo bajo y respuestas exactas.
- La calidad depende de la base de conocimiento: un intent sin ejemplos o una ficha incompleta degradan las respuestas.
- El golden set es obligatorio para calibrar umbrales y detectar regresiones.
