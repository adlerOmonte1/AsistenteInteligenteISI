from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import ConsultaViewSet, MetricasResumenView

router = DefaultRouter()
router.register("conversaciones", ConsultaViewSet, basename="conversacion")

urlpatterns = [
    path("metricas/resumen/", MetricasResumenView.as_view(), name="metricas-resumen"),
    *router.urls,
]
