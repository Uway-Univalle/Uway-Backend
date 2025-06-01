from rest_framework import serializers
from vehicles.models import Vehicle

class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = [
            'vehicle_id',
            'vehicle_type',
            'vehicle_category',
            'vehicle_location',
            'state',
            'brand',
            'tecnicomecanica_date',
            'soat_date',
            'is_verified',
            'plate'
        ]