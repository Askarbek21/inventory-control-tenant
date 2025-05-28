from rest_framework import permissions


class IsStoreMember(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        return obj.store == request.user.store


class RoleBasedPermission(permissions.BasePermission):

    def __init__(self, allowed_roles):
        self.allowed_roles = allowed_roles

    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        return request.user.role in self.allowed_roles


class SalePermission(permissions.BasePermission):
    def has_permission(self, request, view):

        if request.user.is_superuser:
            return True

        if view.action == 'create':
            return request.user.role in ['Продавец', 'Администратор']
        
        return False

    def has_object_permission(self, request, view, obj):

        if request.user.is_superuser:
            return True
            
        if request.user.role == 'Администратор':
            return obj.store == request.user.store
            
        return False