from django_q.tasks import async_task
from rest_framework import mixins, serializers, status, viewsets
from rest_framework.permissions import SAFE_METHODS
from rest_framework.response import Response

from apps.conocimiento.models import Proceso
from comun.permisos import EsEditor, EsLector, LecturaLectorEscrituraEditor

from .models import CasoEvaluacion, Evaluacion, ResultadoCaso


class CasoSerializer(serializers.ModelSerializer):
    proceso_clave = serializers.CharField(source="proceso.clave", read_only=True)

    class Meta:
        model = CasoEvaluacion
        fields = "__all__"


class ResultadoSerializer(serializers.ModelSerializer):
    codigo = serializers.CharField(source="caso.codigo", read_only=True)
    pregunta = serializers.CharField(source="caso.pregunta", read_only=True)
    intent_esperado = serializers.CharField(source="caso.intent_esperado", read_only=True)
    ficha_esperada = serializers.CharField(source="caso.ficha_esperada", read_only=True)
    respuesta_clave = serializers.CharField(source="caso.respuesta_clave", read_only=True)

    class Meta:
        model = ResultadoCaso
        exclude = ["evaluacion", "caso"]


class EvaluacionSerializer(serializers.ModelSerializer):
    proceso = serializers.SlugRelatedField(
        slug_field="clave", queryset=Proceso.objects.all(), required=False, allow_null=True
    )
    proceso_nombre = serializers.CharField(source="proceso.nombre", default=None, read_only=True)

    class Meta:
        model = Evaluacion
        fields = [
            "id",
            "proceso",
            "proceso_nombre",
            "estado",
            "motivo",
            "limite_casos",
            "metricas",
            "mensaje",
            "creada",
            "finalizada",
        ]
        read_only_fields = ["estado", "motivo", "metricas", "mensaje", "creada", "finalizada"]


class EvaluacionDetalleSerializer(EvaluacionSerializer):
    resultados = ResultadoSerializer(many=True, read_only=True)

    class Meta(EvaluacionSerializer.Meta):
        fields = [*EvaluacionSerializer.Meta.fields, "resultados"]


class EvaluacionViewSet(
    mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    """POST encola la ejecución del golden set de un proceso (o de todos)."""

    queryset = Evaluacion.objects.select_related("proceso")

    def get_permissions(self):
        return [EsLector()] if self.request.method in SAFE_METHODS else [EsEditor()]

    def get_serializer_class(self):
        return EvaluacionDetalleSerializer if self.action == "retrieve" else EvaluacionSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action == "retrieve":
            qs = qs.prefetch_related("resultados__caso")
        return qs

    def create(self, request, *args, **kwargs):
        datos = self.get_serializer(data=request.data)
        datos.is_valid(raise_exception=True)
        evaluacion = datos.save(iniciada_por=request.user, motivo=Evaluacion.Motivo.MANUAL)
        async_task("apps.evaluacion.tasks.ejecutar_evaluacion", evaluacion.id)
        evaluacion.refresh_from_db()
        return Response(EvaluacionSerializer(evaluacion).data, status=status.HTTP_202_ACCEPTED)


class CasoViewSet(viewsets.ModelViewSet):
    serializer_class = CasoSerializer
    permission_classes = [LecturaLectorEscrituraEditor]
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_queryset(self):
        qs = CasoEvaluacion.objects.select_related("proceso")
        if self.request.query_params.get("proceso"):
            qs = qs.filter(proceso__clave=self.request.query_params["proceso"])
        return qs
