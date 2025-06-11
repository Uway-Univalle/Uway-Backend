from rest_framework import viewsets, status
from vehicles.models import Vehicle
from vehicles.api.serializers import VehicleSerializer
from rest_framework.generics import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from users.api.permissions import IsCollegeAdminOfOwnCollege
import threading
from emails.helpers import send_verification_notification_to_vehicle_user

class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer

@api_view(["GET"])
@permission_classes([IsCollegeAdminOfOwnCollege])
def unverified_vehicles_by_college(request):
    vehicles = Vehicle.objects.filter(
        is_verified=False,
        college=request.user.college
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
    vehicle.save()

    thread = threading.Thread(
        target=send_verification_notification_to_vehicle_user,
        args=(f"{vehicle.user_id.first_name} {vehicle.user_id.last_name}", vehicle.user_id.email, vehicle.plate)
    )
    thread.start()

    return Response(status=status.HTTP_200_OK)