from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UnverifiedCollegeListView
from colleges.api.views import CollegeApiViewSet,verify_college

college_router = DefaultRouter()
college_router.register('', CollegeApiViewSet, basename='college')

urlpatterns = [
    path('colleges/unverified/', UnverifiedCollegeListView.as_view(), name='unverified-colleges'),
    path('colleges/<college_id>/verify/', verify_college, name='college-verify'),
    #path('colleges/<int:college_id>/generate-college-report', generate_college_report, name='generate-college-report'),
]