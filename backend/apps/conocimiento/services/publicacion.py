"""Ciclo de cambios de una ficha: borrador → en revisión → publicada (o rechazada).

docs/03-arquitectura/base-conocimiento/flujo_actualizacion_admin.md describe el
flujo con Git; aquí se implementa el mismo flujo sin que el personal
administrativo use Git.
"""

from django.db import transaction
from django.db.models import Max
from django_q.tasks import async_task
from rest_framework.exceptions import ValidationError

from comun.excepciones import ErrorDeNegocio

from ..models import Ficha, VersionFicha
from .contrato import errores_de_ficha

Estado = Ficha.EstadoRevision


def _exigir_estado(ficha: Ficha, *permitidos: str):
    if ficha.estado_revision not in permitidos:
        raise ErrorDeNegocio(f"La ficha está «{ficha.get_estado_revision_display()}» y no admite esta acción.")


def marcar_editada(ficha: Ficha, usuario):
    """Se llama al guardar cambios del editor: la ficha vuelve a borrador."""
    _exigir_estado(ficha, Estado.BORRADOR, Estado.PUBLICADA, Estado.RECHAZADA)
    ficha.estado_revision = Estado.BORRADOR
    ficha.actualizada_por = usuario


@transaction.atomic
def enviar_a_revision(ficha: Ficha, usuario) -> Ficha:
    _exigir_estado(ficha, Estado.BORRADOR, Estado.RECHAZADA)
    errores = errores_de_ficha(ficha)
    if errores:
        raise ValidationError(errores)
    if not ficha.tiene_cambios_sin_publicar:
        raise ErrorDeNegocio("La ficha no tiene cambios respecto de la versión publicada.")
    ficha.estado_revision = Estado.EN_REVISION
    ficha.observaciones = ""
    ficha.actualizada_por = usuario
    ficha.save()
    return ficha


def _siguiente_numero(ficha: Ficha) -> int:
    return (ficha.versiones.aggregate(m=Max("numero"))["m"] or 0) + 1


@transaction.atomic
def publicar(
    ficha: Ficha, usuario, nota: str = "", indexar_en_segundo_plano: bool = True, indexar: bool = True
) -> VersionFicha:
    version = VersionFicha.objects.create(
        ficha=ficha,
        numero=_siguiente_numero(ficha),
        contenido=ficha.contenido(),
        nota=nota[:300],
        publicada_por=usuario,
    )
    ficha.version_publicada = version
    ficha.estado_revision = Estado.PUBLICADA
    ficha.observaciones = ""
    ficha.save()
    if not indexar:
        # El índice anterior de la ficha deja de valer; `reindexar` crea el nuevo.
        from apps.recuperacion.models import SeccionIndexada

        SeccionIndexada.objects.filter(ficha=ficha, vigente=True).update(vigente=False)
    elif indexar_en_segundo_plano:
        transaction.on_commit(lambda: async_task("apps.conocimiento.tasks.indexar_y_probar", version.id))
    else:
        from apps.recuperacion.services import indexar_version

        indexar_version(version)
    return version


def aprobar(ficha: Ficha, revisor, nota: str = "") -> VersionFicha:
    _exigir_estado(ficha, Estado.EN_REVISION)
    if ficha.actualizada_por_id == revisor.id and revisor.rol != "superadmin":
        raise ErrorDeNegocio("Quien editó la ficha no puede aprobarla. Pida la revisión a otra persona.")
    return publicar(ficha, revisor, nota or "Aprobada en revisión")


@transaction.atomic
def rechazar(ficha: Ficha, revisor, observaciones: str) -> Ficha:
    _exigir_estado(ficha, Estado.EN_REVISION)
    if not observaciones.strip():
        raise ValidationError({"observaciones": "Explique qué debe corregirse."})
    ficha.estado_revision = Estado.RECHAZADA
    ficha.observaciones = observaciones.strip()
    ficha.save()
    return ficha


@transaction.atomic
def revertir(ficha: Ficha, numero: int, usuario) -> VersionFicha:
    """Publica de nuevo el contenido de una versión anterior como versión nueva."""
    _exigir_estado(ficha, Estado.BORRADOR, Estado.PUBLICADA, Estado.RECHAZADA)
    try:
        anterior = ficha.versiones.get(numero=numero)
    except VersionFicha.DoesNotExist as exc:
        raise ErrorDeNegocio(f"La ficha no tiene versión {numero}.") from exc
    ficha.aplicar_contenido(anterior.contenido)
    return publicar(ficha, usuario, nota=f"Reversión a la versión {numero}")
