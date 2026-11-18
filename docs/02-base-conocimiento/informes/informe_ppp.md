# Diseño de la base de conocimiento y flujo conversacional — Prácticas Pre Profesionales (PPP)

**Fase 2:** Diseño de la base de conocimiento y flujos de conversación
**Proceso:** Prácticas Pre Profesionales, Plan 2021
**Programa Académico:** Ingeniería de Sistemas e Informática — Facultad de Ingeniería, Universidad de Huánuco

## 1. Objetivo

Estructurar la información del proceso de PPP en una base de conocimiento, un catálogo de intenciones y un flujo conversacional que permitan al chatbot orientar al estudiante desde las condiciones de inicio hasta la resolución de aprobación de sus prácticas.

## 2. Fuentes

- Reglamento de PPP 2021 (Res. N.° 221-2021-CF-FI-UDH, ratificado por Res. N.° 029-2022-R-CU-UDH).
- Flujograma de PPP Plan 2021 entregado por la Coordinación del Programa Académico.
- Documento consolidado de procesos de la Fase 1, incluidos los criterios acordados con Coordinación.

## 3. Resumen del entregable

| Componente | Archivo | Cantidad |
|---|---|---|
| Fichas de conocimiento | `fichas/` | 8 (5 de etapa y 3 transversales) |
| Datos estructurados | `datos_clave.json` | Correos, pagos, plazos y anexos de las 4 etapas |
| Intenciones | `intents.yaml` | 14 |
| Frases de entrenamiento | `intents.yaml` | 210 (15 por intención) |
| Entidades | `intents.yaml` | 2 (`etapa`, `anexo`) |
| Flujos conversacionales | `flujo.md` | 3 |
| Plantillas de respuesta | `plantillas.md` | 61 |
| Preguntas de prueba | `golden_set.csv` | 50 |
| Pendientes para Coordinación | `pendientes.md` | 10 |

## 4. Base de conocimiento

La información se dividió en fichas, una por unidad de consulta. Cada ficha tiene un encabezado de metadatos (facultad, programa, proceso, fase, fuente, vigencia y estado) que permite filtrar la búsqueda y extender el chatbot a otros programas sin rediseñar la estructura.

| ID | Ficha |
|---|---|
| PPP_E00 | Condiciones para iniciar las PPP |
| PPP_E01 | Etapa 1: Carta de presentación |
| PPP_E02 | Etapa 2: Aprobación del Plan de PPP |
| PPP_E03 | Etapa 3: Ejecución |
| PPP_E04 | Etapa 4: Informe final y sustentación |
| PPP_T01 | Causales de anulación |
| PPP_T02 | Anexos |
| PPP_T03 | Actores y roles |

Los datos exactos (correos, montos y plazos) se separaron además en `datos_clave.json`, para que el chatbot los tome de una fuente estructurada y no los genere.

## 5. Intenciones y entidades

| Intención | Qué atiende |
|---|---|
| PPP_info_general | Qué son las PPP, horas, obligatoriedad y etapas |
| PPP_requisitos_inicio | Condiciones de inicio, áreas válidas y tipo de entidad |
| PPP_diagnostico_etapa | Ubicar en qué etapa está el estudiante |
| PPP_requisitos_etapa | Documentos de cada etapa |
| PPP_pasos_etapa | Procedimiento de cada etapa |
| PPP_correo_etapa | Correo de destino de cada etapa |
| PPP_costo | Pagos del proceso |
| PPP_plazo | Plazos de presentación y subsanación |
| PPP_anexo_info | Qué es cada anexo y quién lo llena |
| PPP_asesor_supervisor | Designación y funciones del Asesor–Supervisor |
| PPP_sustentacion | Características de la sustentación |
| PPP_anulacion | Causales de anulación y reinicio |
| PPP_estado_tramite | Seguimiento del trámite |
| PPP_siguiente_paso | Qué sigue tras aprobar las PPP |

Entidades: `etapa` (4 valores con sinónimos) y `anexo` (7 valores). Las consultas que corresponden a otros procesos se derivan a `CPP_*` (convalidación por experiencia), `TRA_*` (traslados) y `BAC_*` (bachiller).

## 6. Flujo conversacional

1. **Flujo principal:** identifica la intención, pide la etapa o el anexo cuando falta, consulta la ficha, responde con la plantilla y ofrece la etapa siguiente.
2. **Flujo de diagnóstico de etapa:** mediante preguntas de sí o no, ubica al estudiante en su etapa y le indica qué hacer, con alerta del plazo del Plan.
3. **Flujo de verificación de condiciones:** confirma si el estudiante cumple ciclo, horario, supervisor y área antes de iniciar.

En los tres flujos, dos respuestas no reconocidas seguidas derivan a atención humana (`GEN_derivar_humano`), y todo dato no confirmado se responde con el correo del Programa Académico en lugar de un valor supuesto.

## 7. Criterios de diseño

- Trato formal de usted.
- Respuestas de máximo unas 120 palabras, con requisitos en viñetas y pasos numerados.
- Cada respuesta de etapa termina con el correo de destino y una pregunta de seguimiento.
- Ningún dato se incluye si no está en las fuentes; lo no confirmado se marca como pendiente.
- Donde el reglamento y el flujograma discrepan, se aplica el criterio acordado con Coordinación.

## 8. Validación

El archivo `golden_set.csv` contiene 50 preguntas con la intención, la entidad y la respuesta esperadas. Cubre consultas normales, desambiguación, diagnóstico, datos pendientes, desvíos a otros procesos y consultas fuera de alcance. Se usará en la fase de pruebas para medir la precisión del chatbot.

## 9. Pendientes

Quedan 10 datos por confirmar con Coordinación, detallados en `pendientes.md`: pagos de las etapas 2 y 4, tipo de días del plazo del Plan, plazo de emisión de la carta, descarga de anexos, seguimiento del trámite, modalidad de la sustentación, alcance del reinicio tras anulación, constancia de Seguimiento del Graduado y entrega de la resolución.
