---
name: base-conocimiento
description: Trabaja con la base de conocimiento del Asistente Académico UDH — fichas Markdown con el contrato de la Fase 2, intents.yaml, golden_set.csv, pendientes, plantillas, catálogo de procesos, validar_contrato.py e importar_conocimiento. Úsala al crear o corregir fichas o intents, al validar una carpeta de proceso, al importar a la base de datos o al interpretar el golden set.
---

# Base de conocimiento

Fuentes: `docs/03-arquitectura/base-conocimiento/esquema_metadatos.md` (contrato) y `docs/02-base-conocimiento/estado_conocimiento.md` (estado y cambios).

## Carpeta de un proceso

```
knowledge-base/procesos/<clave>/
  fichas/<ID>.md      una por fase; el nombre del archivo es el id
  intents.yaml        intents con ≥ 10 ejemplos, ficha_relacionada y si_falta_entidad
  golden_set.csv      id,pregunta,intent_esperado,ficha_esperada,respuesta_clave
  flujo.md            diagramas Mermaid; referencia GEN_derivar_humano
  plantillas.md       textos reutilizables
  pendientes.md       datos por confirmar con Coordinación (tabla con ID)
```

Modelo de referencia: `bachiller_conv_ppp/`.

## Ficha

Encabezado YAML con exactamente: `id`, `facultad`, `programa`, `proceso`, `fase`, `titulo`, `fuente`, `vigencia` (`AAAA-MM-DD` o `no indicada`), `estado` (`confirmado` | `pendiente`); opcionales del contrato (`version`, `reemplazada_por`, `palabras_clave`…). Cuerpo con las seis secciones `## Requisitos`, `## Pasos`, `## Pago`, `## Plazo`, `## Enviar a`, `## Siguiente fase`. Secciones extra (Descripción, Resultado…) se aceptan y van a «Información adicional».

Ids: `PREFIJO_` + letra + dos dígitos (`BAC_P02`, `TRA_I01`, `TES_F04`).

## Golden set

- `ficha_esperada` admite `A|B` (cualquiera vale) y `NO_APLICA` (no debe responderse con ficha).
- `respuesta_clave` es **el dato clave** (un monto, un correo), no la respuesta completa: la métrica exige que aparezca en la respuesta.
- Los casos transversales (saludo, derivación) van en `general/golden_set.csv`.

## Reglas no negociables

1. **No invente contenido.** Corregir formato (ids, campos, orden, sangría) sí; agregar requisitos, montos, plazos, correos o normas no. Si falta un dato: `estado: pendiente`, «No indicado» en la sección y una fila en `pendientes.md`.
2. `confirmado` solo con documento o correo oficial citado en `fuente`.
3. `fuente` es una norma o documento oficial, no un archivo de trabajo.
4. Una ficha publicada no se borra: se reemplaza (`reemplazada_por`).
5. Trato de «usted».

## Comandos

```bash
python knowledge-base/herramientas/validar_contrato.py knowledge-base/procesos/<clave>
```

```bash
cd backend && .venv/Scripts/python manage.py importar_conocimiento --dry-run --proceso <clave> --detalle
```

```bash
cd backend && .venv/Scripts/python manage.py importar_conocimiento --proceso <clave> --sin-indexar && .venv/Scripts/python manage.py reindexar
```

`--dry-run` no gasta cuota del proveedor. El importador no borra fichas ni casos que desaparecen de los archivos: si se renombra un id, hay que retirar el anterior de la base.

## En producción

La fuente de verdad es el panel (borrador → revisión → publicación). `knowledge-base/` es la carga inicial y un respaldo legible; los cambios hechos en el panel no vuelven solos a estos archivos.
