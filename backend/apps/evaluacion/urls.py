from rest_framework.routers import DefaultRouter

from .views import CasoViewSet, EvaluacionViewSet

router = DefaultRouter()
router.register("evaluaciones", EvaluacionViewSet, basename="evaluacion")
router.register("casos-evaluacion", CasoViewSet, basename="caso-evaluacion")

urlpatterns = router.urls
