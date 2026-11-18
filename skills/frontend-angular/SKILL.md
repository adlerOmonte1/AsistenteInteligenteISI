---
name: frontend-angular
description: Implementa o modifica el frontend Angular 22 del Asistente Académico UDH — portal público, panel de administración, widget <udh-chat> y librería compartida; componentes standalone con signals, zoneless, data-access por feature, guards por rol y estilos base. Úsala al crear una pantalla, un componente, un servicio HTTP, una ruta o un estilo, o cuando se mencione el portal, el panel, el widget o el chat en el navegador.
---

# Frontend Angular

Carga antes `contexto-proyecto`. Fuentes: `docs/03-arquitectura/modulos.md` §Frontend y `docs/04-desarrollo/convenciones.md`.

## Proyectos

| Proyecto | Para qué | Reglas propias |
|---|---|---|
| `shared` | Modelos, `ChatPanel`, `ChatStream` (SSE con fetch), `MarkdownPipe`, `_base.scss` | Sin dependencias de un proyecto concreto. Se importa como `'shared'` (ruta a las fuentes en `tsconfig.json`). |
| `portal` | Sitio público | Solo endpoints públicos. |
| `admin` | Panel (base `/admin/`) | Rutas con `data: { rol }`; `authInterceptor` + `errorInterceptor`. |
| `widget` | `<udh-chat>` | Shadow DOM, sin `HttpClient`, nombre de archivo sin hash, bundle mínimo. |

## Patrón de una feature

```
features/<feature>/
  pages/<pagina>/<pagina>.ts|html|scss   componentes enrutables (carga diferida)
  components/                            piezas reutilizables de la feature
  data-access/<feature>-api.ts           único lugar con HttpClient
```

Archivos en kebab-case sin sufijo `.component`; clases en PascalCase y en español (`FichaEditor`, `IntentsApi`).

## Reglas no negociables

1. **Ningún componente usa `HttpClient`**: siempre a través de su servicio `data-access`.
2. **Standalone, signals, `inject()`, `input()`/`output()`, `@if`/`@for`/`@let`, `OnPush`, zoneless.** Sin NgModules ni zone.js.
3. **El HTML de respuestas y fichas solo con `MarkdownPipe`**, que escapa antes de transformar. Nunca `bypassSecurityTrust*`.
4. **Errores del backend junto al campo** con el texto literal de `errores` (`erroresDeCampo()`); el `detalle` lo muestra el interceptor.
5. **Lo que se oculta por rol también se rechaza en el backend**: el guard es experiencia de usuario.
6. **El access token solo en memoria** (`Auth`); nunca en `localStorage`.
7. **Formularios en diálogos** se recrean en cada apertura (`@if (abierto())`) para no arrastrar lo escrito.
8. **Accesibilidad**: etiquetas en cada control, `aria-live` en listas que cambian, foco visible, `prefers-reduced-motion`.

## Estilos

Variables CSS en `projects/shared/src/styles/_base.scss` (`--udh-primario`, `--udh-acento`…) y clases utilitarias (`tarjeta`, `boton`, `campo`, `insignia`, `aviso`, `tabla`). El widget define sus propias variables en `:host` porque vive en Shadow DOM.

## Al terminar

```bash
cd frontend && npm run format && npm run build && npm test
```

Si creó una feature o un proyecto, actualice `docs/03-arquitectura/modelo-c4/workspace.dsl` y ejecute `python scripts/validar_c4.py`.
