"""Elige el proveedor según la configuración del entorno."""

from functools import lru_cache

from django.conf import settings

from .base import ErrorProveedor, ProveedorEmbeddings, ProveedorLLM
from .local import EmbeddingsLocales, LLMExtractivo


@lru_cache(maxsize=1)
def obtener_llm() -> ProveedorLLM:
    cfg = settings.LLM
    proveedor = cfg["PROVEEDOR"]
    if proveedor == "local":
        return LLMExtractivo()
    argumentos = {
        "api_key": cfg["API_KEY"],
        "modelo": cfg["MODELO"],
        "url_base": cfg["URL_BASE"],
        "timeout": cfg["TIMEOUT"],
    }
    if proveedor == "gemini":
        from .gemini import LLMGemini

        return LLMGemini(**argumentos)
    if proveedor == "openai":
        from .openai_compatible import LLMOpenAICompatible

        return LLMOpenAICompatible(**argumentos)
    raise ErrorProveedor(f"Proveedor de LLM desconocido: {proveedor}")


@lru_cache(maxsize=1)
def obtener_embeddings() -> ProveedorEmbeddings:
    cfg = settings.EMBEDDINGS
    proveedor = cfg["PROVEEDOR"]
    if proveedor == "local":
        return EmbeddingsLocales(cfg["DIMENSIONES"])
    argumentos = {
        "api_key": cfg["API_KEY"],
        "modelo": cfg["MODELO"],
        "url_base": cfg["URL_BASE"],
        "dimensiones": cfg["DIMENSIONES"],
    }
    if proveedor == "gemini":
        from .gemini import EmbeddingsGemini

        return EmbeddingsGemini(**argumentos)
    if proveedor == "openai":
        from .openai_compatible import EmbeddingsOpenAICompatible

        return EmbeddingsOpenAICompatible(**argumentos)
    raise ErrorProveedor(f"Proveedor de embeddings desconocido: {proveedor}")


def embeber_con_respaldo(textos: list[str], tipo: str = "consulta") -> tuple[list[list[float]], str]:
    """Embebe con el proveedor configurado; si falla, usa el local.

    Devuelve los vectores y el nombre del proveedor usado. Mezclar vectores de
    dos proveedores en una misma búsqueda no tiene sentido, así que quien
    llama decide qué hacer cuando el respaldo entra en juego.
    """
    proveedor = obtener_embeddings()
    try:
        return proveedor.embeber(textos, tipo), proveedor.nombre
    except ErrorProveedor:
        if proveedor.nombre == "local":
            raise
        return EmbeddingsLocales(settings.EMBEDDINGS["DIMENSIONES"]).embeber(textos, tipo), "local"
