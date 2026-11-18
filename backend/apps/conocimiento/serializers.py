from django.conf import settings
from rest_framework import serializers

from .models import (
    SECCIONES,
    CargaDocumento,
    Documento,
    EjemploIntent,
    Facultad,
    Ficha,
    Intent,
    Pendiente,
    Plantilla,
    Proceso,
    Programa,
    VersionFicha,
)
from .services.propuesta import extension_valida

TAMANO_MAXIMO = 10 * 1024 * 1024


# ---------------------------------------------------------------- catálogo


class FacultadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Facultad
        fields = ["id", "nombre", "sigla", "activa"]


class ProgramaSerializer(serializers.ModelSerializer):
    facultad_nombre = serializers.CharField(source="facultad.nombre", read_only=True)

    class Meta:
        model = Programa
        fields = ["id", "facultad", "facultad_nombre", "nombre", "sigla", "activo"]


class ProcesoSerializer(serializers.ModelSerializer):
    programa_nombre = serializers.CharField(source="programa.nombre", read_only=True)
    total_fichas = serializers.IntegerField(read_only=True, default=0)
    fichas_publicadas = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Proceso
        fields = [
            "id",
            "programa",
            "programa_nombre",
            "clave",
            "nombre",
            "descripcion",
            "prefijos",
            "orden",
            "activo",
            "visible_en_portal",
            "total_fichas",
            "fichas_publicadas",
        ]


# ------------------------------------------------------------------- fichas


class VersionFichaSerializer(serializers.ModelSerializer):
    publicada_por = serializers.CharField(source="publicada_por.username", default=None, read_only=True)

    class Meta:
        model = VersionFicha
        fields = ["id", "numero", "contenido", "nota", "publicada_en", "publicada_por"]


class FichaListaSerializer(serializers.ModelSerializer):
    proceso_clave = serializers.CharField(source="proceso.clave", read_only=True)
    proceso_nombre = serializers.CharField(source="proceso.nombre", read_only=True)
    version = serializers.IntegerField(source="version_publicada.numero", default=None, read_only=True)
    actualizada_por = serializers.CharField(source="actualizada_por.username", default=None, read_only=True)

    class Meta:
        model = Ficha
        fields = [
            "id",
            "codigo",
            "proceso",
            "proceso_clave",
            "proceso_nombre",
            "fase",
            "titulo",
            "estado_dato",
            "estado_revision",
            "version",
            "actualizada",
            "actualizada_por",
        ]


class FichaSerializer(serializers.ModelSerializer):
    proceso_clave = serializers.CharField(source="proceso.clave", read_only=True)
    proceso_nombre = serializers.CharField(source="proceso.nombre", read_only=True)
    version = serializers.IntegerField(source="version_publicada.numero", default=None, read_only=True)
    tiene_cambios_sin_publicar = serializers.BooleanField(read_only=True)
    actualizada_por = serializers.CharField(source="actualizada_por.username", default=None, read_only=True)

    class Meta:
        model = Ficha
        fields = [
            "id",
            "proceso",
            "proceso_clave",
            "proceso_nombre",
            "codigo",
            "fase",
            "titulo",
            "fuente",
            "vigencia",
            "vigencia_texto",
            "estado_dato",
            *SECCIONES,
            "informacion_adicional",
            "palabras_clave",
            "estado_revision",
            "observaciones",
            "version",
            "tiene_cambios_sin_publicar",
            "reemplazada_por",
            "creada",
            "actualizada",
            "actualizada_por",
        ]
        read_only_fields = ["estado_revision", "observaciones", "creada", "actualizada"]

    def validate(self, attrs):
        if self.instance and "codigo" in attrs and attrs["codigo"] != self.instance.codigo:
            if self.instance.version_publicada_id:
                raise serializers.ValidationError(
                    {"codigo": "El código de una ficha publicada no cambia; las respuestas lo citan."}
                )
        return attrs


class PublicaFichaSerializer(serializers.Serializer):
    """Contenido publicado de una ficha, tal como lo ve el estudiante en el portal."""

    codigo = serializers.CharField()
    contenido = serializers.JSONField()
    version = serializers.IntegerField()
    publicada_en = serializers.DateTimeField()


# ------------------------------------------------------------------ intents


class EjemploSerializer(serializers.ModelSerializer):
    class Meta:
        model = EjemploIntent
        fields = ["id", "texto"]


class IntentSerializer(serializers.ModelSerializer):
    proceso_clave = serializers.CharField(source="proceso.clave", read_only=True)
    ejemplos = serializers.ListField(child=serializers.CharField(max_length=500), write_only=True, required=False)
    lista_ejemplos = EjemploSerializer(source="ejemplos", many=True, read_only=True)
    fichas = serializers.SlugRelatedField(slug_field="codigo", many=True, queryset=Ficha.objects.all(), required=False)

    class Meta:
        model = Intent
        fields = [
            "id",
            "proceso",
            "proceso_clave",
            "nombre",
            "descripcion",
            "fichas",
            "secciones",
            "entidades",
            "si_falta_entidad",
            "respuesta_fija",
            "activo",
            "ejemplos",
            "lista_ejemplos",
            "actualizado",
        ]

    def validate_secciones(self, valor):
        invalidas = [s for s in valor if s not in SECCIONES]
        if invalidas:
            raise serializers.ValidationError(f"Secciones no válidas: {', '.join(invalidas)}")
        return valor

    def validate_ejemplos(self, valor):
        limpios = list(dict.fromkeys(v.strip() for v in valor if v.strip()))
        if len(limpios) < 5:
            raise serializers.ValidationError("Registre al menos 5 ejemplos distintos (se recomiendan 10).")
        return limpios

    def _guardar_ejemplos(self, intent, ejemplos):
        if ejemplos is None:
            return
        intent.ejemplos.all().delete()
        EjemploIntent.objects.bulk_create(EjemploIntent(intent=intent, texto=e) for e in ejemplos)

    def create(self, validated_data):
        ejemplos = validated_data.pop("ejemplos", None)
        intent = super().create(validated_data)
        self._guardar_ejemplos(intent, ejemplos)
        return intent

    def update(self, instance, validated_data):
        ejemplos = validated_data.pop("ejemplos", None)
        intent = super().update(instance, validated_data)
        self._guardar_ejemplos(intent, ejemplos)
        return intent


class PlantillaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plantilla
        fields = ["id", "proceso", "clave", "texto"]


class PendienteSerializer(serializers.ModelSerializer):
    proceso_clave = serializers.CharField(source="proceso.clave", read_only=True)
    fichas = serializers.SlugRelatedField(slug_field="codigo", many=True, queryset=Ficha.objects.all(), required=False)

    class Meta:
        model = Pendiente
        fields = [
            "id",
            "proceso",
            "proceso_clave",
            "codigo",
            "descripcion",
            "pregunta",
            "fichas",
            "resuelto",
            "resolucion",
            "resuelto_en",
            "creado",
        ]
        read_only_fields = ["resuelto_en", "creado"]


# --------------------------------------------------------------- documentos


def _validar_archivo(archivo, extensiones=(".pdf", ".docx")):
    if archivo.size > TAMANO_MAXIMO:
        raise serializers.ValidationError("El archivo supera los 10 MB.")
    cabecera = archivo.read(8)
    archivo.seek(0)
    if not extension_valida(archivo.name, cabecera) or not archivo.name.lower().endswith(extensiones):
        raise serializers.ValidationError("Solo se aceptan archivos .pdf o .docx válidos.")
    return archivo


class DocumentoSerializer(serializers.ModelSerializer):
    proceso_clave = serializers.CharField(source="proceso.clave", default=None, read_only=True)
    proceso_nombre = serializers.CharField(source="proceso.nombre", default=None, read_only=True)
    url = serializers.SerializerMethodField()

    class Meta:
        model = Documento
        fields = [
            "id",
            "proceso",
            "proceso_clave",
            "proceso_nombre",
            "titulo",
            "tipo",
            "numero",
            "fecha_emision",
            "descripcion",
            "archivo",
            "url_externa",
            "url",
            "publico",
            "creado",
        ]
        extra_kwargs = {"archivo": {"write_only": True, "required": False}}

    def get_url(self, obj):
        if obj.archivo:
            return f"{settings.MEDIA_URL}{obj.archivo.name}"
        return obj.url_externa or None

    def validate_archivo(self, archivo):
        return _validar_archivo(archivo) if archivo else archivo

    def validate(self, attrs):
        archivo = attrs.get("archivo") or getattr(self.instance, "archivo", None)
        url = attrs.get("url_externa") or getattr(self.instance, "url_externa", "")
        if not archivo and not url:
            raise serializers.ValidationError({"archivo": "Adjunte el archivo o indique un enlace externo."})
        return attrs


class CargaDocumentoSerializer(serializers.ModelSerializer):
    fichas_propuestas = FichaListaSerializer(many=True, read_only=True)

    class Meta:
        model = CargaDocumento
        fields = ["id", "proceso", "archivo", "nombre_original", "estado", "mensaje", "fichas_propuestas", "creada"]
        read_only_fields = ["nombre_original", "estado", "mensaje", "creada"]
        extra_kwargs = {"archivo": {"write_only": True}}

    def validate_archivo(self, archivo):
        return _validar_archivo(archivo)
