from datetime import datetime

from django.utils import timezone
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import mixins, serializers, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from comun.permisos import EsLector

from . import services
from .models import Consulta


class ConsultaSerializer(serializers.ModelSerializer):
    proceso_nombre = serializers.CharField(source="proceso.nombre", default=None, read_only=True)

    class Meta:
        model = Consulta
        exclude = ["proceso"]


class ConsultaViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """Historial anonimizado de conversaciones para revisar la calidad de las respuestas."""

    serializer_class = ConsultaSerializer
    permission_classes = [EsLector]

    def get_queryset(self):
        qs = Consulta.objects.select_related("proceso")
        p = self.request.query_params
        if p.get("via"):
            qs = qs.filter(via=p["via"])
        if p.get("derivada") in ("true", "false"):
            qs = qs.filter(derivada=p["derivada"] == "true")
        if p.get("util") in ("true", "false"):
            qs = qs.filter(util=p["util"] == "true")
        if p.get("sesion"):
            qs = qs.filter(sesion=p["sesion"])
        if p.get("proceso"):
            qs = qs.filter(proceso__clave=p["proceso"])
        if p.get("q"):
            qs = qs.filter(pregunta__icontains=p["q"])
        return qs


def _fecha(valor: str | None):
    if not valor:
        return None
    return timezone.make_aware(datetime.fromisoformat(valor))


class MetricasResumenView(APIView):
    permission_classes = [EsLector]

    @extend_schema(
        parameters=[OpenApiParameter("desde", str), OpenApiParameter("hasta", str)],
        responses=dict,
    )
    def get(self, request):
        try:
            desde = _fecha(request.query_params.get("desde"))
            hasta = _fecha(request.query_params.get("hasta"))
        except ValueError:
            return Response({"detalle": "Use fechas AAAA-MM-DD.", "errores": {}}, status=400)
        return Response(services.resumen(desde, hasta))
