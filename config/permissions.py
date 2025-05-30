from rest_framework import permissions


class IsSelfOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True 
        if view.action != 'me':
            return False


class SalePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        
        if view.action in ['list', 'create', 'retrieve', 'update', 'partial_update']:
                return True
        
        return False 
    
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True 
        
        if view.action in ['retrieve', 'update', 'partial_update']:
            return obj.store == request.user.store
        
        return False


class StorePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser or view.action in ['list', 'retrieve']:
            return True 
        
        return False
    
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True 
        
        if view.action == 'retrieve':
            return obj == request.user.store

        return False


class ItemPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.is_superuser:
            return True 
        
        if request.user.role == 'Администратор':
            if view.action in ['list', 'retrieve']:
                return True 
        
        return False
    
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True 

        return False


class ClientPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser or view.action in ['list', 'retrieve', 'create']:
            return True 
        
        return False 


class DebtPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True 
        
        if view.action in ['create', 'list', 'retrieve']:
            return True 
        
        if view.action in ['update', 'partial_update']:
            if request.user.role == 'Администратор':
                return True 
            
        return False

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True 
        if view.action in ['retrieve', 'update', 'partial_update']:
            return obj.store == request.user.store
        return False


class DebtPaymentPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True 
        
        if view.action in ['create', 'list', 'retrieve']:
            return True 
        
        if view.action in ['update', 'partial_update']:
            if request.user.role == 'Администратор':
                return True
            
        return False

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True 
        if view.action in ['retrieve', 'update', 'partial_update']:
            return obj.debt.store == request.user.store
        return False



