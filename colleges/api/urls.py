from django.urls import path, include
from rest_framework.routers import DefaultRouter

from colleges.api.views import CollegeApiViewSet

college_router = DefaultRouter()
college_router.register('colleges', CollegeApiViewSet, basename='college')

urlpatterns = [
    path('', include(college_router.urls))
]