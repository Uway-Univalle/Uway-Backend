from rest_framework import serializers

from routes.models import Route

class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = '__all__'

class CoordinateSerializer(serializers.Serializer):
    coordinates = serializers.ListField(
        child=serializers.ListField(
            child=serializers.FloatField(),
            min_length=2,
            max_length=2
        ),
        min_length=2
    )

class SaveRouteSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=50)
    coordinates = serializers.ListField(
        child=serializers.ListField(
            child=serializers.FloatField(),
            min_length=2,
            max_length=2
        ),
        min_length=2
    )