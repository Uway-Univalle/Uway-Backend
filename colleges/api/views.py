import threading
import uuid

from django.db import transaction

from django.utils.crypto import get_random_string
from drf_spectacular.utils import extend_schema
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework import status

from colleges.api.serializers import CollegeSerializer, CollegeCreateSerializer, ReportRequestSerializer
from colleges.models import College, Color, CollegeColor

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from colleges.models import College
from core.aws.helpers import upload_file_to_s3, delete_file_from_s3
from emails.helpers import send_admin_credentials_email, send_denied_notification_to_college
from users.api.permissions import IsSystemAdmin
from core.aws.helpers import upload_file_to_s3
from emails.helpers import send_admin_credentials_email
from users.api.permissions import IsSystemAdmin, IsCollegeAdminOfOwnCollege
from users.api.serializers import UserSerializer
from users.models import UserType, User
from rest_framework.decorators import api_view, permission_classes, action
from .serializers import CollegeSerializer
from ..tasks import generate_institutional_report


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
        if self.action == 'create' or self.action == 'list':
            return []
        if self.action == 'destroy':
            return [IsAuthenticated(), IsSystemAdmin()]
        return [IsAuthenticated()]

    @extend_schema(request=CollegeCreateSerializer, responses=CollegeSerializer)
    def create(self, request, *args, **kwargs):
        """
        Create a new College instance.
        """
        data = request.data.copy()
        colors = data.pop('colors', [])
        logo_file = request.FILES.get('logo_img')

        with transaction.atomic():
            serializer = self.get_serializer(data=data)
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

        response = self.get_serializer(college).data
        return Response(response, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        """
        Deletes a College instance, its associated documents (from S3 and database),
        and sends a notification email.
        """
        college = get_object_or_404(College, pk=kwargs['pk'])

        if college.logo and college.logo.startswith('https://uway.s3.amazonaws.com/'):
            # Delete logo from S3
            delete_file_from_s3(college.logo.split('https://uway.s3.amazonaws.com/')[1])


        # Save data for the email before deleting the college
        college_name = college.name
        email_to = college.email

        # Delete the college instance
        college.delete()

        # Send notification email in a separate thread
        thread = threading.Thread(
            target=send_denied_notification_to_college,
            args=(college_name, email_to)
        )
        thread.start()

        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(["POST"])
@permission_classes([IsSystemAdmin])
def verify_college(request, college_id):
    """
    Endpoint to verify a college once the System Admin has reviewed
    the essential information of the college.

    The verification process includes setting the college is_verified
    attribute to True as well as creating a new user with the
    CollegeAdmin User Type and sending the user credentials via email.
    """
    try:
        college = College.objects.get(pk=college_id)
    except College.DoesNotExist:
        return Response({'error': 'La institución no existe'}, status=status.HTTP_404_NOT_FOUND)

    if college.is_verified:
        return Response({'detail': 'La institución ya está verificada'}, status=status.HTTP_400_BAD_REQUEST)

    with transaction.atomic():
        college.is_verified = True
        college.save()
        username = f"admin_{uuid.uuid4().hex[:10]}"
        user_type = UserType.objects.get(name="CollegeAdmin")
        email = college.email
        password = get_random_string(20)

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            user_type=user_type,
            college=college,
            is_verified=True
        )
        serializer = UserSerializer(user)

    thread = threading.Thread(
        target=send_admin_credentials_email, args=(username, password, college.name, college.email)
    )
    thread.start()

    return Response(serializer.data, status=status.HTTP_201_CREATED)

@extend_schema(request=ReportRequestSerializer)
@api_view(["POST"])
@permission_classes([IsAuthenticated, IsCollegeAdminOfOwnCollege])
def generate_college_report(request, college_id):
    serializer = ReportRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    start_date = serializer.validated_data['start_date']
    end_date = serializer.validated_data['end_date']

    generate_institutional_report.delay(college_id, start_date.isoformat(), end_date.isoformat(), request.user.email)

    return Response(
        {'detail': 'El reporte se generará y enviará por correo en breve.'},
        status=status.HTTP_200_OK
    )