"""Adaptador para cualquier API con el formato de OpenAI (OpenAI, DeepSeek, Groq, Mistral...)."""

import httpx

from .base import ErrorProveedor, ResultadoLLM, normalizar_vector

URL_POR_DEFECTO = "https://api.openai.com/v1"


class _ClienteOpenAI:
    def __init__(self, api_key: str, modelo: str, url_base: str = "", timeout: float = 30):
        if not api_key:
            raise ErrorProveedor("Falta la API key del proveedor (LLM_API_KEY).")
        self.modelo = modelo
        self.url = (url_base or URL_POR_DEFECTO).rstrip("/")
        self.cliente = httpx.Client(timeout=timeout, headers={"Authorization": f"Bearer {api_key}"})

    def _post(self, ruta: str, cuerpo: dict) -> dict:
        try:
            respuesta = self.cliente.post(f"{self.url}/{ruta}", json=cuerpo)
            respuesta.raise_for_status()
            return respuesta.json()
        except httpx.HTTPStatusError as exc:
            raise ErrorProveedor(
                f"El proveedor respondió {exc.response.status_code}: {exc.response.text[:300]}"
            ) from exc
        except httpx.HTTPError as exc:
            raise ErrorProveedor(f"No se pudo contactar al proveedor: {exc}") from exc


class LLMOpenAICompatible(_ClienteOpenAI):
    nombre = "openai"

    def generar(self, sistema: str, usuario: str, max_tokens: int, temperatura: float = 0.0) -> ResultadoLLM:
        datos = self._post(
            "chat/completions",
            {
                "model": self.modelo,
                "messages": [{"role": "system", "content": sistema}, {"role": "user", "content": usuario}],
                "temperature": temperatura,
                "max_tokens": max_tokens,
            },
        )
        try:
            texto = datos["choices"][0]["message"]["content"] or ""
        except (KeyError, IndexError) as exc:
            raise ErrorProveedor("El proveedor no devolvió texto.") from exc
        uso = datos.get("usage", {})
        return ResultadoLLM(texto.strip(), uso.get("prompt_tokens", 0), uso.get("completion_tokens", 0))


class EmbeddingsOpenAICompatible(_ClienteOpenAI):
    nombre = "openai"

    def __init__(self, *args, dimensiones: int = 768, **kwargs):
        super().__init__(*args, **kwargs)
        self.dimensiones = dimensiones

    def embeber(self, textos: list[str], tipo: str = "consulta", reintentos: int = 0) -> list[list[float]]:
        datos = self._post("embeddings", {"model": self.modelo, "input": textos, "dimensions": self.dimensiones})
        filas = sorted(datos.get("data", []), key=lambda d: d.get("index", 0))
        if len(filas) != len(textos):
            raise ErrorProveedor("El proveedor devolvió un número distinto de embeddings.")
        return [normalizar_vector(f["embedding"]) for f in filas]
