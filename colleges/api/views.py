import uuid

from django.db import transaction
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