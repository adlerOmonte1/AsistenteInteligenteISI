"""Proveedores sin red, para desarrollo, pruebas y como respaldo.

- ``EmbeddingsLocales`` proyecta palabras, pares de palabras y trigramas de
  caracteres en un vector de 768 posiciones (hashing trick). Capta similitud
  léxica, no semántica, pero basta para trabajar sin clave de API y mantiene
  el sistema respondiendo si el proveedor externo cae.
- ``LLMExtractivo`` no redacta: arma la respuesta copiando las secciones
  recuperadas y citando su código. Nunca inventa datos.
"""

import hashlib
import re

from comun.texto import normalizar, tokenizar

from .base import ResultadoLLM, estimar_tokens, normalizar_vector

_BLOQUE_FICHA = re.compile(
    r"\[FICHA (?P<codigo>[A-Z]{3}_[A-Z0-9_]+) · (?P<seccion>[^\]]+)\]\n(?P<texto>.*?)(?=\n\[FICHA |\Z)", re.S
)


def _indice(rasgo: str, dimensiones: int) -> tuple[int, float]:
    digest = hashlib.blake2b(rasgo.encode("utf-8"), digest_size=8).digest()
    valor = int.from_bytes(digest, "little")
    return valor % dimensiones, 1.0 if (valor >> 63) & 1 else -1.0


class EmbeddingsLocales:
    nombre = "local"

    def __init__(self, dimensiones: int = 768):
        self.dimensiones = dimensiones

    def _vector(self, texto: str) -> list[float]:
        vector = [0.0] * self.dimensiones
        tokens = tokenizar(texto)
        rasgos: list[tuple[str, float]] = [(f"p:{t}", 1.0) for t in tokens]
        rasgos += [(f"b:{a}_{b}", 0.7) for a, b in zip(tokens, tokens[1:], strict=False)]
        for token in tokens:
            marcado = f"#{token}#"
            rasgos += [(f"c:{marcado[i : i + 3]}", 0.35) for i in range(len(marcado) - 2)]
        for rasgo, peso in rasgos:
            posicion, signo = _indice(rasgo, self.dimensiones)
            vector[posicion] += signo * peso
        return normalizar_vector(vector)

    def embeber(self, textos: list[str], tipo: str = "consulta", reintentos: int = 0) -> list[list[float]]:
        return [self._vector(t) for t in textos]


class LLMExtractivo:
    nombre = "local"

    def generar(self, sistema: str, usuario: str, max_tokens: int, temperatura: float = 0.0) -> ResultadoLLM:
        bloques = list(_BLOQUE_FICHA.finditer(usuario))
        if not bloques:
            texto = "No encuentro esa información en las fichas del programa."
        else:
            partes = ["Según la información oficial del programa:"]
            for bloque in bloques[:3]:
                contenido = bloque.group("texto").strip()
                partes.append(f"\n**{bloque.group('seccion').strip()}** ({bloque.group('codigo')}):\n{contenido}")
            texto = "\n".join(partes)
        return ResultadoLLM(texto, estimar_tokens(sistema + usuario), estimar_tokens(texto))


def similitud_lexica(a: str, b: str) -> float:
    """Coeficiente de Jaccard entre palabras normalizadas; útil en pruebas."""
    ta, tb = set(normalizar(a).split()), set(normalizar(b).split())
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)
