import uuid

from django.db import transaction
from django.utils.crypto import get_random_string
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework import status

from colleges.api.serializers import CollegeSerializer
from colleges.models import College, Color, CollegeColor

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from colleges.models import College
from core.aws.helpers import upload_file_to_s3
from users.api.permissions import IsSystemAdmin
from users.api.serializers import UserSerializer
from users.models import UserType, User
from rest_framework.decorators import api_view, permission_classes
from .serializers import CollegeSerializer


class UnverifiedCollegeListView(generics.ListAPIView):
    """
    Endpoint to get all unverified colleges. Only SystemAdmins
    can access this endpoint.
    """
    queryset = College.objects.filter(is_verified=False)
    serializer_class = CollegeSerializer
    permission_classes = [IsAuthenticated, IsSystemAdmin]


class CollegeApiViewSet(ModelViewSet):
    """
    API viewset for College model.
    """
    queryset = College.objects.all()
    serializer_class = CollegeSerializer

    def get_permissions(self):
        if self.action == 'create':
            return []
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        """
        Create a new College instance.
        """
        colors = request.data.pop('colors', [])
        logo_file = request.FILES.get('logo_img')

        with transaction.atomic():
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            college = serializer.save()

            # Upload logo image to S3
            if logo_file:
                file_path = f"logos/{str(uuid.uuid4())}_{logo_file.name}"
                logo_url = upload_file_to_s3(
                    file=logo_file,
                    key= file_path,
                )

                college.logo = logo_url
                college.save(update_fields=['logo'])

            # Assign colors
            for color in colors:
                color_instance, _ = Color.objects.get_or_create(hex_code=color)
                CollegeColor.objects.create(
                    college = college,
                    color = color_instance
                )

        data = self.get_serializer(college).data
        return Response(data, status=status.HTTP_201_CREATED)

@api_view(["POST"])
@permission_classes([IsSystemAdmin])
def verify_college(request, college_id):
    if not college_id:
        return Response({'error': 'college_id es requerido'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        college = College.objects.get(pk=college_id)
    except College.DoesNotExist:
        return Response({'error': 'La institución no existe'}, status=status.HTTP_404_NOT_FOUND)

    with transaction.atomic():
        college.is_verified = True
        college.save()
        user_type = UserType.objects.get(name="CollegeAdmin")
        username = f"admin_{college.college_id}"
        email = college.email
        password = get_random_string(20)

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            user_type=user_type,
            college=college
        )
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)