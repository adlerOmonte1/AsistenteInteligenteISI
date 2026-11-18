"""Tareas programadas de django-q2. Se registran con ``manage.py programar_tareas``."""

import logging

from . import services

logger = logging.getLogger(__name__)


def purgar_consultas_antiguas():
    borradas = services.purgar_antiguas()
    logger.info("Purga de consultas: %s registros eliminados", borradas)
    return borradas
