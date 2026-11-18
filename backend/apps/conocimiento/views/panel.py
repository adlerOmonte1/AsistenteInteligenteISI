"""Endpoints del panel de administración (JWT)."""

from django.db.models import Count, Q
from django.utils import timezone
from django_q.tasks import async_task
from drf_spectacular.utils import extend_schema
from rest_framework import mixins, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import SAFE_METHODS
from rest_framework.response import Response

from comun.permisos import (
    EsEditor,
    EsLector,
    EsRevisor,
    EsSuperadmin,
    LecturaLectorEscrituraEditor,
    MismaFacultad,
)

from ..models import CargaDocumento, Documento, Facultad, Ficha, Intent, Pendiente, Plantilla, Proceso, Programa
from ..serializers import (
    CargaDocumentoSerializer,
    DocumentoSerializer,
    FacultadSerializer,
    FichaListaSerializer,
    FichaSerializer,
    IntentSerializer,
    PendienteSerializer,
    PlantillaSerializer,
    ProcesoSerializer,
    ProgramaSerializer,
    VersionFichaSerializer,
)
from ..services import publicacion


def _filtrar_por_facultad(qs, usuario, campo="proceso__programa__facultad"):
    if usuario.facultad_id and usuario.rol != "superadmin":
        return qs.filter(**{campo: usuario.facultad_id})
    return qs


class _LecturaSuperadminEscritura:
    def get_permissions(self):
        return [EsLector()] if self.request.method in SAFE_METHODS else [EsSuperadmin()]


class FacultadViewSet(_LecturaSuperadminEscritura, viewsets.ModelViewSet):
    queryset = Facultad.objects.all()
    serializer_class = FacultadSerializer
    pagination_class = None
    http_method_names = ["get", "post", "patch", "head", "options"]


class ProgramaViewSet(_LecturaSuperadminEscritura, viewsets.ModelViewSet):
    queryset = Programa.objects.select_related("facultad")
    serializer_class = ProgramaSerializer
    pagination_class = None
    http_method_names = ["get", "post", "patch", "head", "options"]


class ProcesoViewSet(_LecturaSuperadminEscritura, viewsets.ModelViewSet):
    serializer_class = ProcesoSerializer
    pagination_class = None
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_queryset(self):
        qs = Proceso.objects.select_related("programa").annotate(
            total_fichas=Count("fichas", distinct=True),
            fichas_publicadas=Count("fichas", filter=Q(fichas__version_publicada__isnull=False), distinct=True),
        )
        return _filtrar_por_facultad(qs.order_by("orden", "nombre"), self.request.user, "programa__facultad")


class ObservacionesSerializer(serializers.Serializer):
    observaciones = serializers.CharField(required=False, allow_blank=True, max_length=2000)


class RevertirSerializer(serializers.Serializer):
    numero = serializers.IntegerField(min_value=1)


class FichaViewSet(viewsets.ModelViewSet):
    """Fichas en borrador y su ciclo de revisión.

    Guardar deja la ficha en borrador; nada cambia en el asistente hasta que un
    revisor la aprueba.
    """

    permission_classes = [LecturaLectorEscrituraEditor, MismaFacultad]
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_queryset(self):
        qs = Ficha.objects.select_related("proceso", "version_publicada", "actualizada_por")
        qs = _filtrar_por_facultad(qs, self.request.user)
        p = self.request.query_params
        if p.get("proceso"):
            qs = qs.filter(proceso__clave=p["proceso"])
        if p.get("estado"):
            qs = qs.filter(estado_dato=p["estado"])
        if p.get("publicacion"):
            qs = qs.filter(estado_revision=p["publicacion"])
        if p.get("q"):
            qs = qs.filter(Q(codigo__icontains=p["q"]) | Q(titulo__icontains=p["q"]))
        return qs

    def get_serializer_class(self):
        return FichaListaSerializer if self.action == "list" else FichaSerializer

    def perform_create(self, serializer):
        serializer.save(actualizada_por=self.request.user, estado_revision=Ficha.EstadoRevision.BORRADOR)

    def perform_update(self, serializer):
        publicacion.marcar_editada(serializer.instance, self.request.user)
        serializer.save(actualizada_por=self.request.user, estado_revision=Ficha.EstadoRevision.BORRADOR)

    @extend_schema(request=None, responses=FichaSerializer)
    @action(detail=True, methods=["post"], url_path="enviar-revision", permission_classes=[EsEditor, MismaFacultad])
    def enviar_revision(self, request, pk=None):
        ficha = publicacion.enviar_a_revision(self.get_object(), request.user)
        return Response(FichaSerializer(ficha).data)

    @extend_schema(request=ObservacionesSerializer, responses=FichaSerializer)
    @action(detail=True, methods=["post"], permission_classes=[EsRevisor, MismaFacultad])
    def aprobar(self, request, pk=None):
        datos = ObservacionesSerializer(data=request.data)
        datos.is_valid(raise_exception=True)
        ficha = self.get_object()
        publicacion.aprobar(ficha, request.user, datos.validated_data.get("observaciones", ""))
        ficha.refresh_from_db()
        return Response(FichaSerializer(ficha).data)

    @extend_schema(request=ObservacionesSerializer, responses=FichaSerializer)
    @action(detail=True, methods=["post"], permission_classes=[EsRevisor, MismaFacultad])
    def rechazar(self, request, pk=None):
        datos = ObservacionesSerializer(data=request.data)
        datos.is_valid(raise_exception=True)
        ficha = publicacion.rechazar(self.get_object(), request.user, datos.validated_data.get("observaciones", ""))
        return Response(FichaSerializer(ficha).data)

    @extend_schema(request=RevertirSerializer, responses=FichaSerializer)
    @action(detail=True, methods=["post"], permission_classes=[EsRevisor, MismaFacultad])
    def revertir(self, request, pk=None):
        datos = RevertirSerializer(data=request.data)
        datos.is_valid(raise_exception=True)
        ficha = self.get_object()
        publicacion.revertir(ficha, datos.validated_data["numero"], request.user)
        ficha.refresh_from_db()
        return Response(FichaSerializer(ficha).data)

    @extend_schema(responses=VersionFichaSerializer(many=True))
    @action(detail=True, methods=["get"])
    def historial(self, request, pk=None):
        versiones = self.get_object().versiones.select_related("publicada_por")
        return Response(VersionFichaSerializer(versiones, many=True).data)


class IntentViewSet(viewsets.ModelViewSet):
    serializer_class = IntentSerializer
    permission_classes = [LecturaLectorEscrituraEditor]
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_queryset(self):
        qs = Intent.objects.select_related("proceso").prefetch_related("fichas", "ejemplos")
        qs = _filtrar_por_facultad(qs, self.request.user)
        if self.request.query_params.get("proceso"):
            qs = qs.filter(proceso__clave=self.request.query_params["proceso"])
        if self.request.query_params.get("q"):
            qs = qs.filter(nombre__icontains=self.request.query_params["q"])
        return qs

    def perform_create(self, serializer):
        intent = serializer.save()
        async_task("apps.conocimiento.tasks.embeber_intent", intent.id)

    def perform_update(self, serializer):
        intent = serializer.save()
        async_task("apps.conocimiento.tasks.embeber_intent", intent.id)


class PendienteViewSet(viewsets.ModelViewSet):
    serializer_class = PendienteSerializer
    permission_classes = [LecturaLectorEscrituraEditor]
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_queryset(self):
        qs = Pendiente.objects.select_related("proceso").prefetch_related("fichas")
        qs = _filtrar_por_facultad(qs, self.request.user)
        p = self.request.query_params
        if p.get("proceso"):
            qs = qs.filter(proceso__clave=p["proceso"])
        if p.get("resuelto") in ("true", "false"):
            qs = qs.filter(resuelto=p["resuelto"] == "true")
        return qs

    def perform_update(self, serializer):
        resuelto = serializer.validated_data.get("resuelto")
        extra = {}
        if resuelto and not serializer.instance.resuelto:
            extra["resuelto_en"] = timezone.now()
        elif resuelto is False:
            extra["resuelto_en"] = None
        serializer.save(**extra)


class PlantillaViewSet(viewsets.ModelViewSet):
    serializer_class = PlantillaSerializer
    permission_classes = [LecturaLectorEscrituraEditor]
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_queryset(self):
        qs = Plantilla.objects.select_related("proceso")
        if self.request.query_params.get("proceso"):
            qs = qs.filter(proceso__clave=self.request.query_params["proceso"])
        return qs


class DocumentoViewSet(viewsets.ModelViewSet):
    """Biblioteca normativa del portal."""

    serializer_class = DocumentoSerializer
    permission_classes = [LecturaLectorEscrituraEditor]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        qs = Documento.objects.select_related("proceso")
        if self.request.query_params.get("proceso"):
            qs = qs.filter(proceso__clave=self.request.query_params["proceso"])
        return qs

    def perform_create(self, serializer):
        serializer.save(creado_por=self.request.user)


class CargaDocumentoViewSet(
    mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    """Sube un .docx o .pdf y propone fichas en borrador (proceso en segundo plano)."""

    serializer_class = CargaDocumentoSerializer
    permission_classes = [EsEditor]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        return CargaDocumento.objects.select_related("proceso").prefetch_related("fichas_propuestas__proceso")

    def create(self, request, *args, **kwargs):
        datos = self.get_serializer(data=request.data)
        datos.is_valid(raise_exception=True)
        carga = datos.save(creada_por=request.user, nombre_original=datos.validated_data["archivo"].name[:255])
        async_task("apps.conocimiento.tasks.procesar_carga", carga.id)
        carga.refresh_from_db()
        return Response(self.get_serializer(carga).data, status=status.HTTP_202_ACCEPTED)
