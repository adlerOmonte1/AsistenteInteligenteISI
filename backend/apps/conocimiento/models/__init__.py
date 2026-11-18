from .catalogo import Facultad, Proceso, Programa
from .documento import CargaDocumento, Documento
from .ficha import SECCIONES, TITULOS_SECCION, Ficha, VersionFicha
from .intent import EjemploIntent, Intent, Pendiente, Plantilla

__all__ = [
    "SECCIONES",
    "TITULOS_SECCION",
    "CargaDocumento",
    "Documento",
    "EjemploIntent",
    "Facultad",
    "Ficha",
    "Intent",
    "Pendiente",
    "Plantilla",
    "Proceso",
    "Programa",
    "VersionFicha",
]
