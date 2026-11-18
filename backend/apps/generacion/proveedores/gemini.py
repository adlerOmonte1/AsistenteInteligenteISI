"""Adaptador para la API de Gemini (Google AI Studio), por REST y sin SDK."""

import logging
import os
import re
import time

import httpx

from .base import ErrorProveedor, ResultadoLLM, normalizar_vector

logger = logging.getLogger(__name__)

URL_POR_DEFECTO = "https://generativelanguage.googleapis.com/v1beta"
# El plan gratuito cuenta cada texto de un lote como una petición: lotes chicos y
# esperas entre ellos evitan agotar la cuota por minuto.
TAMANO_LOTE = int(os.environ.get("EMBED_LOTE", "50"))
PAUSA_ENTRE_LOTES = float(os.environ.get("EMBED_PAUSA", "0"))
REINTENTOS_429 = int(os.environ.get("GEMINI_REINTENTOS", "4"))
RE_ESPERA = re.compile(r'"retryDelay":\s*"(\d+)(?:\.\d+)?s"')


class _ClienteGemini:
    def __init__(self, api_key: str, modelo: str, url_base: str = "", timeout: float = 30):
        if not api_key:
            raise ErrorProveedor("Falta la API key de Gemini (LLM_API_KEY).")
        self.modelo = modelo
        self.url = (url_base or URL_POR_DEFECTO).rstrip("/")
        self.cliente = httpx.Client(timeout=timeout, headers={"x-goog-api-key": api_key})

    def _post(self, accion: str, cuerpo: dict, reintentos: int = 0) -> dict:
        """Llama a la API. Con ``reintentos`` > 0 espera y repite ante un 429 (cuota por minuto)."""
        for intento in range(reintentos + 1):
            try:
                respuesta = self.cliente.post(f"{self.url}/models/{self.modelo}:{accion}", json=cuerpo)
            except httpx.HTTPError as exc:
                raise ErrorProveedor(f"No se pudo contactar a Gemini: {exc}") from exc
            # La cuota diaria no se libera esperando unos minutos: no tiene sentido reintentar.
            diaria = "per day" in respuesta.text.lower() or "perday" in respuesta.text.lower()
            if respuesta.status_code == 429 and intento < reintentos and not diaria:
                espera = _segundos_de_espera(respuesta.text)
                logger.warning("Gemini 429 (cuota); reintento %s de %s en %s s", intento + 1, reintentos, espera)
                time.sleep(espera)
                continue
            if respuesta.is_error:
                raise ErrorProveedor(_mensaje_de_error(respuesta))
            return respuesta.json()
        raise ErrorProveedor("Gemini no respondió tras los reintentos.")


def _segundos_de_espera(cuerpo: str) -> int:
    m = RE_ESPERA.search(cuerpo)
    return min(int(m.group(1)) + 2, 120) if m else 60


def _mensaje_de_error(respuesta: httpx.Response) -> str:
    try:
        error = respuesta.json()["error"]
        mensaje = error.get("message", "")
        # Google pone el motivo concreto (API_KEY_INVALID, SERVICE_DISABLED...) en details[].reason.
        motivos = [d["reason"] for d in error.get("details", []) if isinstance(d, dict) and d.get("reason")]
        estado = error.get("status", "")
        mensaje = " · ".join(filter(None, [mensaje, estado, *motivos]))
    except (ValueError, KeyError, TypeError, AttributeError):
        mensaje = respuesta.text[:800]
    if respuesta.status_code == 429:
        return (
            "Gemini respondió 429: se agotó la cuota del plan. Si es la cuota por minuto, espere y repita; "
            f"si es la diaria, continúe mañana. Detalle: {mensaje}"
        )
    if respuesta.status_code in (401, 403):
        return (
            f"Gemini rechazó la API key ({respuesta.status_code}): {mensaje}. Revise en AI Studio que la clave "
            "siga activa y sin restricciones, y que el proyecto tenga habilitada la Generative Language API."
        )
    return f"Gemini respondió {respuesta.status_code}: {mensaje}"


class LLMGemini(_ClienteGemini):
    nombre = "gemini"

    def generar(self, sistema: str, usuario: str, max_tokens: int, temperatura: float = 0.0) -> ResultadoLLM:
        datos = self._post(
            "generateContent",
            {
                "systemInstruction": {"parts": [{"text": sistema}]},
                "contents": [{"role": "user", "parts": [{"text": usuario}]}],
                "generationConfig": {"temperature": temperatura, "maxOutputTokens": max_tokens},
            },
        )
        try:
            partes = datos["candidates"][0]["content"]["parts"]
        except (KeyError, IndexError) as exc:
            motivo = datos.get("promptFeedback", {}).get("blockReason", "respuesta vacía")
            raise ErrorProveedor(f"Gemini no devolvió texto ({motivo}).") from exc
        uso = datos.get("usageMetadata", {})
        return ResultadoLLM(
            texto="".join(p.get("text", "") for p in partes).strip(),
            tokens_entrada=uso.get("promptTokenCount", 0),
            tokens_salida=uso.get("candidatesTokenCount", 0),
        )


class EmbeddingsGemini(_ClienteGemini):
    nombre = "gemini"

    def __init__(self, *args, dimensiones: int = 768, **kwargs):
        super().__init__(*args, **kwargs)
        self.dimensiones = dimensiones

    def embeber(self, textos: list[str], tipo: str = "consulta", reintentos: int = 0) -> list[list[float]]:
        """``reintentos`` se usa en procesos por lotes (reindexar); el chat no espera."""
        tarea = "RETRIEVAL_QUERY" if tipo == "consulta" else "RETRIEVAL_DOCUMENT"
        vectores: list[list[float]] = []
        for i in range(0, len(textos), TAMANO_LOTE):
            lote = textos[i : i + TAMANO_LOTE]
            if i and PAUSA_ENTRE_LOTES:
                time.sleep(PAUSA_ENTRE_LOTES)
            datos = self._post(
                "batchEmbedContents",
                {
                    "requests": [
                        {
                            "model": f"models/{self.modelo}",
                            "content": {"parts": [{"text": t}]},
                            "taskType": tarea,
                            "outputDimensionality": self.dimensiones,
                        }
                        for t in lote
                    ]
                },
                reintentos=reintentos,
            )
            # Con dimensiones menores a 3072 Gemini no normaliza; la similitud coseno lo necesita.
            vectores.extend(normalizar_vector(e["values"]) for e in datos.get("embeddings", []))
        if len(vectores) != len(textos):
            raise ErrorProveedor("Gemini devolvió un número distinto de embeddings.")
        return vectores
