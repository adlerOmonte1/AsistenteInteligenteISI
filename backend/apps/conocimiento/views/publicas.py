"""Endpoints públicos del portal (sin login): procesos, fichas publicadas y documentos."""

from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Documento, Ficha, Proceso
from ..serializers import DocumentoSerializer, ProcesoSerializer


class _Publica:
    permission_classes = [AllowAny]
    authentication_classes = []


def _procesos_visibles():
    return (
        Proceso.objects.filter(activo=True, visible_en_portal=True)
        .select_related("programa")
        .annotate(
            fichas_publicadas=Count(
                "fichas",
                filter=Q(fichas__version_publicada__isnull=False, fichas__reemplazada_por__isnull=True),
            )
        )
        .order_by("orden", "nombre")  # Meta.ordering no se aplica a consultas con GROUP BY
    )


class ProcesosPublicosView(_Publica, generics.ListAPIView):
    serializer_class = ProcesoSerializer
    pagination_class = None

    def get_queryset(self):
        return _procesos_visibles()


def _fichas_publicadas(proceso):
    fichas = (
        Ficha.objects.filter(proceso=proceso, version_publicada__isnull=False, reemplazada_por__isnull=True)
        .select_related("version_publicada")
        .order_by("fase", "codigo")
    )
    return [
        {
            "codigo": f.codigo,
            "version": f.version_publicada.numero,
            "publicada_en": f.version_publicada.publicada_en,
            "contenido": f.version_publicada.contenido,
        }
        for f in fichas
    ]


class ProcesoPublicoView(_Publica, APIView):
    """Un trámite completo: sus fases publicadas y sus documentos."""

    @extend_schema(responses=dict)
    def get(self, request, clave: str):
        proceso = get_object_or_404(_procesos_visibles(), clave=clave)
        documentos = Documento.objects.filter(publico=True, proceso=proceso)
        return Response(
            {
                "proceso": ProcesoSerializer(proceso).data,
                "fichas": _fichas_publicadas(proceso),
                "documentos": DocumentoSerializer(documentos, many=True).data,
            }
        )


class FichaPublicaView(_Publica, APIView):
    @extend_schema(responses=dict)
    def get(self, request, clave: str, codigo: str):
        ficha = get_object_or_404(
            Ficha.objects.select_related("version_publicada"),
            proceso__clave=clave,
            proceso__visible_en_portal=True,
            codigo=codigo,
            version_publicada__isnull=False,
        )
        v = ficha.version_publicada
        return Response(
            {"codigo": ficha.codigo, "version": v.numero, "publicada_en": v.publicada_en, "contenido": v.contenido}
        )


class DocumentosPublicosView(_Publica, generics.ListAPIView):
    """Biblioteca normativa: resoluciones, reglamentos, formatos y guías."""

    serializer_class = DocumentoSerializer

    def get_queryset(self):
        qs = Documento.objects.filter(publico=True).select_related("proceso")
        p = self.request.query_params
        if p.get("proceso"):
            qs = qs.filter(proceso__clave=p["proceso"])
        if p.get("tipo"):
            qs = qs.filter(tipo=p["tipo"])
        if p.get("q"):
            qs = qs.filter(Q(titulo__icontains=p["q"]) | Q(numero__icontains=p["q"]) | Q(descripcion__icontains=p["q"]))
        return qs


class BuscarPublicoView(_Publica, APIView):
    """Búsqueda por palabras en las fichas publicadas, para el buscador del portal."""

    @extend_schema(responses=dict)
    def get(self, request):
        from apps.recuperacion.services import buscar

        termino = (request.query_params.get("q") or "").strip()[:200]
        if len(termino) < 3:
            return Response({"resultados": []})
        resultados = buscar(termino, vector=None, k=10)
        vistos, salida = set(), []
        for r in resultados:
            ficha = r.seccion.ficha
            if ficha.codigo in vistos or not ficha.proceso.visible_en_portal:
                continue
            vistos.add(ficha.codigo)
            salida.append(
                {
                    "codigo": ficha.codigo,
                    "titulo": r.seccion.version.contenido["titulo"],
                    "proceso": ficha.proceso.clave,
                    "proceso_nombre": ficha.proceso.nombre,
                    "fragmento": r.seccion.texto[:240],
                }
            )
        return Response({"resultados": salida})
