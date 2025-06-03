from rest_framework import permissions


class IsSelfOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True 
        if view.action == 'me':
            return True
        if request.user.role == 'Администратор' and view.action in ['list', 'retrieve']:
            return True 
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
        
        return obj.store == request.user.store


class StorePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser or view.action in ['list', 'retrieve']:
            return True 
        
        return False
    
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True 
        
        return obj == request.user.store


class ItemPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True 
        
        if request.user.role == 'Администратор' and view.action in ['list', 'retrieve']:
            return True 
        
        return False
    
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        if request.user.role == 'Администратор'and view.action == 'retrieve':
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
        return obj.store == request.user.store


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
        return obj.debt.store == request.user.store


class StockPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True 
        
        if view.action in ['list', 'retrieve']:
                return True 
        
        return False
    
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        return obj.store == request.user.store


class ExpensePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser or request.user.role == 'Администратор':
            return True 
        
        return False
    
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True 
        return obj.store.owner == request.user 


class TransferPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True 
        if request.user.role == 'Администратор' and view.action in ['list', 'retrieve', 'create', 'update', 'partial_update']:
            return True 
        return False 
    
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True 
        return obj.from_stock.store == request.user.store
