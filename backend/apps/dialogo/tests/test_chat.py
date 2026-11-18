import json

import pytest
from django.urls import reverse

from apps.analitica.models import Consulta
from apps.dialogo.orquestador import Orquestador
from apps.dialogo.router import Via

pytestmark = pytest.mark.django_db


def _eventos(respuesta) -> list[tuple[str, dict]]:
    cuerpo = b"".join(respuesta.streaming_content).decode("utf-8")
    eventos = []
    for bloque in cuerpo.strip().split("\n\n"):
        tipo, datos = bloque.split("\n", 1)
        eventos.append((tipo.removeprefix("event: "), json.loads(datos.removeprefix("data: "))))
    return eventos


def test_pregunta_conocida_responde_por_via_determinista_con_su_ficha(intent_fotos, sesion):
    r = Orquestador().responder(sesion, "cuántas fotos necesito para el bachiller")
    assert r.via is Via.DETERMINISTA
    assert r.fichas[0]["codigo"] == "BAC_P02"
    assert "4 cm x 5 cm" in r.texto
    assert Consulta.objects.get(pk=r.consulta_id).via == "determinista"


def test_pregunta_fuera_de_tema_no_inventa_y_deriva_al_segundo_intento(intent_fotos, sesion):
    primera = Orquestador().responder(sesion, "cuál es la capital de Francia")
    segunda = Orquestador().responder(sesion, "y quién ganó el mundial")
    assert primera.via is Via.RAG and not primera.fichas
    assert segunda.via is Via.DERIVACION and segunda.derivada


def test_chat_emite_eventos_sse_y_registra_la_consulta(api, intent_fotos, sesion):
    respuesta = api.post(
        reverse("chat"), {"sesion": str(sesion), "mensaje": "fotos para el grado de bachiller"}, format="json"
    )
    assert respuesta["Content-Type"] == "text/event-stream"
    eventos = _eventos(respuesta)
    tipos = [t for t, _ in eventos]
    assert tipos[0] == "token" and tipos[-1] == "fin"
    assert (
        "fuentes",
        {
            "fichas": [
                {
                    "codigo": "BAC_P02",
                    "titulo": "Foto digital y entrega de fotos físicas",
                    "proceso": "bachiller_conv_ppp",
                }
            ]
        },
    ) in eventos
    fin = eventos[-1][1]
    assert Consulta.objects.filter(pk=fin["consultaId"], sesion=sesion).exists()


def test_mensaje_demasiado_largo_se_rechaza(api, sesion):
    respuesta = api.post(reverse("chat"), {"sesion": str(sesion), "mensaje": "x" * 501}, format="json")
    assert respuesta.status_code == 400


def test_limite_de_mensajes_por_sesion(api, intent_fotos, sesion, settings):
    settings.ASISTENTE = {**settings.ASISTENTE, "LIMITE_MENSAJES_SESION_HORA": 2}
    for _ in range(2):
        api.post(reverse("chat"), {"sesion": str(sesion), "mensaje": "hola"}, format="json")
    respuesta = api.post(reverse("chat"), {"sesion": str(sesion), "mensaje": "hola"}, format="json")
    assert respuesta.status_code == 429


def test_feedback_solo_desde_la_misma_sesion(api, intent_fotos, sesion):
    r = Orquestador().responder(sesion, "cuántas fotos necesito para el bachiller")
    url = reverse("chat-feedback", args=[r.consulta_id])
    otra = api.post(url, {"sesion": "00000000-0000-0000-0000-000000000000", "util": True}, format="json")
    assert otra.status_code == 404
    assert api.post(url, {"sesion": str(sesion), "util": True}, format="json").status_code == 204
    assert Consulta.objects.get(pk=r.consulta_id).util is True
