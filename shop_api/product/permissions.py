from rest_framework.permissions import BasePermission


class IsAuthor(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.owner


class IsaAuthorOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_super_user:
            return True
        return request.user == obj.owner
