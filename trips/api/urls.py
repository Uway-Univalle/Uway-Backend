from django.urls import path

from trips.api.views import TripDetailView, start_trip, finish_trip, generate_qr_trip_validator, \
    validate_qr_trip, join_trip, TripListCreateView

urlpatterns = [
    path('trips/', TripListCreateView.as_view(), name='trip-list'),
    path('trips/<int:trip_id>/', TripDetailView.as_view(), name='trip-detail'),
    path('trips/<int:trip_id>/start/', start_trip, name='start-trip'),
    path('trips/<int:trip_id>/finish/', finish_trip, name='finish-trip'),
    path('trips/<int:trip_id>/qr/', generate_qr_trip_validator, name='generate-qr-trip-validator'),
    path('trips/<int:trip_id>/validate-qr/', validate_qr_trip, name='validate-qr-trip'),
    path('trips/<int:trip_id>/join/', join_trip, name='join-trip'),
]