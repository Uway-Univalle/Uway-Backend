from rest_framework.routers import DefaultRouter
from vehicles.api.views import VehicleViewSet, unverified_vehicles_by_college, verify_college_vehicle
from django.urls import include, path

router = DefaultRouter()
router.register(r"vehicles", VehicleViewSet, basename="vehicle")

urlpatterns = [
    path('vehicles/unverified/', unverified_vehicles_by_college, name='unverified_vehicles_by_college'),
    path('vehicles/<int:vehicle_id>/verify/', verify_college_vehicle, name='verify-college-vehicle'),
]
urlpatterns += router.urls