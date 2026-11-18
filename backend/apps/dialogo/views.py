"""Canal del chat: recibe el mensaje y responde con eventos SSE.

Eventos (tipos en frontend/projects/shared/src/lib/models/chat.model.ts):

    event: token     data: {"t": "..."}
    event: opciones  data: {"opciones": [{"etiqueta": "...", "intent": "...", "ficha": "..."}]}
    event: fuentes   data: {"fichas": [{"codigo": "BAC_P02", "titulo": "...", "proceso": "..."}]}
    event: fin       data: {"consultaId": 1234, "via": "determinista", "derivada": false}
    event: error     data: {"mensaje": "..."}
"""

import json
import logging
import uuid

from django.conf import settings
from django.http import StreamingHttpResponse
from drf_spectacular.utils import extend_schema
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.renderers import BaseRenderer, JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.analitica.models import Consulta
from comun.permisos import EsEditor
from comun.texto import fragmentar

from . import limites
from .orquestador import Orquestador

logger = logging.getLogger(__name__)
MENSAJE_ERROR = "El servicio no está disponible en este momento. Intente nuevamente en unos minutos."


class MensajeSerializer(serializers.Serializer):
    sesion = serializers.UUIDField()
    mensaje = serializers.CharField(max_length=settings.ASISTENTE["LONGITUD_MAXIMA_MENSAJE"], trim_whitespace=True)
    intent = serializers.CharField(max_length=80, required=False, allow_blank=True)
    ficha = serializers.CharField(max_length=30, required=False, allow_blank=True)


def _evento(tipo: str, datos: dict) -> str:
    return f"event: {tipo}\ndata: {json.dumps(datos, ensure_ascii=False)}\n\n"


def _flujo(datos: dict):
    try:
        r = Orquestador().responder(
            datos["sesion"], datos["mensaje"], datos.get("intent") or None, datos.get("ficha") or None
        )
    except Exception:
        logger.exception("Fallo al responder en el chat")
        yield _evento("error", {"mensaje": MENSAJE_ERROR})
        return
    for trozo in fragmentar(r.texto):
        yield _evento("token", {"t": trozo})
    if r.opciones:
        yield _evento("opciones", {"opciones": r.opciones})
    if r.fichas:
        yield _evento("fuentes", {"fichas": r.fichas})
    yield _evento("fin", {"consultaId": r.consulta_id, "via": r.via.value, "derivada": r.derivada})


class EventStreamRenderer(BaseRenderer):
    """Permite que el cliente pida ``Accept: text/event-stream``.

    El flujo SSE no pasa por aquí (es un StreamingHttpResponse); este renderer
    solo da formato JSON a los errores (400, 429) de esa misma petición.
    """

    media_type = "text/event-stream"
    format = "sse"
    charset = "utf-8"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        return json.dumps(data, ensure_ascii=False).encode("utf-8")


class ChatView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    renderer_classes = [JSONRenderer, EventStreamRenderer]

    @extend_schema(request=MensajeSerializer, responses={(200, "text/event-stream"): str})
    def post(self, request):
        datos = MensajeSerializer(data=request.data)
        datos.is_valid(raise_exception=True)
        if limites.excede_limite(str(datos.validated_data["sesion"]), limites.ip_cliente(request)):
            return Response(
                {"detalle": "Ha enviado muchos mensajes. Espere unos minutos e intente de nuevo.", "errores": {}},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )
        respuesta = StreamingHttpResponse(_flujo(datos.validated_data), content_type="text/event-stream")
        respuesta["Cache-Control"] = "no-cache"
        respuesta["X-Accel-Buffering"] = "no"
        return respuesta


class FeedbackSerializer(serializers.Serializer):
    sesion = serializers.UUIDField()
    util = serializers.BooleanField()


class FeedbackView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(request=FeedbackSerializer, responses={204: None})
    def post(self, request, consulta_id: int):
        datos = FeedbackSerializer(data=request.data)
        datos.is_valid(raise_exception=True)
        # Solo la misma sesión que hizo la pregunta puede calificarla.
        actualizadas = Consulta.objects.filter(pk=consulta_id, sesion=datos.validated_data["sesion"]).update(
            util=datos.validated_data["util"]
        )
        if not actualizadas:
            return Response({"detalle": "Consulta no encontrada.", "errores": {}}, status=404)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProbadorSerializer(serializers.Serializer):
    mensaje = serializers.CharField(max_length=500)
    sesion = serializers.UUIDField(required=False)


class ProbadorView(APIView):
    """Pregunta de prueba desde el panel: devuelve la respuesta con su traza y no la registra."""

    permission_classes = [EsEditor]

    @extend_schema(request=ProbadorSerializer, responses=dict)
    def post(self, request):
        datos = ProbadorSerializer(data=request.data)
        datos.is_valid(raise_exception=True)
        sesion = datos.validated_data.get("sesion") or uuid.uuid4()
        r = Orquestador(registrar=False).responder(sesion, datos.validated_data["mensaje"])
        return Response(
            {
                "sesion": str(sesion),
                "texto": r.texto,
                "via": r.via.value,
                "intent": r.intent,
                "confianza": r.confianza,
                "fichas": r.fichas,
                "opciones": r.opciones,
                "derivada": r.derivada,
                "motivo": r.motivo,
                "validacion_fallida": r.validacion_fallida,
                "no_respaldados": r.no_respaldados,
                "traza": r.traza,
            }
        )
