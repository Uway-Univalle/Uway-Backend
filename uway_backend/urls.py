from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

from colleges.api.urls import college_router
from users.api.urls import router

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('users.api.urls')),
    path('api/', include('colleges.api.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/docs/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path("api/users/", include(router.urls)),
    path('api/', include('vehicles.api.urls')),
    path('api/', include('routes.api.urls')),
    path('api/', include('trips.api.urls')),
    path('api/colleges/', include(college_router.urls))
]
