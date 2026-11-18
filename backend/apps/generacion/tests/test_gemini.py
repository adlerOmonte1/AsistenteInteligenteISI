import httpx
import pytest

from apps.generacion.proveedores import gemini
from apps.generacion.proveedores.base import ErrorProveedor

CUOTA = '{"error": {"code": 429, "message": "Quota exceeded", "details": [{"retryDelay": "7s"}]}}'


def _proveedor(respuestas: list[httpx.Response]):
    pendientes = iter(respuestas)
    proveedor = gemini.EmbeddingsGemini(api_key="prueba", modelo="gemini-embedding-001", dimensiones=3)
    proveedor.cliente = httpx.Client(transport=httpx.MockTransport(lambda _peticion: next(pendientes)))
    return proveedor


@pytest.fixture
def esperas(monkeypatch):
    registro = []
    monkeypatch.setattr(gemini.time, "sleep", registro.append)
    return registro


def test_reintenta_tras_429_esperando_lo_que_indica_gemini(esperas):
    proveedor = _proveedor(
        [httpx.Response(429, text=CUOTA), httpx.Response(200, json={"embeddings": [{"values": [3.0, 0.0, 4.0]}]})]
    )
    vectores = proveedor.embeber(["hola"], reintentos=2)
    assert vectores == [[0.6, 0.0, 0.8]]
    assert esperas == [9]


def test_sin_reintentos_el_429_se_informa_de_inmediato(esperas):
    proveedor = _proveedor([httpx.Response(429, text=CUOTA)])
    with pytest.raises(ErrorProveedor, match="cuota"):
        proveedor.embeber(["hola"])
    assert esperas == []
