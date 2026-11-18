# ADR-0011 · Límite de mensajes por sesión y por IP

- Estado: Aceptada
- Fecha: 2026-11-17

## Contexto

El chat es público y cada pregunta abierta puede costar una llamada al LLM. El plan técnico proponía 20 mensajes por hora por IP. En el campus, cientos de estudiantes salen a Internet por la misma IP pública: con ese límite, un salón entero quedaría bloqueado en minutos.

## Decisión

Dos límites con ventana de una hora (`backend/apps/dialogo/limites.py`):

| Clave | Por defecto | Variable |
|---|---|---|
| Sesión anónima del navegador | 30 mensajes | `LIMITE_MENSAJES_SESION_HORA` |
| IP | 300 mensajes | `LIMITE_MENSAJES_IP_HORA` |

La IP se toma de `X-Real-IP`, que pone Nginx; no se confía en `X-Forwarded-For` del cliente. Nginx agrega un tercer límite de ráfagas (30 por minuto con margen de 10) sobre `/api/v1/chat/`.

## Alternativas consideradas

- **Solo por IP.** Bloquea redes compartidas.
- **Solo por sesión.** Basta borrar el `sessionStorage` para evadirlo.

## Consecuencias

- Un estudiante normal nunca llega al límite; un script abusivo sí.
- El costo queda acotado además por el tope de gasto mensual del panel y por el límite del proveedor.
- Si la universidad expone el portal detrás de un proxy propio, hay que configurar Nginx para que confíe en la IP que ese proxy informa.
