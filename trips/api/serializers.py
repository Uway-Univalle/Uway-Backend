from rest_framework import serializers

from trips.models import Trip, Rate


class TripSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = '__all__'

class TripQRSerializer(serializers.Serializer):
    trip_id = serializers.IntegerField()
    vehicle_id = serializers.IntegerField()

class QRTripValidatorSerializer(serializers.Serializer):
    trip_id = serializers.IntegerField()
    vehicle_id = serializers.IntegerField()
    signature =  serializers.CharField(max_length=64)

class TripRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rate
        fields = ['trip', 'passenger','ratting', 'comment']