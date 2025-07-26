import datetime
import hashlib
import hmac
import io
import json

import qrcode
from django.conf import settings
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListAPIView, ListCreateAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from routes.models import Route
from trips.api.filters import TripFilter
from trips.api.serializers import TripSerializer, TripQRSerializer, QRTripValidatorSerializer
from trips.models import Trip, PassengerTrip
from users.api.permissions import IsDriver, IsPassenger
from vehicles.models import Vehicle
from trips.tasks import analyze_trip
from redis import Redis

class TripListCreateView(ListCreateAPIView):
    """
    View to list all trips and create a new trip for the current logged driver.
    """
    queryset = Trip.objects.all()
    serializer_class = TripSerializer
    filter_backends = [DjangoFilterBackend,SearchFilter,OrderingFilter]
    filterset_class = TripFilter
    search_fields = ['route__name']
    ordering_fields = ['date']
    ordering = ['date']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsDriver()]
        return [AllowAny()]

    def create(self, request, *args, **kwargs):
        """
        Creates a new trip for the current logged driver
        """
        route_id = request.data.get('route')
        vehicle_id = request.data.get('vehicle')

        # Validate the data using the serializer
        serializer = TripSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        trip_date = serializer.validated_data['date']

        # Validate that the route exists
        if not Route.objects.filter(id=route_id).exists():
            return Response({'error': 'La ruta no existe.'}, status=status.HTTP_404_NOT_FOUND)

        # Validate that the vehicle exists
        if not Vehicle.objects.filter(id=vehicle_id, user_id=request.user).exists():
            return Response({'error': 'El vehículo no existe.'}, status=status.HTTP_404_NOT_FOUND)

        now = datetime.datetime.now(datetime.timezone.utc)

        # Validate that the trip date is not in the past
        if not trip_date or trip_date < now:
            return Response({'error': 'La fecha del viaje no puede ser en el pasado.'},
                            status=status.HTTP_400_BAD_REQUEST)

        new_trip = Trip.objects.create(
            route_id=route_id,
            driver=request.user,
            vehicle_id=vehicle_id,
            date=trip_date
        )

        serializer = TripSerializer(new_trip)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TripDetailView(APIView):
    """
    View to update the status of a trip for the current logged driver.
    """
    permission_classes = [IsAuthenticated, IsDriver]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='trip_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='ID del viaje a actualizar'
            ),
        ],
        request=TripSerializer,
        responses=TripSerializer
    )
    def patch(self, request, trip_id):
        """
        Updates the status of a trip
        """
        try:
            trip = Trip.objects.get(id=trip_id, driver=request.user)
        except Trip.DoesNotExist:
            return Response({'error': 'El viaje no existe.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = TripSerializer(trip, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated, IsDriver])
def start_trip(request, trip_id):
    """
    Starts a trip by updating its status to 'IN_PROGRESS' and setting the start time.
    """
    try:
        trip = Trip.objects.get(id=trip_id, driver=request.user)
    except Trip.DoesNotExist:
        return Response({'error': 'El viaje no existe.'}, status=status.HTTP_404_NOT_FOUND)

    if trip.status != 'CREATED':
        return Response({'error': 'El viaje no puede ser iniciado.'}, status=status.HTTP_400_BAD_REQUEST)

    trip.status = 'IN_PROGRESS'
    trip.start_time = datetime.datetime.now(datetime.timezone.utc).time()
    trip.save(update_fields=['status', 'start_time'])

    # Add the trip to Redis set of active rides
    redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)
    redis.sadd('active_rides', str(trip_id))

    serializer = TripSerializer(trip)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated, IsDriver])
def finish_trip(request, trip_id):
    """
    Finished a trip by updating its status to 'COMPLETED' and setting the end time.
    """
    try:
        trip = Trip.objects.get(id=trip_id, driver=request.user)
    except Trip.DoesNotExist:
        return Response({'error': 'El viaje no existe.'}, status=status.HTTP_404_NOT_FOUND)

    if trip.status != 'IN_PROGRESS':
        return Response({'error': 'El viaje no puede ser finalizado.'}, status=status.HTTP_400_BAD_REQUEST)

    trip.status = 'COMPLETED'
    trip.end_time = datetime.datetime.now(datetime.timezone.utc).time()
    trip.save(update_fields=['status', 'end_time'])

    # Remove the trip from Redis set of active rides
    redis = Redis.from_url(settings.REDIS_URL, decode_responses= True)
    redis.srem('active_rides', str(trip_id))

    analyze_trip.delay(trip_id)  # Trigger the analysis of the trip in the background

    serializer = TripSerializer(trip)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsDriver])
def generate_qr_trip_validator(request, trip_id):
    """
    Generates a QR code for a trip that can be used by passengers to validate their trip. It ensures:
    - The trip exists and belongs to the driver.
    - The QR code contains the trip ID, vehicle ID, and a signature for integrity.
    """

    # Validate the trip exists and belongs to the driver
    trip = Trip.objects.filter(id=trip_id, driver=request.user).first()
    if not trip:
        return Response({'error': 'El viaje no existe o no pertenece al conductor.'}, status=status.HTTP_404_NOT_FOUND)

    payload = {
        "trip_id": trip_id,
        "vehicle_id": trip.vehicle.id,
    }

    # Generate the HMAC signature to ensure the integrity of the QR code
    signature = hmac.new(settings.SECRET_KEY.encode(), json.dumps(payload).encode(), hashlib.sha256).hexdigest()
    qr_payload = {**payload, "signature": signature}

    img = qrcode.make(json.dumps(qr_payload))
    buf = io.BytesIO()
    img.save(buf, format='PNG')

    return HttpResponse(buf.getvalue(), content_type='image/png', status=status.HTTP_200_OK)


@extend_schema(request=QRTripValidatorSerializer)
@api_view(['POST'])
@permission_classes([IsPassenger])
def validate_qr_trip(request, trip_id):
    """
    Validates a trip using a QR code by checking the trip ID, vehicle ID, and signature.
    :param request:
    :return: Response with validation status.
    """
    payload = request.data
    signature = payload.get("signature")

    # Build the data to verify the signature
    data = {
        'trip_id': payload.get("trip_id"),
        'vehicle_id': payload.get("vehicle_id")
    }

    # Generate the expected signature using the same method as when generating the QR code
    expected_signature = hmac.new(
        settings.SECRET_KEY.encode(),
        json.dumps(data, sort_keys=True).encode(),
        hashlib.sha256
    ).hexdigest()

    # Check if the provided signature matches the expected signature
    if signature != expected_signature:
        return Response({'error': 'QR inválido'}, status=status.HTTP_400_BAD_REQUEST)

    # If the signature is valid, proceed to validate the trip
    payload_trip_id = data.get('trip_id')
    if payload_trip_id != trip_id:
        return Response({'error': 'El ID del viaje no coincide con el del QR.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        trip = Trip.objects.get(id=trip_id)
    except Trip.DoesNotExist:
        return Response({'error': 'El viaje no existe.'}, status=status.HTTP_404_NOT_FOUND)

    # Verify the vehicle ID matches the trip's vehicle
    payload_vehicle_id = data.get('vehicle_id')
    if payload_vehicle_id != trip.vehicle.id:
        return Response({'error': 'El ID del vehículo no coincide con el del viaje.'}, status=status.HTTP_400_BAD_REQUEST)

    # Verify the passenger is associated with the trip
    try:
        pt = PassengerTrip.objects.get(trip=trip, passenger=request.user)
    except PassengerTrip.DoesNotExist:
        return Response({'error': 'El pasajero no está asociado a este viaje.'}, status=status.HTTP_404_NOT_FOUND)

    # Validate the trip
    pt.validated = True
    pt.validation_time = datetime.datetime.now(datetime.timezone.utc)
    pt.save(update_fields=['validated', 'validation_time'])

    return Response({'message': 'Viaje validado correctamente.'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsPassenger])
def join_trip(request, trip_id):
    """
    Allows a passenger to join a trip by creating a PassengerTrip entry.
    It ensures:
    - The trip exists and the status is 'CREATED'.
    - The passenger is not already associated with the trip.
    - The trip is not full according to the vehicle's capacity.
    :param request:
    :param trip_id:
    :return:
    """
    try:
        trip = Trip.objects.get(id=trip_id)
    except Trip.DoesNotExist:
        return Response({'error': 'El viaje no existe.'}, status=status.HTTP_404_NOT_FOUND)

    if trip.status != 'CREATED':
        return Response({'error': 'El viaje no está disponible para unirse.'}, status=status.HTTP_400_BAD_REQUEST)

    current_passengers = PassengerTrip.objects.filter(trip=trip).count() + 1  # +1 for the driver
    capacity = trip.vehicle.capacity
    if current_passengers >= capacity:
        return Response({'error': 'El viaje está lleno.'}, status=status.HTTP_400_BAD_REQUEST)

    if PassengerTrip.objects.filter(trip=trip, passenger=request.user).exists():
        return Response({'error': 'Ya estás asociado a este viaje.'}, status=status.HTTP_400_BAD_REQUEST)

    PassengerTrip.objects.create(
        trip=trip,
        passenger=request.user
    )

    return Response({'message': 'Te has unido al viaje correctamente.'}, status=status.HTTP_201_CREATED)