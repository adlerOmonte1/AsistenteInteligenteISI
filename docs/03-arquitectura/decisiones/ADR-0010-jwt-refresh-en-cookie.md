# ADR-0010 · JWT con access en memoria y refresh en cookie HttpOnly

- Estado: Aceptada
- Fecha: 2026-11-17

## Contexto

El panel es una SPA en Angular que consume la API. Guardar tokens en `localStorage` los expone a cualquier script que logre ejecutarse en la página (XSS). Las cuentas del panel publican información oficial, así que su robo tiene consecuencias.

## Decisión

- `djangorestframework-simplejwt`: access de 15 minutos y refresh de 7 días, con rotación y lista negra.
- El **access** vive solo en un signal del servicio `Auth`; se pierde al recargar.
- El **refresh** viaja en una cookie `HttpOnly`, `Secure`, `SameSite=Strict`, limitada a la ruta `/api/v1/auth/`.
- Al cargar el panel, `authGuard` pide un access nuevo con la cookie. Ante un 401, `authInterceptor` renueva una sola vez (las peticiones simultáneas comparten la renovación) y reintenta.
- Tras 5 intentos fallidos, la cuenta se bloquea 15 minutos.

## Alternativas consideradas

- **Sesiones de Django con cookie.** Funcionan, pero requieren CSRF en cada escritura y el plan pedía JWT.
- **Tokens en localStorage.** Más simple, pero vulnerable a XSS.

## Consecuencias

- Un script inyectado no puede leer el refresh; el access robado caduca en 15 minutos.
- Sin HTTPS la cookie `Secure` no se envía: el modo de demostración sin HTTPS (`docker-compose.http.yml`) no mantiene la sesión del panel al recargar.
- El panel y la API deben servirse desde el mismo dominio (Nginx lo resuelve con `/admin/` y `/api/`).
