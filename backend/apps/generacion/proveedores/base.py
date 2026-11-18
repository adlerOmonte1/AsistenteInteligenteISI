"""Contratos que cumple cualquier proveedor de modelo de lenguaje o de embeddings.

El resto del sistema solo conoce estas interfaces. Cambiar de Gemini a otro
proveedor es cambiar variables de entorno, no código (ADR-0004).
"""

import math
from dataclasses import dataclass
from typing import Protocol


class ErrorProveedor(Exception):
    """El proveedor externo no respondió o respondió algo inutilizable."""


@dataclass(frozen=True)
class ResultadoLLM:
    texto: str
    tokens_entrada: int = 0
    tokens_salida: int = 0


class ProveedorLLM(Protocol):
    nombre: str

    def generar(self, sistema: str, usuario: str, max_tokens: int, temperatura: float = 0.0) -> ResultadoLLM: ...


class ProveedorEmbeddings(Protocol):
    nombre: str
    dimensiones: int

    def embeber(self, textos: list[str], tipo: str = "consulta", reintentos: int = 0) -> list[list[float]]:
        """``tipo`` es ``consulta`` (pregunta del estudiante) o ``documento`` (sección indexada).

        ``reintentos``: veces que se espera y repite ante un límite de cuota (procesos por lotes).
        """
        ...


def normalizar_vector(vector: list[float]) -> list[float]:
    norma = math.sqrt(sum(v * v for v in vector))
    if norma == 0:
        return vector
    return [v / norma for v in vector]


def estimar_tokens(texto: str) -> int:
    """Aproximación de 4 caracteres por token, suficiente para estimar costos."""
    return max(1, len(texto) // 4)
