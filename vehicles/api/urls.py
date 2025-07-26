from rest_framework.routers import DefaultRouter
from vehicles.api.views import VehicleViewSet, unverified_vehicles_by_college, verify_college_vehicle, \
    get_vehicle_types, get_vehicle_categories, get_vehicle_categories, deny_vehicle_verification
from django.urls import include, path

router = DefaultRouter()
router.register(r"vehicles", VehicleViewSet, basename="vehicle")

urlpatterns = [
    path('vehicles/unverified/', unverified_vehicles_by_college, name='unverified_vehicles_by_college'),
    path('vehicles/<int:vehicle_id>/verify/', verify_college_vehicle, name='verify-college-vehicle'),
    path('vehicles/get_types/', get_vehicle_types, name='get_vehicle_types'),
    path('vehicles/get_categories/', get_vehicle_categories, name='get_vehicle_categories'),
    path('vehicles/<int:vehicle_id>/deny-vehicles/', deny_vehicle_verification, name='deny_vehicle_verification'),
]
urlpatterns += router.urls