# Plan de pruebas

## 1. Criterio de aceptación del prototipo

El prototipo se acepta cuando, en el golden set de cada proceso y con el proveedor de producción (Gemini), cumple:

| Criterio | Meta |
|---|---|
| Exactitud de intent | ≥ 90 % |
| Exactitud de ficha | ≥ 90 % |
| Respuesta clave contenida | ≥ 95 % |
| Datos inventados (fallos del validador) | 0 |
| Preguntas fuera del reglamento que derivan sin inventar | 100 % |
| Tiempo hasta el primer texto | < 3 s |
| Actualización tras aprobar una ficha | < 2 min, y la respuesta refleja el cambio |

## 2. Tipos de prueba

| Tipo | Herramienta | Qué cubre | Dónde |
|---|---|---|---|
| Unitarias del backend | pytest | Router por confianza, validador, enmascarado de datos personales, importador, ciclo de publicación, reintentos ante cuota | `backend/apps/*/tests/` (44 pruebas) |
| Integración del backend | pytest + PostgreSQL real | Chat SSE de punta a punta, límites, feedback, login con cookie, bloqueo, permisos por rol | `backend/apps/dialogo/tests/`, `cuentas/tests/` |
| Unitarias del frontend | Vitest | Cliente SSE, Markdown seguro (sin XSS), servicio de autenticación del panel | `frontend/projects/*/src/**/*.spec.ts` (11 pruebas) |
| Contrato de conocimiento | `validar_contrato.py` | Formato de fichas, intents y golden set | `knowledge-base/herramientas/` |
| Arquitectura | `validar_c4.py` | Modelo C4 al día con el código | `scripts/` |
| Evaluación | Golden set desde el panel | Métricas de la sección 1 | Panel → Golden set |
| Aceptación con usuarios | Formulario | Precisión percibida, claridad, facilidad de uso (1 a 5) | Sección 4 |

## 3. Pruebas manuales antes de cada entrega

| # | Prueba | Resultado esperado |
|---|---|---|
| 1 | Portal → un trámite | Fases en orden, aviso en las fichas pendientes, documentos del proceso |
| 2 | Chat: «¿cuántas fotos necesito para el bachiller?» | Vía determinista, ficha `BAC_P02`, botón «Siguiente» |
| 3 | Chat: «¿a qué correo envío?» sin decir la etapa | Pregunta por la etapa con botones; al elegir, solo la sección «Enviar a» |
| 4 | Chat: «¿cuál es la capital de Francia?» dos veces | Primero pide reformular; la segunda deriva a Coordinación |
| 5 | Chat: escribir un DNI de 8 dígitos | En Panel → Conversaciones aparece como `[dni]` |
| 6 | Editor modifica el pago de una ficha y guarda | El chat sigue respondiendo el monto anterior |
| 7 | Editor envía a revisión; el mismo usuario intenta aprobar | Rechazado: debe aprobar otra persona |
| 8 | Revisor aprueba | En menos de 2 min el chat responde el monto nuevo |
| 9 | Revisor revierte a la versión anterior | Vuelve el monto anterior |
| 10 | Lector intenta abrir Usuarios | Redirigido al resumen; la API responde 403 |
| 11 | Cinco contraseñas incorrectas | Bloqueo de 15 minutos |
| 12 | Widget en una página externa autorizada | Abre, responde y no altera los estilos de la página |

## 4. Pruebas con usuarios (Fase 4)

- **Participantes:** al menos 15 estudiantes del programa (de distintos ciclos) y 3 administrativos.
- **Estudiantes:** resuelven 5 consultas reales de su situación con el portal y el asistente, y califican de 1 a 5 la precisión percibida, la claridad y la facilidad de uso.
- **Administrativos:** actualizan una ficha, la publican con revisión y verifican el cambio en el chat; califican la facilidad del panel.
- **Evidencia:** respuestas del formulario, métricas del panel durante la prueba (consultas, % útiles, % derivadas) y observaciones.

## 5. Línea base

La primera medición (17/11/2026, proveedor local sin LLM) está en `docs/02-base-conocimiento/estado_conocimiento.md` §5: cero datos inventados en todos los procesos. Debe repetirse con Gemini una vez completado el índice.
