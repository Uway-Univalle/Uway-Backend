from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UnverifiedCollegeListView
from colleges.api.views import CollegeApiViewSet

college_router = DefaultRouter()
college_router.register('colleges', CollegeApiViewSet, basename='college')

urlpatterns = [
    path('', include(college_router.urls)),
    path('unverified-colleges/', UnverifiedCollegeListView.as_view(), name='unverified-colleges'),
]