from django.urls import path, include
from rest_framework.routers import DefaultRouter

from users.api.views import getRoutes, CustomTokenObtainPairView, UserApiViewSet
from rest_framework_simplejwt.views import TokenRefreshView

router = DefaultRouter()
router.register('users', UserApiViewSet, basename='users')
urlpatterns = [
    path('', getRoutes),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', include(router.urls)),
]