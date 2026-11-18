---
name: arquitectura-c4
description: Mantiene la arquitectura documentada del Asistente Académico UDH — modelo C4 en Structurizr (workspace.dsl), su explicación en Mermaid, validar_c4.py, el documento de módulos y las decisiones de arquitectura (ADR). Úsala al crear, renombrar o eliminar una app de Django o una feature de Angular, al cambiar dependencias entre módulos, al tomar una decisión técnica que cambie cómo se construye u opera el sistema, o cuando se pida actualizar el C4 o escribir un ADR.
---

# Arquitectura y modelo C4

## Archivos

| Archivo | Rol |
|---|---|
| `docs/03-arquitectura/modelo-c4/workspace.dsl` | **Fuente de verdad** del modelo (Structurizr DSL) |
| `docs/03-arquitectura/modelo-c4/modelo_c4.md` | Explicación por niveles con Mermaid |
| `docs/03-arquitectura/modulos.md` | Responsabilidad, dependencias y reglas de cada módulo |
| `docs/03-arquitectura/decisiones/` | ADR numerados + índice en `README.md` |
| `scripts/validar_c4.py` | Comprueba en el CI que código y modelo coincidan |

## Al crear o renombrar una app o feature

1. En `workspace.dsl`, agregue (o renombre) el `component` dentro de su contenedor con la propiedad:
   ```
   properties {
       "ruta" "backend/apps/<app>"
   }
   ```
   (para el frontend: `frontend/projects/<proyecto>/src/app/features/<feature>`).
2. Agregue sus relaciones (`->`) con los componentes de los que depende.
3. Actualice la fila en `modulos.md` y, si cambia el diagrama, `modelo_c4.md`.
4. Ejecute `python scripts/validar_c4.py`; debe decir «Modelo C4 al día».

Vista local: `docker run -it --rm -p 8080:8080 -v "$PWD/docs/03-arquitectura/modelo-c4:/usr/local/structurizr" structurizr/lite`.

## Cuándo escribir un ADR

Cuando la decisión cambia cómo se construye u opera el sistema y alguien podría preguntar «¿por qué así?»: una dependencia nueva, un cambio de proveedor, una regla de seguridad, una excepción a un principio. No para detalles de implementación.

## Cómo

- Número siguiente al último en `decisiones/README.md`; archivo `ADR-00NN-titulo-corto.md`.
- Secciones: Contexto · Decisión · Alternativas consideradas · Consecuencias (plantilla en el README).
- Un ADR aceptado no se reescribe: si cambia la decisión, se escribe uno nuevo y el anterior pasa a «Reemplazada por ADR-00NN».
- Agregue la fila al índice.

## Reglas

- Mermaid sin tildes, eñes ni signos de apertura dentro de los bloques.
- El nivel 4 (código) no se dibuja: se remite a modelos, OpenAPI y flujo de consulta.
- Si el código contradice un ADR, se corrige el código o se escribe un ADR nuevo; nunca se deja la contradicción.
