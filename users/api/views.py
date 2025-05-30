import uuid

from django.db import transaction
from django.http import JsonResponse
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view,permission_classes
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from colleges.models import College
from core.aws.helpers import upload_file_to_s3
from users.api.serializers import UserSerializer, UserDocumentSerializer
from users.models import User, UserDocument
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
        college_id = request.data.get('college')
        if college_id is None:
            return Response(
                {'data': 'El usuario debe estar asociado a una institución.'},
                status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()

            for file in files:
                file_path = f"private/{college_id}-{user.college.name}/{user.id}/{str(uuid.uuid4())}_{file.name}"
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