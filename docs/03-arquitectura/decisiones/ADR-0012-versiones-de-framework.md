# ADR-0012 · Django 5.2 LTS y Angular 22 sin zone.js

- Estado: Aceptada
- Fecha: 2026-11-17

## Contexto

El sistema se entrega a un equipo que lo mantendrá sin los autores. Las versiones deben tener soporte durante la vida útil esperada y seguir las prácticas actuales de cada framework, para que la documentación oficial sirva de ayuda.

## Decisión

- **Backend:** Python 3.12 (en la imagen Docker), **Django 5.2 LTS** (soporte hasta abril de 2028) y Django REST Framework.
- **Frontend:** **Angular 22** con componentes standalone, signals, `input()`/`output()`, control de flujo `@if`/`@for`, `ChangeDetectionStrategy.OnPush` y detección de cambios **zoneless** (sin zone.js). Pruebas con Vitest.
- El widget usa Angular Elements y `fetch` en lugar de `HttpClient` para mantener el paquete pequeño (≈ 50 kB transferidos).

## Alternativas consideradas

- **Django 6.x.** Más reciente, pero no es LTS; obligaría a migrar antes de 2028.
- **Angular con NgModules y zone.js.** Patrón anterior; la documentación actual de Angular ya no lo usa.

## Consecuencias

- Actualizar Django dentro de la serie 5.2 es seguro (`pip install -U "Django>=5.2,<5.3"`); pasar a 6.2 LTS será una tarea planificada.
- Angular publica una versión mayor cada seis meses; conviene actualizar con `ng update` una vez al año.
- El código de ejemplo de bibliotecas antiguas (NgModules) no aplica directamente.
