from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import panel, publicas

router = DefaultRouter()
router.register("facultades", panel.FacultadViewSet, basename="facultad")
router.register("programas", panel.ProgramaViewSet, basename="programa")
router.register("admin/procesos", panel.ProcesoViewSet, basename="proceso")
router.register("fichas", panel.FichaViewSet, basename="ficha")
router.register("intents", panel.IntentViewSet, basename="intent")
router.register("pendientes", panel.PendienteViewSet, basename="pendiente")
router.register("plantillas", panel.PlantillaViewSet, basename="plantilla")
router.register("admin/documentos", panel.DocumentoViewSet, basename="documento")
router.register("cargas", panel.CargaDocumentoViewSet, basename="carga")

urlpatterns = [
    path("procesos/", publicas.ProcesosPublicosView.as_view(), name="procesos-publicos"),
    path("procesos/<slug:clave>/", publicas.ProcesoPublicoView.as_view(), name="proceso-publico"),
    path("procesos/<slug:clave>/fichas/<str:codigo>/", publicas.FichaPublicaView.as_view(), name="ficha-publica"),
    path("documentos/", publicas.DocumentosPublicosView.as_view(), name="documentos-publicos"),
    path("buscar/", publicas.BuscarPublicoView.as_view(), name="buscar"),
    *router.urls,
]
