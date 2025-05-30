from django.urls import path, include
from rest_framework.routers import DefaultRouter

from users.api.views import getRoutes, CustomTokenObtainPairView, UserApiViewSet, unverified_users_by_college, \
    get_user_documents
from rest_framework_simplejwt.views import TokenRefreshView

router = DefaultRouter()
router.register("", UserApiViewSet, basename='users')
urlpatterns = [
    path('', getRoutes),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('users/unverified/', unverified_users_by_college, name='unverified_users_by_college'),
    path('user_documents/<user_id>/', get_user_documents, name='get_user_documents')
]