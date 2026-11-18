from django.urls import path

from .views import ConfiguracionPublicaView, ConfiguracionView, SaludView

urlpatterns = [
    path("health/", SaludView.as_view(), name="salud"),
    path("configuracion/", ConfiguracionView.as_view(), name="configuracion"),
    path("configuracion/publica/", ConfiguracionPublicaView.as_view(), name="configuracion-publica"),
]
