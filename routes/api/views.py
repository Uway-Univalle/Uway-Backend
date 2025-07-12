from django.contrib.gis.geos import LineString
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
import requests
from rest_framework.views import APIView

from routes.api.serializers import CoordinateSerializer, SaveRouteSerializer, RouteSerializer
from routes.models import Route
from users.api.permissions import IsDriver


@extend_schema(request=CoordinateSerializer)
@api_view(['POST'])
def create_full_route_from_coordinates(request):
    """
    Calculates the optimal path between two or more points using OSRM (Open Source Routing Machine).
    It receives a list of coordinates in [[lat, lon], [lat, lon], ...] format, queries OSRM to obtain
    the path in GeoJSON format.

    :param request:
    :return: Returns the geometry, total distance and estimated duration of the route.
    """
    serializer = CoordinateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    coordinates = serializer.validated_data.get("coordinates")

    if not coordinates or len(coordinates) < 2:
        return Response({"error": "Se necesitan al menos dos puntos."}, status=status.HTTP_400_BAD_REQUEST)

    formatted_coordinates = ';'.join(f"{lon},{lat}" for lat, lon, in coordinates)
    osrm_url = f"http://router.project-osrm.org/route/v1/driving/{formatted_coordinates}?overview=full&geometries=geojson"

    response = requests.get(osrm_url)
    data = response.json()

    if data.get("code") != "Ok":
        return Response({"error": "Error en OSRM"})

    geometry = data["routes"][0]["geometry"]["coordinates"]

    return Response({
        "geometry": geometry,
        "distance": data["routes"][0]["distance"],
        "duration": data["routes"][0]["duration"]
    })


class DriverRoutesView(APIView):
    permission_classes = [IsDriver]

    @extend_schema(responses=RouteSerializer)
    def get(self, request):
        """
        Filters all routes from the current logged driver
        :param request:
        :return: All the saved routes from the driver
        """
        routes = Route.objects.filter(user=request.user)
        return Response(RouteSerializer(routes, many=True).data, status=status.HTTP_200_OK)

    @extend_schema(request=SaveRouteSerializer, responses=RouteSerializer)
    def post(self, request):
        """
        Saves the route trajectory using a LineString. It makes an HTTP request to OSRM API to
        obtain the route geometry.
        :param request:
        :return:
        """
        serializer = SaveRouteSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        coordinates = serializer.validated_data.get('coordinates')
        name = serializer.validated_data.get('name', '')

        formatted_coordinates = ';'.join(f"{lon},{lat}" for lat, lon, in coordinates)
        osrm_url = f"http://router.project-osrm.org/route/v1/driving/{formatted_coordinates}?overview=full&geometries=geojson"

        response = requests.get(osrm_url)
        data = response.json()

        if data.get("code") != "Ok":
            return Response({"error": "Error en OSRM"})

        geometry = LineString(data["routes"][0]["geometry"]["coordinates"])

        route = Route.objects.create(
            user=request.user,
            name=name,
            trajectory=geometry
        )

        return Response(RouteSerializer(route).data, status=status.HTTP_201_CREATED)