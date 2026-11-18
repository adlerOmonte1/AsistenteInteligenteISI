"""Formato uniforme de error para toda la API.

Cualquier error llega al cliente como ``{"detalle": str, "errores": {...}}``.
El panel muestra ``detalle`` en un aviso y ``errores`` junto a cada campo.
"""

from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import exception_handler


class ErrorDeNegocio(APIException):
    """Una regla del dominio impide la operación (no es un error del cliente HTTP)."""

    status_code = status.HTTP_409_CONFLICT
    default_detail = "La operación no está permitida en el estado actual."
    default_code = "regla_de_negocio"


def manejar_excepcion(exc, context):
    respuesta = exception_handler(exc, context)
    if respuesta is None:
        return None
    datos = respuesta.data
    if isinstance(datos, dict) and set(datos) == {"detail"}:
        cuerpo = {"detalle": str(datos["detail"]), "errores": {}}
    elif isinstance(datos, dict):
        cuerpo = {"detalle": "Revise los datos enviados.", "errores": datos}
    else:
        cuerpo = {"detalle": "Revise los datos enviados.", "errores": {"no_field_errors": datos}}
    return Response(cuerpo, status=respuesta.status_code, headers=respuesta.headers)
