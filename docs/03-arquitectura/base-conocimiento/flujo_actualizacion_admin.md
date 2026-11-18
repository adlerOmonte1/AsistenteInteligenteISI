# Flujo de actualización de la base de conocimiento por el administrador

> Entregable del integrante A · Fase 2

Cuando cambia un dato oficial (nueva resolución, nuevo correo, nuevo monto, respuesta de Coordinación a un pendiente), el administrador **no edita respuestas del chatbot**: edita **la ficha**. Todo lo demás (índice, plantillas, evaluación) se regenera a partir de ella.

## 1. Roles

| Rol | Quién | Qué hace |
|---|---|---|
| **Fuente** | Coordinación del P.A. ISI / Facultad | Emite o confirma el dato oficial |
| **Administrador** | Responsable del asistente | Edita fichas, ejecuta validaciones, publica |
| **Revisor** | Responsable del proceso afectado (B–F) o Coordinación | Aprueba el cambio antes de publicarlo |
| **Sistema** | Validador + indexador + golden set | Comprueba formato, reindexa y evalúa |

## 2. Diagrama del flujo

```mermaid
flowchart TD
  A([Cambio en la fuente oficial<br/>resolución, correo, monto,<br/>respuesta a un pendiente]) --> B[Administrador identifica<br/>las fichas afectadas<br/>por id, proceso y fase]
  B --> C{¿Existe la ficha?}
  C -- No --> C1[Crear ficha nueva con el<br/>esquema de metadatos]
  C -- Sí --> D{¿La norma reemplaza<br/>a la anterior?}
  D -- Sí --> D1[Crear ficha nueva y marcar la antigua<br/>con reemplazada_por]
  D -- No --> D2[Editar la ficha en una rama<br/>actualizar vigencia, version, actualizado]
  C1 & D1 & D2 --> E{¿Dato confirmado<br/>por la fuente?}
  E -- Sí --> E1[estado: confirmado<br/>cerrar el pendiente en pendientes.md]
  E -- No --> E2[estado: pendiente<br/>registrar en pendientes.md]
  E1 & E2 --> F[Ajustar intents, plantillas o golden set<br/>si cambió la respuesta clave]
  F --> G[Ejecutar validar_contrato.py]
  G --> H{¿Pasa la validación<br/>de formato?}
  H -- No --> D2
  H -- Sí --> I[Ejecutar golden set completo<br/>del proceso y de los procesos enlazados]
  I --> J{¿Exactitud ≥ metas y<br/>0 datos inventados?}
  J -- No --> D2
  J -- Sí --> K[Pull request a la rama principal]
  K --> L{¿Revisor aprueba?}
  L -- No, con observaciones --> D2
  L -- Sí --> M[Merge y reindexación automática<br/>de la base de conocimiento]
  M --> N[Prueba de humo en producción<br/>3 preguntas del golden set]
  N --> O{¿Responde bien?}
  O -- No --> P[Revertir al commit anterior<br/>e investigar]
  P --> D2
  O -- Sí --> Q([Publicado · registrar en el historial<br/>de cambios del proceso])
```

## 3. Pasos detallados

1. **Detectar el cambio.** Fuentes posibles: nueva resolución, comunicado de Coordinación, respuesta a un ítem de `pendientes.md`, o un patrón de derivaciones a humano en los registros que revela un dato desactualizado.
2. **Localizar las fichas.** Buscar por `id`, `proceso` y texto (p. ej. un correo que cambió puede aparecer en varias fichas: `secretaria.sistemas.hco@udh.edu.pe` se usa en PPP, convalidación de PPP y título).
3. **Editar en una rama** del repositorio, nunca directamente en la rama principal.
4. **Actualizar metadatos:** `vigencia` (fecha de la nueva norma), `fuente`, `estado`, y los opcionales `version` (+1), `actualizado`, `actualizado_por`.
5. **Actualizar `pendientes.md`:** cerrar el pendiente resuelto (indicar fecha y fuente) o agregar uno nuevo.
6. **Revisar artefactos dependientes:** si cambia una respuesta clave, actualizar `golden_set.csv` y la plantilla correspondiente; si aparece una consulta nueva frecuente, agregar ejemplos al intent.
7. **Validar formato** con `python validar_contrato.py <carpeta_del_proceso>`.
8. **Evaluar** con el golden set. Ningún cambio se publica si aparece un dato no respaldado.
9. **Revisión** por el responsable del proceso o Coordinación mediante pull request.
10. **Publicar:** merge → reindexación → prueba de humo. Si falla, revertir.

## 4. Reglas

- Un cambio = una rama = un pull request, con el `id` de las fichas en el título (p. ej. `CPP_E01: monto del derecho de trámite`).
- Nunca borrar una ficha con normativa histórica: marcarla con `reemplazada_por`.
- No publicar con `estado: confirmado` un dato que solo se conoce de forma verbal; requiere documento o correo oficial de Coordinación citado en `fuente`.
- Los cambios urgentes (p. ej. un correo dado de baja) siguen el mismo flujo, pero la revisión puede hacerla directamente Coordinación.
