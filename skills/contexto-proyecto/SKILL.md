---
name: contexto-proyecto
description: Resumen operativo del Asistente Académico UDH — qué es el sistema, sus procesos, roles, vías de respuesta, principios no negociables y dónde está cada cosa. Cárgala al iniciar cualquier sesión de trabajo en este repositorio, antes de tocar código, fichas o documentación, y cuando se pregunte cómo funciona el asistente o qué falta.
---

# Contexto del proyecto

## Qué es

Portal web de consultas de trámites del P.A. de Ingeniería de Sistemas e Informática (UDH), con:

- **Portal** público: trámites y sus fases, biblioteca normativa, buscador.
- **Asistente** conversacional (flotante y en `/asistente`; también como widget `<udh-chat>`).
- **Panel** para que el personal administrativo mantenga el conocimiento sin programar.

Se entrega al Centro de Cómputo de la UDH como proyecto de servicio social. Debe poder mantenerse sin el equipo: por eso la documentación es parte del producto.

## Procesos (`knowledge-base/catalogo.yaml`)

`ppp` (PPP_) · `bachiller_conv_ppp` (BAC_, CPP_) · `titulo_tesis` (TES_) · `titulo_tsp` (TSP_) · `traslados` (TRA_) · `conv_ppp_experiencia` (CPP_, oculto: duplicado pendiente de decisión) · `general` (GEN_, intents transversales).

## Cómo responde (ADR-0002)

| Confianza | Vía | LLM |
|---|---|---|
| ≥ 0,75 | Determinista: secciones de la ficha del intent | No |
| ≥ 0,75 sin fase | Aclaración con botones | No |
| 0,40–0,75 | Desambiguación: dos intents como botones | No |
| < 0,40 | RAG: secciones recuperadas + LLM + validador | Sí |
| 2 fallos, validación fallida o pedido | Derivación a Coordinación | No |

Umbrales editables en Panel → Configuración; se calibran con el golden set.

## Principios no negociables

1. Cero datos inventados: validador de salida obligatorio.
2. El asistente lee versiones publicadas; editar no cambia nada hasta que un revisor distinto aprueba.
3. Sin datos personales del estudiante.
4. Trato de «usted».
5. Bajo costo: la mayoría de preguntas sin LLM; tope de gasto.

## Roles

`lector` < `editor` < `revisor` < `superadmin`. Los estudiantes no tienen cuenta.

## Estado (noviembre de 2026)

- Sistema funcionando en desarrollo; 44 pruebas de backend y 11 de frontend.
- 5 de 6 carpetas de conocimiento cumplen el contrato; `conv_ppp_experiencia` espera decisión.
- Pendiente: índice completo con Gemini (cuota diaria del plan gratuito), golden set real, documentos del portal, contacto oficial de derivación, despliegue en el servidor de la UDH.

Detalle siempre actualizado en `docs/02-base-conocimiento/estado_conocimiento.md`.

## Mapa

| Necesito… | Ir a |
|---|---|
| Entender la arquitectura | `docs/03-arquitectura/modelo-c4/modelo_c4.md`, `modulos.md`, `decisiones/` |
| Levantar el proyecto | `docs/04-desarrollo/guia_desarrollo.md` |
| Desplegar u operar | `docs/05-despliegue/` |
| Contrato de fichas | `docs/03-arquitectura/base-conocimiento/esquema_metadatos.md` |
| Flujo de una pregunta | `backend/apps/dialogo/orquestador.py`, `docs/03-arquitectura/flujo_consulta.md` |
