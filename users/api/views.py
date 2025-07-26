import threading
import uuid

from django.db import transaction
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view,permission_classes
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from core.aws.helpers import upload_file_to_s3, delete_file_from_s3
from emails.helpers import send_verification_notification_to_user, send_denied_notification_to_user
from users.api.serializers import UserSerializer, UserDocumentSerializer, UserTypeSerializer
from users.models import User, UserDocument, UserType, PassengerType
from users.api.permissions import IsSystemAdmin, IsCollegeAdminOfOwnCollege

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['username'] = user.username

        return token

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        user = User.objects.get(username=request.data['username'])
        user_data = UserSerializer(user).data
        response.data['user'] = user_data
        return response

class UserApiViewSet(ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = []

    def create(self, request, *args, **kwargs):
        files = request.FILES.getlist('attachments')

        data = request.data.copy()
        data.pop('attachments', None)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        validated = serializer.validated_data

        college = validated.get('college')
        user_type = validated.get('user_type')

        if college is None and user_type.name != 'SystemAdmin':
            return Response(
                {'data': 'El usuario debe estar asociado a una institución.'},
                status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            user = User.objects.create_user(**validated)

            for file in files:
                file_path = f"private/{college.college_id}-{user.college.name}/{user.id}/{str(uuid.uuid4())}_{file.name}"
                file_url = upload_file_to_s3(file, file_path)
                UserDocument.objects.create(user=user, url=file_url)

        response = self.get_serializer(user).data
        return Response(response, status=status.HTTP_201_CREATED)


@api_view(["GET"])
@permission_classes([IsCollegeAdminOfOwnCollege])
def unverified_users_by_college(request):
    college_id = request.user.college
    users = User.objects.filter(college=college_id, is_verified=False)
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)


@api_view(['PATCH'])
@permission_classes([IsCollegeAdminOfOwnCollege])
def verify_college_user(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.user.college != user.college:
        return Response(
            {'data': 'No tiene permisos para acceder a este recurso.'},
            status=status.HTTP_403_FORBIDDEN
        )

    user.is_verified = True
    user.passanger_validator = request.user
    user.save()

    thread = threading.Thread(
        target=send_verification_notification_to_user,
        args=(f"{user.first_name} {user.last_name}", user.email)
    )
    thread.start()

    return Response(status=status.HTTP_200_OK)


@api_view(["GET"])
def get_user_documents(request, user_id):
    try:
        user = get_object_or_404(User, id=user_id)
    except User.DoesNotExist:
        return Response({'data':'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)

    documents = UserDocument.objects.filter(user=user)
    serializer = UserDocumentSerializer(documents, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def getRoutes(request):
    routes = [
        'api/token',
        'api/token/refresh',
    ]

    return Response(routes)

@api_view(["GET"])
def get_user_types(request):
    user_types = UserType.objects.all()
    serializer = UserTypeSerializer(user_types, many=True)
    return Response(serializer.data)

@api_view(["GET"])
def get_passenger_types(request):
    passenger_types = PassengerType.objects.all()
    serializer = UserTypeSerializer(passenger_types, many=True)
    return Response(serializer.data)

@api_view(["PATCH"])
@permission_classes([IsCollegeAdminOfOwnCollege])
def deny_driver_verification(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user_documents = UserDocument.objects.filter(user=user)
    reason_denied = request.data.get('reason_denied', '')

    # Eliminar documentos del usuario de S3 y de la base de datos
    for doc in user_documents:
        delete_file_from_s3(doc.url.split('https://uway.s3.amazonaws.com/')[1])
        doc.delete()

    user.denied = True
    user.reason_denied = reason_denied
    user.save()

    # Enviar correo de notificación
    thread = threading.Thread(
        target=send_denied_notification_to_user,
        args=(f"{user.first_name} {user.last_name}", user.email, reason_denied)
    )
    thread.start()

    return Response(status=status.HTTP_200_OK)
