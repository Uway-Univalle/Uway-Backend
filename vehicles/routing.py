from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/vehicle-tracking/(?P<ride_id>\w+)/$', consumers.VehicleLocationConsumer.as_asgi()),
]