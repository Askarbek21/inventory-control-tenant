from rest_framework import viewsets
from rest_framework_roles.granting import allof

from config.roles import is_manager, owns_store
from .serializers import *


class StoreViewset(viewsets.ModelViewSet):
    serializer_class = StoreSerializer
    queryset = Store.objects.all()
    #view_permissions = {
    #    'create': {'admin':True},
    #    'list': {'admin':True},
    #    'retrieve': {'admin':True, 'manager': allof(is_manager, owns_store)},
    #    'update,partial_update': {'admin': True},
    #    'destroy': {'admin':True}, 
    #}
    
