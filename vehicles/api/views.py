from rest_framework import viewsets
from vehicles.models import Vehicle
from vehicles.api.serializers import VehicleSerializer

class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer