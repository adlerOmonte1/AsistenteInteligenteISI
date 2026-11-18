"""Límite de mensajes por sesión y por IP con ventana fija de una hora.

Se limita por sesión (lo que protege del abuso) y, con un tope mucho más alto,
por IP: en el campus muchos estudiantes comparten la misma IP pública.
"""

import time

from django.conf import settings
from django.core.cache import cache

VENTANA_SEGUNDOS = 3600


def _contar(clave: str) -> int:
    ventana = int(time.time() // VENTANA_SEGUNDOS)
    clave = f"limite:{clave}:{ventana}"
    if cache.add(clave, 1, timeout=VENTANA_SEGUNDOS + 60):
        return 1
    try:
        return cache.incr(clave)
    except ValueError:
        cache.set(clave, 1, timeout=VENTANA_SEGUNDOS + 60)
        return 1


def ip_cliente(request) -> str:
    # Nginx coloca la IP real en X-Real-IP; no se confía en X-Forwarded-For del cliente.
    return request.META.get("HTTP_X_REAL_IP") or request.META.get("REMOTE_ADDR", "")


def excede_limite(sesion: str, ip: str) -> bool:
    cfg = settings.ASISTENTE
    por_sesion = _contar(f"sesion:{sesion}")
    por_ip = _contar(f"ip:{ip}")
    return por_sesion > cfg["LIMITE_MENSAJES_SESION_HORA"] or por_ip > cfg["LIMITE_MENSAJES_IP_HORA"]
