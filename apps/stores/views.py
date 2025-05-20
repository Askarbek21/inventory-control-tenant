from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework_roles.granting import allof

from config.roles import is_manager, owns_store
from config.pagination import CustomPageNumberPagination
from .serializers import *
from .filters import StoreFilter


class StoreViewset(viewsets.ModelViewSet):
    serializer_class = StoreSerializer
    queryset = Store.objects.all()
    #view_permissions = {
    #    'options': {'admin':True},
    #    'create': {'admin':True},
    #    'list': {'admin':True},
    #    'retrieve': {'admin':True, 'manager': allof(is_manager, owns_store)},
    #    'update,partial_update': {'admin': True},
    #    'destroy': {'admin':True}, 
    #}
    
    pagination_class = CustomPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = StoreFilter
