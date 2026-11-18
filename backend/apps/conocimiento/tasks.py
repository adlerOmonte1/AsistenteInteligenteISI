"""Tareas en segundo plano (django-q2) de la base de conocimiento."""

import logging

from django.conf import settings

from apps.evaluacion.models import Evaluacion
from apps.evaluacion.services import ejecutar
from apps.recuperacion.services import indexar_version

from .models import VersionFicha

logger = logging.getLogger(__name__)
CASOS_HUMO = 3


def indexar_y_probar(version_id: int):
    """Indexa la versión recién publicada y corre la prueba de humo de su proceso.

    Si la prueba de humo detecta datos inventados, se vuelve a la versión
    anterior: una publicación nunca puede dejar al asistente diciendo algo sin
    respaldo. Los fallos de clasificación se informan, pero no revierten.
    """
    version = VersionFicha.objects.select_related("ficha__proceso").get(pk=version_id)
    indexar_version(version)

    evaluacion = Evaluacion.objects.create(
        proceso=version.ficha.proceso, motivo=Evaluacion.Motivo.HUMO, limite_casos=CASOS_HUMO
    )
    evaluacion = ejecutar(evaluacion.id)
    if evaluacion.metricas.get("datos_inventados"):
        anterior = version.ficha.versiones.filter(numero__lt=version.numero).first()
        if anterior is not None:
            from .services.publicacion import revertir

            logger.warning("Prueba de humo fallida en %s; se revierte a v%s", version, anterior.numero)
            revertir(version.ficha, anterior.numero, None)
    return evaluacion.id


def embeber_intent(intent_id: int):
    from apps.nlu.services import embeber_ejemplos

    from .models import Intent

    return embeber_ejemplos(Intent.objects.get(pk=intent_id))


def procesar_carga(carga_id: int):
    from .services.propuesta import procesar

    return procesar(carga_id)


def reindexar_conocimiento():
    from apps.nlu.services import embeber_ejemplos
    from apps.recuperacion.services import reindexar_todo

    return {
        "secciones": reindexar_todo(),
        "ejemplos": embeber_ejemplos(),
        "proveedor": settings.EMBEDDINGS["PROVEEDOR"],
    }
