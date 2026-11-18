# Convenciones

## Idioma

- **Dominio en español** (`Ficha`, `publicar`, `enviar_a_revision`); **framework en inglés** (`models`, `serializers`, `views`, `ngOnInit`). Los términos del trámite tienen un significado preciso en la universidad y traducirlos lo vuelve ambiguo.
- Textos para el estudiante: español formal, trato de «usted».
- Comentarios solo cuando explican un **por qué** que el código no dice. Nada de comentarios que repiten lo que hace la línea siguiente.

## Backend

| Elemento | Convención | Ejemplo |
|---|---|---|
| App | Una por componente C4, nombre en minúsculas | `apps/recuperacion/` |
| Lógica | En `services.py` (o paquete `services/`), no en vistas ni serializers | `publicacion.aprobar(ficha, revisor)` |
| Vistas | Solo entrada y salida HTTP; permisos de `comun/permisos.py` | `permission_classes = [EsRevisor]` |
| Errores | Formato único `{detalle, errores}`; reglas de negocio con `ErrorDeNegocio` (409) | `comun/excepciones.py` |
| Proveedores externos | Solo detrás de las interfaces de `generacion/proveedores/` | `obtener_llm()` |
| Pruebas | `apps/<app>/tests/test_*.py`, nombre que describe la regla | `test_quien_edita_no_puede_aprobar` |
| Estilo | `ruff` con línea de 120 | `ruff format . && ruff check .` |

Reglas que no se rompen:

1. El asistente y el portal leen `VersionFicha`, nunca los campos de `Ficha` (ADR-0007).
2. Una ficha publicada no se borra: se reemplaza.
3. Ningún dato crítico se responde sin pasar por el validador (ADR-0006).
4. Ninguna vista ni registro expone datos personales del estudiante.

## Frontend

| Elemento | Convención | Ejemplo |
|---|---|---|
| Archivos | kebab-case, sin sufijo `.component` (estilo Angular 20+) | `ficha-editor.ts` |
| Clases | PascalCase en español | `FichaEditor`, `ConocimientoApi` |
| Estado | signals; `toSignal` para observables | `protected readonly ficha = signal<Ficha \| null>(null)` |
| HTTP | Solo en servicios `data-access/`; nunca `HttpClient` en un componente | `features/intents/data-access/intents-api.ts` |
| Modelos | En `shared`, espejo de los serializers | `projects/shared/src/lib/models/` |
| Plantillas | `@if`, `@for`, `@let`; `OnPush` siempre | — |
| Estilo | Prettier (100 columnas, comillas simples) | `npm run format` |

Los errores de validación del backend se muestran junto a cada campo con el texto literal que devuelve la API.

## Git

- `main` está protegida: todo entra por Pull Request con al menos una revisión.
- Una rama por tarea:

| Tipo | Rama | Mensaje de commit |
|---|---|---|
| Funcionalidad | `feat/<tema>` | `feat(conocimiento): revertir a una version anterior` |
| Corrección | `fix/<tema>` | `fix(dialogo): limite por sesion con ventana de una hora` |
| Documentación | `docs/<tema>` | `docs(despliegue): guia de certificados` |
| Base de conocimiento | `kb/<proceso>` | `kb(traslados): fuente de TRA_I01` |

- Mensajes en español, sin tildes, en imperativo y en minúsculas.
- Si el PR crea, renombra o elimina una app o feature, actualiza `workspace.dsl` en el mismo PR.
- Nunca subir `.env`, claves ni datos de estudiantes.
