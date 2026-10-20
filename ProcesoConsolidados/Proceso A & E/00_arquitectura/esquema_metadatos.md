# Esquema de metadatos de las fichas de conocimiento

> Entregable del integrante A · Fase 2
> Esquema formal en JSON Schema: [`esquema_metadatos.schema.json`](esquema_metadatos.schema.json).
> Validación automática: [`validar_contrato.py`](validar_contrato.py).

Cada ficha es un archivo Markdown con un **encabezado YAML** (entre `---`) y un **cuerpo** con secciones fijas. El encabezado es lo que usa el recuperador para filtrar; el cuerpo es lo que se muestra al estudiante.

## 1. Campos obligatorios (contrato, sección 3.3)

| Campo | Tipo | Regla | Ejemplo | Uso en la arquitectura |
|---|---|---|---|---|
| `id` | texto | `PREFIJO_` + letra de unidad + 2 dígitos. Único en todo el repositorio | `TES_F04`, `BAC_P02`, `CPP_E01` | Clave primaria; se cita en respuestas y golden set |
| `facultad` | texto | Fijo | `Ingeniería` | Filtro (multi-facultad a futuro) |
| `programa` | texto | Fijo | `Ingeniería de Sistemas e Informática` | Filtro |
| `proceso` | enum | Nombre de la carpeta del proceso | `titulo_tesis` | Filtro del recuperador y del router |
| `fase` | entero ≥ 0 | Número de fase/paso/etapa; `0` = prerrequisito o condiciones | `4` | Orden y navegación «siguiente fase» |
| `titulo` | texto | Nombre oficial de la fase o del trámite en Login | `Designación de jurados revisores del informe final` | Texto del encabezado de la respuesta |
| `fuente` | texto | Norma o documento oficial; nunca vacío | `Res. N.° 2367-2025-R-CU-UDH` | Trazabilidad |
| `vigencia` | fecha `AAAA-MM-DD` o `no indicada` | Fecha desde la que rige la fuente. Si no consta, `no indicada` y registrar en `pendientes.md` | `2025-11-11` | Priorizar la versión vigente |
| `estado` | enum | `confirmado` \| `pendiente` | `pendiente` | Activa la plantilla de dato pendiente |

### Prefijos válidos y carpeta asociada

| Prefijo | `proceso` | Letra de unidad recomendada |
|---|---|---|
| `TES_` | `titulo_tesis` | `F` (fase) |
| `TSP_` | `titulo_tsp` | `F` (fase); `F00` = prerrequisito |
| `PPP_` | `ppp` | `E` (etapa); `A` para anulaciones |
| `BAC_` | `bachiller_conv_ppp` | `P` (paso) |
| `CPP_` | `bachiller_conv_ppp` | `E` (etapa); `E00` = condiciones |
| `TRA_` | `traslados_generales` | `I` (interno), `X` (externo) |
| `GEN_` | `traslados_generales` | Libre |

## 2. Campos opcionales de administración

No los exige el contrato a B–F; los agrega el administrador al actualizar una ficha (ver `flujo_actualizacion_admin.md`). El validador los acepta si existen.

| Campo | Tipo | Descripción |
|---|---|---|
| `version` | entero ≥ 1 | Se incrementa en cada cambio publicado |
| `actualizado` | fecha | Fecha del último cambio publicado |
| `actualizado_por` | texto | Rol que aprobó el cambio (p. ej. `Coordinación P.A. ISI`) — no datos personales |
| `reemplazada_por` | id de ficha | Si una nueva norma sustituye la ficha; el recuperador la excluye |
| `pendientes` | lista de ids | Ids de `pendientes.md` asociados (p. ej. `[P-E09, P-E10]`) |
| `palabras_clave` | lista de textos | Refuerzo para la búsqueda BM25 |

## 3. Cuerpo de la ficha

Secciones obligatorias, en este orden y con estos títulos exactos (`##`):

1. `Requisitos`
2. `Pasos`
3. `Pago` — monto en `S/ 0.00` o «No indicado»
4. `Plazo` — o «No indicado»
5. `Enviar a` — correo, oficina o «No aplica (…)»
6. `Siguiente fase` — id de la siguiente ficha o «Fin del proceso»

## 4. Ejemplo válido

```markdown
---
id: CPP_E01
facultad: Ingeniería
programa: Ingeniería de Sistemas e Informática
proceso: bachiller_conv_ppp
fase: 1
titulo: Solicitud en el sistema UDH y envío del expediente de convalidación
fuente: Reglamento de PPP 2021, Res. N.° 221-2021-CF-FI-UDH, Arts. 31-32
vigencia: 2022-02-01
estado: pendiente
---
## Requisitos
- ...
## Pasos
1. ...
## Pago
No indicado
## Plazo
Máximo 20 días
## Enviar a
secretaria.sistemas.hco@udh.edu.pe
## Siguiente fase
CPP_E02
```

## 5. Indexación

Al indexar, cada ficha se convierte en **un documento por sección** (requisitos, pasos, pago…) que **hereda todo el encabezado**. Así el recuperador puede responder «¿cuánto cuesta la fase 6 de TSP?» recuperando solo la sección `Pago` de `TSP_F06`, filtrada por `proceso = titulo_tsp` y `fase = 6`.
