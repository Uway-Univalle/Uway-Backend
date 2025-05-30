from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view,permission_classes
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from colleges.models import College
from users.api.serializers import UserSerializer
from users.models import User
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

@api_view(["GET"])
@permission_classes([IsCollegeAdminOfOwnCollege])
def unverified_users_by_college(request):
    print("ENTRÓ AL ENDPOINT")
    college_id = request.user.college
    users = User.objects.filter(college=college_id, is_verified=False)
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def getRoutes(request):
    routes = [
        'api/token',
        'api/token/refresh',
    ]

    return Response(routes)