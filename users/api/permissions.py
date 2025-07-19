# users/api/permissions.py
from rest_framework.permissions import BasePermission

class IsSystemAdmin(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            getattr(request.user.user_type, "name", "") == "SystemAdmin"
        )

class IsCollegeAdminOfOwnCollege(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            getattr(request.user.user_type, "name", "") == "CollegeAdmin" and
            getattr(request.user.college, "is_verified", False)
        )

    def has_object_permission(self, request, view, obj):
        return obj == request.user.college

class IsDriver(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            getattr(request.user.user_type, "name", "") == "Driver"
        )

class IsPassenger(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            getattr(request.user.user_type, "name", "") == "Passenger"
        )