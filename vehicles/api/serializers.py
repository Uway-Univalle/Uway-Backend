from rest_framework import serializers
from vehicles.models import Vehicle, VehicleType

class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = '__all__'

class VehicleTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleType
        fields = ['id','name', 'description']