from django.urls import path, include
from rest_framework.routers import DefaultRouter


from routes.api.views import create_full_route_from_coordinates, DriverRoutesView, get_passenger_routes
from routes.api.views import create_full_route_from_coordinates, DriverRoutesView, delete_route_by_driver

routes_router = DefaultRouter()

urlpatterns = [
    path('routes/', DriverRoutesView.as_view()),
    path('routes/full-route/', create_full_route_from_coordinates),
    path( 'routes/<route_id>/', get_passenger_routes),
    path('routes/<int:route_id>/delete-route', delete_route_by_driver, name='delete_route_by_driver'),
]