from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

api_v1 = [
    path("", include("apps.sistema.urls")),
    path("auth/", include("apps.cuentas.urls_auth")),
    path("", include("apps.cuentas.urls")),
    path("", include("apps.conocimiento.urls")),
    path("", include("apps.dialogo.urls")),
    path("", include("apps.evaluacion.urls")),
    path("", include("apps.analitica.urls")),
    path("esquema/", SpectacularAPIView.as_view(), name="esquema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="esquema"), name="docs"),
]

urlpatterns = [path("api/v1/", include(api_v1))]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
