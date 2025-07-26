from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, status
from vehicles.models import Vehicle, VehicleType, VehicleCategory
from vehicles.api.serializers import VehicleSerializer, VehicleTypeSerializer, DenyVehicleVerificationSerializer
from rest_framework.generics import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from users.api.permissions import IsCollegeAdminOfOwnCollege, IsDriver
import threading
from emails.helpers import send_verification_notification_to_vehicle_user, send_denied_notification_to_vehicle_user

class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = [IsDriver]

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data['user_id'] = request.user.id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(["GET"])
@permission_classes([IsCollegeAdminOfOwnCollege])
def unverified_vehicles_by_college(request):
    vehicles = Vehicle.objects.filter(
        is_verified=False,
        user_id__college=request.user.college
    )
    serializer = VehicleSerializer(vehicles, many=True)
    return Response(serializer.data)

@api_view(['PATCH'])
@permission_classes([IsCollegeAdminOfOwnCollege])
def verify_college_vehicle(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)

    if request.user.college != vehicle.user_id.college:
        return Response(
            {'data': 'No tiene permisos para acceder a este recurso.'},
            status=status.HTTP_403_FORBIDDEN
        )

    vehicle.is_verified = True
    vehicle.vehicle_validator = request.user
    vehicle.save()

    thread = threading.Thread(
        target=send_verification_notification_to_vehicle_user,
        args=(f"{vehicle.user_id.first_name} {vehicle.user_id.last_name}", vehicle.user_id.email, vehicle.plate)
    )
    thread.start()

    return Response(status=status.HTTP_200_OK)

@api_view(["GET"])
@permission_classes([IsDriver])
def get_vehicle_types(request):
    vehicle_types = VehicleType.objects.all()
    serializer = VehicleTypeSerializer(vehicle_types, many=True)
    return Response(serializer.data)

@api_view(["GET"])
@permission_classes([IsDriver])
def get_vehicle_categories(request):
    categories = VehicleCategory.objects.all()
    serializer = VehicleTypeSerializer(categories, many=True)
    return Response(serializer.data)

@extend_schema(request=DenyVehicleVerificationSerializer)
@api_view(["PATCH"])
@permission_classes([IsCollegeAdminOfOwnCollege])
def deny_vehicle_verification(request, vehicle_id):
    serializer = DenyVehicleVerificationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    reason_denied = serializer.validated_data['reason_denied']

    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    vehicle.denied = True
    vehicle.reason_denied = reason_denied
    vehicle.save()

    thread = threading.Thread(
        target=send_denied_notification_to_vehicle_user,
        args=(f"{vehicle.user_id.first_name} {vehicle.user_id.last_name}", vehicle.plate, vehicle.user_id.email, reason_denied)
    )
    thread.start()

    return Response(status=status.HTTP_200_OK)