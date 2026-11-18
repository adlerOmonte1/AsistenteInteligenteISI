from django.conf import settings
from django.db import connection
from drf_spectacular.utils import extend_schema
from rest_framework import serializers
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from comun.permisos import EsSuperadmin

from .models import Configuracion


class ConfiguracionSerializer(serializers.ModelSerializer):
    proveedor_llm = serializers.SerializerMethodField()
    modelo_llm = serializers.SerializerMethodField()
    proveedor_embeddings = serializers.SerializerMethodField()

    class Meta:
        model = Configuracion
        exclude = ["id", "actualizado_por"]
        read_only_fields = ["actualizado"]

    def get_proveedor_llm(self, _obj):
        return settings.LLM["PROVEEDOR"]

    def get_modelo_llm(self, _obj):
        return settings.LLM["MODELO"]

    def get_proveedor_embeddings(self, _obj):
        return settings.EMBEDDINGS["PROVEEDOR"]

    def validate(self, attrs):
        alto = attrs.get("umbral_determinista", getattr(self.instance, "umbral_determinista", 0.75))
        bajo = attrs.get("umbral_desambiguacion", getattr(self.instance, "umbral_desambiguacion", 0.40))
        if not 0 < bajo < alto <= 1:
            raise serializers.ValidationError(
                {"umbral_desambiguacion": "Debe cumplirse 0 < desambiguación < determinista <= 1."}
            )
        return attrs


class ConfiguracionView(APIView):
    permission_classes = [EsSuperadmin]

    @extend_schema(responses=ConfiguracionSerializer)
    def get(self, request):
        return Response(ConfiguracionSerializer(Configuracion.actual()).data)

    @extend_schema(request=ConfiguracionSerializer, responses=ConfiguracionSerializer)
    def patch(self, request):
        obj = Configuracion.actual()
        datos = ConfiguracionSerializer(obj, data=request.data, partial=True)
        datos.is_valid(raise_exception=True)
        datos.save(actualizado_por=request.user)
        return Response(datos.data)


class ConfiguracionPublicaView(APIView):
    """Textos que el widget necesita al abrirse (sin login)."""

    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(responses=dict)
    def get(self, request):
        cfg = Configuracion.actual()
        return Response({"bienvenida": cfg.mensaje_bienvenida, "aviso_legal": cfg.aviso_legal})


class SaludView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(responses=dict)
    def get(self, request):
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            return Response({"estado": "ok"})
        except Exception:  # noqa: BLE001 - cualquier fallo de la base es "no disponible"
            return Response({"estado": "sin_base_de_datos"}, status=503)
