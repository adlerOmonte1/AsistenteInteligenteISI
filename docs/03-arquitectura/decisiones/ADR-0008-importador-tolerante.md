# ADR-0008 · Importador tolerante y catálogo de procesos

- Estado: Aceptada
- Fecha: 2026-11-17

## Contexto

Al empezar el desarrollo, cinco de las seis carpetas de la Fase 2 no cumplían el contrato de fichas (ids, encabezados, golden sets con columnas propias, un proceso en JSON). Exigir el contrato estricto habría detenido el desarrollo hasta que cada responsable corrigiera su carpeta.

## Decisión

- `knowledge-base/catalogo.yaml` define los procesos: clave, carpeta, nombre, prefijos, orden, visibilidad y formato.
- `manage.py importar_conocimiento` carga todo lo que puede leer y reporta cada desviación como **aviso**; solo un archivo ilegible es un **error**. Tolera variantes conocidas (secciones en el bloque `datos`, columnas alternativas del golden set, `NO_APLICA`, `A|B`).
- Con `--estricto`, las fichas que no cumplen el contrato quedan en borrador. Con `--sin-indexar`, se publica sin gastar cuota del proveedor.
- Las claves de proceso del sistema son `traslados` y `general` (el contrato original decía `traslados_generales`).

## Alternativas consideradas

- **Importador estricto.** Habría bloqueado el desarrollo durante semanas.
- **Corregir las carpetas antes de construir.** Correcto en teoría, pero no dependía del equipo de desarrollo.

## Consecuencias

- El sistema funcionó desde el primer día con datos reales; el 17/11/2026 se normalizó el formato de cinco carpetas (ver `docs/02-base-conocimiento/estado_conocimiento.md`).
- Un aviso no rompe el sistema pero sí baja la calidad: el reporte del importador debe revisarse en cada carga.
- En producción la fuente de verdad es el panel; `knowledge-base/` queda como carga inicial y respaldo legible.
