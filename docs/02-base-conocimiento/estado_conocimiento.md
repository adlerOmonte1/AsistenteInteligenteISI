# Estado de la base de conocimiento

Corte: 17/11/2026 (actualizado tras la corrección de `ppp`). Se obtiene con dos herramientas:

```bash
python knowledge-base/herramientas/validar_contrato.py knowledge-base/procesos
```

```bash
cd backend && python manage.py importar_conocimiento --dry-run --detalle
```

La primera aplica el contrato de la Fase 2 de forma estricta. La segunda es el importador del sistema: **carga todo aunque haya errores de forma** y lista cada desviación como aviso. Por eso el desarrollo del software no se detiene mientras los responsables de cada proceso corrigen sus archivos (ADR-0008).

## 1. Resumen por proceso

| Proceso | Contrato | Fichas | Intents | Golden set | Estado |
|---|---|---|---|---|---|
| `bachiller_conv_ppp` | ✅ Cumple | 11 | 16 | 26 | Carpeta de referencia. |
| `ppp` | ✅ Cumple | 8 | 14 | 48 | Corregida por su responsable (25 errores → 0). |
| `titulo_tesis` | ✅ Cumple | 10 | 13 | 61 | Convertida del JSON del entregable al contrato (ver §3). |
| `titulo_tsp` | ✅ Cumple | 9 | 16 | 15 | Formato normalizado (ver §3). |
| `traslados` | ✅ Cumple | 14 | 17 | 30 | Ids y formato normalizados (ver §3). |
| `conv_ppp_experiencia` | ❌ 5 errores | 5 | 4 | 13 | **Decisión pendiente del equipo**: duplica `CPP_E00`–`E04` de `bachiller_conv_ppp`. Se importa oculta del portal y sus intents repetidos se omiten. |
| `general` | — | 0 | 4 | 6 | Intents transversales `GEN_`; recibe los casos de saludo, ayuda y derivación del golden set de tesis. |

El importador reporta **0 errores y 8 avisos**, todos de `conv_ppp_experiencia`.

## 2. Cambio de claves respecto del contrato original

El contrato de la Fase 2 asociaba `TRA_` y `GEN_` a `traslados_generales`. En el sistema los procesos se llaman `traslados` y `general` (catálogo en `knowledge-base/catalogo.yaml`), y `validar_contrato.py` ya usa esas claves. Al corregir sus fichas, el equipo de traslados debe escribir `proceso: traslados`.

## 3. Normalización de formato del 17/11/2026

Se cambió solo la forma, nunca el contenido. Los textos de requisitos, pasos, pagos, plazos y destinos son los de cada entregable.

**Herramienta `validar_contrato.py`.** Tenía falsos errores que no eran de los datos:
- Leía los intents solo con una sangría fija: en `traslados` y `titulo_tsp` informaba «0 ejemplos» cuando había más de 10 por intent.
- Rechazaba `ficha_relacionada: []` (intent sin ficha) y las listas `[A, B]`.
- Leía mal los CSV guardados con BOM (encabezado `﻿id`).

Ahora además acepta en el golden set `ficha_esperada: A|B` (vale cualquiera de las dos) y `NO_APLICA` (la pregunta no debe responderse con una ficha). El evaluador del sistema aplica las mismas reglas.

**`traslados`**
- Ids al formato del contrato: `TRA_INT_F01` → `TRA_I01` y `TRA_EXT_F01` → `TRA_X01` (en fichas, intents, golden set, flujo, plantillas y pendientes).
- `proceso: traslados`; `vigencia: pendiente` → `no indicada` (el estado de la ficha sigue siendo `pendiente`).
- `secciones_fuente` se sumó al campo `fuente`; se quitaron del encabezado `datos` y `siguiente_fase`, que repetían lo que ya está en el cuerpo.

**`titulo_tsp`**: lo mismo, y se quitó `tipo_etapa`.

**`conv_ppp_experiencia`**: se agregó `si_falta_entidad` a los seis intents que no lo tenían (`null` cuando el intent tiene una sola ficha; una pregunta por etapa en `CPP_plazo` y `CPP_resolucion`). No se tocó el proceso ni el prefijo hasta que el equipo decida.

**`titulo_tesis`**: el entregable original (JSON y tablas numeradas) se movió a `docs/02-base-conocimiento/titulo_tesis_entregable/` y se generó la carpeta del contrato:
- `fichas/TES_F00.md` (información general, requisito previo y contactos) a `TES_F09.md`;
- `intents.yaml` desde `3_catalogo_intents.md`, con prefijo `TES_`; saludo, despedida, ayuda y hablar con humano se sumaron a los intents `GEN_`;
- `golden_set.csv` con el formato del contrato; los casos de saludo y derivación pasaron a `general/golden_set.csv`;
- `pendientes.md` con las `notas_observaciones` de cada fase;
- `flujo.md` y `plantillas.md` desde los archivos 4 y 5.

**Queda para los responsables de cada proceso** (requiere conocer el contenido, no solo el formato):
- `titulo_tesis`: las fichas tratan al estudiante de «tú» («Debes cancelar…»); el contrato pide «usted». La `respuesta_clave` del golden set es la respuesta completa esperada, no el dato clave, y baja la métrica «respuesta clave contenida».
- `traslados` y `titulo_tsp`: el campo `fuente` es el nombre de un archivo de trabajo (`Requisitos_para_Convalidacion_Interna.md`, `TrabajoSuficiencia.md`), no una norma o resolución oficial. Hace falta la resolución que respalda cada trámite.
- `traslados`: `pendientes.md` no cita cada ficha pendiente por su id (el validador lo informa como aviso).
- `titulo_tsp`: 15 preguntas en el golden set; se recomiendan al menos 2 por fase.

## 4. Cómo corregir una carpeta

1. Ejecutar el validador sobre la carpeta: `python knowledge-base/herramientas/validar_contrato.py knowledge-base/procesos/<carpeta>`.
2. Tomar como modelo `knowledge-base/procesos/bachiller_conv_ppp/` (fichas, `intents.yaml`, `golden_set.csv`).
3. Corregir en una rama propia y abrir un Pull Request; el CI repite el validador.
4. Tras el merge, en el servidor: `python manage.py importar_conocimiento --proceso <clave>`. Las fichas que no cambiaron no generan versión nueva.

Una vez que el sistema esté en producción, la fuente de verdad pasa a ser **el panel**: los cambios se hacen allí y pasan por revisión. La carpeta `knowledge-base/` queda como carga inicial y respaldo legible.

## 5. Línea base del golden set

Ejecutada con el proveedor `local` (sin API key, embeddings léxicos), solo para tener un punto de partida. Debe repetirse con Gemini antes de la entrega; la exactitud de intent y de ficha debería subir de forma notable, porque los embeddings locales no captan sinónimos ni paráfrasis.

| Proceso | Casos | Intent | Ficha | Clave | Datos inventados |
|---|---|---|---|---|---|
| `ppp` | 50 | 93,8 % | — | 28,0 % | 0 |
| `bachiller_conv_ppp` | 26 | 92,3 % | 73,1 % | 53,8 % | 0 |
| `titulo_tesis` | 67 | — | 49,0 % | — | 0 |
| `titulo_tsp` | 15 | 60,0 % | 66,7 % | 6,7 % | 0 |
| `traslados` | 30 | 56,7 % | 46,7 % | 13,3 % | 0 |
| `conv_ppp_experiencia` | 13 | 38,5 % | 38,5 % | 30,8 % | 0 |

Lectura: **ninguna respuesta inventó datos** en ningún proceso, que es la meta que no admite excepciones. Las carpetas que cumplen el contrato (`bachiller_conv_ppp`) y las que tienen intents completos (`ppp`) superan el 90 % de exactitud de intent incluso sin LLM. La «respuesta clave» baja en `ppp`, `titulo_tsp` y `traslados` porque sus golden sets guardan respuestas largas o redactadas, no el dato clave que el contrato pide.
