"""Autenticación del panel: bloqueo por intentos y cookie del refresh."""

from django.conf import settings
from django.contrib.auth import authenticate
from django.core.cache import cache
from rest_framework_simplejwt.tokens import RefreshToken

from comun.excepciones import ErrorDeNegocio


class CuentaBloqueada(ErrorDeNegocio):
    status_code = 429
    default_detail = "Demasiados intentos fallidos. Intente de nuevo en unos minutos."
    default_code = "cuenta_bloqueada"


class CredencialesInvalidas(ErrorDeNegocio):
    status_code = 401
    default_detail = "Usuario o contraseña incorrectos."
    default_code = "credenciales_invalidas"


def _clave_intentos(username: str) -> str:
    return f"login:intentos:{username.lower()}"


def emitir_refresh(usuario) -> RefreshToken:
    refresh = RefreshToken.for_user(usuario)
    refresh["rol"] = usuario.rol
    return refresh


def iniciar_sesion(username: str, password: str):
    cfg = settings.ASISTENTE
    clave = _clave_intentos(username)
    intentos = cache.get(clave, 0)
    if intentos >= cfg["INTENTOS_LOGIN"]:
        raise CuentaBloqueada()

    usuario = authenticate(username=username, password=password)
    if usuario is None or not usuario.is_active:
        cache.set(clave, intentos + 1, timeout=cfg["BLOQUEO_LOGIN_MINUTOS"] * 60)
        raise CredencialesInvalidas()

    cache.delete(clave)
    return usuario, emitir_refresh(usuario)


def poner_cookie_refresh(respuesta, refresh_token: str):
    cfg = settings.COOKIE_REFRESH
    respuesta.set_cookie(
        cfg["NOMBRE"],
        refresh_token,
        max_age=int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()),
        httponly=True,
        secure=cfg["SECURE"],
        samesite=cfg["SAMESITE"],
        path=cfg["RUTA"],
    )


def borrar_cookie_refresh(respuesta):
    cfg = settings.COOKIE_REFRESH
    respuesta.delete_cookie(cfg["NOMBRE"], path=cfg["RUTA"], samesite=cfg["SAMESITE"])


def leer_cookie_refresh(request) -> str | None:
    return request.COOKIES.get(settings.COOKIE_REFRESH["NOMBRE"])
