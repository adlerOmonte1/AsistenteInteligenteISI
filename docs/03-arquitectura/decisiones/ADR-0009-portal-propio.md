# ADR-0009 · Portal web propio en lugar de integrarse a la web institucional

- Estado: Aceptada
- Fecha: 2026-11-17

## Contexto

La idea inicial era insertar el asistente en la web de la universidad. Modificar esa web requiere permisos y coordinación con otras áreas que el proyecto no controla, y el plazo de la entrega no admite esperar esas aprobaciones. Además, los estudiantes necesitan algo más que un chat: ver las fases de cada trámite y descargar la normativa en un solo lugar.

## Decisión

Construir un **portal de consultas** propio, publicado en un subdominio que asigne el Centro de Cómputo, con:

- la lista de trámites y las fases publicadas de cada uno;
- la biblioteca normativa (resoluciones, reglamentos, formatos, guías);
- un buscador sobre las fichas;
- el asistente, flotante en todas las páginas y a pantalla completa en `/asistente`.

El widget `<udh-chat>` se mantiene para que, cuando haya permisos, cualquier página de la universidad lo inserte con dos líneas de HTML.

## Alternativas consideradas

- **Solo el widget en la web institucional.** Depende de permisos externos y no resuelve la consulta de normativa.
- **Una página dentro de la intranet o del sistema académico.** Mismo problema de permisos y un ciclo de despliegue ajeno.

## Consecuencias

- El proyecto controla su propio despliegue y puede demostrarse sin depender de terceros.
- El portal reutiliza las fichas publicadas: lo que dice el asistente y lo que muestra el portal nunca se contradicen.
- Hay que pedir al Centro de Cómputo el subdominio y los dominios autorizados para el widget (CORS).
