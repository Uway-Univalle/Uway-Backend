from rest_framework.routers import DefaultRouter
from vehicles.api.views import VehicleViewSet

router = DefaultRouter()
router.register(r"vehicles", VehicleViewSet, basename="vehicle")

urlpatterns = router.urls