from rest_framework import permissions


class IsOwner(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if obj:
            if obj.owner == request.user:
                return True
            return False
        return False


class IsStaff(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            return request.user.is_staff
        return False

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)
