# Insertar el asistente en otra página

El asistente puede aparecer en cualquier página de la universidad como un botón flotante, sin modificar el resto de la página.

## Código a insertar

Antes del cierre de `</body>`:

```html
<script src="https://<subdominio>/widget/main.js" defer></script>
<udh-chat api="https://<subdominio>/api/v1"></udh-chat>
```

## Atributos

| Atributo | Por defecto | Uso |
|---|---|---|
| `api` | `/api/v1` | URL de la API. Obligatorio si la página está en otro dominio. |
| `titulo` | `Asistente Académico` | Encabezado de la ventana. |
| `subtitulo` | `P.A. Ingeniería de Sistemas e Informática` | Segunda línea del encabezado. |
| `estado` | `cerrado` | `abierto` para mostrar la conversación al cargar. |

## Requisito en el servidor

El dominio de la página debe figurar en `CORS_ALLOWED_ORIGINS` del `.env` (separado por comas) y hay que reiniciar con `dc up -d`. Sin eso, el navegador bloquea las llamadas y el widget muestra «No se pudo conectar con el asistente».

## Características

- Usa Shadow DOM: sus estilos no cambian la página ni la página cambia los suyos.
- Pesa unos 50 kB comprimidos y se carga con `defer`, sin retrasar la página.
- En pantallas de menos de 480 px la conversación ocupa toda la pantalla.
- La conversación se identifica con un número anónimo guardado en la pestaña; se pierde al cerrarla.
- El archivo `main.js` no lleva huella en el nombre, así que la URL no cambia entre versiones; Nginx lo sirve con una caché de una hora.

## Prueba local

```bash
cd frontend && npm run start:widget
```

Abre `http://localhost:4202` con una página de ejemplo que inserta el widget apuntando a la API de desarrollo (`http://localhost:8000/api/v1`).
