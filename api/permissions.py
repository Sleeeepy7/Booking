from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Права для владелеца и админа"""

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or obj.owner == request.user
                or request.user.is_staff or request.user.is_superuser)


class IsAdminUserOrReadOnly(permissions.BasePermission):
    """Права админа."""
    def has_permission(self, request, view):
        return (
                request.method in permissions.SAFE_METHODS
                or request.user.is_staff and request.user.is_superuser
        )
