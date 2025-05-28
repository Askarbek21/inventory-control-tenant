from rest_framework import viewsets
#from rest_framework_roles.granting import allof

#from config.roles import is_manager, belongs_to_store, is_seller
from .serializers import *
from .filters import SaleFilter


class SaleViewset(viewsets.ModelViewSet):
    queryset = Sale.objects.prefetch_related('sale_items', 'sale_payments').select_related('store')
    serializer_class = SaleSerializer
    filterset_class = SaleFilter
    #view_permissions = {
    #    'options': {'admin':True},
    #    'create': {'admin':True,'manager': allof(is_manager, belongs_to_store), 'seller':allof(is_seller, belongs_to_store)},
    #    'list': {'admin':True,'manager': allof(is_manager, belongs_to_store)},
    #    'retrieve': {'admin':True,'manager': allof(is_manager, belongs_to_store)},
    #    'update,partial_update': {'admin': True},
    #    'destroy': {'admin':True}, 
    #}

    def get_serializer_context(self):
        context = {'request': self.request}
        return context

