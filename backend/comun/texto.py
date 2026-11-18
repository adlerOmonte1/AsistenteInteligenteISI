"""Utilidades de texto compartidas por NLU, recuperación y validación."""

import re
import unicodedata

_ESPACIOS = re.compile(r"\s+")
_NO_PALABRA = re.compile(r"[^a-z0-9ñ@./\s-]")
_PALABRAS_VACIAS = frozenset(
    "a al algo como con de del el en es esta este la las lo los me mi mis o para por que se si "
    "su sus te tu un una y ya yo le les hay ser son fue pero mas muy sobre cual cuales".split()
)


def quitar_tildes(texto: str) -> str:
    descompuesto = unicodedata.normalize("NFD", texto)
    sin_marcas = "".join(c for c in descompuesto if unicodedata.category(c) != "Mn" or c == "\u0303")
    return unicodedata.normalize("NFC", sin_marcas)


def normalizar(texto: str) -> str:
    """Minúsculas, sin tildes (conserva la ñ), sin signos y con espacios simples."""
    texto = quitar_tildes(texto.lower())
    texto = _NO_PALABRA.sub(" ", texto)
    return _ESPACIOS.sub(" ", texto).strip()


def tokenizar(texto: str, quitar_vacias: bool = True) -> list[str]:
    tokens = normalizar(texto).replace("/", " ").split()
    if quitar_vacias:
        tokens = [t for t in tokens if t not in _PALABRAS_VACIAS]
    return tokens


def fragmentar(texto: str, tamano: int = 24):
    """Divide un texto en trozos para simular la salida en streaming."""
    palabras = texto.split(" ")
    for i in range(0, len(palabras), tamano):
        trozo = " ".join(palabras[i : i + tamano])
        yield trozo if i + tamano >= len(palabras) else trozo + " "
