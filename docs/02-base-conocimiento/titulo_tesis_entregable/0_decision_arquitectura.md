# Paso 0 — Decisión de arquitectura

**Proceso:** Optar Título Profesional – Modalidad Sustentación de Tesis
**Programa:** Ingeniería de Sistemas e Informática – Facultad de Ingeniería – UDH
**Fuente:** Resolución N.° 2367-2025-R-CU-UDH (11-nov-2025)

## 1. Arquitectura híbrida confirmada

| Capa | Función en este proceso |
|------|-------------------------|
| **Intents** | Detectar que el estudiante pregunta por "título por tesis" y en qué fase está (`titulo_tesis_info`, `titulo_tesis_fase`, transversales). |
| **RAG** | Responder con el contenido narrativo de las fichas (requisitos, pasos, advertencias) generadas desde `Proceso_Optar_Titulo_MST.md`. |
| **Fichas JSON estructuradas** | Datos exactos que **no se deben generar con el LLM**: correos, teléfonos, montos, plazos, nombres exactos de trámites en Login. |

Regla de prioridad: **dato exacto → ficha JSON; explicación → RAG; nunca inventar**. Si el dato es `pendiente`, se usa la plantilla de dato no confirmado.

Datos exactos que viven en JSON:
- Correos: `secretaria.sistemas.hco@udh.edu.pe` (Fases 1–8), `repositorio@udh.edu.pe` (Fase 9).
- Montos: **S/ 5.00** (solo Fase 9). Fases 2–8: "monto establecido" → `pendiente`.
- Plazos: 1 mes, 4 meses, 2 meses, 6 meses, 30 días, 15 días, 2 años, 1 año, ~2 meses (entrega de grado).
- Trámites Login (nombre exacto, en mayúsculas) y teléfonos: **952 068 664** (consulta Fase 9) y **952069136** (pie de página).

## 2. Tono
**Tuteo ("tú").** Cercano y claro, sin jerga institucional innecesaria. Ejemplo: "Necesitas…", "Envía los requisitos a…".

## 3. Longitud máxima de respuesta
**6 líneas de texto + checklist.** El checklist (`- [ ]`) no cuenta dentro de las 6 líneas. Si hay más contenido, el bot ofrece: "¿Quieres que te detalle los pasos o la siguiente fase?".

## 4. Unidad de fragmentación
**10 fichas:** 1 ficha **General** + 1 ficha por cada una de las **9 fases**.

La ficha General contiene: base normativa, objetivo, indicación previa (curso Conducta Responsable en Investigación), contactos (2 correos, 2 teléfonos, dirección), seguimiento en Login, Consejo de Facultad, entrega del grado y áreas de atención.

## 5. Reglas de contenido
1. Las advertencias **"OJO"** se conservan tal cual (son contenido a comunicar).
2. Las observaciones del apartado 11 del documento **no se corrigen**; se registran como `estado: pendiente` o como nota.
3. Cada respuesta cierra con la fuente (Resolución N.° 2367-2025-R-CU-UDH) y el correo destino.
4. Fuera de alcance: TSP, PPP, bachiller, convalidación → se deriva.
