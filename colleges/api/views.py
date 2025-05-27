from django.db import transaction
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework import status

from colleges.api.serializers import CollegeSerializer
from colleges.models import College, Color, CollegeColor

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from colleges.models import College
from users.api.permissions import IsSystemAdmin
from .serializers import CollegeSerializer

class UnverifiedCollegeListView(generics.ListAPIView):
    queryset = College.objects.filter(is_verified=False)
    serializer_class = CollegeSerializer
    permission_classes = [IsAuthenticated, IsSystemAdmin]
class CollegeApiViewSet(ModelViewSet):
    """
    API viewset for College model.
    """
    queryset = College.objects.all()
    serializer_class = CollegeSerializer
    permission_classes = []

    def create(self, request, *args, **kwargs):
        """
        Create a new College instance.
        """
        colors = request.data.pop('colors', [])
        with transaction.atomic():

            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            college = serializer.save()

            for color in colors:
                color_instance, _ = Color.objects.get_or_create(hex_code=color)
                CollegeColor.objects.create(
                    college = college,
                    color = color_instance
                )

        data = self.get_serializer(college).data
        return Response(data, status=status.HTTP_201_CREATED)