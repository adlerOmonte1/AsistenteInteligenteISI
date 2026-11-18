# Bases del sistema

Reglas que toda decisión técnica debe respetar. Si una tarea entra en conflicto con alguna, gana la base y el conflicto se registra como decisión de arquitectura (`docs/03-arquitectura/decisiones/`).

Origen: *Plan técnico de implementación — Asistente Virtual UDH* (16/11/2026) y la arquitectura híbrida de la Fase 2 (`docs/03-arquitectura/base-conocimiento/arquitectura_hibrida.md`).

## 1. Objetivo

Orientar a los estudiantes del P.A. de Ingeniería de Sistemas e Informática sobre sus trámites, con base en la normativa vigente, y entregar al Centro de Cómputo de la UDH una herramienta operativa y documentada que puedan mantener sin el equipo que la construyó.

El producto es un **portal web de consultas** propio (no se integra a la web institucional, ver ADR-0009) que reúne:

- las fases de cada trámite, con requisitos, pasos, pagos, plazos y destino de los documentos;
- la biblioteca normativa: resoluciones, reglamentos, formatos y guías;
- el asistente conversacional, disponible también como widget `<udh-chat>` para insertarlo en otras páginas;
- el panel con el que el personal administrativo mantiene todo lo anterior.

## 2. Alcance: procesos

| Proceso | Clave | Prefijo | Carpeta en `knowledge-base/procesos/` |
|---|---|---|---|
| Prácticas preprofesionales (Plan 2021) | `ppp` | `PPP_` | `ppp/` |
| Grado de Bachiller y convalidación de PPP | `bachiller_conv_ppp` | `BAC_`, `CPP_` | `bachiller_conv_ppp/` |
| Título por sustentación de tesis | `titulo_tesis` | `TES_` | `titulo_tesis/` |
| Título por trabajo de suficiencia profesional | `titulo_tsp` | `TSP_` | `titulo_tsp/` |
| Traslado interno y externo | `traslados` | `TRA_` | `traslados/` |
| Convalidación de PPP (versión alternativa, oculta) | `conv_ppp_experiencia` | `CPP_` | `conv_ppp_experiencia/` |
| Intents transversales (saludo, ayuda, derivación) | `general` | `GEN_` | `general/` |

El catálogo que usa el importador está en `knowledge-base/catalogo.yaml`.

## 3. Principios no negociables

1. **No inventar datos.** Correos, montos, plazos y resoluciones salen solo de las fichas publicadas. Si un dato falta o está pendiente, se dice que no está confirmado y se deriva a Coordinación. El validador de salida lo hace cumplir.
2. **Registro formal.** El asistente trata al estudiante de «usted».
3. **Solo cuentas administrativas.** Los estudiantes no se registran ni inician sesión.
4. **Panel propio.** No se usa el Django Admin.
5. **Mantenimiento sin programar.** El administrador edita fichas o sube un documento desde el panel; nada se publica sin validación del contrato y aprobación de un revisor distinto del editor.
6. **Bajo costo.** LLM externo por API, sin servidores de IA propios. La mayoría de preguntas se responde sin llamar al modelo.
7. **Escalable a la universidad.** Facultad → programa → proceso; las cuentas pueden limitarse a una facultad.
8. **Sin datos personales.** El widget no pide nombre, DNI ni código; lo que el estudiante escriba se enmascara antes de guardarse y se borra a los 12 meses (Ley N.° 29733).

## 4. Actores y roles

| Actor | Cuenta | Qué hace |
|---|---|---|
| Estudiante | No (sesión anónima) | Consulta el portal y conversa con el asistente |
| Lector | `lector` | Ve métricas, fichas y conversaciones |
| Editor | `editor` | Crea y edita fichas, intents, pendientes y documentos; sube documentos |
| Revisor (Coordinación) | `revisor` | Aprueba o rechaza la publicación de cambios; revierte versiones |
| Centro de Cómputo | `superadmin` | Cuentas, configuración, límites de gasto, despliegue |

Los roles son jerárquicos: cada uno puede lo que pueden los anteriores.

## 5. Metas de calidad

| Métrica | Meta | Cómo se mide |
|---|---|---|
| Exactitud de intent | ≥ 90 % | Golden set: `intent_esperado` frente al obtenido |
| Exactitud de ficha | ≥ 90 % | Golden set: `ficha_esperada` entre las fichas citadas |
| Respuesta clave contenida | ≥ 95 % | Golden set: `respuesta_clave` presente en la respuesta |
| Datos inventados | 0 | Respuestas que fallan el validador de salida |
| Preguntas fuera del reglamento que derivan sin inventar | 100 % | Casos de tipo `fuera_de_tema` |
| Tiempo hasta el primer texto | < 3 s | Latencia registrada en `Consulta.latencia_ms` |
| Actualización tras aprobar una ficha | < 2 min | Indexación en el worker |
| Costo mensual del LLM | < 10 USD | Tope del proveedor + tope interno (`LIMITE_USD_MES`) |

## 6. Unidad de conocimiento: la ficha

Una ficha es una fase o etapa de un trámite, con metadatos (`id`, `facultad`, `programa`, `proceso`, `fase`, `titulo`, `fuente`, `vigencia`, `estado`) y seis secciones fijas: Requisitos, Pasos, Pago, Plazo, Enviar a y Siguiente fase. Es la fuente única para la vía determinista, para la vía RAG y para las páginas del portal. El contrato completo está en `docs/03-arquitectura/base-conocimiento/esquema_metadatos.md`.
