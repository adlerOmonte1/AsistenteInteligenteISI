# Índice de la documentación

| Carpeta | Contenido | Empezar por |
|---|---|---|
| `00-proyecto/` | Objetivo, alcance, principios, roles y metas | [bases_del_sistema.md](00-proyecto/bases_del_sistema.md) |
| `01-levantamiento/` | Fase 1: documentos consolidados de cada trámite | [Documento consolidado (.docx)](01-levantamiento/Documento_Consolidado_Procesos_PA_ISI.docx) |
| `02-base-conocimiento/` | Fase 2: entregables e informes; estado actual de las fichas | [estado_conocimiento.md](02-base-conocimiento/estado_conocimiento.md) |
| `03-arquitectura/` | Modelo C4, decisiones (ADR), módulos, datos, API, flujo de una consulta | [modelo-c4/modelo_c4.md](03-arquitectura/modelo-c4/modelo_c4.md) |
| `04-desarrollo/` | Puesta en marcha local, convenciones, Gemini | [guia_desarrollo.md](04-desarrollo/guia_desarrollo.md) |
| `05-despliegue/` | Instalación en servidor, operación, widget | [guia_despliegue.md](05-despliegue/guia_despliegue.md) |
| `06-pruebas/` | Criterios de aceptación y pruebas | [plan_pruebas.md](06-pruebas/plan_pruebas.md) |

## Por perfil

**Integrante del equipo que va a programar:** bases del sistema → modelo C4 → módulos → guía de desarrollo → convenciones.

**Responsable de un proceso (fichas):** bases del sistema §6 → `03-arquitectura/base-conocimiento/esquema_metadatos.md` → estado del conocimiento.

**Centro de Cómputo:** guía de despliegue → operación → decisiones de arquitectura (ADR) → integración del widget.

**Coordinación:** operación §2 (cómo se actualiza un trámite) y §3 (calidad).

## Arquitectura en detalle

- [Modelo C4](03-arquitectura/modelo-c4/modelo_c4.md) y su fuente [`workspace.dsl`](03-arquitectura/modelo-c4/workspace.dsl)
- [Decisiones de arquitectura](03-arquitectura/decisiones/README.md)
- [Módulos](03-arquitectura/modulos.md) · [Modelo de datos](03-arquitectura/modelo_datos.md) · [API](03-arquitectura/api.md) · [Flujo de una consulta](03-arquitectura/flujo_consulta.md)
- Base de conocimiento (Fase 2): [arquitectura híbrida](03-arquitectura/base-conocimiento/arquitectura_hibrida.md), [esquema de metadatos](03-arquitectura/base-conocimiento/esquema_metadatos.md), [flujo de actualización](03-arquitectura/base-conocimiento/flujo_actualizacion_admin.md)
