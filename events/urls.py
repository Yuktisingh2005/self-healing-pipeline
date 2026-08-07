from rest_framework.routers import DefaultRouter
from .views import DeploymentEventViewSet

router = DefaultRouter()
router.register("events", DeploymentEventViewSet, basename="event")

urlpatterns = router.urls