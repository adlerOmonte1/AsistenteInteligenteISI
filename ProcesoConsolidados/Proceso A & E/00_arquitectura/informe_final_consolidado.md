# Informe final de la Fase 2 — Asistente Inteligente del P.A. ISI

**Universidad de Huánuco · Facultad de Ingeniería · P.A. de Ingeniería de Sistemas e Informática**
**Fecha de consolidación:** 2026-10-19 (borrador) · **Versión:** 0.1 · **Rama:** `jean`

> ⚠️ **Borrador.** La consolidación definitiva es el **29 de octubre**. Hoy solo están integradas las carpetas de los integrantes A y E; las demás se agregarán cuando se entreguen y se volverá a ejecutar `validar_contrato.py`.

## 1. Resumen ejecutivo

Se definió una **arquitectura híbrida** (intents deterministas + recuperación semántica sobre fichas, con validador de salida contra datos inventados), un **esquema de metadatos** formal con validación automática y un **flujo de actualización** controlado por el administrador. Del lado de los procesos, el proceso E (Grado de Bachiller y Convalidación de PPP) está completo: **11 fichas, 16 intents, 26 preguntas de evaluación y 13 pendientes** para Coordinación.

## 2. Equipo y responsabilidades

| Integrante | Responsable de | Carpeta | Estado al 2026-10-19 |
|---|---|---|---|
| A | Arquitectura, metadatos, flujo de actualización, consolidación | `00_arquitectura/` | Completo (falta consolidación del 29/10) |
| B | Título por tesis | `titulo_tesis/` | Por entregar |
| C | Título por TSP | `titulo_tsp/` | Por entregar |
| D | PPP Plan 2021 | `ppp/` | Por entregar |
| E | Bachiller y convalidación de PPP | `bachiller_conv_ppp/` | Completo |
| F | Traslados e intents generales | `traslados_generales/` | Por entregar |

## 3. Arquitectura

Ver [`arquitectura_hibrida.md`](arquitectura_hibrida.md). Puntos clave:

- **Una sola base de conocimiento:** las fichas de cada carpeta.
- **Router por confianza:** ≥ 0.75 vía determinista; 0.40–0.75 desambiguación; < 0.40 RAG con filtro por metadatos.
- **Validador de salida:** todo correo, monto, plazo o resolución de la respuesta debe existir en una ficha citada.
- **Derivación** a `GEN_derivar_humano` tras dos intentos fallidos o si falla el validador.

## 4. Esquema de metadatos y flujo de actualización

- [`esquema_metadatos.md`](esquema_metadatos.md) y [`esquema_metadatos.schema.json`](esquema_metadatos.schema.json): 9 campos obligatorios del contrato + 6 opcionales de administración (`version`, `actualizado`, `actualizado_por`, `reemplazada_por`, `pendientes`, `palabras_clave`).
- [`flujo_actualizacion_admin.md`](flujo_actualizacion_admin.md): cambio en rama → validación de formato → golden set → revisión por PR → reindexación → prueba de humo → reversión si falla.

## 5. Cumplimiento del contrato por carpeta

Salida de `python 00_arquitectura/validar_contrato.py . --md`:

| Carpeta | Fichas | Fichas pendientes | Intents | Golden set | Errores | Estado |
|---|---|---|---|---|---|---|
| `bachiller_conv_ppp/` | 11 | 4 | 16 | 26 | 0 | ✅ Cumple |

| Criterio de aceptación (sección 5) | TES | TSP | PPP | BAC/CPP | TRA/GEN |
|---|---|---|---|---|---|
| Una ficha por fase o etapa | — | — | — | ✅ 6 pasos + 5 etapas | — |
| Encabezados completos | — | — | — | ✅ | — |
| Datos no confirmados con `estado: pendiente` | — | — | — | ✅ 4 fichas | — |
| ≥ 10 ejemplos por intent | — | — | — | ✅ | — |
| Pregunta por entidad faltante | — | — | — | ✅ | — |
| Flujo con desambiguación, seguimiento y derivación | — | — | — | ✅ | — |
| Golden set ≥ 10 preguntas | — | — | — | ✅ 14 BAC + 12 CPP | — |
| Prefijos y estructura | — | — | — | ✅ | — |
| Datos respaldados por fuentes | — | — | — | ✅ | — |
| Pendientes documentados | — | — | — | ✅ 13 | — |

«—» = carpeta aún no entregada.

## 6. Resultados por proceso

### 6.1 Grado de Bachiller y Convalidación de PPP — integrante E

- **Fichas:** 11 (7 confirmadas, 4 pendientes: BAC_P04, BAC_P06, CPP_E00, CPP_E01).
- **Intents:** 16 (8 `BAC_`, 8 `CPP_`) · **Entidades:** `paso_bachiller`, `tipo_foto`, `etapa_cpp`, `documento_cpp`.
- **Golden set:** 26 preguntas (14 BAC, 12 CPP).
- **Observaciones:** el trámite de Bachiller se apoya en un flujograma sin fecha ni base normativa (`vigencia: no indicada`); no tiene montos ni plazos salvo el Consejo de Facultad mensual. La convalidación enlaza con el Bachiller (`CPP_E04 → BAC_P01`) y el Bachiller con los títulos (`TES_F07`, `TSP_F06`; ids a confirmar con B y C).

### 6.2 a 6.5 — Procesos B, C, D y F

Pendientes de entrega (29 de octubre).

## 7. Evaluación con el golden set

Evaluación pendiente de la Fase 3 (implementación). Golden sets disponibles: `bachiller_conv_ppp/golden_set.csv`.

## 8. Pendientes consolidados para Coordinación

Del proceso E (detalle en [`../bachiller_conv_ppp/pendientes.md`](../bachiller_conv_ppp/pendientes.md)):

| ID | Proceso | Fase | Dato que falta | Respuesta de Coordinación | Estado |
|---|---|---|---|---|---|
| P-E01 | Bachiller | BAC_P04 | Requisitos que genera la plataforma | | Abierto |
| P-E02 | Bachiller | BAC_P04 | Correo de la Comisión | | Abierto |
| P-E03 | Bachiller | Todas | Pagos y montos | | Abierto |
| P-E04 | Bachiller | Todas | Plazos por paso | | Abierto |
| P-E05 | Bachiller | BAC_P06 | Entrega de la resolución del grado | | Abierto |
| P-E06 | Bachiller | Todas | Vigencia y base normativa del flujograma | | Abierto |
| P-E07 | Bachiller | BAC_P01 | Cómo se acredita la PPP aprobada | | Abierto |
| P-E08 | Convalidación PPP | CPP_E00 | Ciclo mínimo (6.º vs. VII) | | Abierto |
| P-E09 | Convalidación PPP | CPP_E01 | Monto del derecho de trámite | | Abierto |
| P-E10 | Convalidación PPP | CPP_E01 | Cómputo de los 20 días | | Abierto |
| P-E11 | Convalidación PPP | CPP_E02–E04 | Plazos de cada instancia | | Abierto |
| P-E12 | Convalidación PPP | CPP_E03 | Programación de la exposición | | Abierto |
| P-E13 | Convalidación PPP | CPP_E00 | Suma de periodos en varias instituciones | | Abierto |

## 9. Riesgos y siguientes pasos

| Riesgo / tarea | Impacto | Responsable | Fecha |
|---|---|---|---|
| Ids de fichas de otros procesos referenciados por E (`TES_F07`, `TSP_F06`) deben coincidir con los de B y C | Enlaces rotos en la ruta académica | A, B, C | 26/10 |
| Carpetas B, C, D, F sin entregar | Informe incompleto | B, C, D, F | 29/10 |
| Ejecutar `validar_contrato.py` sobre todas las carpetas | Detectar incumplimientos antes de la consolidación | A | 26–27/10 |
| Reunión con Coordinación con todos los `pendientes.md` | Fichas que pasan a `confirmado` | Todos | 28/10 |
| Calibrar umbrales del router con los golden sets | Calidad de respuesta | A | Fase 3 |

## 10. Anexos

- Fuentes: Reglamento de PPP 2021 (Res. N.° 221-2021-CF-FI-UDH, ratificado por Res. N.° 029-2022-R-CU-UDH); flujograma «Trámite Virtual de optar el Grado Académico de Bachiller»; flujograma «Requisitos para Convalidación de PPP»; Documento Consolidado de Procesos del P.A. ISI (Fase 1).
- Carpetas: [`00_arquitectura/`](.), [`bachiller_conv_ppp/`](../bachiller_conv_ppp/).
