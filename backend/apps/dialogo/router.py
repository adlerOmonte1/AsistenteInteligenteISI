"""Decide por qué vía se responde una pregunta (docs/03-arquitectura/base-conocimiento/arquitectura_hibrida.md §4)."""

from dataclasses import dataclass
from enum import StrEnum


class Via(StrEnum):
    DETERMINISTA = "determinista"
    DESAMBIGUACION = "desambiguacion"
    RAG = "rag"
    DERIVACION = "derivacion"
    ACLARACION = "aclaracion"


@dataclass(frozen=True)
class Umbrales:
    determinista: float = 0.75
    desambiguacion: float = 0.40
    intentos_antes_de_derivar: int = 2

    @classmethod
    def desde_configuracion(cls, cfg) -> "Umbrales":
        return cls(cfg.umbral_determinista, cfg.umbral_desambiguacion, cfg.intentos_antes_de_derivar)


def elegir_via(confianza: float, intentos_fallidos: int, umbrales: Umbrales) -> Via:
    if intentos_fallidos >= umbrales.intentos_antes_de_derivar:
        return Via.DERIVACION
    if confianza >= umbrales.determinista:
        return Via.DETERMINISTA
    if confianza >= umbrales.desambiguacion:
        return Via.DESAMBIGUACION
    return Via.RAG
