# users/api/permissions.py
from rest_framework.permissions import BasePermission

class IsSystemAdmin(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            getattr(request.user.user_type, "name", "") == "SystemAdmin"
        )