"""Validador de salida: ningún dato crítico llega al estudiante sin respaldo.

Extrae de la respuesta los correos, montos, plazos y resoluciones, y exige que
cada uno aparezca en el texto de las fichas citadas. Si alguno no aparece, la
respuesta se descarta y se deriva (docs/03-arquitectura/base-conocimiento/
arquitectura_hibrida.md §6).
"""

import re
from dataclasses import dataclass, field

from comun.texto import quitar_tildes

RE_CORREO = re.compile(r"[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}", re.I)
RE_MONTO = re.compile(r"S/\.?\s*(\d{1,3}(?:[ ,]\d{3})*(?:[.,]\d{1,2})?|\d+(?:[.,]\d{1,2})?)", re.I)
RE_PLAZO = re.compile(
    r"\b(\d{1,3})\s*(?:\(\w+\)\s*)?(d[ií]as?|semanas?|meses|mes|a[nñ]os?|horas?)(\s+h[aá]biles|\s+calendario)?\b",
    re.I,
)
RE_RESOLUCION = re.compile(r"\b(\d{2,5}-\d{4}(?:-[A-Z]{1,6})+)", re.I)


@dataclass
class ResultadoValidacion:
    valida: bool
    no_respaldados: list[str] = field(default_factory=list)


def _monto(texto: str) -> str:
    limpio = texto.replace(" ", "").replace(",", ".")
    if limpio.count(".") > 1:
        limpio = limpio.replace(".", "", limpio.count(".") - 1)
    try:
        return f"{float(limpio):.2f}"
    except ValueError:
        return limpio


def _unidad(texto: str) -> str:
    u = quitar_tildes(texto.lower())
    for raiz in ("dia", "semana", "mes", "ano", "hora"):
        if u.startswith(raiz):
            return raiz
    return u


def extraer_datos(texto: str) -> dict[str, set[str]]:
    plano = quitar_tildes(texto)
    return {
        "correos": {c.lower().rstrip(".") for c in RE_CORREO.findall(texto)},
        "montos": {_monto(m) for m in RE_MONTO.findall(texto)},
        "plazos": {f"{n} {_unidad(u)}" for n, u, _ in RE_PLAZO.findall(plano)},
        "resoluciones": {r.upper() for r in RE_RESOLUCION.findall(texto)},
    }


def validar(respuesta: str, textos_fuente: list[str]) -> ResultadoValidacion:
    """Compara los datos de la respuesta contra la unión de los textos de las fichas citadas."""
    en_respuesta = extraer_datos(respuesta)
    en_fuente = extraer_datos("\n".join(textos_fuente))
    faltan = []
    for tipo, valores in en_respuesta.items():
        for valor in sorted(valores - en_fuente[tipo]):
            faltan.append(f"{tipo}:{valor}")
    return ResultadoValidacion(valida=not faltan, no_respaldados=faltan)
