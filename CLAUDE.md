# Instrucciones para el agente — Asistente Académico UDH

Monorepo del **Asistente Académico** del P.A. de Ingeniería de Sistemas e Informática (Universidad de Huánuco): portal de consultas de trámites, asistente conversacional híbrido (intents + RAG con validación de salida) y panel de mantenimiento. Proyecto de servicio social que se entrega al Centro de Cómputo de la UDH, que lo mantendrá sin el equipo.

## Fuentes de verdad, en este orden

1. `docs/00-proyecto/bases_del_sistema.md` — objetivo, principios no negociables, roles, metas.
2. `docs/03-arquitectura/decisiones/` — ADR-0001 a ADR-0012. Si una tarea contradice un ADR, se escribe un ADR nuevo; no se ignora.
3. `docs/03-arquitectura/modelo-c4/workspace.dsl` y `docs/03-arquitectura/modulos.md` — componentes, dependencias y reglas.
4. `docs/03-arquitectura/base-conocimiento/esquema_metadatos.md` — contrato de las fichas.

Si dos documentos se contradicen, gana el de orden más alto y la contradicción **se reporta**.

## Principios que el código hace cumplir

- **No inventar datos.** Correos, montos, plazos y resoluciones salen solo de versiones publicadas de fichas. Toda respuesta RAG pasa por `apps/validacion` antes de enviarse (ADR-0006).
- **Borrador ≠ publicado.** El asistente y el portal leen `VersionFicha`, nunca los campos editables de `Ficha` (ADR-0007). Una ficha publicada no se borra.
- **Sin datos personales.** Las preguntas se enmascaran al registrarse; nada identifica al estudiante.
- **Proveedor intercambiable.** Ningún módulo llama a un LLM directamente: `obtener_llm()` / `obtener_embeddings()` (ADR-0004). No mezclar vectores de proveedores distintos.
- **Trato de «usted»** en todo texto para el estudiante.

## Estructura

```
backend/          Django 5.2 + DRF · apps/: cuentas, sistema, conocimiento, nlu, recuperacion,
                  generacion, validacion, dialogo, evaluacion, analitica · comun/: permisos, errores, texto
frontend/         Angular 22 · projects/: portal, admin, widget, shared
knowledge-base/   catalogo.yaml · procesos/<clave>/ (contrato de fichas) · herramientas/validar_contrato.py
docs/             00-proyecto … 06-pruebas · INDICE.md
infra/            docker-compose (prod, dev, http), nginx, scripts de respaldo
scripts/          validar_c4.py
skills/           Skills del repositorio (ver abajo)
```

## Skills

Cargue la skill que corresponda antes de trabajar en su área:

| Skill | Cuándo |
|---|---|
| `skills/contexto-proyecto` | Siempre, al empezar una sesión |
| `skills/backend-django` | Cualquier cambio en `backend/` |
| `skills/frontend-angular` | Cualquier cambio en `frontend/` |
| `skills/base-conocimiento` | Fichas, intents, golden set, importador |
| `skills/arquitectura-c4` | Crear o renombrar apps o features; escribir un ADR |
| `skills/despliegue-docker` | `infra/`, Docker, Nginx, CI, guías de despliegue |
| `skills/commit-proyecto` | Al cerrar una tarea |

## Reglas de trabajo

- **El usuario hace los commits.** No ejecute `git add`, `git commit`, ni cree o cambie ramas: entregue los comandos (ver `skills/commit-proyecto`).
- El código no lleva comentarios que narren lo obvio, ni emojis, ni firmas de herramientas. Español para el dominio, inglés para el framework.
- No invente requisitos, montos, plazos ni normas en fichas o documentos. Si falta un dato, márquelo como pendiente y repórtelo.
- Mermaid en los documentos: sin tildes ni eñes dentro de los bloques.
- Una app o feature nueva actualiza `workspace.dsl` en el mismo cambio.

## Verificación antes de entregar

```bash
cd backend && .venv/Scripts/ruff check . && .venv/Scripts/python -m pytest
```

```bash
cd frontend && npm run build && npm test
```

```bash
python scripts/validar_c4.py
```

```bash
python knowledge-base/herramientas/validar_contrato.py knowledge-base/procesos
```
