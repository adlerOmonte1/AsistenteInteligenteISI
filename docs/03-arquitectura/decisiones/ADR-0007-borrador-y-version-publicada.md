# ADR-0007 · Borrador separado de la versión publicada

- Estado: Aceptada
- Fecha: 2026-11-17

## Contexto

El modelo de datos del plan técnico tenía una sola fila por ficha (`id_ficha` único) con un estado de publicación. Con ese diseño, editar una ficha publicada modifica la misma fila que lee el asistente: el cambio llegaría a los estudiantes antes de que el revisor lo apruebe.

## Decisión

- `Ficha` guarda el **borrador** que edita el panel.
- `VersionFicha` guarda una **copia inmutable** de cada publicación, numerada.
- `Ficha.version_publicada` apunta a la versión vigente. El asistente, el índice de búsqueda y el portal leen solo de ahí.
- Revertir publica de nuevo el contenido de una versión anterior como versión nueva; nunca se reescribe el historial.

## Alternativas consideradas

- **Una fila por versión con `(codigo, version)` único.** Equivalente, pero complica las relaciones (intents, pendientes) que deben apuntar a «la ficha», no a una versión.

## Consecuencias

- El editor puede trabajar con calma sobre una ficha publicada: nada cambia para los estudiantes hasta la aprobación.
- Cada publicación queda auditada (quién, cuándo, con qué nota).
- `Ficha.tiene_cambios_sin_publicar` compara el borrador con la versión vigente; el panel lo muestra.
